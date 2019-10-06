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
            o = {
                'url'  : url,
                'title': name or '',
                'body' : desc or '',
            }
            json.dump(o, sys.stdout)
            sys.stdout.write('\n')

if __name__ == '__main__':
    main()
