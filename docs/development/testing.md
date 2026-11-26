# Tests and documentation builds

Install the locked development and documentation dependencies as described
in the [quickstart](../quickstart.md). From the repository root, run:

```bash
uv run --no-sync pytest tests/unit --no-cov
uv run --no-sync mkdocs build --clean --strict
```

The static site is written to the ignored `site/` directory. The
[development test guide](https://github.com/docxology/course/blob/main/tests/README.md)
maps integration, database and performance coverage. Read the fixtures
before enabling tests that use additional services.

The documentation workflow also exercises the native AST extractor with
the model provider disabled. To repeat that check in a temporary
directory:

```python
from tempfile import TemporaryDirectory

from curriculum.documentation import DocumentationGeneratorService

with TemporaryDirectory() as directory:
    generator = DocumentationGeneratorService(output_dir=directory)
    result = generator.generate_documentation("src/curriculum", use_llm=False)
    assert result["status"] == "success", result
    assert result["files_documented"] > 0
    print(generator.get_documentation_stats())
```

The command inventories the checked-out package. The committed
`docs/generated/` snapshot is excluded from the maintained MkDocs
navigation. Application package behavior is verified separately from the
[Template manuscript render](manuscript.md).
