---
name: git-commit-generator
description: ALWAYS use this skill when committing code. Triggers on any commit request including "commit", "git commit", "commit your code", "commit this", "make a commit", etc.
---

# Git Commit Rules

### 1. Headline Format
- Use the **imperative mood** (e.g., "Add feature" or "Fix bug").
- Do not use prefixes like "feat:" or "fix:".

### 2. Length Constraints (Strict)
- **If code diff is <50 lines:** Limit message to **1-2 lines total**.
- **If code diff is 50-200 lines:** Limit message to **maximum 5 lines**.
- **If code diff is >200 lines:** Limit message to **maximum 10 lines**.

### 3. Content & Style
- **Focus:** Explain the "what" and "why." Omit the "how."
- **Specificity:** Reference specific filenames and functions. **Do not** reference line numbers.
- **Formatting:** Use **bullet points** for the body. Avoid walls of text.
- **Cleanliness:** No "Co-authored-by" statements or metadata footers.
- **Completeness:** Look over all changes since the last commit, don't just focus on what you remember from the last few prompts.
- Don't say how many test are passing.  We always require them all to pass.
- **Brevity:** Try to keep the text short.

### git usage
- NEVER "git add -A" or "git add ." since that might add too many files
- Do "git commit ." or "git add -u" instead of always adding each file separately.  You only have to "git add" untracked files that should be in the commit.
