#!/usr/bin/env python3
"""Parse journal hours and generate TSV with daily totals.

This is set up for my own peculiar way of tracking time, which is to
put something like this in my online journal:

  April 30, 2026

  Hours:

  1-3
  4:15-6:33

and then parse it out later by date
"""

import re
from datetime import datetime
from pathlib import Path


TIME_RANGE_PATTERN = re.compile(r"(\d{1,2}):?(\d{0,2})\s*[-–]\s*(\d{1,2}):?(\d{0,2})")


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
    """
    time_str = time_str.strip()
    if not time_str or time_str.startswith("="):
        return None

    time_str = normalize_text_times(time_str)

    # Handle ranges like "9:45-1:17" or "12:35-5:44" or "11-12" (after substitution)
    match = TIME_RANGE_PATTERN.search(time_str)
    if not match:
        return None

    start_hour = int(match.group(1))
    start_min = int(match.group(2)) if match.group(2) else 0
    end_hour = int(match.group(3))
    end_min = int(match.group(4)) if match.group(4) else 0

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
    """Parse journal and return list of (date_str, line_num, hours_total, needs_update, time_ranges)."""
    with open(journal_path, "r") as file:
        lines = file.readlines()

    results = []
    idx = 0

    while idx < len(lines):
        line = lines[idx].strip()

        # Match date lines like "April 30, 2026" or "Apr 30, 2026"
        date_match = re.match(
            r"^(January|February|March|April|May|June|July|August|September|October|November|December|"
            r"Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})",
            line,
        )

        if date_match:
            date_str = line
            # date_line_num = idx

            # Parse the date
            try:
                date_obj = datetime.strptime(date_str.replace(",", ""), "%B %d %Y")
            except ValueError:
                try:
                    date_obj = datetime.strptime(date_str.replace(",", ""), "%b %d %Y")
                except ValueError:
                    idx += 1
                    continue

            # Look for "Hours:" in the next few lines
            hours_idx = None
            for offset in range(1, 10):
                if idx + offset >= len(lines):
                    break
                if lines[idx + offset].strip().startswith("Hours:"):
                    hours_idx = idx + offset
                    break

            if hours_idx is not None:
                hours_line = lines[hours_idx].strip()

                # Check if hours are already calculated (contains '=' or a bare number)
                already_calculated = "=" in hours_line or re.search(
                    r"Hours:\s+\d+\.?\d*\s*$", hours_line
                )

                # Extract time ranges from following lines
                time_ranges = []
                range_idx = hours_idx + 1

                # Skip any blank lines after Hours:
                while range_idx < len(lines) and not lines[range_idx].strip():
                    range_idx += 1

                # Keep reading time ranges until we hit two consecutive blank lines or a non-time-range line
                consecutive_blanks = 0
                while range_idx < len(lines):
                    range_line = lines[range_idx].strip()
                    if not range_line:
                        consecutive_blanks += 1
                        if consecutive_blanks >= 2:
                            break
                        range_idx += 1
                        continue

                    consecutive_blanks = 0

                    # Check if this looks like a time range (after substituting text times)
                    if TIME_RANGE_PATTERN.search(normalize_text_times(range_line)):
                        time_ranges.append(range_line)
                        range_idx += 1
                    else:
                        break

                # Calculate hours from time ranges
                hours_list = []
                for time_range in time_ranges:
                    hours = parse_time_range(time_range)
                    if hours is not None:
                        hours_list.append(hours)

                # If already calculated, extract the total from the Hours: line
                if already_calculated:
                    # Try to extract number after '=' for lines like "Hours: 1.5 + 2.0 = 3.5"
                    equals_match = re.search(r"=\s*(\d+\.?\d*)\s*$", hours_line)
                    if equals_match:
                        total_hours = float(equals_match.group(1))
                    else:
                        # Try to extract bare number for lines like "Hours: 3.5"
                        bare_match = re.search(r"Hours:\s+(\d+\.?\d*)\s*$", hours_line)
                        if bare_match:
                            total_hours = float(bare_match.group(1))
                        else:
                            total_hours = sum(hours_list) if hours_list else 0
                else:
                    total_hours = sum(hours_list) if hours_list else 0

                needs_update = not already_calculated and hours_list

                results.append(
                    {
                        "date": date_obj,
                        "date_str": date_str,
                        "line_num": hours_idx,
                        "hours": total_hours,
                        "needs_update": needs_update,
                        "hours_list": hours_list,
                        "time_ranges": time_ranges,
                        "current_line": hours_line,
                    }
                )

            idx = hours_idx if hours_idx else idx + 1
        else:
            idx += 1

    return results, lines


def update_journal(output_path, results, lines):
    """Create updated journal file with calculated hours."""
    updates_made = 0

    for result in results:
        if result["needs_update"]:
            line_num = result["line_num"]
            new_line = format_hours_line(result["hours_list"])
            print(f"\nLine {line_num + 1} ({result['date_str']}):")
            print(f"  Current: {result['current_line']}")
            print(f"  New:     {new_line}")
            lines[line_num] = new_line + "\n"
            updates_made += 1

    if updates_made > 0:
        with open(output_path, "w") as file:
            file.writelines(lines)

    return updates_made


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


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Parse journal hours and generate TSV with daily totals."
    )
    parser.add_argument("journal", type=Path, help="Path to the journal file")
    args = parser.parse_args()

    journal_path = args.journal.resolve()
    tsv_path = journal_path.parent / "hours.tsv"
    updated_journal_path = journal_path.parent / (journal_path.name + ".1")

    # Parse journal
    print(f"Parsing {journal_path}...")
    results, lines = parse_journal(journal_path)

    print(f"Found {len(results)} date entries with Hours:")

    # Show all parsed dates and hours
    print("\n" + "=" * 60)
    print("Parsed dates and hours:")
    print("=" * 60)
    for result in results:
        date_str = result["date"].strftime("%Y-%m-%d %A")
        hours = result["hours"]
        update_marker = " [NEEDS UPDATE]" if result["needs_update"] else ""
        print(f"{date_str}\t{hours}{update_marker}")

    # Show what will be updated and create new journal
    print("\n" + "=" * 60)
    print("Updates to be made:")
    print("=" * 60)
    updates = update_journal(updated_journal_path, results, lines)

    if updates == 0:
        print("No updates needed - all Hours: lines already have totals")
        print("\nNot creating updated journal since no changes needed")
    else:
        print(f"\nCreated {updated_journal_path} with {updates} updated Hours: lines")

        # Verify file sizes
        orig_size = journal_path.stat().st_size
        new_size = updated_journal_path.stat().st_size
        print(f"\nOriginal journal: {orig_size:,} bytes")
        print(f"Updated journal:  {new_size:,} bytes")

        if new_size < orig_size:
            print(
                f"WARNING: Updated journal is smaller by {orig_size - new_size:,} bytes!"
            )

        print(f"\nTo review changes: diff {journal_path} {updated_journal_path}")
        print(f"To apply changes:  mv {updated_journal_path} {journal_path}")

    # Create TSV
    create_tsv(results, tsv_path)
    print(f"\nCreated {tsv_path}")
    print(f"Total entries: {len(results)}")
    print(f"Total hours: {sum(r['hours'] for r in results)}")


if __name__ == "__main__":
    main()
