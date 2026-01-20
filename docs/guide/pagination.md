# Pagination

The SDK handles pagination automatically, so you can focus on processing results.

## Automatic Iteration

Simply iterate over results - pagination is handled behind the scenes:

```python
with PylonClient() as client:
    # All pages are fetched as you iterate
    for issue in client.issues.list():
        print(issue.title)
```

## Collect All Results

To get all results as a list:

```python
with PylonClient() as client:
    all_issues = client.issues.list().collect()
    print(f"Found {len(all_issues)} issues")
```

!!! warning "Memory Usage"
    `collect()` loads all results into memory. For large result sets,
    prefer iteration to avoid memory issues.

## Limiting Results

Control the number of results per page:

```python
# 50 items per API request
for issue in client.issues.list(limit=50):
    print(issue.title)
```

## Time-Based Filtering

Many resources support time-based filtering:

```python
# Issues from the last 7 days
for issue in client.issues.list(days=7):
    print(issue.title)

# Or with explicit dates
from datetime import datetime, timedelta

end = datetime.now()
start = end - timedelta(days=30)

for issue in client.issues.list(start_time=start, end_time=end):
    print(issue.title)
```

## Async Pagination

The async client works the same way:

```python
async with AsyncPylonClient() as client:
    # Async iteration
    async for issue in client.issues.list():
        print(issue.title)
```

