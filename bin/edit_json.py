#!/usr/bin/env python

"""Edit ndjson with python code.

Takes ndjson on stdin (one json blob per line), prints ndjson on stdout.
"""

import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Edit json from stdin, print to stdout, using python"
    )
    parser.add_argument("code")
    args = parser.parse_args()

    for line in sys.stdin:
        data = json.loads(line)
        data_dict = {"data": data}
        exec("data=" + args.code, data_dict)
        print(json.dumps(data_dict["data"]))


if __name__ == "__main__":
    main()
