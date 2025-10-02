# Module: documentation.generator

**File:** `src/curriculum/documentation/generator.py`

## Description

Documentation generator service with LLM-powered multi-level summarization.

## Classes

### `DocumentationGeneratorService`

Service for automated documentation generation with LLM summarization.

**Methods:** 51


**Method List:**

- `__init__`: Initialize documentation generator service.

- `_validate_model_config`: Validate and normalize model configuration.

- `_validate_configuration`: Validate service configuration and warn about pote

- `get_performance_metrics`: Get comprehensive performance metrics.

- `_setup_output_directories`: Create output directory structure.

- `_get_cache_key`: Generate a cache key for LLM responses.

- `_get_cached_response`: Retrieve cached LLM response if available and not 

- `_get_file_hash`: Get SHA256 hash of a file for change detection.

- `_check_file_changed`: Check if a file has changed since last processing.

- `_invalidate_cache_for_file`: Invalidate cache entries for a specific file.

- `_cache_response`: Store LLM response in cache with file path for inv

- `_select_model_for_analysis`: Select the best model and parameters for a given a

- `_prepare_package_context`: Prepare context string for package analysis.

- `_generate_package_overview`: Generate high-level package overview using optimiz

- `generate_documentation`: Generate comprehensive documentation for the entir

- `_extract_package_documentation`: Extract documentation from all Python files in pac

- `_extract_file_documentation`: Extract documentation from a single Python file.

- `_extract_class_info`: Extract information from a class definition.

- `_extract_function_info`: Extract information from a function or method defi

- `_extract_import_info`: Extract import information.

- `_get_name`: Get name from AST node.

- `_get_annotation`: Get type annotation as string.

- `_get_module_name`: Get module name from file path.

- `_generate_llm_summaries`: Generate LLM-powered summaries at multiple levels 

- `_process_summaries_parallel`: Process LLM summary tasks in parallel with rate li

- `_generate_module_summary`: Generate LLM summary for a module using optimized 

- `_generate_file_summary`: Generate LLM summary for a file using optimized mo

- `_generate_package_overview`: Generate high-level package overview.

- `_prepare_module_context`: Prepare context string for module analysis.

- `_prepare_file_context`: Prepare context string for file analysis.

- `_call_ollama_llm`: Call Ollama LLM for text generation with comprehen

- `_generate_mock_llm_response`: Generate mock LLM response when Ollama is unavaila

- `_generate_output_files`: Generate final documentation output files.

- `_write_module_documentation`: Write documentation for a single module.

- `_write_file_documentation`: Write documentation for a single file.

- `_write_methods_index`: Write index of all methods.

- `_write_llm_summaries`: Write all LLM summaries to files.

- `_write_main_index`: Write main index file.

- `get_documentation_stats`: Get statistics about generated documentation.

- `generate_search_index`: Generate a searchable index for all documentation.

- `_extract_text_from_llm`: Extract searchable text from LLM analysis.

- `_extract_method_signature`: Extract method signature for search indexing.

- `_get_module_name_from_path`: Extract module name from file path.

- `search_documentation`: Search documentation using simple text matching.

- `answer_question_about_codebase`: Answer questions about the codebase using RAG appr

- `export_documentation`: Export all documentation in a single file.

- `_export_markdown`: Export documentation as single Markdown file.

- `_export_json`: Export documentation as single JSON file.

- `_convert_llm_json_to_markdown`: Convert a single LLM analysis JSON to readable Mar

- `export_llm_analyses_to_markdown`: Export all LLM analyses as standalone Markdown fil

- `_create_combined_llm_markdown`: Create a single combined Markdown file with all LL

## Functions

### `_configure_logging`

Configure logging for the documentation system.

**Parameters:**

- `output_dir: Path`
