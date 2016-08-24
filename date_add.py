#!/usr/bin/env python

import datetime
import sys

print (datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d').date() +
       datetime.timedelta(int(sys.argv[2])))
