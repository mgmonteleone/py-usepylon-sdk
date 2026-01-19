"""Unit tests for Pydantic models."""

import pytest

from pylon.models import (
    PylonCustomFieldValue,
    PylonPagination,
    PylonReference,
    PylonResponse,
    PylonTag,
    PylonTeam,
    PylonTeamMember,
    PylonUser,
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

