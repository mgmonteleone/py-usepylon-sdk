#!/usr/bin/env python3
"""Example: Using the filter builder.

This example demonstrates how to:
- Use Field() to create simple filters
- Combine filters with AND/OR
- Use date range filters
- Apply filters to API calls
"""

import os
from datetime import datetime, timedelta

from pylon import PylonClient
from pylon.filters import And, Field, Not, Or


def main():
    """Demonstrate filter builder usage."""
    api_key = os.environ.get("PYLON_API_KEY")
    if not api_key:
        print("Please set PYLON_API_KEY environment variable")
        return

    with PylonClient(api_key=api_key) as _client:
        demonstrate_filters()


def demonstrate_filters():
    """Show various filter building techniques."""
    print("=== Filter Builder Examples ===\n")

    # 1. Simple equality filter
    print("1. Simple equality:")
    filter1 = Field("state").eq("open")
    print(f"   {filter1.to_dict()}")

    # 2. Inequality filter
    print("\n2. Inequality:")
    filter2 = Field("state").neq("closed")
    print(f"   {filter2.to_dict()}")

    # 3. In-list filter
    print("\n3. In list:")
    filter3 = Field("priority").in_(["high", "urgent"])
    print(f"   {filter3.to_dict()}")

    # 4. Comparison filters
    print("\n4. Comparisons:")
    filter4 = Field("priority").gte(3)
    print(f"   Greater than or equal: {filter4.to_dict()}")

    filter5 = Field("touches").lt(5)
    print(f"   Less than: {filter5.to_dict()}")

    # 5. String filters
    print("\n5. String matching:")
    filter6 = Field("title").contains("urgent")
    print(f"   Contains: {filter6.to_dict()}")

    filter7 = Field("title").starts_with("[BUG]")
    print(f"   Starts with: {filter7.to_dict()}")

    # 6. Date filters
    print("\n6. Date filters:")
    now = datetime.now()
    week_ago = now - timedelta(days=7)

    filter8 = Field("created_at").after(week_ago)
    print(f"   After: {filter8.to_dict()}")

    filter9 = Field("created_at").between(week_ago, now)
    print(f"   Between (returns And filter): {filter9.to_dict()}")

    # 7. Null checks
    print("\n7. Null checks:")
    filter10 = Field("assignee_id").is_null()
    print(f"   Is null: {filter10.to_dict()}")

    filter11 = Field("closed_at").is_not_null()
    print(f"   Is not null: {filter11.to_dict()}")

    # 8. Combining filters with AND
    print("\n8. AND combination:")
    combined_and = And(
        Field("state").eq("open"),
        Field("priority").gte(3),
    )
    print(f"   {combined_and.to_dict()}")

    # 9. Combining filters with OR
    print("\n9. OR combination:")
    combined_or = Or(
        Field("state").eq("open"),
        Field("state").eq("pending"),
    )
    print(f"   {combined_or.to_dict()}")

    # 10. NOT filter
    print("\n10. NOT filter:")
    negated = Not(Field("state").eq("closed"))
    print(f"   {negated.to_dict()}")

    # 11. Operator overloading (& | ~)
    print("\n11. Using operators (&, |, ~):")
    using_operators = (
        Field("state").eq("open") | Field("state").eq("pending")
    ) & ~Field("priority").lt(3)
    print(f"   {using_operators.to_dict()}")

    # 12. Complex nested filter
    print("\n12. Complex nested filter:")
    complex_filter = And(
        Or(
            Field("state").eq("open"),
            Field("state").eq("pending"),
        ),
        Field("created_at").after(week_ago),
        Not(Field("assignee_id").is_null()),
    )
    print(f"   {complex_filter.to_dict()}")


if __name__ == "__main__":
    # Just demonstrate filter building (no API calls needed)
    demonstrate_filters()
