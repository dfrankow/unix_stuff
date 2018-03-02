#!/usr/bin/env python

"""Parse a hive log to get the first and last time a stage was running.
Print the first and last stage times.
"""

import re
import sys
# import datetime

begin_map = {}
end_map = {}

# the order in which the stages were encountered
for line in sys.stdin:
    m = re.search(r'((\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d),\d\d\d (Stage-\d+) map = \d+%)', line)
    if m:
        dt, stage = m.group(2), m.group(3)
        if stage not in begin_map:
            # print "stage '%s' dt '%s', line %s" % (stage, dt, line)
            begin_map[stage] = dt
        end_map[stage] = dt

for stage, begin_dt in begin_map.iteritems():
    end_dt = end_map.get(stage)
# this should work, but isn't right now:
#    begin_time = datetime.datetime.strptime(begin_dt, '%Y-%m-%d %H:%M:%S')
#    end_time = datetime.datetime.strptime(end_dt, '%Y-%m-%d %H:%M:%S').time()
#    tdiff = end_time - begin_time

    print stage, begin_dt, 'to', end_map.get(stage)#, "%.1f hours" % (tdiff / 60/60)
