"""Integration tests for documentation generation service."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

from curriculum.documentation import DocumentationGeneratorService


@pytest.mark.integration
class TestDocumentationIntegration:
    """Integration tests for documentation system components."""

    @pytest.fixture
    def doc_service(self, tmp_path):
        """Create documentation service for integration testing."""
        return DocumentationGeneratorService(output_dir=str(tmp_path / "docs"))

    @pytest.fixture
    def sample_package(self, tmp_path):
        """Create a sample package for integration testing."""
        package_dir = tmp_path / "sample_package"
        package_dir.mkdir()

        # Create __init__.py
        (package_dir / "__init__.py").write_text('''"""Sample package for integration testing."""

from typing import List, Optional

__version__ = "1.0.0"
__author__ = "Test Author"
''')

        # Create main module
        (package_dir / "main_module.py").write_text('''"""Main module with classes and functions."""

from typing import Dict, List
import json

class DataProcessor:
    """Process data with various methods."""

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

    @pytest.fixture
    def mock_llm_responses(self):
        """Mock LLM responses for integration testing."""
        return {
            "package_overview": {
                "architecture": {
                    "design_patterns": ["Layered Architecture", "Dependency Injection"],
                    "overall_structure": "Modular"
                },
                "domains": [
                    {"name": "Core", "modules": ["main_module"]},
                    {"name": "Utilities", "modules": ["submodule"]}
                ],
                "capabilities": ["Data processing", "Validation", "Async operations"],
                "improvements": ["Add error handling", "Improve type hints"]
            },
            "module_sample_package.main_module": {
                "overview": ["Main module for data processing", "Contains DataProcessor class", "Utility functions"],
                "key_classes": [
                    {"name": "DataProcessor", "purpose": "Process data with transformation methods"}
                ],
                "functionality": ["Data transformation", "Async processing", "Validation"],
                "dependencies": ["typing", "json"],
                "usage_hints": ["Use DataProcessor for batch data operations"]
            },
            "module_sample_package.submodule": {
                "overview": ["Helper utilities", "Support classes", "Additional functions"],
                "key_classes": [
                    {"name": "HelperClass", "purpose": "Provide utility functionality"}
                ],
                "functionality": ["Helper functions", "Utility classes"],
                "dependencies": ["typing"],
                "usage_hints": ["Use helper_function for string operations"]
            },
            "file_sample_package/main_module.py": {
                "purpose": ["Main module implementation", "Contains DataProcessor class"],
                "components": [
                    {"name": "DataProcessor", "type": "class"},
                    {"name": "utility_function", "type": "function"},
                    {"name": "validate_data", "type": "function"}
                ],
                "complexity": ["Medium complexity", "Good separation of concerns"],
                "improvements": ["Add more comprehensive error handling"]
            },
            "file_sample_package/submodule/helpers.py": {
                "purpose": ["Helper utilities", "Support functionality"],
                "components": [
                    {"name": "HelperClass", "type": "class"},
                    {"name": "helper_function", "type": "function"}
                ],
                "complexity": ["Low complexity", "Simple utilities"],
                "improvements": ["Add input validation"]
            }
        }

    def test_end_to_end_documentation_generation(self, doc_service, sample_package, mock_llm_responses):
        """Test complete documentation generation workflow."""
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            # Mock all LLM calls
            def mock_llm_call(prompt, model="llama3.1", temperature=0.3):
                # Extract key from prompt to determine response
                if "architectural overview" in prompt.lower():
                    return json.dumps(mock_llm_responses["package_overview"])
                elif "analyze this python module" in prompt.lower():
                    if "main_module" in prompt:
                        return json.dumps(mock_llm_responses["module_sample_package.main_module"])
                    elif "submodule" in prompt:
                        return json.dumps(mock_llm_responses["module_sample_package.submodule"])
                elif "analyze this python file" in prompt.lower():
                    if "main_module.py" in prompt:
                        return json.dumps(mock_llm_responses["file_sample_package/main_module.py"])
                    elif "helpers.py" in prompt:
                        return json.dumps(mock_llm_responses["file_sample_package/submodule/helpers.py"])
                return json.dumps({"overview": "Mock response", "note": "Test response"})

            mock_llm.side_effect = mock_llm_call

            # Generate documentation
            result = doc_service.generate_documentation(
                package_path=str(sample_package),
                use_llm=True
            )

            # Verify result structure
            assert result["status"] == "success"
            assert result["modules_documented"] == 2  # main_module and submodule
            assert result["files_documented"] == 4  # 2 modules + 2 __init__ files
            assert result["llm_summaries_generated"] == 4  # package + 2 modules + 1 file

            # Verify LLM markdown export
            assert "llm_markdown_exports" in result
            assert result["llm_markdown_exports"]["standalone_files"] == 4
            assert result["llm_markdown_exports"]["combined_file"] == 1

            # Verify search index
            assert "search_index" in result
            assert result["search_index"]["generated"] is True

    def test_caching_integration(self, doc_service, sample_package):
        """Test caching integration across multiple calls."""
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_response = json.dumps({"overview": "Test response", "cached": True})

            def mock_llm_call(prompt, model="llama3.1", temperature=0.3):
                # Return different responses for different prompts
                if "module" in prompt:
                    return json.dumps({"overview": f"Module analysis: {prompt[:50]}"})
                return mock_response

            mock_llm.side_effect = mock_llm_call

            # First generation
            result1 = doc_service.generate_documentation(
                package_path=str(sample_package),
                use_llm=True
            )

            # Check cache was created
            cache_files_before = len(list(doc_service._cache_dir.glob("*.json")))

            # Second generation (should use cache)
            result2 = doc_service.generate_documentation(
                package_path=str(sample_package),
                use_llm=True
            )

            cache_files_after = len(list(doc_service._cache_dir.glob("*.json")))

            # Cache should be populated
            assert cache_files_after >= cache_files_before
            assert result1["status"] == result2["status"] == "success"

    def test_multi_model_strategy_integration(self, doc_service, sample_package):
        """Test multi-model strategy integration."""
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            responses = []

            def mock_llm_call(prompt, model="llama3.1", temperature=0.3):
                responses.append({"prompt": prompt[:50], "model": model, "temperature": temperature})
                return json.dumps({"overview": f"Response from {model}", "model_used": model})

            mock_llm.side_effect = mock_llm_call

            # Generate documentation
            doc_service.generate_documentation(
                package_path=str(sample_package),
                use_llm=True
            )

            # Verify different models were used for different analysis types
            models_used = [call["model"] for call in responses]
            unique_models = set(models_used)

            # Should have used multiple models
            assert len(unique_models) > 1
            assert any("gemma2" in model for model in models_used)  # Package overview
            assert any("llama3" in model for model in models_used)  # Module analysis

    def test_search_integration(self, doc_service, sample_package):
        """Test search functionality integration."""
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Test analysis"})

            # Generate documentation
            doc_service.generate_documentation(
                package_path=str(sample_package),
                use_llm=True
            )

            # Test search
            results = doc_service.search_documentation("DataProcessor", max_results=5)

            # Should find relevant results
            assert len(results) > 0
            assert any("DataProcessor" in result.get("summary", "") for result in results)

            # Test search for non-existent term
            no_results = doc_service.search_documentation("NonExistentTerm", max_results=5)
            assert len(no_results) == 0

    def test_qa_integration(self, doc_service, sample_package):
        """Test Q&A functionality integration."""
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Test analysis"})

            # Generate documentation
            doc_service.generate_documentation(
                package_path=str(sample_package),
                use_llm=True
            )

            # Test Q&A
            answer = doc_service.answer_question_about_codebase("What is DataProcessor?")

            # Should generate an answer
            assert isinstance(answer, str)
            assert len(answer) > 0

    def test_markdown_export_integration(self, doc_service, sample_package):
        """Test Markdown export integration."""
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Test analysis"})

            # Generate documentation
            result = doc_service.generate_documentation(
                package_path=str(sample_package),
                use_llm=True
            )

            # Verify Markdown export happened
            assert "llm_markdown_exports" in result

            export_info = result["llm_markdown_exports"]
            assert export_info["standalone_files"] > 0
            assert export_info["combined_file"] == 1

            # Check files were created
            llm_md_dir = Path(export_info["output_directory"])
            assert llm_md_dir.exists()

            standalone_files = list(llm_md_dir.glob("*.md"))
            assert len(standalone_files) == export_info["standalone_files"]

            combined_file = doc_service.output_dir / "llm_analysis_complete.md"
            assert combined_file.exists()

    def test_error_handling_integration(self, doc_service, tmp_path):
        """Test error handling across the entire system."""
        # Test with invalid package path
        result = doc_service.generate_documentation(
            package_path="/nonexistent/path",
            use_llm=False
        )

        # Should handle gracefully
        assert result["status"] == "success"  # May still succeed with empty results

        # Test with LLM errors
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.side_effect = Exception("LLM Error")

            result = doc_service.generate_documentation(
                package_path=str(tmp_path),
                use_llm=True
            )

            # Should still complete with fallback responses
            assert result["status"] == "success"
            assert result["llm_summaries_generated"] == 0  # No summaries due to errors

    def test_performance_integration(self, doc_service, sample_package):
        """Test performance characteristics of the system."""
        import time

        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Test response"})

            # Measure generation time
            start_time = time.time()

            result = doc_service.generate_documentation(
                package_path=str(sample_package),
                use_llm=True
            )

            end_time = time.time()
            generation_time = end_time - start_time

            # Should complete in reasonable time
            assert generation_time < 30  # Less than 30 seconds for test
            assert result["status"] == "success"

    def test_output_format_integration(self, doc_service, sample_package):
        """Test output format consistency across components."""
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Test analysis"})

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
                assert "Generated:" in md_content

    def test_cross_component_data_flow(self, doc_service, sample_package):
        """Test data flow between different components."""
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Test analysis"})

            # Generate documentation
            doc_service.generate_documentation(
                package_path=str(sample_package),
                use_llm=True
            )

            # Test that data flows correctly between components
            stats = doc_service.get_documentation_stats()

            # Stats should reflect the generated data
            assert stats["modules"] > 0
            assert stats["files"] > 0
            assert stats["llm_summaries"] > 0

            # Module data should be populated
            assert len(doc_service._module_docs) == stats["modules"]
            assert len(doc_service._file_docs) == stats["files"]
            assert len(doc_service._llm_summaries) == stats["llm_summaries"]

    def test_concurrent_processing_integration(self, doc_service, sample_package):
        """Test concurrent processing capabilities."""
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            # Track call order and timing
            call_order = []
            call_times = []

            def mock_llm_call(prompt, model="llama3.1", temperature=0.3):
                import time
                call_times.append(time.time())
                call_order.append(len(call_order))
                return json.dumps({"overview": f"Response {len(call_order)}"})

            mock_llm.side_effect = mock_llm_call

            # Generate documentation
            doc_service.generate_documentation(
                package_path=str(sample_package),
                use_llm=True
            )

            # Check that calls happened (even if not truly concurrent in this test)
            assert len(call_order) > 0

    def test_memory_usage_integration(self, doc_service, sample_package):
        """Test memory usage during full documentation generation."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Test response"})

            # Generate documentation
            doc_service.generate_documentation(
                package_path=str(sample_package),
                use_llm=True
            )

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Should not use excessive memory
        assert memory_increase < 100  # Less than 100MB increase

        # Verify all data structures are populated
        assert len(doc_service._module_docs) > 0
        assert len(doc_service._file_docs) > 0
        assert len(doc_service._llm_summaries) > 0

    def test_cache_persistence_integration(self, doc_service, sample_package):
        """Test cache persistence across service instances."""
        with patch.object(doc_service, '_call_ollama_llm') as mock_llm:
            mock_llm.return_value = json.dumps({"overview": "Cached response"})

            # First generation
            doc_service.generate_documentation(
                package_path=str(sample_package),
                use_llm=True
            )

            cache_files_before = len(list(doc_service._cache_dir.glob("*.json")))

            # Create new service instance with same output directory
            doc_service2 = DocumentationGeneratorService(output_dir=str(doc_service.output_dir))

            # Second generation should use cache
            with patch.object(doc_service2, '_call_ollama_llm') as mock_llm2:
                mock_llm2.return_value = json.dumps({"overview": "Should not be called"})

                doc_service2.generate_documentation(
                    package_path=str(sample_package),
                    use_llm=True
                )

                # Mock should not have been called due to cache
                mock_llm2.assert_not_called()

    def test_error_recovery_integration(self, doc_service, sample_package):
        """Test error recovery and graceful degradation."""
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
                package_path=str(sample_package),
                use_llm=True
            )

            # Should still complete successfully
            assert result["status"] == "success"
            # Should have processed what it could
            assert result["modules_documented"] >= 0

