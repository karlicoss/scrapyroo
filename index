#!/usr/bin/env python3
# pylint: skip-file
import json
from pathlib import Path
from subprocess import check_call
import sys
import shutil
import tempfile

import argparse


def main():
    p = argparse.ArgumentParser()
    p.add_argument('input', type=Path)
    p.add_argument('--index', type=Path, required=True)
    p.add_argument('--reuse', action='store_true', help='Reuse existing index')
    p.add_argument('--purge', action='store_true', help='Purge index before repoopulating')
    args = p.parse_args()
    path = args.input

    indexer = index_py
    # indexer = index_cli

    indexer(
        path,
        index=args.index,
        purge=args.purge,
        reuse=args.reuse,
    )

def index_py(path: Path, *, index: Path, purge: bool=False, reuse: bool=False):
    if purge:
        shutil.rmtree(str(index))
    index.mkdir(exist_ok=True)

    import tantivy # type: ignore

    # TODO how to reuse schema??
    schema_builder = tantivy.SchemaBuilder()
    schema_builder.add_text_field(
        'title',
        stored=True,
        tokenizer_name='en_stem',
        index_option='position',
    )
    schema_builder.add_text_field(
        'body',
        stored=True,
        tokenizer_name='en_stem',
        index_option='position',
    )
    schema_builder.add_text_field(
        'url',
        stored=True,
        # TODO 'basic' results in
        # Panicked at 'Parsing the query failed: FieldDoesNotHavePositionsIndexed("url")'
        index_option='position',
    )
    schema = schema_builder.build()

    idx = tantivy.Index(schema, str(index), reuse=reuse)

    writer = idx.writer()
    writer.delete_all_documents()
    with path.open('r') as fo:
        items = 0
        for m in iter_menus(fo):
            items += 1
            writer.add_document(tantivy.Document(**m))
    opstamp = writer.commit()
    print(f"Finished reindexing {items} items; opstamp {opstamp}")


    test_query = "chicken AND soup"
    print(f"Testing query: '{test_query}'")
    searcher = idx.searcher()
    query = idx.parse_query(test_query, ['title', 'body', 'url'])
    top_docs = tantivy.TopDocs(20)

    from pprint import pprint
    for score, address in searcher.search(query, top_docs):
        dd = searcher.doc(address).to_dict()
        title = dd['title'][0] # TODO FIMXE why 0 index?
        url = dd['url'][0]
        print(f'{title}\n    {url}')


def index_cli(path: Path, purge: bool=False, reuse: bool=False):
    assert not reuse
    if purge:
        check_call(['scrapyroo-index/clean'])

    with tempfile.TemporaryDirectory() as tdir:
        tfile = Path(tdir) / 'data.json'
        with tfile.open('w') as tf, path.open('r') as ff:
            for o in iter_menus(ff):
                json.dump(o, tf)
                tf.write('\n')

        tantivy_bin = 'tantivy'
        tantivy_bin = '/L/coding/tantivy-cli/target/x86_64-unknown-linux-musl/release/tantivy'
        with tfile.open('r') as fo:
            check_call([tantivy_bin, 'index', '-i', 'scrapyroo-index'], stdin=fo)

def iter_menus(from_):
    processed = {}
    for line in from_:
        j = json.loads(line)

        rest = j['restaurant']
        menu = j['menu']['items']
        url = j['urls']['current']
        if url in processed:
            # not sure why that happens, most likely some data races/pagination artifacts
            print(f"WARNING: multiple scraped results for {url}", file=sys.stderr)
            continue
        processed[url] = j

        name = rest['name']
        desc = rest['description']
        # TODO uname?
        # TODO opens_at/closes_at
        # TODO address?

        bodies = [
            # desc or '', # eh, not sure if I really need it
        ]
        raw = []

        for m in menu:
            iname = m['name']
            idesc = m['description'] or ''
            price = m['raw_price']
            ps = f'{price:.2f}'

            # TODO meh.
            def cleanup(s):
                s = s.replace('\t', ' ')
                s = s.replace('\r\n', ' ')
                s = s.replace('\n', ' ')
                return s
            (ps, iname, idesc) = map(cleanup, (ps, iname, idesc))

            raw.append({
                'name' : iname,
                'price': ps,
                'description': idesc,
            })
            bodies.append(ps + '\t' + iname + '\t' + idesc)

        # TODO post about it?
        # dbg!(text.len());
        #         let ch: Vec<char> = text.chars().collect();
        #         dbg!(ch.len());
        # [/L/coding/tantivy/src/snippet/mod.rs:353] text.len() = 6146
        # [/L/coding/tantivy/src/snippet/mod.rs:355] ch.len() = 6140
        deunicode = lambda s: s.encode('ascii', 'ignore').decode('ascii')
        bodies = [deunicode(s) for s in bodies]
        bodys = '\n'.join(bodies)

        yield {
            'url'  : url,
            'title': name or '',
            'body' : bodys,
        }

if __name__ == '__main__':
    main()
