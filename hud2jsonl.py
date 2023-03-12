#!python3

import os
import sys
import json
import datetime

import xlrd


def parse_hud_xls(fn):
    '''
        Parse HUD inspection data from .xls file at `fn`.  Yield one dictionary per inspection.
    '''
    def stderr(*args):
        print(fn, *args, file=sys.stderr)

    def convert_cell(c):
        'Return properly-typed value for xls Cell `c`.'
        if c.ctype == xlrd.XL_CELL_NUMBER:
            v = int(c.value)
            if v != c.value:
                return c.value
            return v

        if c.ctype == xlrd.XL_CELL_DATE:
            t = xlrd.xldate.xldate_as_tuple(c.value, 0)
            dt = datetime.datetime(*t)
            return dt.isoformat(sep=' ')

        if c.ctype == xlrd.XL_CELL_BOOLEAN:
            return bool(c.value)

        if c.ctype == xlrd.XL_CELL_ERROR:
            stderr(f'error: {c.value}')
            return f'error: {c.value}'

        return c.value.strip()

    hud_cols = {
        'REMS Property Id'          : 'rems_property_id',
        'Property_Id'               : 'rems_property_id',
        'Property Name'             : 'property_name',
        'City'                      : 'city',
        'state_code'                : 'state',
        'has_active_financing_ind'  : 'has_financing',
        'has_active_assistance_ind' : 'has_assistance',
    }

    unused_cols = set([
        'state_name_text'
    ])

    wb = xlrd.open_workbook(fn, logfile=sys.stderr)
    if wb.nsheets > 1:
        stderr(f'unexpected sheets in {fn}')

    sheet = wb[0]

    hdrs = [c.value.strip() for c in sheet.row(0)]

    for i in range(1, sheet.nrows):
        row = dict(zip(hdrs, [convert_cell(c) for c in sheet.row(i)]))

        d = {v:row.pop(k) for k, v in hud_cols.items() if k in row}

        for i in [1,2,3]:
            d['inspection_id'] = row.pop(f'Inspection Id {i}')
            d['inspection_date'] = row.pop(f'Release Date {i}')
            d['inspection_score'] = row.pop(f'Inspection Score{i}')
            if d['inspection_id'] or d['inspection_date'] or d['inspection_score']:
                yield d

        remaining = set(row.keys() - unused_cols)
        if remaining:
            stderr(f'unexpected columns remain: {remaining}')


if __name__ == '__main__':
    for d in parse_hud_xls(sys.argv[1]):
        print(json.dumps(d))
