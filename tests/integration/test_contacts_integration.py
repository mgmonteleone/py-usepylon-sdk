"""Integration tests for contacts resource with mocked API."""

from typing import Any

import httpx
import pytest
import respx

from pylon import AsyncPylonClient, PylonClient


def make_contact_data(
    contact_id: str = "contact_123",
    name: str = "John Doe",
    email: str = "john@example.com",
    **overrides: Any,
) -> dict[str, Any]:
    """Create valid contact data for tests."""
    base_data = {
        "id": contact_id,
        "name": name,
        "email": email,
        "emails": [email],
        "custom_fields": {},
    }
    base_data.update(overrides)
    return base_data


class TestContactsIntegration:
    """Integration tests for contacts resource."""

    @respx.mock
    def test_list_contacts(self):
        """Should list contacts with pagination."""
        respx.get("https://api.usepylon.com/contacts").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        make_contact_data(
                            contact_id="contact_1",
                            name="Alice",
                            email="alice@example.com",
                        ),
                        make_contact_data(
                            contact_id="contact_2",
                            name="Bob",
                            email="bob@example.com",
                        ),
                    ],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            contacts = list(client.contacts.list())
            assert len(contacts) == 2
            assert contacts[0].name == "Alice"
            assert contacts[1].email == "bob@example.com"

    @respx.mock
    def test_get_contact_by_id(self):
        """Should retrieve a single contact by ID."""
        respx.get("https://api.usepylon.com/contacts/contact_456").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": make_contact_data(
                        contact_id="contact_456",
                        name="Charlie",
                        email="charlie@example.com",
                    )
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            contact = client.contacts.get("contact_456")
            assert contact.id == "contact_456"
            assert contact.name == "Charlie"

    @respx.mock
    def test_search_contacts(self):
        """Should search contacts by query."""
        respx.post(
            "https://api.usepylon.com/contacts/search",
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        make_contact_data(
                            contact_id="contact_found",
                            name="Found User",
                            email="search@example.com",
                        ),
                    ],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            contacts = list(client.contacts.search("search@example.com"))
            assert len(contacts) == 1
            assert contacts[0].email == "search@example.com"

    @respx.mock
    def test_list_contacts_pagination(self):
        """Should paginate through multiple pages of contacts."""
        call_count = 0

        def pagination_handler(_request):  # noqa: ARG001
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return httpx.Response(
                    200,
                    json={
                        "data": [make_contact_data(contact_id="contact_1")],
                        "pagination": {"cursor": "page2", "has_next_page": True},
                    },
                )
            else:
                return httpx.Response(
                    200,
                    json={
                        "data": [make_contact_data(contact_id="contact_2")],
                        "pagination": {"cursor": None, "has_next_page": False},
                    },
                )

        respx.get("https://api.usepylon.com/contacts").mock(
            side_effect=pagination_handler
        )

        with PylonClient(api_key="test-key") as client:
            contacts = list(client.contacts.list())
            assert len(contacts) == 2


class TestAsyncContactsIntegration:
    """Integration tests for async contacts resource."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_list_contacts(self):
        """Should list contacts asynchronously."""
        respx.get("https://api.usepylon.com/contacts").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        make_contact_data(contact_id="async_contact_1"),
                    ],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            contacts = []
            async for contact in client.contacts.list():
                contacts.append(contact)
            assert len(contacts) == 1

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_contact(self):
        """Should get single contact asynchronously."""
        respx.get("https://api.usepylon.com/contacts/async_contact").mock(
            return_value=httpx.Response(
                200,
                json={"data": make_contact_data(contact_id="async_contact")},
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            contact = await client.contacts.get("async_contact")
            assert contact.id == "async_contact"


class TestContactsCRUDOperations:
    """Integration tests for contact CRUD operations."""

    @respx.mock
    def test_create_contact(self):
        """Should create a new contact."""
        respx.post("https://api.usepylon.com/contacts").mock(
            return_value=httpx.Response(
                201,
                json={
                    "data": make_contact_data(
                        contact_id="new_contact",
                        name="Jane Doe",
                        email="jane@example.com",
                    )
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            contact = client.contacts.create(name="Jane Doe", email="jane@example.com")
            assert contact.id == "new_contact"
            assert contact.name == "Jane Doe"

    @respx.mock
    def test_update_contact(self):
        """Should update an existing contact."""
        respx.patch("https://api.usepylon.com/contacts/contact_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": make_contact_data(
                        contact_id="contact_123", name="Updated Name"
                    )
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            contact = client.contacts.update("contact_123", name="Updated Name")
            assert contact.id == "contact_123"
            assert contact.name == "Updated Name"

    @respx.mock
    def test_search_contacts(self):
        """Should search contacts by query."""
        respx.post("https://api.usepylon.com/contacts/search").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [make_contact_data(contact_id="found_contact")],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            contacts = list(client.contacts.search("john"))
            assert len(contacts) == 1
            assert contacts[0].id == "found_contact"


class TestAsyncContactsCRUD:
    """Integration tests for async contact CRUD operations."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_create_contact(self):
        """Should create contact asynchronously."""
        respx.post("https://api.usepylon.com/contacts").mock(
            return_value=httpx.Response(
                201,
                json={"data": make_contact_data(contact_id="async_new_contact")},
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            contact = await client.contacts.create(name="Async User", email="a@b.com")
            assert contact.id == "async_new_contact"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_update_contact(self):
        """Should update contact asynchronously."""
        respx.patch("https://api.usepylon.com/contacts/async_contact").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": make_contact_data(
                        contact_id="async_contact", name="Async Updated"
                    )
                },
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            contact = await client.contacts.update(
                "async_contact", name="Async Updated"
            )
            assert contact.name == "Async Updated"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_search_contacts(self):
        """Should search contacts asynchronously."""
        respx.post("https://api.usepylon.com/contacts/search").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [make_contact_data(contact_id="async_found")],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            contacts = []
            async for contact in client.contacts.search("query"):
                contacts.append(contact)
            assert len(contacts) == 1
