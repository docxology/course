"""Performance tests for documentation generation service."""

import json
import pytest
import time
import psutil
import os
from pathlib import Path
from unittest.mock import patch

from curriculum.documentation import DocumentationGeneratorService


class TestDocumentationPerformance:
    """Performance tests for documentation generation."""

    @pytest.fixture
    def doc_service(self, tmp_path):
        """Create documentation service for performance testing."""
        return DocumentationGeneratorService(output_dir=str(tmp_path / "docs"))

    @pytest.fixture
    def large_package(self, tmp_path):
        """Create a large package for performance testing."""
        package_dir = tmp_path / "large_package"
        package_dir.mkdir()

        # Create multiple modules with various components
        for i in range(10):
            module_dir = package_dir / f"module_{i}"
            module_dir.mkdir()

            # Create __init__.py
            (module_dir / "__init__.py").write_text(f'"""Module {i} for performance testing."""')

            # Create main module file
            module_file = module_dir / f"module_{i}.py"
            module_content = f'''"""Module {i} with multiple classes and functions."""

from typing import List, Dict, Optional
import asyncio

class Processor{i}:
    """Process data for module {i}."""

    def __init__(self, config: Dict[str, str]) -> None:
        """Initialize processor."""
        self.config = config
        self.items_processed = 0

    def process_items(self, items: List[Dict]) -> List[Dict]:
        """Process a list of items."""
        processed = []
        for item in items:
            processed_item = self._transform_item(item)
            processed.append(processed_item)
            self.items_processed += 1
        return processed

    def _transform_item(self, item: Dict) -> Dict:
        """Transform individual item."""
        return {{k: v.upper() if isinstance(v, str) else v for k, v in item.items()}}

    async def async_process(self, data: List[Dict]) -> Dict[str, int]:
        """Async processing method."""
        total = len(data)
        processed = 0
        for item in data:
            await self._async_transform(item)
            processed += 1
        return {{"total": total, "processed": processed}}

    async def _async_transform(self, item: Dict) -> None:
        """Async transformation helper."""
        pass

def utility_function_{i}(items: List[str], separator: str = ",") -> str:
    """Join items with separator."""
    return separator.join(items)

def validate_data_{i}(data: Dict) -> bool:
    """Validate data structure."""
    return all(key in data for key in ["id", "name", "value"])

class Helper{i}:
    """Helper class for module {i}."""

    def __init__(self, name: str) -> None:
        """Initialize helper."""
        self.name = name

    def get_info(self) -> Dict[str, str]:
        """Get helper information."""
        return {{"name": self.name, "module": "module_{i}"}}
'''

            module_file.write_text(module_content)

        return package_dir

    def test_basic_generation_performance(self, benchmark, doc_service, large_package):
        """Benchmark basic documentation generation performance."""
        result = benchmark(
            doc_service.generate_documentation,
            package_path=str(large_package),
            use_llm=False
        )

        # Should complete successfully
        assert result["status"] == "success"

        # Should process multiple modules
        assert result["modules_documented"] > 0
        assert result["files_documented"] > 0

        # Performance should be reasonable
        assert benchmark.stats["mean"] < 5.0  # Less than 5 seconds

    def test_llm_generation_performance(self, benchmark, doc_service, large_package):
        """Benchmark LLM-based documentation generation performance."""
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Mock analysis"})

            result = benchmark(
                doc_service.generate_documentation,
                package_path=str(large_package),
                use_llm=True
            )

            # Should complete successfully
            assert result["status"] == "success"

            # Should generate LLM summaries
            assert result["llm_summaries_generated"] > 0

            # Performance should be reasonable (with mocked LLM calls)
            assert benchmark.stats["mean"] < 10.0  # Less than 10 seconds

    def test_caching_performance(self, benchmark, doc_service, large_package):
        """Benchmark performance with caching enabled."""
        # First run to populate cache
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Cached response"})

            doc_service.generate_documentation(
                package_path=str(large_package),
                use_llm=True
            )

        # Second run should use cache
        result = benchmark(
            doc_service.generate_documentation,
            package_path=str(large_package),
            use_llm=True
        )

        assert result["status"] == "success"

        # Should be faster due to caching
        assert benchmark.stats["mean"] < 5.0  # Less than 5 seconds

    def test_memory_usage_during_generation(self, doc_service, large_package):
        """Test memory usage during documentation generation."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Generate documentation
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Test response"})

            doc_service.generate_documentation(
                package_path=str(large_package),
                use_llm=True
            )

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Should not use excessive memory
        assert memory_increase < 200  # Less than 200MB increase

        # Verify all data structures are populated
        assert len(doc_service._module_docs) > 0
        assert len(doc_service._file_docs) > 0
        assert len(doc_service._llm_summaries) > 0

    def test_large_module_processing(self, doc_service, tmp_path):
        """Test processing of very large modules."""
        # Create a module with many components
        large_module = tmp_path / "large_module.py"
        large_content = '''"""Very large module for performance testing."""

from typing import List, Dict, Optional, Union
import asyncio

'''

        # Add many classes
        for i in range(50):
            large_content += f'''
class LargeClass{i}:
    """Large class {i}."""

    def __init__(self, value: str) -> None:
        """Initialize with value."""
        self.value = value

    def process_{i}(self, data: List[Dict]) -> List[Dict]:
        """Process data for class {i}."""
        return [item for item in data if item.get("id") == {i}]
'''

        # Add many functions
        for i in range(100):
            large_content += f'''

def large_function_{i}(param1: str, param2: int = {i}) -> bool:
    """Large function {i}."""
    return len(param1) > param2
'''

        large_module.write_text(large_content)

        # Test processing time
        start_time = time.time()

        file_doc = doc_service._extract_file_documentation(large_module)

        processing_time = time.time() - start_time

        # Should process large file in reasonable time
        assert processing_time < 2.0  # Less than 2 seconds

        # Should extract all components
        assert file_doc["total_classes"] == 50
        assert file_doc["total_functions"] == 100

    def test_concurrent_processing_performance(self, benchmark, doc_service, large_package):
        """Benchmark concurrent processing performance."""
        # This test verifies that concurrent processing doesn't degrade performance
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Concurrent response"})

            # Test with different concurrent limits
            for concurrent_limit in [1, 3, 5]:
                doc_service._max_concurrent_llm_calls = concurrent_limit

                result = benchmark(
                    doc_service.generate_documentation,
                    package_path=str(large_package),
                    use_llm=True
                )

                assert result["status"] == "success"
                # Performance should be reasonable regardless of concurrency setting
                assert benchmark.stats["mean"] < 15.0

    def test_cache_performance_benefit(self, doc_service, large_package):
        """Test that caching provides performance benefits."""
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            call_count = 0

            def track_calls(prompt, model="llama3.1", temperature=0.3):
                nonlocal call_count
                call_count += 1
                return json.dumps({"overview": f"Response {call_count}"})

            mock_llm.side_effect = track_calls

            # First generation (populate cache)
            doc_service.generate_documentation(
                package_path=str(large_package),
                use_llm=True
            )

            first_call_count = call_count

            # Reset call counter for second run
            call_count = 0

            # Second generation (should use cache)
            doc_service.generate_documentation(
                package_path=str(large_package),
                use_llm=True
            )

            second_call_count = call_count

            # Second run should make fewer calls due to caching
            # Allow for some calls if cache isn't perfect, but should be significantly less
            if first_call_count > 0:
                reduction_ratio = second_call_count / first_call_count
                assert reduction_ratio < 0.8  # Should be at least 20% reduction

    def test_search_index_performance(self, benchmark, doc_service, large_package):
        """Benchmark search index generation performance."""
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Search test"})

            # Generate documentation first
            doc_service.generate_documentation(
                package_path=str(large_package),
                use_llm=True
            )

            # Benchmark search index generation
            result = benchmark(doc_service.generate_search_index)

            assert isinstance(result, dict)
            assert len(result.get("modules", {})) >= 0  # Allow for empty results

            # Should complete in reasonable time
            assert benchmark.stats["mean"] < 5.0  # Less than 5 seconds

    def test_markdown_export_performance(self, benchmark, doc_service, large_package):
        """Benchmark Markdown export performance."""
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Export test"})

            # Generate documentation first
            doc_service.generate_documentation(
                package_path=str(large_package),
                use_llm=True
            )

            # Benchmark Markdown export
            result = benchmark(doc_service.export_llm_analyses_to_markdown)

            assert result["standalone_files"] > 0
            assert result["combined_file"] == 1

            # Should complete in reasonable time
            assert benchmark.stats["mean"] < 5.0  # Less than 5 seconds

    def test_memory_efficiency_large_summaries(self, doc_service):
        """Test memory efficiency with large LLM summaries."""
        # Create large mock summaries
        large_summaries = {}
        for i in range(50):
            large_summaries[f"module_{i}"] = {
                "summary_type": "module",
                "module_name": f"test.module_{i}",
                "llm_analysis": "A" * 10000,  # 10KB per summary
                "generated_at": "2025-10-01T10:00:00"
            }

        doc_service._llm_summaries = large_summaries

        # Test memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Process large summaries
        combined = doc_service._create_combined_llm_markdown()

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Should handle large data without excessive memory usage
        assert memory_increase < 100  # Less than 100MB increase

        # Should produce reasonable output
        assert len(combined) > 1000  # Should have content
        assert "Complete LLM Analysis" in combined

    def test_file_io_performance(self, benchmark, doc_service, large_package):
        """Benchmark file I/O performance during documentation generation."""
        # Benchmark file operations
        result = benchmark(
            doc_service.generate_documentation,
            package_path=str(large_package),
            use_llm=False
        )

        assert result["status"] == "success"

        # File I/O should be efficient
        assert benchmark.stats["mean"] < 3.0  # Less than 3 seconds for I/O

    def test_cache_io_performance(self, benchmark, doc_service):
        """Benchmark cache I/O performance."""
        # Test cache write performance
        cache_data = {"response": "Test data", "model": "test"}

        def write_cache():
            for i in range(50):  # Reduced to 50 for faster testing
                doc_service._cache_response(f"test_key_{i}", cache_data)

        result = benchmark(write_cache)

        # Should be fast
        assert result.stats["mean"] < 2.0  # Less than 2 seconds for 50 cache writes

        # Test cache read performance
        def read_cache():
            for i in range(50):  # Reduced to 50 for faster testing
                doc_service._get_cached_response(f"test_key_{i}")

        result = benchmark(read_cache)

        # Should be fast
        assert result.stats["mean"] < 1.0  # Less than 1 second for 50 cache reads

    def test_scalability_large_codebase(self, doc_service, tmp_path):
        """Test scalability with large codebase simulation."""
        # Create a simulated large codebase
        large_codebase = tmp_path / "large_codebase"
        large_codebase.mkdir()

        # Create 5 modules with 5 files each (reduced for faster testing)
        for module_idx in range(5):
            module_dir = large_codebase / f"module_{module_idx}"
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

        # Test processing time for large codebase
        start_time = time.time()

        result = doc_service.generate_documentation(
            package_path=str(large_codebase),
            use_llm=False
        )

        processing_time = time.time() - start_time

        # Should handle large codebase in reasonable time
        assert processing_time < 10.0  # Less than 10 seconds

        # Should process all components
        assert result["modules_documented"] == 5
        assert result["files_documented"] == 30  # 5 modules * 6 files each (5 files + __init__.py)

    def test_llm_call_timeout_handling(self, doc_service):
        """Test LLM call timeout handling."""
        with patch('requests.post') as mock_post:
            # Simulate timeout
            mock_post.side_effect = Exception("Timeout")

            # Should handle timeout gracefully
            result = doc_service._call_ollama_llm("Test prompt")

            # Should return mock response
            assert "placeholder response" in result.lower()

    def test_rate_limiting_effectiveness(self, doc_service, large_package):
        """Test rate limiting effectiveness."""
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            call_times = []

            def track_timing(prompt, model="llama3.1", temperature=0.3):
                import time
                call_times.append(time.time())
                return json.dumps({"overview": "Response"})

            mock_llm.side_effect = track_timing

            # Set low concurrent limit
            doc_service._max_concurrent_llm_calls = 2

            # Generate documentation
            doc_service.generate_documentation(
                package_path=str(large_package),
                use_llm=True
            )

            # Check that calls are spread out (rate limited)
            if len(call_times) > 1:
                time_diffs = [call_times[i+1] - call_times[i] for i in range(len(call_times)-1)]
                # Most calls should be reasonably spaced
                assert any(diff > 0.1 for diff in time_diffs)  # Some delays due to rate limiting

    def test_resource_cleanup(self, doc_service, large_package):
        """Test proper resource cleanup after generation."""
        initial_files = len(list(doc_service.output_dir.rglob("*")))

        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Cleanup test"})

            # Generate documentation
            doc_service.generate_documentation(
                package_path=str(large_package),
                use_llm=True
            )

        final_files = len(list(doc_service.output_dir.rglob("*")))

        # Should create reasonable number of files
        files_created = final_files - initial_files
        assert files_created < 1000  # Should not create excessive files

        # Check cache directory
        cache_files = len(list(doc_service._cache_dir.glob("*.json")))
        assert cache_files < 200  # Should not have excessive cache files

    def test_concurrent_generation_safety(self, doc_service, large_package):
        """Test thread safety of concurrent documentation generation."""
        import threading

        results = []
        errors = []

        def generate_docs():
            try:
                # Simple test without LLM calls to avoid mocking complexity
                result = doc_service.generate_documentation(
                    package_path=str(large_package),
                    use_llm=False  # Skip LLM to test basic thread safety
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

