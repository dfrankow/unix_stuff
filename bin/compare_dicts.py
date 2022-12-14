#!/usr/bin/env python

"""Compare a java map to a python dict.

Example usage:

$ bin/compare_dicts.py file1 file2

This is pretty hacky.
It doesn't deal with some punctuation, especially quotes and commas.
"""

import argparse
from collections import defaultdict

from parse_dict import _match_largest_dict


def main():
    parser = argparse.ArgumentParser(description='Compare dicts')

    parser.add_argument('file1', help='File 1')
    parser.add_argument('file2', help='File 2')
    args = parser.parse_args()

    with open(args.file1) as file1:
        the_dict1 = _match_largest_dict(file1)
    with open(args.file2) as file2:
        the_dict2 = _match_largest_dict(file2)

    print(f"{len(the_dict1)} entries in dict1")
    print(f"{len(the_dict2)} entries in dict2")
    # compare keys
    if the_dict1.keys() == the_dict2.keys():
        print("same keys")
    else:
        set1 = set(the_dict1.keys()) - set(the_dict2.keys())
        print(f"{len(set1)} keys in dict1 not in dict2: {set1}")
        set2 = set(the_dict2.keys()) - set(the_dict1.keys())
        print(f"{len(set2)} keys in dict2 not in dict1: {set2}")
    print()

    # compare values
    float_compare = True
    same_dict = defaultdict(int)
    output = defaultdict(str)
    keys_in_common = set(the_dict1.keys()).intersection(set(the_dict2.keys()))
    for key in keys_in_common:
        the_same = 'different'
        if float_compare:
            f1 = float(the_dict1[key])
            f2 = float(the_dict2[key])
            if f1==f2:
                the_same = 'same'
            elif abs(f1-f2) < 0.001:
                the_same = 'close'
            else:
                the_same = 'diff'
        else:
            if the_dict1[key] == the_dict2[key]:
                the_same = 'same'

        same_dict[the_same] += 1
        output[the_same] += f"{key} = {the_dict1[key]} = {the_dict2[key]}  ({the_same})\n"

    for key in sorted(same_dict.keys()):
        print(f"{same_dict[key]} values {key}")
    print()

    for key in sorted(same_dict.keys()):
        if key not in ('same', 'close'):
            print(f"** {same_dict[key]} {key} values:\n\n{output[key]}")


if __name__ == '__main__':
    main()
