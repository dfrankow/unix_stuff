#!/usr/bin/env python3

"""Read json and make a tsv from it.

Takes the union of all columns encountered.
Reads it all into memory first.

Could use jq instead.  See https://github.com/jqlang/jq.
"""

import json
import sys
from collections import OrderedDict

SEPARATOR = "\t"

# Grab the set of fields
fields = OrderedDict()
infos = []
for line in sys.stdin:
    info = json.loads(line)
    assert type(info) == dict, f"json.loads should make a dict, but it's a {type(info)}"
    for field in info.keys():
        fields[field] = 1
    infos.append(info)

# Print the header
# fields = fields.keys().sort()
print(SEPARATOR.join(fields.keys()))

# Print the lines with fields
for info in infos:
    vals = []
    for field in fields.keys():
        val = str(info[field])
        assert SEPARATOR not in val, "value cannot contain separator"
        vals.append(val)
    print(SEPARATOR.join(vals))
