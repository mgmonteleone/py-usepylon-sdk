# Webhook Handling

Securely receive and process Pylon webhook events.

## Setup

```python
from pylon.webhooks import WebhookHandler

handler = WebhookHandler(secret="your-webhook-secret")
```

## Register Event Handlers

```python
from pylon.webhooks.events import (
    IssueNewEvent,
    IssueAssignedEvent,
    IssueStateChangedEvent,
)

@handler.on(IssueNewEvent)
def handle_new_issue(event: IssueNewEvent):
    print(f"New issue: {event.issue_title}")

@handler.on(IssueAssignedEvent)
def handle_assignment(event: IssueAssignedEvent):
    print(f"Assigned to: {event.assignee_id}")

# Catch all events
@handler.on_any()
def log_all(event):
    print(f"Event: {event.event_type}")
```

## Process Webhooks

When a webhook arrives:

```python
handler.handle(
    payload=request_body,      # Raw bytes
    signature=signature,       # X-Pylon-Signature header
    timestamp=timestamp,       # X-Pylon-Timestamp header
)
```

## Flask Integration

```python
from flask import Flask, request

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers.get("X-Pylon-Signature")
    timestamp = request.headers.get("X-Pylon-Timestamp")
    
    try:
        handler.handle(
            payload=request.get_data(),
            signature=signature,
            timestamp=timestamp,
        )
        return "OK", 200
    except ValueError:
        return "Invalid signature", 401
```

## FastAPI Integration

```python
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    signature = request.headers.get("X-Pylon-Signature")
    timestamp = request.headers.get("X-Pylon-Timestamp")
    body = await request.body()
    
    try:
        handler.handle(
            payload=body,
            signature=signature,
            timestamp=timestamp,
        )
        return {"status": "ok"}
    except ValueError:
        raise HTTPException(401, "Invalid signature")
```

## Available Events

| Event | Description |
|-------|-------------|
| `IssueNewEvent` | New issue created |
| `IssueAssignedEvent` | Issue assigned |
| `IssueStateChangedEvent` | Issue state changed |
| `MessageNewEvent` | New message on issue |

## Parsing Events Manually

```python
from pylon.webhooks import parse_webhook_event

event = parse_webhook_event(payload)
print(f"Type: {event.event_type}")
```

