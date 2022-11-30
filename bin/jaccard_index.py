#!/usr/bin/env python

"""Measure Jaccard index of two data sources, line by line.

Ignores duplicate lines.

Example usage:

$ jaccard_index.py <(head -50 file1) <(head -50 file2)
# unique lines of file1: 25
# unique lines of file2: 40
# in intersection: 9
# in union: 56
jaccard index: 0.16071428571428573
"""

import sys


def main():
    if len(sys.argv) != 3:
        print("Usage: {sys.argv[0]} file1 file2")
        sys.exit(1)

    with open(sys.argv[1]) as the_file:
        lines1 = set(the_file.readlines())

    with open(sys.argv[2]) as the_file:
        lines2 = set(the_file.readlines())

    intersection = len(lines1.intersection(lines2))
    union = len(lines1.union(lines2))
    jaccard = intersection / float(union) if union else float('nan')

    print(f"# unique lines of file1: {len(lines1)}")
    print(f"# unique lines of file2: {len(lines2)}")
    print(f"# in intersection: {intersection}")
    print(f"# in union: {union}")
    print(f"jaccard index: {jaccard}")


main()
