"""Pylon API Client implementations.

This module provides the main client classes for interacting with
the Pylon API using both synchronous and asynchronous patterns.
"""

from __future__ import annotations

import os
from typing import Any

from pylon._http import (
    DEFAULT_BASE_URL,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    AsyncHTTPTransport,
    SyncHTTPTransport,
)
from pylon.resources.accounts import AccountsResource, AsyncAccountsResource
from pylon.resources.attachments import (
    AsyncAttachmentsResource,
    AttachmentsResource,
)
from pylon.resources.contacts import AsyncContactsResource, ContactsResource
from pylon.resources.issues import AsyncIssuesResource, IssuesResource
from pylon.resources.knowledge_base import (
    AsyncKnowledgeBaseResource,
    KnowledgeBaseResource,
)
from pylon.resources.messages import AsyncMessagesResource, MessagesResource
from pylon.resources.tags import AsyncTagsResource, TagsResource
from pylon.resources.teams import AsyncTeamsResource, TeamsResource
from pylon.resources.users import AsyncUsersResource, UsersResource


class PylonClient:
    """Synchronous client for the Pylon API.

    Provides a resource-based interface for interacting with the Pylon
    customer support API. Uses httpx for HTTP requests with connection
    pooling and automatic retries.

    Example:
        # Basic usage
        client = PylonClient(api_key="...")

        # List recent issues
        for issue in client.issues.list(days=7):
            print(f"#{issue.number}: {issue.title}")

        # Get a specific issue
        issue = client.issues.get("issue_123")

        # Context manager usage (recommended)
        with PylonClient(api_key="...") as client:
            for account in client.accounts.list():
                print(account.name)

    Attributes:
        issues: Resource for managing issues.
        accounts: Resource for managing accounts.
        contacts: Resource for managing contacts.
        users: Resource for managing users.
        teams: Resource for managing teams.
        tags: Resource for managing tags.
        messages: Resource for managing issue messages.
        attachments: Resource for managing attachments.
        knowledge_bases: Resource for managing knowledge bases.
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        """Initialize the Pylon client.

        Args:
            api_key: Pylon API key. If not provided, uses PYLON_API_KEY env var.
            base_url: Base URL for the Pylon API.
            timeout: Timeout in seconds for HTTP requests.
            max_retries: Maximum number of retry attempts for failed requests.

        Raises:
            ValueError: If no API key is provided or found in environment.
        """
        resolved_api_key = api_key or os.getenv("PYLON_API_KEY")
        if not resolved_api_key:
            raise ValueError(
                "Pylon API key must be provided or set in PYLON_API_KEY environment "
                "variable."
            )

        self._transport = SyncHTTPTransport(
            api_key=resolved_api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Initialize resources
        self._issues = IssuesResource(self._transport)
        self._accounts = AccountsResource(self._transport)
        self._contacts = ContactsResource(self._transport)
        self._users = UsersResource(self._transport)
        self._teams = TeamsResource(self._transport)
        self._tags = TagsResource(self._transport)
        self._messages = MessagesResource(self._transport)
        self._attachments = AttachmentsResource(self._transport)
        self._knowledge_bases = KnowledgeBaseResource(self._transport)

    @property
    def issues(self) -> IssuesResource:
        """Access the issues resource."""
        return self._issues

    @property
    def accounts(self) -> AccountsResource:
        """Access the accounts resource."""
        return self._accounts

    @property
    def contacts(self) -> ContactsResource:
        """Access the contacts resource."""
        return self._contacts

    @property
    def users(self) -> UsersResource:
        """Access the users resource."""
        return self._users

    @property
    def teams(self) -> TeamsResource:
        """Access the teams resource."""
        return self._teams

    @property
    def tags(self) -> TagsResource:
        """Access the tags resource."""
        return self._tags

    @property
    def messages(self) -> MessagesResource:
        """Access the messages resource."""
        return self._messages

    @property
    def attachments(self) -> AttachmentsResource:
        """Access the attachments resource."""
        return self._attachments

    @property
    def knowledge_bases(self) -> KnowledgeBaseResource:
        """Access the knowledge bases resource."""
        return self._knowledge_bases

    def close(self) -> None:
        """Close the client and release resources."""
        self._transport.close()

    def __enter__(self) -> PylonClient:
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Context manager exit."""
        self.close()


