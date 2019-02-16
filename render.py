#!/usr/bin/env python3
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
import logging

import dominate
from dominate.tags import *
from dominate.util import text, raw # type: ignore

STYLE = """
  .restaurant {
    padding-top: 5em;
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
  #results {
    padding-left: 2em;
  }

  .error {
    color: red;
  }
"""

def iter_data(f):
    for line in f:
        yield json.loads(line)

def setup_parser(p):
    p.add_argument('--json', type=str, default='menus.jl')
    p.add_argument('--output', type=str, default='scrapyroo.html')
    p.add_argument('--base-url', type=str, default='https://deliveroo.co.uk')

def run(args):
    scrapedf = Path(args.json)
    when = datetime.fromtimestamp(scrapedf.stat().st_mtime)
    with scrapedf.open('r') as fo:
        datas = list(sorted(iter_data(fo), key=lambda d: d['restaurant']['name']))


    doc = dominate.document(title=f'scrapyroo: {len(datas)} results from {when.strftime("%H:%M %d %B %Y")}')
    with doc.head:
        style(STYLE)
        script(src='https://unpkg.com/lunr/lunr.js')

    index_items = []
    with doc:
        # TODO make sure cas insensitive
        div('enter search terms. use + for logical AND, e.g. +pasta +seafood')
        input(type="text", id="query", size='80')
        button('search', type='button', onclick='search(this)')
        div('results:')
        with div(id='results'):
            pass

        for data in datas:
            with div(cls='restaurant'):
                try:
                    index_item = {}
                    rest = data['restaurant']

                    rname = rest['name']
                    uname = rest['uname']
                    index_item['uname'] = uname

                    with div(cls='rest-name'):
                        a(rname, name=uname, href=args.base_url + data['urls']['current'])
                        with span(cls='times'):
                            text((rest['opens_at'] or '???') + ' to ' + (rest['closes_at'] or '???'))
                    menu = data['menu']['items']

                    menu_items = ""
                    with div(cls='menu'):
                        for m in menu: # TODO sort as well
                            with div(cls='menu-item'):
                                iname = m['name']
                                idesc = m['description'] or ''
                                div(iname)
                                div(idesc)
                                div(m['raw_price'])
                                menu_items += iname + ' ' + idesc + ' '
                    index_item['text'] = menu_items
                    index_items.append(index_item)
                except Exception as e:
                    logging.exception(e)
                    div('ERROR WHILE RENDERING: ' + str(e), cls='error')

    with doc.head:
        with script():
            raw("""
var documents = """ + json.dumps(index_items) + """;
var idx = lunr(function () {
  this.ref('uname')
  this.field('text')

  documents.forEach(function (doc) {
    this.add(doc)
  }, this)
});


window.onload = function () {
  document.getElementById('query').addEventListener("keyup", function(event) {
    if (event.keyCode === 13) {
       search();
    }
  });
};

function search() {
    var query = document.getElementById('query').value;
    var results = idx.search(query);
    var container = document.getElementById('results');
    // clear previous results
    while (container.hasChildNodes()) {
        container.removeChild(container.lastChild);
    }
    if (results.length == 0) {
        container.appendChild(document.createTextNode("nothing found :("));
    } else {
        for (r of results) {
            var linkc = document.createElement('div');
            var link = document.createElement('a');
            link.title = r.ref;
            link.href = '#' + r.ref;
            link.textContent = r.score.toFixed(2) + ' ' + r.ref;
            linkc.appendChild(link);
            container.appendChild(linkc);
            console.log(r);
        }
    }
}
        """)


    with open(args.output, 'w') as fo:
        fo.write(doc.render())


def main():
    p = argparse.ArgumentParser()
    setup_parser(p)
    args = p.parse_args()
    run(args)

if __name__ == '__main__':
    main()
