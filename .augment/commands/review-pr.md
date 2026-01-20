---
description: Process PR review comments and manage the PR lifecycle
argument-hint: <pr-number>
model: claude-sonnet-4-5

Activate the PR Review Boss agent to process and resolve review comments on PR $ARGUMENTS.

Follow the complete PR Review Boss workflow:

1. Fetch all review comments from automated reviewers and humans
2. Categorize issues by priority (CRITICAL, HIGH, MEDIUM, LOW)
3. Dispatch bug-fixer agents to resolve CRITICAL, HIGH, and MEDIUM issues
4. Request re-review after fixes are committed
5. Update documentation and fill test coverage gaps in parallel
6. Verify all CI checks pass and lock file is in sync
7. Request my approval before merging

Report progress as you work through each phase.

