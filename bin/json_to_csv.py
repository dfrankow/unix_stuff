#!/usr/bin/env python3

"""Read json and make a tsv from it.

Takes the union of all columns encountered.
Reads it all into memory first.
"""

from collections import OrderedDict
import csv
import json
import sys

# SEPARATOR = '\t'
SEPARATOR = ','

# Grab the set of fields
fields = OrderedDict()
infos = []
for line in sys.stdin:
    info = json.loads(line)
    assert type(info) == dict, "json.loads should make a dict"
    for field in info.keys():
        fields[field]=1
    infos.append(info)

# Print the header
print(SEPARATOR.join(fields.keys()))

# Print the lines with fields
writer = csv.writer(sys.stdout, delimiter=',',
                    quotechar='"', quoting=csv.QUOTE_MINIMAL)

for info in infos:
    writer.writerow([info[field] for field in fields.keys()])
