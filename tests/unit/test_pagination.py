"""Unit tests for pagination utilities."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from pylon.models import PylonIssue
from pylon.resources._pagination import AsyncPaginator, SyncPaginator
from tests.conftest import make_issue_data


class TestSyncPaginator:
    """Tests for SyncPaginator."""

    def test_iterates_single_page(self):
        """Should iterate through single page of results."""
        transport = MagicMock()
        transport.request.return_value = {
            "data": [
                make_issue_data(issue_id="issue_1", number=1),
                make_issue_data(issue_id="issue_2", number=2),
            ],
            "pagination": {"cursor": None, "has_next_page": False},
        }

        paginator = SyncPaginator(
            transport=transport,
            endpoint="/issues",
            model=PylonIssue,
            params={},
        )

        # Use .iter() method for sync paginator
        items = list(paginator.iter())
        assert len(items) == 2
        assert items[0].id == "issue_1"
        assert items[1].id == "issue_2"

    def test_iterates_multiple_pages(self):
        """Should iterate through multiple pages."""
        transport = MagicMock()
        transport.request.side_effect = [
            {
                "data": [make_issue_data(issue_id="issue_1", number=1)],
                "pagination": {"cursor": "cursor_1", "has_next_page": True},
            },
            {
                "data": [make_issue_data(issue_id="issue_2", number=2)],
                "pagination": {"cursor": "cursor_2", "has_next_page": True},
            },
            {
                "data": [make_issue_data(issue_id="issue_3", number=3)],
                "pagination": {"cursor": None, "has_next_page": False},
            },
        ]

        paginator = SyncPaginator(
            transport=transport,
            endpoint="/issues",
            model=PylonIssue,
            params={},
        )

        # Use .iter() method for sync paginator
        items = list(paginator.iter())
        assert len(items) == 3
        assert items[0].id == "issue_1"
        assert items[1].id == "issue_2"
        assert items[2].id == "issue_3"

    def test_collect_returns_all_items(self):
        """Should collect all items into a list."""
        transport = MagicMock()
        transport.request.return_value = {
            "data": [
                make_issue_data(issue_id="issue_1", number=1),
                make_issue_data(issue_id="issue_2", number=2),
            ],
            "pagination": {"cursor": None, "has_next_page": False},
        }

        paginator = SyncPaginator(
            transport=transport,
            endpoint="/issues",
            model=PylonIssue,
            params={},
        )

        items = paginator.collect()
        assert isinstance(items, list)
        assert len(items) == 2

    def test_respects_limit_param(self):
        """Should pass limit parameter to API."""
        transport = MagicMock()
        transport.request.return_value = {
            "data": [],
            "pagination": {"cursor": None, "has_next_page": False},
        }

        paginator = SyncPaginator(
            transport=transport,
            endpoint="/issues",
            model=PylonIssue,
            params={"limit": 50},
        )

        # Use .iter() method
        list(paginator.iter())
        transport.request.assert_called_once()
        call_args = transport.request.call_args
        assert call_args[1]["params"]["limit"] == 50


class TestAsyncPaginator:
    """Tests for AsyncPaginator."""

    @pytest.mark.asyncio
    async def test_iterates_single_page(self):
        """Should iterate through single page asynchronously."""
        # Create async mock for arequest method
        async_response = {
            "data": [
                make_issue_data(issue_id="async_1", number=1),
                make_issue_data(issue_id="async_2", number=2),
            ],
            "pagination": {"cursor": None, "has_next_page": False},
        }

        transport = MagicMock()
        transport.arequest = AsyncMock(return_value=async_response)

        paginator = AsyncPaginator(
            transport=transport,
            endpoint="/issues",
            model=PylonIssue,
            params={},
        )

        items = []
        async for item in paginator:
            items.append(item)

        assert len(items) == 2
        assert items[0].id == "async_1"
        assert items[1].id == "async_2"

    @pytest.mark.asyncio
    async def test_collect_returns_all_items(self):
        """Should collect all items asynchronously."""
        async_response = {
            "data": [
                make_issue_data(issue_id="async_1", number=1),
            ],
            "pagination": {"cursor": None, "has_next_page": False},
        }

        transport = MagicMock()
        transport.arequest = AsyncMock(return_value=async_response)

        paginator = AsyncPaginator(
            transport=transport,
            endpoint="/issues",
            model=PylonIssue,
            params={},
        )

        items = await paginator.collect()
        assert isinstance(items, list)
        assert len(items) == 1
