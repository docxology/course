# AI Agents Guide - Documentation Module

## Overview

The documentation module provides automated documentation generation with AI-powered analysis using LLMs (primarily Ollama). It extracts code structure, generates multi-level summaries, and produces comprehensive documentation.

## Module Structure

```
documentation/
├── generator.py        # Main documentation generator service
├── __init__.py         # Module exports
├── README.md           # User documentation
└── AGENTS.md           # This file
```

## Development Guidelines

### When Working on Documentation Features

1. **AST Parsing Best Practices**:
```python
def _extract_class_info(self, node: ast.ClassDef) -> Dict[str, Any]:
    """Extract comprehensive class information."""
    docstring = ast.get_docstring(node)
    
    # Extract methods
    methods = []
    for item in node.body:
        if isinstance(item, ast.FunctionDef):
            method_info = self._extract_function_info(item, is_method=True)
            methods.append(method_info)
    
    # Extract base classes
    bases = [self._get_name(base) for base in node.bases]
    
    return {
        "name": node.name,
        "docstring": docstring,
        "bases": bases,
        "methods": methods,
        "line_number": node.lineno,
    }
```

2. **LLM Integration Patterns**:
```python
def _call_ollama_llm(self, prompt: str, model: str = "llama3.2") -> Optional[str]:
    """Call Ollama with proper error handling."""
    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            timeout=30,
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return self._generate_mock_llm_response(prompt)
    
    except (subprocess.TimeoutExpired, FileNotFoundError):
        # Fallback when Ollama unavailable
        return self._generate_mock_llm_response(prompt)
```

3. **Output Organization**:
```python
def _setup_output_directories(self) -> None:
    """Create structured output directories."""
    directories = [
        self.output_dir,
        self.output_dir / "modules",
        self.output_dir / "files",
        self.output_dir / "methods",
        self.output_dir / "summaries",
        self.output_dir / "llm_analysis",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
```

### LLM Prompt Engineering

1. **Module Analysis Prompt**:
```python
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
```

2. **Package Overview Prompt**:
```python
prompt = f"""Provide a high-level architectural overview of this Python package:

Package Statistics:
- Total Modules: {total_modules}
- Total Classes: {total_classes}
- Total Functions: {total_functions}

Modules:
{module_list}

Please provide:
1. Overall architecture and design patterns
2. Key domain areas and their organization
3. System capabilities and features
4. Suggested improvements for structure and organization

Format your response as JSON"""
```

### Code Extraction Patterns

1. **Function/Method Extraction**:
```python
def _extract_function_info(self, node: ast.FunctionDef, is_method: bool = False):
    """Extract detailed function information."""
    # Extract parameters with type annotations
    params = []
    for arg in node.args.args:
        param_info = {
            "name": arg.arg,
            "annotation": self._get_annotation(arg.annotation) if arg.annotation else None,
        }
        params.append(param_info)
    
    # Extract return type
    return_type = self._get_annotation(node.returns) if node.returns else None
    
    return {
        "name": node.name,
        "docstring": ast.get_docstring(node),
        "parameters": params,
        "return_type": return_type,
        "is_async": isinstance(node, ast.AsyncFunctionDef),
    }
```

2. **Import Analysis**:
```python
def _extract_import_info(self, node) -> Dict[str, Any]:
    """Extract import statements."""
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
```

### Output Generation

1. **Markdown Generation**:
```python
def _write_module_documentation(self, module_name: str, module_data: Dict[str, Any]):
    """Write module documentation in Markdown."""
    content = [
        f"# Module: {module_name}\n",
        f"**File:** `{module_data['file_path']}`\n",
    ]
    
    # Add classes
    for cls in doc["classes"]:
        content.append(f"### `{cls['name']}`\n")
        if cls.get("docstring"):
            content.append(f"{cls['docstring']}\n")
    
    # Add LLM analysis
    if llm_key in self._llm_summaries:
        content.append("\n## AI-Generated Analysis\n")
        content.append(f"```json\n{self._llm_summaries[llm_key]['llm_analysis']}\n```\n")
    
    output_file.write_text("\n".join(content))
```

