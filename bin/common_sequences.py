#!/usr/bin/env python

"""
Print common sequences from space-separated input lines.

Output is (tab-separated):

sequence #-lines-with-sequence
"""

import sys
from collections import defaultdict


def generate_ngrams(items, n):
    if len(items) < n:
        yield items
    else:
        # sliding window
        for idx in xrange(0, len(items)-n):
            yield items[idx:(idx+n)]


# common 5-grams
N=5
the_map = defaultdict(int)
for line in sys.stdin:
    # all N-grams
    for ngram in generate_ngrams(line.strip().split(' '), 5):
        the_map[' '.join(ngram)] += 1


# get the top 50 most common
top_counts = sorted(the_map.values(), reverse=True)
if len(top_counts) > 50:
    top_counts = top_counts[:50]

entries = []
for entry, count in the_map.iteritems():
    if count >= top_counts[-1]:
        entries.append((entry, count))

for entry, count in sorted(entries, key=lambda x: x[1], reverse=True):
    print '\t'.join(map(str, [entry, count]))
