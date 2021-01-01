#!/usr/bin/env python

# from https://stackoverflow.com/a/20420243
import sys
import yaml

the_file=sys.stdin
if (len(sys.argv) == 2):
    the_file=open(sys.argv[1])

yaml.safe_load(the_file)

print("ok")

