"""Unit tests for PylonAccount model."""

from pylon.models import PylonAccount
from pylon.models.base import PylonCustomFieldValue, PylonReference


class TestPylonAccount:
    """Tests for PylonAccount model."""

    def test_from_pylon_dict_minimal(self):
        """Should create account with minimal required fields."""
        data = {
            "id": "acc_123",
            "name": "Acme Corp",
            "type": "customer",
            "created_at": "2024-01-15T10:30:00Z",
        }
        account = PylonAccount.from_pylon_dict(data)
        assert account.id == "acc_123"
        assert account.name == "Acme Corp"
        assert account.type == "customer"
        # Check datetime is parsed correctly (timezone-aware)
        assert account.created_at is not None
        assert account.created_at.year == 2024
        assert account.created_at.month == 1
        assert account.created_at.day == 15

    def test_from_pylon_dict_with_all_fields(self):
        """Should create account with all fields."""
        data = {
            "id": "acc_456",
            "name": "TechCorp",
            "owner": {"id": "user_789"},
            "domain": "techcorp.com",
            "domains": ["techcorp.com", "tech.io"],
            "primary_domain": "techcorp.com",
            "type": "enterprise",
            "channels": [{"type": "slack"}, {"type": "email"}],
            "created_at": "2024-02-20T08:00:00Z",
            "tags": ["tag_1", "tag_2"],
            "custom_fields": {
                "priority": {"slug": "priority", "value": "high"},
            },
            "latest_customer_activity_time": "2024-03-15T14:00:00Z",
            "external_ids": {"salesforce": "SF_001"},
        }
        account = PylonAccount.from_pylon_dict(data)
        assert account.id == "acc_456"
        assert account.name == "TechCorp"
        assert isinstance(account.owner, PylonReference)
        assert account.owner.id == "user_789"
        assert account.domain == "techcorp.com"
        assert account.domains == ["techcorp.com", "tech.io"]
        assert account.type == "enterprise"
        assert account.channels is not None
        assert len(account.channels) == 2
        assert account.tags is not None
        assert len(account.tags) == 2
        assert account.custom_fields is not None
        assert "priority" in account.custom_fields
        assert isinstance(account.custom_fields["priority"], PylonCustomFieldValue)
        assert account.external_ids is not None
        assert account.external_ids["salesforce"] == "SF_001"

    def test_from_pylon_dict_handles_empty_latest_activity(self):
        """Should handle empty string for latest_customer_activity_time."""
        data = {
            "id": "acc_789",
            "name": "NewCorp",
            "type": "prospect",
            "created_at": "2024-01-01T00:00:00Z",
            "latest_customer_activity_time": "",
        }
        account = PylonAccount.from_pylon_dict(data)
        assert account.latest_customer_activity_time is None

    def test_from_pylon_dict_converts_custom_field_strings(self):
        """Should convert string custom fields to PylonCustomFieldValue."""
        data = {
            "id": "acc_101",
            "name": "SimpleCorp",
            "type": "customer",
            "created_at": "2024-01-01T00:00:00Z",
            "custom_fields": {
                "simple_field": "simple_value",
            },
        }
        account = PylonAccount.from_pylon_dict(data)
        assert "simple_field" in account.custom_fields
        assert account.custom_fields["simple_field"].value == "simple_value"

    def test_get_salesforce_account_id_from_new_field(self):
        """Should extract Salesforce ID from new field name."""
        data = {
            "id": "acc_sf1",
            "name": "SalesCorp",
            "type": "customer",
            "created_at": "2024-01-01T00:00:00Z",
            "custom_fields": {
                "account.salesforce.Account_ID_for_Pylon__c": {"value": "001ABC123"},
            },
        }
        account = PylonAccount.from_pylon_dict(data)
        assert account.get_salesforce_account_id() == "001ABC123"

    def test_get_salesforce_account_id_from_legacy_field(self):
        """Should fall back to legacy field name."""
        data = {
            "id": "acc_sf2",
            "name": "LegacyCorp",
            "type": "customer",
            "created_at": "2024-01-01T00:00:00Z",
            "custom_fields": {
                "account_crm_id": {"value": "001XYZ789"},
            },
        }
        account = PylonAccount.from_pylon_dict(data)
        assert account.get_salesforce_account_id() == "001XYZ789"

    def test_get_salesforce_account_id_returns_none_if_missing(self):
        """Should return None if no Salesforce ID field exists."""
        data = {
            "id": "acc_no_sf",
            "name": "NoSFCorp",
            "type": "customer",
            "created_at": "2024-01-01T00:00:00Z",
        }
        account = PylonAccount.from_pylon_dict(data)
        assert account.get_salesforce_account_id() is None

    def test_get_is_enterprise_true(self):
        """Should extract is_enterprise as True."""
        data = {
            "id": "acc_ent1",
            "name": "EnterpriseCorp",
            "type": "customer",
            "created_at": "2024-01-01T00:00:00Z",
            "custom_fields": {
                "account.is_enterprise": {"value": "true"},
            },
        }
        account = PylonAccount.from_pylon_dict(data)
        assert account.get_is_enterprise() is True

    def test_get_is_enterprise_false(self):
        """Should extract is_enterprise as False."""
        data = {
            "id": "acc_ent2",
            "name": "SMBCorp",
            "type": "customer",
            "created_at": "2024-01-01T00:00:00Z",
            "custom_fields": {
                "account.is_enterprise": {"value": "false"},
            },
        }
        account = PylonAccount.from_pylon_dict(data)
        assert account.get_is_enterprise() is False

    def test_get_is_enterprise_returns_none_if_missing(self):
        """Should return None if is_enterprise field doesn't exist."""
        data = {
            "id": "acc_ent3",
            "name": "UnknownCorp",
            "type": "customer",
            "created_at": "2024-01-01T00:00:00Z",
        }
        account = PylonAccount.from_pylon_dict(data)
        assert account.get_is_enterprise() is None
