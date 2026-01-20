"""API resource classes for the Pylon SDK.

This package contains resource classes that provide methods for
interacting with specific Pylon API endpoints.
"""

from pylon.resources._base import BaseAsyncResource, BaseSyncResource
from pylon.resources._pagination import AsyncPaginator, SyncPaginator
from pylon.resources.accounts import AccountsResource, AsyncAccountsResource
from pylon.resources.attachments import (
    AsyncAttachmentsResource,
    AttachmentsResource,
)
from pylon.resources.audit_logs import AsyncAuditLogsResource, AuditLogsResource
from pylon.resources.contacts import AsyncContactsResource, ContactsResource
from pylon.resources.custom_fields import (
    AsyncCustomFieldsResource,
    CustomFieldsResource,
)
from pylon.resources.issues import AsyncIssuesResource, IssuesResource
from pylon.resources.knowledge_base import (
    AsyncKnowledgeBaseResource,
    KnowledgeBaseResource,
)
from pylon.resources.me import AsyncMeResource, MeResource
from pylon.resources.messages import AsyncMessagesResource, MessagesResource
from pylon.resources.projects import AsyncProjectsResource, ProjectsResource
from pylon.resources.tags import AsyncTagsResource, TagsResource
from pylon.resources.tasks import AsyncTasksResource, TasksResource
from pylon.resources.teams import AsyncTeamsResource, TeamsResource
from pylon.resources.ticket_forms import AsyncTicketFormsResource, TicketFormsResource
from pylon.resources.user_roles import AsyncUserRolesResource, UserRolesResource
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
    "AttachmentsResource",
    "AuditLogsResource",
    "ContactsResource",
    "CustomFieldsResource",
    "KnowledgeBaseResource",
    "MeResource",
    "MessagesResource",
    "ProjectsResource",
    "TagsResource",
    "TasksResource",
    "TeamsResource",
    "TicketFormsResource",
    "UserRolesResource",
    "UsersResource",
    # Async resources
    "AsyncIssuesResource",
    "AsyncAccountsResource",
    "AsyncAttachmentsResource",
    "AsyncAuditLogsResource",
    "AsyncContactsResource",
    "AsyncCustomFieldsResource",
    "AsyncKnowledgeBaseResource",
    "AsyncMeResource",
    "AsyncMessagesResource",
    "AsyncProjectsResource",
    "AsyncTagsResource",
    "AsyncTasksResource",
    "AsyncTeamsResource",
    "AsyncTicketFormsResource",
    "AsyncUserRolesResource",
    "AsyncUsersResource",
]

