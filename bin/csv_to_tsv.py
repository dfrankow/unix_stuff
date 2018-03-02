#!/usr/bin/env python

"""Use Python's csv package to translate CSV files to tab-separated newline-delimited.

Removes tabs and newlines.
"""
import csv
import re
import sys

csvreader = csv.reader(sys.stdin, delimiter=',')
for row in csvreader:
    for idx in xrange(len(row)):
        row[idx] = re.sub(r'[\t\r\n]', ' ', row[idx])
    print '\t'.join(row)
