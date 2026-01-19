"""
Pydantic models for Pylon API entities.

These models represent the data structures returned by the Pylon API.
"""

from datetime import datetime
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field


class PylonReference(BaseModel):
    """Reference to another Pylon entity (just ID)."""
    id: str


class PylonSlackInfoForIssues(BaseModel):
    """Slack-specific information for issues."""
    message_ts: str
    channel_id: str
    workspace_id: str


class PylonCustomFieldValue(BaseModel):
    """Custom field value structure used by Pylon.

    In API responses, ``custom_fields`` are represented as an object keyed by
    slug, where each value includes at least a ``value`` and, for multi-select
    fields, ``values``. Some APIs also repeat the slug inside the value
    payload, so we capture that here when present.
    """

    slug: Optional[str] = None
    value: str = ""
    values: Optional[List[str]] = None


class PylonTag(BaseModel):
    """Pylon tag entity."""
    id: str
    value: str
    object_type: str  # "account" or "issue"
    hex_color: Optional[str] = None

    @classmethod
    def from_pylon_dict(cls, data: Dict[str, Any]) -> 'PylonTag':
        """Create a PylonTag from Pylon API response."""
        return cls(**data)


class PylonAccount(BaseModel):
    """Pylon account entity (read-only for matching)."""
    id: str
    name: str
    owner: Optional[PylonReference] = None
    domain: Optional[str] = None
    domains: Optional[List[str]] = None
    primary_domain: Optional[str] = None
    type: str
    channels: List[Any] = Field(default_factory=list)
    created_at: datetime
    tags: Optional[List[str]] = None
    custom_fields: Dict[str, PylonCustomFieldValue] = Field(default_factory=dict)
    latest_customer_activity_time: Optional[datetime] = None
    external_ids: Optional[Dict[str, str]] = None

    @classmethod
    def from_pylon_dict(cls, data: Dict[str, Any]) -> 'PylonAccount':
        """Create a PylonAccount from Pylon API response."""
        # Convert custom_fields to PylonCustomFieldValue objects
        if 'custom_fields' in data and data['custom_fields']:
            custom_fields = {}
            for key, value in data['custom_fields'].items():
                if isinstance(value, dict):
                    custom_fields[key] = PylonCustomFieldValue(**value)
                else:
                    custom_fields[key] = PylonCustomFieldValue(value=str(value))
            data['custom_fields'] = custom_fields

        # Handle empty string for datetime fields
        if 'latest_customer_activity_time' in data and data['latest_customer_activity_time'] == '':
            data['latest_customer_activity_time'] = None

        return cls(**data)

    def get_salesforce_account_id(self) -> Optional[str]:
        """
        Extract Salesforce Account ID from custom fields.

        Uses the new Pylon custom field 'account.salesforce.Account_ID_for_Pylon__c'
        which contains the Salesforce Account ID.

        This is used for matching Pylon accounts to Salesforce accounts during migration.

        Returns:
            Salesforce Account ID (18-character ID) if found, None otherwise
        """
        # Try new field name first (API slug format)
        if 'account.salesforce.Account_ID_for_Pylon__c' in self.custom_fields:
            field_value = self.custom_fields['account.salesforce.Account_ID_for_Pylon__c']
            if field_value.value:
                return field_value.value

        # Fall back to old field name for backwards compatibility
        if 'account_crm_id' in self.custom_fields:
            field_value = self.custom_fields['account_crm_id']
            if field_value.value:
                return field_value.value

        return None

    def get_is_enterprise(self) -> Optional[bool]:
        """
        Extract is_enterprise flag from custom fields.

        Uses the Pylon custom field 'account.is_enterprise' which indicates
        whether this is an enterprise account.

        This field is used for customer segmentation in analytics.

        Returns:
            True if enterprise account, False if not, None if field not found
        """
        if 'account.is_enterprise' in self.custom_fields:
            field_value = self.custom_fields['account.is_enterprise']
            if field_value.value:
                # Handle various boolean representations
                value_str = str(field_value.value).lower()
                if value_str in ('true', '1', 'yes'):
                    return True
                elif value_str in ('false', '0', 'no'):
                    return False

        return None


