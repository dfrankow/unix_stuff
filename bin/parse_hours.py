#!/usr/bin/env python3
"""Parse journal hours and generate TSV with daily totals.

This is set up for my own peculiar way of tracking time, which is to
put something like this in my online journal:

  April 30, 2026

  Hours:

  1-3
  4:15-6:33

and then parse it out later by date.

The format is enforced rather than guessed at, so that time never goes missing
without saying so:

1. "Hours:" must be the next non-empty line after the date line. Nothing in
   between, or the date is reported as having no hours.

2. A time entry starts with its range, after an optional "- " bullet. Whatever
   follows the range is a note and is ignored, so "5:30-9  ESI 1 and 2" counts
   as 3.5 hours.

3. A range that starts but never finishes -- "11-", "4:55-", "2-?" -- is an
   error. This is the whole point: a half-written entry used to be skipped
   silently, taking the rest of the day's entries with it.

4. The first line that doesn't start with a range ends the block. Put the times
   first and the prose after, and the prose stays out of the total.

Entries before an "Invoiced through: <date>" line in the journal are frozen:
their problems collapse to a one-line count and their Hours: lines are never
rewritten, because the invoice has already gone out. One such line accumulates
per invoice, and the latest date among them wins; --since overrides them all.

Keep this script self-contained: standard library only, no imports from the
rest of unix_stuff. It gets run on machines where this repo isn't on the path.
"""

import re
from collections import namedtuple
from datetime import datetime, timedelta
from pathlib import Path


TIME_RANGE_PATTERN = re.compile(r"(\d{1,2}):?(\d{0,2})\s*[-–]\s*(\d{1,2}):?(\d{0,2})")
DATE_PATTERN = re.compile(
    r"^(January|February|March|April|May|June|July|August|September|October|November|December|"
    r"Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})"
)
SEPARATOR_PATTERN = re.compile(r"^-{10,}\s*$")
# Looser than TIME_RANGE_PATTERN: matches anything that *starts* like a time
# range, so a dangling entry such as "11-" is reported rather than silently
# treated as the end of the hours block.
TIME_ENTRY_PATTERN = re.compile(r"^\d{1,2}(?::\d{0,2})?\s*[-–]")
# An optional bullet before a time range: "- 9:25-10:18".
BULLET_PATTERN = re.compile(r"^[-–—*•]\s*")
INVOICED_THROUGH_PATTERN = re.compile(r"^Invoiced through:\s*(.+?)\s*$", re.IGNORECASE)
# All case-insensitive: a missed shift key shouldn't cost a day's hours.
HOURS_LINE_PATTERN = re.compile(r"^Hours:", re.IGNORECASE)
BARE_HOURS_PATTERN = re.compile(r"^Hours:\s*$", re.IGNORECASE)
# "Hours: 3.5", versus "Hours: 1.5 + 2.0 = 3.5" for the summed form.
STATED_TOTAL_PATTERN = re.compile(r"Hours:\s+(\d+\.?\d*)\s*$", re.IGNORECASE)
SUMMED_TOTAL_PATTERN = re.compile(r"=\s*(\d+\.?\d*)\s*$")
MAX_DAILY_HOURS = 15
# Something wrong with the journal. `date` is None when the date line itself
# could not be parsed; `line_num` is 1-based, for printing.
Problem = namedtuple("Problem", "date line_num message")


