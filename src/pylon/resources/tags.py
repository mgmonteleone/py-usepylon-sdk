"""Tags resource for the Pylon SDK."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING

from pylon.models import PylonTag
from pylon.resources._base import BaseAsyncResource, BaseSyncResource
from pylon.resources._pagination import AsyncPaginator, SyncPaginator

if TYPE_CHECKING:
    from pylon._http import AsyncHTTPTransport, SyncHTTPTransport


class TagsResource(BaseSyncResource[PylonTag]):
    """Synchronous resource for managing Pylon tags."""

    _endpoint = "/tags"
    _model = PylonTag

    def __init__(self, transport: SyncHTTPTransport) -> None:
        super().__init__(transport)

    def list(self, *, limit: int = 100) -> Iterator[PylonTag]:
        """List all tags."""
        paginator = SyncPaginator(
            transport=self._transport,
            endpoint=self._endpoint,
            model=self._model,
            params={"limit": limit},
            parser=PylonTag.from_pylon_dict,
        )
        yield from paginator.iter()


class AsyncTagsResource(BaseAsyncResource[PylonTag]):
    """Asynchronous resource for managing Pylon tags."""

    _endpoint = "/tags"
    _model = PylonTag

    def __init__(self, transport: AsyncHTTPTransport) -> None:
        super().__init__(transport)

    async def list(self, *, limit: int = 100) -> AsyncIterator[PylonTag]:
        """List all tags asynchronously."""
        paginator = AsyncPaginator(
            transport=self._transport,
            endpoint=self._endpoint,
            model=self._model,
            params={"limit": limit},
            parser=PylonTag.from_pylon_dict,
        )
        async for tag in paginator:
            yield tag

