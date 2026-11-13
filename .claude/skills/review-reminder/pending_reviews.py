#!/usr/bin/env python3
"""Write an HTML list of your open PRs that wait on a requested reviewer.

Lists open PRs you authored in one GitHub organization that still have a
pending review request to a person or team, oldest first. A PR's age is the
time since you first requested a person or team, so that requests to bots
such as Copilot don't make a PR look older or count as a reviewer.

Opened in a browser and copied, the list pastes into Slack with its links
intact. Reviewers appear as "@<Slack name>" from a JSON map of GitHub login to
Slack display name; the script fails, naming each login it can't map, so that
the reminder never goes out with someone left unmentioned.
"""

import argparse
import html
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

QUERY = """
query($search: String!) {
  search(query: $search, type: ISSUE, first: 100) {
    pageInfo { hasNextPage }
    nodes { ... on PullRequest {
      number title url repository { name }
      reviewRequests(first: 50) { nodes { requestedReviewer {
        __typename ... on User { login name } ... on Team { slug name }
      } } }
      timelineItems(first: 100, itemTypes: [REVIEW_REQUESTED_EVENT]) {
        nodes { ... on ReviewRequestedEvent {
          createdAt requestedReviewer { __typename }
        } }
      }
    } }
  }
}
"""

PERSON_TYPES = {"User", "Team"}


def fetch_prs(org: str) -> list[dict]:
    search = f"org:{org} is:pr is:open author:@me"
    result = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={QUERY}", "-f", f"search={search}"],
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)["data"]["search"]
    assert not data["pageInfo"]["hasNextPage"], "more than 100 open PRs"
    return data["nodes"]


def reviewer_key(reviewer: dict) -> str:
    return reviewer["login"] if reviewer["__typename"] == "User" else reviewer["slug"]


def pending_rows(prs: list[dict]) -> list[dict]:
    rows = []
    for pr in prs:
        reviewers = [
            node["requestedReviewer"]
            for node in pr["reviewRequests"]["nodes"]
            if node["requestedReviewer"]["__typename"] in PERSON_TYPES
        ]
        if reviewers:
            requested_at = [
                event["createdAt"]
                for event in pr["timelineItems"]["nodes"]
                if event["requestedReviewer"]
                and event["requestedReviewer"]["__typename"] in PERSON_TYPES
            ]
            rows.append(
                {
                    "first_requested": min(requested_at),
                    "label": f"{pr['repository']['name']}#{pr['number']}",
                    "title": pr["title"],
                    "url": pr["url"],
                    "reviewers": reviewers,
                }
            )
    return sorted(rows, key=lambda row: row["first_requested"])


def short_date(timestamp: str) -> str:
    when = datetime.fromisoformat(timestamp)
    return f"{when:%b} {when.day}"


def render(rows: list[dict], slack_names: dict[str, str]) -> str:
    items = []
    for row in rows:
        mentions = ", ".join(
            f"@{html.escape(slack_names[reviewer_key(reviewer)])}"
            for reviewer in row["reviewers"]
        )
        items.append(
            f'<li><a href="{html.escape(row["url"])}">{html.escape(row["label"])}</a> '
            f"{html.escape(row['title'])} – {mentions}, "
            f"since {short_date(row['first_requested'])}</li>"
        )
    body = "\n".join(items)
    return (
        '<!doctype html>\n<html><head><meta charset="utf-8">'
        "<title>Review reminder</title></head>\n<body>\n"
        "<p>PRs waiting for review, oldest first:</p>\n"
        f"<ul>\n{body}\n</ul>\n</body></html>\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("org", help="GitHub organization to search")
    parser.add_argument(
        "--slack-names",
        type=Path,
        default=Path.home() / ".config/review-reminder/slack_names.json",
        help="JSON map of GitHub login (or team slug) to Slack display name",
    )
    parser.add_argument("--output", type=Path, required=True, help="HTML file to write")
    args = parser.parse_args()

    slack_names = (
        json.loads(args.slack_names.read_text()) if args.slack_names.exists() else {}
    )
    rows = pending_rows(fetch_prs(args.org))
    missing = {
        reviewer_key(reviewer): reviewer["name"]
        for row in rows
        for reviewer in row["reviewers"]
        if reviewer_key(reviewer) not in slack_names
    }
    if missing:
        for login, name in sorted(missing.items()):
            print(f"No Slack name for {login} ({name})", file=sys.stderr)
        sys.exit(f"Add them to {args.slack_names}")
    args.output.write_text(render(rows, slack_names))
    print(f"{len(rows)} PRs written to {args.output}")


if __name__ == "__main__":
    main()
