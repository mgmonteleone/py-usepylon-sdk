# py-usepylon-sdk

A modern Python SDK for the [Pylon](https://usepylon.com) customer support API.

## Features

- **Type-safe models** - All Pylon API entities are represented as Pydantic v2 models
- **Comprehensive exceptions** - Clear exception hierarchy for different error scenarios
- **Webhook support** - Parse and validate Pylon webhook events
- **Modern Python** - Requires Python 3.11+, uses modern typing syntax

## Installation

```bash
pip install py-usepylon-sdk
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv add py-usepylon-sdk
```

## Quick Start

> **Note**: Phase 1 of this SDK includes models, exceptions, and webhook support. The `PylonClient` for making API calls will be available in a future release.

### Working with Models

```python
from pylon.models import PylonIssue, PylonUser

# Parse API response data into type-safe models
issue_data = {
    "id": "issue_123",
    "number": 42,
    "title": "Example Issue",
    "status": "open",
    # ... other fields
}
issue = PylonIssue.from_pylon_dict(issue_data)
print(f"#{issue.number}: {issue.title}")
```

## Webhook Handling

```python
from pylon.webhooks import parse_webhook_event, IssueNewEvent

# Parse incoming webhook payload
event = parse_webhook_event(payload)

if isinstance(event, IssueNewEvent):
    print(f"New issue: {event.issue_title}")
```

## Exception Handling

```python
from pylon.exceptions import (
    PylonAPIError,
    PylonAuthenticationError,
    PylonNotFoundError,
    PylonRateLimitError,
    PylonValidationError,
)

# All Pylon exceptions inherit from PylonError
# Use them to handle different error scenarios when the client is available

# Example exception usage (when client is implemented):
# try:
#     issue = client.issues.get("nonexistent_id")
# except PylonNotFoundError as e:
#     print(f"Issue not found: {e.message}")
# except PylonAuthenticationError:
#     print("Invalid API key")
# except PylonRateLimitError as e:
#     print(f"Rate limited. Retry after {e.retry_after} seconds")
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/mgmonteleone/py-usepylon-sdk.git
cd py-usepylon-sdk

# Install with development dependencies
uv sync --all-extras
```

### Running Tests

```bash
uv run pytest
```

### Linting and Type Checking

```bash
uv run ruff check .
uv run mypy src/
```

## License

MIT License - see [LICENSE](LICENSE) for details.

