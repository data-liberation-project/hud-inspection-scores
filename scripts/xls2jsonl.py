#!/usr/bin/env python3

import os
import sys
import json
import datetime
import copy
import re

from utils import JsonOutputter, load


def main(*args):
    for fn in args:
        out = JsonOutputter(fn)
        for tblname, row in load(fn):
            out.output(tblname, row)

        out.close()


if __name__ == '__main__':
    main(*sys.argv[1:])
