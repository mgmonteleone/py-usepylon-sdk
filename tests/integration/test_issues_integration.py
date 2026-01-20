"""Integration tests for issues resource with mocked API."""

import httpx
import pytest
import respx

from pylon import AsyncPylonClient, PylonClient
from pylon.exceptions import (
    PylonAuthenticationError,
    PylonNotFoundError,
    PylonRateLimitError,
)
from tests.conftest import make_issue_data


class TestIssuesIntegration:
    """Integration tests for issues resource."""

    @respx.mock
    def test_list_issues_workflow(self):
        """Should list issues with pagination."""
        call_count = 0

        def pagination_handler(_request):  # noqa: ARG001
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return httpx.Response(
                    200,
                    json={
                        "data": [
                            make_issue_data(
                                issue_id="issue_1", number=1, title="First"
                            ),
                            make_issue_data(
                                issue_id="issue_2", number=2, title="Second"
                            ),
                        ],
                        "pagination": {"cursor": "page2", "has_next_page": True},
                    },
                )
            else:
                return httpx.Response(
                    200,
                    json={
                        "data": [
                            make_issue_data(
                                issue_id="issue_3", number=3, title="Third"
                            ),
                        ],
                        "pagination": {"cursor": None, "has_next_page": False},
                    },
                )

        respx.get("https://api.usepylon.com/issues").mock(
            side_effect=pagination_handler
        )

        with PylonClient(api_key="test-key") as client:
            issues = list(client.issues.list())
            assert len(issues) == 3
            assert issues[0].title == "First"
            assert issues[2].title == "Third"

    @respx.mock
    def test_get_issue_by_id(self):
        """Should retrieve a single issue by ID."""
        respx.get("https://api.usepylon.com/issues/issue_123").mock(
            return_value=httpx.Response(
                200,
                json={"data": make_issue_data(issue_id="issue_123", number=42)},
            )
        )

        with PylonClient(api_key="test-key") as client:
            issue = client.issues.get("issue_123")
            assert issue.id == "issue_123"
            assert issue.number == 42

    @respx.mock
    def test_get_issue_not_found(self):
        """Should raise PylonNotFoundError for 404."""
        respx.get("https://api.usepylon.com/issues/nonexistent").mock(
            return_value=httpx.Response(
                404,
                json={"error": {"message": "Issue not found"}},
            )
        )

        with PylonClient(api_key="test-key") as client:
            with pytest.raises(PylonNotFoundError) as exc_info:
                client.issues.get("nonexistent")
            assert exc_info.value.status_code == 404

    @respx.mock
    def test_authentication_error(self):
        """Should raise PylonAuthenticationError for 401."""
        respx.get("https://api.usepylon.com/issues/issue_123").mock(
            return_value=httpx.Response(
                401,
                json={"error": {"message": "Invalid API key"}},
            )
        )

        with PylonClient(api_key="bad-key") as client:
            with pytest.raises(PylonAuthenticationError) as exc_info:
                client.issues.get("issue_123")
            assert exc_info.value.status_code == 401

    @respx.mock
    def test_rate_limit_error(self):
        """Should raise PylonRateLimitError for 429."""
        respx.get("https://api.usepylon.com/issues/issue_123").mock(
            return_value=httpx.Response(
                429,
                json={"error": {"message": "Rate limit exceeded"}},
            )
        )

        # Use max_retries=0 to avoid retry delays in tests
        with PylonClient(api_key="test-key", max_retries=0) as client:
            with pytest.raises(PylonRateLimitError) as exc_info:
                client.issues.get("issue_123")
            assert exc_info.value.status_code == 429

    @respx.mock
    def test_collect_all_issues(self):
        """Should collect all issues into a list."""
        respx.get("https://api.usepylon.com/issues").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        make_issue_data(issue_id=f"issue_{i}", number=i)
                        for i in range(5)
                    ],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            # The list() method returns a generator, use list() to collect
            issues = list(client.issues.list())
            assert isinstance(issues, list)
            assert len(issues) == 5


