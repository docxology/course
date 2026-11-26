# Reproduce the software manuscript

Use the [library walkthrough](../library.md), [local health
check](../quickstart.md) and [offline documentation inventory](testing.md)
to collect the observations described in the manuscript. Compare the
file, module, method and model-summary counts with the committed
[evidence record](https://github.com/docxology/course/blob/main/data/ast_inventory.json).

To build PDF and HTML, use a dedicated
[Docxology Template checkout](https://github.com/docxology/template).
Install Pandoc, pandoc-crossref and XeLaTeX using Template's setup
instructions. The render was checked with Template revision
`87704feae0a4490ef7dad9c931d268e8c30273c2`.

From the Course checkout, register a clean worktree with that renderer:

```bash
template_dir=/absolute/path/to/template
git -C "$template_dir" switch --detach 87704feae0a4490ef7dad9c931d268e8c30273c2
mkdir -p "$template_dir/projects/working"
git worktree add --detach "$template_dir/projects/working/course" HEAD
cd "$template_dir"
uv sync --locked --python 3.14 --no-dev
uv run --no-sync python scripts/pipeline/stage_03_render.py --project working/course
uv run --no-sync python scripts/pipeline/stage_04_validate.py --project working/course
```

The output is under `projects/working/course/output/`.
Authored sections, configuration and bibliography are in
`docs/manuscript/` of the Course checkout.
