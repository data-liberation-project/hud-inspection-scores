#!/usr/bin/env python3

import os
import sys
import json
import datetime
import copy
import re
from pathlib import Path

from utils import JsonOutputter, load


def main(*args):
    tables = {}  # tblname -> tblnum

    for fn in args:
        out = JsonOutputter('data/converted/' + Path(fn).name)
        for tblname, row in load(fn):
            tblnum = tables.setdefault(tblname, len(tables)+1)
            out.output(tblnum, row)

        out.close()


if __name__ == '__main__':
    main(*sys.argv[1:])
