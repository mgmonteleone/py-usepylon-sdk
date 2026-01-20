# Quick Start

This guide will help you get started with the Pylon SDK.

## Initialize the Client

```python
from pylon import PylonClient

# Using environment variable (recommended)
# Set PYLON_API_KEY in your environment
client = PylonClient()

# Or pass API key directly
client = PylonClient(api_key="your-api-key")
```

## Use as Context Manager

Always use the client as a context manager for proper cleanup:

```python
with PylonClient() as client:
    # Your code here
    issues = list(client.issues.list(days=7))
```

## List Resources

```python
with PylonClient() as client:
    # List issues from the last 7 days
    for issue in client.issues.list(days=7):
        print(f"#{issue.number}: {issue.title}")
    
    # List all accounts
    for account in client.accounts.list():
        print(f"Account: {account.name}")
    
    # List contacts
    for contact in client.contacts.list():
        print(f"Contact: {contact.name} ({contact.email})")
```

## Get a Specific Resource

```python
with PylonClient() as client:
    # Get issue by ID
    issue = client.issues.get("issue_abc123")
    print(f"Title: {issue.title}")
    print(f"State: {issue.state}")
    
    # Get issue by number
    issue = client.issues.get_by_number(42)
    print(f"#{issue.number}: {issue.title}")
```

## Async Usage

For async applications:

```python
import asyncio
from pylon import AsyncPylonClient

async def main():
    async with AsyncPylonClient() as client:
        async for issue in client.issues.list(days=7):
            print(f"#{issue.number}: {issue.title}")

asyncio.run(main())
```

## Error Handling

```python
from pylon import PylonClient
from pylon.exceptions import PylonNotFoundError, PylonAPIError

with PylonClient() as client:
    try:
        issue = client.issues.get("nonexistent")
    except PylonNotFoundError:
        print("Issue not found")
    except PylonAPIError as e:
        print(f"API error: {e.message}")
```

## Next Steps

- [Pagination Guide](../guide/pagination.md) - Handle large result sets
- [Filter Builder](../guide/filtering.md) - Build complex queries
- [Webhook Handling](../guide/webhooks.md) - Process incoming events