2. **JSON Export**:
```python
def _export_json(self, output_file: Optional[str] = None) -> str:
    """Export complete documentation as JSON."""
    complete_data = {
        "generated_at": datetime.utcnow().isoformat(),
        "modules": self._module_docs,
        "files": self._file_docs,
        "methods": self._method_docs,
        "llm_summaries": self._llm_summaries,
    }
    
    Path(output_path).write_text(json.dumps(complete_data, indent=2))
    return output_path
```

### Testing Requirements

- **Test AST parsing** for various code structures
- **Test LLM integration** with mock responses
- **Test output generation** in all formats
- **Test error handling** for malformed code
- **Test large codebases** for performance

Example test:
```python
def test_module_documentation_generation():
    """Test generating documentation for a module."""
    doc_service = DocumentationGeneratorService(output_dir="./test_docs")
    
    result = doc_service.generate_documentation(
        package_path="src/curriculum/core",
        use_llm=False,  # Skip LLM for faster testing
    )
    
    assert result["status"] == "success"
    assert result["modules_documented"] > 0
    assert (Path("./test_docs") / "index.json").exists()
```

### Performance Considerations

- **Large Files**: Process files in chunks if over 10k lines
- **LLM Calls**: Batch requests when possible (future enhancement)
- **Caching**: Cache AST parsing results for unchanged files
- **Parallel Processing**: Use multiprocessing for large codebases

### Common Patterns

#### Safe AST Node Name Extraction
```python
def _get_name(self, node) -> str:
    """Safely extract name from various AST node types."""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        return f"{self._get_name(node.value)}.{node.attr}"
    elif isinstance(node, ast.Subscript):
        return f"{self._get_name(node.value)}[...]"
    return str(node)
```

#### Error-Tolerant File Processing
```python
def _extract_file_documentation(self, file_path: Path) -> Dict[str, Any]:
    """Extract documentation with error handling."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        
        tree = ast.parse(source)
        # Process tree...
        
    except Exception as e:
        return {
            "file_path": str(file_path),
            "error": str(e),
        }
```

### Extension Points

- **Custom Extractors**: Add extractors for specific patterns
- **Additional LLM Providers**: Support OpenAI, Anthropic
- **Interactive Viewers**: Web-based documentation browser
- **Live Updates**: Watch mode for continuous documentation
- **Cross-References**: Automatic linking between modules

### Ollama Model Selection

Different models for different tasks:

1. **llama3.2**: General-purpose, balanced performance
2. **codellama**: Code-specific, better technical analysis
3. **mistral**: Fast summaries, good for overviews
4. **deepseek-coder**: Advanced code understanding

```python
# Use appropriate model for task
module_summary = self._call_ollama_llm(prompt, model="llama3.2")
code_analysis = self._call_ollama_llm(prompt, model="codellama")
quick_overview = self._call_ollama_llm(prompt, model="mistral")
```

### Best Practices

1. **Always provide fallbacks** when LLM is unavailable
2. **Structure prompts** for consistent JSON responses
3. **Limit context size** to avoid token limits
4. **Cache LLM responses** to avoid redundant calls
5. **Test without LLM** for faster CI/CD
6. **Document prompt templates** for reproducibility

### Debugging Tips

1. **Check AST parsing**:
```bash
python -c "import ast; ast.parse(open('file.py').read())"
```

2. **Test Ollama**:
```bash
ollama run llama3.2 "Summarize this code: def hello(): pass"
```

3. **Verify output structure**:
```bash
tree docs/generated/
cat docs/generated/index.json | jq
```

4. **Check for parsing errors**:
```python
for file_path, file_data in self._file_docs.items():
    if "error" in file_data:
        print(f"Error in {file_path}: {file_data['error']}")
```

## Integration with Other Modules

The documentation module can integrate with:

- **Content Module**: Document content types and formats
- **AI Module**: Use AI services for enhanced analysis
- **Export Module**: Include in exported packages
- **Search Module**: Make documentation searchable

## Future Enhancements

1. **Incremental Updates**: Only regenerate changed modules
2. **Diff Analysis**: Show documentation changes over time
3. **API Documentation**: Extract FastAPI endpoint docs
4. **Diagram Generation**: Create UML and architecture diagrams
5. **Interactive Explorer**: Web-based documentation viewer
6. **Multi-Language**: Support TypeScript, JavaScript, etc.

