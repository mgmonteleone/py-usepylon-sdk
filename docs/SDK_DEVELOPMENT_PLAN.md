# Pylon Python SDK Development Plan

## Project Overview

**Package Name**: `py-usepylon-sdk`  
**Import Name**: `pylon`  
**Repository**: `py-usepylon-sdk`  
**Target**: Production-ready PyPI SDK for the Pylon API

## Decision Log

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Package name | `py-usepylon-sdk` | Matches Pylon branding |
| Async support | Phase 2 | High priority for modern Python apps |
| Backward compatibility | No | Clean break for better API design |
| Knowledge Base scraper | Remove | API now available |
| Webhook verification | Yes | Security best practice |

---

## Current State Analysis

### Existing Components

| Component | Status | Action |
|-----------|--------|--------|
| PylonClient | Partial | Refactor to resource-based pattern |
| Models (Pydantic v1) | Partial | Migrate to Pydantic v2 |
| Webhook Events | Good | Keep, enhance with signature verification |
| Knowledge Base Scraper | Workaround | Remove, replace with API |
| Error Handling | Basic | Expand exception hierarchy |
| Pagination | Good | Keep, add iterator pattern |
| Retry Logic | Good | Keep tenacity integration |

### Missing API Coverage

- Attachments (full CRUD)
- Audit Logs
- Custom Fields
- Knowledge Base API
- Me (current user)
- Tasks & Projects
- Ticket Forms
- User Roles
- Account sub-resources (activities, files, highlights)

---

## Target Architecture

```
py-usepylon-sdk/
├── src/
│   └── pylon/
│       ├── __init__.py              # Public API exports
│       ├── _version.py              # Version info
│       ├── client.py                # PylonClient (sync)
│       ├── async_client.py          # AsyncPylonClient
│       ├── _base_client.py          # Shared client logic
│       ├── auth.py                  # Authentication handling
│       ├── exceptions.py            # Exception hierarchy
│       ├── pagination.py            # Pagination utilities
│       ├── models/
│       │   ├── __init__.py
│       │   ├── accounts.py
│       │   ├── contacts.py
│       │   ├── issues.py
│       │   ├── messages.py
│       │   ├── attachments.py
│       │   ├── knowledge_base.py
│       │   ├── teams.py
│       │   ├── users.py
│       │   ├── tags.py
│       │   ├── custom_fields.py
│       │   ├── tasks.py
│       │   ├── ticket_forms.py
│       │   ├── audit_logs.py
│       │   └── webhooks.py
│       ├── resources/
│       │   ├── __init__.py
│       │   ├── accounts.py
│       │   ├── contacts.py
│       │   ├── issues.py
│       │   ├── messages.py
│       │   ├── attachments.py
│       │   ├── knowledge_base.py
│       │   ├── teams.py
│       │   ├── users.py
│       │   ├── tags.py
│       │   ├── custom_fields.py
│       │   ├── tasks.py
│       │   ├── ticket_forms.py
│       │   ├── audit_logs.py
│       │   └── me.py
│       ├── webhooks/
│       │   ├── __init__.py
│       │   ├── handler.py           # WebhookHandler class
│       │   ├── verification.py      # Signature verification
│       │   └── events.py            # Event parsing
│       └── _utils.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docs/
├── examples/
├── pyproject.toml
├── README.md
├── CHANGELOG.md
└── LICENSE
```

---

## Development Phases

### Phase 1: Project Restructuring & Foundation
**Duration**: 3-4 days  
**Goal**: Establish proper SDK structure and packaging

#### Tasks

1. **Restructure project layout**
   - Create `src/pylon/` package structure
   - Set up proper `__init__.py` exports
   - Create `_version.py` for version management

2. **Update `pyproject.toml`**
   - Package name: `py-usepylon-sdk`
   - Dependencies: `pydantic>=2.0`, `httpx>=0.25.0`, `tenacity>=8.0`
   - Dev dependencies: `pytest`, `pytest-asyncio`, `pytest-cov`, `ruff`, `mypy`, `respx`
   - Configure ruff, mypy, pytest

3. **Migrate models to Pydantic v2**
   - Update all model definitions to v2 syntax
   - Use `model_config = ConfigDict(...)` instead of `class Config`
   - Use `field_validator` instead of `validator`

