#!/usr/bin/env python3

"""Read a config file and use it to substitute variables on stdin.

>>> import re
>>> _substitute("hello @NAME@", {"NAME": re.compile(r"@NAME@")}, {"NAME": "world"})
'hello world'
>>> _substitute("hi @A@ and @B@", {"A": re.compile(r"@A@"), "B": re.compile(r"@B@")}, {"A": "foo", "B": "bar"})
'hi foo and bar'
"""

import argparse
import re
import sys

import yaml


def _substitute(line, patterns, config):
    for var, pattern in patterns.items():
        line = pattern.sub(str(config[var]), line)
    return line


def main():
    parser = argparse.ArgumentParser(
        description="Read a config file and use it to substitute variables on stdin."
    )
    parser.add_argument(
        "--config",
        metavar="FILE",
        help="Config file with variables",
        dest="config",
        required=True,
    )
    args = parser.parse_args()

    with open(args.config) as config_file:
        config = yaml.safe_load(config_file)

    patterns = {var: re.compile("@%s@" % var) for var in config}

    for line in sys.stdin:
        line = _substitute(line, patterns, config)
        m = re.search("@[^@]+@", line)
        if m:
            print(f"Unsubstituted pattern: {m.group(0)}", file=sys.stderr)
            sys.exit(1)
        sys.stdout.write(line)


if __name__ == "__main__":
    main()
