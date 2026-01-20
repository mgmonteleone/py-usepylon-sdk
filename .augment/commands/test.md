---
description: Run tests and analyze results, optionally with coverage
argument-hint: [scope] [--coverage]
model: claude-sonnet-4-5
---

Run tests for: $ARGUMENTS

If no scope specified, run the full test suite.

Workflow:

1. Run pytest with appropriate scope:
   - No args: `pytest`
   - `unit`: `pytest tests/unit/`
   - `integration`: `pytest tests/integration/`
   - File path: `pytest {path}`

2. Analyze any failures and report root cause

3. If `--coverage` specified:
   - Run `pytest --cov=src/pylon --cov-report=term-missing`
   - Identify untested code paths
   - Suggest tests for uncovered critical paths

Report failures with file, line number, and suggested fixes.

