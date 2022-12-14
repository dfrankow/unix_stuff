#!/usr/bin/env python

"""Compare a java set to a python set.

Example usage:

$ bin/compare_sets.py file1 file2

This is pretty hacky.
It doesn't deal with some punctuation, especially quotes and commas.
"""

import argparse

import re


def _match_set_with(line, regex, group):
    entries = set()
    # Note: this matches only those sets where the entries can be stripped.
    for match in re.finditer(regex, line):
        val = match.group(group).strip()
        assert val not in entries, f"repeated val {val}"
        entries.add(val)
    return entries


def _match_java_set(line):
    # Note: this matches only those sets where the entries don't
    # contain =,{, and can be stripped.
    return _match_set_with(
        line,
        '(([^={},]+)(, )?)+',
        2)


def _match_python_set(line):
    # Note: this matches only those sets where the entries don't
    # contain :,{, and can be stripped.
    #
    # HACK: this doesn't deal with commas or brackets that well
    entries = []

    leftb = line.find('[')
    rightb = line.rfind(']')

    if leftb != -1 and rightb != -1:
        the_str = line[(leftb+1):rightb]
        entries = the_str.split(", ")
        # drop quotes from the sides because we're comparing with java
        result = []
        for entry in entries:
            if entry[0] == "'" or entry[0] == '"':
                entry = entry[1:]
            if entry[-1] == "'" or entry[-1] == '"':
                entry = entry[:-1]
            result.append(entry)
        entries = result

    return set(entries)


def _match_set(line):
    set1 = _match_java_set(line)
    set2 = _match_python_set(line)
    the_set = set1
    if len(set2) > len(set1):
        the_set = set2
    return the_set


def _match_largest_set(fileh):
    the_set1 = set()
    for line in fileh:
        a_set = _match_set(line)
        if len(a_set) > len(the_set1):
            the_set1 = a_set
    return the_set1


def main():
    parser = argparse.ArgumentParser(description='Compare sets')

    parser.add_argument('file1', help='File 1')
    parser.add_argument('file2', help='File 2')
    args = parser.parse_args()

    with open(args.file1) as file1:
        the_set1 = _match_largest_set(file1)
    with open(args.file2) as file2:
        the_set2 = _match_largest_set(file2)

    print(f"{len(the_set1)} entries in set1")
    print(f"{len(the_set2)} entries in set2")

    # compare keys
    if the_set1 == the_set2:
        print("same")
    else:
        diff1 = the_set1 - the_set2
        print(f"{len(diff1)} keys in set1 not in set2: {diff1}")
        diff2 = the_set2 - the_set1
        print(f"{len(diff2)} keys in set2 not in set1: {diff2}")
    print()


if __name__ == '__main__':
    main()
