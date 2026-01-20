"""Integration tests for accounts resource with mocked API."""

from typing import Any

import httpx
import pytest
import respx

from pylon import AsyncPylonClient, PylonClient


def make_account_data(
    account_id: str = "acc_123",
    name: str = "Test Account",
    **overrides: Any,
) -> dict[str, Any]:
    """Create valid account data for tests."""
    base_data = {
        "id": account_id,
        "name": name,
        "type": "customer",
        "created_at": "2024-01-15T10:00:00Z",
        "channels": [],
        "custom_fields": {},
    }
    base_data.update(overrides)
    return base_data


class TestAccountsIntegration:
    """Integration tests for accounts resource."""

    @respx.mock
    def test_list_accounts(self):
        """Should list accounts with pagination."""
        respx.get("https://api.usepylon.com/accounts").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        make_account_data(account_id="acc_1", name="Acme Corp"),
                        make_account_data(account_id="acc_2", name="TechCorp"),
                    ],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            accounts = list(client.accounts.list())
            assert len(accounts) == 2
            assert accounts[0].name == "Acme Corp"
            assert accounts[1].name == "TechCorp"

    @respx.mock
    def test_get_account_by_id(self):
        """Should retrieve a single account by ID."""
        respx.get("https://api.usepylon.com/accounts/acc_456").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": make_account_data(
                        account_id="acc_456",
                        name="Enterprise Customer",
                        type="enterprise",
                    )
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            account = client.accounts.get("acc_456")
            assert account.id == "acc_456"
            assert account.name == "Enterprise Customer"
            assert account.type == "enterprise"

    @respx.mock
    def test_list_accounts_pagination(self):
        """Should paginate through multiple pages of accounts."""
        # Use side_effect to return different responses for each call
        call_count = 0

        def pagination_handler(_request):  # noqa: ARG001
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # Page 1
                return httpx.Response(
                    200,
                    json={
                        "data": [make_account_data(account_id="acc_1")],
                        "pagination": {"cursor": "page2", "has_next_page": True},
                    },
                )
            else:
                # Page 2
                return httpx.Response(
                    200,
                    json={
                        "data": [make_account_data(account_id="acc_2")],
                        "pagination": {"cursor": None, "has_next_page": False},
                    },
                )

        respx.get("https://api.usepylon.com/accounts").mock(
            side_effect=pagination_handler
        )

        with PylonClient(api_key="test-key") as client:
            accounts = list(client.accounts.list())
            assert len(accounts) == 2


class TestAsyncAccountsIntegration:
    """Integration tests for async accounts resource."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_list_accounts(self):
        """Should list accounts asynchronously."""
        respx.get("https://api.usepylon.com/accounts").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        make_account_data(account_id="async_acc_1", name="Async Corp"),
                    ],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            accounts = []
            async for account in client.accounts.list():
                accounts.append(account)
            assert len(accounts) == 1
            assert accounts[0].name == "Async Corp"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_get_account(self):
        """Should get single account asynchronously."""
        respx.get("https://api.usepylon.com/accounts/async_acc_123").mock(
            return_value=httpx.Response(
                200,
                json={"data": make_account_data(account_id="async_acc_123")},
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            account = await client.accounts.get("async_acc_123")
            assert account.id == "async_acc_123"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_list_multiple_accounts(self):
        """Should list multiple accounts asynchronously."""
        respx.get("https://api.usepylon.com/accounts").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [
                        make_account_data(account_id=f"acc_{i}") for i in range(3)
                    ],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            accounts = []
            async for account in client.accounts.list():
                accounts.append(account)
            assert len(accounts) == 3


class TestAccountsCRUDOperations:
    """Integration tests for account CRUD operations."""

    @respx.mock
    def test_create_account(self):
        """Should create a new account."""
        respx.post("https://api.usepylon.com/accounts").mock(
            return_value=httpx.Response(
                201,
                json={
                    "data": make_account_data(account_id="new_acc", name="New Account")
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            account = client.accounts.create(name="New Account")
            assert account.id == "new_acc"
            assert account.name == "New Account"

    @respx.mock
    def test_update_account(self):
        """Should update an existing account."""
        respx.patch("https://api.usepylon.com/accounts/acc_123").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": make_account_data(
                        account_id="acc_123", name="Updated Account"
                    )
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            account = client.accounts.update("acc_123", name="Updated Account")
            assert account.id == "acc_123"
            assert account.name == "Updated Account"

    @respx.mock
    def test_search_accounts(self):
        """Should search accounts by custom field."""
        respx.post("https://api.usepylon.com/accounts/search").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [make_account_data(account_id="found_acc")],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        with PylonClient(api_key="test-key") as client:
            accounts = list(client.accounts.search("domain", "example.com"))
            assert len(accounts) == 1
            assert accounts[0].id == "found_acc"


class TestAsyncAccountsCRUD:
    """Integration tests for async account CRUD operations."""

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_create_account(self):
        """Should create account asynchronously."""
        respx.post("https://api.usepylon.com/accounts").mock(
            return_value=httpx.Response(
                201,
                json={"data": make_account_data(account_id="async_new_acc")},
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            account = await client.accounts.create(name="Async Account")
            assert account.id == "async_new_acc"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_update_account(self):
        """Should update account asynchronously."""
        respx.patch("https://api.usepylon.com/accounts/async_acc").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": make_account_data(
                        account_id="async_acc", name="Async Updated"
                    )
                },
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            account = await client.accounts.update("async_acc", name="Async Updated")
            assert account.name == "Async Updated"

    @pytest.mark.asyncio
    @respx.mock
    async def test_async_search_accounts(self):
        """Should search accounts asynchronously."""
        respx.post("https://api.usepylon.com/accounts/search").mock(
            return_value=httpx.Response(
                200,
                json={
                    "data": [make_account_data(account_id="async_found")],
                    "pagination": {"cursor": None, "has_next_page": False},
                },
            )
        )

        async with AsyncPylonClient(api_key="test-key") as client:
            accounts = []
            async for account in client.accounts.search("type", "enterprise"):
                accounts.append(account)
            assert len(accounts) == 1
