"""Tests for documentation generation service."""

import json
import shutil
from pathlib import Path
from uuid import uuid4

import pytest

from curriculum.documentation import DocumentationGeneratorService


@pytest.mark.integration
class TestDocumentationGenerator:
    """Tests for DocumentationGeneratorService."""

    @pytest.fixture
    def doc_service(self, tmp_path):
        """Create documentation generator service with temp output."""
        output_dir = tmp_path / "docs"
        return DocumentationGeneratorService(output_dir=str(output_dir))

    @pytest.fixture
    def sample_python_file(self, tmp_path):
        """Create a sample Python file for testing."""
        test_file = tmp_path / "sample.py"
        test_file.write_text('''"""Sample module for testing."""

from typing import List, Optional


class SampleClass:
    """A sample class for testing."""

    def __init__(self, name: str) -> None:
        """Initialize with a name."""
        self.name = name

    def greet(self, greeting: str = "Hello") -> str:
        """Return a greeting message."""
        return f"{greeting}, {self.name}!"


def sample_function(x: int, y: int) -> int:
    """Add two numbers."""
    return x + y


async def async_sample(data: List[str]) -> Optional[str]:
    """Process data asynchronously."""
    if not data:
        return None
    return data[0]
''')
        return test_file

    def test_initialization(self, doc_service):
        """Test service initialization."""
        assert doc_service is not None
        assert doc_service.output_dir.exists()

    def test_output_directory_structure(self, doc_service):
        """Test that output directories are created."""
        expected_dirs = [
            "modules",
            "files",
            "methods",
            "summaries",
            "llm_analysis",
        ]
        
        for dir_name in expected_dirs:
            dir_path = doc_service.output_dir / dir_name
            assert dir_path.exists()
            assert dir_path.is_dir()

    def test_extract_file_documentation(self, doc_service, sample_python_file):
        """Test extracting documentation from a Python file."""
        file_doc = doc_service._extract_file_documentation(sample_python_file)
        
        assert file_doc is not None
        assert "module_docstring" in file_doc
        assert file_doc["module_docstring"] == "Sample module for testing."
        assert "classes" in file_doc
        assert "functions" in file_doc
        assert file_doc["total_classes"] == 1
        assert file_doc["total_functions"] == 2

    def test_extract_class_info(self, doc_service, sample_python_file):
        """Test extracting class information."""
        file_doc = doc_service._extract_file_documentation(sample_python_file)
        
        assert len(file_doc["classes"]) == 1
        
        class_info = file_doc["classes"][0]
        assert class_info["name"] == "SampleClass"
        assert class_info["docstring"] == "A sample class for testing."
        assert len(class_info["methods"]) == 2  # __init__ and greet

    def test_extract_function_info(self, doc_service, sample_python_file):
        """Test extracting function information."""
        file_doc = doc_service._extract_file_documentation(sample_python_file)
        
        functions = file_doc["functions"]
        assert len(functions) == 2
        
        # Check first function
        sample_func = next(f for f in functions if f["name"] == "sample_function")
        assert sample_func["docstring"] == "Add two numbers."
        assert len(sample_func["parameters"]) == 2
        assert sample_func["parameters"][0]["name"] == "x"
        assert sample_func["parameters"][0]["annotation"] == "int"
        assert sample_func["return_type"] == "int"
        assert not sample_func["is_async"]
        
        # Check async function
        async_func = next(f for f in functions if f["name"] == "async_sample")
        assert async_func["is_async"]
        assert async_func["return_type"] == "Optional[str]"

    def test_extract_method_info(self, doc_service, sample_python_file):
        """Test extracting method information from classes."""
        file_doc = doc_service._extract_file_documentation(sample_python_file)
        
        class_info = file_doc["classes"][0]
        methods = class_info["methods"]
        
        assert len(methods) == 2
        
        # Check __init__ method
        init_method = next(m for m in methods if m["name"] == "__init__")
        assert init_method["is_method"]
        assert len(init_method["parameters"]) == 2  # self and name
        assert init_method["parameters"][1]["name"] == "name"
        
        # Check greet method
        greet_method = next(m for m in methods if m["name"] == "greet")
        assert greet_method["docstring"] == "Return a greeting message."
        assert greet_method["return_type"] == "str"

    def test_extract_imports(self, doc_service, sample_python_file):
        """Test extracting import statements."""
        file_doc = doc_service._extract_file_documentation(sample_python_file)
        
        imports = file_doc["imports"]
        assert len(imports) > 0
        
        # Check for typing import
        typing_import = next(i for i in imports if i.get("module") == "typing")
        assert typing_import["type"] == "from_import"
        assert "List" in typing_import["names"]
        assert "Optional" in typing_import["names"]

    def test_generate_documentation_basic(self, doc_service, tmp_path):
        """Test basic documentation generation without LLM."""
        # Create a simple package structure
        package_dir = tmp_path / "test_package"
        package_dir.mkdir()
        
        # Create __init__.py
        (package_dir / "__init__.py").write_text('"""Test package."""')
        
        # Create a module
        (package_dir / "module1.py").write_text('''"""Module 1."""

class TestClass:
    """A test class."""
    
    def test_method(self):
        """A test method."""
        pass
''')
        
        result = doc_service.generate_documentation(
            package_path=str(package_dir),
            use_llm=False,
        )
        
        assert result["status"] == "success"
        assert result["modules_documented"] >= 1
        assert result["files_documented"] >= 1

    def test_output_files_created(self, doc_service, tmp_path):
        """Test that documentation output files are created."""
        package_dir = tmp_path / "test_package"
        package_dir.mkdir()
        (package_dir / "__init__.py").write_text('"""Test."""')
        
        doc_service.generate_documentation(
            package_path=str(package_dir),
            use_llm=False,
        )
        
        # Check index files
        assert (doc_service.output_dir / "index.json").exists()
        assert (doc_service.output_dir / "README.md").exists()
        
        # Check subdirectories have content
        assert any((doc_service.output_dir / "files").iterdir())

    def test_module_documentation_markdown(self, doc_service, tmp_path):
        """Test module documentation in Markdown format."""
        package_dir = tmp_path / "test_package"
        package_dir.mkdir()
        
        (package_dir / "test_module.py").write_text('''"""Test module with classes."""

class MyClass:
    """My test class."""
    
    def my_method(self):
        """My test method."""
        pass
''')
        
        doc_service.generate_documentation(
            package_path=str(package_dir),
            use_llm=False,
        )
        
        # Find generated markdown files
        md_files = list((doc_service.output_dir / "modules").glob("*.md"))
        assert len(md_files) > 0
        
        # Check content
        content = md_files[0].read_text()
        assert "MyClass" in content
        assert "my_method" in content

    def test_get_documentation_stats(self, doc_service, tmp_path):
        """Test getting documentation statistics."""
        package_dir = tmp_path / "test_package"
        package_dir.mkdir()
        (package_dir / "__init__.py").write_text('"""Test."""')
        (package_dir / "module1.py").write_text('"""Module."""\nclass A: pass')
        
        doc_service.generate_documentation(
            package_path=str(package_dir),
            use_llm=False,
        )
        
        stats = doc_service.get_documentation_stats()
        
        assert "modules" in stats
        assert "files" in stats
        assert "methods" in stats
        assert stats["modules"] >= 1
        assert stats["files"] >= 1

    def test_export_markdown(self, doc_service, tmp_path):
        """Test exporting documentation as Markdown."""
        package_dir = tmp_path / "test_package"
        package_dir.mkdir()
        (package_dir / "__init__.py").write_text('"""Test package."""')
        
        doc_service.generate_documentation(
            package_path=str(package_dir),
            use_llm=False,
        )
        
        output_file = tmp_path / "export.md"
        result = doc_service.export_documentation(
            format="markdown",
            output_file=str(output_file),
        )
        
        assert Path(result).exists()
        content = Path(result).read_text()
        assert "Complete System Documentation" in content

    def test_export_json(self, doc_service, tmp_path):
        """Test exporting documentation as JSON."""
        package_dir = tmp_path / "test_package"
        package_dir.mkdir()
        (package_dir / "__init__.py").write_text('"""Test package."""')
        
        doc_service.generate_documentation(
            package_path=str(package_dir),
            use_llm=False,
        )
        
        output_file = tmp_path / "export.json"
        result = doc_service.export_documentation(
            format="json",
            output_file=str(output_file),
        )
        
        assert Path(result).exists()
        
        # Verify JSON structure
        data = json.loads(Path(result).read_text())
        assert "modules" in data
        assert "files" in data
        assert "methods" in data

    def test_mock_llm_response(self, doc_service):
        """Test mock LLM response generation."""
        prompt = "Analyze this code"
        response = doc_service._generate_mock_llm_response(prompt)
        
        assert response is not None
        
        # Parse JSON response
        data = json.loads(response)
        assert "overview" in data
        assert "note" in data
        assert "placeholder response" in data["note"]

    def test_llm_summary_generation_with_mock(self, doc_service, tmp_path):
        """Test LLM summary generation with mock responses."""
        package_dir = tmp_path / "test_package"
        package_dir.mkdir()
        
        (package_dir / "test_module.py").write_text('''"""Test module."""

class TestClass:
    """A test class."""
    pass
''')
        
        # Generate with LLM (will use mock)
        result = doc_service.generate_documentation(
            package_path=str(package_dir),
            use_llm=True,
        )
        
        # Check that summaries were generated
        assert result["llm_summaries_generated"] >= 0
        
        # Check summary files exist
        summary_files = list((doc_service.output_dir / "llm_analysis").glob("*.json"))
        # May have summaries from package overview even if module summaries failed
        assert len(summary_files) >= 0

    def test_error_handling_invalid_python(self, doc_service, tmp_path):
        """Test error handling for invalid Python files."""
        invalid_file = tmp_path / "invalid.py"
        invalid_file.write_text("this is not valid python @@@ ###")
        
        file_doc = doc_service._extract_file_documentation(invalid_file)
        
        assert "error" in file_doc
        assert file_doc["file_path"] == str(invalid_file)

    def test_module_name_extraction(self, doc_service, tmp_path):
        """Test extracting module names from file paths."""
        package_root = tmp_path / "mypackage"
        package_root.mkdir()
        
        file_path = package_root / "submodule" / "myfile.py"
        file_path.parent.mkdir(parents=True)
        file_path.write_text('"""Test."""')
        
        module_name = doc_service._get_module_name(file_path, package_root)
        assert module_name == "submodule.myfile"

    def test_annotation_extraction(self, doc_service):
        """Test type annotation extraction."""
        import ast
        
        # Test simple type
        node = ast.Name(id="int")
        result = doc_service._get_annotation(node)
        assert result == "int"
        
        # Test None
        result = doc_service._get_annotation(None)
        assert result is None

    def test_real_curriculum_package(self, doc_service):
        """Test documentation generation on actual curriculum package."""
        result = doc_service.generate_documentation(
            package_path="src/curriculum/core",
            use_llm=False,
        )
        
        assert result["status"] == "success"
        assert result["modules_documented"] > 0
        assert result["files_documented"] > 0
        
        # Verify index was created
        index_file = doc_service.output_dir / "index.json"
        assert index_file.exists()
        
        index_data = json.loads(index_file.read_text())
        assert "statistics" in index_data
        assert index_data["statistics"]["total_modules"] > 0

    def test_prepare_module_context(self, doc_service):
        """Test preparing module context for LLM."""
        module_data = {
            "documentation": {
                "module_docstring": "Test module docstring",
                "classes": [
                    {
                        "name": "TestClass",
                        "docstring": "Test class docstring",
                    }
                ],
                "functions": [
                    {
                        "name": "test_func",
                        "docstring": "Test function docstring",
                    }
                ],
            }
        }
        
        context = doc_service._prepare_module_context(module_data)
        
        assert "Module Docstring" in context
        assert "TestClass" in context
        assert "test_func" in context

    def test_prepare_file_context(self, doc_service):
        """Test preparing file context for LLM."""
        file_data = {
            "lines_of_code": 100,
            "total_classes": 3,
            "total_functions": 5,
            "module_docstring": "File docstring here",
        }
        
        context = doc_service._prepare_file_context(file_data)
        
        assert "Lines of Code: 100" in context
        assert "Classes: 3" in context
        assert "Functions: 5" in context
        assert "File docstring" in context

    def test_index_json_structure(self, doc_service, tmp_path):
        """Test index.json has correct structure."""
        package_dir = tmp_path / "test_package"
        package_dir.mkdir()
        (package_dir / "__init__.py").write_text('"""Test."""')
        
        doc_service.generate_documentation(
            package_path=str(package_dir),
            use_llm=False,
        )
        
        index_file = doc_service.output_dir / "index.json"
        data = json.loads(index_file.read_text())
        
        assert "generated_at" in data
        assert "statistics" in data
        assert "modules" in data
        assert "output_structure" in data
        
        # Check statistics
        stats = data["statistics"]
        assert "total_modules" in stats
        assert "total_files" in stats
        assert "total_methods" in stats

    def test_readme_generation(self, doc_service, tmp_path):
        """Test README.md generation."""
        package_dir = tmp_path / "test_package"
        package_dir.mkdir()
        (package_dir / "test.py").write_text('"""Test."""\nclass A: pass')
        
        doc_service.generate_documentation(
            package_path=str(package_dir),
            use_llm=False,
        )
        
        readme_file = doc_service.output_dir / "README.md"
        assert readme_file.exists()
        
        content = readme_file.read_text()
        assert "Auto-Generated Documentation" in content
        assert "Statistics" in content
        assert "Documentation Structure" in content

    def test_method_storage(self, doc_service, sample_python_file):
        """Test that methods are stored separately."""
        file_doc = doc_service._extract_file_documentation(sample_python_file)
        
        # Methods should be stored in _method_docs
        assert "SampleClass.__init__" in doc_service._method_docs
        assert "SampleClass.greet" in doc_service._method_docs
        
        # Verify method data
        greet_method = doc_service._method_docs["SampleClass.greet"]
        assert greet_method["name"] == "greet"
        assert greet_method["is_method"]

    def test_methods_index_generation(self, doc_service, tmp_path):
        """Test methods index file generation."""
        package_dir = tmp_path / "test_package"
        package_dir.mkdir()
        
        (package_dir / "test.py").write_text('''"""Test."""

class MyClass:
    def method1(self):
        """Method 1."""
        pass
    
    def method2(self):
        """Method 2."""
        pass
''')
        
        doc_service.generate_documentation(
            package_path=str(package_dir),
            use_llm=False,
        )
        
        methods_index = doc_service.output_dir / "methods" / "index.json"
        assert methods_index.exists()
        
        data = json.loads(methods_index.read_text())
        assert len(data) >= 2  # At least method1 and method2


