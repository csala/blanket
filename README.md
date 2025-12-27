# Blanket

Blank Line Enforcement

## Overview

Blanket enforces separation of logical code blocks in Python with proper usage of blank lines,
using indentation changes and keywords as a primary way to know where logical blocks start or end.

## Usage

Run on one or more files:

```bash
blanket path/to/file.py
```

Use from Python:

```python
from blanket import enforce

enforce(["path/to/file.py"])
```

## Pre-commit

Add the hook to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/csala/blanket
    rev: v0.1.0
    hooks:
      - id: blanket
```

Install and run:

```bash
pre-commit install
pre-commit run blanket --all-files
```

## Development Roadmap

- [x] Standalone script to run on individual files
- [x] Installable package and cli tool to run on individual files
- [ ] Pre-commit hook
- [ ] Run recursively on folders
- [ ] Separate validation from file formatting
- [ ] Add discovery CLI options (such as exclude or include)
- [ ] Read options from pyproject
- [ ] Add formatting options
