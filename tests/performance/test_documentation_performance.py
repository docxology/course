"""Performance tests for documentation generation service."""

import json
import os
import statistics
import threading
import time
from typing import Any, Callable, List, Tuple
from unittest.mock import patch

import psutil
import pytest

from curriculum.documentation import DocumentationGeneratorService

# ``large_package`` has 10 sub-packages, each holding ``__init__.py`` and one
# module. Every non-root ``__init__`` is a module ("module_i") and every
# submodule is a module ("module_i.module_i"), so both counts are 20.
LARGE_PACKAGE_FILES = 20
LARGE_PACKAGE_MODULES = 20
# One package overview plus one summary per module and per file.
LARGE_PACKAGE_SUMMARIES = 1 + LARGE_PACKAGE_MODULES + LARGE_PACKAGE_FILES


def _benchmark_with_timings(
    benchmark: Any, func: Callable[..., Any], *args: Any, **kwargs: Any
) -> Tuple[Any, float]:
    """Run ``func`` through the single permitted ``benchmark`` call and time every round.

    ``benchmark.stats`` is ``None`` under ``--benchmark-disable``, so latency budgets
    are checked against per-round timings recorded identically in both modes.
    """
    durations: List[float] = []

    def timed() -> Any:
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            durations.append(time.perf_counter() - start)

    result = benchmark(timed)
    assert durations, "benchmark did not invoke the measured callable"
    return result, statistics.fmean(durations)


