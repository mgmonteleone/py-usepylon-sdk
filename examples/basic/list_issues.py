#!/usr/bin/env python3
"""Example: List issues from Pylon.

This example demonstrates how to:
- Initialize the PylonClient
- List issues with time-based filtering
- Access issue properties
- Use pagination to get all results
"""

import os

from pylon import PylonClient


def main():
    """List recent issues from Pylon."""
    # Get API key from environment variable
    api_key = os.environ.get("PYLON_API_KEY")
    if not api_key:
        print("Please set PYLON_API_KEY environment variable")
        return

    # Use context manager for automatic cleanup
    with PylonClient(api_key=api_key) as client:
        print("Fetching issues from the last 7 days...\n")

        # List issues from the last 7 days
        issue_count = 0
        for issue in client.issues.list(days=7):
            issue_count += 1
            print(f"#{issue.number}: {issue.title}")
            print(f"  State: {issue.state}")
            print(f"  Source: {issue.source}")
            print(f"  Created: {issue.created_at}")
            if issue.assignee:
                print(f"  Assignee: {issue.assignee.id}")
            print()

        print(f"Total issues: {issue_count}")


def example_with_collect():
    """Alternative: Collect all issues into a list."""
    with PylonClient() as client:  # Uses PYLON_API_KEY env var
        # Collect all results at once (useful for smaller result sets)
        all_issues = client.issues.list(days=30).collect()
        print(f"Found {len(all_issues)} issues in the last 30 days")

        # Now you can work with the list
        open_issues = [i for i in all_issues if i.state == "open"]
        print(f"Open issues: {len(open_issues)}")


if __name__ == "__main__":
    main()
