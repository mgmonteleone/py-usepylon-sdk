"""Unit tests for Pydantic models."""

import pytest

from pylon.models import (
    PylonAuditLog,
    PylonCustomField,
    PylonCustomFieldOption,
    PylonCustomFieldValue,
    PylonMe,
    PylonPagination,
    PylonProject,
    PylonReference,
    PylonResponse,
    PylonTag,
    PylonTask,
    PylonTeam,
    PylonTeamMember,
    PylonTicketForm,
    PylonTicketFormField,
    PylonUser,
    PylonUserRole,
)


class TestPylonReference:
    """Tests for PylonReference."""

    def test_creates_from_dict(self):
        """Should create reference from dict."""
        ref = PylonReference.model_validate({"id": "abc123"})
        assert ref.id == "abc123"

    def test_is_frozen(self):
        """Should be immutable."""
        ref = PylonReference(id="abc123")
        with pytest.raises(Exception):  # ValidationError for frozen
            ref.id = "xyz"  # type: ignore[misc]


class TestPylonCustomFieldValue:
    """Tests for PylonCustomFieldValue."""

    def test_creates_with_defaults(self):
        """Should create with default values."""
        field = PylonCustomFieldValue()
        assert field.slug is None
        assert field.value == ""
        assert field.values is None

    def test_creates_with_all_fields(self):
        """Should create with all fields."""
        field = PylonCustomFieldValue(
            slug="my_field",
            value="test",
            values=["a", "b"],
        )
        assert field.slug == "my_field"
        assert field.value == "test"
        assert field.values == ["a", "b"]


class TestPylonTag:
    """Tests for PylonTag."""

    def test_from_pylon_dict(self):
        """Should create from API response."""
        data = {
            "id": "tag_123",
            "value": "urgent",
            "object_type": "issue",
            "hex_color": "#FF0000",
        }
        tag = PylonTag.from_pylon_dict(data)
        assert tag.id == "tag_123"
        assert tag.value == "urgent"
        assert tag.object_type == "issue"
        assert tag.hex_color == "#FF0000"


class TestPylonUser:
    """Tests for PylonUser."""

    def test_from_pylon_dict(self):
        """Should create from API response."""
        data = {
            "id": "user_123",
            "name": "John Doe",
            "status": "active",
            "email": "john@example.com",
            "emails": ["john@example.com", "jdoe@example.com"],
            "role_id": "role_admin",
            "avatar_url": "https://example.com/avatar.png",
        }
        user = PylonUser.from_pylon_dict(data)
        assert user.id == "user_123"
        assert user.name == "John Doe"
        assert user.status == "active"
        assert len(user.emails) == 2


class TestPylonTeam:
    """Tests for PylonTeam."""

    def test_from_pylon_dict(self):
        """Should create from API response."""
        data = {
            "id": "team_123",
            "name": "Support Team",
            "users": [
                {"id": "user_1", "email": "a@example.com"},
                {"id": "user_2", "email": "b@example.com"},
            ],
        }
        team = PylonTeam.from_pylon_dict(data)
        assert team.id == "team_123"
        assert team.name == "Support Team"
        assert len(team.users) == 2
        assert isinstance(team.users[0], PylonTeamMember)


class TestPylonPagination:
    """Tests for PylonPagination."""

    def test_defaults(self):
        """Should have correct defaults."""
        pagination = PylonPagination()
        assert pagination.cursor is None
        assert pagination.has_next_page is False

    def test_from_response(self):
        """Should parse from API response."""
        data = {"cursor": "cursor_abc", "has_next_page": True}
        pagination = PylonPagination.model_validate(data)
        assert pagination.cursor == "cursor_abc"
        assert pagination.has_next_page is True


class TestPylonResponse:
    """Tests for PylonResponse."""

    def test_parses_response(self):
        """Should parse API response."""
        data = {
            "data": [{"id": "1"}, {"id": "2"}],
            "pagination": {"cursor": "abc", "has_next_page": True},
            "request_id": "req_123",
        }
        response = PylonResponse.model_validate(data)
        assert len(response.data) == 2
        assert response.pagination is not None
        assert response.pagination.cursor == "abc"
        assert response.request_id == "req_123"