@pytest.mark.integration
@pytest.mark.slow
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
        result, mean_seconds = _benchmark_with_timings(
            benchmark,
            doc_service.generate_documentation,
            package_path=str(large_package),
            use_llm=False,
        )

        # Should complete successfully
        assert result["status"] == "success"

        # Should document every module and file in the fixture
        assert result["modules_documented"] == LARGE_PACKAGE_MODULES
        assert result["files_documented"] == LARGE_PACKAGE_FILES

        # Performance should be reasonable
        assert mean_seconds < 5.0  # Less than 5 seconds

    def test_llm_generation_performance(self, benchmark, doc_service, large_package):
        """Benchmark LLM-based documentation generation performance."""
        with patch.object(doc_service, "_call_ollama_llm") as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Mock analysis"})

            result, mean_seconds = _benchmark_with_timings(
                benchmark,
                doc_service.generate_documentation,
                package_path=str(large_package),
                use_llm=True,
            )

            # Should complete successfully
            assert result["status"] == "success"

            # Should generate a package, module and file summary for every component
            assert result["llm_summaries_generated"] == LARGE_PACKAGE_SUMMARIES
            assert mock_llm.call_count >= LARGE_PACKAGE_SUMMARIES

            # Performance should be reasonable (with mocked LLM calls)
            assert mean_seconds < 10.0  # Less than 10 seconds

    def test_caching_performance(self, benchmark, doc_service, large_package):
        """Benchmark performance with caching enabled."""
        # First run to populate cache
        with patch.object(doc_service, "_call_ollama_llm") as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Cached response"})

            first = doc_service.generate_documentation(
                package_path=str(large_package), use_llm=True
            )

        # Later runs must be served entirely from the cache
        with patch.object(doc_service, "_call_ollama_llm") as uncached_llm:
            result, mean_seconds = _benchmark_with_timings(
                benchmark,
                doc_service.generate_documentation,
                package_path=str(large_package),
                use_llm=True,
            )

        assert result["status"] == "success"
        assert uncached_llm.call_count == 0
        assert result["llm_summaries_generated"] == first["llm_summaries_generated"]

        # Should be fast because no provider calls are made
        assert mean_seconds < 5.0  # Less than 5 seconds

    def test_memory_usage_during_generation(self, doc_service, large_package):
        """Test memory usage during documentation generation."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Generate documentation
        with patch.object(doc_service, "_call_ollama_llm") as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Test response"})

            doc_service.generate_documentation(package_path=str(large_package), use_llm=True)

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

    @pytest.mark.parametrize("concurrent_limit", [1, 3, 5])
    def test_concurrent_processing_performance(
        self, benchmark, doc_service, large_package, concurrent_limit
    ):
        """Benchmark generation at each concurrency limit (one benchmark per limit)."""
        doc_service._max_concurrent_llm_calls = concurrent_limit
        with patch.object(doc_service, "_call_ollama_llm") as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Concurrent response"})

            result, mean_seconds = _benchmark_with_timings(
                benchmark,
                doc_service.generate_documentation,
                package_path=str(large_package),
                use_llm=True,
            )

        assert result["status"] == "success"
        assert result["llm_summaries_generated"] == LARGE_PACKAGE_SUMMARIES
        # Performance should be reasonable regardless of concurrency setting
        assert mean_seconds < 15.0

    def test_cache_performance_benefit(self, doc_service, large_package):
        """Test that caching provides performance benefits."""
        with patch.object(doc_service, "_call_ollama_llm") as mock_llm:
            call_count = 0

            def track_calls(prompt, model="llama3.1", temperature=0.3):
                nonlocal call_count
                call_count += 1
                return json.dumps({"overview": f"Response {call_count}"})

            mock_llm.side_effect = track_calls

            # First generation (populate cache)
            doc_service.generate_documentation(package_path=str(large_package), use_llm=True)

            first_call_count = call_count

            # Reset call counter for second run
            call_count = 0

            # Second generation (should use cache)
            doc_service.generate_documentation(package_path=str(large_package), use_llm=True)

            second_call_count = call_count

            # Second run should make fewer calls due to caching
            # Allow for some calls if cache isn't perfect, but should be significantly less
            if first_call_count > 0:
                reduction_ratio = second_call_count / first_call_count
                assert reduction_ratio < 0.8  # Should be at least 20% reduction

    def test_search_index_performance(self, benchmark, doc_service, large_package):
        """Benchmark search index generation performance."""
        with patch.object(doc_service, "_call_ollama_llm") as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Search test"})

            # Generate documentation first
            doc_service.generate_documentation(package_path=str(large_package), use_llm=True)

            # Benchmark search index generation
            result, mean_seconds = _benchmark_with_timings(
                benchmark, doc_service.generate_search_index
            )

            assert isinstance(result, dict)
            assert set(result["modules"]) == set(doc_service._module_docs)
            assert len(result["modules"]) == LARGE_PACKAGE_MODULES

            # Should complete in reasonable time
            assert mean_seconds < 5.0  # Less than 5 seconds

    def test_markdown_export_performance(self, benchmark, doc_service, large_package):
        """Benchmark Markdown export performance."""
        with patch.object(doc_service, "_call_ollama_llm") as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Export test"})

            # Generate documentation first
            doc_service.generate_documentation(package_path=str(large_package), use_llm=True)

            # Benchmark Markdown export
            result, mean_seconds = _benchmark_with_timings(
                benchmark, doc_service.export_llm_analyses_to_markdown
            )

            assert result["standalone_files"] == LARGE_PACKAGE_SUMMARIES
            assert result["combined_file"] == 1

            # Should complete in reasonable time
            assert mean_seconds < 5.0  # Less than 5 seconds

    def test_memory_efficiency_large_summaries(self, doc_service):
        """Test memory efficiency with large LLM summaries."""
        # Create large mock summaries
        large_summaries = {}
        for i in range(50):
            large_summaries[f"module_{i}"] = {
                "summary_type": "module",
                "module_name": f"test.module_{i}",
                "llm_analysis": "A" * 10000,  # 10KB per summary
                "generated_at": "2025-10-01T10:00:00",
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
        result, mean_seconds = _benchmark_with_timings(
            benchmark,
            doc_service.generate_documentation,
            package_path=str(large_package),
            use_llm=False,
        )

        assert result["status"] == "success"
        assert result["files_documented"] == LARGE_PACKAGE_FILES

        # File I/O should be efficient
        assert mean_seconds < 3.0  # Less than 3 seconds for I/O

    CACHE_DATA = {"response": "Test data", "model": "test"}
    CACHE_ENTRIES = 50

    def test_cache_write_performance(self, benchmark, doc_service):
        """Benchmark cache writes."""

        def write_cache() -> None:
            for i in range(self.CACHE_ENTRIES):
                doc_service._cache_response(f"test_key_{i}", self.CACHE_DATA)

        _, mean_seconds = _benchmark_with_timings(benchmark, write_cache)

        assert len(list(doc_service._cache_dir.glob("test_key_*.json"))) == self.CACHE_ENTRIES
        # Should be fast
        assert mean_seconds < 2.0  # Less than 2 seconds for 50 cache writes

    def test_cache_read_performance(self, benchmark, doc_service):
        """Benchmark cache reads of previously written entries."""
        for i in range(self.CACHE_ENTRIES):
            doc_service._cache_response(f"test_key_{i}", self.CACHE_DATA)

        def read_cache() -> List[Any]:
            return [
                doc_service._get_cached_response(f"test_key_{i}") for i in range(self.CACHE_ENTRIES)
            ]

        responses, mean_seconds = _benchmark_with_timings(benchmark, read_cache)

        assert responses == [self.CACHE_DATA] * self.CACHE_ENTRIES
        # Should be fast
        assert mean_seconds < 1.0  # Less than 1 second for 50 cache reads

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

        result = doc_service.generate_documentation(package_path=str(large_codebase), use_llm=False)

        processing_time = time.time() - start_time

        # Should handle large codebase in reasonable time
        assert processing_time < 10.0  # Less than 10 seconds

        # Should process all components. Each of the 5 sub-packages contributes its
        # ``__init__`` ("module_i") plus 5 submodules ("module_i.file_j"); the root
        # directory has no ``__init__.py`` and is therefore not a module.
        assert result["modules_documented"] == 30  # 5 * (1 package init + 5 submodules)
        assert result["files_documented"] == 30  # 5 * (5 files + __init__.py)

    def test_llm_call_timeout_handling(self, doc_service):
        """Test LLM call timeout handling."""
        with patch("requests.post") as mock_post:
            # Simulate timeout
            mock_post.side_effect = Exception("Timeout")

            # Should handle timeout gracefully
            result = doc_service._call_ollama_llm("Test prompt")

            # Should return mock response
            assert "placeholder response" in result.lower()

    def test_rate_limiting_effectiveness(self, doc_service, large_package):
        """Provider calls never exceed the configured concurrency limit.

        The generator rate-limits with a bounded worker pool rather than time
        delays. The first ``limit`` calls rendezvous at a barrier, proving the
        limit is actually reached; every call records the in-flight peak, proving
        it is never exceeded.
        """
        limit = 2
        doc_service._max_concurrent_llm_calls = limit
        state_lock = threading.Lock()
        rendezvous = threading.Barrier(limit, timeout=10)
        calls = 0
        in_flight = 0
        peak_in_flight = 0

        def bounded_call(prompt, model="llama3.1", temperature=0.3):
            nonlocal calls, in_flight, peak_in_flight
            with state_lock:
                calls += 1
                call_index = calls
                in_flight += 1
                peak_in_flight = max(peak_in_flight, in_flight)
            try:
                if call_index <= limit:
                    rendezvous.wait()
                else:
                    time.sleep(0.002)  # Give queued work a chance to overlap
                return json.dumps({"overview": "Response"})
            finally:
                with state_lock:
                    in_flight -= 1

        with patch.object(doc_service, "_call_ollama_llm", side_effect=bounded_call):
            result = doc_service.generate_documentation(
                package_path=str(large_package), use_llm=True
            )

        assert result["status"] == "success"
        assert result["llm_summaries_generated"] == LARGE_PACKAGE_SUMMARIES
        assert calls == LARGE_PACKAGE_SUMMARIES
        assert peak_in_flight == limit

    def test_resource_cleanup(self, doc_service, large_package):
        """Test proper resource cleanup after generation."""
        initial_files = len(list(doc_service.output_dir.rglob("*")))

        with patch.object(doc_service, "_call_ollama_llm") as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Cleanup test"})

            # Generate documentation
            doc_service.generate_documentation(package_path=str(large_package), use_llm=True)

        final_files = len(list(doc_service.output_dir.rglob("*")))

        # Should create reasonable number of files
        files_created = final_files - initial_files
        assert files_created < 1000  # Should not create excessive files

        # Check cache directory
        cache_files = len(list(doc_service._cache_dir.glob("*.json")))
        assert cache_files < 200  # Should not have excessive cache files

    def test_concurrent_generation_safety(self, doc_service, large_package):
        """Test thread safety of concurrent documentation generation."""
        results = []
        errors = []

        def generate_docs():
            try:
                # Simple test without LLM calls to avoid mocking complexity
                result = doc_service.generate_documentation(
                    package_path=str(large_package),
                    use_llm=False,  # Skip LLM to test basic thread safety
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
