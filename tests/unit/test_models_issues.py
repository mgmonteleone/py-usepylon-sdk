"""Unit tests for PylonIssue model."""

from pylon.models import PylonIssue
from pylon.models.base import PylonReference


class TestPylonIssue:
    """Tests for PylonIssue model."""

    def test_from_pylon_dict_minimal(self):
        """Should create issue with minimal required fields."""
        data = {
            "id": "issue_123",
            "number": 42,
            "title": "Test Issue",
            "link": "https://app.usepylon.com/issues/issue_123",
            "body_html": "<p>Test body</p>",
            "state": "open",
            "latest_message_time": "2024-01-15T10:30:00Z",
            "created_at": "2024-01-15T10:00:00Z",
            "customer_portal_visible": True,
            "source": "email",
            "type": "Conversation",
            "number_of_touches": 1,
        }
        issue = PylonIssue.from_pylon_dict(data)
        assert issue.id == "issue_123"
        assert issue.number == 42
        assert issue.title == "Test Issue"
        assert issue.state == "open"
        assert issue.source == "email"
        assert issue.number_of_touches == 1

    def test_from_pylon_dict_with_all_fields(self):
        """Should create issue with all optional fields."""
        data = {
            "id": "issue_456",
            "number": 100,
            "title": "Complete Issue",
            "link": "https://app.usepylon.com/issues/issue_456",
            "body_html": "<p>Full body</p>",
            "state": "closed",
            "latest_message_time": "2024-02-20T14:00:00Z",
            "created_at": "2024-02-20T08:00:00Z",
            "customer_portal_visible": False,
            "source": "slack",
            "type": "Bug",
            "number_of_touches": 5,
            "assignee": {"id": "user_123"},
            "team": {"id": "team_456"},
            "account": {"id": "acc_789"},
            "tags": ["tag_1", "tag_2"],
        }
        issue = PylonIssue.from_pylon_dict(data)
        assert issue.id == "issue_456"
        assert isinstance(issue.assignee, PylonReference)
        assert issue.assignee.id == "user_123"
        assert isinstance(issue.team, PylonReference)
        assert issue.team.id == "team_456"
        assert isinstance(issue.account, PylonReference)
        assert issue.account.id == "acc_789"
        assert issue.tags is not None
        assert len(issue.tags) == 2

    def test_from_pylon_dict_ignores_extra_fields(self):
        """Should ignore extra/unknown fields in API response."""
        data = {
            "id": "issue_extra",
            "number": 50,
            "title": "Extra Fields",
            "link": "https://app.usepylon.com/issues/issue_extra",
            "body_html": "<p>Open issue</p>",
            "state": "open",
            "latest_message_time": "2024-01-01T00:00:00Z",
            "created_at": "2024-01-01T00:00:00Z",
            "customer_portal_visible": True,
            "source": "email",
            "type": "Conversation",
            "number_of_touches": 1,
            # Extra fields that should be ignored
            "closed_at": "2024-01-01T00:00:00Z",
            "snoozed_until": "2024-01-02T00:00:00Z",
            "some_random_field": "value",
        }
        # Should not raise an error due to extra fields
        issue = PylonIssue.from_pylon_dict(data)
        assert issue.id == "issue_extra"
        # Verify extra fields are not accessible
        assert not hasattr(issue, "closed_at")
        assert not hasattr(issue, "snoozed_until")
        assert not hasattr(issue, "some_random_field")

    def test_from_pylon_dict_handles_custom_fields(self):
        """Should handle custom_fields dictionary."""
        data = {
            "id": "issue_custom",
            "number": 60,
            "title": "Custom Fields Issue",
            "link": "https://app.usepylon.com/issues/issue_custom",
            "body_html": "<p>With custom fields</p>",
            "state": "open",
            "latest_message_time": "2024-01-01T00:00:00Z",
            "created_at": "2024-01-01T00:00:00Z",
            "customer_portal_visible": True,
            "source": "email",
            "type": "Conversation",
            "number_of_touches": 1,
            "custom_fields": {
                "severity": {"slug": "severity", "value": "critical"},
            },
        }
        issue = PylonIssue.from_pylon_dict(data)
        assert "severity" in issue.custom_fields
        assert issue.custom_fields["severity"].value == "critical"
