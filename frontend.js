'use strict';

const e = React.createElement;


const ENDPOINT = 'http://localhost:3000/api/';
// const ENDPOINT = 'https://scrapyroo.karlicoss.xyz/search/api/';

function handle_body(res) {
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
    for (const snippet of snippets) {
        // console.log(snippet.highlighted);
        for (let [start, stop] of snippet.highlighted) {
            // console.log("%d %d", start, stop);
            // console.log(body.substring(start, stop));
        }
        // TODO bodies are all same?
        highlighted = highlighted.concat(snippet.highlighted);
    }
    highlighted.sort((a, b) => a[0] - b[0]);



    let hl = "";
    let cur = 0;
    // console.log(highlighted);
    for (let [start, stop] of highlighted) {
        hl += body.substring(cur, start);
        hl += "<span style='color: orange; font-weight: bold;'>";
        hl += body.substring(start, stop);
        hl += "</span>";
        cur = stop;
    }
    hl += body.substring(stop, body.length);
    hl = hl.replace(/\n/g, '<br/>');
    return e(
        'div',
        {
            dangerouslySetInnerHTML: {__html: hl},
        }
    );
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
    console.log(url);
    const uuid = url.replace(/\//g, '_');
    console.log(uuid);
    return uuid;
}

class SearchResults extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            results: [],
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
        const toc = e('ul', {
            key: 'toc',
            id: 'toc',
        }, toc_elems);
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
                    e('a', {key: 'back', href: '#toc'}, 'back '), // TODO arrow up
                    `score: ${res.score.toFixed(2)} `,
                    e('a', {
                        key: 'link',
                        href: "https://deliveroo.co.uk" + res.doc.url[0],
                    }, res.doc.title),
                ]),
                e('div', {
                    key: 'body',
                    className: 'body',
                }, handle_body(res)),
            ]
        ));
        return e('div', {
        }, [
            e('form', {
                key: 'search-form',
                onSubmit: (e) => {
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
                        // value: 'chicken AND soup AND -noodle', // TODO FIXME doesn't work
                        // value: '"Add Chicken Soup"',
                }),
            // e(
            //     'button',
            //     {
            //         key: 'search',
            //         onClick: () => {
            //         }},
            //     'Search'
            // ),
            ]),
            toc,
            e('ul' , {key: 'results'}, children),
        ]);
    }

    componentDidMount () {
        // TODO not sure if need some extra callback..
        document.querySelector('#query').focus();
    }
}

const resContainer = document.querySelector('#search_result_container');
ReactDOM.render(e(SearchResults), resContainer);
