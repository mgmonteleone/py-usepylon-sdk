"""Teams resource for the Pylon SDK."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING

from pylon.models import PylonTeam
from pylon.resources._base import BaseAsyncResource, BaseSyncResource
from pylon.resources._pagination import AsyncPaginator, SyncPaginator

if TYPE_CHECKING:
    from pylon._http import AsyncHTTPTransport, SyncHTTPTransport


class TeamsResource(BaseSyncResource[PylonTeam]):
    """Synchronous resource for managing Pylon teams."""

    _endpoint = "/teams"
    _model = PylonTeam

    def __init__(self, transport: SyncHTTPTransport) -> None:
        super().__init__(transport)

    def list(self, *, limit: int = 100) -> Iterator[PylonTeam]:
        """List all teams."""
        paginator = SyncPaginator(
            transport=self._transport,
            endpoint=self._endpoint,
            model=self._model,
            params={"limit": limit},
            parser=PylonTeam.from_pylon_dict,
        )
        yield from paginator.iter()


class AsyncTeamsResource(BaseAsyncResource[PylonTeam]):
    """Asynchronous resource for managing Pylon teams."""

    _endpoint = "/teams"
    _model = PylonTeam

    def __init__(self, transport: AsyncHTTPTransport) -> None:
        super().__init__(transport)

    async def list(self, *, limit: int = 100) -> AsyncIterator[PylonTeam]:
        """List all teams asynchronously."""
        paginator = AsyncPaginator(
            transport=self._transport,
            endpoint=self._endpoint,
            model=self._model,
            params={"limit": limit},
            parser=PylonTeam.from_pylon_dict,
        )
        async for team in paginator:
            yield team