class AsyncPylonClient:
    """Asynchronous client for the Pylon API.

    Provides a resource-based interface for interacting with the Pylon
    customer support API using async/await. Uses httpx.AsyncClient for
    efficient asynchronous HTTP requests.

    Example:
        # Basic usage with async context manager
        async with AsyncPylonClient(api_key="...") as client:
            # List recent issues
            async for issue in client.issues.list(days=7):
                print(f"#{issue.number}: {issue.title}")

            # Get a specific issue
            issue = await client.issues.get("issue_123")

    Attributes:
        issues: Async resource for managing issues.
        accounts: Async resource for managing accounts.
        contacts: Async resource for managing contacts.
        users: Async resource for managing users.
        teams: Async resource for managing teams.
        tags: Async resource for managing tags.
        messages: Async resource for managing issue messages.
        attachments: Async resource for managing attachments.
        knowledge_bases: Async resource for managing knowledge bases.
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        """Initialize the async Pylon client.

        Args:
            api_key: Pylon API key. If not provided, uses PYLON_API_KEY env var.
            base_url: Base URL for the Pylon API.
            timeout: Timeout in seconds for HTTP requests.
            max_retries: Maximum number of retry attempts for failed requests.

        Raises:
            ValueError: If no API key is provided or found in environment.
        """
        resolved_api_key = api_key or os.getenv("PYLON_API_KEY")
        if not resolved_api_key:
            raise ValueError(
                "Pylon API key must be provided or set in PYLON_API_KEY environment "
                "variable."
            )

        self._transport = AsyncHTTPTransport(
            api_key=resolved_api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
        )

        # Initialize async resources
        self._issues = AsyncIssuesResource(self._transport)
        self._accounts = AsyncAccountsResource(self._transport)
        self._contacts = AsyncContactsResource(self._transport)
        self._users = AsyncUsersResource(self._transport)
        self._teams = AsyncTeamsResource(self._transport)
        self._tags = AsyncTagsResource(self._transport)
        self._messages = AsyncMessagesResource(self._transport)
        self._attachments = AsyncAttachmentsResource(self._transport)
        self._knowledge_bases = AsyncKnowledgeBaseResource(self._transport)

    @property
    def issues(self) -> AsyncIssuesResource:
        """Access the async issues resource."""
        return self._issues

    @property
    def accounts(self) -> AsyncAccountsResource:
        """Access the async accounts resource."""
        return self._accounts

    @property
    def contacts(self) -> AsyncContactsResource:
        """Access the async contacts resource."""
        return self._contacts

    @property
    def users(self) -> AsyncUsersResource:
        """Access the async users resource."""
        return self._users

    @property
    def teams(self) -> AsyncTeamsResource:
        """Access the async teams resource."""
        return self._teams

    @property
    def tags(self) -> AsyncTagsResource:
        """Access the async tags resource."""
        return self._tags

    @property
    def messages(self) -> AsyncMessagesResource:
        """Access the async messages resource."""
        return self._messages

    @property
    def attachments(self) -> AsyncAttachmentsResource:
        """Access the async attachments resource."""
        return self._attachments

    @property
    def knowledge_bases(self) -> AsyncKnowledgeBaseResource:
        """Access the async knowledge bases resource."""
        return self._knowledge_bases

    async def aclose(self) -> None:
        """Close the async client and release resources."""
        await self._transport.aclose()

    async def __aenter__(self) -> AsyncPylonClient:
        """Async context manager entry."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> None:
        """Async context manager exit."""
        await self.aclose()

