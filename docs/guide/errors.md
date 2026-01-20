# Error Handling

The SDK provides a detailed exception hierarchy for handling errors.

## Exception Hierarchy

```
PylonError (base)
└── PylonAPIError (API errors)
    ├── PylonAuthenticationError (401)
    ├── PylonValidationError (400)
    ├── PylonNotFoundError (404)
    ├── PylonRateLimitError (429)
    └── PylonServerError (5xx)
```

## Basic Error Handling

```python
from pylon import PylonClient
from pylon.exceptions import (
    PylonAPIError,
    PylonNotFoundError,
    PylonAuthenticationError,
)

with PylonClient() as client:
    try:
        issue = client.issues.get("nonexistent")
    except PylonNotFoundError as e:
        print(f"Not found: {e.message}")
    except PylonAuthenticationError:
        print("Invalid API key")
    except PylonAPIError as e:
        print(f"API error [{e.status_code}]: {e.message}")
```

## Error Details

All `PylonAPIError` exceptions include:

- `status_code`: HTTP status code
- `message`: Error message from API
- `request_id`: Request ID for debugging (if available)

```python
try:
    issue = client.issues.get("bad_id")
except PylonAPIError as e:
    print(f"Status: {e.status_code}")
    print(f"Message: {e.message}")
    print(f"Request ID: {e.request_id}")
```

## Rate Limiting

Handle rate limits with retry logic:

```python
import time
from pylon.exceptions import PylonRateLimitError

def get_with_retry(client, issue_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.issues.get(issue_id)
        except PylonRateLimitError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = e.retry_after or 60
            print(f"Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
```

## Validation Errors

Validation errors include field-level details:

```python
from pylon.exceptions import PylonValidationError

try:
    client.contacts.create(name="", email="invalid")
except PylonValidationError as e:
    print(f"Validation failed: {e.message}")
    for error in e.errors:
        print(f"  {error['field']}: {error['message']}")
```

## Catching All Pylon Errors

```python
from pylon.exceptions import PylonError

try:
    # Any Pylon operation
    issue = client.issues.get("issue_123")
except PylonError as e:
    # Catches all Pylon-specific errors
    print(f"Pylon error: {e}")
```

