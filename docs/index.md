# py-usepylon-sdk

A modern, fully-typed Python SDK for the [Pylon](https://usepylon.com) customer support API.

## Features

- ✨ **Full API Coverage** - Issues, accounts, contacts, messages, webhooks, and more
- 🔒 **Type-safe** - Complete type hints with Pydantic v2 models
- ⚡ **Async Support** - Both sync and async clients for maximum flexibility
- 🔄 **Automatic Pagination** - Seamlessly iterate through all results
- 🎯 **Filter Builder** - Fluent API for building complex queries
- 🔔 **Webhook Handler** - Secure webhook signature verification and event routing
- 🛡️ **Robust Error Handling** - Detailed exception hierarchy for all error types
- 🐍 **Modern Python** - Requires Python 3.11+, uses modern typing syntax

## Quick Example

```python
from pylon import PylonClient

with PylonClient(api_key="your-api-key") as client:
    # List recent issues
    for issue in client.issues.list(days=7):
        print(f"#{issue.number}: {issue.title}")
```

## Installation

```bash
pip install py-usepylon-sdk
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv add py-usepylon-sdk
```

## Next Steps

- [Getting Started Guide](getting-started/quickstart.md) - Learn the basics
- [API Reference](api/client.md) - Detailed API documentation
- [Examples](https://github.com/mgmonteleone/py-usepylon-sdk/tree/main/examples) - Real-world usage examples

