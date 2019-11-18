#!/usr/bin/env python3

"""Use Python's csv package to translate CSV files to tab-separated newline-delimited.

Removes tabs and newlines.
"""
import csv
import re
import sys

# Python 3.7 and newer
# This encoding is more tolerant than utf-8:
# sys.stdin.reconfigure(encoding='cp1252')

# See also https://stackoverflow.com/a/15063941/34935
csv.field_size_limit(sys.maxsize)

csvreader = csv.reader(sys.stdin, delimiter=',')
for row in csvreader:
    for idx in range(len(row)):
        row[idx] = re.sub(r'[\t\r\n]', ' ', row[idx])
    print('\t'.join(row))
