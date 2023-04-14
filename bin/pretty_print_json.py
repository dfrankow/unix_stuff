#!/usr/bin/env python3

import argparse
import json
import sys

parser = argparse.ArgumentParser(
    description='Read a file and pretty-print the json')
parser.add_argument('--whole-file', action='store_true',
                    help='If given, grab the whole file as one JSON blog')
parser.add_argument('--sort-keys', action=argparse.BooleanOptionalAction,
                    help='sort the keys',
                    default=False)
parser.add_argument('--no-indent', action='store_true',
                    help="If True, use the most compact representation",
                    default=False)
args = parser.parse_args()

indent = None if args.no_indent else 2

if args.whole_file:
    the_obj = json.loads(sys.stdin.read())
    print(json.dumps(the_obj, sort_keys = args.sort_keys,
                     indent=indent, ensure_ascii=False))
else:
    for line in sys.stdin:
        the_obj = json.loads(line)
        print(json.dumps(the_obj, sort_keys = args.sort_keys,
                         indent=indent, ensure_ascii=False))