4. **Create comprehensive exception hierarchy**
   ```python
   class PylonError(Exception): ...
   class PylonAPIError(PylonError): ...
   class PylonAuthenticationError(PylonAPIError): ...
   class PylonRateLimitError(PylonAPIError): ...
   class PylonNotFoundError(PylonAPIError): ...
   class PylonValidationError(PylonAPIError): ...
   class PylonServerError(PylonAPIError): ...
   ```

5. **Remove Knowledge Base scraper**
   - Delete `knowledge_base_scraper.py`
   - Remove BeautifulSoup dependency

#### Deliverables
- [ ] New project structure in place
- [ ] All models migrated to Pydantic v2
- [ ] Exception hierarchy implemented
- [ ] pyproject.toml configured
- [ ] Scraper removed

---

### Phase 2: Core Client with Async Support
**Duration**: 4-5 days
**Goal**: Production-ready sync and async clients

#### Tasks

1. **Replace `requests` with `httpx`**
   - Unified HTTP client for sync/async
   - Connection pooling
   - Timeout configuration

2. **Create base client abstraction**
   ```python
   class BaseClient:
       def _request(self, method, path, **kwargs) -> dict: ...
       def _paginate(self, path, **kwargs) -> Iterator: ...
   ```

3. **Implement resource-based pattern**
   ```python
   client = PylonClient(api_key="...")
   client.issues.list()
   client.issues.get("id")
   client.issues.create(...)
   client.accounts.get("id").activities.list()
   ```

4. **Create AsyncPylonClient**
   ```python
   async with AsyncPylonClient() as client:
       issues = await client.issues.list()
   ```

5. **Improve pagination**
   - Iterator pattern for memory efficiency
   - `.collect()` method for full list
   - Configurable page size

#### Deliverables
- [ ] `PylonClient` with httpx
- [ ] `AsyncPylonClient` fully functional
- [ ] Resource-based API pattern
- [ ] Improved pagination utilities

---

### Phase 3: Complete API Coverage
**Duration**: 5-6 days
**Goal**: Full Pylon API coverage

#### Resources to Implement

| Resource | Methods | Priority |
|----------|---------|----------|
| Issues | list, get, get_by_number, search, create, update, snooze | High |
| Messages | list, get, create | High |
| Accounts | list, get, search, create, update + sub-resources | High |
| Contacts | list, get, search, create, update | High |
| Attachments | list, get, create, create_from_url | High |
| Knowledge Base | list_kb, get_kb, list_articles, get_article, create_article | High |
| Teams | list, get, create | Medium |
| Users | list, get, search | Medium |
| Tags | list, get, create | Medium |
| Custom Fields | list, get | Medium |
| Tasks | list, get, create, update | Medium |
| Projects | list, get, create | Medium |
| Ticket Forms | list, get | Low |
| User Roles | list, get | Low |
| Audit Logs | list, search | Low |
| Me | get | Low |

#### Deliverables
- [ ] All resources implemented
- [ ] Sub-resource support (e.g., issue.messages)
- [ ] Search/filter capabilities
- [ ] Bulk operations where supported

---

### Phase 4: Webhook Support & Developer Experience
**Duration**: 3-4 days
**Goal**: Secure webhooks and delightful DX

#### Tasks

1. **Webhook signature verification**
   - Implement HMAC-SHA256 verification per Pylon docs
   - Timing-safe comparison
   - Timestamp validation

2. **WebhookHandler class**
   ```python
   from pylon.webhooks import WebhookHandler

   handler = WebhookHandler(secret="...")

   @handler.on("issue_new")
   def handle_new_issue(event: IssueNewEvent):
       ...

   # Verify and dispatch
   handler.handle(payload, headers)
   ```

3. **Rich model methods**
   ```python
   issue = client.issues.get("123")
   issue.add_message("Response text")
   issue.resolve()
   issue.assign_to(user_id="...")
   ```

4. **Filter builder**
   ```python
   from pylon import filters

   client.issues.search(
       filters.And(
           filters.Field("state").in_(["open", "pending"]),
           filters.Field("created_at").after(datetime(2024, 1, 1))
       )
   )
   ```

#### Deliverables
- [ ] Webhook signature verification
- [ ] WebhookHandler with decorator pattern
- [ ] Rich model methods
- [ ] Filter builder utilities

---

