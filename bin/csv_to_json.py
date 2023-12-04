#!/usr/bin/env python3

"""Read a .csv file as a pandas dataframe, and print the records as json"""

import sys

import pandas


def main():
    df = pandas.read_csv(sys.stdin)
    for index, row in df.iterrows():
        print(row.to_json())


main()
