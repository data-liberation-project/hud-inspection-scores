import sys
import re


def stderr(*args):
    print(*args, file=sys.stderr)


def clean_id(s):
    if s is None:
        return ''
    s = re.sub(r'[^\w\d_]', '_', s)  # replace non-alphanum chars with _
    s = re.sub(r'_+', '_', s)  # replace runs of _ with a single _
    s = s.strip('_')
    return s


def load(fn):
    if fn.endswith('.jsonl'):
        yield from load_jsonl(fn)
    elif fn.endswith('.xls'):
        yield from load_xls(fn)
    elif fn.endswith('.xlsx'):
        yield from load_xlsx(fn)
    else:
        stderr(f'cannot process {fn}')


from .jsonl import *
from .xls import *
