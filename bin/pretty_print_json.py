#!/usr/bin/env python2.7

import json
import sys

for line in sys.stdin:
    the_obj = json.loads(line)
    print json.dumps(the_obj, sort_keys = True, indent=2)
