#!/usr/bin/env python

"""
Print common sequences from space-separated input lines.

Output is (tab-separated):

sequence #-lines-with-sequence
"""

# Use one of these
TOPN_THRESHOLD = None
COUNT_THRESHOLD = 1000


import sys
from collections import defaultdict


def generate_ngrams(items, n):
    if len(items) < n:
        yield tuple(items)
    else:
        # sliding window
        for idx in xrange(0, len(items)-n):
            yield tuple(items[idx:(idx+n)])


# common 5-grams
N=5
the_map = defaultdict(int)
for line in sys.stdin:
    # all N-grams, but only one counted per line
    all = set([])
    for ngram in generate_ngrams(line.strip().split(' '), 5):
        all.add(ngram)
    for ngram in all:
        the_map[' '.join(ngram)] += 1

the_threshold = None
if TOPN_THRESHOLD:
    # get the most common
    top_counts = sorted(the_map.values(), reverse=True)
    if len(top_counts) > TOPN_THRESHOLD:
        top_counts = top_counts[:TOPN_THRESHOLD]
else:
    the_threshold = COUNT_THRESHOLD

entries = []
for entry, count in the_map.iteritems():
    if the_threshold is None or count >= the_threshold:
        entries.append((entry, count))

for entry, count in sorted(entries, key=lambda x: x[1], reverse=True):
    print '\t'.join(map(str, [entry, count]))
