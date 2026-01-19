"""Pylon Python SDK.

A modern Python SDK for the Pylon customer support API.

This SDK provides:
- Type-safe models for all Pylon API entities
- Comprehensive exception handling
- Webhook event parsing and validation
- Support for both sync and async operations (async coming in Phase 2)

Example:
    from pylon import PylonClient
    from pylon.exceptions import PylonNotFoundError

    client = PylonClient(api_key="your_api_key")

    try:
        issues = list(client.issues.list(days=7))
        for issue in issues:
            print(f"#{issue.number}: {issue.title}")
    except PylonNotFoundError:
        print("Issue not found")

For webhook handling:
    from pylon.webhooks import parse_webhook_event, IssueNewEvent

    event = parse_webhook_event(payload)
    if isinstance(event, IssueNewEvent):
        print(f"New issue: {event.issue_title}")
"""

from pylon._version import __version__

# Exceptions
from pylon.exceptions import (
    PylonAPIError,
    PylonAuthenticationError,
    PylonError,
    PylonNotFoundError,
    PylonRateLimitError,
    PylonServerError,
    PylonValidationError,
)

# Models
from pylon.models import (
    PylonAccount,
    PylonAttachment,
    PylonContact,
    PylonCustomFieldValue,
    PylonEmailInfo,
    PylonIssue,
    PylonMessage,
    PylonMessageAuthor,
    PylonMessageAuthorContact,
    PylonMessageAuthorUser,
    PylonPagination,
    PylonReference,
    PylonResponse,
    PylonSlackInfoForIssues,
    PylonSlackInfoForMessages,
    PylonTag,
    PylonTeam,
    PylonTeamMember,
    PylonUser,
)

# Webhook events
from pylon.webhooks import (
    BaseIssueEvent,
    IssueAssignedEvent,
    IssueFieldChangedEvent,
    IssueMessageNewEvent,
    IssueNewEvent,
    IssueReactionEvent,
    IssueSnapshotEvent,
    IssueStatusChangedEvent,
    IssueTagsChangedEvent,
    PylonWebhookEvent,
    parse_webhook_event,
)

__all__ = [
    # Version
    "__version__",
    # Exceptions
    "PylonError",
    "PylonAPIError",
    "PylonAuthenticationError",
    "PylonRateLimitError",
    "PylonNotFoundError",
    "PylonValidationError",
    "PylonServerError",
    # Base models
    "PylonReference",
    "PylonCustomFieldValue",
    # Account models
    "PylonAccount",
    # Contact models
    "PylonContact",
    # Issue models
    "PylonIssue",
    "PylonSlackInfoForIssues",
    # Message models
    "PylonMessage",
    "PylonMessageAuthor",
    "PylonMessageAuthorContact",
    "PylonMessageAuthorUser",
    "PylonEmailInfo",
    "PylonSlackInfoForMessages",
    # Attachment models
    "PylonAttachment",
    # User models
    "PylonUser",
    # Team models
    "PylonTeam",
    "PylonTeamMember",
    # Tag models
    "PylonTag",
    # Pagination models
    "PylonPagination",
    "PylonResponse",
    # Webhook events
    "BaseIssueEvent",
    "IssueSnapshotEvent",
    "IssueNewEvent",
    "IssueAssignedEvent",
    "IssueFieldChangedEvent",
    "IssueStatusChangedEvent",
    "IssueTagsChangedEvent",
    "IssueReactionEvent",
    "IssueMessageNewEvent",
    "PylonWebhookEvent",
    "parse_webhook_event",
]

