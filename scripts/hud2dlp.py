#!/usr/bin/env python3

import sys
import copy

import dateutil.parser

from utils import JsonOutputter, load, stderr


def parse_date(s):
    if not s or s == '.':
        return ''
    return dateutil.parser.parse(s).strftime('%Y-%m-%d')


def col_rename(origcolname, newcolname=None):
    return origcolname, newcolname or origcolname


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

properties = { }  # property_id:str -> dict of property attributes
inspections = { }  # (property_id:str, date:YYYY-MM-DD) -> dict of inspection attributes

def getonly(d, k):
    n = len(d[k])
    if n == 1:
        return list(d[k].values())[0]
    raise Exception(f'{n} values for {k}')


def singlify(d, keep_diffs=True):
    r = {}
    for k, v in d.items():
        if not keep_diffs or len(v) == 1:
            v = list(v.values())[-1]
        r[k] = v
    return r


def dedup(table, key, row, origin=''):
    'Set table[key]=row, ignoring exact duplicates but warning about differences.'
    if key not in table:
        table[key] = {}

    d = table[key]

    for k, v in row.items():
        if not v:
            continue

        if k not in d:
            d[k] = {}  # origin -> value

        if d[k]:
            oldvalues = list(str(x) for x in d[k].values())

            if str(v).lower() not in tuple(x.lower() for x in oldvalues):
                yield dict(origin=origin, key=key, attr=k, oldvalues=oldvalues, newvalue=v)
            else:
                continue  # an existing value matches

        d[k][origin] = v


def process_rems(row):
    'Parse HUD data.  Yield one row per inspection.'
    prop = {v:row.pop(k) for k, v in rems_cols.items() if k in row}
    prop['property_id'] = str(prop['property_id'])

    yield 'properties', prop

    for i in [1,2,3]:
        r = copy.copy(prop)
        r['inspection_id'] = row.pop(f'inspection_id_{i}')
        r['date'] = parse_date(row.pop(f'release_date_{i}'))
        r['score'] = row.pop(f'inspection_score{i}')
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
    prop['property_id'] = str(prop['property_id'])

    yield 'properties', prop
    yield 'inspections', dict(
        inspection_id=row.pop('inspection_id', None),
        property_id=prop.get('property_id'),
        date=parse_date(row.pop('inspection_date')),
        score=row.pop('inspection_score'),
    )

    remaining = set(row.keys()) - pis_unused_cols
    if remaining:
        stderr(f'unexpected columns remain: {remaining}')
        pis_unused_cols.update(remaining)


def main(*filenames):
    outputter = JsonOutputter('hud')

    for fn in filenames:
        stderr(fn)

        if 'multifamily' in fn or 'public' in fn:
            processfunc = process_hudpis
        elif 'mf_' in fn.lower():
            processfunc = process_rems
        else:
            stderr('unknown file to parse', fn)
            continue

        origin = fn.split('/')[-1][:20]

        for dbname, row in load(fn):
            try:
                for tblname, outputrow in processfunc(row):
                    propid = str(outputrow.get('property_id'))
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
