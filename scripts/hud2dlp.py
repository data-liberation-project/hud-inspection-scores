#!/usr/bin/env python3

import sys
import copy
from collections import defaultdict

import dateutil.parser

from utils import JsonOutputter, load, stderr

opt_keep_diffs = False  # set to True to make it easier when tracking down discrepancies


def parse_date(s):
    if not s or s == '.':
        return ''
    return dateutil.parser.parse(s).strftime('%Y-%m-%d')


def col_rename(origcolname, newcolname=None):
    return origcolname, newcolname or origcolname

properties = defaultdict(dict)  # property_id:str -> dict of property attributes
inspections = defaultdict(dict)  # (property_id:str, date:YYYY-MM-DD) -> dict of inspection attributes

def getonly(d, k):
    n = len(d[k])
    if n == 1:
        return list(d[k].values())[0]
    raise Exception(f'{n} values for {k}')


def singlify(d, keep_diffs=opt_keep_diffs):
    r = {}
    origins = defaultdict(list)
    for k, v in d.items():
        if not keep_diffs or len(v) == 1:
            origin, v = list(v.items())[-1]
            origins[origin].append(k)
        r[k] = v

    r['_origins'] = ' '.join(origins.keys())

    return r


def stringify(x):
    if x is None:
        return ''
    return str(x)


def boiled(x):
    return str(x).lower()


def dedup(table, key, row, origin=''):
    'Set table[key]=row, ignoring exact duplicates but yield diffs about changed values.'

    d = table[key]
    changes = set()

    for k, v in row.items():
        if not v:
            continue

        if k not in d:
            d[k] = {}  # origin -> value

        if d[k]:
            oldvalues = list(str(x) for x in d[k].values())

            if boiled(v) not in tuple(boiled(x) for x in oldvalues):
                yield dict(origin=origin, attr=k, oldvalue=oldvalues[-1], newvalue=v, **row)
                changes.add(k)
            else:
                continue  # an existing value matches

        d[k][origin] = v


# mapping of source .xls header to cleaned column name
rems_cols = {
    'rems_property_id'          : 'property_id',
    'property_id'               : 'property_id',
    'property_name'             : 'property_name',
    'city'                      : 'city',
    'state_code'                : 'state',
    'has_active_financing_ind'  : 'has_financing',
    'has_active_assistance_ind' : 'has_assistance',
}

rems_unused_cols = set([
    'state_name_text'
])

def process_rems(row):
    'Parse HUD data.  Yield one row per inspection.'
    prop = {v:row.pop(k) for k, v in rems_cols.items() if k in row}

    prop['property_id'] = stringify(prop['property_id'])

    yield 'properties', prop

    for i in [1,2,3]:
        r = {}
        r['property_id'] = prop['property_id']
        r['inspection_id'] = row.pop(f'inspection_id_{i}', None)
        r['date'] = parse_date(row.pop(f'release_date_{i}', None))
        r['score'] = row.pop(f'inspection_score{i}', None)
        if r['inspection_id'] or r['date'] or r['score']:
            yield 'inspections', r

    remaining = set(row.keys() - rems_unused_cols)
    if remaining:
        stderr(f'unexpected columns remain: {remaining}')
        rems_unused_cols.update(remaining)


pis_cols = dict(col_rename(*line.split(':')) for line in '''
    property_id
    devlopment_id:property_id
    development_id:property_id
    property_name
    pha_name
    develpment_name:property_name
    development_name:property_name
    address
    city
    county_name:county
    state_name:state
    cbsa_name
    zip:zipcode
    zipcode
    latitude
    longitude
    location_quality
'''.split())

pis_unused_cols = set('cbsa_code state_code county_code pha_code fips_state_code'.split())


def process_hudpis(row):
    prop = {v:row.pop(k) for k, v in pis_cols.items() if k in row}
    prop['property_id'] = stringify(prop['property_id'])

    r = dict(
        inspection_id=row.pop('inspection_id', None),
        property_id=prop.get('property_id', None),
        date=parse_date(row.pop('inspection_date', None)),
        score=row.pop('inspection_score', None),
    )

    yield 'properties', prop

    if r['inspection_id'] or r['date'] or r['score']:
        yield 'inspections', r

    remaining = set(row.keys()) - pis_unused_cols
    if remaining:
        stderr(f'unexpected columns remain: {remaining}')
        pis_unused_cols.update(remaining)


def main(*filenames):
    outputter = JsonOutputter('data/output/hud')

    for fn in filenames:
        stderr(fn)

        if 'multifamily' in fn or 'public' in fn:
            processfunc = process_hudpis
        elif 'mf_' in fn.lower():
            processfunc = process_rems
        else:
            stderr('unknown file to parse', fn)
            continue

        origin = fn.split('/')[-1][:12]

        for dbname, row in load(fn):
            try:
                for tblname, outputrow in processfunc(row):
                    propid = stringify(outputrow.get('property_id'))
                    if tblname == 'properties':
                        for duprow in dedup(properties, propid, outputrow, origin=origin):
                            outputter.output('properties-diffs', duprow)
                    elif tblname == 'inspections':
                        for duprow in dedup(inspections, (propid, outputrow['date']), outputrow, origin=origin):
                            duprow['origin'] = origin
                            outputter.output('inspections-diffs', duprow)
                    else:
                        stderr(f'unknown table "{tblname}"')

            except Exception as e:
                stderr(row, outputrow)
                raise

    for k, prop in properties.items():
        outputter.output('properties', singlify(prop))

    for k, insp in inspections.items():
        outputter.output('inspections', singlify(insp))

    outputter.close()


if __name__ == '__main__':
    main(*sys.argv[1:])
