#!/usr/bin/env python3

"""Rewrap Markdown prose to a fixed width, leaving structure alone.

    rewrap_markup_doc.py --width 80 README.md docs/*.md
    rewrap_markup_doc.py --check *.md          # exit 1 if anything would change
    cat in.md | rewrap_markup_doc.py > out.md  # no paths: stdin to stdout

Refills paragraphs, list items and block quotes. Left untouched, because their
own layout carries meaning: headings of both styles, table rows, horizontal
rules, fenced and indented code, YAML front matter, link reference definitions,
and HTML blocks. Words longer than the width overhang rather than being broken,
so a long URL or a spreadsheet formula survives intact.

Only whitespace changes, which an assertion enforces on every file.
"""

import argparse
import re
import sys
import textwrap

FENCE = re.compile(r"^\s*(?P<mark>```+|~~~+)")
HEADING = re.compile(r"^\s*#")
SETEXT = re.compile(r"^\s*(=+|-+)\s*$")
TABLE_ROW = re.compile(r"^\s*\|")
RULE = re.compile(r"^\s*([-*_])(\s*\1){2,}\s*$")
LINK_DEF = re.compile(r"^\s*\[[^\]]+\]:")
HTML_BLOCK = re.compile(r"^\s*<")
LIST_ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+")
QUOTE = re.compile(r"^(\s*(?:>\s?)+)")


def is_verbatim(line: str, in_block: bool) -> bool:
    """True for lines whose own layout carries meaning.

    Indented code only counts when nothing is being filled, since a wrapped
    list item's continuation lines are indented too.

    >>> is_verbatim('| a | b |', False)
    True
    >>> is_verbatim('## Heading', False)
    True
    >>> is_verbatim('---', False)
    True
    >>> is_verbatim('[ref]: https://example.com', False)
    True
    >>> is_verbatim('    code', False)
    True
    >>> is_verbatim('    a wrapped continuation line', True)
    False
    >>> is_verbatim('ordinary prose', False)
    False
    """
    indented_code = not in_block and re.match(r"^\s{4,}\S", line)
    return bool(
        not line.strip()
        or HEADING.match(line)
        or SETEXT.match(line)
        or TABLE_ROW.match(line)
        or RULE.match(line)
        or LINK_DEF.match(line)
        or HTML_BLOCK.match(line)
        or indented_code
    )


def split_prefix(line: str) -> tuple[str, str, str]:
    """Separate a line into first-line indent, continuation indent, and text.

    A list marker or quote arrow belongs to the indent, not the text, or
    refilling would repeat it on every wrapped line.

    >>> split_prefix('plain prose')
    ('', '', 'plain prose')
    >>> split_prefix('- an item')
    ('- ', '  ', 'an item')
    >>> split_prefix('  1. nested')
    ('  1. ', '     ', 'nested')
    >>> split_prefix('> quoted')
    ('> ', '> ', 'quoted')
    >>> split_prefix('> - quoted item')
    ('> - ', '>   ', 'quoted item')
    """
    quote = QUOTE.match(line)
    lead = quote.group(1) if quote else ""
    body = line[len(lead) :]
    item = LIST_ITEM.match(body)
    if item:
        result = (
            lead + item.group(0),
            lead + " " * len(item.group(0)),
            body[item.end() :],
        )
    else:
        indent = re.match(r"\s*", body).group(0)
        result = lead + indent, lead + indent, body[len(indent) :]
    return result


def starts_block(line: str) -> bool:
    """A list item begins its own block rather than continuing the last one."""
    return bool(LIST_ITEM.match(QUOTE.sub("", line)))


def rewrap(text: str, width: int) -> str:
    """Refill prose to the width, leaving structural lines exactly as they are.

    >>> print(rewrap('one two three four', 8))
    one two
    three
    four

    A list item's continuations line up under its text, not its marker:

    >>> print(rewrap('- one two three', 9))
    - one two
      three

    Quote arrows are re-added to every line:

    >>> print(rewrap('> one two three', 9))
    > one two
    > three

    Tables, fences and their contents are untouched however long:

    >>> print(rewrap('| a very long row indeed |', 5))
    | a very long row indeed |
    >>> print(rewrap('```\\nlong line inside a fence\\n```', 5))
    ```
    long line inside a fence
    ```

    A word longer than the width overhangs rather than being broken:

    >>> print(rewrap('supercalifragilistic ok', 5))
    supercalifragilistic
    ok

    A blank line separates blocks, so consecutive paragraphs stay apart:

    >>> print(rewrap('one two\\n\\nthree four', 20))
    one two
    <BLANKLINE>
    three four

    Rewrapping is idempotent, so running it twice is running it once. This is
    what keeps the continuation indent of a wrapped list item from being read
    back as indented code:

    >>> once = rewrap('- one two three four five six seven', 12)
    >>> once == rewrap(once, 12)
    True
    """
    out: list[str] = []
    block: list[str] = []
    first_indent = ""
    rest_indent = ""
    fence_mark = ""

    def flush() -> None:
        if block:
            out.extend(
                textwrap.wrap(
                    " ".join(block),
                    width=width,
                    initial_indent=first_indent,
                    subsequent_indent=rest_indent,
                    break_long_words=False,
                    break_on_hyphens=False,
                )
            )
            block.clear()

    for line in text.split("\n"):
        fence = FENCE.match(line)
        if fence_mark:
            out.append(line)
            if fence and fence.group("mark").startswith(fence_mark):
                fence_mark = ""
        elif fence:
            flush()
            fence_mark = fence.group("mark")
            out.append(line)
        elif is_verbatim(line, bool(block)):
            flush()
            out.append(line)
        elif block and not starts_block(line):
            block.append(split_prefix(line)[2].strip())
        else:
            flush()
            first_indent, rest_indent, body = split_prefix(line)
            block.append(body.strip())

    flush()
    return "\n".join(out)


def content(text: str) -> list[str]:
    """The words, ignoring the quote arrows that refilling may redistribute.

    >>> content('> one two')
    ['one', 'two']
    >>> content('one two') == content('>one\\n>two')
    True
    """
    return text.replace(">", " ").split()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="files to rewrap in place")
    parser.add_argument("--width", type=int, default=80)
    parser.add_argument(
        "--check", action="store_true", help="report what would change, change nothing"
    )
    args = parser.parse_args()

    if not args.paths:
        original = sys.stdin.read()
        wrapped = rewrap(original, args.width)
        assert content(wrapped) == content(original), "content changed"
        sys.stdout.write(wrapped)
        return

    changed = []
    for path in args.paths:
        with open(path) as handle:
            original = handle.read()
        wrapped = rewrap(original, args.width)
        assert content(wrapped) == content(original), f"{path}: content changed"
        if wrapped != original:
            changed.append(path)
            if not args.check:
                with open(path, "w") as handle:
                    handle.write(wrapped)

    for path in changed:
        print(f"{'would rewrap' if args.check else 'rewrapped'} {path}")
    if changed and args.check:
        sys.exit(1)


if __name__ == "__main__":
    main()
