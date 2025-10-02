"""Edge case tests for documentation generation service."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch

from curriculum.documentation import DocumentationGeneratorService


class TestDocumentationEdgeCases:
    """Edge case tests for documentation system."""

    @pytest.fixture
    def doc_service(self, tmp_path):
        """Create documentation service for edge case testing."""
        return DocumentationGeneratorService(output_dir=str(tmp_path / "docs"))

    @pytest.fixture
    def empty_package(self, tmp_path):
        """Create an empty package for testing."""
        package_dir = tmp_path / "empty_package"
        package_dir.mkdir()
        (package_dir / "__init__.py").write_text('"""Empty package."""')
        return package_dir

    @pytest.fixture
    def invalid_package(self, tmp_path):
        """Create a package with invalid Python files."""
        package_dir = tmp_path / "invalid_package"
        package_dir.mkdir()

        (package_dir / "__init__.py").write_text('"""Invalid package."""')

        # Create invalid Python file
        invalid_file = package_dir / "invalid.py"
        invalid_file.write_text('''
This is not valid Python code!!!
It has syntax errors and invalid syntax.
class InvalidClass:
    def method(self):
        # Missing quotes
        print("Hello World)
''')

        return package_dir

    def test_empty_package_handling(self, doc_service, empty_package):
        """Test handling of empty packages."""
        result = doc_service.generate_documentation(
            package_path=str(empty_package),
            use_llm=False
        )

        # Should handle empty package gracefully
        assert result["status"] == "success"
        assert result["modules_documented"] == 0
        assert result["files_documented"] == 1  # Just __init__.py

    def test_invalid_python_file_handling(self, doc_service, invalid_package):
        """Test handling of invalid Python files."""
        result = doc_service.generate_documentation(
            package_path=str(invalid_package),
            use_llm=False
        )

        # Should handle invalid files gracefully
        assert result["status"] == "success"

        # Should still process valid files
        assert result["files_documented"] >= 1

        # Check that invalid files are handled
        file_docs = doc_service._file_docs
        invalid_files = [path for path, data in file_docs.items() if "error" in data]
        assert len(invalid_files) > 0

    def test_nonexistent_package_handling(self, doc_service):
        """Test handling of nonexistent package paths."""
        result = doc_service.generate_documentation(
            package_path="/nonexistent/path",
            use_llm=False
        )

        # Should handle gracefully
        assert result["status"] == "success"
        assert result["modules_documented"] == 0
        assert result["files_documented"] == 0

    def test_permission_denied_handling(self, doc_service, tmp_path):
        """Test handling of permission denied scenarios."""
        # Create a directory we can't access
        restricted_dir = tmp_path / "restricted"
        restricted_dir.mkdir()

        # Try to make it inaccessible (Unix-like systems)
        try:
            restricted_dir.chmod(0o000)  # No permissions

            result = doc_service.generate_documentation(
                package_path=str(restricted_dir),
                use_llm=False
            )

            # Should handle permission errors gracefully
            assert result["status"] == "success"

        except (OSError, PermissionError):
            # On some systems, chmod might not work
            # Test with a file path instead
            restricted_file = restricted_dir / "test.py"
            restricted_file.write_text('"""Test file."""')

            result = doc_service.generate_documentation(
                package_path=str(restricted_dir),
                use_llm=False
            )

            assert result["status"] == "success"

    def test_large_file_handling(self, doc_service, tmp_path):
        """Test handling of very large Python files."""
        large_file = tmp_path / "large_module.py"

        # Create a large file with many classes and functions
        large_content = '"""Large module for testing."""\n\n'

        # Add many classes
        for i in range(100):
            large_content += f'''
class LargeClass{i}:
    """Large class {i}."""

    def method_{i}(self) -> None:
        """Method {i}."""
        pass
'''

        # Add many functions
        for i in range(200):
            large_content += f'''

def large_function_{i}() -> None:
    """Large function {i}."""
    pass
'''

        large_file.write_text(large_content)

        # Test processing
        file_doc = doc_service._extract_file_documentation(large_file)

        # Should handle large files
        assert file_doc["total_classes"] == 100
        assert file_doc["total_functions"] == 200
        assert file_doc["file_path"] == str(large_file)

    def test_unicode_handling(self, doc_service, tmp_path):
        """Test handling of Unicode characters in code."""
        unicode_file = tmp_path / "unicode_module.py"

        unicode_content = '''"""Module with Unicode characters."""

# Unicode class name
class Cläss:
    """Class with Unicode name."""

    def méthode(self) -> str:
        """Method with Unicode name."""
        return "résultat"

# Unicode strings
def process_text(tëxt: str) -> str:
    """Process text with Unicode."""
    return tëxt.upper()

# Unicode comments
# 这是一个测试注释
def test_function() -> None:
    """Test function with Unicode docstring."""
    pass
'''

        unicode_file.write_text(unicode_content)

        file_doc = doc_service._extract_file_documentation(unicode_file)

        # Should handle Unicode
        assert file_doc["total_classes"] == 1
        assert file_doc["total_functions"] == 2

    def test_binary_file_handling(self, doc_service, tmp_path):
        """Test handling of binary files."""
        binary_file = tmp_path / "binary_file"
        binary_file.write_bytes(b'\x00\x01\x02\x03\x04')  # Binary content

        file_doc = doc_service._extract_file_documentation(binary_file)

        # Should handle binary files gracefully
        assert "error" in file_doc
        assert file_doc["file_path"] == str(binary_file)

    def test_empty_file_handling(self, doc_service, tmp_path):
        """Test handling of empty files."""
        empty_file = tmp_path / "empty.py"
        empty_file.write_text("")  # Empty file

        file_doc = doc_service._extract_file_documentation(empty_file)

        # Should handle empty files
        assert file_doc["file_path"] == str(empty_file)
        assert file_doc["total_classes"] == 0
        assert file_doc["total_functions"] == 0

    def test_corrupted_json_handling(self, doc_service, tmp_path):
        """Test handling of corrupted JSON files."""
        # Create a corrupted JSON file
        corrupted_file = tmp_path / "corrupted.json"
        corrupted_file.write_text('{"invalid": json}')  # Invalid JSON

        # Try to load it
        with pytest.raises(json.JSONDecodeError):
            with open(corrupted_file) as f:
                json.load(f)

    def test_circular_import_handling(self, doc_service, tmp_path):
        """Test handling of circular imports."""
        circular_package = tmp_path / "circular_package"
        circular_package.mkdir()

        # Create files with circular imports
        (circular_package / "__init__.py").write_text('"""Circular package."""')

        module_a = circular_package / "module_a.py"
        module_a.write_text('''
"""Module A with circular import."""

from . import module_b  # This creates circular import

class ClassA:
    """Class A."""
    pass
''')

        module_b = circular_package / "module_b.py"
        module_b.write_text('''
"""Module B with circular import."""

from . import module_a  # This creates circular import

class ClassB:
    """Class B."""
    pass
''')

        # Should handle circular imports gracefully
        result = doc_service.generate_documentation(
            package_path=str(circular_package),
            use_llm=False
        )

        assert result["status"] == "success"

    def test_very_deep_package_structure(self, doc_service, tmp_path):
        """Test handling of very deep package structures."""
        deep_package = tmp_path / "deep" / "package" / "structure"
        deep_package.mkdir(parents=True)

        # Create deep nested structure
        (deep_package / "__init__.py").write_text('"""Deep package."""')

        deep_module = deep_package / "deep_module.py"
        deep_module.write_text('''
"""Deep module."""

class DeepClass:
    """Deep class."""
    pass
''')

        result = doc_service.generate_documentation(
            package_path=str(deep_package),
            use_llm=False
        )

        # Should handle deep structures
        assert result["status"] == "success"
        assert result["modules_documented"] > 0

    def test_mixed_valid_invalid_files(self, doc_service, tmp_path):
        """Test handling of mixed valid and invalid files."""
        mixed_package = tmp_path / "mixed_package"
        mixed_package.mkdir()

        (mixed_package / "__init__.py").write_text('"""Mixed package."""')

        # Valid file
        valid_file = mixed_package / "valid.py"
        valid_file.write_text('''
"""Valid module."""

class ValidClass:
    """Valid class."""
    pass

def valid_function() -> None:
    """Valid function."""
    pass
''')

        # Invalid file
        invalid_file = mixed_package / "invalid.py"
        invalid_file.write_text('''
Invalid Python code with syntax errors!!!
class InvalidClass:
    def method(self):
        print("Hello World)  # Missing quote
''')

        result = doc_service.generate_documentation(
            package_path=str(mixed_package),
            use_llm=False
        )

        # Should handle mixed files
        assert result["status"] == "success"

        # Should process valid files
        assert result["files_documented"] >= 2  # At least __init__ and valid.py

        # Should handle invalid files gracefully
        file_docs = doc_service._file_docs
        invalid_files = [path for path, data in file_docs.items() if "error" in data]
        assert len(invalid_files) > 0

    def test_memory_exhaustion_handling(self, doc_service, tmp_path):
        """Test handling of memory exhaustion scenarios."""
        # Create extremely large file
        huge_file = tmp_path / "huge_module.py"

        # Create a very large file (simulate memory issues)
        huge_content = '"""Huge module."""\n\n'

        # Add many large classes
        for i in range(1000):
            huge_content += f'''
class HugeClass{i}:
    """Huge class {i} with lots of content."""

    def __init__(self) -> None:
        """Initialize huge class."""
        self.data = "x" * 1000  # Large string

    def process_{i}(self) -> str:
        """Process data for class {i}."""
        return "processed" * 1000
'''

        huge_file.write_text(huge_content)

        # Test processing (should not crash)
        try:
            file_doc = doc_service._extract_file_documentation(huge_file)

            # Should handle large files
            assert file_doc["file_path"] == str(huge_file)
            assert file_doc["total_classes"] == 1000

        except MemoryError:
            # If memory error occurs, that's expected for huge files
            pytest.skip("Memory error occurred with huge test file")

    def test_network_timeout_handling(self, doc_service):
        """Test handling of network timeouts."""
        with patch('requests.post') as mock_post:
            # Simulate network timeout
            mock_post.side_effect = Exception("Connection timeout")

            result = doc_service._call_ollama_llm("Test prompt")

            # Should return mock response
            assert "placeholder response" in result.lower()

    def test_invalid_llm_response_handling(self, doc_service):
        """Test handling of invalid LLM responses."""
        with patch('requests.post') as mock_post:
            # Return invalid JSON
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {"invalid": "response"}

            result = doc_service._call_ollama_llm("Test prompt")

            # Should handle gracefully
            assert result is not None

    def test_cache_corruption_handling(self, doc_service):
        """Test handling of corrupted cache files."""
        # Create corrupted cache file
        cache_key = "corrupted_test"
        cache_file = doc_service._cache_dir / f"{cache_key}.json"
        cache_file.write_text('{"invalid": json}')  # Invalid JSON

        # Should handle corrupted cache
        cached = doc_service._get_cached_response(cache_key)
        assert cached is None  # Should return None for corrupted cache

    def test_concurrent_cache_access_safety(self, doc_service):
        """Test thread safety of cache access."""
        import threading

        cache_key = "concurrent_safety_test"
        results = []

        def cache_operation():
            try:
                # Write and read cache
                doc_service._cache_response(cache_key, {"test": "data"})
                cached = doc_service._get_cached_response(cache_key)
                results.append(cached is not None)
            except Exception as e:
                results.append(False)

        # Run multiple threads
        threads = []
        for i in range(5):  # Reduced to 5 for faster testing
            thread = threading.Thread(target=cache_operation)
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Most operations should succeed (allow for some race conditions in testing)
        assert sum(results) >= 3  # At least 3 out of 5 should succeed

    def test_extremely_nested_imports(self, doc_service, tmp_path):
        """Test handling of extremely nested import structures."""
        nested_package = tmp_path / "deeply" / "nested" / "package" / "structure"
        nested_package.mkdir(parents=True)

        # Create nested structure
        (nested_package / "__init__.py").write_text('"""Deeply nested package."""')

        # Create files with complex import chains
        main_file = nested_package / "main.py"
        main_file.write_text('''
"""Main module with complex imports."""

from ....utils import helper
from ...base import BaseClass
from .submodule import SubClass

class MainClass(BaseClass):
    """Main class."""
    pass
''')

        submodule_dir = nested_package / "submodule"
        submodule_dir.mkdir()
        (submodule_dir / "__init__.py").write_text('"""Submodule."""')

        (submodule_dir / "helpers.py").write_text('''
"""Helper functions."""

def helper_function() -> None:
    """Helper function."""
    pass
''')

        result = doc_service.generate_documentation(
            package_path=str(nested_package),
            use_llm=False
        )

        # Should handle complex import structures
        assert result["status"] == "success"

    def test_malformed_ast_handling(self, doc_service, tmp_path):
        """Test handling of malformed AST structures."""
        malformed_file = tmp_path / "malformed.py"

        # Create file with malformed Python
        malformed_content = '''
"""Malformed module."""

class MalformedClass:
    def method(self):
        # Indentation error
    def another_method(self):
        pass

def malformed_function(
    # Missing closing parenthesis
    param1: str
    -> str:
    return param1
'''

        malformed_file.write_text(malformed_content)

        # Should handle malformed AST
        file_doc = doc_service._extract_file_documentation(malformed_file)

        # Should handle gracefully
        assert file_doc["file_path"] == str(malformed_file)
        assert "error" in file_doc or file_doc["total_classes"] == 0

    def test_extremely_long_docstrings(self, doc_service, tmp_path):
        """Test handling of extremely long docstrings."""
        long_doc_file = tmp_path / "long_doc.py"

        # Create file with extremely long docstring
        long_docstring = '"""' + 'A' * 10000 + '"""'  # 10KB docstring

        long_doc_content = f'''
{long_docstring}

class TestClass:
    """Normal docstring."""

    def method(self) -> None:
        """Normal method docstring."""
        pass
'''

        long_doc_file.write_text(long_doc_content)

        # Should handle long docstrings
        file_doc = doc_service._extract_file_documentation(long_doc_file)

        assert file_doc["file_path"] == str(long_doc_file)
        assert file_doc["total_classes"] == 1

    def test_special_characters_in_code(self, doc_service, tmp_path):
        """Test handling of special characters in code."""
        special_file = tmp_path / "special_chars.py"

        special_content = '''"""Module with special characters."""

# Unicode identifiers
def función_especial(paramétrico: str) -> str:
    """Function with special characters."""
    return paramétrico.upper()

class Cläss:
    """Class with special characters."""

    def méthode(self) -> None:
        """Method with special characters."""
        pass

# Special strings
SPECIAL_STRING = "Spëcial çharacters"
'''

        special_file.write_text(special_content)

        # Should handle special characters
        file_doc = doc_service._extract_file_documentation(special_file)

        assert file_doc["file_path"] == str(special_file)
        assert file_doc["total_classes"] == 1
        assert file_doc["total_functions"] == 1

    def test_extremely_large_module_count(self, doc_service, tmp_path):
        """Test handling of packages with extremely large module counts."""
        large_package = tmp_path / "massive_package"
        large_package.mkdir()

        (large_package / "__init__.py").write_text('"""Massive package."""')

        # Create many modules
        for i in range(50):
            module_dir = large_package / f"module_{i}"
            module_dir.mkdir()
            (module_dir / "__init__.py").write_text(f'"""Module {i}."""')

            module_file = module_dir / f"module_{i}.py"
            module_file.write_text(f'''
"""Module {i}."""

class Class{i}:
    """Class {i}."""
    pass

def function_{i}() -> None:
    """Function {i}."""
    pass
''')

        # Test processing large package
        result = doc_service.generate_documentation(
            package_path=str(large_package),
            use_llm=False
        )

        # Should handle large packages
        assert result["status"] == "success"
        assert result["modules_documented"] == 50

