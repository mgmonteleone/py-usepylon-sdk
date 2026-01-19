"""Pydantic models for Pylon issue webhook events.

These models mirror the flattened JSON payloads sent by Pylon webhooks for
issue-related events. They are intentionally separate from the richer
``PylonIssue`` API model so that the Cloud Run ingress service can validate and
normalize incoming webhook payloads while still retaining the original field
names used by Pylon.
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Dict, List, Optional, Union, Literal, Any

from pydantic import BaseModel, Field, TypeAdapter


class BaseIssueEvent(BaseModel):
    """Fields common to all Pylon issue webhook events.

    This mirrors the flattened ``issue_*`` keys observed in Datastore for every
    ``event_type``. Numeric identifiers are modelled as ``int`` values for
    better type-safety; Pydantic will coerce from the string values used in the
    raw JSON payloads.
    """

    event_type: str
    issue_id: str
    issue_number: int
    issue_title: str
    issue_team_name: str
    issue_account_id: str
    issue_account_name: str
    issue_requester_email: str
    issue_requesteer_id: str  # sic: matches Pylon payload spelling
    issue_assignee_email: str
    issue_assignee_id: str
    issue_salesforce_account_id: Optional[str] = None


class IssueSnapshotEvent(BaseIssueEvent):
    """Full issue snapshot fields shared by most ``issue_*`` events.

    Present on: ``issue_new``, ``issue_assigned``, ``issue_field_changed``,
    ``issue_status_changed``, ``issue_tags_changed``, and ``issue_reaction``.
    """

    issue_body: str
    issue_status: str
    issue_sf_type: str
    issue_last_message_sent_at: datetime
    issue_link: str
    issue_tags: List[str] = Field(default_factory=list)
    issue_account_domains: List[str] = Field(default_factory=list)
    issue_attachment_urls: List[str] = Field(default_factory=list)
    issue_custom_field_feature_mentioned: Optional[str] = None
    issue_custom_field_ide_mentioned: Optional[str] = None
    issue_custom_field_priority: Optional[str] = None
    issue_custom_field_question_type: Optional[str] = None
    issue_custom_field_request_id_if_applicable: Optional[str] = None
    issue_custom_field_salesforce_issue_id: Optional[str] = None


class IssueNewEvent(IssueSnapshotEvent):
    """Pylon webhook event for newly-created issues."""

    event_type: Literal["issue_new"] = "issue_new"


class IssueAssignedEvent(IssueSnapshotEvent):
    """Issue assignment or reassignment event."""

    event_type: Literal["issue_assigned"] = "issue_assigned"


class IssueFieldChangedEvent(IssueSnapshotEvent):
    """Event emitted when arbitrary issue fields (including custom fields) change."""

    event_type: Literal["issue_field_changed"] = "issue_field_changed"


class IssueStatusChangedEvent(IssueSnapshotEvent):
    """Event emitted when the issue status transitions."""

    event_type: Literal["issue_status_changed"] = "issue_status_changed"


class IssueTagsChangedEvent(IssueSnapshotEvent):
    """Event emitted when the set of tags on an issue changes."""

    event_type: Literal["issue_tags_changed"] = "issue_tags_changed"


class IssueReactionEvent(IssueSnapshotEvent):
    """Reaction activity on an issue.

    The payload schema is expected to match ``IssueNewEvent`` based on the Pylon
    webhook contract, even though we do not yet have live sample data for this
    event type.
    """

    event_type: Literal["issue_reaction"] = "issue_reaction"


class IssueMessageNewEvent(BaseIssueEvent):
    """New message added to an issue (customer-visible or internal)."""

    event_type: Literal["issue_message_new"] = "issue_message_new"
    message_id: str
    message_author_id: str
    message_author_name: str
    message_body_html: str
    message_ccs: List[str] = Field(default_factory=list)
    message_is_private: bool
    message_sent_at: datetime


PylonWebhookEvent = Annotated[
    Union[
        IssueNewEvent,
        IssueAssignedEvent,
        IssueFieldChangedEvent,
        IssueStatusChangedEvent,
        IssueTagsChangedEvent,
        IssueReactionEvent,
        IssueMessageNewEvent,
    ],
    Field(discriminator="event_type"),
]


_PYLON_WEBHOOK_EVENT_ADAPTER: TypeAdapter[PylonWebhookEvent] = TypeAdapter(PylonWebhookEvent)


def parse_webhook_event(payload: Dict[str, Any]) -> PylonWebhookEvent:
    """Parse a raw webhook JSON payload into a strongly-typed event model.

    Args:
        payload: Raw JSON body decoded into a Python dict.

    Returns:
        A concrete ``Issue*Event`` instance corresponding to ``event_type``.

    Raises:
        pydantic.ValidationError: If the payload does not conform to the
        expected schema or ``event_type`` is unknown.
    """

    return _PYLON_WEBHOOK_EVENT_ADAPTER.validate_python(payload)
