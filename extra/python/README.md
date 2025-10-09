# extra.python

This directory contains the Python package for the `dse.ncodec` project.

Layout
- `src/` — source packages (importable packages live under `src/`)
- `tests/` — unit tests (pytest)
- `pyproject.toml` — build metadata and packaging configuration
- `README.md` — this file

Install

Create a virtual environment and install the package in editable mode for development:

```bash
cd dse.ncodec/extra/python
python -m venv .venv
source .venv/bin/activate
pip install -e .[test]
```

Quick usage

```py

```

Run tests

```bash
pytest
```

Development notes

- The package uses a src-layout so packaging tools find packages under `src/`.
- Follow the repository license in the top-level `LICENSE` file.

Contact

Please update `pyproject.toml` authors and metadata with the appropriate project contact information.
