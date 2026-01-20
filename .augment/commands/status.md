---
description: Check project status including git, tests, linting, and open issues
argument-hint: [git|tests|lint|issues|prs|all]
model: claude-sonnet-4-5
---

Check project status for: $ARGUMENTS

If no scope specified, check everything.

Run the following checks based on scope:

**git** - Branch, uncommitted changes, sync with remote
**lint** - Run `ruff check .` and `mypy .`
**tests** - Run `pytest --tb=no -q`
**issues** - List GitHub issues assigned to me
**prs** - List open pull requests in this repo
**all** - Run all of the above plus `uv lock --check`

Provide a clear summary of the current state.

