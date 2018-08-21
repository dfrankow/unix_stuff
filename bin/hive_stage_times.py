#!/usr/bin/env python

"""Parse a hive log to get the first and last time a stage was running.
Print the first and last stage times.
"""

import re
import sys
import datetime

begin_map = {}
end_map = {}
reduce_begin_map = {}
num_mappers_map = {}
num_reducers_map = {}
stage_map = {}
# job_map: map current stage => job.  could change for lots of jobs.
job_map = {}

# the order in which the stages were encountered
for line in sys.stdin:
    m = re.search(r'Hadoop job information for (Stage-\d+): number of mappers: (\d+); number of reducers: (\d+)', line)
    if m:
        stage, num_mappers, num_reducers = m.group(1), m.group(2), m.group(3)
        job = job_map[stage]
        num_mappers_map[job] = num_mappers
        num_reducers_map[job] = num_reducers

    m = re.search(r'Starting Job = ([^,]+), Stage = (Stage-\d+)', line)
    if m:
        job, stage = m.group(1), m.group(2)
        job_map[stage] = job
        stage_map[job] = stage

    # m = re.search(r'Kill Command = /usr/local/hadoop/bin/hadoop job  -kill ([^ ]+)', line)

    m = re.search(r'((\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d),\d\d\d (Stage-\d+) map = (\d+)%,  reduce = (\d+)%)', line)
    if m:
        dt, stage, map_percent, reduce_percent = (
            m.group(2), m.group(3), m.group(4), m.group(5))
        job = job_map[stage]
        if job not in begin_map:
            # print "stage '%s' dt '%s', line %s" % (stage, dt, line)
            begin_map[job] = dt
        if int(reduce_percent) > 0 and job not in reduce_begin_map:
            # print "stage '%s' dt '%s' reduce %s, line %s" % (stage, dt, reduce_percent, line)
            reduce_begin_map[job] = dt
        end_map[job] = dt

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

print '\t'.join(['stage', 'start', 'end',
                 'time', 'reduce_time',
                 'mappers', 'reducers',
                 'job'])

for job in sorted(begin_map.keys(), cmp=lambda x,y: cmp(begin_map[x], begin_map[y])):
    stage = stage_map[job]
    num_mappers = num_mappers_map[job]
    num_reducers = num_reducers_map[job]

    begin_dt = begin_map[job]
    end_dt = end_map.get(job)
    reduce_begin_dt = reduce_begin_map.get(job)

    begin_time = datetime.datetime.strptime(begin_dt, DATETIME_FORMAT)
    end_time = datetime.datetime.strptime(end_dt, DATETIME_FORMAT)
    reduce_begin_time = ''
    if reduce_begin_dt:
        reduce_begin_time = datetime.datetime.strptime(reduce_begin_dt, DATETIME_FORMAT)
    tdiff = end_time - begin_time
    reduce_diff = ''
    reduce_diff_hours = ''
    if reduce_begin_time:
        reduce_diff = end_time - reduce_begin_time
        reduce_diff_hours = "%.1f hours" % (
            reduce_diff.total_seconds() / 60.0 / 60)

    print '\t'.join([stage, begin_dt, end_dt,
                     "%.1f hours" % (tdiff.total_seconds() / 60.0 / 60),
                     # 'reduce began', reduce_begin_dt,
                     reduce_diff_hours,
                     num_mappers,
                     num_reducers,
                     job
    ])
