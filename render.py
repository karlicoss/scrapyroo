#!/usr/bin/env python3
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import dominate
from dominate.tags import *
from dominate.util import text, raw # type: ignore

STYLE = """
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
"""

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

    # datas = datas[:10]

    doc = dominate.document(title=f'scrapyroo: {len(datas)} results from {when.strftime("%H:%M %d %B %Y")}')
    with doc.head:
        style(STYLE)
        script(src='https://unpkg.com/lunr/lunr.js')

    index_items = []
    with doc:
        for data in datas:
            index_item = {}
            with div(cls='restaurant'):
                rest = data['restaurant']

                rname = rest['name']
                index_item['name'] = rname # TODO get some id?

                with div(cls='rest-name'):
                    a(rname, href=args.base_url + data['urls']['current'])
                    with span(cls='times'):
                        text(rest['opens_at'] + ' to ' + rest['closes_at'])
                menu = data['menu']['items']

                menu_items = ""
                with div(cls='menu'):
                    for m in menu: # TODO sort as well
                        with div(cls='menu-item'):
                            iname = m['name']
                            idesc = m['description'] or ''
                            div(iname)
                            div(idesc)
                            div(m['price'])
                            menu_items += iname + ' ' + idesc + ' '
                index_item['text'] = menu_items
            index_items.append(index_item)

    with doc.head:
        with script():
            raw("""
var documents = """ + json.dumps(index_items) + """;
var idx = lunr(function () {
  this.ref('name')
  this.field('text')

  documents.forEach(function (doc) {
    this.add(doc)
  }, this)
})
        """)


    with open(args.output, 'w') as fo:
        fo.write(doc.render())






if __name__ == '__main__':
    main()
