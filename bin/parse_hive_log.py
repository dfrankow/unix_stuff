#!/usr/bin/env python

import datetime
import re
import sys

stage_begin = {}
stage_end = {}
for line in sys.stdin:
    m = re.search('(\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d)', line)
    if m:
        the_datetime = m.group(1)
    m = re.search('Stage-(\d+)', line)
    if m:
        stage = m.group(1)
        if stage not in stage_begin:
            stage_begin[stage] = the_datetime
        stage_end[stage] = the_datetime

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

for stage in sorted(map(int, stage_begin.keys())):
    stage = str(stage)
    begin = datetime.datetime.strptime(stage_begin[stage], DATETIME_FORMAT)
    end = datetime.datetime.strptime(stage_end[stage], DATETIME_FORMAT)
    print "Stage %s, start %s, end %s, diff %s" % (
        stage, stage_begin[stage], stage_end[stage], end-begin)
