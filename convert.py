#!/usr/bin/env python3
import json
from pathlib import Path
import sys

def main():
    fname = "/L/zzz_syncthing/states/scrapyroo.jl"
    with Path(fname).open('r') as fo:
        for line in fo.readlines():
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
            json.dump(o, sys.stdout)
            sys.stdout.write('\n')

if __name__ == '__main__':
    main()
