#!/usr/bin/env python

"""Add days to a date, print the new date.

Can use negative numbers.

Usage: date_add.py 2016-07-01 -27
2016-06-04
"""

import datetime
import sys

print (datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d').date() +
       datetime.timedelta(int(sys.argv[2])))
