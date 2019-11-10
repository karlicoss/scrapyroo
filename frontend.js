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

    body = snippets[0].fragments; // TODO??
    // console.log(body);
    // console.log(body.length);


    let highlighted = [];
    let sidx = 0;
    for (const snippet of snippets) {
        // console.log(snippet.highlighted);

        const hls = snippet.highlighted.map(([start, stop]) => [start, stop, sidx]);
        // TODO bodies are all same?
        highlighted = highlighted.concat(hls);
        sidx++;
    }
    highlighted.sort((a, b) => a[0] - b[0]);



    let hl = "";
    let cur = 0;
    // console.log(highlighted);
    for (let [start, stop, si] of highlighted) {
        hl += body.substring(cur, start);

        hl += `<span class='highlight'>`;
        hl += body.substring(start, stop);
        hl += "</span>";
        if (that.state.debug) {
            // TODO mm, maybe make them invisible or something
            hl += `<sup class='snippet snippet_${si}'>${si}</sup>`;
        }
        cur = stop;
    }
    hl += body.substring(stop, body.length);
    // console.log("FINISHED!");
    // TODO FIXME weird, snippets 
    // TODO write about that?

    const lines = hl.split('\n');
    if (that.state.sort) {
        lines.sort((a, b) => b.includes('<span') - a.includes('<span')); // TODO meh..
    }

    const table = e('table', {
        key: 'tbl',
        class: 'menu',
    }, e('tbody', {}, lines.map(l => {
        const [price, name, text] = l.split('\t'); // TODO careful
        return e('tr', { // TODO FIXME non unique key
            key: 'row'
        }, [
            e('td', {key: 'price'}, price),
            e('td', {
                key: 'item',
                dangerouslySetInnerHTML: {__html: name + "<br>" + text},
            }),
       ]);
    })));

    return table;
    // const html = lines.join('<br/>');
    // return e(
    //     'div',
    //     {
    //         dangerouslySetInnerHTML: {__html: html},
    //     }
    // );
    // return body.split('\n').map((item, key) => {
        // TODO what's up with non unique key???
        // console.log(key);
    //     return e(
    //         'span',
    //         {
    //             key: key,
    //             dangerouslySetInnerHTML: {'__html': 'hi'},
    //         },
    //         [
    //             e('br'),
    //         ],
    //     );
    // });
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
            results: [],
            debug: false,
            sort: true,
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
        }, e('div', {}, "Restaurants:"), e('ul', {}, toc_elems));
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
                    e('div', {}, `score: ${res.score.toFixed(2)} `),
                    e('a', {
                        key: 'link',
                        href: "https://deliveroo.co.uk" + res.doc.url[0],
                    }, res.doc.title),
                ]),
                e('div', {
                    key: 'body',
                    className: 'body',
                }, handle_body(this, res)),
                // TODO FIXME would be nice to reorder highlighted stuff?
            ]
        ));
        return e('div', {
        }, [
            e('div', {},
              e('input', {
                  type: 'checkbox',
                  key: 'debug-checkbox',
                  checked: this.state.debug,
                  onChange: (e) => { this.setState({debug: e.target.checked});},
                }),
              e('label', {}, "Debug"),
             ),
            e('div', {},
              e('input', {
                  type: 'checkbox',
                  key: 'sort-checkbox',
                  checked: this.state.sort,
                  onChange: (e) => { this.setState({sort: e.target.checked});},
              }),
              e('label', {}, "Show matched menu items first"),
             ),
            e('form', {
                key: 'search-form',
                onSubmit: (e) => {
                    // TODO !!! validate and do incremental search??
                    // TODO special mode?
                    const qq = document.querySelector('#query');
                    const q = qq.value;

                    reqwest({url: `${ENDPOINT}?q=${q}&nhits=20`,  contentType: 'application/json', method: 'GET'}).then(res => {
                        console.log(res);
                        // TODO eh? e.g. query duck, it results in multiple documents with same id??
                        // TODO what does id even mean here??
                        // "/menu/london/brick-lane/suito-japanese-platters"

                        // TODO show rating?

                        this.setState({ results: res.hits });
                    });

                    e.preventDefault();
                }
            }, [
                e('button', {
                    key: 'submit',
                    type: 'submit',
                }, 'Search'),
                e('input', {
                    key: 'query',
                    type: 'text',
                    id: 'query',
                }),
            ]),
            toc,
            e('ul' , {key: 'results', id: 'results'}, children),
        ]);
    }

    componentDidMount () {
        // TODO not sure if need some extra callback..
        const query = document.querySelector('#query');
        query.value = '"duck soup"';
        query.focus();
    }
}

const resContainer = document.querySelector('#search_result_container');
ReactDOM.render(e(SearchResults), resContainer);
