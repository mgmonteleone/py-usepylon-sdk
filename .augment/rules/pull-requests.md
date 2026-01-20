---
type: "agent_requested"
description: "Pull request creation, code review workflow, and merge process"
---

# Pull Request and Code Review Standards

## When to Create Pull Requests

**Create PRs before committing MINOR and MAJOR version changes.**

| Version Change | PR Required | Review Required |
|----------------|-------------|-----------------|
| PATCH (0.0.X)  | Optional    | Optional        |
| MINOR (0.X.0)  | **Required**| Human + AI      |
| MAJOR (X.0.0)  | **Required**| Human + AI      |

## PR Creation Workflow

### 1. Pre-PR Checklist

Before creating a PR, verify:

- [ ] All tests pass: `pytest`
- [ ] Code quality checks pass: `ruff check . && flake8 .`
- [ ] Code is formatted: `ruff format .`
- [ ] No secrets or PII in code
- [ ] Documentation is updated
- [ ] Version is bumped appropriately
- [ ] CHANGELOG is updated (for MINOR/MAJOR)

### 2. Branch Preparation

```bash
# Ensure branch is up to date with main
git fetch origin
git rebase origin/main

# Verify all checks pass
pytest
ruff check .
```

### 3. PR Title Format

Follow conventional commit format:

```
<type>(<scope>): <description>
```

Examples:
- `feat(auth): add OAuth2 authentication support`
- `fix(api): handle rate limiting errors gracefully`
- `refactor(models): consolidate user data models`

### 4. PR Description Template

```markdown
## Summary

Brief description of what this PR does and why.

## Changes

- List of specific changes made
- Breaking changes (if any)
- New dependencies added

## Testing

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing performed

## Screenshots (if applicable)

## Checklist

- [ ] Tests pass
- [ ] Linting passes
- [ ] Documentation updated
- [ ] Version bumped
- [ ] No secrets committed
```

## Review Process

### Human Review

Human reviewers should verify:

1. **Business Logic**: Does the code do what it's supposed to?
2. **Architecture**: Does this fit well with existing patterns?
3. **Security**: Are there any security concerns?
4. **User Impact**: How does this affect end users?

### AI Review

AI reviewers should verify:

1. **Code Quality**: Follows project standards
2. **Test Coverage**: Adequate tests for new functionality
3. **Documentation**: Clear and complete
4. **Best Practices**: OOP principles, DRY, SOLID
5. **Dependencies**: Latest stable versions used

## PR Review Checklist

### For Reviewers

- [ ] Code follows project style guidelines
- [ ] No obvious bugs or logic errors
- [ ] Error handling is appropriate
- [ ] No security vulnerabilities introduced
- [ ] Tests are meaningful (not trivially passing)
- [ ] Documentation is clear and accurate
- [ ] No unnecessary complexity
- [ ] Breaking changes are documented

### Common Review Feedback

When reviewing, look for:

- Unused imports or variables
- Missing type hints
- Inadequate error handling
- Hardcoded values that should be configurable
- Missing or weak tests
- Performance concerns
- Security issues (SQL injection, XSS, etc.)

## Merging Strategy

### Merge Requirements

- At least 1 human approval
- All CI checks pass
- No unresolved conversations
- Branch is up to date with target

### Merge Method

- **Squash and merge**: For feature branches (clean history)
- **Merge commit**: For release branches (preserve history)
- **Rebase and merge**: When linear history is preferred

## Post-Merge Actions

After PR is merged:

1. Delete the feature branch
2. Tag the release (for version bumps)
3. Deploy if applicable
4. Update related issues/tickets

```bash
# Tag after merge (on main branch)
git checkout main
git pull origin main
git tag -a v1.2.0 -m "Release v1.2.0: Feature description"
git push origin v1.2.0
```

## Handling PR Feedback

When feedback is received:

1. Respond to all comments
2. Make requested changes
3. Re-request review after updates
4. Don't force-push after review has started (unless agreed)

## Agent Code Review Comment Handling

