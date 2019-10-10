'use strict';

const e = React.createElement;


// const ENDPOINT = 'https://localhost:3000/api/';
const ENDPOINT = 'https://scrapyroo.karlicoss.xyz/search/api/';

function handle_body(res) {
    // TODO not sure why it's an array of length 1?
    // const body = res.doc.body[0];
    let snippet = res.snippet;
    let body = res.doc.body[0];
    console.log(snippet.highlighted);
    let hl = "";
    let cur = 0;
    for (let [start, stop] of snippet.highlighted) {
        hl += body.substring(cur, start);
        hl += "[";
        hl += body.substring(start, stop);
        hl += "]";
        cur = stop;
    }
    hl += body.substring(stop, body.length);
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

class SearchResults extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            results: [],
        };
    }

    // TODO FIXME children with the same key?
    render() {
        const children = this.state.results.map(res => e(
            'div',
            {
                key: res.id,
                className: 'item',
            },
            [
                e('div', {key: 'heading', className: 'heading'}, `score: ${res.score} ${res.doc.title}`),
                e('div',
                  {key: 'body'   , className: 'body'   },
                  handle_body(res),
                 ),
            ]
        ));
        return e(
            'div',
            {},
            [
                e(
                    'button',
                    {
                        key: 'search',
                        onClick: () => {
                            const qq = document.querySelector('#query');
                            const q = qq.value;

                            reqwest({url: `${ENDPOINT}?q=${q}&nhits=20`,  contentType: 'application/json', method: 'GET'}).then(res => {
                                console.log(res);

                                this.setState({ results: res.hits });
                            });
                        }},
                    'Search'
                ),
                e('input', {
                    type: 'text',
                    id: 'query',
                    value: 'chicken AND soup AND -noodle', // TODO FIXME doesn't work
                }),
                e('div', {key: 'results'}, children),
            ]
        );
    }
}

const resContainer = document.querySelector('#search_result_container');
ReactDOM.render(e(SearchResults), resContainer);
