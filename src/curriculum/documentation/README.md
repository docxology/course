# Documentation Module

The documentation module provides automated documentation generation with AI-powered multi-level summarization using Ollama.

## Features

- **Automated Extraction**: Automatically extracts documentation from all Python modules
- **AST Parsing**: Uses Python AST to analyze code structure, classes, and methods
- **LLM Summarization**: Leverages Ollama for intelligent multi-level code analysis
- **Multi-Format Output**: Generates documentation in Markdown and JSON formats
- **Structured Output**: Organizes documentation into logical subdirectories

## Services

- `DocumentationGeneratorService`: Main service for documentation generation

## Output Structure

```
docs/generated/
├── README.md                    # Main index and overview
├── index.json                   # Statistics and navigation
├── modules/                     # Module-level documentation (Markdown)
│   ├── core_base.md
│   ├── content_content.md
│   └── ...
├── files/                       # File-level analysis (JSON)
│   ├── base_abc123.json
│   └── ...
├── methods/                     # Method index and details
│   └── index.json
├── llm_analysis/               # AI-generated summaries
│   ├── all_summaries.json
│   ├── module_core_base.json
│   ├── package_overview.json
│   └── ...
└── summaries/                   # Additional summaries
```

## Usage

### Basic Documentation Generation

```python
from curriculum.documentation import DocumentationGeneratorService

# Initialize service
doc_service = DocumentationGeneratorService(output_dir="./docs/generated")

# Generate documentation for entire package
result = doc_service.generate_documentation(
    package_path="src/curriculum",
    use_llm=True,
)

print(f"Documentation generated in: {result['output_directory']}")
print(f"Modules documented: {result['modules_documented']}")
```

### Without LLM (Faster)

```python
# Generate without AI summarization
result = doc_service.generate_documentation(
    package_path="src/curriculum",
    use_llm=False,
)
```

### Export Complete Documentation

```python
# Export as single Markdown file
markdown_file = doc_service.export_documentation(
    format="markdown",
    output_file="./docs/complete_docs.md"
)

# Export as single JSON file
json_file = doc_service.export_documentation(
    format="json",
    output_file="./docs/complete_docs.json"
)
```

### Get Statistics

```python
stats = doc_service.get_documentation_stats()
print(f"Files analyzed: {stats['files']}")
print(f"Methods documented: {stats['methods']}")
print(f"LLM summaries: {stats['llm_summaries']}")
```

## LLM Integration

The module uses Ollama for AI-powered code analysis. It generates:

1. **Module-level summaries**: Overview, key classes, functionality
2. **File-level summaries**: Purpose, components, complexity assessment
3. **Package overview**: Architecture, design patterns, capabilities

### Ollama Setup

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull recommended models
ollama pull llama3.2
ollama pull codellama

# Verify installation
ollama list
```

### Supported Models

- `llama3.2` (default): General-purpose analysis
- `codellama`: Code-specific analysis and architecture review
- `mistral`: Alternative for summaries

## Output Examples

### Module Documentation (Markdown)

```markdown
# Module: curriculum.core.base

**File:** `src/curriculum/core/base.py`

## Description

Base classes and mixins for the curriculum system.

## Classes

### `BaseEntity`
Base entity with UUID, timestamps, and soft delete functionality.

**Inherits from:** UUIDMixin, TimestampMixin, SoftDeleteMixin
**Methods:** 3

## AI-Generated Analysis
{
  "overview": "Provides foundational classes for all entities...",
  "key_classes": ["BaseEntity", "UUIDMixin", "TimestampMixin"],
  ...
}
```

### LLM Analysis (JSON)

```json
{
  "module_name": "curriculum.core.base",
  "summary_type": "module",
  "llm_analysis": {
    "overview": "Core base classes providing common functionality...",
    "key_classes": {
      "BaseEntity": "Primary base class for all domain entities",
      "UUIDMixin": "Provides UUID primary key functionality"
    },
    "functionality": [
      "Soft delete support",
      "Automatic timestamp management",
      "UUID generation"
    ]
  }
}
```

## Performance Considerations

- **Large Codebases**: Processing time scales with codebase size
- **LLM Calls**: Each module makes 1-2 LLM API calls (can be slow)
- **Parallel Processing**: Not yet implemented (future enhancement)
- **Caching**: LLM responses are cached per generation run

## Testing

```bash
pytest tests/integration/test_documentation.py -v
pytest tests/integration/test_documentation_unit.py -v
pytest tests/integration/test_documentation_integration.py -v
pytest tests/integration/test_documentation_comprehensive.py -v
pytest tests/integration/test_documentation_edge_cases.py -v
pytest tests/performance/test_documentation_performance.py -v
```

## Configuration

The service respects these settings:

- `output_dir`: Where to write documentation (default: `./docs/generated`)
- `use_llm`: Whether to use Ollama for summarization (default: `True`)
- `llm_model`: Which Ollama model to use (default: `llama3.2`)

## Future Enhancements

- Parallel processing for faster generation
- Support for additional LLM providers (OpenAI, Anthropic)
- Interactive documentation browser
- Automatic documentation updates on code changes
- Cross-reference linking between modules
- API endpoint documentation extraction

