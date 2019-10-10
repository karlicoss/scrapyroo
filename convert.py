#!/usr/bin/env python3
import json
from pathlib import Path
from subprocess import check_call
import sys
import tempfile

import argparse

def main():
    p = argparse.ArgumentParser()
    p.add_argument('input', type=Path)
    p.add_argument('--purge-index', action='store_true')
    args = p.parse_args()

    path = args.input

    if args.purge_index:
        check_call(['./scrapyroo-index/clean'])

    with tempfile.TemporaryDirectory() as tdir:
        tfile = Path(tdir) / 'data.json'
        with tfile.open('w') as tf, path.open('r') as ff:
            convert(ff, tf)

        with tfile.open('r') as fo:
            check_call(['tantivy', 'index', '-i', 'scrapyroo-index'], stdin=fo)

def convert(from_, to):
    for line in from_:
        j = json.loads(line)

        rest = j['restaurant']
        menu = j['menu']['items']
        url = j['urls']['current']

        name = rest['name']
        desc = rest['description']
        # TODO uname?
        # TODO opens_at/closes_at
        # TODO address?
        # TODO maybe just store the whole thing?

        body = desc or ''

        for m in menu:
            iname = m['name']
            idesc = m['description'] or ''
            price = m['raw_price']
            pound, pence = divmod(price, 1)
            ps = f'{price:.0f}' if pence < 0.1 else f'{price:.1f}'

            # TODO use positions to highlight?
            body += iname + ' ' + ps + ' ' + idesc + '\n'

        o = {
            'url'  : url,
            'title': name or '',
            'body' : body,
        }
        json.dump(o, to)
        to.write('\n')

if __name__ == '__main__':
    main()
