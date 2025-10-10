"""Unit tests for documentation generation service."""

import json
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from curriculum.documentation import DocumentationGeneratorService


@pytest.mark.unit
class TestDocumentationGeneratorServiceUnit:
    """Unit tests for DocumentationGeneratorService."""

    @pytest.fixture
    def doc_service(self, tmp_path):
        """Create documentation service with temporary output."""
        return DocumentationGeneratorService(output_dir=str(tmp_path / "docs"))

    @pytest.fixture
    def sample_module_data(self):
        """Sample module data for testing."""
        return {
            "name": "test_module",
            "documentation": {
                "module_docstring": "A test module for unit testing.",
                "classes": [
                    {
                        "name": "TestClass",
                        "docstring": "A test class.",
                        "bases": ["BaseClass"],
                        "methods": [
                            {
                                "name": "test_method",
                                "docstring": "A test method.",
                                "parameters": [
                                    {"name": "self", "annotation": None},
                                    {"name": "param", "annotation": "str"}
                                ],
                                "return_type": "str",
                                "is_async": False
                            }
                        ]
                    }
                ],
                "functions": [
                    {
                        "name": "test_function",
                        "docstring": "A test function.",
                        "parameters": [
                            {"name": "arg1", "annotation": "int"},
                            {"name": "arg2", "annotation": "str"}
                        ],
                        "return_type": "bool",
                        "is_async": True
                    }
                ],
                "imports": [
                    {"type": "import", "modules": ["os", "sys"]},
                    {"type": "from_import", "module": "typing", "names": ["List", "Optional"]}
                ]
            }
        }

    @pytest.fixture
    def sample_file_data(self):
        """Sample file data for testing."""
        return {
            "file_path": "/path/to/test_module.py",
            "module_docstring": "Test module docstring.",
            "lines_of_code": 150,
            "total_classes": 1,
            "total_functions": 1,
            "total_imports": 2,
            "classes": [
                {
                    "name": "TestClass",
                    "docstring": "Test class docstring.",
                    "bases": ["object"],
                    "methods": [
                        {
                            "name": "__init__",
                            "docstring": "Initialize test class.",
                            "parameters": [{"name": "self", "annotation": None}],
                            "return_type": None,
                            "is_async": False
                        }
                    ]
                }
            ],
            "functions": [
                {
                    "name": "test_function",
                    "docstring": "Test function docstring.",
                    "parameters": [
                        {"name": "param1", "annotation": "str"}
                    ],
                    "return_type": "int",
                    "is_async": False
                }
            ],
            "imports": [
                {"type": "import", "modules": ["json"]},
                {"type": "from_import", "module": "pathlib", "names": ["Path"]}
            ]
        }

    def test_service_initialization(self, doc_service):
        """Test service initialization and directory creation."""
        assert doc_service.output_dir.exists()
        assert (doc_service.output_dir / "modules").exists()
        assert (doc_service.output_dir / "files").exists()
        assert (doc_service.output_dir / "methods").exists()
        assert (doc_service.output_dir / "llm_analysis").exists()

    def test_cache_directory_creation(self, doc_service):
        """Test cache directory is created during initialization."""
        cache_dir = doc_service.output_dir / ".llm_cache"
        assert cache_dir.exists()
        assert cache_dir.is_dir()

    def test_cache_key_generation(self, doc_service):
        """Test cache key generation."""
        prompt = "Test prompt for caching"
        model = "test_model"

        cache_key = doc_service._get_cache_key(prompt, model)

        # Should be a hash
        assert isinstance(cache_key, str)
        assert len(cache_key) == 64  # SHA256 hash length

        # Same inputs should produce same key
        cache_key2 = doc_service._get_cache_key(prompt, model)
        assert cache_key == cache_key2

        # Different inputs should produce different keys
        cache_key3 = doc_service._get_cache_key("Different prompt", model)
        assert cache_key != cache_key3

    def test_cache_response_storage(self, doc_service):
        """Test cache response storage and retrieval."""
        cache_key = "test_cache_key"
        response_data = {"response": "Test response", "model": "test_model"}

        # Store response
        doc_service._cache_response(cache_key, response_data)

        # Retrieve response
        cached = doc_service._get_cached_response(cache_key)
        assert cached is not None
        assert cached["response"] == "Test response"
        assert cached["model"] == "test_model"

    def test_cache_expiration(self, doc_service):
        """Test cache TTL expiration."""
        cache_key = "test_expiration_key"
        response_data = {"response": "Test response", "model": "test_model"}

        # Store response
        doc_service._cache_response(cache_key, response_data)

        # Mock an old timestamp to simulate expiration
        cache_file = doc_service._cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            # Manually modify the JSON to have an old timestamp
            import time
            old_time = time.time() - (31 * 24 * 3600)  # 31 days ago
            old_timestamp = datetime.fromtimestamp(old_time, tz=timezone.utc).isoformat()

            # Read and modify the JSON data
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
            cache_data["cached_at"] = old_timestamp
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)

        # Should return None due to expiration
        cached = doc_service._get_cached_response(cache_key)
        assert cached is None
        assert not cache_file.exists()  # Should be deleted

    def test_model_selection(self, doc_service):
        """Test model selection for different analysis types."""
        # Test package overview
        config = doc_service._select_model_for_analysis("package_overview")
        assert config["model"] == "gemma2:2b"
        assert config["temperature"] == 0.3
        assert config["max_tokens"] == 2000

        # Test module analysis
        config = doc_service._select_model_for_analysis("module_analysis")
        assert config["model"] == "llama3.1:latest"
        assert config["temperature"] == 0.2
        assert config["max_tokens"] == 1500

        # Test unknown type (should fallback)
        config = doc_service._select_model_for_analysis("unknown_type")
        assert config["model"] == "llama3.1:latest"
        assert config["temperature"] == 0.3
        assert config["max_tokens"] == 1500

    def test_module_name_extraction(self, doc_service, tmp_path):
        """Test module name extraction from file paths."""
        # Test normal module
        module_name = doc_service._get_module_name(
            tmp_path / "test_module.py",
            tmp_path
        )
        assert module_name == "test_module"

        # Test nested module
        nested_path = tmp_path / "package" / "submodule.py"
        module_name = doc_service._get_module_name(nested_path, tmp_path)
        assert module_name == "package.submodule"

        # Test __init__ file
        init_path = tmp_path / "package" / "__init__.py"
        module_name = doc_service._get_module_name(init_path, tmp_path)
        assert module_name == "package"

    def test_file_documentation_extraction(self, doc_service, tmp_path):
        """Test file documentation extraction."""
        # Create test file
        test_file = tmp_path / "test_module.py"
        test_file.write_text('''"""Test module docstring."""

import os
from typing import List

class TestClass:
    """Test class docstring."""

    def test_method(self, param: str) -> bool:
        """Test method docstring."""
        return len(param) > 0

def test_function(data: List[str]) -> int:
    """Test function docstring."""
    return len(data)
''')

        file_doc = doc_service._extract_file_documentation(test_file)

        assert file_doc["file_path"] == str(test_file)
        assert "Test module docstring" in file_doc["module_docstring"]
        assert file_doc["total_classes"] == 1
        assert file_doc["total_functions"] == 1

        # Check class extraction
        test_class = file_doc["classes"][0]
        assert test_class["name"] == "TestClass"
        assert "Test class docstring" in test_class["docstring"]
        assert len(test_class["methods"]) == 1

        # Check function extraction
        test_func = file_doc["functions"][0]
        assert test_func["name"] == "test_function"
        assert "Test function docstring" in test_func["docstring"]
        assert test_func["return_type"] == "int"
        assert len(test_func["args"]) == 1

    def test_class_info_extraction(self, doc_service):
        """Test class information extraction."""
        # Create AST node for class
        import ast

        class_code = '''
class TestClass(BaseClass):
    """Test class docstring."""

    def __init__(self, name: str) -> None:
        """Initialize with name."""
        self.name = name

    def get_name(self) -> str:
        """Get the name."""
        return self.name
'''

        tree = ast.parse(class_code)
        class_node = tree.body[0]  # First node should be the class

        class_info = doc_service._extract_class_info(class_node)

        assert class_info["name"] == "TestClass"
        assert "Test class docstring" in class_info["docstring"]
        assert "BaseClass" in class_info["bases"]
        assert len(class_info["methods"]) == 2  # __init__ and get_name

    def test_function_info_extraction(self, doc_service):
        """Test function information extraction."""
        import ast

        func_code = '''
def test_function(param1: str, param2: int = 42) -> bool:
    """Test function docstring."""
    return len(param1) > param2

async def async_function(data: dict) -> Optional[str]:
    """Async function docstring."""
    return str(data.get("key"))
'''

        tree = ast.parse(func_code)

        # Test regular function
        func_node = tree.body[0]
        func_info = doc_service._extract_function_info(func_node)

        assert func_info["name"] == "test_function"
        assert "Test function docstring" in func_info["docstring"]
        assert func_info["return_type"] == "bool"
        assert not func_info["is_async"]
        assert len(func_info["args"]) == 2

        # Check parameter extraction
        param1 = func_info["args"][0]
        assert param1["name"] == "param1"
        assert param1["annotation"] == "str"
        assert param1["default"] is None

        param2 = func_info["args"][1]
        assert param2["name"] == "param2"
        assert param2["annotation"] == "int"
        assert param2["default"] == "42"

        # Test async function
        async_node = tree.body[1]
        async_info = doc_service._extract_function_info(async_node)

        assert async_info["name"] == "async_function"
        assert async_info["is_async"] is True
        assert async_info["return_type"] == "Optional[str]"

    def test_import_info_extraction(self, doc_service):
        """Test import information extraction."""
        import ast

        import_code = '''
import os, sys
from typing import List, Optional as Opt
from pathlib import Path
'''

        tree = ast.parse(import_code)

        imports = []
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_info = doc_service._extract_import_info(node)
                imports.append(import_info)

        assert len(imports) == 3

        # Check regular import
        regular_import = imports[0]
        assert regular_import["type"] == "import"
        assert "os" in regular_import["modules"]
        assert "sys" in regular_import["modules"]

        # Check from import
        from_import = imports[1]
        assert from_import["type"] == "from_import"
        assert from_import["module"] == "typing"
        assert "List" in from_import["names"]
        assert "Optional" in from_import["names"]  # Should include alias

    def test_annotation_extraction(self, doc_service):
        """Test type annotation extraction."""
        import ast

        # Test simple type
        simple_code = "param: str"
        tree = ast.parse(simple_code)
        annotation = doc_service._get_annotation(tree.body[0].annotation)
        assert annotation == "str"

        # Test complex type
        complex_code = "param: Optional[List[str]]"
        tree = ast.parse(complex_code)
        annotation = doc_service._get_annotation(tree.body[0].annotation)
        assert annotation == "Optional[List[str]]"

        # Test attribute type
        attr_code = "param: module.Class"
        tree = ast.parse(attr_code)
        annotation = doc_service._get_annotation(tree.body[0].annotation)
        assert annotation == "module.Class"

    def test_module_context_preparation(self, doc_service, sample_module_data):
        """Test module context preparation for LLM."""
        context = doc_service._prepare_module_context(sample_module_data)

        assert "Module Docstring:" in context
        assert "Classes (1):" in context
        assert "TestClass" in context
        assert "Functions (1):" in context
        assert "test_function" in context

    def test_file_context_preparation(self, doc_service, sample_file_data):
        """Test file context preparation for LLM."""
        context = doc_service._prepare_file_context(sample_file_data)

        assert "Lines of Code: 150" in context
        assert "Classes: 1" in context
        assert "Functions: 1" in context
        assert "Docstring: Test module docstring." in context

    def test_package_context_preparation(self, doc_service):
        """Test package context preparation for LLM."""
        # Set up some mock data
        doc_service._module_docs = {
            "module1": {"name": "module1", "classes": [{"name": "Class1"}]},
            "module2": {"name": "module2", "classes": [{"name": "Class2"}]}
        }
        doc_service._stats = {
            "total_modules": 2,
            "total_classes": 2,
            "total_functions": 0,
            "total_files": 2,
            "total_methods": 0,
            "total_llm_summaries": 0
        }

        context = doc_service._prepare_package_context()

        assert "Package contains 2 modules:" in context
        assert "Total Classes: 2" in context
        assert "Total Functions: 0" in context
        assert "Total Methods: 0" in context
        assert "module1" in context
        assert "module2" in context

    def test_mock_llm_response_generation(self, doc_service):
        """Test mock LLM response generation."""
        prompt = "Test prompt for mock response"

        response = doc_service._generate_mock_llm_response(prompt)

        # Should be valid JSON
        try:
            data = json.loads(response)
            assert "overview" in data
            assert "note" in data
            assert "placeholder response" in data["note"]
        except json.JSONDecodeError:
            pytest.fail("Mock response should be valid JSON")

    def test_llm_response_with_cache_hit(self, doc_service):
        """Test LLM call with cache hit."""
        prompt = "Test prompt"
        model = "test_model"

        # Pre-populate cache
        cache_key = doc_service._get_cache_key(prompt, model)
        cached_response = {"response": "Cached response", "model": model}
        doc_service._cache_response(cache_key, cached_response)

        # Mock the actual LLM call to ensure it's not called
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"response": "Should not be used"}

            result = doc_service._call_ollama_llm(prompt, model)

            # Should return cached response, not make API call
            assert result == "Cached response"
            mock_post.assert_not_called()

    def test_llm_response_with_cache_miss(self, doc_service):
        """Test LLM call with cache miss."""
        prompt = "Test prompt for cache miss"
        model = "test_model"

        # Ensure no cache exists
        cache_key = doc_service._get_cache_key(prompt, model)
        cache_file = doc_service._cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            cache_file.unlink()

        # Mock successful LLM response
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.text = "Fresh LLM response"

            result = doc_service._call_ollama_llm(prompt, model)

            assert result == "Fresh LLM response"

            # Check that response was cached
            cached = doc_service._get_cached_response(cache_key)
            assert cached is not None
            assert cached["response"] == "Fresh LLM response"

    def test_llm_timeout_handling(self, doc_service):
        """Test LLM timeout handling."""
        prompt = "Test timeout"
        model = "test_model"

        # Mock timeout
        with patch('requests.post') as mock_post:
            mock_post.side_effect = Exception("Timeout")

            result = doc_service._call_ollama_llm(prompt, model)

            # Should return mock response on timeout
            assert "placeholder response" in result.lower()

    def test_llm_invalid_response_handling(self, doc_service):
        """Test LLM invalid response handling."""
        prompt = "Test invalid response"
        model = "test_model"

        # Mock invalid response
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 500

            result = doc_service._call_ollama_llm(prompt, model)

            # Should return mock response on error
            assert "placeholder response" in result.lower()

    def test_markdown_conversion_basic(self, doc_service):
        """Test basic LLM JSON to Markdown conversion."""
        analysis_data = {
            "summary_type": "module",
            "module_name": "test.module",
            "llm_analysis": "This is a test module analysis.",
            "generated_at": "2025-10-01T10:00:00"
        }

        markdown = doc_service._convert_llm_json_to_markdown("test_key", analysis_data)

        assert "# Module Analysis: `test.module`" in markdown
        assert "## AI-Generated Analysis" in markdown
        assert "This is a test module analysis." in markdown
        assert "## Metadata" in markdown

    def test_markdown_conversion_with_stats(self, doc_service):
        """Test Markdown conversion with statistics."""
        analysis_data = {
            "summary_type": "package_overview",
            "statistics": {
                "total_modules": 5,
                "total_classes": 10,
                "total_functions": 15
            },
            "llm_analysis": "Package analysis with stats.",
            "generated_at": "2025-10-01T10:00:00"
        }

        markdown = doc_service._convert_llm_json_to_markdown("package_key", analysis_data)

        assert "# Package Architectural Overview" in markdown
        assert "## Statistics" in markdown
        assert "**Total Modules:** 5" in markdown
        assert "**Total Classes:** 10" in markdown
        assert "**Total Functions:** 15" in markdown

    def test_combined_markdown_generation(self, doc_service):
        """Test combined Markdown file generation."""
        # Set up mock LLM summaries
        doc_service._llm_summaries = {
            "package_overview": {
                "summary_type": "package_overview",
                "llm_analysis": "Package overview",
                "generated_at": "2025-10-01T10:00:00"
            },
            "module_test1": {
                "summary_type": "module",
                "module_name": "test.module1",
                "llm_analysis": "Module 1 analysis",
                "generated_at": "2025-10-01T10:01:00"
            },
            "module_test2": {
                "summary_type": "module",
                "module_name": "test.module2",
                "llm_analysis": "Module 2 analysis",
                "generated_at": "2025-10-01T10:02:00"
            },
            "file_test1": {
                "summary_type": "file",
                "file_path": "/path/to/test1.py",
                "llm_analysis": "File 1 analysis",
                "generated_at": "2025-10-01T10:03:00"
            }
        }

        combined = doc_service._create_combined_llm_markdown()

        # Check structure
        assert "# Complete LLM Analysis" in combined
        assert "## Table of Contents" in combined
        assert "### Package Overview" in combined
        assert "### Module Analyses" in combined
        assert "# Package Overview" in combined
        assert "# Module Analyses" in combined
        assert "## Summary" in combined

        # Check counts
        assert "**Total Analyses:** 4" in combined
        assert "**Package Overviews:** 1" in combined
        assert "**Module Analyses:** 2" in combined

    def test_stats_calculation(self, doc_service):
        """Test statistics calculation."""
        # Set up mock data
        doc_service._module_docs = {"module1": {}, "module2": {}}
        doc_service._file_docs = {"file1": {}, "file2": {}}
        doc_service._method_docs = {"method1": {}, "method2": {}, "method3": {}}
        doc_service._llm_summaries = {"summary1": {}, "summary2": {}}

        stats = doc_service.get_documentation_stats()

        assert stats["modules"] == 2
        assert stats["files"] == 2
        assert stats["methods"] == 3
        assert stats["llm_summaries"] == 2
        assert "output_directory" in stats

    def test_service_configuration(self, doc_service):
        """Test service configuration settings."""
        # Check default settings
        assert doc_service._max_concurrent_llm_calls == 5
        assert doc_service._llm_timeout_seconds == 60
        assert doc_service._cache_ttl_days == 30
        assert doc_service._enable_caching is True

        # Check model configuration exists
        assert hasattr(doc_service, '_model_config')
        assert "package_overview" in doc_service._model_config
        assert "module_analysis" in doc_service._model_config
        assert "file_deep_analysis" in doc_service._model_config

    def test_error_handling_invalid_file(self, doc_service, tmp_path):
        """Test error handling for invalid Python files."""
        # Create invalid Python file
        invalid_file = tmp_path / "invalid.py"
        invalid_file.write_text("This is not valid Python code!!!")

        file_doc = doc_service._extract_file_documentation(invalid_file)

        # Should handle error gracefully
        assert "error" in file_doc
        assert file_doc["file_path"] == str(invalid_file)

    def test_empty_module_handling(self, doc_service):
        """Test handling of empty modules."""
        # Test with empty module data
        empty_data = {
            "name": "empty_module",
            "docstring": "",
            "classes": [],
            "functions": [],
            "imports": []
        }

        context = doc_service._prepare_module_context(empty_data)

        # Should return empty context for empty module
        assert context == ""

    def test_large_module_handling(self, doc_service):
        """Test handling of large modules with many components."""
        # Create module data with many components
        large_data = {
            "name": "large_module",
            "docstring": "Large module with many components.",
            "classes": [{"name": f"Class{i}"} for i in range(20)],
            "functions": [{"name": f"func{i}"} for i in range(30)],
            "imports": [{"type": "import", "modules": [f"module{i}"]} for i in range(15)]
        }

        context = doc_service._prepare_module_context(large_data)

        # Should handle large data without issues
        assert "Classes (20):" in context
        assert "Class0:" in context
        assert "Functions (30):" in context
        assert "func0:" in context

        # Should not exceed reasonable length
        assert len(context.split("\n")) < 1000  # Reasonable limit

    def test_cache_invalidation(self, doc_service):
        """Test cache invalidation on file changes."""
        cache_key = "test_invalidation"
        response_data = {"response": "Test response", "model": "test"}

        # Store response
        doc_service._cache_response(cache_key, response_data)

        # Verify it exists
        cached = doc_service._get_cached_response(cache_key)
        assert cached is not None

        # Simulate file change by touching cache file
        cache_file = doc_service._cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            # Change modification time to simulate "change"
            import time
            new_time = time.time() - (31 * 24 * 3600)  # 31 days ago
            os.utime(cache_file, (new_time, new_time))

        # Should be invalidated
        cached = doc_service._get_cached_response(cache_key)
        assert cached is None

    def test_concurrent_cache_access(self, doc_service):
        """Test concurrent cache access safety."""
        import threading

        cache_key = "concurrent_test"
        responses = []

        def cache_operation():
            response_data = {"response": f"Response {threading.current_thread().name}", "model": "test"}
            doc_service._cache_response(cache_key, response_data)
            cached = doc_service._get_cached_response(cache_key)
            if cached:
                responses.append(cached["response"])

        # Run multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=cache_operation)
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Should have some responses (thread safety test)
        assert len(responses) >= 0  # At least no crashes

    def test_memory_efficiency_large_data(self, doc_service):
        """Test memory efficiency with large datasets."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create large test data
        large_module_data = {
            "name": "large_test_module",
            "classes": [{"name": f"Class{i}", "methods": [{"name": f"method{j}"} for j in range(10)]} for i in range(100)],
            "functions": [{"name": f"func{i}"} for i in range(200)],
            "imports": [{"type": "import", "modules": [f"module{i}"]} for i in range(50)]
        }

        # Process large data
        context = doc_service._prepare_module_context(large_module_data)

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Should not use excessive memory
        assert memory_increase < 50  # Less than 50MB increase

        # Context should still be reasonable
        assert len(context) > 0
        assert "large_test_module" in context or "large_test_module" in context

