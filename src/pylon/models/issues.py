"""Pydantic models for Pylon issue entities."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from pylon.models.base import PylonCustomFieldValue, PylonReference

if TYPE_CHECKING:
    from pylon._http import AsyncHTTPTransport, SyncHTTPTransport
    from pylon.resources.bound.issue_attachments import (
        IssueAttachmentsAsyncResource,
        IssueAttachmentsSyncResource,
    )
    from pylon.resources.bound.issue_messages import (
        IssueMessagesAsyncResource,
        IssueMessagesSyncResource,
    )


class PylonSlackInfoForIssues(BaseModel):
    """Slack-specific information for issues.

    Contains metadata about the Slack message that created this issue.

    Attributes:
        message_ts: Slack message timestamp.
        channel_id: Slack channel ID.
        workspace_id: Slack workspace ID.
    """

    model_config = ConfigDict(
        extra="ignore",
    )

    message_ts: str = Field(description="Slack message timestamp")
    channel_id: str = Field(description="Slack channel ID")
    workspace_id: str = Field(description="Slack workspace ID")


class PylonIssue(BaseModel):
    """Pylon issue entity (PRIMARY MIGRATION TARGET).

    Represents a support issue/ticket in Pylon.

    Attributes:
        id: Unique identifier for the issue.
        number: Human-readable issue number.
        title: Issue title.
        link: URL to the issue in Pylon.
        body_html: HTML content of the issue body.
        state: Issue state ("new", "waiting_on_customer", etc.).
        account: Reference to the associated account.
        assignee: Reference to the assigned user.
        requester: Reference to the requester contact.
        team: Reference to the assigned team.
        tags: List of tag IDs.
        custom_fields: Custom field values keyed by slug.
        first_response_time: Time of first response.
        resolution_time: Time of resolution.
        latest_message_time: Time of most recent message.
        created_at: When the issue was created.
        customer_portal_visible: Whether visible in customer portal.
        source: Source channel ("slack", "email", "form").
        slack: Slack-specific information (if source is slack).
        type: Issue type ("Conversation", "Ticket").
        number_of_touches: Number of interactions.
        first_response_seconds: Seconds until first response.
        business_hours_first_response_seconds: Business hours until first response.
    """

    model_config = ConfigDict(
        extra="ignore",
    )

    # Private attributes for sub-resource access
    _sync_transport: SyncHTTPTransport | None = PrivateAttr(default=None)
    _async_transport: AsyncHTTPTransport | None = PrivateAttr(default=None)

    id: str = Field(description="Unique identifier for the issue")
    number: int = Field(description="Human-readable issue number")
    title: str = Field(description="Issue title")
    link: str = Field(description="URL to the issue in Pylon")
    body_html: str = Field(description="HTML content of the issue body")
    state: str = Field(description="Issue state")
    account: PylonReference | None = Field(
        default=None,
        description="Reference to the associated account",
    )
    assignee: PylonReference | None = Field(
        default=None,
        description="Reference to the assigned user",
    )
    requester: PylonReference | None = Field(
        default=None,
        description="Reference to the requester contact",
    )
    team: PylonReference | None = Field(
        default=None,
        description="Reference to the assigned team",
    )
    tags: list[str] | None = Field(default=None, description="List of tag IDs")
    custom_fields: dict[str, PylonCustomFieldValue] = Field(
        default_factory=dict,
        description="Custom field values keyed by slug",
    )
    first_response_time: datetime | None = Field(
        default=None,
        description="Time of first response",
    )
    resolution_time: datetime | None = Field(
        default=None,
        description="Time of resolution",
    )
    latest_message_time: datetime = Field(description="Time of most recent message")
    created_at: datetime = Field(description="When the issue was created")
    customer_portal_visible: bool = Field(
        description="Whether visible in customer portal"
    )
    source: str = Field(description="Source channel: 'slack', 'email', 'form'")
    slack: PylonSlackInfoForIssues | None = Field(
        default=None,
        description="Slack-specific information",
    )
    type: str = Field(description="Issue type: 'Conversation', 'Ticket'")
    number_of_touches: int = Field(description="Number of interactions")
    first_response_seconds: int | None = Field(
        default=None,
        description="Seconds until first response",
    )
    business_hours_first_response_seconds: int | None = Field(
        default=None,
        description="Business hours until first response",
    )

    @classmethod
    def from_pylon_dict(cls, data: dict[str, Any]) -> PylonIssue:
        """Create a PylonIssue from Pylon API response.

        Args:
            data: Raw dictionary from the Pylon API.

        Returns:
            A PylonIssue instance.
        """
        # Make a copy to avoid mutating input
        data = data.copy()

        # Convert custom_fields to PylonCustomFieldValue objects
        if "custom_fields" in data and data["custom_fields"]:
            custom_fields = {}
            for key, value in data["custom_fields"].items():
                if isinstance(value, dict):
                    custom_fields[key] = PylonCustomFieldValue.model_validate(value)
                else:
                    custom_fields[key] = PylonCustomFieldValue(value=str(value))
            data["custom_fields"] = custom_fields

        return cls.model_validate(data)

    def _with_sync_transport(self, transport: SyncHTTPTransport) -> PylonIssue:
        """Inject a sync transport for sub-resource access.

        Args:
            transport: The sync HTTP transport.

        Returns:
            Self for chaining.
        """
        self._sync_transport = transport
        return self

    def _with_async_transport(self, transport: AsyncHTTPTransport) -> PylonIssue:
        """Inject an async transport for sub-resource access.

        Args:
            transport: The async HTTP transport.

        Returns:
            Self for chaining.
        """
        self._async_transport = transport
        return self

    @property
    def messages(self) -> IssueMessagesSyncResource | IssueMessagesAsyncResource:
        """Access messages sub-resource.

        Returns:
            A bound resource for accessing messages.

        Raises:
            RuntimeError: If no transport has been injected.
        """
        from pylon.resources.bound.issue_messages import (
            IssueMessagesAsyncResource,
            IssueMessagesSyncResource,
        )

        if self._sync_transport:
            return IssueMessagesSyncResource(self._sync_transport, self.id)
        elif self._async_transport:
            return IssueMessagesAsyncResource(self._async_transport, self.id)
        raise RuntimeError(
            "No transport available. Issue was not fetched through client."
        )

    @property
    def attachments(
        self,
    ) -> IssueAttachmentsSyncResource | IssueAttachmentsAsyncResource:
        """Access attachments sub-resource.

        Returns:
            A bound resource for accessing attachments.

        Raises:
            RuntimeError: If no transport has been injected.
        """
        from pylon.resources.bound.issue_attachments import (
            IssueAttachmentsAsyncResource,
            IssueAttachmentsSyncResource,
        )

        if self._sync_transport:
            return IssueAttachmentsSyncResource(self._sync_transport, self.id)
        elif self._async_transport:
            return IssueAttachmentsAsyncResource(self._async_transport, self.id)
        raise RuntimeError(
            "No transport available. Issue was not fetched through client."
        )
