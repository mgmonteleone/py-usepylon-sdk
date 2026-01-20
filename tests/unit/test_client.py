"""Unit tests for Pylon client implementations."""

import os
from unittest.mock import patch

import httpx
import pytest
import respx

from pylon import AsyncPylonClient, PylonClient
from pylon.models import PylonIssue
from tests.conftest import make_issue_data


class TestPylonClient:
    """Tests for synchronous PylonClient."""

    def test_requires_api_key(self):
        """Should raise ValueError if no API key provided."""
        with patch.dict(os.environ, {}, clear=True):
            # Ensure PYLON_API_KEY is not set
            os.environ.pop("PYLON_API_KEY", None)
            with pytest.raises(ValueError, match="API key must be provided"):
                PylonClient()

    def test_uses_env_var_for_api_key(self):
        """Should use PYLON_API_KEY environment variable."""
        with patch.dict(os.environ, {"PYLON_API_KEY": "test-api-key"}):
            client = PylonClient()
            assert client._transport.api_key == "test-api-key"
            client.close()

    def test_explicit_api_key_overrides_env(self):
        """Should use explicit API key over environment variable."""
        with patch.dict(os.environ, {"PYLON_API_KEY": "env-key"}):
            client = PylonClient(api_key="explicit-key")
            assert client._transport.api_key == "explicit-key"
            client.close()

    def test_context_manager(self):
        """Should work as context manager."""
        with PylonClient(api_key="test-key") as client:
            assert client._transport._client is not None
        # Transport should be closed after exiting context

    def test_has_resource_accessors(self):
        """Should have accessors for all resources."""
        with PylonClient(api_key="test-key") as client:
            assert hasattr(client, "issues")
            assert hasattr(client, "accounts")
            assert hasattr(client, "contacts")
            assert hasattr(client, "users")
            assert hasattr(client, "teams")
            assert hasattr(client, "tags")

    @respx.mock
    def test_issues_get(self):
        """Should get an issue by ID."""
        respx.get("https://api.usepylon.com/issues/issue_123").mock(
            return_value=httpx.Response(200, json={"data": make_issue_data()})
        )

        with PylonClient(api_key="test-key") as client:
            issue = client.issues.get("issue_123")
            assert isinstance(issue, PylonIssue)
            assert issue.id == "issue_123"
            assert issue.number == 42
            assert issue.title == "Test Issue"

    @respx.mock
    def test_issues_get_by_number(self):
        """Should get an issue by number (passes number as string ID)."""
        # Note: get_by_number converts the number to a string and calls get()
        respx.get("https://api.usepylon.com/issues/100").mock(
            return_value=httpx.Response(
                200, json={"data": make_issue_data(issue_id="issue_456", number=100)}
            )
        )

        with PylonClient(api_key="test-key") as client:
            issue = client.issues.get_by_number(100)
            assert isinstance(issue, PylonIssue)
            assert issue.number == 100

    @respx.mock
    def test_issues_list_single_page(self):
        """Should iterate through single page of results."""
        response_data = {
            "data": [
                make_issue_data(issue_id="issue_1", number=1, title="Issue 1"),
                make_issue_data(issue_id="issue_2", number=2, title="Issue 2"),
            ],
            "pagination": {"cursor": None, "has_more": False},
        }

        respx.get("https://api.usepylon.com/issues").mock(
            return_value=httpx.Response(200, json=response_data)
        )

        with PylonClient(api_key="test-key") as client:
            issues = list(client.issues.list())
            assert len(issues) == 2
            assert issues[0].id == "issue_1"
            assert issues[1].id == "issue_2"


class TestAsyncPylonClient:
    """Tests for asynchronous AsyncPylonClient."""

    def test_requires_api_key(self):
        """Should raise ValueError if no API key provided."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("PYLON_API_KEY", None)
            with pytest.raises(ValueError, match="API key must be provided"):
                AsyncPylonClient()

    def test_uses_env_var_for_api_key(self):
        """Should use PYLON_API_KEY environment variable."""
        with patch.dict(os.environ, {"PYLON_API_KEY": "test-api-key"}):
            client = AsyncPylonClient()
            assert client._transport.api_key == "test-api-key"

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Should work as async context manager."""
        async with AsyncPylonClient(api_key="test-key") as client:
            assert client._transport._client is not None

    @pytest.mark.asyncio
    @respx.mock
    async def test_issues_get(self):
        """Should get an issue by ID asynchronously."""
        respx.get("https://api.usepylon.com/issues/issue_async_123").mock(
            return_value=httpx.Response(
                200,
                json={"data": make_issue_data(issue_id="issue_async_123", number=99)},
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            issue = await client.issues.get("issue_async_123")
            assert isinstance(issue, PylonIssue)
            assert issue.id == "issue_async_123"
            assert issue.number == 99

    @pytest.mark.asyncio
    @respx.mock
    async def test_issues_list_single_page(self):
        """Should iterate through single page of results asynchronously."""
        response_data = {
            "data": [
                make_issue_data(issue_id="async_issue_1", number=1, title="Async 1"),
                make_issue_data(issue_id="async_issue_2", number=2, title="Async 2"),
            ],
            "pagination": {"cursor": None, "has_more": False},
        }

        respx.get("https://api.usepylon.com/issues").mock(
            return_value=httpx.Response(200, json=response_data)
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            issues = []
            async for issue in client.issues.list():
                issues.append(issue)
            assert len(issues) == 2
            assert issues[0].id == "async_issue_1"
            assert issues[1].id == "async_issue_2"
