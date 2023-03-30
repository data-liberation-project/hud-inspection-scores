#!/usr/bin/env python3

import sys
import csv

from utils import load


def main(*filenames):
    rows = []  # list of (fn, rowdict)
    for fn in filenames:
        filerows = list(load(fn))
        print(f'{fn} has {len(filerows)} rows', file=sys.stderr)
        rows.extend(filerows)


    # get sum of all headers
    hdrs = []
    for fn, r in rows:
        for k in r.keys():
            if k not in hdrs:
                hdrs.append(k)

    writer = csv.DictWriter(sys.stdout, hdrs)
    writer.writeheader()
    writer.writerows((r for fn,r in rows))


if __name__ == '__main__':
    main(*sys.argv[1:])
