#!/usr/bin/env python3

'''
Usage:

   $0 <output-dir> <file.xlsx>

Convert .xlsx (or .xls) file to JSONL, 1 file per sheet in the input.

The files are put in <output-dir> and named with the full filename of the input, plus a number to indicate the sheet:

    <output-dir>/file.xlsx-1.jsonl
    <output-dir>/file.xlsx-2.jsonl
'''

import os
import sys
import json
import datetime
import copy
import re
from pathlib import Path

from utils import JsonOutputter, load


def main(output_dir, *args):
    tables = {}  # tblname -> tblnum

    for fn in args:
        out = JsonOutputter(output_dir+'/'+Path(fn).name)
        for tblname, row in load(fn):
            tblnum = tables.setdefault(tblname, len(tables)+1)
            out.output(tblnum, row)

        out.close()


if __name__ == '__main__':
    main(*sys.argv[1:])
