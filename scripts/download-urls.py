#!/usr/bin/env python3

'''
Usage:

    $0 list-of-urls.txt <output-dir>

HTTP HEAD for each URL from stdin, and download all files not already in <output-dir>.
'''

import sys
import shutil
from pathlib import Path
import urllib.request

def to_isodate(dt):
    import dateutil.parser
    return dateutil.parser.parse(dt).strftime("%Y-%m-%d")


def maybe_download(url, outdir):
    req = urllib.request.Request(url, method='HEAD')
    resp = urllib.request.urlopen(req)
    size = int(resp.headers.get('Content-Length'))
    mod = resp.headers.get('Last-Modified')
    mod = to_isodate(mod)

    fn = f'{mod}-' + Path(url).name

    fullpath = Path(outdir)/fn

    if fullpath.exists():
        if fullpath.stat().st_size == size:
            print('exists, skipping', fn)
            return

        # use size in name
        fn = f'{mod}-{size}-' + Path(url).name

    print('getting', size, mod, fn)

    with urllib.request.urlopen(url) as resp:
        with open(fullpath, 'wb') as fp:
            shutil.copyfileobj(resp, fp)


def main(outdir='.'):
    with sys.stdin as fp:
        for url in fp:
            url = url.strip()
            maybe_download(url, outdir)


if __name__ == '__main__':
    main(*sys.argv[1:])
