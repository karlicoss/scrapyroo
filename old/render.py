#!/usr/bin/env python3
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
import logging

import dominate # type: ignore
from dominate.tags import *
from dominate.util import text, raw # type: ignore

STYLE = """
  .restaurant {
    padding-top: 5em;
  }
  .menu {
    padding-left: 2em;
    font-family: sans-serif;
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

  mark {
      background: orange;
      color: black;
  }
"""

def iter_data(f):
    for line in f:
        yield json.loads(line)

def setup_parser(p):
    p.add_argument('--json', type=Path, default=Path('menus.jl'))
    p.add_argument('--output', type=str, default='scrapyroo.html')
    p.add_argument('--base-url', type=str, default='https://deliveroo.co.uk')

def run(args):
    scrapedf = args.json
    when = datetime.fromtimestamp(scrapedf.stat().st_mtime)
    with scrapedf.open('r') as fo:
        datas = list(sorted(iter_data(fo), key=lambda d: d['restaurant']['name']))


    doc = dominate.document(title=f'scrapyroo: {len(datas)} results from {when.strftime("%H:%M %d %B %Y")}')
    with doc.head:
        style(STYLE)
        script(src='https://unpkg.com/lunr/lunr.js')
        script(src="https://cdnjs.cloudflare.com/ajax/libs/mark.js/8.11.1/mark.min.js")

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
            try:
                rest = data['restaurant']
                uname = rest['uname']
                index_item = {}
                with div(cls='restaurant', id=uname):
                    rname = rest['name']
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
                                price = m['raw_price']
                                pound, pence = divmod(price, 1)
                                ps = f'{price:.0f}' if pence < 0.1 else f'{price:.1f}'

                                div(iname + ' ' + ps)
                                div(idesc)

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
    const mark_options = {
        caseSensitive: false,
        ignorePunctuation: ":;.,-–—‒_(){}[]!'\\"+=".split(""),
        diacritics: false, /* caused some crazy shit while matching... */
    };

    var query = document.getElementById('query').value;
    var results = idx.search(query);
    var container = document.getElementById('results');
    // clear previous results
    while (container.hasChildNodes()) {
        container.removeChild(container.lastChild);
    }

    new Mark("div.restaurant").unmark(mark_options);


    if (results.length == 0) {
        container.appendChild(document.createTextNode("nothing found :("));
    } else {
        const found = new Set();
        for (r of results) {
            found.add(r.ref);

            var linkc = document.createElement('div');
            var link = document.createElement('a');
            link.title = r.ref;
            link.href = '#' + r.ref;
            link.textContent = r.score.toFixed(2) + ' ' + r.ref;
            linkc.appendChild(link);
            container.appendChild(linkc);
        }

        const visible_rests = [];
        const rests = document.getElementsByClassName('restaurant');
        for (r of rests) {
            const visible = found.has(r.id);
            r.hidden = !visible;
            if (visible) {
                visible_rests.push(r);
            }
        }
        console.log('visible: ', visible_rests);
        const mark_query = query.replace(/[^a-zA-Z0-9]/g, ' ').split(' ');
        console.log('marking: ', mark_query);
        new Mark(visible_rests).mark(mark_query, mark_options);
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
