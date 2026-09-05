#!/usr/bin/env python3
"""Export plain text from Google Docs.

Input refs can be provided as:
- positional arguments
- newline-delimited refs from --input-file
- newline-delimited refs from stdin

A ref may be either:
- a full Google Docs URL, optionally with ?tab=<tab_id>
- a bare document ID

Authentication supports either:
- a Google service-account JSON key file
- an OAuth desktop-app credentials JSON file with a cached token

Recommended credentials setup for one-off or personal use:
1. Create or choose a Google Cloud project.
2. Enable the Google Docs API in that project.
3. Configure the Google Auth platform / OAuth consent screen enough to create a
   desktop client.
4. Create an OAuth client with application type "Desktop app".
5. Download the JSON file and pass it with --credentials-file.
6. On the first run, complete the browser sign-in flow. The script will cache
   the resulting OAuth token next to the credentials file unless --token-file
   is provided.

Typical first run:
    python3 google_docs_export.py \\
      --credentials-file ~/path/to/desktop_client.json \\
      --input-file doc_refs.txt \\
      --output-dir out/

Service-account setup is better for automation, but each target document must
be shared with the service account email address before the script can read it.

Python dependencies:
    python3 -m pip install --user -r requirements-google-docs-export.txt
"""

from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import parse_qs, urlparse

DOCS_READONLY_SCOPE = "https://www.googleapis.com/auth/documents.readonly"
DOC_URL_RE = re.compile(r"/document/d/([a-zA-Z0-9_-]+)")

if TYPE_CHECKING:
    from collections.abc import Iterable


def import_google_clients() -> dict[str, object]:
    try:
        request_module = importlib.import_module("google.auth.transport.requests")
        service_account_module = importlib.import_module(
            "google.oauth2.service_account"
        )
        credentials_module = importlib.import_module("google.oauth2.credentials")
        flow_module = importlib.import_module("google_auth_oauthlib.flow")
        discovery_module = importlib.import_module("googleapiclient.discovery")
        errors_module = importlib.import_module("googleapiclient.errors")
    except ImportError as import_error:
        print(
            "Missing Google client libraries. Install with:\n"
            "  python3 -m pip install --user "
            "google-api-python-client google-auth google-auth-oauthlib",
            file=sys.stderr,
        )
        raise SystemExit(2) from import_error

    return {
        "Request": request_module.Request,
        "service_account": service_account_module,
        "Credentials": credentials_module.Credentials,
        "InstalledAppFlow": flow_module.InstalledAppFlow,
        "build": discovery_module.build,
        "HttpError": errors_module.HttpError,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--credentials-file",
        required=True,
        help="Path to a Google service-account JSON or OAuth client JSON file.",
    )
    parser.add_argument(
        "--token-file",
        help=(
            "Optional OAuth token cache path. Only used for installed-app OAuth "
            "credentials. Defaults to <credentials-file>.token.json."
        ),
    )
    parser.add_argument(
        "--input-file",
        help="Optional file with one document ref per line.",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory where exported files will be written.",
    )
    parser.add_argument(
        "--all-tabs",
        action="store_true",
        help=(
            "Export every tab in each document. By default, a URL with ?tab= uses "
            "only that tab; a ref without a tab exports all tabs."
        ),
    )
    parser.add_argument(
        "--format",
        choices=("txt", "json", "both"),
        default="both",
        help="Write text files, metadata JSON files, or both.",
    )
    parser.add_argument(
        "doc_refs",
        nargs="*",
        help="Google Docs URLs or bare document IDs.",
    )
    return parser.parse_args()


