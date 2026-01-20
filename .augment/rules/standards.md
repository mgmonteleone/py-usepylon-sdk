---
type: "always_apply"
description: "Core Python SDK development standards, code quality, and git workflow"
---

# Python SDK Development Standards

## Python Version and Style

- Target Python 3.11+ with modern features (`match`, `|` union types)
- Use type hints for all function signatures and class attributes
- Use `str | None` instead of `Optional[str]`
- Use Google-style docstrings for all public modules, classes, and functions

## Object-Oriented Design

- Use OOP with clear single responsibilities (SOLID principles)
- Favor composition over inheritance
- Use abstract base classes (ABC) for interfaces
- Implement proper encapsulation with underscore conventions

## Code Organization

```
src/pylon/
├── __init__.py
├── _client.py
├── _http.py
├── _version.py
├── exceptions.py
├── models/
├── resources/
└── webhooks/
```

## Naming Conventions

- Classes: `PascalCase`
- Functions/methods: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_single_leading_underscore`

## Dependency Management

This project uses **uv** for dependency management.

**CRITICAL: Always run these commands when changing dependencies or version:**

```bash
# After ANY change to pyproject.toml (dependencies OR version)
uv lock

# Verify lock file is in sync before committing
uv lock --check
```

- Always use the most recent stable versions of libraries
- Use package managers (uv, pip) - never edit pyproject.toml manually for deps
- CI uses `--locked` flag - builds fail if lock file is stale

## Code Quality Tools

Run before every commit:

```bash
ruff check .
ruff format --check .
mypy .
pytest
```

### Ruff Configuration

The project uses ruff for linting and formatting with Black-compatible style:
- Line length: 88 characters
- Double quotes for strings

## Git Workflow

### Commit Message Format

Use conventional commits:

```
<type>(<scope>): <subject>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`

### Branch Strategy

- `main`: Production-ready, always stable
- `feature/`: New features (e.g., `feature/add-pagination`)
- `fix/`: Bug fixes (e.g., `fix/retry-logic`)

### Pre-Commit Checklist

1. [ ] All tests pass: `pytest`
2. [ ] No linting errors: `ruff check .`
3. [ ] Code is formatted: `ruff format --check .`
4. [ ] Type checks pass: `mypy .`
5. [ ] Lock file in sync: `uv lock --check`
6. [ ] No secrets in code

## Semantic Versioning

Version format: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking API changes
- **MINOR**: New features (backwards-compatible)
- **PATCH**: Bug fixes

### Version File

Single source of truth: `src/pylon/_version.py`

```python
__version__ = "0.1.0"
```

Note: `pyproject.toml` uses dynamic versioning via hatch, reading from `_version.py`.

### Version Bump Procedure

```bash
# 1. Update version file
# Edit src/pylon/_version.py: __version__ = "X.Y.Z"

# 2. Commit and tag
git add src/pylon/_version.py
git commit -m "chore: bump version to X.Y.Z for release"
git tag -a vX.Y.Z -m "Release version X.Y.Z"
git push origin main --tags
```

## SDK-Specific Patterns

- Use Pydantic v2 for all data models
- Use httpx for HTTP client
- Use tenacity for retry logic
- Implement async/sync client variants
- Provide clear error hierarchy in `exceptions.py`

