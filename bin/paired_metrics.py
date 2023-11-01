#!/usr/bin/env python

"""Compute metrics on a sequence of pairs of numbers.

Input is lines with two columns of numbers, tab-separated.
Each line is a pair of numbers for the same record.

Produces: confusion matrix, Cohen's kappa

TODO: correlation, % correct, ..

Note: requires sklearn in the python import path.
"""

import sys

from sklearn.metrics import cohen_kappa_score, confusion_matrix


def main():
    vals1, vals2 = [], []
    for line in sys.stdin:
        val1, val2 = line.strip().split("\t")
        vals1.append(val1)
        vals2.append(val2)

    # Confusion matrix
    confusion = confusion_matrix(vals1, vals2)
    print(f"confusion matrix (column 1 is rows, column 2 is columns):\n{confusion}\n\n")
    print(f"column 1 labels: {sorted(set(vals1))}")
    print(f"column 2 labels: {sorted(set(vals2))}\n")

    # Cohen's kappa
    kappa = cohen_kappa_score(vals1, vals2, weights="quadratic")
    print(f"Cohen's kappa (quadratic): {kappa:.3f}")


main()
