#!/usr/bin/env python3
"""Example: Flask webhook integration.

This example demonstrates how to:
- Set up a Flask endpoint for webhooks
- Verify webhook signatures
- Handle events securely

Requirements:
    pip install flask py-usepylon-sdk
"""

import os

from flask import Flask, abort, request

from pylon.webhooks import WebhookHandler
from pylon.webhooks.events import IssueAssignedEvent, IssueNewEvent

app = Flask(__name__)

# Initialize webhook handler with secret
webhook_handler = WebhookHandler(
    secret=os.environ.get("PYLON_WEBHOOK_SECRET", "your-secret")
)


# Register event handlers
@webhook_handler.on(IssueNewEvent)
def on_new_issue(event: IssueNewEvent):
    """Handle new issue creation."""
    print(f"New issue: {event.issue_title}")
    # Your business logic here


@webhook_handler.on(IssueAssignedEvent)
def on_issue_assigned(event: IssueAssignedEvent):
    """Handle issue assignment."""
    print(f"Issue {event.issue_id} assigned to {event.assignee_id}")
    # Your business logic here


@app.route("/webhook/pylon", methods=["POST"])
def pylon_webhook():
    """Endpoint to receive Pylon webhooks."""
    # Get signature and timestamp from headers
    signature = request.headers.get("X-Pylon-Signature")
    timestamp = request.headers.get("X-Pylon-Timestamp")

    if not signature or not timestamp:
        abort(400, "Missing signature headers")

    try:
        # Handle the webhook (verifies signature and dispatches event)
        webhook_handler.handle(
            payload=request.get_data(),
            signature=signature,
            timestamp=timestamp,
        )
        return "OK", 200
    except ValueError as e:
        # Invalid signature or timestamp
        print(f"Webhook verification failed: {e}")
        abort(401, "Invalid signature")
    except Exception as e:
        print(f"Error processing webhook: {e}")
        abort(500, "Internal error")


@app.route("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}, 200


if __name__ == "__main__":
    # For development only - use gunicorn/uwsgi in production
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
