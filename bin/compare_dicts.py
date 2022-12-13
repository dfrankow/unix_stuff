#!/usr/bin/env python

"""Compare a java map to a python dict.

Example usage:

$ bin/compare_dicts.py file1 file2

This is pretty hacky.
It doesn't deal with some punctuation, especially quotes and commas.
"""

import argparse
import re
from collections import defaultdict


def _match_dict_with(line, regex, group1, group2):
    entries = {}
    # Note: this matches only those dicts where the entries can be stripped.
    for match in re.finditer(regex, line):
        key, val = match.group(group1).strip(), match.group(group2).strip()
        assert key not in entries
        entries[key] = val
    return entries


def _match_java_dict(line):
    # Note: this matches only those dicts where the entries don't
    # contain =,{, and can be stripped.
    return _match_dict_with(
        line,
        '(([^={},]+)=([^=,{}]+))+',
        2, 3)


def _match_python_dict(line):
    # Note: this matches only those dicts where the entries don't
    # contain :,{, and can be stripped.
    #
    # HACK: this doesn't deal with quotes correctly
    return _match_dict_with(
        line,
        '(\'|")?(([^:{},\'"]+)(\'|")?: (\'|")?([^:,\'"{}]+)(\'|")?)+',
        3, 6)


def _match_dict(line):
    dict1 = _match_java_dict(line)
    dict2 = _match_python_dict(line)
    the_dict = dict1
    if len(dict2) > len(dict1):
        the_dict = dict2
    return the_dict


def _match_largest_dict(filename):
    the_dict1 = {}
    with open(filename) as the_file:
        for line in the_file:
            a_dict = _match_dict(line)
            if len(a_dict) > len(the_dict1):
                the_dict1 = a_dict
    return the_dict1


def main():
    parser = argparse.ArgumentParser(description='Compare dicts')

    parser.add_argument('file1', help='File 1')
    parser.add_argument('file2', help='File 2')
    args = parser.parse_args()

    the_dict1 = _match_largest_dict(args.file1)
    the_dict2 = _match_largest_dict(args.file2)

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


main()
