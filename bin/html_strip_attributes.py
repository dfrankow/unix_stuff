#!/usr/bin/env python3

import sys

import lxml.html.clean as clean
from lxml import etree, html

document_root = html.fromstring(sys.stdin.read())

cleaner = clean.Cleaner(safe_attrs_only=True, safe_attrs=frozenset())
cleansed = cleaner.clean_html(document_root)

pretty_print = False
print(etree.tostring(
    cleansed, encoding='unicode', pretty_print=pretty_print))
