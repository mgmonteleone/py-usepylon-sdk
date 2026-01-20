# Clients

The SDK provides two client classes for interacting with the Pylon API.

## Synchronous Client

The `PylonClient` is for synchronous applications:

```python
from pylon import PylonClient

# Create client
client = PylonClient(api_key="your-api-key")

# Use as context manager (recommended)
with PylonClient() as client:
    issues = list(client.issues.list())

# Or manage lifecycle manually
client = PylonClient()
try:
    issues = list(client.issues.list())
finally:
    client.close()
```

## Asynchronous Client

The `AsyncPylonClient` is for async applications:

```python
import asyncio
from pylon import AsyncPylonClient

async def main():
    # Use as async context manager
    async with AsyncPylonClient() as client:
        async for issue in client.issues.list():
            print(issue.title)

asyncio.run(main())
```

## Available Resources

Both clients provide access to the same resources:

| Resource | Description |
|----------|-------------|
| `client.issues` | Support tickets and conversations |
| `client.accounts` | Customer accounts/companies |
| `client.contacts` | Customer contacts |
| `client.users` | Team members/agents |
| `client.teams` | Support teams |
| `client.tags` | Issue and account tags |
| `client.messages` | Conversation messages |
| `client.tasks` | Follow-up tasks |
| `client.projects` | Customer projects |

## Configuration

### API Key

The API key can be provided in two ways:

1. Environment variable (recommended):
   ```bash
   export PYLON_API_KEY="your-api-key"
   ```
   
2. Direct parameter:
   ```python
   client = PylonClient(api_key="your-api-key")
   ```

### Custom Base URL

For testing or custom deployments:

```python
client = PylonClient(
    api_key="your-api-key",
    base_url="https://custom-api.example.com"
)
```

