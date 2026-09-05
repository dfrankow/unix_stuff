---
name: review-pr
description: Review someone else's pull request - gather its current state, read the diff against Dan's correctness and style criteria, and report findings in his preferred shape. Use when asked to review a PR by number, URL, or branch.
---

# Reviewing someone else's pull request

Reviewing another person's PR, not your own uncommitted work (that is `/lime:local-review`).
The author owns the fix; you own naming the problem clearly and being right about it.

## 1. Get the current state before saying anything about it

Never report a PR's review state from memory or from earlier in the session — Dan approves,
comments and merges between turns.

```bash
gh pr view <n> --json number,title,state,isDraft,author,baseRefName,headRefName,reviewDecision,reviews,mergeable,additions,deletions,changedFiles,updatedAt,body
gh api repos/limebike/<repo>/pulls/<n>/comments   # inline threads
```

`reviewDecision` only ever reads APPROVED, CHANGES_REQUESTED or REVIEW_REQUIRED. A comment-only
review leaves it at REVIEW_REQUIRED, so it never means "nobody has reviewed this" — read the
`reviews` array and the inline comments to answer that.

Read existing review threads before writing your own points, so you don't repeat a point someone
already made or one the author already answered.

Only look at repos under `limebike`.

## 2. Read the diff, and check the description against it

```bash
gh pr diff <n>
gh pr view <n> --json commits
```

The PR body is a claim, not evidence. Where it says a change is safe because of something
elsewhere in the system, go read that code. An unverified "because" in a PR body is the same
defect as one in a comment: it is exactly where a reviewer stops checking.

For a stacked branch, review only what this PR adds — diff against its actual base, not main.

Do not run the test suite to review. CI runs on push and covers it. If you do want a local run,
background it and carry on.

Judge a wrong description by whether someone will act on it. A runbook that tells an operator to
run the wrong thing is blocking; a stale sentence about a test is not, since whoever merges edits
the squash box and the body never reaches main's history. Say when a body is too long for a
person to read, and propose the 3-8 line squash message.

## 3. What to look for, in priority order

**Correctness first.** Everything below is secondary to whether the code does what it says.

- Does the change actually produce the described behavior, on the paths the author names *and*
  the ones they don't? Migrations and data backfills: is it idempotent, reversible, and safe to
  run while the old image is still writing?
- Silent wrong answers beat loud failures for damage: a fallback to a less reliable data source,
  a swallowed exception, a default that hides a missing value.
- Concurrency and ordering: what runs between the migration and the deploy, between two tasks,
  between a read and its write.
- Tests: does a bug fix have a regression test that fails without the change? Are the new tests
  pinning the invariant the change rests on, or just restating the implementation?
  Tests mirror source structure — `bar/foo.py` → `tests/bar/test_foo.py`.

**Then the house style** (from `agent_advice.md` and the project `CLAUDE.md`) — these are real
findings, not nits, because they are settled decisions:

- `except Exception` and other broad catches. Let it raise, or use an `if`, or catch narrowly.
- New `# noqa` / `pylint: disable` without discussion.
- Default parameters on inner functions; defaults belong at the argparse/config layer.
- A literal value copied where an enum or constant symbol exists.
- One-letter variable names; `sys.path` edits; imports inside functions.
- `hasattr` — usually a parent class depending on its children.
- Comments that describe today's task, leak implementation details, or carry a magic number that
  will go stale. Docstrings that will not read correctly in six months.
- New JavaScript where server-side rendering or htmx would do.
- More code than the change needs, or a new helper where an existing one fits.

**Then everything else** — naming, ordering, readability — only where it genuinely impairs
understanding.

## 4. How to write the findings

- Every point opens with **one sentence naming the problem**. Suggest a fix after that if you
  have a good one; never lead with the action or bold it as the ask. Solving it is the author's
  problem, and leading with a prescribed fix skips past whether they agree the problem is real.
- Say plainly which points are blocking and which are not. Do not inflate a nit into a blocker;
  do not soften a real defect into a question.
- Anchor each point to `file:line`.
- Don't claim more than you checked. "I did not verify X" is a fine thing to write.
- Note what is genuinely good, briefly, where it is worth noting — not as padding.
- If you found nothing blocking, say so in a line rather than manufacturing findings.

**Under 10 lines, always.** The whole review, not each point. If you cannot fit a point in a
line it is usually two points, or one you have not finished thinking through. Detail goes in the
diff, which the author is already reading.

Shape: a Blocking header and a Non-blocking header, then a closing line saying what you verified.
Drop a header that has nothing under it.

Number the findings, in one sequence that runs across both headers — blocking 1, non-blocking 2
and 3, not two lists that each restart at 1. The number is how the author refers to a point in
their reply, so it has to be unique in the review.

**Formatting of review prose:**

- No inline backticks in the prose. Nearly every noun is code, and a paragraph of backticks is
  unreadable. Fenced blocks are fine, and are where a suggestion belongs.
- No line-prefix markers (`> `, `| `) on text Dan may want to copy — the prefix comes along
  with the selection.
- Don't wrap lines; GitHub reflows.

## 5. Posting

Print the review in the terminal first. Show the exact text before posting anything to GitHub,
and post only when Dan says to — a review is outward-facing and there is no clean undo.

Keep the terminal summary to a few lines, not a categorized breakdown.
