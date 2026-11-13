---
name: review-reminder
description: Build a Slack-pasteable reminder listing the user's open PRs that wait on requested reviewers, oldest first, with each reviewer @-mentioned. Use when asked to remind people to review the user's PRs, or for /review-reminder.
---

# Review reminder

Lists the user's open PRs in one GitHub organization that still have a pending
review request, oldest first by when a reviewer was first requested, as an HTML
page whose links survive copy and paste into Slack.

## Usage

- `/review-reminder <org>` - the GitHub organization to search
- `/review-reminder` - the owner of the current repo's `origin`

## Process

1. Run the script, with `gh` authenticated for the organization (in a repo that
   loads its token through direnv, prefix with `direnv exec .`):
   `.claude/skills/review-reminder/pending_reviews.py <org> --output <scratchpad>/review-reminder.html`
   (the path is relative to this skill's directory).
2. If it names logins with no Slack name, ask the user for each Slack display
   name, add them to the map file it names, and run it again.
3. `open` the HTML file and tell the user to select all, copy and paste into
   Slack. Pasted "@Name" text may stay plain text rather than a mention; if so,
   the user retypes each @ so Slack's autocomplete picks the person.

## What counts

- Only reviewers whose request is still pending. A reviewer who has reviewed
  drops off GitHub's request list until re-requested, so an approved PR or one
  with changes requested is left out.
- Requests to bots (Copilot) neither count as a reviewer nor set the age.