### Phase 5: Testing & Documentation
**Duration**: 4-5 days
**Goal**: Production-ready quality

#### Testing

1. **Unit tests** (target: 80%+ coverage)
   - Model serialization/deserialization
   - Pagination logic
   - Error handling
   - Webhook verification
   - Filter building

2. **Integration tests** (with mocked API via respx)
   - Full CRUD workflows
   - Pagination scenarios
   - Error scenarios
   - Async operations

#### Documentation

1. **README.md**
   - Installation
   - Quick start
   - Authentication
   - Common use cases

2. **API Reference**
   - Auto-generated from docstrings
   - All resources documented
   - Type hints visible

3. **Examples**
   - Basic CRUD operations
   - Async usage
   - Webhook handling
   - Pagination patterns

#### Deliverables
- [ ] 80%+ test coverage
- [ ] Comprehensive README
- [ ] API reference documentation
- [ ] Example scripts

---

### Phase 6: Publishing & CI/CD
**Duration**: 2-3 days
**Goal**: Available on PyPI

#### Tasks

1. **GitHub Actions workflows**
   - Test on Python 3.11, 3.12, 3.13
   - Lint with ruff
   - Type check with mypy
   - Coverage reporting

2. **PyPI publishing**
   - Automated release on tag
   - Proper classifiers and metadata

3. **Repository setup**
   - Issue templates
   - PR template
   - Contributing guidelines
   - Security policy

#### Deliverables
- [ ] CI/CD pipeline
- [ ] Published to PyPI
- [ ] Repository documentation

---

## API Design Examples

### Basic Usage

```python
from pylon import PylonClient

# Initialize (uses PYLON_API_KEY env var if not provided)
client = PylonClient(api_key="your_api_key")

# List issues from last 7 days
for issue in client.issues.list(days=7):
    print(f"#{issue.number}: {issue.title}")

# Get specific issue
issue = client.issues.get_by_number(36800)

# Create issue
new_issue = client.issues.create(
    title="API Integration Question",
    description="How do I authenticate?",
    account_id="acc_123",
    tags=["api", "question"]
)

# Update issue
client.issues.update(
    issue.id,
    state="resolved"
)
```

### Async Usage

```python
from pylon import AsyncPylonClient
import asyncio

async def main():
    async with AsyncPylonClient() as client:
        # Concurrent requests
        issues, accounts = await asyncio.gather(
            client.issues.list(limit=100).collect(),
            client.accounts.list().collect()
        )

        for issue in issues:
            messages = await client.issues.messages.list(issue.id)
            print(f"Issue #{issue.number}: {len(messages)} messages")

asyncio.run(main())
```

### Webhook Handling

```python
from pylon.webhooks import WebhookHandler

handler = WebhookHandler(secret="your_webhook_secret")

@handler.on("issue_new")
def on_new_issue(event):
    print(f"New issue: {event.issue_title}")
    if "billing" in event.issue_tags:
        client.issues.assign(event.issue_id, team_id="billing_team")

@handler.on("issue_message_new")
def on_new_message(event):
    if not event.message_is_private:
        notify_slack(event)

# In your web framework
@app.post("/webhooks/pylon")
def webhook(request):
    return handler.handle(request.body, request.headers)
```

---

## Dependencies

### Required
```toml
dependencies = [
    "httpx>=0.25.0",
    "pydantic>=2.0",
    "tenacity>=8.0",
]
```

### Development
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-cov>=4.1.0",
    "respx>=0.20.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
]
```

---

## Timeline Summary

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Phase 1: Restructuring | 3-4 days | Week 1 |
| Phase 2: Core Client + Async | 4-5 days | Week 1-2 |
| Phase 3: API Coverage | 5-6 days | Week 2-3 |
| Phase 4: Webhooks & DX | 3-4 days | Week 3 |
| Phase 5: Testing & Docs | 4-5 days | Week 4 |
| Phase 6: Publishing | 2-3 days | Week 4 |

**Total Estimated Duration**: 3-4 weeks

---

## Success Criteria

1. **Functionality**: All Pylon API endpoints covered
2. **Quality**: 80%+ test coverage, strict type checking
3. **Performance**: Async support, connection pooling
4. **Security**: Webhook signature verification
5. **Usability**: Intuitive API, comprehensive docs
6. **Distribution**: Published on PyPI, installable via pip

