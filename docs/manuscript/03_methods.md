# Verification methods

The local verification uses three independent interfaces. The Python
library creates a Markdown lesson, confirms its draft state and reads
the same UUID through the service. The web process starts on loopback
and exposes its health response and OpenAPI routes. The documentation
generator runs in a temporary directory with `use_llm=False`.

The offline generation result reports modules, files and extracted method
entries. Module names and source files are distinct units. The counts describe the extractor's
inventory of the package. The tests use synthetic lesson and user
identifiers. The [reproduction guide](https://github.com/docxology/course/blob/main/docs/development/manuscript.md) gives the exact commands.
