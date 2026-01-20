---
description: Fix a specific bug, error, or code issue
argument-hint: <issue-description> [file-path]
model: claude-sonnet-4-5
---

Activate the bug-fixer agent to resolve: $ARGUMENTS

Follow the bug fixing workflow:

1. Understand the issue and analyze what needs to be fixed
2. Locate the problem by searching the codebase for affected files
3. Implement the fix with minimal, targeted changes
4. Verify the fix by running relevant tests
5. Check quality with `ruff check` and `mypy` on changed files
6. Commit changes using conventional commit format `fix: description`

Keep changes minimal and focused. Don't refactor unrelated code.

