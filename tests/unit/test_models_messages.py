"""Unit tests for PylonMessage model."""

from pylon.models.messages import (
    PylonEmailInfo,
    PylonMessage,
    PylonMessageAuthor,
    PylonSlackInfoForMessages,
)


class TestPylonMessageAuthor:
    """Tests for PylonMessageAuthor and nested classes."""

    def test_author_with_contact(self):
        """Should create author with contact info."""
        data = {
            "contact": {"id": "contact_123", "email": "customer@example.com"},
            "name": "Customer Name",
            "avatar_url": "https://example.com/avatar.jpg",
        }
        author = PylonMessageAuthor.model_validate(data)
        assert author.contact is not None
        assert author.contact.id == "contact_123"
        assert author.contact.email == "customer@example.com"
        assert author.name == "Customer Name"
        assert author.user is None

    def test_author_with_user(self):
        """Should create author with user info."""
        data = {
            "user": {"id": "user_456", "email": "agent@company.com", "name": "Agent"},
            "name": "Agent Name",
        }
        author = PylonMessageAuthor.model_validate(data)
        assert author.user is not None
        assert author.user.id == "user_456"
        assert author.user.email == "agent@company.com"
        assert author.contact is None


class TestPylonEmailInfo:
    """Tests for PylonEmailInfo."""

    def test_email_info_full(self):
        """Should parse full email info."""
        data = {
            "from_email": "sender@example.com",
            "to_emails": ["recipient1@example.com", "recipient2@example.com"],
            "cc_emails": ["cc@example.com"],
            "bcc_emails": ["bcc@example.com"],
        }
        info = PylonEmailInfo.model_validate(data)
        assert info.from_email == "sender@example.com"
        assert len(info.to_emails) == 2
        assert len(info.cc_emails) == 1
        assert len(info.bcc_emails) == 1

    def test_email_info_defaults(self):
        """Should have empty list defaults."""
        info = PylonEmailInfo()
        assert info.from_email is None
        assert info.to_emails == []
        assert info.cc_emails == []
        assert info.bcc_emails == []


class TestPylonSlackInfo:
    """Tests for PylonSlackInfoForMessages."""

    def test_slack_info(self):
        """Should parse Slack info."""
        data = {
            "channel_id": "C12345",
            "thread_ts": "1234567890.123456",
            "message_ts": "1234567890.654321",
        }
        info = PylonSlackInfoForMessages.model_validate(data)
        assert info.channel_id == "C12345"
        assert info.thread_ts == "1234567890.123456"
        assert info.message_ts == "1234567890.654321"


class TestPylonMessage:
    """Tests for PylonMessage model."""

    def test_from_pylon_dict_minimal(self):
        """Should create message with minimal fields."""
        data = {
            "id": "msg_123",
            "timestamp": "2024-01-15T10:30:00Z",
        }
        message = PylonMessage.from_pylon_dict(data)
        assert message.id == "msg_123"
        # Check datetime values (may be timezone-aware)
        assert message.timestamp.year == 2024
        assert message.timestamp.month == 1
        assert message.timestamp.day == 15
        assert message.timestamp.hour == 10
        assert message.timestamp.minute == 30
        assert message.message_html is None
        assert message.is_private is False

    def test_from_pylon_dict_full(self):
        """Should create message with all fields."""
        data = {
            "id": "msg_456",
            "message_html": "<p>Hello world</p>",
            "message_text": "Hello world",
            "timestamp": "2024-02-20T14:00:00Z",
            "source": "email",
            "author": {
                "contact": {"id": "contact_789", "email": "user@example.com"},
                "name": "User Name",
            },
            "is_private": True,
            "email_info": {
                "from_email": "user@example.com",
                "to_emails": ["support@company.com"],
            },
        }
        message = PylonMessage.from_pylon_dict(data)
        assert message.id == "msg_456"
        assert message.message_html == "<p>Hello world</p>"
        assert message.message_text == "Hello world"
        assert message.source == "email"
        assert message.author is not None
        assert message.author.contact is not None
        assert message.is_private is True
        assert message.email_info is not None
        assert message.email_info.from_email == "user@example.com"

    def test_from_pylon_dict_parses_file_urls(self):
        """Should parse file_urls into attachments."""
        data = {
            "id": "msg_with_files",
            "timestamp": "2024-01-01T00:00:00Z",
            "file_urls": [
                "https://cdn.example.com/files/abc123-document.pdf",
                "https://cdn.example.com/files/def456-image.png",
            ],
        }
        message = PylonMessage.from_pylon_dict(data)
        assert len(message.attachments) == 2
        assert message.attachments[0]["url"] == data["file_urls"][0]
        assert "filename" in message.attachments[0]

    def test_from_pylon_dict_parses_uuid_prefixed_filenames(self):
        """Should strip UUID prefix from filenames."""
        uuid = "12345678-1234-1234-1234-123456789012"
        data = {
            "id": "msg_uuid_files",
            "timestamp": "2024-01-01T00:00:00Z",
            "file_urls": [
                f"https://cdn.example.com/files/{uuid}-report.pdf",
            ],
        }
        message = PylonMessage.from_pylon_dict(data)
        assert len(message.attachments) == 1
        assert message.attachments[0]["filename"] == "report.pdf"

    def test_from_pylon_dict_with_slack_info(self):
        """Should parse Slack info."""
        data = {
            "id": "msg_slack",
            "timestamp": "2024-01-01T00:00:00Z",
            "source": "slack",
            "slack_info": {
                "channel_id": "C12345",
                "thread_ts": "1234567890.123456",
            },
        }
        message = PylonMessage.from_pylon_dict(data)
        assert message.source == "slack"
        assert message.slack_info is not None
        assert message.slack_info.channel_id == "C12345"
