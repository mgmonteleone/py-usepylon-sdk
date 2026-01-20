"""Users resource for the Pylon SDK."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING

from pylon.models import PylonUser
from pylon.resources._base import BaseAsyncResource, BaseSyncResource
from pylon.resources._pagination import AsyncPaginator, SyncPaginator

if TYPE_CHECKING:
    from pylon._http import AsyncHTTPTransport, SyncHTTPTransport


class UsersResource(BaseSyncResource[PylonUser]):
    """Synchronous resource for managing Pylon users."""

    _endpoint = "/users"
    _model = PylonUser

    def __init__(self, transport: SyncHTTPTransport) -> None:
        super().__init__(transport)

    def list(self, *, limit: int = 100) -> Iterator[PylonUser]:
        """List all users."""
        paginator = SyncPaginator(
            transport=self._transport,
            endpoint=self._endpoint,
            model=self._model,
            params={"limit": limit},
            parser=PylonUser.from_pylon_dict,
        )
        yield from paginator.iter()

    def get(self, user_id: str) -> PylonUser:
        """Get a specific user by ID."""
        response = self._get(f"{self._endpoint}/{user_id}")
        data = response.get("data", response)
        return PylonUser.from_pylon_dict(data)


class AsyncUsersResource(BaseAsyncResource[PylonUser]):
    """Asynchronous resource for managing Pylon users."""

    _endpoint = "/users"
    _model = PylonUser

    def __init__(self, transport: AsyncHTTPTransport) -> None:
        super().__init__(transport)

    async def list(self, *, limit: int = 100) -> AsyncIterator[PylonUser]:
        """List all users asynchronously."""
        paginator = AsyncPaginator(
            transport=self._transport,
            endpoint=self._endpoint,
            model=self._model,
            params={"limit": limit},
            parser=PylonUser.from_pylon_dict,
        )
        async for user in paginator:
            yield user

    async def get(self, user_id: str) -> PylonUser:
        """Get a specific user by ID asynchronously."""
        response = await self._get(f"{self._endpoint}/{user_id}")
        data = response.get("data", response)
        return PylonUser.from_pylon_dict(data)