class PylonContact(BaseModel):
    """Pylon contact entity (read-only for matching)."""
    id: str
    name: str
    email: Optional[str] = None  # Some contacts may not have an email
    emails: List[str] = Field(default_factory=list)
    account: Optional[PylonReference] = None
    custom_fields: Dict[str, PylonCustomFieldValue] = Field(default_factory=dict)
    portal_role: Optional[str] = None
    avatar_url: Optional[str] = None

    @classmethod
    def from_pylon_dict(cls, data: Dict[str, Any]) -> 'PylonContact':
        """Create a PylonContact from Pylon API response."""
        # Convert custom_fields to PylonCustomFieldValue objects
        if 'custom_fields' in data and data['custom_fields']:
            custom_fields = {}
            for key, value in data['custom_fields'].items():
                if isinstance(value, dict):
                    custom_fields[key] = PylonCustomFieldValue(**value)
                else:
                    custom_fields[key] = PylonCustomFieldValue(value=str(value))
            data['custom_fields'] = custom_fields
        
        return cls(**data)

    def get_salesforce_contact_id(self, sf_client=None) -> Optional[str]:
        """
        Extract Salesforce Contact ID from custom fields, with email-based fallback.

        Uses the new Pylon custom field 'contact.salesforce.Contact_ID_for_Pylon__c'
        which contains the Salesforce Contact ID.

        If no ID is found in custom fields and a Salesforce client is provided,
        attempts to find the contact by email address in Salesforce.

        This is used for matching Pylon contacts to Salesforce contacts during migration.

        Args:
            sf_client: Optional Salesforce client for email-based fallback lookup

        Returns:
            Salesforce Contact ID (18-character ID) if found, None otherwise
        """
        # Try new field name first (API slug format)
        if 'contact.salesforce.Contact_ID_for_Pylon__c' in self.custom_fields:
            field_value = self.custom_fields['contact.salesforce.Contact_ID_for_Pylon__c']
            if field_value.value:
                return field_value.value

        # Fall back to old field name for backwards compatibility
        if 'contact_crm_id' in self.custom_fields:
            field_value = self.custom_fields['contact_crm_id']
            if field_value.value:
                return field_value.value

        # Email-based fallback: Try to find contact in Salesforce by email
        if sf_client and self.email:
            try:
                # Escape single quotes in the email to avoid breaking the SOQL
                # query or introducing injection vectors.
                safe_email = self.email.replace("'", "\\'")

                # Query Salesforce for contact with this email
                query = f"SELECT Id FROM Contact WHERE Email = '{safe_email}' LIMIT 1"
                result = sf_client.query(query)

                if result.get('totalSize', 0) > 0:
                    contact_id = result['records'][0]['Id']
                    return contact_id
            except Exception:
                # Silently fail - email lookup is best-effort
                pass

        return None


class PylonUser(BaseModel):
    """Pylon user entity (read-only for matching)."""
    id: str
    name: str
    status: str  # "active", "out_of_office", etc.
    email: str
    emails: List[str] = Field(default_factory=list)
    role_id: str
    avatar_url: Optional[str] = None

    @classmethod
    def from_pylon_dict(cls, data: Dict[str, Any]) -> 'PylonUser':
        """Create a PylonUser from Pylon API response."""
        return cls(**data)


class PylonTeamMember(BaseModel):
    """Team member reference."""
    id: str
    email: str


class PylonTeam(BaseModel):
    """Pylon team entity (read-only for matching)."""
    id: str
    name: str
    users: List[PylonTeamMember] = Field(default_factory=list)

    @classmethod
    def from_pylon_dict(cls, data: Dict[str, Any]) -> 'PylonTeam':
        """Create a PylonTeam from Pylon API response."""
        return cls(**data)


class PylonIssue(BaseModel):
    """Pylon issue entity (PRIMARY MIGRATION TARGET)."""
    id: str
    number: int
    title: str
    link: str
    body_html: str
    state: str  # "new", "waiting_on_customer", etc.
    account: Optional[PylonReference] = None
    assignee: Optional[PylonReference] = None
    requester: Optional[PylonReference] = None
    team: Optional[PylonReference] = None
    tags: Optional[List[str]] = None
    custom_fields: Dict[str, PylonCustomFieldValue] = Field(default_factory=dict)
    first_response_time: Optional[datetime] = None
    resolution_time: Optional[datetime] = None
    latest_message_time: datetime
    created_at: datetime
    customer_portal_visible: bool
    source: str  # "slack", "email", "form"
    slack: Optional[PylonSlackInfoForIssues] = None
    type: str  # "Conversation", "Ticket"
    number_of_touches: int
    first_response_seconds: Optional[int] = None
    business_hours_first_response_seconds: Optional[int] = None

    @classmethod
    def from_pylon_dict(cls, data: Dict[str, Any]) -> 'PylonIssue':
        """Create a PylonIssue from Pylon API response."""
        # Convert custom_fields to PylonCustomFieldValue objects
        if 'custom_fields' in data and data['custom_fields']:
            custom_fields = {}
            for key, value in data['custom_fields'].items():
                if isinstance(value, dict):
                    custom_fields[key] = PylonCustomFieldValue(**value)
                else:
                    custom_fields[key] = PylonCustomFieldValue(value=str(value))
            data['custom_fields'] = custom_fields
        
        return cls(**data)


class PylonMessageAuthorContact(BaseModel):
    """Contact information in message author."""
    id: str
    email: Optional[str] = None

    @classmethod
    def from_pylon_dict(cls, data: Dict[str, Any]) -> 'PylonMessageAuthorContact':
        """Create from Pylon API response."""
        return cls(**data)


class PylonMessageAuthorUser(BaseModel):
    """User information in message author."""
    id: str
    email: Optional[str] = None
    name: Optional[str] = None

    @classmethod
    def from_pylon_dict(cls, data: Dict[str, Any]) -> 'PylonMessageAuthorUser':
        """Create from Pylon API response."""
        return cls(**data)


