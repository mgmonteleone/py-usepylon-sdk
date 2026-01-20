"""Unit tests for rich model methods."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import Mock

import pytest

from pylon.models.base import ClientNotBoundError
from pylon.models.issues import PylonIssue


class TestRichModelMixin:
    """Tests for RichModelMixin."""

    def test_ensure_client_raises_without_client(self):
        """Should raise ClientNotBoundError when no client is bound."""
        issue = _create_test_issue()
        # Clear any default client
        object.__setattr__(issue, "_sync_client", None)
        object.__setattr__(issue, "_async_client", None)

        with pytest.raises(ClientNotBoundError) as exc_info:
            issue._ensure_client("resolve")

        assert "resolve()" in str(exc_info.value)
        assert "PylonIssue" in str(exc_info.value)

    def test_has_sync_client_property(self):
        """Should correctly report sync client presence."""
        issue = _create_test_issue()
        # Clear any default client
        object.__setattr__(issue, "_sync_client", None)
        object.__setattr__(issue, "_async_client", None)

        assert issue._has_sync_client is False

        object.__setattr__(issue, "_sync_client", Mock())
        assert issue._has_sync_client is True

    def test_has_async_client_property(self):
        """Should correctly report async client presence."""
        issue = _create_test_issue()
        # Clear any default client
        object.__setattr__(issue, "_sync_client", None)
        object.__setattr__(issue, "_async_client", None)

        assert issue._has_async_client is False

        object.__setattr__(issue, "_async_client", Mock())
        assert issue._has_async_client is True


class TestPylonIssueRichMethods:
    """Tests for PylonIssue rich methods."""

    def test_add_message_sync(self):
        """Should add message via sync client."""
        issue = _create_test_issue()
        mock_client = Mock()
        mock_message = Mock()
        mock_client.messages.create.return_value = mock_message
        object.__setattr__(issue, "_sync_client", mock_client)
        object.__setattr__(issue, "_async_client", None)

        result = issue.add_message("Hello, world!")

        mock_client.messages.create.assert_called_once_with(
            issue_id="issue_123", content="Hello, world!", is_private=False
        )
        assert result is mock_message

    def test_add_internal_note_sync(self):
        """Should add internal note with is_private=True."""
        issue = _create_test_issue()
        mock_client = Mock()
        mock_message = Mock()
        mock_client.messages.create.return_value = mock_message
        object.__setattr__(issue, "_sync_client", mock_client)
        object.__setattr__(issue, "_async_client", None)

        result = issue.add_internal_note("Internal note")

        mock_client.messages.create.assert_called_once_with(
            issue_id="issue_123", content="Internal note", is_private=True
        )
        assert result is mock_message

    def test_resolve_sync(self):
        """Should resolve issue via sync client."""
        issue = _create_test_issue()
        mock_client = Mock()
        updated_issue = _create_test_issue(state="resolved")
        mock_client.issues.update.return_value = updated_issue
        object.__setattr__(issue, "_sync_client", mock_client)
        object.__setattr__(issue, "_async_client", None)

        result = issue.resolve()

        mock_client.issues.update.assert_called_once_with("issue_123", state="resolved")
        assert result is issue
        assert issue.state == "resolved"

    def test_reopen_sync(self):
        """Should reopen issue via sync client."""
        issue = _create_test_issue(state="resolved")
        mock_client = Mock()
        updated_issue = _create_test_issue(state="open")
        mock_client.issues.update.return_value = updated_issue
        object.__setattr__(issue, "_sync_client", mock_client)
        object.__setattr__(issue, "_async_client", None)

        result = issue.reopen()

        mock_client.issues.update.assert_called_once_with("issue_123", state="open")
        assert result is issue
        assert issue.state == "open"

    def test_assign_to_sync(self):
        """Should assign issue to user via sync client."""
        issue = _create_test_issue()
        mock_client = Mock()
        updated_issue = _create_test_issue()
        mock_client.issues.update.return_value = updated_issue
        object.__setattr__(issue, "_sync_client", mock_client)
        object.__setattr__(issue, "_async_client", None)

        issue.assign_to("user_456")

        mock_client.issues.update.assert_called_once_with(
            "issue_123", assignee_id="user_456"
        )

    def test_snooze_sync(self):
        """Should snooze issue via sync client."""
        issue = _create_test_issue()
        mock_client = Mock()
        updated_issue = _create_test_issue()
        mock_client.issues.snooze.return_value = updated_issue
        object.__setattr__(issue, "_sync_client", mock_client)
        object.__setattr__(issue, "_async_client", None)

        until = datetime(2024, 1, 15, 10, 0, 0)
        issue.snooze(until)

        mock_client.issues.snooze.assert_called_once_with("issue_123", until=until)

    def test_refresh_sync(self):
        """Should refresh issue via sync client."""
        issue = _create_test_issue(title="Old Title")
        mock_client = Mock()
        updated_issue = _create_test_issue(title="New Title")
        mock_client.issues.get.return_value = updated_issue
        object.__setattr__(issue, "_sync_client", mock_client)
        object.__setattr__(issue, "_async_client", None)

        result = issue.refresh()

        mock_client.issues.get.assert_called_once_with("issue_123")
        assert result is issue
        assert issue.title == "New Title"

    def test_add_tags_sync(self):
        """Should add tags via sync client."""
        issue = _create_test_issue()
        mock_client = Mock()
        updated_issue = _create_test_issue(tags=["tag_1", "tag_2"])
        mock_client.issues.bulk_add_tags.return_value = [updated_issue]
        object.__setattr__(issue, "_sync_client", mock_client)
        object.__setattr__(issue, "_async_client", None)

        result = issue.add_tags(["tag_1", "tag_2"])

        mock_client.issues.bulk_add_tags.assert_called_once_with(
            ["issue_123"], ["tag_1", "tag_2"]
        )
        assert result is issue
        assert issue.tags == ["tag_1", "tag_2"]

    def test_remove_tags_sync(self):
        """Should remove tags via sync client."""
        issue = _create_test_issue(tags=["tag_1", "tag_2"])
        mock_client = Mock()
        updated_issue = _create_test_issue(tags=[])
        mock_client.issues.bulk_remove_tags.return_value = [updated_issue]
        object.__setattr__(issue, "_sync_client", mock_client)
        object.__setattr__(issue, "_async_client", None)

        result = issue.remove_tags(["tag_1", "tag_2"])

        mock_client.issues.bulk_remove_tags.assert_called_once_with(
            ["issue_123"], ["tag_1", "tag_2"]
        )
        assert result is issue
        assert issue.tags == []

    def test_assign_to_team_sync(self):
        """Should assign issue to team via sync client."""
        issue = _create_test_issue()
        mock_client = Mock()
        updated_issue = _create_test_issue()
        mock_client.issues.update.return_value = updated_issue
        object.__setattr__(issue, "_sync_client", mock_client)
        object.__setattr__(issue, "_async_client", None)

        issue.assign_to_team("team_789")

        mock_client.issues.update.assert_called_once_with(
            "issue_123", team_id="team_789"
        )


class TestClientNotBoundError:
    """Tests for ClientNotBoundError."""

    def test_error_message(self):
        """Should include model name and method name."""
        error = ClientNotBoundError("PylonIssue", "resolve")
        assert "PylonIssue" in str(error)
        assert "resolve()" in str(error)
        assert "not bound to a client" in str(error)

    def test_attributes(self):
        """Should store model_name and method_name."""
        error = ClientNotBoundError("PylonAccount", "refresh")
        assert error.model_name == "PylonAccount"
        assert error.method_name == "refresh"


def _create_test_issue(
    id: str = "issue_123",
    number: int = 42,
    title: str = "Test Issue",
    state: str = "open",
    tags: list[str] | None = None,
) -> PylonIssue:
    """Create a test PylonIssue instance."""
    return PylonIssue(
        id=id,
        number=number,
        title=title,
        link=f"https://app.usepylon.com/issues/{id}",
        body_html="<p>Test body</p>",
        state=state,
        account=None,
        assignee=None,
        requester=None,
        team=None,
        tags=tags,
        custom_fields={},
        first_response_time=None,
        resolution_time=None,
        latest_message_time=datetime(2024, 1, 10, 12, 0, 0),
        created_at=datetime(2024, 1, 1, 10, 0, 0),
        customer_portal_visible=True,
        source="email",
        slack=None,
        type="Ticket",
        number_of_touches=1,
        first_response_seconds=None,
        business_hours_first_response_seconds=None,
    )
