# Augment CLI Configuration

This folder contains agents and rules for the Augment Code CLI to automate development workflows for the Pylon Python SDK.

## Workflows

### 1. Feature Development (Foreman)

**Trigger**: Ask the coordinating agent to work on a GitHub issue.

```
"Implement issue #15"
"Work on the pagination feature from issue #42"
```

**Flow**:
1. **Planning** → Foreman analyzes the issue, codebase, and creates an implementation plan
2. **Building** → Parallel `builder` agents implement components (using git worktrees for isolation)
3. **Quality Check** → Foreman verifies code quality, test coverage (80%+), and linting
4. **Documentation** → `documentation` agent updates README/CHANGELOG in parallel
5. **PR Creation** → Comprehensive PR is created and handed off to PR Review Boss

### 2. PR Review Lifecycle (PR Review Boss)

**Trigger**: New PR created, review comments added, or explicit request.

```
"Review PR #8"
"Process the code review feedback on the open PR"
```

**Flow**:
1. **Review Processing** → Fetches automated review comments, categorizes by priority
2. **Bug Fixing** → Dispatches `bug-fixer` agents for CRITICAL/HIGH/MEDIUM issues
3. **Documentation & Tests** → Updates docs and fills test coverage gaps in parallel
4. **Human Approval** → Requests explicit approval before merging
5. **Merge** → Squash merges, deletes branch, closes related issues

## Agents

| Agent | Purpose | Invoked By |
|-------|---------|------------|
| `foreman` | Orchestrates feature development from issue to PR | Human |
| `pr-review-boss` | Manages PR review lifecycle to merge | Human, Foreman |
| `builder` | Implements specific components with tests | Foreman |
| `bug-fixer` | Fixes code review issues and test gaps | Foreman, PR Review Boss |
| `documentation` | Updates README, CHANGELOG, inline docs | Foreman, PR Review Boss |
| `release-manager` | Handles version bumps and releases | Human |

## Rules

| Rule | Type | Purpose |
|------|------|---------|
| `standards.md` | always_apply | Python style, code quality, git workflow |
| `data-modeling.md` | agent_requested | Pydantic v2 patterns |
| `testing.md` | agent_requested | Pytest standards, HTTP mocking |
| `security.md` | agent_requested | Secrets management, PII protection |
| `pull-requests.md` | agent_requested | PR creation guidelines |

## Slash Commands

Use these `/` commands for quick access to workflows:

| Command | Description | Usage |
|---------|-------------|-------|
| `/implement` | Start feature development on a GitHub issue | `/implement 15` |
| `/review-pr` | Process PR review comments | `/review-pr 8` |
| `/release` | Create a new versioned release | `/release 1.2.0` |
| `/fix` | Fix a specific bug or issue | `/fix "type error in client.py"` |
| `/test` | Run tests with optional coverage | `/test unit --coverage` |
| `/status` | Check project health | `/status all` |

### Usage Examples

```bash
# Implement a GitHub issue
/implement 15
/implement 42 feature/custom-branch

# Process PR reviews
/review-pr 8

# Create a release
/release 1.2.0

# Fix a specific issue
/fix "failing test in test_client.py"
/fix "type error" src/pylon/models.py

# Run tests
/test                    # Run all tests
/test unit               # Run unit tests only
/test --coverage         # Run with coverage analysis

# Check project status
/status                  # Check everything
/status git              # Git status only
/status lint             # Linting only
```

## Agent Coordination

```
┌─────────┐     ┌─────────┐     ┌─────────────────┐
│  Human  │────▶│ Foreman │────▶│ PR Review Boss  │────▶ Merge
└─────────┘     └────┬────┘     └────────┬────────┘
                     │                   │
          ┌──────────┼──────────┐        │
          ▼          ▼          ▼        ▼
     ┌─────────┐ ┌───────┐ ┌─────────┐ ┌───────────┐
     │ Builder │ │Builder│ │  Docs   │ │ Bug Fixer │
     │   (1)   │ │  (2)  │ │         │ │           │
     └─────────┘ └───────┘ └─────────┘ └───────────┘
         │           │
         ▼           ▼
    [worktree-1] [worktree-2]  ← Git worktrees for isolation
```

## Notes

- **Builders write their own unit tests** - no separate tester agent needed
- **Bug Fixer handles test gaps** - dispatched when coverage is insufficient
- **Worktrees enable parallelism** - agents don't clobber each other's work
- **Human approval required** - PRs never merge without explicit approval