class TestAsyncIssuesIntegration:
    """Integration tests for async issues resource."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_list_issues(self):
        """Should list issues asynchronously."""
        respx.get("https://api.usepylon.com/issues").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        make_issue_data(issue_id="async_1", number=1),
                        make_issue_data(issue_id="async_2", number=2),
                    ],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            issues = []
            async for issue in client.issues.list():
                issues.append(issue)
            assert len(issues) == 2

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_issue(self):
        """Should get single issue asynchronously."""
        respx.get("https://api.usepylon.com/issues/async_123").mock(
            return_value=httpx.Response(
                200,
                json={"data": make_issue_data(issue_id="async_123", number=99)},
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            issue = await client.issues.get("async_123")
            assert issue.id == "async_123"
            assert issue.number == 99


class TestIssuesCRUDOperations:
    """Integration tests for issue CRUD operations."""

    @respx.mock
    def test_create_issue(self):
        """Should create a new issue."""
        respx.post("https://api.usepylon.com/issues").mock(
            return_value=httpx.Response(
                201,
                json={"data": make_issue_data(issue_id="new_issue", number=100)},
            )
        )

        with PylonClient(api_key="test-key") as client:
            issue = client.issues.create(
                title="New Issue", description="Issue description"
            )
            assert issue.id == "new_issue"
            assert issue.number == 100

    @respx.mock
    def test_update_issue(self):
        """Should update an existing issue."""
        respx.patch("https://api.usepylon.com/issues/issue_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": make_issue_data(
                        issue_id="issue_123", number=42, title="Updated Title"
                    )
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            issue = client.issues.update("issue_123", title="Updated Title")
            assert issue.id == "issue_123"
            assert issue.title == "Updated Title"

    @respx.mock
    def test_search_issues(self):
        """Should search issues with query."""
        respx.post("https://api.usepylon.com/issues/search").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        make_issue_data(issue_id="found_1", title="Bug report"),
                    ],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            issues = list(client.issues.search("bug"))
            assert len(issues) == 1
            assert issues[0].id == "found_1"

    @respx.mock
    def test_update_issue_state_to_closed(self):
        """Should update issue state to closed."""
        respx.patch("https://api.usepylon.com/issues/issue_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": make_issue_data(
                        issue_id="issue_123", number=42, state="closed"
                    )
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            issue = client.issues.update("issue_123", state="closed")
            assert issue.state == "closed"

    @respx.mock
    def test_update_issue_state_to_open(self):
        """Should update issue state to open."""
        respx.patch("https://api.usepylon.com/issues/issue_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": make_issue_data(
                        issue_id="issue_123", number=42, state="open"
                    )
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            issue = client.issues.update("issue_123", state="open")
            assert issue.state == "open"


class TestAsyncIssuesCRUD:
    """Integration tests for async issue CRUD operations."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_create_issue(self):
        """Should create issue asynchronously."""
        respx.post("https://api.usepylon.com/issues").mock(
            return_value=httpx.Response(
                201,
                json={"data": make_issue_data(issue_id="async_new", number=101)},
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            issue = await client.issues.create(
                title="Async Issue", description="Async description"
            )
            assert issue.id == "async_new"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_update_issue(self):
        """Should update issue asynchronously."""
        respx.patch("https://api.usepylon.com/issues/async_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": make_issue_data(issue_id="async_123", title="Async Updated")
                },
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            issue = await client.issues.update("async_123", title="Async Updated")
            assert issue.title == "Async Updated"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_search_issues(self):
        """Should search issues asynchronously."""
        respx.post("https://api.usepylon.com/issues/search").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [make_issue_data(issue_id="async_found")],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            issues = []
            async for issue in client.issues.search("query"):
                issues.append(issue)
            assert len(issues) == 1
