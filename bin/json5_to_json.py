#!/usr/bin/env python
import json
import sys

import json5


def main():
    data = json5.load(sys.stdin)
    json.dump(data, sys.stdout)


main()