def credentials_from_file(
    credentials_path: Path,
    token_path: Path | None,
    google_clients: dict[str, object],
) -> object:
    payload = json.loads(credentials_path.read_text())
    service_account = google_clients["service_account"]
    credentials_cls = google_clients["Credentials"]
    installed_app_flow = google_clients["InstalledAppFlow"]
    request_cls = google_clients["Request"]
    scopes = [DOCS_READONLY_SCOPE]

    if payload.get("type") == "service_account":
        return service_account.Credentials.from_service_account_file(
            str(credentials_path),
            scopes=scopes,
        )

    if "installed" in payload or "web" in payload:
        resolved_token_path = token_path
        if resolved_token_path is None:
            resolved_token_path = credentials_path.with_suffix(".token.json")

        creds = None
        if resolved_token_path.exists():
            creds = credentials_cls.from_authorized_user_file(
                str(resolved_token_path),
                scopes,
            )

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(request_cls())
            else:
                flow = installed_app_flow.from_client_secrets_file(
                    str(credentials_path),
                    scopes,
                )
                creds = flow.run_local_server(port=0)
            resolved_token_path.write_text(creds.to_json(), encoding="utf-8")

        return creds

    raise SystemExit(
        "Unsupported credentials JSON. Expected a service account key file or an "
        "installed-app OAuth client credentials file."
    )


def iter_input_refs(args: argparse.Namespace) -> Iterable[str]:
    for doc_ref in args.doc_refs:
        if doc_ref.strip():
            yield doc_ref.strip()

    if args.input_file:
        for line in Path(args.input_file).read_text(encoding="utf-8").splitlines():
            stripped_line = line.strip()
            if stripped_line and not stripped_line.startswith("#"):
                yield stripped_line

    if not sys.stdin.isatty():
        for line in sys.stdin:
            stripped_line = line.strip()
            if stripped_line and not stripped_line.startswith("#"):
                yield stripped_line


def parse_doc_ref(text: str) -> dict[str, str | None]:
    match = DOC_URL_RE.search(text)
    if not match:
        return {
            "document_id": text.strip(),
            "tab_id": None,
            "source_ref": text.strip(),
        }

    parsed_url = urlparse(text)
    query = parse_qs(parsed_url.query)
    tab_id = None
    if query.get("tab"):
        tab_id = query["tab"][0]

    return {
        "document_id": match.group(1),
        "tab_id": tab_id,
        "source_ref": text,
    }


def unique_doc_refs(raw_refs: Iterable[str]) -> list[dict[str, str | None]]:
    seen_keys = set()
    results = []
    for raw_ref in raw_refs:
        parsed_ref = parse_doc_ref(raw_ref)
        dedupe_key = (parsed_ref["document_id"], parsed_ref["tab_id"])
        if dedupe_key in seen_keys:
            continue
        seen_keys.add(dedupe_key)
        results.append(parsed_ref)
    return results


def flatten_tabs(tab_items: Iterable[dict]) -> list[dict]:
    flat_tabs = []
    for tab_item in tab_items:
        flat_tabs.append(tab_item)
        child_tabs = tab_item.get("childTabs", [])
        if child_tabs:
            flat_tabs.extend(flatten_tabs(child_tabs))
    return flat_tabs


def structural_elements_to_text(elements: Iterable[dict]) -> str:
    text_parts = []
    for element in elements:
        paragraph = element.get("paragraph")
        table = element.get("table")
        table_of_contents = element.get("tableOfContents")

        if paragraph:
            for paragraph_element in paragraph.get("elements", []):
                text_run = paragraph_element.get("textRun")
                if text_run:
                    text_parts.append(text_run.get("content", ""))
        elif table:
            for table_row in table.get("tableRows", []):
                text_parts.extend(
                    structural_elements_to_text(table_cell.get("content", []))
                    for table_cell in table_row.get("tableCells", [])
                )
        elif table_of_contents:
            text_parts.append(
                structural_elements_to_text(table_of_contents.get("content", []))
            )

    return "".join(text_parts)


