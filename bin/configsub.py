#!/usr/bin/env python

import re
import sys
import yaml

"""Read a config file and use it to substitute variables on stdin"""

import argparse

parser = argparse.ArgumentParser(
    description='Read a config file and use it to substitute variables on stdin.')
parser.add_argument('--config', metavar='FILE',
                    help='Config file with variables', dest='config',
                    required=True)
args = parser.parse_args()

# Read the YAML config file
# TODO(dan): Figure out what to do with nested data structures (error out?)
config = {}
with open(args.config) as config_file:
    config = yaml.load(config_file)

# Precompute the regex patterns, why not
config_pattern = {}
for var, value in config.iteritems():
    config_pattern[var] = re.compile('@%s@' % var)

# Substitute the pattern on stdin
for line in sys.stdin.readlines():
    for var, value in config.iteritems():
        pattern = config_pattern[var]
        line = pattern.sub(str(value), line)
    sys.stdout.write(line)
