'use strict';

function debounce(a,b,c){var d,e;return function(){function h(){d=null,c||(e=a.apply(f,g))}var f=this,g=arguments;return clearTimeout(d),d=setTimeout(h,b),c&&!d&&(e=a.apply(f,g)),e}}

const e = React.createElement;


function handle_body(that, res) {
    // TODO not sure why it's an array of length 1?
    let body = res.doc.body[0];
    const highlights = res.highlights;

    if (highlights.length == 0) {
        return e('div', {key: 'error', className: 'error'}, "ERROR: empty snippet");
    }

    let highlighted = [];
    let sidx = 0;
    for (const snippet of highlights) {

        const hls = snippet.positions.map(([start, stop]) => [start, stop, sidx]);
        highlighted = highlighted.concat(hls);
        sidx++;
    }
    highlighted.sort((a, b) => a[0] - b[0]);

    let hl = "";
    let cur = 0;
    for (let [start, stop, si] of highlighted) {
        hl += body.substring(cur, start);

        const dbgcls = that.state.debug ? `snippet_${si}` : '';
        hl += `<span class='highlight ${dbgcls}'>`;
        hl += body.substring(start, stop);
        hl += "</span>";
        // TODO mm, maybe make them invisible or something
        // hl += `<sup class='snippet snippet_${si} ${dbgcls}'>${si}</sup>`;
        cur = stop;
    }
    hl += body.substring(stop, body.length);

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
            query: 'fish AND salad AND -"fish cake"',
            results: [],

            status: '',
            error: false,

            debug: false,
            sort: true,
            show_unmwatched: false,

            // TODO FIXME
            debounce: false,
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
                e('a', {
                    key: 'link',
                    href: `#${uuid(res)}`,
                }, `${res.doc.title}`),
                e('span', {key: 'score', className: 'score' + (this.state.debug ? 'debug' : '')}, ` ${res.score.toFixed(1)} `),
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
                    e('div', {key: 'score', className: 'score ' + (this.state.debug ? 'debug' : '')}, `score: ${res.score.toFixed(2)} `),
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
        const endpoint_localhost = 'http://localhost:3000';
        const endpoint_remote = 'https://scrapyroo.karlicoss.xyz/search';
        const controls = e(
            'div', {key: 'controls', id: 'controls'},
            e('div', {}, e('input', {
                type: 'input',
                id: 'endpoint',
                key: 'endpoint-input',
                list: 'endpoints',
                defaultValue: endpoint_remote,
            })),
            e('datalist', {id: 'endpoints'},
              e('option', {value: endpoint_localhost}),
              e('option', {value: endpoint_remote}),
             ),
            e('div', {}, e('input', {
                type: 'checkbox',
                key: 'debounce-checkbox',
                checked: this.state.debounce,
                onChange: (e) => { this.setState({debounce: e.target.checked});},
            }), "Debounce"),
            e('div', {}, e('input', {
                type: 'checkbox',
                key: 'incremental-checkbox',
                checked: this.state.incremental,
                onChange: (e) => { this.setState({incremental: e.target.checked});},
            }), "Search as you type"),
            e('div', {}, e('input', {
                type: 'checkbox',
                key: 'debug-checkbox',
                id: 'debug-checkbox',
                checked: this.state.debug,
                onChange: (e) => { this.setState({debug: e.target.checked});},
            }), "Debug"),
            e('div', {}, e('input', {
                type: 'checkbox',
                key: 'sort-checkbox',
                checked: this.state.sort,
                onChange: (e) => { this.setState({sort: e.target.checked});},
            }), "Show matched menu items first"),
            e('div', {}, e('input', {
                type: 'checkbox',
                key: 'unmatched-checkbox',
                checked: this.state.show_unmatched,
                onChange: (e) => { this.setState({show_unmatched: e.target.checked});},
            }), "Show unmatched menu items"),
            // TODO setting to debounce?
        );

        const status_c = this.state.status;
        return e('div', {}, [
            e('div', {key: 'settings', id: 'sidebar'},
              toc,
              controls,
             ),
            e('div', {
                key: 'search-line-extra',
                id: 'search-line-extra',
            }, [
                'You can use: AND/OR operators, "exact matches" or negative terms: -excludeme',
                e('form', {
                    key: 'search-form',
                    autoComplete: 'off',
                    onSubmit: (e) => {
                        this.search();
                        e.preventDefault();
                    }
                }, [
                    e('div', {
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
                                    this.doSearch();
                                }
                            },
                        }),
                        e('button', {
                            key: 'submit',
                            id: 'search',
                            type: 'submit',
                        }, '🔍'),
                    ])
                ]),
                e('div', {key: 'status' , id: 'status', className: this.state.error ? 'error': ''}, status_c),
            ]),
            e('ul' , {key: 'results', id: 'results'}, children),
        ]);
    }

    search() {
        // TODO !!! validate and do incremental search??
        const qq = document.querySelector('#query');
        const q = qq.value;

        const endpoint = document.querySelector('#endpoint').value + '/api/';

        reqwest({
            // TODO FIXME not sure if we should pass nhits at all?
            url: `${endpoint}?q=${q}&nhits=20`,
            contentType: 'application/json',
            method: 'GET',
        }).then(res => {
            // console.log(res);
            // TODO eh? e.g. query duck, it results in multiple documents with same id??
            // TODO what does id even mean here??
            // "/menu/london/brick-lane/suito-japanese-platters"

            // TODO show rating?

            const hits = res.hits;
            this.setState({results: hits, error: false, status: `${this.state.query}: ${hits.length} results` });
        }, (err, msg) => {
            console.error(err);
            console.error(msg);
            this.setState({error: true, status: `${err.status} ${err.statusText} ${msg}`});
        });
    }

    componentDidUpdate() {
        if (this.state.debounce) {
            this.doSearch = debounce(() => {
                this.search();
            }, 300);
        } else {
            this.doSearch = () => {
                this.search();
            };
        }
    }
    componentDidMount () {
        // TODO not sure if need some extra callback..
        const query = document.querySelector('#query');
        query.focus();
    }
}

const resContainer = document.querySelector('#search_result_container');
ReactDOM.render(e(SearchResults), resContainer);
