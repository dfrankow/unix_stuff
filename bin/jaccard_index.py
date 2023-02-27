#!/usr/bin/env python

"""Measure Jaccard index of two data sources, line by line.

Ignores duplicate lines.

Example usage:

$ jaccard_index.py <(head -25 file1) <(head -40 file2)
# unique lines of file1: 25
# unique lines of file2: 40
# in intersection: 9
# in union: 56
jaccard index: 0.16071428571428573
"""
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(description='Compare dicts')

    parser.add_argument('file1', help='File 1')
    parser.add_argument('file2', help='File 2')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose')
    args = parser.parse_args()

    with open(args.file1) as the_file:
        lines1 = set(the_file.readlines())

    with open(args.file2) as the_file:
        lines2 = set(the_file.readlines())

    intersection = lines1.intersection(lines2)
    intersection_len = len(intersection)
    union = lines1.union(lines2)
    union_len = len(union)
    jaccard = intersection_len / float(union_len) if union_len else float('nan')

    print(f"# unique lines of file1: {len(lines1)}")
    print(f"# unique lines of file2: {len(lines2)}")
    print(f"# in intersection: {intersection_len}")
    print(f"# in union: {union_len}")
    print(f"jaccard index: {jaccard}")

    if args.verbose:
        print()
        # Output like comm
        lines1 = sorted(lines1)
        lines2 = sorted(lines2)
        for line in (sorted(list(intersection))
                     + sorted(list(set(lines1)-intersection))
                     + sorted(list(set(lines2)-intersection))):
            line1 = line.replace('\n', '')
            print(line1, "\t", end='')
            if line in intersection:
                print("both")
            elif line in lines1:
                print("file1")
            else:
                assert line in lines2
                print("file2")


if __name__ == '__main__':
    main()
