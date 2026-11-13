---
paths:
  - "**/*.py"
  - "**/templates/**/*.html"
---

# Python and Django Agent Advice

This file adds to `agent_advice.md` and loads only while working on Python or
Django template files.

## Python-Specific Style

- **Calling with named parameters is okay** - we can still catch missing
  parameters
- **All imports at the top of the file** - never use inline imports inside
  functions or methods, even in tests
- **Don't manually remove unused imports** - ruff handles this automatically
- **Never modify sys.path** - assume PYTHONPATH is set correctly
- **Don't use `from __future__ import annotations`** unless the project is on
  Python < 3.12 and you actually need it

## Test File Naming

**Unit tests mirror source directory structure:**

- `bar/foo.py` → `tests/bar/test_foo.py`
- `evaluation/metrics.py` → `tests/evaluation/test_metrics.py`
- `app/foo.py` → `app/tests/test_foo.py` (Django convention)
- `classifiers.py` → `tests/test_classifiers.py`

## Django

- **Minimal JavaScript**: Absolute bare minimum. Prefer server-side solutions.
- **When JS needed**: Use htmx first, custom JavaScript only as last resort.
- **Architecture**: Server-side rendering, standard HTML forms, progressive
  enhancement.
