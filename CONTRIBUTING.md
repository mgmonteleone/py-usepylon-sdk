# Contributing to py-usepylon-sdk

Thank you for your interest in contributing to the Pylon Python SDK! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.11 or higher
- [uv](https://docs.astral.sh/uv/) package manager (recommended)

### Getting Started

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/py-usepylon-sdk.git
   cd py-usepylon-sdk
   ```

2. **Install dependencies with uv**:
   ```bash
   uv sync
   ```

3. **Verify setup by running tests**:
   ```bash
   uv run pytest tests/
   ```

## Development Workflow

### Creating a Branch

Create a feature branch for your changes:
```bash
git checkout -b feature/your-feature-name
```

Use these prefixes:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring

### Running Quality Checks

Before committing, run all quality checks:

```bash
# Linting
uv run ruff check .

# Formatting
uv run ruff format .

# Type checking
uv run mypy src/

# Tests
uv run pytest tests/

# Lock file sync
uv lock --check
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

**Examples**:
```
feat(issues): add bulk update method
fix(webhooks): handle missing timestamp header
docs: update README with new examples
```

## Code Style

- Follow PEP 8 with 88 character line length
- Use type hints for all functions and methods
- Write docstrings for all public APIs (Google style)
- Keep functions focused and under 50 lines when possible

### Example

```python
def get_issue(self, issue_id: str) -> PylonIssue:
    """Retrieve an issue by ID.

    Args:
        issue_id: The unique identifier of the issue.

    Returns:
        The issue object.

    Raises:
        PylonNotFoundError: If the issue doesn't exist.
    """
    response = self._client.get(f"/issues/{issue_id}")
    return PylonIssue.model_validate(response)
```

## Testing

- Write tests for all new functionality
- Aim for 80%+ coverage on new code
- Use pytest fixtures for common setup
- Mock external API calls with `respx`

```bash
# Run tests with coverage
uv run pytest tests/ --cov=src/pylon --cov-report=term-missing
```

## Pull Request Process

1. **Create a PR** against the `main` branch
2. **Fill out the PR template** completely
3. **Ensure CI passes** (tests, linting, type checking)
4. **Request review** from maintainers
5. **Address feedback** and update as needed
6. **Squash merge** once approved

## Reporting Issues

- Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) for bugs
- Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md) for enhancements
- Search existing issues before creating new ones

## Questions?

Feel free to open a [discussion](https://github.com/mgmonteleone/py-usepylon-sdk/discussions) for questions or ideas.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

