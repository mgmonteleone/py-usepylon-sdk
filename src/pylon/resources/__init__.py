"""API resource classes for the Pylon SDK.

This package contains resource classes that provide methods for
interacting with specific Pylon API endpoints.
"""

from pylon.resources._base import BaseAsyncResource, BaseSyncResource
from pylon.resources._pagination import AsyncPaginator, SyncPaginator
from pylon.resources.accounts import AccountsResource, AsyncAccountsResource
from pylon.resources.contacts import AsyncContactsResource, ContactsResource
from pylon.resources.issues import AsyncIssuesResource, IssuesResource
from pylon.resources.tags import AsyncTagsResource, TagsResource
from pylon.resources.teams import AsyncTeamsResource, TeamsResource
from pylon.resources.users import AsyncUsersResource, UsersResource

__all__ = [
    # Base classes
    "BaseSyncResource",
    "BaseAsyncResource",
    # Pagination
    "SyncPaginator",
    "AsyncPaginator",
    # Sync resources
    "IssuesResource",
    "AccountsResource",
    "ContactsResource",
    "UsersResource",
    "TeamsResource",
    "TagsResource",
    # Async resources
    "AsyncIssuesResource",
    "AsyncAccountsResource",
    "AsyncContactsResource",
    "AsyncUsersResource",
    "AsyncTeamsResource",
    "AsyncTagsResource",
]