class TestPylonCustomField:
    """Tests for PylonCustomField."""

    def test_from_pylon_dict(self):
        """Should create from API response."""
        data = {
            "id": "cf_123",
            "name": "Priority Level",
            "slug": "priority_level",
            "field_type": "select",
            "description": "Issue priority",
            "options": [
                {"id": "opt_1", "value": "High"},
                {"id": "opt_2", "value": "Low"},
            ],
        }
        field = PylonCustomField.from_pylon_dict(data)
        assert field.id == "cf_123"
        assert field.name == "Priority Level"
        assert field.slug == "priority_level"
        assert field.field_type == "select"
        assert len(field.options) == 2
        assert isinstance(field.options[0], PylonCustomFieldOption)


class TestPylonTask:
    """Tests for PylonTask."""

    def test_from_pylon_dict(self):
        """Should create from API response."""
        data = {
            "id": "task_123",
            "title": "Follow up with customer",
            "description": "Check on resolution",
            "status": "pending",
            "due_at": "2024-01-15T10:00:00Z",
            "issue": {"id": "issue_456"},
            "assignee": {"id": "user_789"},
        }
        task = PylonTask.from_pylon_dict(data)
        assert task.id == "task_123"
        assert task.title == "Follow up with customer"
        assert task.status == "pending"
        assert task.issue is not None
        assert task.issue.id == "issue_456"


class TestPylonProject:
    """Tests for PylonProject."""

    def test_from_pylon_dict(self):
        """Should create from API response."""
        data = {
            "id": "proj_123",
            "name": "Q1 Onboarding",
            "description": "Customer onboarding project",
            "status": "active",
            "account": {"id": "acc_456"},
        }
        project = PylonProject.from_pylon_dict(data)
        assert project.id == "proj_123"
        assert project.name == "Q1 Onboarding"
        assert project.status == "active"


class TestPylonTicketForm:
    """Tests for PylonTicketForm."""

    def test_from_pylon_dict(self):
        """Should create from API response."""
        data = {
            "id": "form_123",
            "name": "Bug Report",
            "description": "Form for bug reports",
            "fields": [
                {"id": "field_1", "name": "Summary", "field_type": "text"},
                {"id": "field_2", "name": "Steps", "field_type": "textarea"},
            ],
        }
        form = PylonTicketForm.from_pylon_dict(data)
        assert form.id == "form_123"
        assert form.name == "Bug Report"
        assert len(form.fields) == 2
        assert isinstance(form.fields[0], PylonTicketFormField)


class TestPylonUserRole:
    """Tests for PylonUserRole."""

    def test_from_pylon_dict(self):
        """Should create from API response."""
        data = {
            "id": "role_123",
            "name": "Support Agent",
            "description": "Standard support role",
            "permissions": ["view_issues", "edit_issues"],
        }
        role = PylonUserRole.from_pylon_dict(data)
        assert role.id == "role_123"
        assert role.name == "Support Agent"


class TestPylonAuditLog:
    """Tests for PylonAuditLog."""

    def test_from_pylon_dict(self):
        """Should create from API response."""
        data = {
            "id": "log_123",
            "action": "issue.created",
            "actor": {"id": "user_456"},
            "resource_type": "issue",
            "resource_id": "issue_789",
            "timestamp": "2024-01-10T15:30:00Z",
        }
        log = PylonAuditLog.from_pylon_dict(data)
        assert log.id == "log_123"
        assert log.action == "issue.created"
        assert log.resource_type == "issue"


class TestPylonMe:
    """Tests for PylonMe."""

    def test_from_pylon_dict(self):
        """Should create from API response."""
        data = {
            "id": "user_123",
            "name": "Current User",
            "email": "me@example.com",
            "status": "active",
            "role_id": "role_admin",
        }
        me = PylonMe.from_pylon_dict(data)
        assert me.id == "user_123"
        assert me.name == "Current User"
        assert me.email == "me@example.com"

