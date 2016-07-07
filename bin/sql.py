#!/usr/bin/env python2.6

"""Run a SQL statement on a text file.

The text file is referred to as the 'data' table in the SQL statement.

Examples:

sql.py --file stats.usmen.tsv --sql 'select avg(`q2.rate`) from data'
"""

import os
import sys
import getopt
import tempfile
import re

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def runCmd(cmd):
    if os.system(cmd):
        print "Error running " + cmd
        sys.exit(1)
        # TODO(dan): Return actual exit code

def usage():
    print >>sys.stderr, "Usage: sql.py --file file --sql sql"

def main(argv=None):
    if argv is None:
        argv = sys.argv

    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h",
                                       ["help", "file=", "sql=",
                                        "leave-sqlite-file",
                                        "show-header",
                                        "debug",
                                        "log-sqlite-commands"])
        except getopt.error, msg:
            raise Usage(msg)
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

    filename = None
    sql = None
    leave_sqlite_file = False
    log_sqlite_commands = False
    debug = False
    show_header = True
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            return 0
        elif o in ("--file"):
            filename = a
        elif o in ("--sql"):
            sql = a
        elif o in ("--leave-sqlite-file"):
            leave_sqlite_file = True
        elif o in ("--log-sqlite-commands"):
            log_sqlite_commands = True
        elif o in ("--debug"):
            debug = True
        elif o in ("--show-header"):
            show_header = True
        else:
            print "Found unexpected option " + o

    if not filename:
        print >>sys.stderr, "Must give --file"
        sys.exit(1)
    if not sql:
        print >>sys.stderr, "Must give --sql"
        sys.exit(1)
    if not ('data' in sql):
        print >>sys.stderr, "WARNING: SELECT statement probably should refer to 'data' table"

    # Get the first line of the file to make a CREATE statement
    #
    # Copy the rest of the lines into a new file (datafile) so that
    # sqlite3 can import data without header.  If sqlite3 could skip
    # the first line with .import, this copy would be unnecessary.
    foo = open(filename)
    datafile = tempfile.NamedTemporaryFile()
    first = True
    for line in foo.readlines():
        if first:
            headers = line.rstrip().split()
            first = False
        else:
            print >>datafile, line,
    datafile.flush()
    if debug:
        print datafile.name
        runCmd("cat %s" % datafile.name)
    # Create columns with NUMERIC affinity so that if they are numbers,
    # SQL queries will treat them as such.
    create_statement = "CREATE TABLE data (" + ",".join(
        map(lambda x: "`%s` NUMERIC" % x, headers)) + ");"

    cmdfile = tempfile.NamedTemporaryFile()
    if debug:
        print cmdfile.name
    print >>cmdfile,create_statement
    print >>cmdfile,".separator '\t'"
    print >>cmdfile,".import '" + datafile.name + "' data"
    if show_header:
        print >>cmdfile, ".header on"
    print >>cmdfile, sql + ";"
    cmdfile.flush()
    if debug or log_sqlite_commands:
        runCmd("cat %s" % cmdfile.name)
    runCmd("cat %s | sqlite3" % cmdfile.name)


if __name__ == "__main__":
    sys.exit(main())
