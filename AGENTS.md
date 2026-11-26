# Working on Course

Start at [the docs index](docs/index.md) for the library workflow,
architecture, module map and manuscript. The [contributing
guide](CONTRIBUTING.md) covers branch, code and review conventions.

- Install from `uv.lock` using the [quickstart](docs/quickstart.md).
- Keep request adapters in `src/curriculum/routes/`, business logic in
  the owning service package, and validated records in
  `src/curriculum/core/`. Read the nearest `AGENTS.md` before editing a
  module.
- Use the [test and documentation commands](docs/development/testing.md)
  to check changes. Keep tests isolated from real external services.
- Keep maintained guides under `docs/` and authored publication sources
  under `docs/manuscript/`. Keep module README files as navigation to the
  matching guide. Rendered manuscripts are generated locally.
- Preserve published snapshots. Update references to changed code,
  examples and supported commands in the same change.
