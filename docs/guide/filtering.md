# Filtering

Build complex queries using the fluent filter API.

## Basic Filters

Use `Field()` to create filters:

```python
from pylon.filters import Field

# Equality
Field("state").eq("open")

# Inequality  
Field("state").neq("closed")

# In list
Field("priority").in_(["high", "urgent"])

# Not in list
Field("priority").not_in(["low"])
```

## Comparison Filters

```python
# Greater than
Field("priority").gt(3)

# Greater than or equal
Field("priority").gte(3)

# Less than
Field("priority").lt(5)

# Less than or equal
Field("priority").lte(5)
```

## String Filters

```python
# Contains substring
Field("title").contains("urgent")

# Starts with
Field("title").starts_with("[BUG]")

# Ends with
Field("email").ends_with("@example.com")
```

## Date Filters

```python
from datetime import datetime, timedelta

now = datetime.now()
week_ago = now - timedelta(days=7)

# After date
Field("created_at").after(week_ago)

# Before date
Field("created_at").before(now)

# Between dates
Field("created_at").between(week_ago, now)
```

## Null Checks

```python
# Is null (unassigned)
Field("assignee_id").is_null()

# Is not null
Field("closed_at").is_not_null()
```

## Combining Filters

### Using Classes

```python
from pylon.filters import And, Or, Not

# AND: both conditions must match
And(
    Field("state").eq("open"),
    Field("priority").gte(3)
)

# OR: either condition matches
Or(
    Field("state").eq("open"),
    Field("state").eq("pending")
)

# NOT: negate a condition
Not(Field("state").eq("closed"))
```

### Using Operators

Use Python operators for more readable code:

```python
# AND with &
open_high = Field("state").eq("open") & Field("priority").gte(3)

# OR with |
open_or_pending = Field("state").eq("open") | Field("state").eq("pending")

# NOT with ~
not_closed = ~Field("state").eq("closed")

# Complex combinations
complex_filter = (
    (Field("state").eq("open") | Field("state").eq("pending"))
    & ~Field("priority").lt(3)
)
```