**CRITICAL: Agents MUST follow this workflow for every code review comment.**

### Step 1: React to Each Comment

For **every** code review comment found on a PR:

- **👍 (thumbs up)**: If the comment is valid and will be addressed
- **👎 (thumbs down)**: If the comment is not valid or doesn't apply

Use the GitHub Reactions API:
```
POST /repos/{owner}/{repo}/pulls/comments/{comment_id}/reactions
{"content": "+1"}  # or "-1" for thumbs down
```

### Step 2: Reply to Each Comment

**ALWAYS reply to every code review comment** with an explanation:

**For valid comments (👍):**
```markdown
✅ **Fixed in commit `abc1234`**

[Brief explanation of how the issue was addressed]

- Changed X to Y
- Updated the logic to handle Z
- Added test coverage for edge case
```

**For invalid comments (👎):**
```markdown
❌ **Not applicable**

[Clear explanation of why the comment doesn't apply]

- The suggested change would break X
- This is intentional because Y
- The API actually returns Z, not what was assumed
```

Use the GitHub API to reply:
```
POST /repos/{owner}/{repo}/pulls/comments/{comment_id}/replies
{"body": "Your response here"}
```

### Step 3: Resolve the Comment

After addressing and replying to a comment, **resolve the conversation** to indicate it's been handled.

**Note:** GitHub API doesn't have a direct "resolve" endpoint. Instead:
1. Create a review that marks conversations as resolved, OR
2. The reply itself serves as acknowledgment (reviewer can resolve)

For automated resolution, use:
```
POST /repos/{owner}/{repo}/pulls/{pull_number}/reviews
{
  "event": "COMMENT",
  "body": "All review comments have been addressed.",
  "comments": []
}
```

### Complete Workflow Example

```python
# Pseudocode for agent review comment handling
for comment in get_review_comments(pr_number):
    # Step 1: Evaluate and react
    if is_valid_comment(comment):
        add_reaction(comment.id, "+1")

        # Fix the issue
        fix_result = fix_issue(comment)

        # Step 2: Reply with fix details
        reply_to_comment(comment.id, f"""
✅ **Fixed in commit `{fix_result.commit_sha}`**

{fix_result.description}
        """)
    else:
        add_reaction(comment.id, "-1")

        # Step 2: Reply with explanation
        reply_to_comment(comment.id, f"""
❌ **Not applicable**

{get_rejection_reason(comment)}
        """)

    # Step 3: Mark as resolved (via PR summary comment)

# Final summary comment
add_pr_comment(pr_number, """
## Review Comments Summary

| Comment | Status | Action |
|---------|--------|--------|
| Pagination inconsistency | ✅ Fixed | Commit abc1234 |
| Missing tests | ✅ Fixed | Commit def5678 |
| Style suggestion | ❌ N/A | Intentional design |

All review comments have been addressed.
""")
```

### Priority Classification

When processing review comments, classify by priority:

| Priority | Reaction | Action Required |
|----------|----------|-----------------|
| **CRITICAL** | 👍 | Fix immediately, blocks merge |
| **HIGH** | 👍 | Must fix before merge |
| **MEDIUM** | 👍 | Should fix, may defer with issue |
| **LOW** | 👎 or 👍 | Nice-to-have, create issue if skipped |

### GitHub API Reference

```bash
# List review comments
GET /repos/{owner}/{repo}/pulls/{pull_number}/comments

# Add reaction to comment
POST /repos/{owner}/{repo}/pulls/comments/{comment_id}/reactions
Content-Type: application/json
{"content": "+1"}  # Options: +1, -1, laugh, confused, heart, hooray, rocket, eyes

# Reply to a review comment
POST /repos/{owner}/{repo}/pulls/{pull_number}/comments
{
  "body": "Reply text",
  "in_reply_to": {comment_id}
}
```

## Emergency Hotfixes

For critical production issues:

1. Create `hotfix/` branch from main
2. Minimal changes only
3. Fast-track review (single approval)
4. Merge and tag as PATCH version
5. Create follow-up PR for comprehensive fix if needed