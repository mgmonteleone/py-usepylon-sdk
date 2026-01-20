"""Issues resource for the Pylon SDK.

This module provides resource classes for interacting with the
Pylon Issues API endpoint.
"""

from __future__ import annotations

import builtins
from collections.abc import AsyncIterator, Iterator
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from pylon.models import PylonIssue, PylonMessage
from pylon.resources._base import BaseAsyncResource, BaseSyncResource
from pylon.resources._pagination import AsyncPaginator, SyncPaginator

if TYPE_CHECKING:
    from pylon._http import AsyncHTTPTransport, SyncHTTPTransport


class IssuesResource(BaseSyncResource[PylonIssue]):
    """Synchronous resource for managing Pylon issues.

    Provides methods for listing, retrieving, creating, and updating
    issues via the Pylon API.

    Example:
        client = PylonClient(api_key="...")

        # List recent issues
        for issue in client.issues.list(days=7):
            print(f"#{issue.number}: {issue.title}")

        # Get a specific issue
        issue = client.issues.get("issue_123")
    """

    _endpoint = "/issues"
    _model = PylonIssue

    def __init__(self, transport: SyncHTTPTransport) -> None:
        """Initialize the issues resource.

        Args:
            transport: The HTTP transport to use for requests.
        """
        super().__init__(transport)

    def list(
        self,
        *,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        days: int | None = None,
        limit: int = 100,
    ) -> Iterator[PylonIssue]:
        """List issues with optional time filtering.

        Args:
            start_time: Start of time range filter.
            end_time: End of time range filter.
            days: Number of days to look back (alternative to start_time).
            limit: Number of items per page.

        Yields:
            PylonIssue instances.
        """
        # Calculate time range
        if end_time is None:
            end_time = datetime.now(UTC)

        if start_time is None and days is not None:
            from datetime import timedelta

            start_time = end_time - timedelta(days=days)

        params: dict[str, Any] = {"limit": limit}
        if start_time:
            params["start_time"] = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        if end_time:
            params["end_time"] = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        paginator = SyncPaginator(
            transport=self._transport,
            endpoint=self._endpoint,
            model=self._model,
            params=params,
            parser=PylonIssue.from_pylon_dict,
        )
        yield from paginator.iter()

    def get(self, issue_id: str) -> PylonIssue:
        """Get a specific issue by ID.

        Args:
            issue_id: The issue ID or ticket number.

        Returns:
            The PylonIssue instance.
        """
        response = self._get(f"{self._endpoint}/{issue_id}")
        data = response.get("data", response)
        return PylonIssue.from_pylon_dict(data)

    def get_by_number(self, number: int) -> PylonIssue | None:
        """Get an issue by its ticket number.

        Args:
            number: The human-readable ticket number.

        Returns:
            The PylonIssue instance or None if not found.
        """
        from pylon.exceptions import PylonNotFoundError

        try:
            return self.get(str(number))
        except PylonNotFoundError:
            return None

    def update(self, issue_id: str, **kwargs: Any) -> PylonIssue:
        """Update an issue.

        Args:
            issue_id: The issue ID to update.
            **kwargs: Fields to update.

        Returns:
            The updated PylonIssue instance.
        """
        response = self._patch(f"{self._endpoint}/{issue_id}", data=kwargs)
        data = response.get("data", response)
        return PylonIssue.from_pylon_dict(data)

    def messages(
        self, issue_id: str, limit: int | None = None
    ) -> builtins.list[PylonMessage]:
        """Get messages for a specific issue.

        Args:
            issue_id: The issue ID.
            limit: Maximum number of messages to retrieve.

        Returns:
            List of PylonMessage instances.
        """
        params: dict[str, Any] = {}
        if limit:
            params["limit"] = limit

        response = self._get(f"{self._endpoint}/{issue_id}/messages", params=params)
        items = response.get("data", [])
        return [PylonMessage.from_pylon_dict(item) for item in items]


class AsyncIssuesResource(BaseAsyncResource[PylonIssue]):
    """Asynchronous resource for managing Pylon issues.

    Provides async methods for listing, retrieving, creating, and updating
    issues via the Pylon API.

    Example:
        async with AsyncPylonClient(api_key="...") as client:
            # List recent issues
            async for issue in client.issues.list(days=7):
                print(f"#{issue.number}: {issue.title}")

            # Get a specific issue
            issue = await client.issues.get("issue_123")
    """

    _endpoint = "/issues"
    _model = PylonIssue

    def __init__(self, transport: AsyncHTTPTransport) -> None:
        """Initialize the async issues resource.

        Args:
            transport: The async HTTP transport to use for requests.
        """
        super().__init__(transport)

    async def list(
        self,
        *,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        days: int | None = None,
        limit: int = 100,
    ) -> AsyncIterator[PylonIssue]:
        """List issues asynchronously with optional time filtering.

        Args:
            start_time: Start of time range filter.
            end_time: End of time range filter.
            days: Number of days to look back (alternative to start_time).
            limit: Number of items per page.

        Yields:
            PylonIssue instances.
        """
        # Calculate time range
        if end_time is None:
            end_time = datetime.now(UTC)

        if start_time is None and days is not None:
            from datetime import timedelta

            start_time = end_time - timedelta(days=days)

        params: dict[str, Any] = {"limit": limit}
        if start_time:
            params["start_time"] = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        if end_time:
            params["end_time"] = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        paginator = AsyncPaginator(
            transport=self._transport,
            endpoint=self._endpoint,
            model=self._model,
            params=params,
            parser=PylonIssue.from_pylon_dict,
        )
        async for issue in paginator:
            yield issue

    async def get(self, issue_id: str) -> PylonIssue:
        """Get a specific issue by ID asynchronously.

        Args:
            issue_id: The issue ID or ticket number.

        Returns:
            The PylonIssue instance.
        """
        response = await self._get(f"{self._endpoint}/{issue_id}")
        data = response.get("data", response)
        return PylonIssue.from_pylon_dict(data)

    async def get_by_number(self, number: int) -> PylonIssue | None:
        """Get an issue by its ticket number asynchronously.

        Args:
            number: The human-readable ticket number.

        Returns:
            The PylonIssue instance or None if not found.
        """
        from pylon.exceptions import PylonNotFoundError

        try:
            return await self.get(str(number))
        except PylonNotFoundError:
            return None

    async def update(self, issue_id: str, **kwargs: Any) -> PylonIssue:
        """Update an issue asynchronously.

        Args:
            issue_id: The issue ID to update.
            **kwargs: Fields to update.

        Returns:
            The updated PylonIssue instance.
        """
        response = await self._patch(f"{self._endpoint}/{issue_id}", data=kwargs)
        data = response.get("data", response)
        return PylonIssue.from_pylon_dict(data)

    async def messages(
        self, issue_id: str, limit: int | None = None
    ) -> builtins.list[PylonMessage]:
        """Get messages for a specific issue asynchronously.

        Args:
            issue_id: The issue ID.
            limit: Maximum number of messages to retrieve.

        Returns:
            List of PylonMessage instances.
        """
        params: dict[str, Any] = {}
        if limit:
            params["limit"] = limit

        response = await self._get(
            f"{self._endpoint}/{issue_id}/messages", params=params
        )
        items = response.get("data", [])
        return [PylonMessage.from_pylon_dict(item) for item in items]

