# Install and run locally

Install Git and [uv](https://docs.astral.sh/uv/getting-started/installation/).
From a terminal:

```bash
git clone https://github.com/docxology/course.git
cd course
uv python install
uv sync --locked --extra dev --extra docs
uv run --no-sync curriculum-server --help
```

The repository's `.python-version` selects the default development
interpreter. The dependency lock also supports running the library and
documentation checks with `uv sync --locked --python 3.14 --extra dev --extra docs`.

Start a local API with a fresh in-memory store:

```bash
uv run --no-sync curriculum-server serve --host 127.0.0.1 --port 8000
```

In a second terminal, run `curl -fsS http://127.0.0.1:8000/health`.
The response includes a healthy status, the application version and a
timestamp. Open `http://127.0.0.1:8000/docs` to inspect the routes. Stop
the process with Ctrl+C.

The [library walkthrough](library.md) needs no running server, database
or model service. See [architecture](architecture.md) for the distinction
between the default local stores and separately configured integrations.
