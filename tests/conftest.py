"""Shared pytest fixtures for Pylon SDK tests."""

from typing import Any

import pytest


def make_issue_data(
    issue_id: str = "issue_123",
    number: int = 42,
    title: str = "Test Issue",
    **overrides: Any,
) -> dict[str, Any]:
    """Create valid issue data for tests.

    Args:
        issue_id: Issue ID.
        number: Issue number.
        title: Issue title.
        **overrides: Additional field overrides.

    Returns:
        Dictionary with valid issue data.
    """
    base_data = {
        "id": issue_id,
        "number": number,
        "title": title,
        "link": f"https://app.usepylon.com/issues/{issue_id}",
        "body_html": "<p>Test body</p>",
        "state": "open",
        "latest_message_time": "2024-01-01T12:00:00Z",
        "created_at": "2024-01-01T00:00:00Z",
        "customer_portal_visible": True,
        "source": "email",
        "type": "Conversation",
        "number_of_touches": 1,
    }
    base_data.update(overrides)
    return base_data


@pytest.fixture
def issue_data() -> dict[str, Any]:
    """Fixture providing valid issue data."""
    return make_issue_data()


@pytest.fixture
def issue_list_page_1() -> dict[str, Any]:
    """First page of paginated issues."""
    return {
        "data": [make_issue_data(issue_id="issue_1", number=1, title="Issue 1")],
        "pagination": {"cursor": "cursor_1", "has_more": True},
    }


@pytest.fixture
def issue_list_page_2() -> dict[str, Any]:
    """Second page of paginated issues."""
    return {
        "data": [make_issue_data(issue_id="issue_2", number=2, title="Issue 2")],
        "pagination": {"cursor": "cursor_2", "has_more": False},
    }

