#!/usr/bin/env python

"""Parse a python or java dict, output a tsv.

Example usage:

$ bin/compare_dicts.py file1 file2

This is pretty hacky.
It doesn't deal with some punctuation, especially quotes and commas.
"""
import re
import sys


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
    # contain ,{, and can be stripped.
    #
    # HACK: this doesn't deal with quotes correctly
    return _match_dict_with(
        line,
        '(\'|")?(([^{},\'"]+)(\'|")?: (\'|")?([^,\'"{}]+)(\'|")?)+',
        3, 6)


def _match_dict(line):
    dict1 = _match_java_dict(line)
    dict2 = _match_python_dict(line)
    the_dict = dict1
    if len(dict2) > len(dict1):
        the_dict = dict2
    return the_dict


def _match_largest_dict(fileh):
    the_dict1 = {}
    for line in fileh:
        a_dict = _match_dict(line)
        if len(a_dict) > len(the_dict1):
            the_dict1 = a_dict
    return the_dict1


def main():
    for key, val in _match_largest_dict(sys.stdin).items():
        print('\t'.join([key, val]))


if __name__ == '__main__':
    main()
