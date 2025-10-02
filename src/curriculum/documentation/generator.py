"""Documentation generator service with LLM-powered multi-level summarization."""

"""
Documentation generator service with LLM-powered multi-level summarization.

This module provides comprehensive documentation generation capabilities including:
- AST-based code analysis and extraction
- Multi-model LLM integration with caching
- Hierarchical organization and cross-referencing
- Search and Q&A capabilities
- Performance optimization and error handling
"""

import ast
import asyncio
import hashlib
import importlib
import inspect
import json
import logging
import os
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union, Callable
from uuid import UUID, uuid4
from datetime import datetime, timezone

from curriculum.config import settings

# Configure logging
def _configure_logging(output_dir: Path) -> logging.Logger:
    """Configure logging for the documentation system."""
    log_file = output_dir / "documentation.log"

    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )

    # Create handlers
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)

    # Configure root logger
    logger = logging.getLogger('curriculum.documentation')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = _configure_logging(Path("./docs/generated"))


class DocumentationGeneratorService:
    """Service for automated documentation generation with LLM summarization."""

    def __init__(self, output_dir: str = "./docs/generated") -> None:
        """Initialize documentation generator service."""
        self.output_dir = Path(output_dir)
        self._module_docs: Dict[str, Dict[str, Any]] = {}
        self._file_docs: Dict[str, Dict[str, Any]] = {}
        self._method_docs: Dict[str, Dict[str, Any]] = {}
        self._llm_summaries: Dict[str, Dict[str, Any]] = {}
        self._stats = {
            "total_modules": 0,
            "total_files": 0,
            "total_classes": 0,
            "total_functions": 0,
            "total_methods": 0,
            "total_llm_summaries": 0,
        }

        # LLM caching system
        self._cache_dir = Path(output_dir) / ".llm_cache"
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache_ttl_days = 30  # Cache responses for 30 days
        self._enable_caching = True

        # File change detection for cache invalidation
        self._file_hashes = {}  # Store file hashes for change detection
        self._cache_invalidation_enabled = True

        # Performance monitoring
        self._performance_metrics = {
            "total_llm_calls": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "llm_api_calls": 0,
            "llm_subprocess_calls": 0,
            "processing_time": 0,
            "files_processed": 0,
            "errors_encountered": 0
        }

        # Performance settings
        self._max_concurrent_llm_calls = 5
        self._llm_timeout_seconds = 60

        # Multi-model strategy with validation
        self._model_config = self._validate_model_config({
            "package_overview": {
                "model": "gemma2:2b",  # Fast, good for summaries
                "temperature": 0.3,
                "max_tokens": 2000
            },
            "module_analysis": {
                "model": "llama3.1:latest",  # Balanced performance
                "temperature": 0.2,
                "max_tokens": 1500
            },
            "file_deep_analysis": {
                "model": "codellama:latest",  # Code-specific analysis
                "temperature": 0.1,
                "max_tokens": 3000
            },
            "code_review": {
                "model": "deepseek-coder:latest",  # Advanced code understanding
                "temperature": 0.15,
                "max_tokens": 2500
            },
            "quick_summary": {
                "model": "mistral:latest",  # Very fast
                "temperature": 0.4,
                "max_tokens": 800
            }
        })

        # Validate configuration
        self._validate_configuration()

        # Create output directory structure
        self._setup_output_directories()

        # Update logger with correct output directory
        global logger
        logger = _configure_logging(self.output_dir)

        logger.info(f"DocumentationGeneratorService initialized with output_dir={output_dir}")

    def _validate_model_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize model configuration."""
        validated_config = {}

        required_keys = ["model", "temperature", "max_tokens"]

        for analysis_type, model_settings in config.items():
            if not isinstance(model_settings, dict):
                logger.warning(f"Invalid model config for {analysis_type}: not a dict")
                continue

            # Validate required keys
            missing_keys = [key for key in required_keys if key not in model_settings]
            if missing_keys:
                logger.warning(f"Missing keys in model config for {analysis_type}: {missing_keys}")
                continue

            # Validate temperature
            temperature = model_settings["temperature"]
            if not isinstance(temperature, (int, float)) or not 0 <= temperature <= 2:
                logger.warning(f"Invalid temperature for {analysis_type}: {temperature}, using 0.3")
                temperature = 0.3

            # Validate max_tokens
            max_tokens = model_settings["max_tokens"]
            if not isinstance(max_tokens, int) or max_tokens <= 0:
                logger.warning(f"Invalid max_tokens for {analysis_type}: {max_tokens}, using 1500")
                max_tokens = 1500

            validated_config[analysis_type] = {
                "model": str(model_settings["model"]),
                "temperature": temperature,
                "max_tokens": max_tokens
            }

        return validated_config

    def _validate_configuration(self) -> None:
        """Validate service configuration and warn about potential issues."""
        # Validate concurrent calls
        if not isinstance(self._max_concurrent_llm_calls, int) or self._max_concurrent_llm_calls < 1:
            logger.warning(f"Invalid max_concurrent_llm_calls: {self._max_concurrent_llm_calls}, using 5")
            self._max_concurrent_llm_calls = 5

        # Validate timeout
        if not isinstance(self._llm_timeout_seconds, (int, float)) or self._llm_timeout_seconds < 1:
            logger.warning(f"Invalid llm_timeout_seconds: {self._llm_timeout_seconds}, using 60")
            self._llm_timeout_seconds = 60

        # Validate cache TTL
        if not isinstance(self._cache_ttl_days, int) or self._cache_ttl_days < 1:
            logger.warning(f"Invalid cache_ttl_days: {self._cache_ttl_days}, using 30")
            self._cache_ttl_days = 30

        # Check if output directory is writable
        try:
            test_file = self.output_dir / ".test_write"
            test_file.write_text("test")
            test_file.unlink()
        except Exception as e:
            logger.error(f"Output directory is not writable: {self.output_dir}, error: {e}")
            raise ValueError(f"Output directory is not writable: {self.output_dir}")

        logger.info(f"Configuration validated: concurrent_calls={self._max_concurrent_llm_calls}, "
                   f"timeout={self._llm_timeout_seconds}s, cache_ttl={self._cache_ttl_days}d")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics."""
        return {
            "llm_calls": {
                "total": self._performance_metrics["total_llm_calls"],
                "cache_hits": self._performance_metrics["cache_hits"],
                "cache_misses": self._performance_metrics["cache_misses"],
                "api_calls": self._performance_metrics["llm_api_calls"],
                "subprocess_calls": self._performance_metrics["llm_subprocess_calls"],
                "cache_hit_rate": (
                    self._performance_metrics["cache_hits"] /
                    max(1, self._performance_metrics["total_llm_calls"])
                ) if self._performance_metrics["total_llm_calls"] > 0 else 0
            },
            "processing": {
                "files_processed": self._performance_metrics["files_processed"],
                "errors_encountered": self._performance_metrics["errors_encountered"],
                "processing_time": self._performance_metrics["processing_time"]
            },
            "cache": {
                "cache_files": len(list(self._cache_dir.glob("*.json"))),
                "cache_enabled": self._enable_caching,
                "cache_ttl_days": self._cache_ttl_days,
                "cache_invalidation_enabled": self._cache_invalidation_enabled
            },
            "configuration": {
                "max_concurrent_calls": self._max_concurrent_llm_calls,
                "llm_timeout_seconds": self._llm_timeout_seconds,
                "output_directory": str(self.output_dir)
            }
        }

    def _setup_output_directories(self) -> None:
        """Create output directory structure."""
        directories = [
            self.output_dir,
            self.output_dir / "modules",
            self.output_dir / "files",
            self.output_dir / "methods",
            self.output_dir / "summaries",
            self.output_dir / "llm_analysis",
        ]

        created_count = 0
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                created_count += 1
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {e}")
                raise

        logger.info(f"Created {created_count} output directories")

    def _get_cache_key(self, prompt: str, model: str = "default") -> str:
        """Generate a cache key for LLM responses."""
        # Create a hash of the prompt and model for consistent caching
        content = f"{model}:{prompt}".encode("utf-8")
        return hashlib.sha256(content).hexdigest()

    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached LLM response if available and not expired."""
        self._performance_metrics["total_llm_calls"] += 1

        if not self._enable_caching:
            logger.debug("Caching disabled, skipping cache lookup")
            self._performance_metrics["cache_misses"] += 1
            return None

        cache_file = self._cache_dir / f"{cache_key}.json"
        if not cache_file.exists():
            logger.debug(f"Cache miss for key: {cache_key}")
            self._performance_metrics["cache_misses"] += 1
            return None

        try:
            with open(cache_file, "r") as f:
                cached_data = json.load(f)

            # Check if cache is expired
            cached_time = datetime.fromisoformat(cached_data["cached_at"])
            age_days = (datetime.now(timezone.utc) - cached_time).days

            if age_days > self._cache_ttl_days:
                # Cache expired, remove it
                logger.debug(f"Cache expired for key: {cache_key} (age: {age_days} days)")
                cache_file.unlink()
                self._performance_metrics["cache_misses"] += 1
                return None

            logger.debug(f"Cache hit for key: {cache_key}")
            self._performance_metrics["cache_hits"] += 1
            return cached_data["response"]

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Invalid cache file, remove it
            logger.warning(f"Invalid cache file for key: {cache_key}, removing: {e}")
            try:
                cache_file.unlink()
            except OSError:
                pass  # Ignore if file doesn't exist
            self._performance_metrics["cache_misses"] += 1
        return None

    def _get_file_hash(self, file_path: str) -> Optional[str]:
        """Get SHA256 hash of a file for change detection."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except (OSError, IOError):
            return None

    def _check_file_changed(self, file_path: str) -> bool:
        """Check if a file has changed since last processing."""
        if not self._cache_invalidation_enabled:
            return False

        current_hash = self._get_file_hash(file_path)
        if current_hash is None:
            return True  # File doesn't exist or can't be read

        previous_hash = self._file_hashes.get(file_path)

        if previous_hash != current_hash:
            self._file_hashes[file_path] = current_hash
            return True

        return False

    def _invalidate_cache_for_file(self, file_path: str) -> int:
        """Invalidate cache entries for a specific file."""
        if not self._cache_invalidation_enabled:
            return 0

        invalidated_count = 0
        cache_files_to_remove = []

        # Find all cache files that might be related to this file
        for cache_file in self._cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)

                # Check if this cache entry is for our file
                if cache_data.get("file_path") == file_path:
                    cache_files_to_remove.append(cache_file)
                    invalidated_count += 1

            except (json.JSONDecodeError, KeyError):
                # Invalid cache file, mark for removal
                cache_files_to_remove.append(cache_file)

        # Remove invalidated cache files
        for cache_file in cache_files_to_remove:
            try:
                cache_file.unlink()
            except OSError:
                pass  # Ignore if file doesn't exist

        if invalidated_count > 0:
            logger.debug(f"Invalidated {invalidated_count} cache entries for file: {file_path}")

        return invalidated_count

    def _cache_response(self, cache_key: str, response: Dict[str, Any], file_path: Optional[str] = None) -> None:
        """Store LLM response in cache with file path for invalidation."""
        if not self._enable_caching:
            return

        try:
            cache_data = {
                "cached_at": datetime.now(timezone.utc).isoformat(),
                "response": response,
                "file_path": file_path,  # Include file path for invalidation
            }

            cache_file = self._cache_dir / f"{cache_key}.json"
            with open(cache_file, "w") as f:
                json.dump(cache_data, f, indent=2)

            logger.debug(f"Cached response for key: {cache_key} (file: {file_path})")

        except Exception as e:
            logger.warning(f"Failed to cache response for key: {cache_key}: {e}")
            self._performance_metrics["errors_encountered"] += 1
            # Don't raise exception, just log the warning

    def _select_model_for_analysis(self, analysis_type: str) -> Dict[str, Any]:
        """Select the best model and parameters for a given analysis type."""
        return self._model_config.get(analysis_type, {
            "model": "llama3.1:latest",
            "temperature": 0.3,
            "max_tokens": 1500
        })

    def _prepare_package_context(self) -> str:
        """Prepare context string for package analysis."""
        context_parts = []

        # Add module summary
        context_parts.append(f"Package contains {len(self._module_docs)} modules:")
        for module_name in sorted(self._module_docs.keys())[:10]:  # Limit to first 10
            module_data = self._module_docs[module_name]
            context_parts.append(f"  - {module_name}")

        # Add statistics
        context_parts.append(f"\nStatistics:")
        context_parts.append(f"- Total Classes: {self._stats['total_classes']}")
        context_parts.append(f"- Total Functions: {self._stats['total_functions']}")
        context_parts.append(f"- Total Methods: {self._stats['total_methods']}")

        return "\n".join(context_parts)

    def _generate_package_overview(self) -> Optional[Dict[str, Any]]:
        """Generate high-level package overview using optimized model."""
        model_config = self._select_model_for_analysis("package_overview")

        context = self._prepare_package_context()
        prompt = f"""Provide a comprehensive architectural overview of this Python package:

Package Statistics:
- Total Modules: {len(self._module_docs)}
- Total Classes: {self._stats['total_classes']}
- Total Functions: {self._stats['total_functions']}

Code Structure:
{context}

Please provide:
1. Overall architecture and design patterns used
2. Key functional domains and their organization
3. System capabilities and main features
4. Suggested improvements for structure and organization

Format your response as JSON with keys: architecture, domains, capabilities, improvements"""

        llm_response = self._call_ollama_llm(
            prompt,
            model=model_config["model"],
            temperature=model_config["temperature"]
        )

        if llm_response:
            try:
                return json.loads(llm_response)
            except json.JSONDecodeError:
                return {"llm_analysis": llm_response, "generated_at": datetime.now(timezone.utc).isoformat()}
        return None

    def generate_documentation(
        self,
        package_path: str = "src/curriculum",
        use_llm: bool = True,
    ) -> Dict[str, Any]:
        """Generate comprehensive documentation for the entire package."""
        start_time = time.time()
        logger.info(f"Starting documentation generation for package: {package_path}")

        try:
            package_root = Path(package_path)

            # Validate package path
            if not package_root.exists():
                raise ValueError(f"Package path does not exist: {package_path}")

            if not package_root.is_dir():
                raise ValueError(f"Package path is not a directory: {package_path}")

            logger.info(f"Processing package at: {package_root}")

            # Extract documentation from all modules
            logger.info("Extracting package documentation...")
            self._extract_package_documentation(package_root)

            # Generate LLM summaries if enabled
            if use_llm:
                logger.info("Generating LLM summaries...")
                self._generate_llm_summaries()

                logger.info("Exporting LLM analyses to Markdown...")
                llm_md_export = self.export_llm_analyses_to_markdown()

                logger.info("Generating search index...")
                search_index = self.generate_search_index()
            else:
                llm_md_export = None
                search_index = None

            # Generate final documentation files
            logger.info("Generating output files...")
            self._generate_output_files()

            # Calculate duration
            duration = time.time() - start_time

            result = {
                "status": "success",
                "output_directory": str(self.output_dir),
                "modules_documented": len(self._module_docs),
                "files_documented": len(self._file_docs),
                "methods_documented": len(self._method_docs),
                "llm_summaries_generated": len(self._llm_summaries),
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "generation_duration_seconds": duration,
            }

            if use_llm:
                result["llm_markdown_exports"] = llm_md_export
                result["search_index"] = {
                    "generated": True,
                    "modules_indexed": len(search_index.get("modules", {})),
                    "files_indexed": len(search_index.get("files", {})),
                    "keywords": len(search_index.get("keywords", [])),
                    "index_file": str(self.output_dir / "search_index.json")
                }
            else:
                result["search_index"] = {
                    "generated": False,
                    "reason": "LLM analysis disabled"
                }

            # Add performance metrics
            result["performance_metrics"] = self.get_performance_metrics()

            logger.info(f"Documentation generation completed successfully in {duration:.2f}s")
            return result

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Error generating documentation: {e}")
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "error": str(e),
                "output_directory": str(self.output_dir),
                "modules_documented": len(self._module_docs),
                "files_documented": len(self._file_docs),
                "methods_documented": len(self._method_docs),
                "llm_summaries_generated": len(self._llm_summaries),
                "generation_duration_seconds": duration,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }

    def _extract_package_documentation(self, package_root: Path) -> None:
        """Extract documentation from all Python files in package."""
        logger.info(f"Extracting documentation from package: {package_root}")

        files_processed = 0
        files_with_errors = 0

        for python_file in package_root.rglob("*.py"):
            try:
                # Skip __pycache__ and test files
                if "__pycache__" in str(python_file):
                    continue

                logger.debug(f"Processing file: {python_file}")

                # Check if file has changed (for cache invalidation)
                file_path_str = str(python_file)
                if self._check_file_changed(file_path_str):
                    logger.debug(f"File changed, invalidating cache: {python_file}")
                    self._invalidate_cache_for_file(file_path_str)

                # Extract file documentation
                file_doc = self._extract_file_documentation(python_file)
                if file_doc:
                    self._file_docs[str(python_file)] = file_doc

                    # Update statistics
                    self._stats["total_files"] += 1
                    self._stats["total_classes"] += file_doc.get("total_classes", 0)
                    self._stats["total_functions"] += file_doc.get("total_functions", 0)
                    self._stats["total_methods"] += file_doc.get("total_methods", 0)

                    # Extract module documentation
                    module_name = self._get_module_name(python_file, package_root)
                    if module_name:
                        self._module_docs[module_name] = {
                            "file_path": str(python_file),
                            "module_name": module_name,
                            "documentation": file_doc,
                        }
                        self._stats["total_modules"] = len(self._module_docs)

                        logger.debug(f"Extracted module: {module_name}")
                    else:
                        logger.debug(f"Could not extract module name for: {python_file}")

                    files_processed += 1
                else:
                    logger.debug(f"No documentation extracted for: {python_file}")

            except Exception as e:
                logger.warning(f"Error processing file {python_file}: {e}")
                files_with_errors += 1
                self._performance_metrics["errors_encountered"] += 1

        logger.info(f"Package documentation extraction complete: {files_processed} files processed, {files_with_errors} errors")

    def _extract_file_documentation(self, file_path: Path) -> Dict[str, Any]:
        """Extract documentation from a single Python file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                source = f.read()
            
            tree = ast.parse(source)
            
            # Extract module docstring
            module_docstring = ast.get_docstring(tree)
            
            # Extract classes and functions
            classes = []
            functions = []
            imports = []
            
            # First pass - extract top-level items
            for node in tree.body:
                if isinstance(node, ast.ClassDef):
                    class_info = self._extract_class_info(node)
                    classes.append(class_info)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    func_info = self._extract_function_info(node)
                    functions.append(func_info)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.append(self._extract_import_info(node))
            
            return {
                "file_path": str(file_path),
                "module_docstring": module_docstring,
                "imports": imports,
                "classes": classes,
                "functions": functions,
                "total_classes": len(classes),
                "total_functions": len(functions),
                "lines_of_code": len(source.splitlines()),
            }
        
        except Exception as e:
            return {
                "file_path": str(file_path),
                "error": str(e),
            }

    def _extract_class_info(self, node: ast.ClassDef) -> Dict[str, Any]:
        """Extract information from a class definition."""
        docstring = ast.get_docstring(node)
        
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_info = self._extract_function_info(item, is_method=True)
                methods.append(method_info)
                
                # Store method documentation separately
                method_key = f"{node.name}.{item.name}"
                self._method_docs[method_key] = method_info
        
        # Extract base classes
        bases = [self._get_name(base) for base in node.bases]
        
        return {
            "name": node.name,
            "docstring": docstring,
            "bases": bases,
            "methods": methods,
            "total_methods": len(methods),
            "line_number": node.lineno,
        }

    def _extract_function_info(
        self, 
        node: ast.FunctionDef, 
        is_method: bool = False
    ) -> Dict[str, Any]:
        """Extract information from a function or method definition."""
        docstring = ast.get_docstring(node)
        
        # Extract parameters
        params = []
        if hasattr(node, 'args') and hasattr(node.args, 'args'):
            # Get default values (they correspond to the last N arguments)
            defaults = node.args.defaults
            num_defaults = len(defaults)

            for i, arg in enumerate(node.args.args):
                # Extract default value if this argument has one
                default_value = None
                if i >= len(node.args.args) - num_defaults and num_defaults > 0:
                    default_index = i - (len(node.args.args) - num_defaults)
                    if default_index >= 0:
                        default_value = ast.unparse(defaults[default_index])

                param_info = {
                    "name": arg.arg,
                    "annotation": self._get_annotation(arg.annotation) if arg.annotation else None,
                    "default": default_value,
                }
                params.append(param_info)
        
        # Extract return type
        return_type = self._get_annotation(node.returns) if node.returns else None
        
        # Extract decorators
        decorators = [self._get_name(dec) for dec in node.decorator_list]
        
        return {
            "name": node.name,
            "docstring": docstring,
            "parameters": params,
            "args": params,  # Keep backward compatibility with tests
            "return_type": return_type,
            "decorators": decorators,
            "is_method": is_method,
            "is_async": isinstance(node, ast.AsyncFunctionDef),
            "line_number": node.lineno,
        }

    def _extract_import_info(self, node) -> Dict[str, Any]:
        """Extract import information."""
        if isinstance(node, ast.Import):
            return {
                "type": "import",
                "modules": [alias.name for alias in node.names],
            }
        elif isinstance(node, ast.ImportFrom):
            return {
                "type": "from_import",
                "module": node.module,
                "names": [alias.name for alias in node.names],
            }
        return {}

    def _get_name(self, node) -> str:
        """Get name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            # Handle subscripted types like Optional[str], List[int], etc.
            base = self._get_name(node.value)
            if hasattr(node.slice, 'elts'):  # Tuple of types
                args = ', '.join(self._get_name(elt) for elt in node.slice.elts)
            else:  # Single type
                args = self._get_name(node.slice)
            return f"{base}[{args}]"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        return str(node)

    def _get_annotation(self, node) -> str:
        """Get type annotation as string."""
        if node is None:
            return None
        return self._get_name(node)

    def _get_module_name(self, file_path: Path, package_root: Path) -> str:
        """Get module name from file path."""
        try:
            relative_path = file_path.relative_to(package_root)
            parts = list(relative_path.parts[:-1])  # Exclude filename
            if relative_path.stem != "__init__":
                parts.append(relative_path.stem)
            return ".".join(parts) if parts else None
        except ValueError:
            return None

    def _generate_llm_summaries(self) -> None:
        """Generate LLM-powered summaries at multiple levels with caching and parallel processing."""
        logger.info("Generating LLM summaries with caching and parallel processing...")

        # Prepare all summary tasks
        summary_tasks = []

        # Package overview
        package_overview = self._generate_package_overview()
        if package_overview:
            summary_tasks.append(("package_overview", {"data": package_overview}))

        # Module summaries
        for module_name in sorted(self._module_docs.keys()):
            module_data = self._module_docs[module_name]
            summary_tasks.append((f"module_{module_name}", {
                "type": "module",
                "module_name": module_name,
                "module_data": module_data
            }))

        # File summaries
        for file_path in sorted(self._file_docs.keys()):
            file_data = self._file_docs[file_path]
            summary_tasks.append((f"file_{file_path}", {
                "type": "file",
                "file_path": file_path,
                "file_data": file_data
            }))

        # Process in parallel
        if summary_tasks:
            results = self._process_summaries_parallel(summary_tasks)
            self._llm_summaries.update(results)

        logger.info(f"Generated {len(self._llm_summaries)} LLM summaries (parallel processing with caching)")

    def _process_summaries_parallel(self, summary_tasks: List[Tuple[str, Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
        """Process LLM summary tasks in parallel with rate limiting."""
        logger.info(f"Processing {len(summary_tasks)} summary tasks in parallel")

        async def process_with_limit(task_key: str, task_data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
            """Process a single summary task with semaphore limiting."""
            semaphore = asyncio.Semaphore(self._max_concurrent_llm_calls)

            async with semaphore:
                task_type = task_data.get("type")

                try:
                    if task_type == "module":
                        # For module summaries
                        module_name = task_data.get("module_name")
                        module_data = task_data.get("module_data")
                        result = self._generate_module_summary(module_name, module_data)
                        logger.debug(f"Processed module summary: {module_name}")
                        return task_key, result

                    elif task_type == "file":
                        # For file summaries
                        file_path = task_data.get("file_path")
                        file_data = task_data.get("file_data")
                        result = self._generate_file_summary(file_path, file_data)
                        logger.debug(f"Processed file summary: {file_path}")
                        return task_key, result

                    else:
                        # For package overview or other types
                        data = task_data.get("data", {})
                        logger.debug(f"Processed package overview")
                        return task_key, data

                except Exception as e:
                    logger.error(f"Error processing task {task_key}: {e}")
                    # Return empty result on error
                    return task_key, {}

        async def main_async():
            tasks = [process_with_limit(key, data) for key, data in summary_tasks]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle any exceptions that occurred
            processed_results = {}
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    task_key = summary_tasks[i][0]
                    logger.error(f"Task {task_key} failed with exception: {result}")
                    processed_results[task_key] = {}
                else:
                    task_key, task_result = result
                    processed_results[task_key] = task_result

            return processed_results

        # Run the async function
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, run differently
                import nest_asyncio
                nest_asyncio.apply()
                return loop.run_until_complete(main_async())
            else:
                return loop.run_until_complete(main_async())

        except RuntimeError as e:
            # Fallback to sequential processing if asyncio fails
            logger.warning(f"Asyncio failed, falling back to sequential processing: {e}")
            results = {}
            for key, data in summary_tasks:
                try:
                    task_type = data.get("type")
                    if task_type == "module":
                        module_name = data.get("module_name")
                        module_data = data.get("module_data")
                        results[key] = self._generate_module_summary(module_name, module_data)
                    elif task_type == "file":
                        file_path = data.get("file_path")
                        file_data = data.get("file_data")
                        results[key] = self._generate_file_summary(file_path, file_data)
                    else:
                        results[key] = data.get("data", {})
                except Exception as e:
                    logger.error(f"Error in sequential processing for {key}: {e}")
                    results[key] = {}

            return results

    def _generate_module_summary(
        self, 
        module_name: str, 
        module_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate LLM summary for a module using optimized model."""
        model_config = self._select_model_for_analysis("module_analysis")

        # Prepare context for LLM
        context = self._prepare_module_context(module_data)

        prompt = f"""Analyze this Python module and provide a comprehensive summary:

Module: {module_name}

Context:
{context}

Please provide:
1. A brief overview (2-3 sentences)
2. Key classes and their purposes
3. Main functionality provided
4. Dependencies and integrations
5. Usage examples if apparent from the code

Format your response as JSON with keys: overview, key_classes, functionality, dependencies, usage_hints"""

        # Call Ollama LLM with optimized model
        llm_response = self._call_ollama_llm(
            prompt,
            model=model_config["model"],
            temperature=model_config["temperature"]
        )
        
        if llm_response:
            return {
                "module_name": module_name,
                "summary_type": "module",
                "llm_analysis": llm_response,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
        
        return None

    def _generate_file_summary(
        self, 
        file_path: str, 
        file_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Generate LLM summary for a file using optimized model."""
        model_config = self._select_model_for_analysis("file_deep_analysis")

        context = self._prepare_file_context(file_data)

        prompt = f"""Analyze this Python file and provide a detailed summary:

File: {file_path}

Context:
{context}

Please provide:
1. File purpose and role
2. Main components (classes/functions)
3. Code complexity assessment
4. Potential improvements or concerns

Format your response as JSON with keys: purpose, components, complexity, improvements"""

        llm_response = self._call_ollama_llm(
            prompt,
            model=model_config["model"],
            temperature=model_config["temperature"]
        )
        
        if llm_response:
            return {
                "file_path": file_path,
                "summary_type": "file",
                "llm_analysis": llm_response,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
        
        return None

    def _generate_package_overview(self) -> Optional[Dict[str, Any]]:
        """Generate high-level package overview."""
        # Aggregate all module information
        total_modules = len(self._module_docs)
        total_classes = sum(
            doc["documentation"].get("total_classes", 0) 
            for doc in self._module_docs.values()
        )
        total_functions = sum(
            doc["documentation"].get("total_functions", 0) 
            for doc in self._module_docs.values()
        )
        
        module_list = list(self._module_docs.keys())
        
        prompt = f"""Provide a high-level architectural overview of this Python package:

Package Statistics:
- Total Modules: {total_modules}
- Total Classes: {total_classes}
- Total Functions: {total_functions}

Modules:
{chr(10).join(f'- {m}' for m in module_list[:20])}  # Limit to first 20

Please provide:
1. Overall architecture and design patterns
2. Key domain areas and their organization
3. System capabilities and features
4. Suggested improvements for structure and organization

Format your response as JSON with keys: architecture, domains, capabilities, improvements"""
        
        llm_response = self._call_ollama_llm(prompt, model="gemma2:2b")
        
        if llm_response:
            return {
                "summary_type": "package_overview",
                "statistics": {
                    "total_modules": total_modules,
                    "total_classes": total_classes,
                    "total_functions": total_functions,
                },
                "llm_analysis": llm_response,
                "generated_at": datetime.now(timezone.utc).isoformat(),
            }
        
        return None

    def _prepare_module_context(self, module_data: Dict[str, Any]) -> str:
        """Prepare context string for module analysis."""
        doc = module_data.get("documentation", module_data)
        
        context_parts = []
        
        if doc.get("module_docstring"):
            context_parts.append(f"Module Docstring: {doc['module_docstring']}")
        
        if doc.get("classes"):
            context_parts.append(f"\nClasses ({len(doc['classes'])}):")
            for cls in doc["classes"][:5]:  # Limit to first 5
                context_parts.append(f"  - {cls['name']}: {cls.get('docstring', 'No docstring')[:100]}")
        
        if doc.get("functions"):
            context_parts.append(f"\nFunctions ({len(doc['functions'])}):")
            for func in doc["functions"][:5]:  # Limit to first 5
                context_parts.append(f"  - {func['name']}: {func.get('docstring', 'No docstring')[:100]}")
        
        return "\n".join(context_parts)

    def _prepare_file_context(self, file_data: Dict[str, Any]) -> str:
        """Prepare context string for file analysis."""
        context_parts = [
            f"Lines of Code: {file_data.get('lines_of_code', 0)}",
            f"Classes: {file_data.get('total_classes', 0)}",
            f"Functions: {file_data.get('total_functions', 0)}",
        ]
        
        if file_data.get("module_docstring"):
            context_parts.append(f"Docstring: {file_data['module_docstring'][:200]}")
        
        return "\n".join(context_parts)

    def _call_ollama_llm(
        self,
        prompt: str,
        model: str = "llama3.1",
        temperature: float = 0.3
    ) -> Optional[str]:
        """Call Ollama LLM for text generation with comprehensive error handling and caching."""
        if not prompt or not prompt.strip():
            logger.warning("Empty or invalid prompt provided to LLM")
            return self._generate_mock_llm_response(prompt)

        try:
            # Check cache first
            cache_key = self._get_cache_key(prompt, model)
            cached_response = self._get_cached_response(cache_key)

            if cached_response:
                logger.debug(f"Cache hit for model {model}, prompt length: {len(prompt)}")
                return cached_response.get("response", "")

            logger.info(f"Calling Ollama LLM with model {model}, prompt length: {len(prompt)}")

            # Try REST API first
            try:
                import requests

                url = "http://localhost:11434/api/generate"
                payload = {
                    "model": model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "stream": False,
                }

                response = requests.post(url, json=payload, timeout=self._llm_timeout_seconds)
                self._performance_metrics["llm_api_calls"] += 1

                if response.status_code == 200:
                    try:
                        result = response.json()
                        llm_response = result.get("response", "").strip()

                        if not llm_response:
                            logger.warning("Empty response from Ollama API")
                            return self._generate_mock_llm_response(prompt)

                        # Cache the response
                        self._cache_response(cache_key, {"response": llm_response, "model": model}, file_path)
                        logger.debug(f"Successfully called Ollama API with model {model}")
                        return llm_response

                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse Ollama API response as JSON: {e}")
                        return self._generate_mock_llm_response(prompt)

                else:
                    logger.warning(f"Ollama API returned status {response.status_code}")

            except ImportError:
                logger.warning("requests library not available, trying subprocess")
            except requests.exceptions.RequestException as e:
                logger.warning(f"Ollama API request failed: {e}")
            except Exception as e:
                logger.warning(f"Ollama API call failed: {e}")

            # Fallback to subprocess method
            try:
                logger.debug(f"Trying subprocess method with model {model}")
                result = subprocess.run(
                    ["ollama", "run", model, "--", prompt],
                    capture_output=True,
                    text=True,
                    timeout=self._llm_timeout_seconds,
                    input=prompt,
                )

                if result.returncode == 0:
                    llm_response = result.stdout.strip()
                    self._performance_metrics["llm_subprocess_calls"] += 1

                    if not llm_response:
                        logger.warning("Empty response from Ollama subprocess")
                        return self._generate_mock_llm_response(prompt)

                    # Cache the response
                    self._cache_response(cache_key, {"response": llm_response, "model": model}, file_path)
                    logger.debug(f"Successfully called Ollama subprocess with model {model}")
                    return llm_response
                else:
                    logger.warning(f"Ollama subprocess returned non-zero exit code: {result.returncode}")
                    logger.debug(f"Subprocess stderr: {result.stderr}")

            except subprocess.TimeoutExpired:
                logger.error(f"Ollama subprocess timed out after {self._llm_timeout_seconds} seconds")
            except FileNotFoundError:
                logger.error("Ollama command not found - is Ollama installed and running?")
            except Exception as e:
                logger.error(f"Ollama subprocess call failed: {e}")

                # All methods failed, use mock response
                mock_response = self._generate_mock_llm_response(prompt)
                self._cache_response(cache_key, {"response": mock_response, "model": model})
                logger.warning(f"Using mock response due to Ollama unavailability for model {model}")
                return mock_response

        except Exception as e:
            logger.error(f"Unexpected error in _call_ollama_llm: {e}")
            logger.error(traceback.format_exc())
            # Return mock response as final fallback
            return self._generate_mock_llm_response(prompt)

    def _generate_mock_llm_response(self, prompt: str) -> str:
        """Generate mock LLM response when Ollama is unavailable."""
        return "This is a placeholder response. Install and run Ollama for AI-powered analysis."

    def _generate_output_files(self) -> None:
        """Generate final documentation output files."""
        # Generate module documentation files
        for module_name, module_data in self._module_docs.items():
            self._write_module_documentation(module_name, module_data)
        
        # Generate file documentation
        for file_path, file_data in self._file_docs.items():
            self._write_file_documentation(file_path, file_data)
        
        # Generate method documentation
        self._write_methods_index()
        
        # Generate LLM summaries
        self._write_llm_summaries()
        
        # Generate main index
        self._write_main_index()

    def _write_module_documentation(
        self, 
        module_name: str, 
        module_data: Dict[str, Any]
    ) -> None:
        """Write documentation for a single module."""
        safe_name = module_name.replace(".", "_")
        output_file = self.output_dir / "modules" / f"{safe_name}.md"
        
        doc = module_data["documentation"]
        
        content = [
            f"# Module: {module_name}\n",
            f"**File:** `{module_data['file_path']}`\n",
        ]
        
        if doc.get("module_docstring"):
            content.append(f"## Description\n\n{doc['module_docstring']}\n")
        
        # Classes
        if doc.get("classes"):
            content.append("## Classes\n")
            for cls in doc["classes"]:
                content.append(f"### `{cls['name']}`\n")
                if cls.get("docstring"):
                    content.append(f"{cls['docstring']}\n")
                if cls.get("bases"):
                    content.append(f"**Inherits from:** {', '.join(cls['bases'])}\n")
                content.append(f"**Methods:** {cls['total_methods']}\n")
                
                # List methods
                if cls.get("methods"):
                    content.append("\n**Method List:**\n")
                    for method in cls["methods"]:
                        content.append(f"- `{method['name']}`: {method.get('docstring', 'No description')[:50]}\n")
        
        # Functions
        if doc.get("functions"):
            content.append("## Functions\n")
            for func in doc["functions"]:
                content.append(f"### `{func['name']}`\n")
                if func.get("docstring"):
                    content.append(f"{func['docstring']}\n")
                if func.get("parameters"):
                    content.append("**Parameters:**\n")
                    for param in func["parameters"]:
                        param_type = f": {param['annotation']}" if param['annotation'] else ""
                        content.append(f"- `{param['name']}{param_type}`\n")
        
        # LLM Summary
        llm_key = f"module_{module_name}"
        if llm_key in self._llm_summaries:
            content.append("\n## AI-Generated Analysis\n")
            content.append(f"```json\n{self._llm_summaries[llm_key]['llm_analysis']}\n```\n")
        
        output_file.write_text("\n".join(content))

    def _write_file_documentation(self, file_path: str, file_data: Dict[str, Any]) -> None:
        """Write documentation for a single file."""
        safe_name = Path(file_path).stem + "_" + str(uuid4())[:8]
        output_file = self.output_dir / "files" / f"{safe_name}.json"
        
        output_file.write_text(json.dumps(file_data, indent=2))

    def _write_methods_index(self) -> None:
        """Write index of all methods."""
        output_file = self.output_dir / "methods" / "index.json"
        output_file.write_text(json.dumps(self._method_docs, indent=2))

    def _write_llm_summaries(self) -> None:
        """Write all LLM summaries to files."""
        for summary_key, summary_data in self._llm_summaries.items():
            safe_name = summary_key.replace("/", "_").replace(".", "_")
            output_file = self.output_dir / "llm_analysis" / f"{safe_name}.json"
            output_file.write_text(json.dumps(summary_data, indent=2))
        
        # Also write a combined summary
        combined_file = self.output_dir / "llm_analysis" / "all_summaries.json"
        combined_file.write_text(json.dumps(self._llm_summaries, indent=2))

    def _write_main_index(self) -> None:
        """Write main index file."""
        index_data = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "statistics": {
                "total_modules": len(self._module_docs),
                "total_files": len(self._file_docs),
                "total_methods": len(self._method_docs),
                "total_llm_summaries": len(self._llm_summaries),
            },
            "modules": list(self._module_docs.keys()),
            "output_structure": {
                "modules": "Module-level documentation (Markdown)",
                "files": "File-level documentation (JSON)",
                "methods": "Method index and documentation (JSON)",
                "llm_analysis": "AI-generated summaries and analysis (JSON)",
                "summaries": "Human-readable summaries (Markdown)",
            },
        }
        
        # Write JSON index
        index_file = self.output_dir / "index.json"
        index_file.write_text(json.dumps(index_data, indent=2))
        
        # Write Markdown index
        readme_content = [
            "# Auto-Generated Documentation\n",
            f"**Generated:** {datetime.now(timezone.utc).isoformat()}\n",
            "## Statistics\n",
            f"- **Modules Documented:** {index_data['statistics']['total_modules']}",
            f"- **Files Analyzed:** {index_data['statistics']['total_files']}",
            f"- **Methods Extracted:** {index_data['statistics']['total_methods']}",
            f"- **LLM Summaries Generated:** {index_data['statistics']['total_llm_summaries']}\n",
            "## Documentation Structure\n",
            "### `/modules`",
            "Module-level documentation in Markdown format.\n",
            "### `/files`",
            "Detailed file-level analysis in JSON format.\n",
            "### `/methods`",
            "Index of all methods and functions.\n",
            "### `/llm_analysis`",
            "AI-generated summaries and architectural analysis.\n",
            "### `/summaries`",
            "Human-readable summary documents.\n",
            "## Modules Documented\n",
        ]
        
        for module in sorted(index_data["modules"]):
            safe_name = module.replace(".", "_")
            readme_content.append(f"- [{module}](modules/{safe_name}.md)")
        
        readme_file = self.output_dir / "README.md"
        readme_file.write_text("\n".join(readme_content))

    def get_documentation_stats(self) -> Dict[str, Any]:
        """Get statistics about generated documentation."""
        return {
            "modules": len(self._module_docs),
            "files": len(self._file_docs),
            "methods": len(self._method_docs),
            "llm_summaries": len(self._llm_summaries),
            "output_directory": str(self.output_dir),
        }

    def generate_search_index(self) -> Dict[str, Any]:
        """Generate a searchable index for all documentation."""
        print("Generating search index...")

        search_index = {
            "modules": {},
            "files": {},
            "classes": {},
            "functions": {},
            "keywords": {},
            "domains": {},
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

        # Index modules
        for module_name, module_data in self._module_docs.items():
            search_index["modules"][module_name] = {
                "file_path": module_data.get("file_path", ""),
                "summary": self._extract_text_from_llm(module_name, "module"),
                "classes": [cls["name"] for cls in module_data.get("classes", [])],
                "functions": [func["name"] for func in module_data.get("functions", [])]
            }

            # Index classes
            for cls in module_data.get("classes", []):
                class_key = f"{module_name}.{cls['name']}"
                search_index["classes"][class_key] = {
                    "module": module_name,
                    "name": cls["name"],
                    "docstring": cls.get("docstring", ""),
                    "methods": [method["name"] for method in cls.get("methods", [])]
                }

                # Index methods
                for method in cls.get("methods", []):
                    method_key = f"{module_name}.{cls['name']}.{method['name']}"
                    search_index["functions"][method_key] = {
                        "module": module_name,
                        "class": cls["name"],
                        "name": method["name"],
                        "signature": self._extract_method_signature(method),
                        "docstring": method.get("docstring", "")
                    }

        # Index files
        for file_path, file_data in self._file_docs.items():
            search_index["files"][file_path] = {
                "module": self._get_module_name_from_path(file_path),
                "summary": self._extract_text_from_llm(file_path, "file"),
                "classes": [cls["name"] for cls in file_data.get("classes", [])],
                "functions": [func["name"] for func in file_data.get("functions", [])]
            }

        # Extract keywords from all content
        all_content = []
        for key, data in self._llm_summaries.items():
            if isinstance(data, dict) and "llm_analysis" in data:
                all_content.append(str(data["llm_analysis"]))

        # Simple keyword extraction (can be enhanced with NLP)
        keywords = set()
        for content in all_content:
            words = content.lower().split()
            for word in words:
                if len(word) > 4:  # Only meaningful words
                    keywords.add(word)

        search_index["keywords"] = list(keywords)
        search_index["total_documents"] = len(self._llm_summaries)

        # Save search index
        index_file = self.output_dir / "search_index.json"
        with open(index_file, "w") as f:
            json.dump(search_index, f, indent=2)

        print(f"  Generated search index with {len(search_index['modules'])} modules, {len(search_index['files'])} files")
        return search_index

    def _extract_text_from_llm(self, key: str, summary_type: str) -> str:
        """Extract searchable text from LLM analysis."""
        if key not in self._llm_summaries:
            return ""

        data = self._llm_summaries[key]
        if "llm_analysis" in data:
            return str(data["llm_analysis"])
        return ""

    def _extract_method_signature(self, method: Dict[str, Any]) -> str:
        """Extract method signature for search indexing."""
        params = []
        for arg in method.get("args", []):
            param_str = arg["name"]
            if arg.get("annotation"):
                param_str += f": {arg['annotation']}"
            if arg.get("default"):
                param_str += f" = {arg['default']}"
            params.append(param_str)

        signature = f"def {method['name']}({', '.join(params)})"
        if method.get("return_type"):
            signature += f" -> {method['return_type']}"

        return signature

    def _get_module_name_from_path(self, file_path: str) -> str:
        """Extract module name from file path."""
        try:
            path_obj = Path(file_path)
            # Remove .py extension and convert to module notation
            module_parts = path_obj.stem.replace(".", "_").split("_")
            return ".".join(module_parts)
        except:
            return "unknown"

    def search_documentation(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search documentation using simple text matching."""
        if not hasattr(self, '_search_index'):
            self._search_index = self.generate_search_index()

        results = []
        query_lower = query.lower()

        # Search modules
        for module_name, module_data in self._search_index["modules"].items():
            score = 0
            text_to_search = f"{module_name} {module_data.get('summary', '')}".lower()

            if query_lower in module_name.lower():
                score += 10
            if query_lower in text_to_search:
                score += 5

            if score > 0:
                results.append({
                    "type": "module",
                    "name": module_name,
                    "score": score,
                    "path": module_data.get("file_path", ""),
                    "summary": module_data.get("summary", "")[:200]
                })

        # Search files
        for file_path, file_data in self._search_index["files"].items():
            score = 0
            text_to_search = f"{file_path} {file_data.get('summary', '')}".lower()

            if query_lower in file_path.lower():
                score += 8
            if query_lower in text_to_search:
                score += 4

            if score > 0:
                results.append({
                    "type": "file",
                    "name": file_path,
                    "score": score,
                    "module": file_data.get("module", ""),
                    "summary": file_data.get("summary", "")[:200]
                })

        # Sort by score and return top results
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]

    def answer_question_about_codebase(self, question: str) -> str:
        """Answer questions about the codebase using RAG approach."""
        print(f"Answering question: {question}")

        # First, search for relevant documentation
        search_results = self.search_documentation(question, max_results=5)

        if not search_results:
            return "I couldn't find relevant documentation to answer your question."

        # Build context from search results
        context_parts = []
        for result in search_results:
            if result["type"] == "module":
                context_parts.append(f"Module: {result['name']}\n{result['summary']}")
            elif result["type"] == "file":
                context_parts.append(f"File: {result['name']}\n{result['summary']}")

        context = "\n\n".join(context_parts)

        # Create enhanced prompt
        model_config = self._select_model_for_analysis("code_review")
        prompt = f"""Based on the following documentation context, answer this question about the codebase:

Question: {question}

Relevant Documentation:
{context}

Provide a clear, accurate answer based on the documentation. If the documentation doesn't contain enough information, say so clearly."""

        # Get answer from LLM
        answer = self._call_ollama_llm(
            prompt,
            model=model_config["model"],
            temperature=0.2  # Lower temperature for factual answers
        )

        return answer or "I couldn't generate an answer to your question."

    def export_documentation(
        self, 
        format: str = "markdown", 
        output_file: Optional[str] = None
    ) -> str:
        """Export all documentation in a single file."""
        if format == "markdown":
            return self._export_markdown(output_file)
        elif format == "json":
            return self._export_json(output_file)
        else:
            return f"Unsupported format: {format}"

    def _export_markdown(self, output_file: Optional[str] = None) -> str:
        """Export documentation as single Markdown file."""
        output_path = output_file or str(self.output_dir / "complete_documentation.md")
        
        content = [
            "# Complete System Documentation\n",
            f"**Generated:** {datetime.now(timezone.utc).isoformat()}\n",
            "---\n",
        ]
        
        # Add all module documentation
        for module_name in sorted(self._module_docs.keys()):
            safe_name = module_name.replace(".", "_")
            module_file = self.output_dir / "modules" / f"{safe_name}.md"
            if module_file.exists():
                content.append(module_file.read_text())
                content.append("\n---\n")
        
        Path(output_path).write_text("\n".join(content))
        return output_path

    def _export_json(self, output_file: Optional[str] = None) -> str:
        """Export documentation as single JSON file."""
        output_path = output_file or str(self.output_dir / "complete_documentation.json")
        
        complete_data = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "modules": self._module_docs,
            "files": self._file_docs,
            "methods": self._method_docs,
            "llm_summaries": self._llm_summaries,
        }
        
        # Add statistics if available
        if hasattr(self, '_stats'):
            complete_data["statistics"] = self._stats
        
        Path(output_path).write_text(json.dumps(complete_data, indent=2))
        return output_path

    def _convert_llm_json_to_markdown(self, analysis_key: str, analysis_data: Dict[str, Any]) -> str:
        """Convert a single LLM analysis JSON to readable Markdown."""
        content = []
        
        # Title based on summary type
        summary_type = analysis_data.get("summary_type", "unknown")
        
        if summary_type == "package_overview":
            content.append("# Package Architectural Overview\n")
        elif summary_type == "module":
            module_name = analysis_data.get("module_name", "Unknown Module")
            content.append(f"# Module Analysis: `{module_name}`\n")
        elif summary_type == "file":
            file_path = analysis_data.get("file_path", "Unknown File")
            file_name = Path(file_path).name if file_path != "Unknown File" else "Unknown"
            content.append(f"# File Analysis: `{file_name}`\n")
            content.append(f"**Full Path:** `{file_path}`\n")
        else:
            content.append(f"# {summary_type.title()} Analysis\n")
        
        # Generated timestamp
        generated_at = analysis_data.get("generated_at", "Unknown")
        content.append(f"**Generated:** {generated_at}\n")
        content.append("---\n")
        
        # Statistics if available
        if "statistics" in analysis_data:
            content.append("\n## Statistics\n")
            stats = analysis_data["statistics"]
            for key, value in stats.items():
                formatted_key = key.replace("_", " ").title()
                content.append(f"- **{formatted_key}:** {value}")
            content.append("\n")
        
        # Module/file name if present
        if "module_name" in analysis_data and summary_type != "module":
            content.append(f"\n**Module:** `{analysis_data['module_name']}`\n")
        
        # LLM Analysis - the main content
        content.append("\n## AI-Generated Analysis\n")
        
        llm_analysis = analysis_data.get("llm_analysis", "No analysis available")
        
        # Check if it's already formatted JSON
        if llm_analysis.strip().startswith("{") or llm_analysis.strip().startswith("```"):
            content.append(llm_analysis)
        else:
            content.append(llm_analysis)
        
        content.append("\n")
        
        # Metadata
        content.append("\n## Metadata\n")
        content.append(f"- **Analysis Type:** {summary_type}")
        content.append(f"- **Analysis Key:** `{analysis_key}`")
        content.append(f"- **Generated At:** {generated_at}")
        content.append("\n")
        
        return "\n".join(content)

    def export_llm_analyses_to_markdown(self) -> Dict[str, int]:
        """Export all LLM analyses as standalone Markdown files and a combined file.
        
        Returns:
            Dict with counts of exported files
        """
        print("Exporting LLM analyses to Markdown...")
        
        # Create output directory for Markdown LLM analyses
        llm_md_dir = self.output_dir / "llm_analysis_md"
        llm_md_dir.mkdir(parents=True, exist_ok=True)
        
        standalone_count = 0
        
        # Export each LLM analysis as a standalone Markdown file
        for analysis_key, analysis_data in self._llm_summaries.items():
            # Generate Markdown content
            md_content = self._convert_llm_json_to_markdown(analysis_key, analysis_data)
            
            # Create informative filename
            summary_type = analysis_data.get("summary_type", "unknown")
            
            if summary_type == "package_overview":
                filename = "00_package_overview.md"
            elif summary_type == "module":
                module_name = analysis_data.get("module_name", "unknown").replace(".", "_")
                filename = f"module_{module_name}.md"
            elif summary_type == "file":
                # Extract filename from path
                file_path = analysis_data.get("file_path", "unknown")
                safe_name = Path(file_path).stem.replace(".", "_") if file_path != "unknown" else "unknown"
                filename = f"file_{safe_name}.md"
            else:
                filename = f"{summary_type}_{analysis_key}.md"
            
            # Write standalone file
            output_file = llm_md_dir / filename
            output_file.write_text(md_content)
            standalone_count += 1
        
        print(f"  ✓ Exported {standalone_count} standalone Markdown files")
        
        # Create combined Markdown file
        combined_content = self._create_combined_llm_markdown()
        combined_file = self.output_dir / "llm_analysis_complete.md"
        combined_file.write_text(combined_content)
        
        print(f"  ✓ Created combined Markdown file: {combined_file}")
        
        return {
            "standalone_files": standalone_count,
            "combined_file": 1,
            "output_directory": str(llm_md_dir),
        }

    def _create_combined_llm_markdown(self) -> str:
        """Create a single combined Markdown file with all LLM analyses."""
        content = []
        
        # Header
        content.append("# Complete LLM Analysis - Curriculum Repository System\n")
        content.append(f"**Generated:** {datetime.now(timezone.utc).isoformat()}\n")
        content.append(f"**Total Analyses:** {len(self._llm_summaries)}\n")
        content.append("---\n")
        
        # Table of Contents
        content.append("\n## Table of Contents\n")
        
        # Organize by type
        package_analyses = []
        module_analyses = []
        file_analyses = []
        
        for key, data in self._llm_summaries.items():
            summary_type = data.get("summary_type", "unknown")
            if summary_type == "package_overview":
                package_analyses.append((key, data))
            elif summary_type == "module":
                module_analyses.append((key, data))
            elif summary_type == "file":
                file_analyses.append((key, data))
        
        if package_analyses:
            content.append("\n### Package Overview")
            for key, data in package_analyses:
                content.append(f"- [Package Architectural Overview](#package-architectural-overview)")
        
        if module_analyses:
            content.append("\n### Module Analyses")
            for key, data in sorted(module_analyses, key=lambda x: x[1].get("module_name", "")):
                module_name = data.get("module_name", "Unknown")
                anchor = module_name.lower().replace(".", "-")
                content.append(f"- [Module: {module_name}](#module-analysis-{anchor})")
        
        if file_analyses:
            content.append(f"\n### File Analyses ({len(file_analyses)} files)")
            content.append("*(See individual sections below)*")
        
        content.append("\n---\n")
        
        # Package Overview Section
        if package_analyses:
            content.append("\n# Package Overview\n")
            for key, data in package_analyses:
                md_section = self._convert_llm_json_to_markdown(key, data)
                content.append(md_section)
                content.append("\n---\n")
        
        # Module Analyses Section
        if module_analyses:
            content.append("\n# Module Analyses\n")
            for key, data in sorted(module_analyses, key=lambda x: x[1].get("module_name", "")):
                md_section = self._convert_llm_json_to_markdown(key, data)
                content.append(md_section)
                content.append("\n---\n")
        
        # File Analyses Section
        if file_analyses:
            content.append("\n# File Analyses\n")
            for key, data in sorted(file_analyses, key=lambda x: x[1].get("file_path", "")):
                md_section = self._convert_llm_json_to_markdown(key, data)
                content.append(md_section)
                content.append("\n---\n")
        
        # Footer
        content.append("\n## Summary\n")
        content.append(f"- **Total Analyses:** {len(self._llm_summaries)}")
        content.append(f"- **Package Overviews:** {len(package_analyses)}")
        content.append(f"- **Module Analyses:** {len(module_analyses)}")
        content.append(f"- **File Analyses:** {len(file_analyses)}")
        content.append(f"\n**Generated:** {datetime.now(timezone.utc).isoformat()}\n")
        
        return "\n".join(content)