def parse_date_str(date_str):
    """Parse a journal date like 'April 30, 2026' into a datetime, or None.

    >>> parse_date_str('April 30, 2026')
    datetime.datetime(2026, 4, 30, 0, 0)
    >>> parse_date_str('Apr 30 2026')
    datetime.datetime(2026, 4, 30, 0, 0)
    >>> parse_date_str('2026-08-15')
    datetime.datetime(2026, 8, 15, 0, 0)
    >>> parse_date_str('sometime last week')
    """
    cleaned = date_str.replace(",", "")
    for fmt in ("%B %d %Y", "%b %d %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None


def invoiced_cutoff(lines):
    """Return the first date not covered by any 'Invoiced through:' line, or None.

    The journal accumulates one of these lines per invoice, so the latest date
    wins regardless of where it sits in the file. Raises ValueError on a line
    whose date can't be parsed, rather than quietly ignoring it.

    >>> invoiced_cutoff(['Invoiced through: August 15, 2026'])
    datetime.datetime(2026, 8, 16, 0, 0)
    >>> invoiced_cutoff(['Invoiced through: 2026-08-15', 'Invoiced through: 2026-09-30'])
    datetime.datetime(2026, 10, 1, 0, 0)
    >>> invoiced_cutoff(['Invoiced through: 2026-09-30', 'Invoiced through: 2026-08-15'])
    datetime.datetime(2026, 10, 1, 0, 0)
    >>> invoiced_cutoff(['April 30, 2026', 'Hours: 1.0'])
    >>> invoiced_cutoff(['Invoiced through: whenever'])
    Traceback (most recent call last):
        ...
    ValueError: cannot parse 'Invoiced through:' date on line 1: 'whenever'
    """
    latest = None
    for line_num, raw_line in enumerate(lines, start=1):
        match = INVOICED_THROUGH_PATTERN.match(raw_line.strip())
        if not match:
            continue
        date_obj = parse_date_str(match.group(1))
        if date_obj is None:
            raise ValueError(
                f"cannot parse 'Invoiced through:' date on line {line_num}: "
                f"{match.group(1)!r}"
            )
        if latest is None or date_obj > latest:
            latest = date_obj
    return None if latest is None else latest + timedelta(days=1)


def is_frozen(date_obj, cutoff):
    """True if this entry predates the cutoff, i.e. it has already been invoiced."""
    return cutoff is not None and date_obj is not None and date_obj < cutoff


def normalize_text_times(time_str):
    """Replace text times like 'noon' and 'midnight' with numbers."""
    time_str = re.sub(r"\bnoon\b", "12", time_str, flags=re.IGNORECASE)
    time_str = re.sub(r"\bmidnight\b", "0", time_str, flags=re.IGNORECASE)
    return time_str


def parse_time_range(time_str):
    """Parse a time range like '9:45-1:17' and return hours as float.

    Handles:
    - Simple hour ranges: '9-10' -> 1.0
    - Ranges with minutes: '9:45-1:17' -> 3.5 (crosses noon)
    - Text times: '11-noon' -> 1.0, 'noon-1:30' -> 1.5
    - Quarter-hour rounding: '12:40-1:13' -> 0.6 (33 min rounds to 0.55)

    >>> parse_time_range('9-10')
    1.0
    >>> parse_time_range('11-noon')
    1.0
    >>> parse_time_range('1-2')
    1.0
    >>> parse_time_range('9:45-1:17')
    3.5
    >>> parse_time_range('12:40-1:13')
    0.6
    >>> parse_time_range('noon-1:30')
    1.5
    >>> parse_time_range('11:30-noon')
    0.5
    >>> parse_time_range('midnight-1')
    1.0
    >>> parse_time_range('11:50-1')
    1.2
    >>> parse_time_range('codex resume 019e21a7-9314-78a2-bda6-e6c25d8d6f9b')
    >>> parse_time_range('11-')
    """
    time_str = time_str.strip()
    if not time_str or time_str.startswith("="):
        return None

    time_str = normalize_text_times(time_str)
    if re.search(r"[a-zA-Z]", time_str):
        return None

    match = TIME_RANGE_PATTERN.search(time_str)
    if not match:
        return None

    start_hour = int(match.group(1))
    start_min = int(match.group(2)) if match.group(2) else 0
    end_hour = int(match.group(3))
    end_min = int(match.group(4)) if match.group(4) else 0

    if start_hour > 23 or end_hour > 23:
        return None

    # Handle times that cross noon/midnight (like 9:45-1:17 means 9:45am-1:17pm)
    if end_hour < start_hour:
        end_hour += 12

    start_total = start_hour + start_min / 60
    end_total = end_hour + end_min / 60

    duration = end_total - start_total

    # Round to one decimal or quarter hours
    if abs(duration - round(duration * 4) / 4) < 0.01:  # Close to quarter hour
        return round(duration * 4) / 4
    else:
        return round(duration, 1)


def classify_range_line(line):
    """Decide what one line under a Hours: heading is.

    Returns (kind, hours), where kind is one of:
      "hours"     a time range worth counting, with its duration
      "malformed" it looks like a time range but doesn't parse, e.g. "11-"
      "end"       not part of the hours block at all

    The range has to start the line, after an optional bullet. Whatever follows
    it is a note and is ignored: entries used to be written as "5:30-9  ESI",
    and those hours count. A line that doesn't start with a range ends the
    block, which is how prose below the times stays out of the total.

    >>> classify_range_line('9-10')
    ('hours', 1.0)
    >>> classify_range_line('- 9:25-10:18')
    ('hours', 0.9)
    >>> classify_range_line('5:30-9  ESI 1 and 2')
    ('hours', 3.5)
    >>> classify_range_line('11-noon')
    ('hours', 1.0)
    >>> classify_range_line('11-')
    ('malformed', None)
    >>> classify_range_line('4:55-')
    ('malformed', None)
    >>> classify_range_line('25-26')
    ('malformed', None)
    >>> classify_range_line('codex resume 019e21a7-9314-78a2-bda6')
    ('end', None)
    >>> classify_range_line('====')
    ('end', None)
    """
    normalized = normalize_text_times(BULLET_PATTERN.sub("", line))

    match = TIME_RANGE_PATTERN.match(normalized)
    if match:
        hours = parse_time_range(match.group(0))
        return ("hours", hours) if hours is not None else ("malformed", None)

    if TIME_ENTRY_PATTERN.match(normalized):
        return ("malformed", None)

    return ("end", None)


def scan_time_ranges(lines, hours_idx):
    """Read the time ranges under the Hours: line at hours_idx.

    Returns (hours_list, malformed), where malformed holds (line_num, text) for
    lines that look like time ranges but don't parse. A malformed line does not
    end the block, so one bad entry can't hide the ones below it.

    >>> scan_time_ranges(['Hours:', '', '9-10', '11-', '1-2'], 0)
    ([1.0, 1.0], [(4, '11-')])
    >>> scan_time_ranges(['Hours:', '', '9-10', '', '', 'Talked to Bob'], 0)
    ([1.0], [])
    """
    hours_list = []
    malformed = []

    idx = hours_idx + 1

    # Skip any blank lines after Hours:
    while idx < len(lines) and not lines[idx].strip():
        idx += 1

    # Keep reading until two consecutive blank lines or a line that isn't an entry
    consecutive_blanks = 0
    while idx < len(lines):
        line = lines[idx].strip()
        if not line:
            consecutive_blanks += 1
            if consecutive_blanks >= 2:
                break
            idx += 1
            continue

        consecutive_blanks = 0
        kind, hours = classify_range_line(line)
        if kind == "end":
            break
        if kind == "hours":
            hours_list.append(hours)
        elif kind == "malformed":
            malformed.append((idx + 1, line))
        idx += 1

    return hours_list, malformed


def find_hours_line(lines, date_idx):
    """Return the index of the Hours: line belonging to the date at date_idx.

    It has to be the next non-empty line. A wider search would let a date with
    no hours block borrow the *next* entry's Hours: line and escape the check.

    >>> find_hours_line(['April 30, 2026', '', 'Hours:'], 0)
    2
    >>> find_hours_line(['April 30, 2026', '', 'Talked to Bob', 'Hours:'], 0)
    """
    idx = date_idx + 1
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    if idx < len(lines) and HOURS_LINE_PATTERN.match(lines[idx].strip()):
        return idx
    return None


def format_hours_line(hours_list):
    """Format hours list into a Hours: line with calculation."""
    if not hours_list:
        return "Hours:"

    total = sum(hours_list)
    parts = [str(h) for h in hours_list]

    if len(parts) == 1:
        return f"Hours: {parts[0]}"
    else:
        return f"Hours: {' + '.join(parts)} = {round(total, 1)}"


def parse_journal(journal_path):
    """Parse journal and return (results, lines).

    Each result is a dict describing one dated entry: its date and date line,
    the 0-based index of its Hours: line, the total hours, the individual hours
    making up that total, whether the Hours: line needs filling in, and any
    (line_num, text) lines that look like time ranges but could not be parsed.
    """
    with open(journal_path, "r") as file:
        lines = file.readlines()

    results = []
    idx = 0

    while idx < len(lines):
        date_line = lines[idx].strip()
        date_obj = parse_date_str(date_line) if DATE_PATTERN.match(date_line) else None
        hours_idx = None if date_obj is None else find_hours_line(lines, idx)

        if hours_idx is None:
            idx += 1
            continue

        hours_line = lines[hours_idx].strip()

        # Check if hours are already calculated (contains '=' or a bare number)
        already_calculated = "=" in hours_line or STATED_TOTAL_PATTERN.search(
            hours_line
        )

        hours_list, malformed = scan_time_ranges(lines, hours_idx)

        total_hours = sum(hours_list)
        if already_calculated:
            # Trust the number already on the line.
            stated = SUMMED_TOTAL_PATTERN.search(
                hours_line
            ) or STATED_TOTAL_PATTERN.search(hours_line)
            if stated:
                total_hours = float(stated.group(1))

        results.append(
            {
                "date": date_obj,
                "date_str": date_line,
                "hours_idx": hours_idx,
                "hours": total_hours,
                "hours_list": hours_list,
                # A day with an unparseable range would get a total that is
                # missing time, so leave its Hours: line alone until it's fixed.
                "needs_update": bool(
                    not already_calculated and hours_list and not malformed
                ),
                "malformed": malformed,
                "current_line": hours_line,
            }
        )

        idx = hours_idx

    return results, lines


def update_journal(output_path, pending, lines):
    """Write a copy of the journal with the pending Hours: lines filled in."""
    if not pending:
        return

    updated = list(lines)
    for result in pending:
        updated[result["hours_idx"]] = format_hours_line(result["hours_list"]) + "\n"

    with open(output_path, "w") as file:
        file.writelines(updated)


def create_tsv(results, output_path):
    """Create TSV file with date, day of week, and hours."""
    with open(output_path, "w") as file:
        file.write("Date\tDay of Week\tTotal Hours\n")

        for result in results:
            date = result["date"]
            date_str = date.strftime("%Y-%m-%d")
            day_of_week = date.strftime("%A")
            hours = result["hours"]

            file.write(f"{date_str}\t{day_of_week}\t{hours}\n")


def monthly_totals(results):
    """Sum hours by calendar month, as sorted (YYYY-MM, hours, days) tuples.

    >>> monthly_totals([
    ...     {"date": datetime(2026, 9, 1), "hours": 3.0},
    ...     {"date": datetime(2026, 8, 20), "hours": 1.5},
    ...     {"date": datetime(2026, 8, 21), "hours": 2.0},
    ... ])
    [('2026-08', 3.5, 2), ('2026-09', 3.0, 1)]
    >>> monthly_totals([])
    []
    """
    totals = {}
    for result in results:
        month = result["date"].strftime("%Y-%m")
        hours, days = totals.get(month, (0.0, 0))
        totals[month] = (hours + result["hours"], days + 1)
    return [
        (month, round(hours, 1), days)
        for month, (hours, days) in sorted(totals.items())
    ]


def collect_problems(lines, results):
    """Find structural problems in the journal, as Problem tuples.

    Reports a date line after a separator with no Hours: line below it, lines
    that look like time ranges but don't parse, bare Hours: lines with nothing
    to compute from, and days totalling more than MAX_DAILY_HOURS.
    """
    problems = []

    prev_was_separator = False
    for idx, raw_line in enumerate(lines):
        line = raw_line.strip()
        if SEPARATOR_PATTERN.match(line):
            prev_was_separator = True
            continue
        if prev_was_separator and DATE_PATTERN.match(line):
            prev_was_separator = False
            if find_hours_line(lines, idx) is None:
                problems.append(
                    Problem(parse_date_str(line), idx + 1, f"{line}: no Hours: line")
                )
        elif line:
            prev_was_separator = False

    for result in results:
        hours_line_num = result["hours_idx"] + 1
        notes = [
            (line_num, f"cannot parse time range {text!r}")
            for line_num, text in result["malformed"]
        ]

        # Only worth reporting when nothing above already explains the missing time.
        if (
            BARE_HOURS_PATTERN.match(result["current_line"])
            and not result["hours_list"]
            and not result["malformed"]
        ):
            notes.append((hours_line_num, "bare Hours: line with no time ranges"))

        if result["hours"] > MAX_DAILY_HOURS:
            notes.append((hours_line_num, f"{result['hours']} hours in one day"))

        problems.extend(
            Problem(result["date"], line_num, f"{result['date_str']}: {text}")
            for line_num, text in notes
        )

    return problems


def resolve_cutoff(args, lines, parser):
    """Work out the date before which entries are already invoiced, or None."""
    if args.since:
        cutoff = parse_date_str(args.since)
        if cutoff is None:
            parser.error(f"could not parse --since date: {args.since!r}")
        return cutoff

    try:
        return invoiced_cutoff(lines)
    except ValueError as err:
        parser.error(str(err))


def report_problems(problems, cutoff):
    """Print the problems, and return True if any of them still need fixing.

    Already-invoiced entries get a one-line count rather than a list: they are
    not going to be fixed, so the detail is just noise on every run.
    """
    invoiced = []
    current = []
    for problem in problems:
        if is_frozen(problem.date, cutoff):
            invoiced.append(problem)
        else:
            current.append(problem)

    if invoiced:
        # Enough of a pointer to go look, without listing every one.
        latest = sorted({p.date for p in invoiced if p.date}, reverse=True)[:3]
        dates = ", ".join(f"{d:%Y-%m-%d}" for d in latest)
        detail = f" (latest: {dates})" if dates else ""
        print(f"{len(invoiced)} warnings before {cutoff:%Y-%m-%d}{detail}")

    if not current:
        return False

    print(f"ERROR: {len(current)} problems:")
    for problem in sorted(current, key=lambda p: p.line_num):
        print(f"  Line {problem.line_num}: {problem.message}")
    if cutoff is None:
        print(
            "  (to grandfather entries you have already invoiced, add a line "
            "'Invoiced through: <date>' to the journal, or pass --since)"
        )
    return True


def main():
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Parse journal hours and generate TSV with daily totals."
    )
    parser.add_argument("journal", type=Path, help="Path to the journal file")
    parser.add_argument(
        "--since",
        metavar="DATE",
        help="Only fail on problems in entries on or after DATE, e.g. 2026-08-15. "
        "Defaults to the day after the journal's 'Invoiced through:' line, if it has one.",
    )
    args = parser.parse_args()

    journal_path = args.journal.resolve()
    tsv_path = journal_path.parent / "hours.tsv"
    updated_journal_path = journal_path.parent / (journal_path.name + ".1")

    results, lines = parse_journal(journal_path)
    cutoff = resolve_cutoff(args, lines, parser)

    # Entries before the cutoff have already been invoiced. The numbers that went
    # out are the numbers of record, so don't rewrite them even if they are wrong.
    pending = [
        r for r in results if r["needs_update"] and not is_frozen(r["date"], cutoff)
    ]
    update_journal(updated_journal_path, pending, lines)

    if not pending:
        print("No updates needed.")
    else:
        print(f"Updated Hours: for {len(pending)} dates:")
        for result in pending:
            print(f"  {result['date_str']}: {result['hours']}")
        print(f"diff {journal_path} {updated_journal_path}")
        print(f"mv {updated_journal_path} {journal_path}")

    create_tsv(results, tsv_path)
    print(f"{tsv_path}: {len(results)} entries")

    # Invoicing is monthly, so only the not-yet-invoiced months are worth totalling.
    if cutoff is not None:
        print(f"Entries before {cutoff:%Y-%m-%d} are already invoiced.")
    uninvoiced = [r for r in results if not is_frozen(r["date"], cutoff)]
    for month, hours, days in monthly_totals(uninvoiced):
        print(f"  {month}: {hours} hours over {days} day{'s' if days != 1 else ''}")

    if report_problems(collect_problems(lines, results), cutoff):
        sys.exit(1)


if __name__ == "__main__":
    main()
