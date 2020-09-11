#!/usr/bin/env python3

"""Parse and save tables in a web page into tab-separated-values (tsv) files.

Takes input from stdin.

Writes files in the current directory based on "id" attribute of each table.

NOTE: to fit into tsv, cell values \t \n \r are made into spaces instead.
To exactly preserve values, we'll have to use csv.

Based on https://srome.github.io/Parsing-HTML-Tables-in-Python-with-BeautifulSoup-and-pandas/

Requires beautifulsoup4==4.9.1.
"""

import logging
import sys
from bs4 import BeautifulSoup


def parse_text(txt):
    """Parse all tables in the given HTML text"""
    soup = BeautifulSoup(txt, 'html.parser')
    idx = 1
    for table in soup.find_all('table'):
        parse_html_table(table, f'table{idx:03d}')
        idx += 1


def clean_text(txt):
    """Make \t, \n, \r into spaces"""
    return txt.replace("\n", " ").replace("\t", " ").replace("\r", " ")


def parse_html_table(table, backup_id):
    """Parse tables out of the beautifulsoup table and write them into files."""
    n_columns = 0
    column_names = []

    table_id = table.get('id', backup_id)
    # logging.info(f"*** table {table_id}")
    # Find number of rows and columns
    # we also find the column titles if we can
    for row in table.find_all('tr'):
        # Determine the number of rows in the table
        td_tags = row.find_all('td')
        if len(td_tags) > 0:
            if n_columns == 0:
                # Set the number of columns for our table
                # TODO(dan): Handle colspan > 1
                n_columns = len(td_tags)

        # Handle column names if we find them
        th_tags = row.find_all('th')
        if len(th_tags) > 0 and len(column_names) == 0:
            assert len(column_names) == 0, "found more column names"
            for th in th_tags:
                column_names.append(th.get_text())

    # TODO(dan): Handle colspan > 1
    # Safeguard on Column Titles
    # if len(column_names) > 0 and len(column_names) != n_columns:
    #    raise Exception("Column titles do not match the number of columns")

    # TODO(dan): Handle table without id attribute
    filename = f"{table_id}.tsv"
    logging.info(f"Write {filename}..")
    with open(filename, 'w') as the_tsv:
        if not column_names:
            # there were no column names, so print a fake header col1, col2, ..
            print('\t'.join([f"col{col}" for col in range(n_columns)]),
                  file=the_tsv)
        for row in table.find_all('tr'):
            # always look for td or th because sometimes people use either in
            # a row, possibly for formatting reasons
            # this has the side effect of printing any existing table headers
            columns = row.find_all(['td', 'th'])
            col_texts = [col.get_text() for col in columns]
            if col_texts:
                print('\t'.join([clean_text(col) for col in col_texts]),
                      file=the_tsv)


def main():
    logging.basicConfig(format='%(name)s: %(message)s', level=logging.INFO)
    parse_text(sys.stdin.read())


main()
