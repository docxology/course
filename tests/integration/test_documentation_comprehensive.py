"""Comprehensive tests for the complete documentation system."""

import json
import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

from curriculum.documentation import DocumentationGeneratorService


@pytest.mark.integration
class TestDocumentationSystemComprehensive:
    """Comprehensive tests for the entire documentation system."""

    @pytest.fixture
    def doc_service(self):
        """Create documentation service for comprehensive testing."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield DocumentationGeneratorService(output_dir=tmp_dir)

    @pytest.fixture
    def sample_package(self, tmp_path):
        """Create a comprehensive sample package for testing."""
        package_dir = tmp_path / "test_package"
        package_dir.mkdir()

        # Create __init__.py
        (package_dir / "__init__.py").write_text('''"""Test package for comprehensive testing."""

from typing import List, Dict, Optional

__version__ = "1.0.0"
__author__ = "Test Author"
''')

        # Create main module
        main_module = package_dir / "main_module.py"
        main_module.write_text('''"""Main module with comprehensive features."""

from typing import Dict, List, Optional
import json
import asyncio

class DataProcessor:
    """Process data with comprehensive methods."""

    def __init__(self, config: Dict[str, str]) -> None:
        """Initialize with configuration."""
        self.config = config
        self.processed_items = 0

    def process_data(self, data: List[Dict]) -> List[Dict]:
        """Process a list of data items."""
        processed = []
        for item in data:
            processed_item = self._transform_item(item)
            processed.append(processed_item)
            self.processed_items += 1
        return processed

    def _transform_item(self, item: Dict) -> Dict:
        """Transform a single data item."""
        return {k: v.upper() if isinstance(v, str) else v for k, v in item.items()}

    async def async_process(self, data: List[Dict]) -> Dict[str, int]:
        """Asynchronously process data and return statistics."""
        total_items = len(data)
        processed_count = 0

        for item in data:
            await self._async_transform(item)
            processed_count += 1

        return {
            "total": total_items,
            "processed": processed_count,
            "success_rate": processed_count / total_items if total_items > 0 else 0
        }

    async def _async_transform(self, item: Dict) -> None:
        """Async transformation helper."""
        pass

def utility_function(items: List[str], separator: str = ",") -> str:
    """Join items with separator."""
    return separator.join(items)

def validate_data(data: Dict) -> bool:
    """Validate data structure."""
    required_keys = ["id", "name", "value"]
    return all(key in data for key in required_keys)

class HelperClass:
    """Helper class for various utilities."""

    def __init__(self, name: str) -> None:
        """Initialize helper."""
        self.name = name

    def get_info(self) -> Dict[str, str]:
        """Get helper information."""
        return {"name": self.name, "type": "helper"}
''')

        # Create submodule
        submodule_dir = package_dir / "submodule"
        submodule_dir.mkdir()

        (submodule_dir / "__init__.py").write_text('''"""Submodule for additional functionality."""''')

        (submodule_dir / "helpers.py").write_text('''"""Helper functions for the submodule."""

from typing import Optional

class HelperClass:
    """Helper class for various utilities."""

    def __init__(self, name: str) -> None:
        """Initialize helper."""
        self.name = name

    def get_info(self) -> Dict[str, str]:
        """Get helper information."""
        return {"name": self.name, "type": "helper"}

def helper_function(value: str, default: Optional[str] = None) -> str:
    """Return value or default."""
    return value if value else (default or "")
''')

        return package_dir

    def test_complete_system_workflow(self, doc_service, sample_package):
        """Test the complete documentation generation workflow."""
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            # Mock all LLM calls
            def mock_llm_call(prompt, model="llama3.1", temperature=0.3):
                return json.dumps({
                    "overview": "Comprehensive analysis",
                    "key_classes": [{"name": "DataProcessor", "purpose": "Process data"}],
                    "functionality": ["Data processing", "Validation"],
                    "dependencies": ["typing", "json"],
                    "usage_hints": ["Use DataProcessor for batch operations"]
                })

            mock_llm.side_effect = mock_llm_call

            # Generate documentation
            result = doc_service.generate_documentation(
                package_path=str(sample_package),
                use_llm=True
            )

            # Verify complete workflow
            assert result["status"] == "success"
            assert result["modules_documented"] == 2  # main_module and submodule
            assert result["files_documented"] == 4  # 2 modules + 2 __init__ files
            assert result["llm_summaries_generated"] == 4  # package + 2 modules + 1 file

            # Verify caching
            cache_files = len(list(doc_service._cache_dir.glob("*.json")))
            assert cache_files > 0  # Cache should be populated

            # Verify Markdown export
            assert "llm_markdown_exports" in result
            assert result["llm_markdown_exports"]["standalone_files"] > 0

            # Verify search index
            assert "search_index" in result
            assert result["search_index"]["generated"] is True

    def test_system_resilience(self, doc_service):
        """Test system resilience under various conditions."""
        # Test with invalid package path
        result = doc_service.generate_documentation(
            package_path="/nonexistent/path",
            use_llm=False
        )
        assert result["status"] == "error"
        assert "does not exist" in result["error"]

        # Test with LLM failures
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.side_effect = Exception("LLM Error")

            result = doc_service.generate_documentation(
                package_path="src/curriculum/core",
                use_llm=True
            )

            # Should still complete with fallback responses
            assert result["status"] == "success"

    def test_performance_benchmarks(self, doc_service, sample_package):
        """Test performance benchmarks for the system."""
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Performance test"})

            # Measure generation time
            start_time = time.time()

            result = doc_service.generate_documentation(
                package_path=str(sample_package),
                use_llm=True
            )

            generation_time = time.time() - start_time

            # Should complete in reasonable time
            assert generation_time < 30.0  # Less than 30 seconds
            assert result["status"] == "success"
            assert result["generation_duration_seconds"] == generation_time

    def test_configuration_validation(self, doc_service):
        """Test configuration validation and error handling."""
        # Test invalid concurrent calls
        doc_service._max_concurrent_llm_calls = 0
        doc_service._validate_configuration()

        # Should be corrected to default
        assert doc_service._max_concurrent_llm_calls == 5

        # Test invalid timeout
        doc_service._llm_timeout_seconds = -1
        doc_service._validate_configuration()

        # Should be corrected to default
        assert doc_service._llm_timeout_seconds == 60

        # Test invalid cache TTL
        doc_service._cache_ttl_days = 0
        doc_service._validate_configuration()

        # Should be corrected to default
        assert doc_service._cache_ttl_days == 30

    def test_model_configuration_validation(self, doc_service):
        """Test model configuration validation."""
        # Test invalid model config
        invalid_config = {
            "test_type": "not_a_dict"
        }

        validated = doc_service._validate_model_config(invalid_config)
        assert len(validated) == 0  # Should filter out invalid configs

        # Test config with missing keys
        incomplete_config = {
            "test_type": {"model": "test_model"}  # Missing temperature and max_tokens
        }

        validated = doc_service._validate_model_config(incomplete_config)
        assert len(validated) == 0  # Should filter out incomplete configs

        # Test config with invalid values
        invalid_values_config = {
            "test_type": {
                "model": "test_model",
                "temperature": 5.0,  # Invalid temperature
                "max_tokens": -1     # Invalid max_tokens
            }
        }

        validated = doc_service._validate_model_config(invalid_values_config)
        assert "test_type" in validated
        assert validated["test_type"]["temperature"] == 0.3  # Should be corrected
        assert validated["test_type"]["max_tokens"] == 1500  # Should be corrected

    def test_cache_system_comprehensive(self, doc_service):
        """Test comprehensive cache system functionality."""
        # Test cache key generation
        prompt1 = "Test prompt 1"
        prompt2 = "Test prompt 2"
        model = "test_model"

        key1 = doc_service._get_cache_key(prompt1, model)
        key2 = doc_service._get_cache_key(prompt2, model)

        assert key1 != key2  # Different prompts should have different keys
        assert len(key1) == 64  # SHA256 hash length

        # Test cache storage and retrieval
        response_data = {"response": "Test response", "model": model}
        doc_service._cache_response(key1, response_data)

        cached = doc_service._get_cached_response(key1)
        assert cached is not None
        assert cached["response"] == "Test response"

        # Test cache miss
        cached = doc_service._get_cached_response("nonexistent_key")
        assert cached is None

    def test_multi_model_strategy(self, doc_service):
        """Test multi-model strategy functionality."""
        # Test model selection for different analysis types
        package_config = doc_service._select_model_for_analysis("package_overview")
        assert package_config["model"] == "gemma2:2b"
        assert package_config["temperature"] == 0.3

        module_config = doc_service._select_model_for_analysis("module_analysis")
        assert module_config["model"] == "llama3.1:latest"
        assert module_config["temperature"] == 0.2

        file_config = doc_service._select_model_for_analysis("file_deep_analysis")
        assert file_config["model"] == "codellama:latest"
        assert file_config["temperature"] == 0.1

    def test_search_and_qa_integration(self, doc_service, sample_package):
        """Test search and Q&A integration."""
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Test analysis"})

            # Generate documentation
            doc_service.generate_documentation(
                package_path=str(sample_package),
                use_llm=True
            )

            # Test search functionality
            results = doc_service.search_documentation("DataProcessor", max_results=5)
            assert len(results) > 0

            # Test Q&A functionality
            answer = doc_service.answer_question_about_codebase("What is DataProcessor?")
            assert isinstance(answer, str)
            assert len(answer) > 0

    def test_error_handling_comprehensive(self, doc_service):
        """Test comprehensive error handling."""
        # Test with empty prompt
        result = doc_service._call_ollama_llm("")
        assert "placeholder response" in result.lower()

        # Test with None prompt
        result = doc_service._call_ollama_llm(None)
        assert "placeholder response" in result.lower()

        # Test with invalid model config
        invalid_config = {
            "invalid_type": {"model": "test"}
        }
        validated = doc_service._validate_model_config(invalid_config)
        assert len(validated) == 0

    def test_memory_usage_comprehensive(self, doc_service, sample_package):
        """Test memory usage throughout the system."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Memory test"})

            # Generate documentation
            doc_service.generate_documentation(
                package_path=str(sample_package),
                use_llm=True
            )

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Should not use excessive memory
        assert memory_increase < 150  # Less than 150MB increase

        # Verify all data structures are populated
        assert len(doc_service._module_docs) > 0
        assert len(doc_service._file_docs) > 0
        assert len(doc_service._llm_summaries) > 0

    def test_output_format_consistency(self, doc_service, sample_package):
        """Test output format consistency across all components."""
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Format test"})

            # Generate documentation
            doc_service.generate_documentation(
                package_path=str(sample_package),
                use_llm=True
            )

            # Test JSON export
            json_file = doc_service.export_documentation(format="json")
            assert Path(json_file).exists()

            with open(json_file) as f:
                json_data = json.load(f)
                assert "modules" in json_data
                assert "files" in json_data
                assert "llm_summaries" in json_data

            # Test Markdown export
            md_file = doc_service.export_documentation(format="markdown")
            assert Path(md_file).exists()

            with open(md_file) as f:
                md_content = f.read()
                assert "# Complete System Documentation" in md_content

    def test_configuration_persistence(self, doc_service):
        """Test configuration persistence across service instances."""
        # Modify configuration
        doc_service._max_concurrent_llm_calls = 10
        doc_service._llm_timeout_seconds = 120
        doc_service._cache_ttl_days = 60

        # Create new service instance with same output directory
        new_service = DocumentationGeneratorService(output_dir=str(doc_service.output_dir))

        # Configuration should be reset to defaults
        assert new_service._max_concurrent_llm_calls == 5
        assert new_service._llm_timeout_seconds == 60
        assert new_service._cache_ttl_days == 30

    def test_cache_invalidation_on_changes(self, doc_service, sample_package):
        """Test cache invalidation when source files change."""
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Cache test"})

            # First generation
            doc_service.generate_documentation(
                package_path=str(sample_package),
                use_llm=True
            )

            cache_files_before = len(list(doc_service._cache_dir.glob("*.json")))

            # Modify a source file
            main_module = sample_package / "main_module.py"
            original_content = main_module.read_text()
            main_module.write_text(original_content + "\n# Modified")

            # Second generation should invalidate cache
            doc_service.generate_documentation(
                package_path=str(sample_package),
                use_llm=True
            )

            cache_files_after = len(list(doc_service._cache_dir.glob("*.json")))

            # Cache should be repopulated with new responses
            assert cache_files_after >= cache_files_before

    def test_system_scalability(self, doc_service, tmp_path):
        """Test system scalability with large codebases."""
        # Create a large test package
        large_package = tmp_path / "large_test_package"
        large_package.mkdir()

        # Create 10 modules with 5 files each
        for module_idx in range(10):
            module_dir = large_package / f"module_{module_idx}"
            module_dir.mkdir()

            (module_dir / "__init__.py").write_text(f'"""Module {module_idx}."""')

            for file_idx in range(5):
                file_content = f'''"""File {file_idx} in module {module_idx}."""

class Class{file_idx}:
    """Class {file_idx}."""

    def method_{file_idx}(self) -> None:
        """Method {file_idx}."""
        pass

def function_{file_idx}() -> None:
    """Function {file_idx}."""
    pass
'''
                (module_dir / f"file_{file_idx}.py").write_text(file_content)

        # Test scalability
        result = doc_service.generate_documentation(
            package_path=str(large_package),
            use_llm=False
        )

        # Should handle large packages
        assert result["status"] == "success"
        assert result["modules_documented"] == 10
        assert result["files_documented"] == 60  # 10 modules * 6 files each

    def test_concurrent_access_safety(self, doc_service, sample_package):
        """Test thread safety and concurrent access."""
        import threading

        results = []
        errors = []

        def generate_docs():
            try:
                with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
                    mock_llm.return_value = json.dumps({"overview": "Concurrent test"})

                    result = doc_service.generate_documentation(
                        package_path=str(sample_package),
                        use_llm=True
                    )

                    results.append(result["status"])
            except Exception as e:
                errors.append(str(e))

        # Run multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=generate_docs)
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Should complete without errors
        assert len(errors) == 0
        assert all(status == "success" for status in results)

    def test_system_recovery(self, doc_service):
        """Test system recovery from various failure scenarios."""
        # Test with partial failures
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            call_count = 0

            def mock_llm_call(prompt, model="llama3.1", temperature=0.3):
                nonlocal call_count
                call_count += 1

                # Fail on every other call
                if call_count % 2 == 0:
                    raise Exception("Simulated LLM failure")
                return json.dumps({"overview": f"Response {call_count}"})

            mock_llm.side_effect = mock_llm_call

            # Generate documentation despite some failures
            result = doc_service.generate_documentation(
                package_path="src/curriculum/core",
                use_llm=True
            )

            # Should still complete successfully
            assert result["status"] == "success"

    def test_output_validation(self, doc_service, sample_package):
        """Test output validation and consistency."""
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Validation test"})

            # Generate documentation
            doc_service.generate_documentation(
                package_path=str(sample_package),
                use_llm=True
            )

            # Validate JSON export
            json_file = doc_service.export_documentation(format="json")
            with open(json_file) as f:
                json_data = json.load(f)

            # Should have consistent structure
            assert "modules" in json_data
            assert "files" in json_data
            assert "llm_summaries" in json_data
            assert "generated_at" in json_data

            # Validate Markdown export
            md_file = doc_service.export_documentation(format="markdown")
            with open(md_file) as f:
                md_content = f.read()

            # Should have consistent structure
            assert "# Complete System Documentation" in md_content
            assert "Generated:" in md_content

    def test_cache_system_robustness(self, doc_service):
        """Test cache system robustness under various conditions."""
        # Test cache with very large responses
        large_response = {"response": "x" * 10000, "model": "test"}  # 10KB response
        cache_key = doc_service._get_cache_key("Large response test", "test_model")

        doc_service._cache_response(cache_key, large_response)

        # Should handle large responses
        cached = doc_service._get_cached_response(cache_key)
        assert cached is not None
        assert len(cached["response"]) == 10000

        # Test cache with special characters
        special_response = {"response": "Response with spëcial çharacters! 🚀", "model": "test"}
        special_key = doc_service._get_cache_key("Special characters test", "test_model")

        doc_service._cache_response(special_key, special_response)

        cached = doc_service._get_cached_response(special_key)
        assert cached is not None
        assert "spëcial çharacters" in cached["response"]

    def test_system_integration_end_to_end(self, doc_service, sample_package):
        """Test complete end-to-end system integration."""
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            # Mock all LLM responses
            def mock_llm_call(prompt, model="llama3.1", temperature=0.3):
                return json.dumps({
                    "overview": "End-to-end integration test",
                    "key_classes": [{"name": "TestClass", "purpose": "Test class"}],
                    "functionality": ["Testing", "Integration"],
                    "dependencies": ["unittest", "pytest"],
                    "usage_hints": ["Use for comprehensive testing"]
                })

            mock_llm.side_effect = mock_llm_call

            # Complete workflow
            result = doc_service.generate_documentation(
                package_path=str(sample_package),
                use_llm=True
            )

            # Verify complete workflow
            assert result["status"] == "success"
            assert result["modules_documented"] > 0
            assert result["files_documented"] > 0
            assert result["llm_summaries_generated"] > 0

            # Verify caching
            cache_files = len(list(doc_service._cache_dir.glob("*.json")))
            assert cache_files > 0

            # Verify Markdown export
            assert "llm_markdown_exports" in result
            assert result["llm_markdown_exports"]["standalone_files"] > 0

            # Verify search index
            assert "search_index" in result
            assert result["search_index"]["generated"] is True

            # Test search functionality
            search_results = doc_service.search_documentation("TestClass", max_results=5)
            assert len(search_results) > 0

            # Test Q&A functionality
            qa_answer = doc_service.answer_question_about_codebase("What is the main class?")
            assert isinstance(qa_answer, str)
            assert len(qa_answer) > 0

    def test_system_performance_under_load(self, doc_service, sample_package):
        """Test system performance under load conditions."""
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Load test"})

            # Multiple generations to test caching and performance
            for i in range(3):
                result = doc_service.generate_documentation(
                    package_path=str(sample_package),
                    use_llm=True
                )

                assert result["status"] == "success"

                # Performance should be consistent
                generation_time = result["generation_duration_seconds"]
                assert generation_time < 30.0  # Less than 30 seconds per generation

    def test_system_resource_management(self, doc_service, sample_package):
        """Test resource management and cleanup."""
        initial_cache_files = len(list(doc_service._cache_dir.glob("*.json")))

        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Resource test"})

            # Generate documentation
            doc_service.generate_documentation(
                package_path=str(sample_package),
                use_llm=True
            )

        final_cache_files = len(list(doc_service._cache_dir.glob("*.json")))

        # Cache should be populated but not excessive
        assert final_cache_files > initial_cache_files
        assert final_cache_files < 100  # Should not create excessive cache files

        # Test cleanup by creating new service
        new_service = DocumentationGeneratorService(output_dir=str(doc_service.output_dir))

        # Should have clean state
        assert len(new_service._module_docs) == 0
        assert len(new_service._file_docs) == 0
        assert len(new_service._llm_summaries) == 0

    def test_system_error_recovery(self, doc_service):
        """Test system error recovery capabilities."""
        # Test with various error conditions
        error_scenarios = [
            # Invalid package path
            ("/nonexistent/path", False, "does not exist"),

            # Empty package
            ("", False, "does not exist"),

            # LLM failures
            ("src/curriculum/core", True, "LLM Error")
        ]

        for package_path, use_llm, expected_error in error_scenarios:
            with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
                if use_llm and "LLM Error" in expected_error:
                    mock_llm.side_effect = Exception(expected_error)

                result = doc_service.generate_documentation(
                    package_path=package_path,
                    use_llm=use_llm
                )

                # Should handle errors gracefully
                if "does not exist" in expected_error:
                    assert result["status"] == "error"
                    assert expected_error in result["error"]
                else:
                    # Should complete with fallback responses
                    assert result["status"] == "success"

    def test_system_configuration_flexibility(self, doc_service):
        """Test configuration flexibility and customization."""
        # Test different concurrent call limits
        for concurrent_limit in [1, 3, 5, 10]:
            doc_service._max_concurrent_llm_calls = concurrent_limit
            doc_service._validate_configuration()

            # Should accept valid limits
            assert doc_service._max_concurrent_llm_calls == concurrent_limit

        # Test different timeout values
        for timeout in [30, 60, 120, 300]:
            doc_service._llm_timeout_seconds = timeout
            doc_service._validate_configuration()

            # Should accept valid timeouts
            assert doc_service._llm_timeout_seconds == timeout

        # Test different cache TTL values
        for ttl in [1, 7, 30, 90]:
            doc_service._cache_ttl_days = ttl
            doc_service._validate_configuration()

            # Should accept valid TTL values
            assert doc_service._cache_ttl_days == ttl

    def test_system_output_completeness(self, doc_service, sample_package):
        """Test completeness of system outputs."""
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Completeness test"})

            # Generate documentation
            result = doc_service.generate_documentation(
                package_path=str(sample_package),
                use_llm=True
            )

            # Verify all outputs are generated
            assert "modules_documented" in result
            assert "files_documented" in result
            assert "methods_documented" in result
            assert "llm_summaries_generated" in result
            assert "generation_duration_seconds" in result

            # Verify LLM outputs
            assert "llm_markdown_exports" in result
            assert "search_index" in result

            # Verify file system outputs
            assert (doc_service.output_dir / "modules").exists()
            assert (doc_service.output_dir / "files").exists()
            assert (doc_service.output_dir / "llm_analysis").exists()
            assert (doc_service.output_dir / "llm_analysis_md").exists()

    def test_system_logging_and_monitoring(self, doc_service, sample_package):
        """Test logging and monitoring capabilities."""
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Logging test"})

            # Generate documentation
            doc_service.generate_documentation(
                package_path=str(sample_package),
                use_llm=True
            )

            # Check that log file was created
            log_file = doc_service.output_dir / "documentation.log"
            assert log_file.exists()

            # Check log content
            log_content = log_file.read_text()
            assert "DocumentationGeneratorService initialized" in log_content
            assert "Extracting package documentation" in log_content
            assert "Generating LLM summaries" in log_content

    def test_system_backward_compatibility(self, doc_service, sample_package):
        """Test backward compatibility with existing functionality."""
        # Test without LLM (should work as before)
        result = doc_service.generate_documentation(
            package_path=str(sample_package),
            use_llm=False
        )

        assert result["status"] == "success"
        assert result["modules_documented"] > 0
        assert result["files_documented"] > 0
        assert result["llm_summaries_generated"] == 0  # No LLM calls

        # Test with LLM (should work with new features)
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Compatibility test"})

            result = doc_service.generate_documentation(
                package_path=str(sample_package),
                use_llm=True
            )

            assert result["status"] == "success"
            assert result["llm_summaries_generated"] > 0
            assert "llm_markdown_exports" in result
            assert "search_index" in result

    def test_system_extensibility(self, doc_service):
        """Test system extensibility for future features."""
        # Test that new configuration options can be added
        doc_service._custom_feature_enabled = True
        doc_service._custom_feature_config = {"setting": "value"}

        # Should not break existing functionality
        result = doc_service.generate_documentation(
            package_path="src/curriculum/core",
            use_llm=False
        )

        assert result["status"] == "success"

        # Custom features should be preserved
        assert hasattr(doc_service, '_custom_feature_enabled')
        assert doc_service._custom_feature_enabled is True

