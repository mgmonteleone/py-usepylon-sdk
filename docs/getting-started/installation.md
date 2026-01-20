# Installation

## Requirements

- Python 3.11 or higher
- A Pylon API key (get one from your [Pylon dashboard](https://app.usepylon.com))

## Install from PyPI

The recommended way to install py-usepylon-sdk:

```bash
pip install py-usepylon-sdk
```

Or with [uv](https://github.com/astral-sh/uv):

```bash
uv add py-usepylon-sdk
```

## Install from Source

For development or to get the latest changes:

```bash
git clone https://github.com/mgmonteleone/py-usepylon-sdk.git
cd py-usepylon-sdk
uv sync --all-extras
```

## Configuration

Set your API key as an environment variable:

```bash
export PYLON_API_KEY="your-api-key"
```

Or pass it directly to the client:

```python
from pylon import PylonClient

client = PylonClient(api_key="your-api-key")
```

## Verify Installation

```python
from pylon import PylonClient

with PylonClient() as client:
    # List first issue to verify connection
    for issue in client.issues.list(limit=1):
        print(f"Connected! Found issue: {issue.title}")
        break
```

