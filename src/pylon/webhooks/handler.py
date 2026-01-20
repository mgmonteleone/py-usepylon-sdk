"""Webhook handler for the Pylon SDK.

This module provides the WebhookHandler class for processing incoming
Pylon webhooks with signature verification and event dispatching.

Example:
    from pylon.webhooks import WebhookHandler

    handler = WebhookHandler(secret="your_webhook_secret")

    @handler.on("issue_new")
    def on_new_issue(event):
        print(f"New issue: {event.issue_title}")

    # In your web framework
    @app.post("/webhooks/pylon")
    def webhook(request):
        return handler.handle(request.body, request.headers)
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, Any

from pylon.exceptions import (
    PylonWebhookError,
    PylonWebhookSignatureError,
    PylonWebhookTimestampError,
)
from pylon.webhooks.events import PylonWebhookEvent, parse_webhook_event

if TYPE_CHECKING:
    pass

# Type alias for event handlers
EventHandler = Callable[[PylonWebhookEvent], Any]

# Default timestamp tolerance: 5 minutes
DEFAULT_TIMESTAMP_TOLERANCE_SECONDS = 300


class WebhookHandler:
    """Handler for processing Pylon webhook events.

    The WebhookHandler provides:
    - HMAC-SHA256 signature verification
    - Timing-safe signature comparison
    - Timestamp validation to prevent replay attacks
    - Event routing via decorator pattern

    Example:
        handler = WebhookHandler(secret="whsec_...")

        @handler.on("issue_new")
        def handle_new_issue(event: IssueNewEvent):
            print(f"New issue created: {event.issue_title}")

        @handler.on("issue_message_new")
        def handle_new_message(event: IssueMessageNewEvent):
            if not event.message_is_private:
                notify_team(event)

        # Process incoming webhook
        result = handler.handle(payload_bytes, headers)

    Attributes:
        secret: The webhook secret for signature verification.
        timestamp_tolerance: Maximum age of webhook in seconds.
    """

    def __init__(
        self,
        secret: str,
        *,
        timestamp_tolerance: int = DEFAULT_TIMESTAMP_TOLERANCE_SECONDS,
        verify_signature: bool = True,
    ) -> None:
        """Initialize the webhook handler.

        Args:
            secret: The webhook secret from Pylon for signature verification.
            timestamp_tolerance: Maximum allowed age of webhook in seconds.
                Webhooks older than this are rejected to prevent replay attacks.
                Default is 300 seconds (5 minutes).
            verify_signature: Whether to verify webhook signatures.
                Set to False only for testing/development.
        """
        self._secret = secret
        self._timestamp_tolerance = timestamp_tolerance
        self._verify_signature = verify_signature
        self._handlers: dict[str, list[EventHandler]] = {}
        self._catch_all_handlers: list[EventHandler] = []

    def on(self, event_type: str) -> Callable[[EventHandler], EventHandler]:
        """Decorator to register a handler for a specific event type.

        Args:
            event_type: The event type to handle (e.g., "issue_new").

        Returns:
            A decorator function that registers the handler.

        Example:
            @handler.on("issue_new")
            def handle_new_issue(event):
                print(f"New issue: {event.issue_title}")
        """

        def decorator(func: EventHandler) -> EventHandler:
            if event_type not in self._handlers:
                self._handlers[event_type] = []
            self._handlers[event_type].append(func)
            return func

        return decorator

    def on_any(self) -> Callable[[EventHandler], EventHandler]:
        """Decorator to register a handler for all event types.

        Returns:
            A decorator function that registers the catch-all handler.

        Example:
            @handler.on_any()
            def log_all_events(event):
                logger.info(f"Received event: {event.event_type}")
        """

        def decorator(func: EventHandler) -> EventHandler:
            self._catch_all_handlers.append(func)
            return func

        return decorator

    def verify_signature(
        self,
        payload: bytes,
        signature: str,
        timestamp: str | None = None,
    ) -> None:
        """Verify the webhook signature.

        Uses HMAC-SHA256 for signature verification with timing-safe
        comparison to prevent timing attacks.

        Args:
            payload: The raw webhook payload bytes.
            signature: The signature from the webhook header.
            timestamp: Optional timestamp for replay attack prevention.

        Raises:
            PylonWebhookSignatureError: If signature verification fails.
            PylonWebhookTimestampError: If timestamp is too old.
        """
        if timestamp:
            self._validate_timestamp(timestamp)

        # Build the signed payload (timestamp + payload if timestamp provided)
        signed_payload = (
            f"{timestamp}.".encode() + payload if timestamp else payload
        )

        # Compute expected signature
        expected_sig = hmac.new(
            self._secret.encode("utf-8"),
            signed_payload,
            hashlib.sha256,
        ).hexdigest()

        # Timing-safe comparison to prevent timing attacks
        if not hmac.compare_digest(expected_sig, signature):
            raise PylonWebhookSignatureError(
                "Webhook signature verification failed: signature mismatch"
            )

    def _validate_timestamp(self, timestamp: str) -> None:
        """Validate the webhook timestamp.

        Args:
            timestamp: Unix timestamp as a string.

        Raises:
            PylonWebhookTimestampError: If timestamp is invalid or too old.
        """
        try:
            webhook_time = int(timestamp)
        except ValueError as e:
            raise PylonWebhookTimestampError(
                f"Invalid webhook timestamp format: {timestamp}",
                timestamp=timestamp,
                tolerance_seconds=self._timestamp_tolerance,
            ) from e

        current_time = int(time.time())
        age = current_time - webhook_time

        if age > self._timestamp_tolerance:
            raise PylonWebhookTimestampError(
                f"Webhook timestamp too old: {age} seconds "
                f"(tolerance: {self._timestamp_tolerance}s)",
                timestamp=timestamp,
                tolerance_seconds=self._timestamp_tolerance,
            )

        if age < -self._timestamp_tolerance:
            raise PylonWebhookTimestampError(
                f"Webhook timestamp in the future: {-age} seconds ahead",
                timestamp=timestamp,
                tolerance_seconds=self._timestamp_tolerance,
            )

    def handle(
        self,
        payload: bytes | str,
        headers: Mapping[str, str],
    ) -> list[Any]:
        """Process an incoming webhook.

        Verifies the signature (if enabled), parses the event, and
        dispatches to registered handlers.

        Args:
            payload: The raw webhook payload (bytes or string).
            headers: HTTP headers from the webhook request.

        Returns:
            List of results from all executed handlers.

        Raises:
            PylonWebhookSignatureError: If signature verification fails.
            PylonWebhookTimestampError: If timestamp validation fails.
            PylonWebhookError: If payload parsing fails.
        """
        # Convert string payload to bytes if needed
        payload_bytes = payload.encode("utf-8") if isinstance(payload, str) else payload

        # Extract signature and timestamp from headers
        # Common header formats: X-Pylon-Signature, X-Signature, Pylon-Signature
        signature = (
            headers.get("X-Pylon-Signature")
            or headers.get("x-pylon-signature")
            or headers.get("X-Signature")
            or headers.get("x-signature")
        )
        timestamp = (
            headers.get("X-Pylon-Timestamp")
            or headers.get("x-pylon-timestamp")
            or headers.get("X-Timestamp")
            or headers.get("x-timestamp")
        )

        # Verify signature if enabled
        if self._verify_signature:
            if not signature:
                raise PylonWebhookSignatureError(
                    "Missing webhook signature header"
                )
            self.verify_signature(payload_bytes, signature, timestamp)

        # Parse the payload
        try:
            payload_dict = json.loads(payload_bytes)
        except json.JSONDecodeError as e:
            raise PylonWebhookError(f"Invalid JSON payload: {e}") from e

        # Parse into event model
        event = parse_webhook_event(payload_dict)

        # Dispatch to handlers
        results: list[Any] = []

        # Call event-specific handlers
        event_type = event.event_type
        if event_type in self._handlers:
            for handler_func in self._handlers[event_type]:
                result = handler_func(event)
                results.append(result)

        # Call catch-all handlers
        for handler_func in self._catch_all_handlers:
            result = handler_func(event)
            results.append(result)

        return results

    @property
    def registered_event_types(self) -> list[str]:
        """Get list of event types that have registered handlers."""
        return list(self._handlers.keys())

