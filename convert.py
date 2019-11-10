#!/usr/bin/env python3
# pylint: skip-file
import json
from pathlib import Path
from subprocess import check_call
import sys
import shutil
import tempfile

import argparse


# TODO odd, with scrapyroo-index-2 it doesn't work quite well
"""
cargo run serve --index /L/coding/scrapyroo/scrapyroo-index-2 2>&1 | tee log
    Finished dev [unoptimized + debuginfo] target(s) in 0.11s
     Running `target/debug/tantivy serve --index /L/coding/scrapyroo/scrapyroo-index-2`
thread 'main' panicked at 'attempt to shift left with overflow', /L/coding/tantivy/src/common/vint.rs:152:31
note: Run with `RUST_BACKTRACE=1` environment variable to display a backtrace
"""

# that works fine though..
# cargo run serve --index /L/coding/scrapyroo/scrapyroo-index 2>&1 | tee log


def main():
    p = argparse.ArgumentParser()
    p.add_argument('input', type=Path)
    p.add_argument('--purge-index', action='store_true')
    args = p.parse_args()
    path = args.input

    # indexer = index_py
    indexer = index_cli

    # ipath = Path('scrapyroo-index-2') # TODO FIXME
    if args.purge_index:
        check_call(['scrapyroo-index/clean'])
        # shutil.rmtree(str(ipath))
        # ipath.mkdir()

    indexer(path, purge=args.purge_index)

def index_py(path: Path, purge: bool=False):
    assert purge # TODO not sure what do we do?
    import tantivy # type: ignore

    # TODO how to reuse schema??
    schema_builder = tantivy.SchemaBuilder()
    schema_builder.add_text_field('title', stored=True, index_option='position')
    schema_builder.add_text_field('body' , stored=True, index_option='position')
    # TODO doesn't support 'indexing': none??
    schema_builder.add_text_field('url'  , stored=True, index_option='basic')
    schema = schema_builder.build()

    # idx = tantivy.Index(schema, 'scrapyroo-index', reuse=True)
    index = tantivy.Index(schema, 'scrapyroo-index-2')

    writer = index.writer()

    with path.open('r') as fo:
        for m in iter_menus(fo):
            writer.add_document(tantivy.Document(**m))
    writer.commit()

    index.reload()

    searcher = index.searcher()
    query = index.parse_query("chicken AND soup", ['title', 'body', 'url'])
    top_docs = tantivy.TopDocs(20)

    from pprint import pprint
    for score, address in searcher.search(query, top_docs):
        doc = searcher.doc(address)
        print(doc)
        # pprint(doc.to_dict())


def index_cli(path: Path, purge: bool=False):
    with tempfile.TemporaryDirectory() as tdir:
        tfile = Path(tdir) / 'data.json'
        with tfile.open('w') as tf, path.open('r') as ff:
            for o in iter_menus(ff):
                json.dump(o, tf)
                tf.write('\n')

        with tfile.open('r') as fo:
            check_call(['tantivy', 'index', '-i', 'scrapyroo-index'], stdin=fo)

def iter_menus(from_):
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

        body = [
            desc or '',
        ]
        raw = []

        # TODO could explain how I'm compensating for lack of hierarchical search?
        # TODO not sure if need some sentinels?

        # TODO can we keep this in index??
        # TODO serialize
        for m in menu:
            iname = m['name']
            idesc = m['description'] or ''
            price = m['raw_price']
            pound, pence = divmod(price, 1)
            ps = f'{price:.0f}' if pence < 0.1 else f'{price:.1f}'

            raw.append({
                'name' : iname,
                'price': ps,
                'description': idesc,
            })
            # TODO use positions to highlight?
            body.append(ps + ' ' + iname + ' ' + idesc)

        # TODO FIXME issue in cocotte
        # https://repl.it/languages/rust
        # if 'Add Chicken Soup' in body:
        #     import ipdb; ipdb.set_trace() 
        #     pass

        # TODO post about it?
        # dbg!(text.len());
        #         let ch: Vec<char> = text.chars().collect();
        #         dbg!(ch.len());
        # [/L/coding/tantivy/src/snippet/mod.rs:353] text.len() = 6146
        # [/L/coding/tantivy/src/snippet/mod.rs:355] ch.len() = 6140
        bodys = '\n'.join(body)
        bodys = bodys.encode('ascii', 'ignore').decode('ascii')

        # TODO FIXME eh. how to correlate price back?..
        # TODO maybe, include some markers??
        raws = json.dumps(raw)

        yield {
            'url'  : url,
            'title': name or '',
            'body' : bodys,
            'raw'  : raws,
        }

if __name__ == '__main__':
    main()
