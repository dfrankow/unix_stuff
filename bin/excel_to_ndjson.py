#!/usr/bin/env python

"""Excel sheet (xls, xlsx) to ndjson.

Note: could use https://github.com/dilshod/xlsx2csv instead
"""

import datetime
import json
import sys

import pandas as pd
from tqdm import tqdm


class PandasJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if o is None:
            return o
        if pd.isnull(o):
            # NaT => "NaT", NaN => "NaN"
            return str(o)
        if isinstance(o, pd.Timestamp) or isinstance(o, datetime.datetime):
            return o.isoformat()
        return super().default(o)


def main():
    if len(sys.argv) != 2:
        print("Usage: {sys.argv[0]} excel-file")
        sys.exit(1)

    # TODO: Allow nrows as an argument
    df = pd.read_excel(sys.argv[1], nrows=None)
    dicts = df.to_dict(orient="records")
    for the_dict in tqdm(dicts):
        print(json.dumps(the_dict, cls=PandasJSONEncoder))


main()
