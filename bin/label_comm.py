#!/usr/bin/env python

"""Label the output lines of the 'comm' command-line utility."""

import sys

for line in sys.stdin.readlines():
    line_no_tabs = line.replace(chr(9), "").replace("\n", "")
    label = None
    if "\t" not in line:
        label = "file1"
    elif line.count("\t") == 1:
        label = "file2"
    else:
        label = "both"

    print(f"{label}: {line_no_tabs}")
