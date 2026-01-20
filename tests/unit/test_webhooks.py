"""Unit tests for webhook handling.

Tests for WebhookHandler including signature verification,
event dispatching, timestamp validation, and error handling.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any

import pytest

from pylon.exceptions import (
    PylonWebhookError,
    PylonWebhookSignatureError,
    PylonWebhookTimestampError,
)
from pylon.webhooks import WebhookHandler
from pylon.webhooks.events import IssueNewEvent


# Test fixtures
@pytest.fixture
def webhook_secret() -> str:
    """Return a test webhook secret."""
    return "test_webhook_secret_12345"


@pytest.fixture
def handler(webhook_secret: str) -> WebhookHandler:
    """Create a WebhookHandler for testing."""
    return WebhookHandler(secret=webhook_secret)


@pytest.fixture
def sample_issue_new_payload() -> dict[str, Any]:
    """Return a sample issue_new event payload."""
    return {
        "event_type": "issue_new",
        "issue_id": "issue_123",
        "issue_number": 42,
        "issue_title": "Test Issue",
        "issue_team_name": "Support",
        "issue_account_id": "acc_123",
        "issue_account_name": "Test Account",
        "issue_requester_email": "user@example.com",
        "issue_requesteer_id": "user_123",
        "issue_assignee_email": "agent@example.com",
        "issue_assignee_id": "agent_123",
        "issue_body": "This is a test issue",
        "issue_status": "open",
        "issue_sf_type": "support",
        "issue_last_message_sent_at": "2024-01-15T10:30:00Z",
        "issue_link": "https://app.usepylon.com/issues/issue_123",
        "issue_tags": ["billing", "urgent"],
        "issue_account_domains": ["example.com"],
        "issue_attachment_urls": [],
    }


def compute_signature(secret: str, payload: bytes, timestamp: str | None = None) -> str:
    """Compute HMAC-SHA256 signature for testing."""
    signed_payload = f"{timestamp}.".encode() + payload if timestamp else payload
    return hmac.new(
        secret.encode("utf-8"),
        signed_payload,
        hashlib.sha256,
    ).hexdigest()


class TestWebhookHandler:
    """Tests for WebhookHandler class."""

    def test_handler_initialization(self, webhook_secret: str) -> None:
        """Test handler initializes with correct defaults."""
        handler = WebhookHandler(secret=webhook_secret)
        assert handler._secret == webhook_secret
        assert handler._timestamp_tolerance == 300
        assert handler._verify_signature is True

    def test_handler_custom_tolerance(self, webhook_secret: str) -> None:
        """Test handler can be initialized with custom timestamp tolerance."""
        handler = WebhookHandler(secret=webhook_secret, timestamp_tolerance=600)
        assert handler._timestamp_tolerance == 600

    def test_handler_disable_verification(self, webhook_secret: str) -> None:
        """Test handler can disable signature verification."""
        handler = WebhookHandler(secret=webhook_secret, verify_signature=False)
        assert handler._verify_signature is False


class TestEventRegistration:
    """Tests for event handler registration."""

    def test_on_decorator_registers_handler(self, handler: WebhookHandler) -> None:
        """Test @handler.on() decorator registers event handlers."""

        @handler.on("issue_new")
        def handle_new_issue(_event: IssueNewEvent) -> str:
            return "handled"

        assert "issue_new" in handler._handlers
        assert len(handler._handlers["issue_new"]) == 1

    def test_on_decorator_allows_multiple_handlers(
        self, handler: WebhookHandler
    ) -> None:
        """Test multiple handlers can be registered for same event."""

        @handler.on("issue_new")
        def handler1(_event: IssueNewEvent) -> str:
            return "handler1"

        @handler.on("issue_new")
        def handler2(_event: IssueNewEvent) -> str:
            return "handler2"

        assert len(handler._handlers["issue_new"]) == 2

    def test_on_any_decorator_registers_catch_all(
        self, handler: WebhookHandler
    ) -> None:
        """Test @handler.on_any() registers catch-all handler."""

        @handler.on_any()
        def log_all(_event: Any) -> str:
            return "logged"

        assert len(handler._catch_all_handlers) == 1

    def test_registered_event_types_property(self, handler: WebhookHandler) -> None:
        """Test registered_event_types returns list of registered types."""

        @handler.on("issue_new")
        def h1(e: Any) -> None:
            pass

        @handler.on("issue_assigned")
        def h2(e: Any) -> None:
            pass

        event_types = handler.registered_event_types
        assert "issue_new" in event_types
        assert "issue_assigned" in event_types


class TestSignatureVerification:
    """Tests for webhook signature verification."""

    def test_valid_signature_passes(
        self, handler: WebhookHandler, webhook_secret: str
    ) -> None:
        """Test valid signature is accepted."""
        payload = b'{"event_type": "issue_new"}'
        signature = compute_signature(webhook_secret, payload)

        # Should not raise
        handler.verify_signature(payload, signature)

    def test_valid_signature_with_timestamp_passes(
        self, handler: WebhookHandler, webhook_secret: str
    ) -> None:
        """Test valid signature with timestamp is accepted."""
        payload = b'{"event_type": "issue_new"}'
        timestamp = str(int(time.time()))
        signature = compute_signature(webhook_secret, payload, timestamp)

        # Should not raise
        handler.verify_signature(payload, signature, timestamp)

    def test_invalid_signature_raises_error(
        self, handler: WebhookHandler
    ) -> None:
        """Test invalid signature raises PylonWebhookSignatureError."""
        payload = b'{"event_type": "issue_new"}'
        bad_signature = "invalid_signature_12345"

        with pytest.raises(PylonWebhookSignatureError) as exc_info:
            handler.verify_signature(payload, bad_signature)

        assert "signature mismatch" in str(exc_info.value)

    def test_tampered_payload_fails_verification(
        self, handler: WebhookHandler, webhook_secret: str
    ) -> None:
        """Test signature fails if payload was tampered with."""
        original_payload = b'{"event_type": "issue_new"}'
        signature = compute_signature(webhook_secret, original_payload)
        tampered_payload = b'{"event_type": "issue_new", "hacked": true}'

        with pytest.raises(PylonWebhookSignatureError):
            handler.verify_signature(tampered_payload, signature)


class TestTimestampValidation:
    """Tests for webhook timestamp validation."""

    def test_current_timestamp_passes(
        self, handler: WebhookHandler, webhook_secret: str
    ) -> None:
        """Test current timestamp is accepted."""
        payload = b'{"event_type": "issue_new"}'
        timestamp = str(int(time.time()))
        signature = compute_signature(webhook_secret, payload, timestamp)

        # Should not raise
        handler.verify_signature(payload, signature, timestamp)

    def test_expired_timestamp_raises_error(
        self, webhook_secret: str
    ) -> None:
        """Test expired timestamp raises PylonWebhookTimestampError."""
        handler = WebhookHandler(secret=webhook_secret, timestamp_tolerance=300)
        payload = b'{"event_type": "issue_new"}'
        # 10 minutes ago - beyond 5 minute tolerance
        old_timestamp = str(int(time.time()) - 600)
        signature = compute_signature(webhook_secret, payload, old_timestamp)

        with pytest.raises(PylonWebhookTimestampError) as exc_info:
            handler.verify_signature(payload, signature, old_timestamp)

        assert "too old" in str(exc_info.value)

    def test_future_timestamp_raises_error(
        self, webhook_secret: str
    ) -> None:
        """Test future timestamp raises PylonWebhookTimestampError."""
        handler = WebhookHandler(secret=webhook_secret, timestamp_tolerance=300)
        payload = b'{"event_type": "issue_new"}'
        # 10 minutes in the future
        future_timestamp = str(int(time.time()) + 600)
        signature = compute_signature(webhook_secret, payload, future_timestamp)

        with pytest.raises(PylonWebhookTimestampError) as exc_info:
            handler.verify_signature(payload, signature, future_timestamp)

        assert "future" in str(exc_info.value)

    def test_invalid_timestamp_format_raises_error(
        self, handler: WebhookHandler, webhook_secret: str
    ) -> None:
        """Test invalid timestamp format raises error."""
        payload = b'{"event_type": "issue_new"}'
        bad_timestamp = "not-a-number"
        signature = compute_signature(webhook_secret, payload, bad_timestamp)

        with pytest.raises(PylonWebhookTimestampError) as exc_info:
            handler.verify_signature(payload, signature, bad_timestamp)

        assert "Invalid" in str(exc_info.value)


class TestEventDispatch:
    """Tests for webhook event dispatching."""

    def test_handle_dispatches_to_registered_handler(
        self,
        webhook_secret: str,
        sample_issue_new_payload: dict[str, Any],
    ) -> None:
        """Test handle() calls registered event handlers."""
        handler = WebhookHandler(secret=webhook_secret, verify_signature=False)
        results: list[str] = []

        @handler.on("issue_new")
        def handle_new_issue(event: IssueNewEvent) -> str:
            results.append(f"Received: {event.issue_title}")
            return "handled"

        payload = json.dumps(sample_issue_new_payload).encode()
        handler_results = handler.handle(payload, {})

        assert len(results) == 1
        assert "Test Issue" in results[0]
        assert handler_results == ["handled"]

    def test_handle_calls_multiple_handlers(
        self,
        webhook_secret: str,
        sample_issue_new_payload: dict[str, Any],
    ) -> None:
        """Test handle() calls all registered handlers for event type."""
        handler = WebhookHandler(secret=webhook_secret, verify_signature=False)
        call_count = 0

        @handler.on("issue_new")
        def handler1(_event: IssueNewEvent) -> int:
            nonlocal call_count
            call_count += 1
            return 1

        @handler.on("issue_new")
        def handler2(_event: IssueNewEvent) -> int:
            nonlocal call_count
            call_count += 1
            return 2

        payload = json.dumps(sample_issue_new_payload).encode()
        results = handler.handle(payload, {})

        assert call_count == 2
        assert results == [1, 2]

    def test_handle_calls_catch_all_handlers(
        self,
        webhook_secret: str,
        sample_issue_new_payload: dict[str, Any],
    ) -> None:
        """Test handle() calls catch-all handlers."""
        handler = WebhookHandler(secret=webhook_secret, verify_signature=False)
        logged_events: list[str] = []

        @handler.on_any()
        def log_all(event: Any) -> None:
            logged_events.append(event.event_type)

        payload = json.dumps(sample_issue_new_payload).encode()
        handler.handle(payload, {})

        assert logged_events == ["issue_new"]

    def test_handle_accepts_string_payload(
        self,
        webhook_secret: str,
        sample_issue_new_payload: dict[str, Any],
    ) -> None:
        """Test handle() accepts string payload."""
        handler = WebhookHandler(secret=webhook_secret, verify_signature=False)

        @handler.on("issue_new")
        def handle_new_issue(event: IssueNewEvent) -> str:
            return event.issue_id

        payload_str = json.dumps(sample_issue_new_payload)
        results = handler.handle(payload_str, {})

        assert results == ["issue_123"]


class TestHandleWithSignatureVerification:
    """Tests for handle() with signature verification enabled."""

    def test_handle_verifies_signature_from_headers(
        self,
        webhook_secret: str,
        sample_issue_new_payload: dict[str, Any],
    ) -> None:
        """Test handle() verifies signature from X-Pylon-Signature header."""
        handler = WebhookHandler(secret=webhook_secret)

        @handler.on("issue_new")
        def handle_new_issue(_event: IssueNewEvent) -> str:
            return "success"

        payload = json.dumps(sample_issue_new_payload).encode()
        timestamp = str(int(time.time()))
        signature = compute_signature(webhook_secret, payload, timestamp)

        headers = {
            "X-Pylon-Signature": signature,
            "X-Pylon-Timestamp": timestamp,
        }

        results = handler.handle(payload, headers)
        assert results == ["success"]

    def test_handle_missing_signature_raises_error(
        self,
        webhook_secret: str,
        sample_issue_new_payload: dict[str, Any],
    ) -> None:
        """Test handle() raises error when signature header is missing."""
        handler = WebhookHandler(secret=webhook_secret)

        payload = json.dumps(sample_issue_new_payload).encode()

        with pytest.raises(PylonWebhookSignatureError) as exc_info:
            handler.handle(payload, {})

        assert "Missing" in str(exc_info.value)


class TestErrorHandling:
    """Tests for webhook error handling."""

    def test_invalid_json_raises_error(
        self, webhook_secret: str
    ) -> None:
        """Test invalid JSON payload raises PylonWebhookError."""
        handler = WebhookHandler(secret=webhook_secret, verify_signature=False)

        with pytest.raises(PylonWebhookError) as exc_info:
            handler.handle(b"not valid json", {})

        assert "Invalid JSON" in str(exc_info.value)