def select_tab_exports(
    document_payload: dict,
    requested_ref: dict[str, str | None],
    export_all_tabs: bool,
) -> list[dict[str, str | None]]:
    tabs = flatten_tabs(document_payload.get("tabs", []))
    if not tabs:
        return [
            {
                "tab_id": None,
                "tab_title": document_payload.get("title", ""),
                "text": structural_elements_to_text(
                    document_payload.get("body", {}).get("content", [])
                ),
            }
        ]

    if export_all_tabs or requested_ref["tab_id"] is None:
        return [
            {
                "tab_id": tab_item.get("tabProperties", {}).get("tabId"),
                "tab_title": tab_item.get("tabProperties", {}).get("title", ""),
                "text": structural_elements_to_text(
                    tab_item.get("documentTab", {}).get("body", {}).get("content", [])
                ),
            }
            for tab_item in tabs
        ]

    requested_tab_id = requested_ref["tab_id"]
    for tab_item in tabs:
        tab_properties = tab_item.get("tabProperties", {})
        if tab_properties.get("tabId") == requested_tab_id:
            return [
                {
                    "tab_id": requested_tab_id,
                    "tab_title": tab_properties.get("title", ""),
                    "text": structural_elements_to_text(
                        tab_item.get("documentTab", {})
                        .get("body", {})
                        .get("content", [])
                    ),
                }
            ]

    raise KeyError(
        f"Tab '{requested_tab_id}' was not found in document "
        f"'{requested_ref['document_id']}'."
    )


def sanitize_filename_part(value: str | None) -> str:
    if not value:
        return "none"
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    sanitized = sanitized.strip("._")
    return sanitized or "none"


def output_base_name(
    document_id: str,
    tab_id: str | None,
    tab_title: str | None,
) -> str:
    parts = [f"doc_{sanitize_filename_part(document_id)}"]
    if tab_id:
        parts.append(f"tab_{sanitize_filename_part(tab_id)}")
    if tab_title:
        parts.append(sanitize_filename_part(tab_title))
    return "__".join(parts)


def main() -> int:
    args = parse_args()
    google_clients = import_google_clients()
    credentials_path = Path(args.credentials_file)
    token_path = Path(args.token_file) if args.token_file else None
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    parsed_refs = unique_doc_refs(iter_input_refs(args))
    if not parsed_refs:
        print("No document refs were provided.", file=sys.stderr)
        return 2

    creds = credentials_from_file(credentials_path, token_path, google_clients)
    build = google_clients["build"]
    http_error_cls = google_clients["HttpError"]
    docs_service = build("docs", "v1", credentials=creds, cache_discovery=False)

    manifest = []
    for parsed_ref in parsed_refs:
        document_id = parsed_ref["document_id"]
        try:
            document_payload = (
                docs_service.documents()
                .get(
                    documentId=document_id,
                    includeTabsContent=True,
                )
                .execute()
            )
        except http_error_cls as error:
            manifest.append(
                {
                    "document_id": document_id,
                    "tab_id": parsed_ref["tab_id"],
                    "source_ref": parsed_ref["source_ref"],
                    "error": str(error),
                }
            )
            continue

        try:
            tab_exports = select_tab_exports(
                document_payload, parsed_ref, args.all_tabs
            )
        except KeyError as error:
            manifest.append(
                {
                    "document_id": document_id,
                    "tab_id": parsed_ref["tab_id"],
                    "source_ref": parsed_ref["source_ref"],
                    "error": str(error),
                }
            )
            continue

        for tab_export in tab_exports:
            base_name = output_base_name(
                document_id,
                tab_export["tab_id"],
                tab_export["tab_title"],
            )
            metadata = {
                "document_id": document_id,
                "document_title": document_payload.get("title", ""),
                "tab_id": tab_export["tab_id"],
                "tab_title": tab_export["tab_title"],
                "source_ref": parsed_ref["source_ref"],
                "output_base_name": base_name,
                "text_length": len(tab_export["text"] or ""),
            }

            if args.format in ("txt", "both"):
                (output_dir / f"{base_name}.txt").write_text(
                    tab_export["text"] or "",
                    encoding="utf-8",
                )
            if args.format in ("json", "both"):
                (output_dir / f"{base_name}.json").write_text(
                    json.dumps(metadata, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )

            manifest.append(metadata)

    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    num_errors = sum(1 for item in manifest if "error" in item)
    num_successes = len(manifest) - num_errors
    print(
        f"Wrote manifest for {len(manifest)} item(s): "
        f"{num_successes} succeeded, {num_errors} failed."
    )
    return 0 if num_errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
