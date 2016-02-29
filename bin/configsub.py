#!/usr/bin/env python

import re
import sys

"""Read a config file and use it to substitute variables on stdin"""

import argparse

parser = argparse.ArgumentParser(
description='Read a config file and use it to substitute variables on stdin.')
parser.add_argument('--config', metavar='FILE',
                   help='Config file with variables', dest='config',
                    required=True)
args = parser.parse_args()

print args.config

# Read the config file: lines of the form var=value
config = {}
config_pattern = {}
for line in open(args.config).readlines():
    line = line.rstrip('\n\r')
    # skip empty lines and comments
    if not line or line.startswith('#'):
        continue

    # Separate on first equals sign
    var, value = line.split('=', 1)

    config[var] = value
    config_pattern[var] = re.compile('@%s@' % var)

# Substitute the pattern on stdin
for line in sys.stdin.readlines():
    for var, value in config.iteritems():
        pattern = config_pattern[var]
        line = pattern.sub(value, line)
    sys.stdout.write(line)
