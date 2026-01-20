"""Unit tests for PylonContact model."""

from unittest.mock import MagicMock

from pylon.models import PylonContact
from pylon.models.base import PylonCustomFieldValue, PylonReference


class TestPylonContact:
    """Tests for PylonContact model."""

    def test_from_pylon_dict_minimal(self):
        """Should create contact with minimal required fields."""
        data = {
            "id": "contact_123",
            "name": "John Doe",
        }
        contact = PylonContact.from_pylon_dict(data)
        assert contact.id == "contact_123"
        assert contact.name == "John Doe"
        assert contact.email is None
        assert contact.emails == []

    def test_from_pylon_dict_with_all_fields(self):
        """Should create contact with all fields."""
        data = {
            "id": "contact_456",
            "name": "Jane Smith",
            "email": "jane@example.com",
            "emails": ["jane@example.com", "jsmith@work.com"],
            "account": {"id": "acc_789"},
            "custom_fields": {
                "department": {"slug": "department", "value": "Engineering"},
            },
            "portal_role": "admin",
            "avatar_url": "https://example.com/avatar.jpg",
        }
        contact = PylonContact.from_pylon_dict(data)
        assert contact.id == "contact_456"
        assert contact.name == "Jane Smith"
        assert contact.email == "jane@example.com"
        assert len(contact.emails) == 2
        assert isinstance(contact.account, PylonReference)
        assert contact.account.id == "acc_789"
        assert "department" in contact.custom_fields
        assert contact.portal_role == "admin"
        assert contact.avatar_url == "https://example.com/avatar.jpg"

    def test_from_pylon_dict_converts_string_custom_fields(self):
        """Should convert string custom fields to PylonCustomFieldValue."""
        data = {
            "id": "contact_789",
            "name": "Bob Wilson",
            "custom_fields": {
                "title": "VP Engineering",
            },
        }
        contact = PylonContact.from_pylon_dict(data)
        assert "title" in contact.custom_fields
        assert isinstance(contact.custom_fields["title"], PylonCustomFieldValue)
        assert contact.custom_fields["title"].value == "VP Engineering"

    def test_from_pylon_dict_handles_empty_custom_fields(self):
        """Should handle empty custom_fields gracefully."""
        data = {
            "id": "contact_none",
            "name": "No Fields",
            "custom_fields": {},
        }
        contact = PylonContact.from_pylon_dict(data)
        assert contact.custom_fields == {}

    def test_from_pylon_dict_handles_missing_custom_fields(self):
        """Should use empty dict when custom_fields is missing."""
        data = {
            "id": "contact_no_fields",
            "name": "No Fields Contact",
        }
        contact = PylonContact.from_pylon_dict(data)
        assert contact.custom_fields == {}

    def test_get_salesforce_contact_id_from_new_field(self):
        """Should extract Salesforce Contact ID from new field name."""
        data = {
            "id": "contact_sf1",
            "name": "Sales Person",
            "custom_fields": {
                "contact.salesforce.Contact_ID_for_Pylon__c": {"value": "003ABC123"},
            },
        }
        contact = PylonContact.from_pylon_dict(data)
        assert contact.get_salesforce_contact_id() == "003ABC123"

    def test_get_salesforce_contact_id_from_legacy_field(self):
        """Should fall back to legacy field name."""
        data = {
            "id": "contact_sf2",
            "name": "Legacy Contact",
            "custom_fields": {
                "contact_crm_id": {"value": "003XYZ789"},
            },
        }
        contact = PylonContact.from_pylon_dict(data)
        assert contact.get_salesforce_contact_id() == "003XYZ789"

    def test_get_salesforce_contact_id_returns_none_if_missing(self):
        """Should return None if no Salesforce ID field exists."""
        data = {
            "id": "contact_no_sf",
            "name": "No SF Contact",
        }
        contact = PylonContact.from_pylon_dict(data)
        assert contact.get_salesforce_contact_id() is None

    def test_get_salesforce_contact_id_with_email_fallback(self):
        """Should fall back to email lookup via SF client."""
        data = {
            "id": "contact_email_lookup",
            "name": "Email Contact",
            "email": "test@example.com",
        }
        contact = PylonContact.from_pylon_dict(data)

        # Mock Salesforce client
        mock_sf_client = MagicMock()
        mock_sf_client.query.return_value = {
            "totalSize": 1,
            "records": [{"Id": "003EMAILFOUND"}],
        }

        result = contact.get_salesforce_contact_id(sf_client=mock_sf_client)
        assert result == "003EMAILFOUND"
        mock_sf_client.query.assert_called_once()

    def test_get_salesforce_contact_id_email_fallback_not_found(self):
        """Should return None if email lookup finds nothing."""
        data = {
            "id": "contact_email_not_found",
            "name": "Unknown Contact",
            "email": "unknown@example.com",
        }
        contact = PylonContact.from_pylon_dict(data)

        mock_sf_client = MagicMock()
        mock_sf_client.query.return_value = {"totalSize": 0, "records": []}

        result = contact.get_salesforce_contact_id(sf_client=mock_sf_client)
        assert result is None

    def test_get_salesforce_contact_id_handles_sf_exception(self):
        """Should handle Salesforce client exceptions gracefully."""
        data = {
            "id": "contact_sf_error",
            "name": "Error Contact",
            "email": "error@example.com",
        }
        contact = PylonContact.from_pylon_dict(data)

        mock_sf_client = MagicMock()
        mock_sf_client.query.side_effect = Exception("SF API Error")

        result = contact.get_salesforce_contact_id(sf_client=mock_sf_client)
        assert result is None

    def test_get_salesforce_contact_id_escapes_quotes_in_email(self):
        """Should escape quotes in email for SF query."""
        data = {
            "id": "contact_quote",
            "name": "Quote Contact",
            "email": "test'quote@example.com",
        }
        contact = PylonContact.from_pylon_dict(data)

        mock_sf_client = MagicMock()
        mock_sf_client.query.return_value = {"totalSize": 0, "records": []}

        contact.get_salesforce_contact_id(sf_client=mock_sf_client)
        # Verify the quote was escaped
        call_args = mock_sf_client.query.call_args[0][0]
        assert "\\'" in call_args
