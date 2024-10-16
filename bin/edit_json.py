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
    parser.add_argument(
        "--array",
        "-a",
        action="store_true",
        default=False,
        help="Read/write a json array instead of ndjson (one json record per line)",
    )
    parser.add_argument(
        "--compact",
        "-c",
        action="store_true",
        default=False,
        help="Write each json record in a compact one-line format, "
        "otherwise it is multi-line and indented.",
    )
    parser.add_argument(
        "code",
        help="Code to execute against each record, stored in a variable called 'data'.",
    )
    args = parser.parse_args()

    input_data = (json.loads(line) for line in sys.stdin)
    if args.array:
        input_data = (elem for elem in json.loads(sys.stdin.read()))

    if args.array:
        print("[")
    first = True
    data_not_none = False
    for data in input_data:
        # transform data
        data_dict = {"data": data}
        exec(args.code, data_dict)
        data = data_dict["data"]

        # print data (possibly with a leading comma for --array mode)
        data_not_none = data is not None
        if args.array and data_not_none:
            if not first:
                print(",")
            first = False

        if data_not_none:
            print(
                json.dumps(data_dict["data"], indent=None if args.compact else 2),
                end="",
            )
    if args.array:
        print("]")


if __name__ == "__main__":
    main()
