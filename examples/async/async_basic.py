#!/usr/bin/env python3
"""Example: Async client usage.

This example demonstrates how to:
- Use the AsyncPylonClient
- Perform async iteration over results
- Make concurrent API calls
"""

import asyncio
import os

from pylon import AsyncPylonClient


async def main():
    """Demonstrate async client usage."""
    api_key = os.environ.get("PYLON_API_KEY")
    if not api_key:
        print("Please set PYLON_API_KEY environment variable")
        return

    # Use async context manager
    async with AsyncPylonClient(api_key=api_key) as client:
        print("=== Async Issue Listing ===")

        # Async iteration
        count = 0
        async for issue in client.issues.list(days=7):
            count += 1
            print(f"#{issue.number}: {issue.title}")
            if count >= 5:
                print("... (showing first 5)")
                break

        # Get a specific issue
        print("\n=== Get Specific Issue ===")
        # Replace with an actual issue ID
        try:
            issue = await client.issues.get("issue_123")
            print(f"Issue: {issue.title}")
        except Exception as e:
            print(f"Could not fetch issue: {e}")


async def concurrent_requests():
    """Make multiple requests concurrently."""
    async with AsyncPylonClient() as client:
        # Fetch multiple issues concurrently
        issue_ids = ["issue_1", "issue_2", "issue_3"]

        tasks = [client.issues.get(issue_id) for issue_id in issue_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for issue_id, result in zip(issue_ids, results, strict=True):
            if isinstance(result, Exception):
                print(f"Error fetching {issue_id}: {result}")
            else:
                print(f"Fetched: {result.title}")


async def parallel_list_operations():
    """List multiple resources in parallel."""
    async with AsyncPylonClient() as client:
        # Start both list operations
        issues_task = asyncio.create_task(collect_async(client.issues.list(days=7)))
        accounts_task = asyncio.create_task(collect_async(client.accounts.list()))

        # Wait for both to complete
        issues, accounts = await asyncio.gather(issues_task, accounts_task)

        print(f"Found {len(issues)} issues and {len(accounts)} accounts")


async def collect_async(async_iterator):
    """Helper to collect async iterator into a list."""
    items = []
    async for item in async_iterator:
        items.append(item)
    return items


if __name__ == "__main__":
    asyncio.run(main())
