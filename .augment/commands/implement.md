---
description: Start feature development on a GitHub issue using the Foreman workflow
argument-hint: <issue-number> [branch-name]
model: claude-opus-4-5
---

Activate the foreman agent to implement GyesitHub issue $ARGUMENTS.

If you do not recieve a issue number or numbers, then look at the github issue list and present the user with
a list of issues with suggestions as to what could be implemented next. then pass this to the foreman agent.

Follow the complete Foreman workflow:

1. Fetch and analyze the specified issue from GitHub
2. Review the codebase to understand architecture and patterns
3. Create an implementation plan with parallel component groups
4. Create feature branch using standard naming: `feature/issue-{number}-{slug}`
5. Dispatch parallel builder agents using git worktrees for isolation
6. Verify quality after all builders complete (coverage, linting, tests)
7. Update documentation in parallel with quality verification
8. Create a comprehensive PR and hand off to PR Review Boss

Keep me informed of progress. Ask clarifying questions if the issue requirements are unclear.

