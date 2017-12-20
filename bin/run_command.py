#!/usr/bin/env python

"""run a command on a periodic basis and time it"""

import argparse
import datetime
import shlex
import subprocess
import sys
import time

parser = argparse.ArgumentParser(
    description='Run a command on a periodic basis')
parser.add_argument('command')
parser.add_argument('--every', dest='every')
args = parser.parse_args()

def run_the_command(cmd):
    before_command_time = time.time()
    try:
        ret = subprocess.check_call(shlex.split(cmd))
        if ret == 0:
            status = "ok"
        else:
            status = "return code %d" % ret
    except Exception, msg:
        status = "exception %s" % msg

    curtime = time.time()
    curtimestamp = datetime.datetime.fromtimestamp(curtime).strftime('%c')
    runtime = curtime - before_command_time

    print >>sys.stderr, '\t'.join([
            "STATUS:", curtime, curtimestamp, runtime, cmd, status])

if not args.every:
    run_the_command(args.command)
else:
    if args.every.endswith('m'):
        every_seconds = int(args.every[:-1])*60
    elif args.every.endswith('s'):
        every_seconds = int(args.every[:-1])
    else:
        print "every must be a number of minutes, e.g. '20m', or number of seconds, e.g., '1s'"
        sys.exit(1)

    last_time = time.time()
    while True:
        run_the_command(args.command)
        while (time.time() - last_time) < every_seconds:
            # sleep until we're back on the every_seconds schedule
            time.sleep((last_time+every_seconds)-time.time())
        last_time += every_seconds