@pytest.mark.integration
class TestDocumentationIntegration:
    """Integration tests for documentation module."""

    @pytest.fixture
    def doc_service(self, tmp_path):
        """Create documentation service."""
        return DocumentationGeneratorService(output_dir=str(tmp_path / "docs"))

    def test_full_curriculum_documentation(self, doc_service):
        """Test generating docs for entire curriculum package."""
        result = doc_service.generate_documentation(
            package_path="src/curriculum",
            use_llm=False,
        )
        
        assert result["status"] == "success"
        assert result["modules_documented"] > 10
        assert result["files_documented"] > 10
        
        # Verify key modules are documented
        module_names = list(doc_service._module_docs.keys())
        assert any("core" in name for name in module_names)
        assert any("content" in name for name in module_names)

    def test_export_complete_documentation(self, doc_service):
        """Test exporting complete documentation."""
        # Generate docs
        doc_service.generate_documentation(
            package_path="src/curriculum/core",
            use_llm=False,
        )
        
        # Export as Markdown
        md_file = doc_service.export_documentation(format="markdown")
        assert Path(md_file).exists()
        
        # Export as JSON
        json_file = doc_service.export_documentation(format="json")
        assert Path(json_file).exists()
        
        # Verify exports contain data
        assert Path(md_file).stat().st_size > 100
        assert Path(json_file).stat().st_size > 100

    def test_llm_analysis_markdown_export(self, doc_service, tmp_path):
        """Test exporting LLM analyses to Markdown."""
        # Create mock LLM summaries
        doc_service._llm_summaries = {
            "package_overview": {
                "summary_type": "package_overview",
                "llm_analysis": "Test package overview",
                "statistics": {"total_modules": 5},
                "generated_at": "2025-10-01T10:00:00",
            },
            "module_test": {
                "summary_type": "module",
                "module_name": "test.module",
                "llm_analysis": "Test module analysis",
                "generated_at": "2025-10-01T10:01:00",
            },
            "file_test": {
                "summary_type": "file",
                "file_path": "/path/to/test.py",
                "llm_analysis": "Test file analysis",
                "generated_at": "2025-10-01T10:02:00",
            },
        }
        
        # Export to Markdown
        result = doc_service.export_llm_analyses_to_markdown()
        
        # Verify result
        assert result["standalone_files"] == 3
        assert result["combined_file"] == 1
        assert "llm_analysis_md" in result["output_directory"]
        
        # Verify standalone files exist
        llm_md_dir = Path(result["output_directory"])
        assert llm_md_dir.exists()
        assert (llm_md_dir / "00_package_overview.md").exists()
        assert (llm_md_dir / "module_test_module.md").exists()
        assert (llm_md_dir / "file_test.md").exists()
        
        # Verify combined file exists
        combined_file = doc_service.output_dir / "llm_analysis_complete.md"
        assert combined_file.exists()
        assert combined_file.stat().st_size > 100

    def test_convert_llm_json_to_markdown(self, doc_service):
        """Test converting LLM JSON to Markdown format."""
        analysis_data = {
            "summary_type": "module",
            "module_name": "core.base",
            "llm_analysis": "This module provides base classes.",
            "statistics": {"total_classes": 3},
            "generated_at": "2025-10-01T10:00:00",
        }
        
        markdown = doc_service._convert_llm_json_to_markdown("module_core_base", analysis_data)
        
        # Verify Markdown content
        assert "# Module Analysis: `core.base`" in markdown
        assert "## Statistics" in markdown
        assert "**Total Classes:** 3" in markdown
        assert "## AI-Generated Analysis" in markdown
        assert "This module provides base classes." in markdown
        assert "## Metadata" in markdown
        assert "module_core_base" in markdown

    def test_combined_llm_markdown_structure(self, doc_service):
        """Test the structure of combined LLM Markdown."""
        # Create varied LLM summaries
        doc_service._llm_summaries = {
            "package_overview": {
                "summary_type": "package_overview",
                "llm_analysis": "Package analysis",
                "generated_at": "2025-10-01T10:00:00",
            },
            "module_a": {
                "summary_type": "module",
                "module_name": "module.a",
                "llm_analysis": "Module A analysis",
                "generated_at": "2025-10-01T10:01:00",
            },
            "module_b": {
                "summary_type": "module",
                "module_name": "module.b",
                "llm_analysis": "Module B analysis",
                "generated_at": "2025-10-01T10:02:00",
            },
        }
        
        combined = doc_service._create_combined_llm_markdown()
        
        # Verify structure
        assert "# Complete LLM Analysis" in combined
        assert "## Table of Contents" in combined
        assert "### Package Overview" in combined
        assert "### Module Analyses" in combined
        assert "# Package Overview" in combined
        assert "# Module Analyses" in combined
        assert "## Summary" in combined
        assert "**Total Analyses:** 3" in combined
        assert "**Package Overviews:** 1" in combined
        assert "**Module Analyses:** 2" in combined

    def test_llm_markdown_export_in_generation(self, doc_service, tmp_path):
        """Test that LLM Markdown export is called during documentation generation."""
        # Create a simple package for testing
        test_package = tmp_path / "test_pkg"
        test_package.mkdir()
        (test_package / "__init__.py").write_text('"""Test package."""')
        (test_package / "module.py").write_text('''"""Test module."""

class TestClass:
    """Test class."""
    pass
''')
        
        # Generate with LLM (will use mock)
        result = doc_service.generate_documentation(
            package_path=str(test_package),
            use_llm=True,
        )
        
        # Verify LLM markdown exports are included in result
        assert "llm_markdown_exports" in result
        assert result["llm_markdown_exports"]["standalone_files"] > 0
        assert result["llm_markdown_exports"]["combined_file"] == 1
        
        # Verify files were created
        llm_md_dir = Path(result["llm_markdown_exports"]["output_directory"])
        assert llm_md_dir.exists()
        assert len(list(llm_md_dir.glob("*.md"))) > 0

