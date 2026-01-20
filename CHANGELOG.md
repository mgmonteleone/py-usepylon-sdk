# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- GitHub Actions CI/CD pipeline
- PyPI publishing workflow with trusted publisher
- Issue and PR templates
- Contributing guidelines
- Security policy
- Code of conduct

## [0.3.0] - 2026-01-20

### Added
- Rich model methods for `PylonIssue`:
  - `add_message()` - Add a message to an issue
  - `add_internal_note()` - Add an internal note
  - `resolve()` - Mark issue as resolved
  - `reopen()` - Reopen a resolved issue
  - `assign_to()` - Assign to a user
  - `assign_to_team()` - Assign to a team
  - `snooze()` - Snooze until a specific time
  - `add_tags()` / `remove_tags()` - Tag management
  - `refresh()` - Refresh data from API
- `RichModelMixin` base class for client binding
- `ClientNotBoundError` exception for unbound models

### Changed
- Models returned from resources are now automatically bound to the client

## [0.2.0] - 2026-01-20

### Added
- Webhook support with `WebhookHandler` class
- HMAC-SHA256 signature verification
- Decorator pattern for event handlers (`@handler.on("event_type")`)
- Replay attack protection with timestamp validation
- Filter builder utilities with fluent API
- `Field`, `And`, `Or`, `Not` filter classes
- Python operator overloading for filters (`&`, `|`, `~`)
- Webhook-specific exceptions (`PylonWebhookError`, `WebhookSignatureError`)

### Changed
- Filter operators updated to match Pylon API spec (`equals`, `not_equals`, etc.)

## [0.1.0] - 2026-01-19

### Added
- Initial release of the Pylon Python SDK
- `PylonClient` and `AsyncPylonClient` for sync/async operations
- Complete API coverage for all Pylon resources:
  - Issues (CRUD, search, snooze)
  - Accounts
  - Contacts
  - Users
  - Teams
  - Tags
  - Attachments
  - Messages
  - Knowledge Bases
  - Ticket Forms
- Sub-resources for nested operations
- Bulk operations with `bulk_create()` and `bulk_update()`
- Pagination support with `collect()` method
- Pydantic v2 models with strict typing
- Automatic retry with exponential backoff
- Comprehensive error handling

[Unreleased]: https://github.com/mgmonteleone/py-usepylon-sdk/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/mgmonteleone/py-usepylon-sdk/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/mgmonteleone/py-usepylon-sdk/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/mgmonteleone/py-usepylon-sdk/releases/tag/v0.1.0

