---
description: Create a new release with version bump, changelog, and git tag
argument-hint: <version>
model: claude-sonnet-4-5
---

Activate the release-manager agent to create release version $ARGUMENTS.

Follow the release workflow:

1. Verify main branch is clean and up to date
2. Update version in `src/pylon/_version.py`
3. Regenerate lock file with `uv lock`
4. Update CHANGELOG.md with release notes
5. Commit changes with message `chore: bump version to {version} for release`
6. Create annotated tag `v{version}`
7. Push to origin (commit and tag)
8. Create GitHub release with changelog excerpt

Ask me to confirm before pushing to remote.

