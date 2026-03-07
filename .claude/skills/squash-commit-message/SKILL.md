---
name: squash-commit-message
description: Generate a squash-merge commit message for GitHub by analyzing all commit messages since a base branch
---

# Squash Commit Message Generator

Generate a commit message suitable for GitHub squash-merge by analyzing all commit messages since a base branch.

## Usage
- `/squash-commit-message` - uses "main" as base branch
- `/squash-commit-message work` - uses "work" as base branch
- `/squash-commit-message stuff` - uses "stuff" as base branch

## Process
1. Get all full commit messages since the base branch: `git log --format=fuller ${base_branch}..HEAD`
2. Get the diff stats and changed files
3. Filter out commits that are internal fixes (e.g., "fix bug introduced in previous commit")
4. Synthesize remaining commits into one cohesive message following git-commit guidelines
5. Write the message to `squash-commit-message.txt` for copy/paste

## Filtering Rules
- **Skip internal fixes**: Don't include commits that fix issues introduced on the same branch
- **Skip typo/formatting fixes**: Unless they fix production issues
- **Focus on net changes**: What would a user see as the final result?
- **Combine related work**: Group commits that work toward the same goal

## Message Guidelines
Follow git-commit skill rules:
- **Be concise** - scale to total change size
- **Use bullets** for multiple changes
- **Be specific** - mention key files/classes that changed
- **No fluff** - no "comprehensive", "enhance", "streamline"
- **Factual only** - what changed, not how great it is
- **No attribution** - no "Co-Authored-By" or similar

## Output
Write the final message to `squash-commit-message.txt` in the current directory for easy copy/paste.

## Implementation

**Arguments:** The first argument is the base branch (defaults to "main" if not provided)

**Current branch:**
!`git branch --show-current`

**Available branches:**
!`git branch -a`

**Note:** After determining base branch from args, I'll run the appropriate git commands to analyze commits and generate the squash message.
