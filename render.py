#!/usr/bin/env python3
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import dominate
from dominate.tags import *
from dominate.util import text, raw # type: ignore

def iter_data(f):
    for line in f:
        yield json.loads(line)

def main():
    from argparse import ArgumentParser
    p = ArgumentParser()
    p.add_argument('--output', type=str, default='menus.html')
    p.add_argument('--base-url', type=str, default='https://deliveroo.co.uk')
    args = p.parse_args()


    # scrapedf = Path(sys.argv[1])
    scrapedf = Path('rests.jl')
    when = datetime.fromtimestamp(scrapedf.stat().st_mtime)
    with scrapedf.open('r') as fo:
        datas = list(sorted(iter_data(fo), key=lambda d: d['restaurant']['name']))

    doc = dominate.document(title=f'scrapyroo: {len(datas)} results from {when.strftime("%H:%M %d %B %Y")}')
    with doc.head:
        style("""
.restaurant {
  padding-bottom: 5em;
}
.menu {
  padding-left: 2em;
}

.menu-item {
  padding-bottom: 0.5em;
}
a {
 text-decoration: none;
}

        """)
    with doc:
        for data in datas[:10]:
            with div(cls='restaurant'):
                # print(data['name'])
                # import ipdb; ipdb.set_trace() 
                # 'urls' 'current'
                # 'restaurant' : 'name' 'menu' 'opens_at', 'closes_at',
                rest = data['restaurant']
                with div(cls='rest-name'):
                    a(rest['name'], href=args.base_url + data['urls']['current'])
                    with span(cls='times'):
                        text(rest['opens_at'] + ' to ' + rest['closes_at'])
                menu = data['menu']['items']
                with div(cls='menu'):
                    for m in menu: # TODO sort as well
                        with div(cls='menu-item'):
                            div(m['name'])
                            div(m['description'] or '')
                            div(m['price'])


                # 'menu' : 'items': 'name', 'price', 'description' 


    with open(args.output, 'w') as fo:
        fo.write(doc.render())






if __name__ == '__main__':
    main()
