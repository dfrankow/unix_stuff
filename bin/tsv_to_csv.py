#!/usr/bin/env python3

"""Use Python's csv package to translate TSV to CSV"""
import csv
import sys

# Python 3.7 and newer
# This encoding is more tolerant than utf-8:
# sys.stdin.reconfigure(encoding='cp1252')

# See also https://stackoverflow.com/a/15063941
csv.field_size_limit(sys.maxsize)

csvreader = csv.reader(sys.stdin, delimiter="\t")
csvwriter = csv.writer(sys.stdout, quoting=csv.QUOTE_MINIMAL)
for row in csvreader:
    csvwriter.writerow(row)
