#!/usr/bin/env python3

import argparse
import json
import sys

parser = argparse.ArgumentParser(
    description='Read a file and pretty-print the json')
parser.add_argument('--whole-file', action='store_true',
                    help='If given, grab the whole file as one JSON blog',
                    dest='whole_file')
args = parser.parse_args()

if args.whole_file:
    the_obj = json.loads(sys.stdin.read())
    print(json.dumps(the_obj, sort_keys = True, indent=2, ensure_ascii=False))
else:
    for line in sys.stdin:
        the_obj = json.loads(line)
        print(json.dumps(the_obj, sort_keys = True, indent=2, ensure_ascii=False))
