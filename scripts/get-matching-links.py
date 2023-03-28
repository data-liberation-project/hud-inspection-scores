#!/usr/bin/env python3

'''
Usage:

    $0 <url> <.ext> [...]

Fetch <url> and print all links ending in .ext.  Multiple .ext may be given.
'''

import sys

from urllib.parse import urljoin
import urllib.request

from bs4 import BeautifulSoup


def iterhrefs(url, *exts):
    'Fetch page at url and generate absolute urls from matching hrefs therein.'
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req)

    soup = BeautifulSoup(resp.read(), 'html.parser')

    # find all the <a> tags with an href attribute
    for link in soup.find_all('a', href=True):
        # make all the links absolute
        href = link['href']

        if exts and not href.endswith(exts):
            continue

        abshref = urljoin(url, href)
        yield abshref

if __name__ == '__main__':
    for url in iterhrefs(*sys.argv[1:]):
        print(url)