class PylonMessageAuthor(BaseModel):
    """Author of a Pylon message (can be contact or user)."""
    contact: Optional[PylonMessageAuthorContact] = None
    user: Optional[PylonMessageAuthorUser] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None

    @classmethod
    def from_pylon_dict(cls, data: Dict[str, Any]) -> 'PylonMessageAuthor':
        """Create from Pylon API response."""
        parsed_data = data.copy()

        # Parse nested contact
        if 'contact' in parsed_data and parsed_data['contact']:
            parsed_data['contact'] = PylonMessageAuthorContact.from_pylon_dict(parsed_data['contact'])

        # Parse nested user
        if 'user' in parsed_data and parsed_data['user']:
            parsed_data['user'] = PylonMessageAuthorUser.from_pylon_dict(parsed_data['user'])

        return cls(**parsed_data)


class PylonEmailInfo(BaseModel):
    """Email-specific information for messages."""
    from_email: Optional[str] = None
    to_emails: List[str] = Field(default_factory=list)
    cc_emails: List[str] = Field(default_factory=list)
    bcc_emails: List[str] = Field(default_factory=list)

    @classmethod
    def from_pylon_dict(cls, data: Dict[str, Any]) -> 'PylonEmailInfo':
        """Create from Pylon API response."""
        return cls(**data)


class PylonSlackInfoForMessages(BaseModel):
    """Slack-specific information for messages."""
    channel_id: Optional[str] = None
    thread_ts: Optional[str] = None
    message_ts: Optional[str] = None

    @classmethod
    def from_pylon_dict(cls, data: Dict[str, Any]) -> 'PylonSlackInfoForMessages':
        """Create from Pylon API response."""
        return cls(**data)


class PylonMessage(BaseModel):
    """Pylon message/comment entity."""
    id: str
    message_html: Optional[str] = None  # HTML content of the message
    message_text: Optional[str] = None  # Plain text content (if available)
    timestamp: datetime  # When the message was created
    source: Optional[str] = None  # Source: 'email', 'slack', 'chat', 'web', etc.
    author: Optional[PylonMessageAuthor] = None
    is_private: bool = False  # Whether this is an internal/private message

    # Source-specific information
    email_info: Optional[PylonEmailInfo] = None
    slack_info: Optional[PylonSlackInfoForMessages] = None

    # Attachments (if any)
    attachments: List[Dict[str, Any]] = Field(default_factory=list)

    @classmethod
    def from_pylon_dict(cls, data: Dict[str, Any]) -> 'PylonMessage':
        """Create a PylonMessage from Pylon API response."""
        parsed_data = data.copy()

        # Parse nested author
        if 'author' in parsed_data and parsed_data['author']:
            parsed_data['author'] = PylonMessageAuthor.from_pylon_dict(parsed_data['author'])

        # Parse email_info
        if 'email_info' in parsed_data and parsed_data['email_info']:
            parsed_data['email_info'] = PylonEmailInfo.from_pylon_dict(parsed_data['email_info'])

        # Parse slack_info
        if 'slack_info' in parsed_data and parsed_data['slack_info']:
            parsed_data['slack_info'] = PylonSlackInfoForMessages.from_pylon_dict(parsed_data['slack_info'])

        # Parse file_urls into attachments
        # Pylon embeds attachment URLs in the 'file_urls' array
        if 'file_urls' in parsed_data and parsed_data['file_urls']:
            from urllib.parse import unquote, urlparse
            import re

            attachments = []
            for url in parsed_data['file_urls']:
                # Extract filename from URL
                # Format: https://assets.usepylon.com/{account_id}%2F{file_id}-{filename}?Expires=...
                parsed_url = urlparse(url)
                path = parsed_url.path
                decoded_path = unquote(path)
                filename = decoded_path.split('/')[-1]

                # Remove UUID prefix if present
                # UUIDs are 36 chars with format: 8-4-4-4-12 (e.g., "5c80d99b-e74c-49c1-825e-4355c4f40c53")
                # Pattern: {uuid}-{actual_filename}
                uuid_pattern = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}-(.+)$'
                match = re.match(uuid_pattern, filename)
                if match:
                    filename = match.group(1)  # Extract everything after the UUID

                attachments.append({
                    'url': url,
                    'filename': filename
                })

            parsed_data['attachments'] = attachments

            # Remove file_urls from parsed_data (not part of PylonMessage model)
            del parsed_data['file_urls']

        return cls(**parsed_data)


class PylonAttachment(BaseModel):
    """Pylon attachment entity."""
    id: str
    filename: str
    url: str
    content_type: Optional[str] = None
    size: Optional[int] = None
    created_at: datetime

    @classmethod
    def from_pylon_dict(cls, data: Dict[str, Any]) -> 'PylonAttachment':
        """Create a PylonAttachment from Pylon API response."""
        return cls(**data)


class PylonPagination(BaseModel):
    """Pagination information from Pylon API."""
    cursor: Optional[str] = None
    has_next_page: bool = False


class PylonResponse(BaseModel):
    """Generic Pylon API response wrapper."""
    data: List[Dict[str, Any]]
    pagination: Optional[PylonPagination] = None
    request_id: str

