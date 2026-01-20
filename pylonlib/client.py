"""
Pylon API Client

This module provides a client for interacting with the Pylon API.
"""

import os
import time
from collections.abc import Iterator
from datetime import datetime, timedelta
from typing import Any

import requests
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .models import (
    PylonAccount,
    PylonAttachment,
    PylonContact,
    PylonIssue,
    PylonMessage,
    PylonResponse,
    PylonTag,
    PylonTeam,
    PylonUser,
)


class PylonAPIError(Exception):
    """Exception raised for Pylon API errors."""

    pass


class PylonRateLimitError(PylonAPIError):
    """Exception raised when rate limit is exceeded."""

    pass


class PylonClient:
    """
    Client for interacting with the Pylon API.

    This client provides methods to retrieve data from Pylon including:
    - Issues (support tickets/conversations)
    - Messages (comments on issues)
    - Tags
    - Attachments
    - Accounts (read-only for matching)
    - Contacts (read-only for matching)
    - Users (read-only for matching)
    - Teams (read-only for matching)

    Example:
        client = PylonClient(api_key="your_api_key")
        issues = list(client.get_issues(days=30))
    """

    BASE_URL = "https://api.usepylon.com"

    def __init__(self, api_key: str | None = None, timeout: float = 30.0):
        """
        Initialize the Pylon client.

        Args:
            api_key: Pylon API key. If not provided, will look for PYLON_API_KEY env var.
            timeout: Timeout in seconds for HTTP requests to the Pylon API.

        Raises:
            ValueError: If no API key is provided or found in environment.
        """
        self.api_key = api_key or os.getenv("PYLON_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Pylon API key must be provided or set in PYLON_API_KEY environment variable"
            )

        self.session = requests.Session()
        self.timeout = timeout
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=4, max=60),
        retry=retry_if_exception_type(
            (requests.exceptions.RequestException, PylonRateLimitError)
        ),
    )
    def _make_request(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        method: str = "GET",
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make a request to the Pylon API with retry logic.

        Args:
            endpoint: API endpoint (e.g., "/issues")
            params: Query parameters (for GET/DELETE requests)
            method: HTTP method ("GET", "POST", or "PATCH")
            data: JSON data (for POST/PATCH requests)

        Returns:
            JSON response as dictionary

        Raises:
            PylonAPIError: If the API returns an error
        """
        url = f"{self.BASE_URL}{endpoint}"

        if method == "POST":
            response = self.session.post(
                url, json=data, params=params, timeout=self.timeout
            )
        elif method == "PATCH":
            response = self.session.patch(
                url, json=data, params=params, timeout=self.timeout
            )
        else:
            response = self.session.get(url, params=params, timeout=self.timeout)

        if response.status_code == 429:
            # Rate limit exceeded - raise special exception to trigger retry
            raise PylonRateLimitError(f"Rate limit exceeded: {response.text}")

        if response.status_code != 200:
            error_msg = f"Pylon API error {response.status_code}: {response.text}"
            raise PylonAPIError(error_msg)

        return response.json()

    def _paginate(
        self, endpoint: str, params: dict[str, Any] | None = None, delay: float = 0.5
    ) -> Iterator[dict[str, Any]]:
        """
        Paginate through API results using cursor-based pagination.

        Args:
            endpoint: API endpoint
            params: Query parameters
            delay: Delay in seconds between requests to avoid rate limiting

        Yields:
            Individual items from the paginated response
        """
        # Work on a copy so that we don't mutate the caller's params dict while
        # adding pagination cursors.
        params = dict(params or {})
        cursor = None

        while True:
            if cursor:
                params["cursor"] = cursor

            response_data = self._make_request(endpoint, params)
            response = PylonResponse(**response_data)

            # Yield each item in the data array
            yield from response.data

            # Check if there are more pages
            if not response.pagination or not response.pagination.has_next_page:
                break

            cursor = response.pagination.cursor

            # Add delay between requests to avoid rate limiting
            if delay > 0:
                time.sleep(delay)

    def get_issues(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        days: int | None = None,
        limit: int | None = None,
    ) -> Iterator[PylonIssue]:
        """
        Get issues from Pylon.

        Args:
            start_time: Start of time range (defaults to 30 days ago if days not specified)
            end_time: End of time range (defaults to now)
            days: Number of days to look back (alternative to start_time)
            limit: Maximum number of issues to retrieve per page

        Yields:
            PylonIssue objects

        Example:
            # Get issues from last 7 days
            for issue in client.get_issues(days=7):
                print(issue.title)
        """
        # Set default time range
        if end_time is None:
            end_time = datetime.utcnow()

        if start_time is None:
            if days is not None:
                start_time = end_time - timedelta(days=days)
            else:
                start_time = end_time - timedelta(days=30)

        params = {
            "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end_time": end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        if limit:
            params["limit"] = limit

        for item in self._paginate("/issues", params):
            yield PylonIssue.from_pylon_dict(item)

    def get_issue_by_number(self, number: int) -> PylonIssue | None:
        """Fetch a single issue by its ticket number.

        Uses the GET /issues/{id} endpoint which accepts either an issue ID
        or ticket number.

        Args:
            number: The ticket number to fetch (e.g., 36800).

        Returns:
            PylonIssue if found, None otherwise.

        Example:
            issue = client.get_issue_by_number(36800)
            if issue:
                print(f"Found: {issue.title}")
        """
        try:
            response = self._make_request(f"/issues/{number}", method="GET")
            data = response.get("data", response)
            return PylonIssue.from_pylon_dict(data)
        except PylonAPIError as e:
            if "404" in str(e):
                return None
            raise

    def search_issues_by_account(
        self,
        account_id: str,
        limit: int | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> Iterator[PylonIssue]:
        """Search for issues associated with a specific Pylon account.

        This uses the /issues/search API endpoint to filter issues by ``account_id``.
        It can optionally apply a time window on ``latest_message_time`` so callers
        can implement efficient incremental syncs.

        Args:
            account_id: The Pylon account ID to filter by.
            limit: Maximum number of issues to retrieve per page (defaults to 100, max 1000).
            start_time: Optional lower bound (inclusive) for ``latest_message_time`` (UTC).
            end_time: Optional upper bound (exclusive) for ``latest_message_time`` (UTC).

        Yields:
            PylonIssue objects associated with the account.

        Example:
            # Get all issues for a specific account
            for issue in client.search_issues_by_account('account_123'):
                print(f"Issue #{issue.number}: {issue.title}")

            # Get issues for an account updated since a specific time
            from datetime import datetime, timedelta
            cutoff = datetime.utcnow() - timedelta(days=1)
            for issue in client.search_issues_by_account('account_123', start_time=cutoff):
                print(issue.latest_message_time)
        """
        # Build time-aware filter only when a time window is requested to preserve
        # the original simple payload shape used in existing callers.
        if start_time or end_time:
            subfilters = [
                {
                    "field": "account_id",
                    "operator": "equals",
                    "value": account_id,
                }
            ]

            if start_time is not None:
                subfilters.append(
                    {
                        "field": "latest_message_time",
                        "operator": "time_is_after",
                        "value": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    }
                )

            if end_time is not None:
                subfilters.append(
                    {
                        "field": "latest_message_time",
                        "operator": "time_is_before",
                        "value": end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    }
                )

            payload = {
                "filter": {
                    "operator": "and",
                    "subfilters": subfilters,
                },
                "limit": limit or 100,
            }
        else:
            payload = {
                "filter": {
                    "field": "account_id",
                    "operator": "equals",
                    "value": account_id,
                },
                "limit": limit or 100,
            }

        response = self._make_request("/issues/search", method="POST", data=payload)

        # Handle paginated response
        if "data" in response:
            for item in response["data"]:
                yield PylonIssue.from_pylon_dict(item)

            # Handle pagination if there are more results
            while response.get("pagination", {}).get("has_next_page"):
                cursor = response["pagination"]["cursor"]
                payload["cursor"] = cursor
                response = self._make_request(
                    "/issues/search", method="POST", data=payload
                )
                if "data" in response:
                    for item in response["data"]:
                        yield PylonIssue.from_pylon_dict(item)

    def get_tags(self, limit: int | None = None) -> Iterator[PylonTag]:
        """
        Get tags from Pylon.

        Args:
            limit: Maximum number of tags to retrieve per page

        Yields:
            PylonTag objects
        """
        params = {}
        if limit:
            params["limit"] = limit

        for item in self._paginate("/tags", params):
            yield PylonTag.from_pylon_dict(item)

    def get_accounts(self, limit: int | None = None) -> Iterator[PylonAccount]:
        """
        Get accounts from Pylon (read-only for matching).

        Args:
            limit: Maximum number of accounts to retrieve per page

        Yields:
            PylonAccount objects
        """
        params = {}
        if limit:
            params["limit"] = limit

        for item in self._paginate("/accounts", params):
            yield PylonAccount.from_pylon_dict(item)

    def get_account(self, account_id: str) -> PylonAccount:
        """
        Get a single account by ID from Pylon.

        Args:
            account_id: The Pylon account ID

        Returns:
            PylonAccount object

        Raises:
            PylonAPIError: If the account is not found or API error occurs
        """
        response = self._make_request(f"/accounts/{account_id}")
        # Single entity responses are wrapped in 'data'
        if "data" in response:
            return PylonAccount.from_pylon_dict(response["data"])
        return PylonAccount.from_pylon_dict(response)

    def search_accounts_by_custom_field(
        self, field_slug: str, value: str
    ) -> Iterator[PylonAccount]:
        """
        Search for accounts by custom field value using Pylon's search API.

        This is much faster than iterating through all accounts when searching
        for a specific custom field value (e.g., Salesforce Account ID).

        Args:
            field_slug: The slug of the custom field (e.g., 'account.salesforce.Account_ID_for_Pylon__c')
            value: The value to search for

        Yields:
            PylonAccount objects matching the search criteria

        Example:
            # Find account by Salesforce ID
            for account in client.search_accounts_by_custom_field(
                'account.salesforce.Account_ID_for_Pylon__c',
                '001PU00000BRiY7'
            ):
                print(f"Found: {account.name}")
        """
        payload = {
            "filter": {"field": field_slug, "operator": "equals", "value": value},
            "limit": 100,
        }

        response = self._make_request("/accounts/search", method="POST", data=payload)

        # Handle paginated response
        if "data" in response:
            for item in response["data"]:
                yield PylonAccount.from_pylon_dict(item)

            # Handle pagination if there are more results
            while response.get("pagination", {}).get("has_next_page"):
                cursor = response["pagination"]["cursor"]
                payload["cursor"] = cursor
                response = self._make_request(
                    "/accounts/search", method="POST", data=payload
                )
                if "data" in response:
                    for item in response["data"]:
                        yield PylonAccount.from_pylon_dict(item)

    def get_contacts(self, limit: int | None = None) -> Iterator[PylonContact]:
        """
        Get contacts from Pylon (read-only for matching).

        Args:
            limit: Maximum number of contacts to retrieve per page

        Yields:
            PylonContact objects
        """
        params = {}
        if limit:
            params["limit"] = limit

        for item in self._paginate("/contacts", params):
            yield PylonContact.from_pylon_dict(item)

    def get_contact(self, contact_id: str) -> PylonContact:
        """
        Get a single contact by ID from Pylon.

        Args:
            contact_id: The Pylon contact ID

        Returns:
            PylonContact object

        Raises:
            PylonAPIError: If the contact is not found or API error occurs
        """
        response = self._make_request(f"/contacts/{contact_id}")
        # Single entity responses are wrapped in 'data'
        if "data" in response:
            return PylonContact.from_pylon_dict(response["data"])
        return PylonContact.from_pylon_dict(response)

    def get_users(self, limit: int | None = None) -> Iterator[PylonUser]:
        """
        Get users from Pylon (read-only for matching).

        Args:
            limit: Maximum number of users to retrieve per page

        Yields:
            PylonUser objects
        """
        params = {}
        if limit:
            params["limit"] = limit

        for item in self._paginate("/users", params):
            yield PylonUser.from_pylon_dict(item)

    def get_user(self, user_id: str) -> PylonUser:
        """
        Get a single user by ID from Pylon.

        Issue #195/#196: Added for fetching assignee information.

        Args:
            user_id: The Pylon user ID

        Returns:
            PylonUser object

        Raises:
            PylonAPIError: If the user is not found or API error occurs
        """
        response = self._make_request(f"/users/{user_id}")
        # Single entity responses are wrapped in 'data'
        if "data" in response:
            return PylonUser.from_pylon_dict(response["data"])
        return PylonUser.from_pylon_dict(response)

    def get_teams(self, limit: int | None = None) -> Iterator[PylonTeam]:
        """
        Get teams from Pylon (read-only for matching).

        Args:
            limit: Maximum number of teams to retrieve per page

        Yields:
            PylonTeam objects
        """
        params = {}
        if limit:
            params["limit"] = limit

        for item in self._paginate("/teams", params):
            yield PylonTeam.from_pylon_dict(item)

    def get_messages(
        self, issue_id: str, limit: int | None = None
    ) -> list[PylonMessage]:
        """
        Get messages for a specific issue.

        Args:
            issue_id: The Pylon issue ID
            limit: Maximum number of messages to retrieve

        Returns:
            List of PylonMessage objects
        """
        params = {}
        if limit:
            params["limit"] = limit

        response = self._make_request(f"/issues/{issue_id}/messages", params=params)
        messages = []

        if "data" in response:
            for item in response["data"]:
                try:
                    messages.append(PylonMessage.from_pylon_dict(item))
                except Exception as e:
                    print(
                        f"Warning: Failed to parse message {item.get('id', 'unknown')}: {e}"
                    )
                    continue

        return messages

    def get_issue(self, issue_id: str) -> PylonIssue:
        """Fetch a single issue via Pylon's GET /issues/{id} endpoint.

        This is useful when other endpoints (such as /issues/search) return a
        partial issue representation that omits certain fields (for example,
        tenant custom fields).

        Args:
            issue_id: The Pylon issue ID.

        Returns:
            A :class:`PylonIssue` instance.
        """
        response = self._make_request(f"/issues/{issue_id}", method="GET")

        # Single-entity responses are often wrapped in "data".
        data = response.get("data", response)
        return PylonIssue.from_pylon_dict(data)

    def update_issue(self, issue_id: str, payload: dict[str, Any]) -> PylonIssue:
        """Update an issue via Pylon's PATCH /issues/{id} endpoint.

        Callers are responsible for constructing a payload that matches the
        Pylon Issues API schema. For example, to update a custom field::

            {
                "custom_fields": [
                    {"slug": "check_in_history", "value": "line1\nline2"}
                ]
            }

        Args:
            issue_id: The Pylon issue ID to update.
            payload: The JSON body to send to the PATCH endpoint.

        Returns:
            The updated :class:`PylonIssue` instance.
        """
        if not payload:
            raise ValueError("update_issue called with empty payload")

        response = self._make_request(
            f"/issues/{issue_id}", method="PATCH", data=payload
        )

        # Single-entity responses are wrapped in "data" according to the
        # Pylon API docs; fall back to top-level JSON for robustness.
        data = response.get("data", response)
        return PylonIssue.from_pylon_dict(data)

    def get_attachments(self, issue_id: str) -> list[PylonAttachment]:
        """
        Get attachments for a specific issue.

        Note: This endpoint structure is not yet confirmed.
        May need to be updated based on actual API behavior.

        Args:
            issue_id: The Pylon issue ID

        Returns:
            List of PylonAttachment objects
        """
        # TODO: Verify the correct endpoint for attachments
        # Possible endpoints: /issues/{id}/attachments or /attachments?issue_id={id}
        raise NotImplementedError("Attachments endpoint structure not yet confirmed")

    def close(self):
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
