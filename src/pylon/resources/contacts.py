"""Contacts resource for the Pylon SDK."""

from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import TYPE_CHECKING

from pylon.models import PylonContact
from pylon.resources._base import BaseAsyncResource, BaseSyncResource
from pylon.resources._pagination import AsyncPaginator, SyncPaginator

if TYPE_CHECKING:
    from pylon._http import AsyncHTTPTransport, SyncHTTPTransport


class ContactsResource(BaseSyncResource[PylonContact]):
    """Synchronous resource for managing Pylon contacts."""

    _endpoint = "/contacts"
    _model = PylonContact

    def __init__(self, transport: SyncHTTPTransport) -> None:
        super().__init__(transport)

    def list(self, *, limit: int = 100) -> Iterator[PylonContact]:
        """List all contacts."""
        paginator = SyncPaginator(
            transport=self._transport,
            endpoint=self._endpoint,
            model=self._model,
            params={"limit": limit},
            parser=PylonContact.from_pylon_dict,
        )
        yield from paginator.iter()

    def get(self, contact_id: str) -> PylonContact:
        """Get a specific contact by ID."""
        response = self._get(f"{self._endpoint}/{contact_id}")
        data = response.get("data", response)
        return PylonContact.from_pylon_dict(data)


class AsyncContactsResource(BaseAsyncResource[PylonContact]):
    """Asynchronous resource for managing Pylon contacts."""

    _endpoint = "/contacts"
    _model = PylonContact

    def __init__(self, transport: AsyncHTTPTransport) -> None:
        super().__init__(transport)

    async def list(self, *, limit: int = 100) -> AsyncIterator[PylonContact]:
        """List all contacts asynchronously."""
        paginator = AsyncPaginator(
            transport=self._transport,
            endpoint=self._endpoint,
            model=self._model,
            params={"limit": limit},
            parser=PylonContact.from_pylon_dict,
        )
        async for contact in paginator:
            yield contact

    async def get(self, contact_id: str) -> PylonContact:
        """Get a specific contact by ID asynchronously."""
        response = await self._get(f"{self._endpoint}/{contact_id}")
        data = response.get("data", response)
        return PylonContact.from_pylon_dict(data)

