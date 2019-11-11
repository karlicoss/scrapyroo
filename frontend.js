'use strict';

const e = React.createElement;


const ENDPOINT = 'http://localhost:3000/api/';
// const ENDPOINT = 'https://scrapyroo.karlicoss.xyz/search/api/';

function handle_body(that, res) {
    // TODO not sure why it's an array of length 1?
    // const body = res.doc.body[0];
    const snippets = res.snippets;


    let body = res.doc.body[0];
    // console.log(body);
    // console.log(snippets[0].fragments);

    // for (let i = 0; i < body.length; i++) {
    //     console.log(i, body[i]);
    // }

    if (snippets.length == 0) {
        return e('div', {key: 'error', className: 'error'}, "ERROR: empty snippet");
    }

    body = snippets[0].fragments; // TODO??

    let highlighted = [];
    let sidx = 0;
    for (const snippet of snippets) {

        const hls = snippet.highlighted.map(([start, stop]) => [start, stop, sidx]);
        // TODO bodies are all same?
        highlighted = highlighted.concat(hls);
        sidx++;
    }
    highlighted.sort((a, b) => a[0] - b[0]);



    let hl = "";
    let cur = 0;
    for (let [start, stop, si] of highlighted) {
        hl += body.substring(cur, start);

        hl += `<span class='highlight'>`;
        hl += body.substring(start, stop);
        hl += "</span>";
        const dbgcls = that.state.debug ? 'debug' : 'nodebug';
        // TODO mm, maybe make them invisible or something
        hl += `<sup class='snippet snippet_${si} ${dbgcls}'>${si}</sup>`;
        cur = stop;
    }
    hl += body.substring(stop, body.length);
    // TODO FIXME weird, snippets 
    // TODO write about that?

    const split = hl.split('\n');
    let matched = [];
    let unmatched = [];
    for (const line of split) {
        (line.includes('<span') ? matched : unmatched).push(line);
    }
    if (!that.state.show_unmatched) {
        unmatched = [];
    }
    const lines = that.state.sort ? (matched.concat(unmatched)) : split;

    const table = e('table', {
        key: 'tbl',
        className: 'menu',
    }, e('tbody', {}, lines.map((l, idx) => {
        const [price, name, text] = l.split('\t'); // TODO careful
        return e('tr', {
            key: `row${idx}`,
        }, [
            e('td', {key: 'price', className: 'price'}, `£${price}`),
            e('td', {
                key: 'item',
                dangerouslySetInnerHTML: {__html: name + "<br>" + text},
            }),
       ]);
    })));

    return table;
}

function uuid(res) {
    const url = res.doc.url[0];
    const uuid = url.replace(/\//g, '_');
    return uuid;
}

class SearchResults extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            query: 'fish and salad and -"fish cake"',
            results: [],
            error: '',
            debug: false,
            sort: true,
            show_unmwatched: false,
            incremental: true,
        };
    }

    // TODO would be nice if snippets had some sort of score as well? e.g. try on "duck soup"
    // TODO duck -- single place on deliveroo that opens at 7PM. really?
    render() {
        const toc_elems = this.state.results.map(
            res => e('li', {
                key: res.doc.url[0],
            }, [
                `${res.score.toFixed(1)} `,
                e('a', {
                    key: 'link',
                    href: `#${uuid(res)}`,
                }, `${res.doc.title}`),
            ]),
        );
        const toc = e('div', {
            key: 'toc',
            id: 'toc',
        }, "Restaurants:", e('ul', {key: 'toc-list'}, toc_elems));
        const children = this.state.results.map(
            res => e('div', {
                key: res.doc.url[0],
                className: 'item',
            }, [
                e('div', {
                    key: 'heading',
                    className: 'heading',
                    id: uuid(res),
                }, [
                    // TODO actually don't really need it?
                    // e('a', {key: 'back', href: '#toc', className: 'back'}, 'back '), // TODO arrow up
                    // TODO 'next' button for quick jumping?
                    e('div', {key: 'score'}, `score: ${res.score.toFixed(2)} `),
                    e('a', {
                        key: 'link',
                        href: "https://deliveroo.co.uk" + res.doc.url[0],
                    }, res.doc.title),
                ]),
                e('div', {
                    key: 'body',
                    className: 'body',
                }, handle_body(this, res)),
            ]
        ));

        const error_c = this.state.error;


        const that = this;
        function search() {
            // TODO !!! validate and do incremental search??
            // TODO special mode?
            const qq = document.querySelector('#query');
            const q = qq.value;

            reqwest({
                url: `${ENDPOINT}?q=${q}&nhits=20`,
                contentType: 'application/json',
                method: 'GET',
            }).then(res => {
                // console.log(res);
                // TODO eh? e.g. query duck, it results in multiple documents with same id??
                // TODO what does id even mean here??
                // "/menu/london/brick-lane/suito-japanese-platters"

                // TODO show rating?

                that.setState({results: res.hits, error: '' });
            }, (err, msg) => {
                console.error(err);
                console.error(msg);
                that.setState({error: `${err.status} ${err.statusText} ${msg}`});
            });
        }

        return e('div', {}, [
            e('div', {key: 'settings', id: 'settings'},
              e('input', {
                  type: 'checkbox',
                  key: 'incremental-checkbox',
                  checked: this.state.incremental,
                  onChange: (e) => { this.setState({incremental: e.target.checked});},
              }),
              "Search as you type",
              e('br'),
              e('input', {
                  type: 'checkbox',
                  key: 'debug-checkbox',
                  checked: this.state.debug,
                  onChange: (e) => { this.setState({debug: e.target.checked});},
                }),
              "Debug",
              e('br'),
              e('input', {
                  type: 'checkbox',
                  key: 'sort-checkbox',
                  checked: this.state.sort,
                  onChange: (e) => { this.setState({sort: e.target.checked});},
              }),
              "Show matched menu items first",
              e('br'),
              e('input', {
                  type: 'checkbox',
                  key: 'unmatched-checkbox',
                  checked: this.state.show_unmatched,
                  onChange: (e) => { this.setState({show_unmatched: e.target.checked});},
              }),
              "Show unmatched menu items"
             ),
            e('form', {
                 key: 'search-form',
                 onSubmit: (e) => {
                     search();
                     e.preventDefault();
                 }
            }, e('div', {
                key: 'search-form-container',
                id: 'search-line'
            }, [
                e('input', {
                     key: 'query',
                     type: 'text',
                     id: 'query',
                     value: this.state.query,
                     onChange: (event) => {
                         this.setState({query: event.target.value});
                         if (this.state.incremental) {
                             search();
                         }
                     },
                 }),
                e('button', {
                    key: 'submit',
                    id: 'search',
                    type: 'submit',
                }, 'Search'),
            ])),
            toc,
            e('div', {key: 'error'  , id: 'error', className: 'error'}, error_c),
            e('ul' , {key: 'results', id: 'results'}, children),
        ]);
    }

    componentDidMount () {
        // TODO not sure if need some extra callback..
        const query = document.querySelector('#query');
        query.focus();
    }
}

const resContainer = document.querySelector('#search_result_container');
ReactDOM.render(e(SearchResults), resContainer);
