#!/usr/bin/env python3
"""Example: Basic webhook handling.

This example demonstrates how to:
- Set up a WebhookHandler
- Register event handlers
- Verify webhook signatures
- Parse and route events
"""

import os

from pylon.webhooks import WebhookHandler, parse_webhook_event
from pylon.webhooks.events import (
    IssueAssignedEvent,
    IssueNewEvent,
    IssueStateChangedEvent,
    MessageNewEvent,
)


def setup_handler():
    """Set up webhook handler with event registrations."""
    # Get webhook secret from environment
    secret = os.environ.get("PYLON_WEBHOOK_SECRET", "your-webhook-secret")
    handler = WebhookHandler(secret=secret)

    # Handle new issues
    @handler.on(IssueNewEvent)
    def handle_new_issue(event: IssueNewEvent):
        print("🆕 New issue created!")
        print(f"   Title: {event.issue_title}")
        print(f"   Issue ID: {event.issue_id}")
        # Add your logic here: notify team, create ticket, etc.

    # Handle issue assignments
    @handler.on(IssueAssignedEvent)
    def handle_assignment(event: IssueAssignedEvent):
        print("👤 Issue assigned!")
        print(f"   Issue ID: {event.issue_id}")
        print(f"   Assignee: {event.assignee_id}")
        # Add your logic here: notify assignee, update dashboard, etc.

    # Handle state changes
    @handler.on(IssueStateChangedEvent)
    def handle_state_change(event: IssueStateChangedEvent):
        print("🔄 Issue state changed!")
        print(f"   Issue ID: {event.issue_id}")
        print(f"   New State: {event.new_state}")
        # Add your logic here: update metrics, trigger workflows, etc.

    # Handle new messages
    @handler.on(MessageNewEvent)
    def handle_new_message(event: MessageNewEvent):
        print("💬 New message received!")
        print(f"   Issue ID: {event.issue_id}")
        # Add your logic here: analyze sentiment, auto-respond, etc.

    # Catch-all handler for logging
    @handler.on_any()
    def log_all_events(event):
        print(f"📝 Event received: {event.event_type}")

    return handler


def simulate_webhook():
    """Simulate receiving a webhook (for testing)."""
    handler = setup_handler()

    # Example webhook payload
    payload = b"""{
        "event_type": "issue.new",
        "issue_id": "issue_123",
        "issue_title": "Need help with integration",
        "account_id": "acc_456"
    }"""

    # In production, these come from HTTP headers:
    # signature = request.headers.get("X-Pylon-Signature")  # "sha256=..."
    # timestamp = request.headers.get("X-Pylon-Timestamp")  # "1234567890"

    try:
        # Process the webhook
        # In production, handler.handle() verifies signature and timestamp
        event = parse_webhook_event(payload)
        print(f"Parsed event: {event.event_type}")

        # Manually dispatch for demo (normally done by handler.handle())
        handler._dispatch_event(event)
    except Exception as e:
        print(f"Error processing webhook: {e}")


if __name__ == "__main__":
    print("=== Webhook Handler Demo ===\n")
    simulate_webhook()
