'use strict';

const e = React.createElement;

class SearchResults extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            results: [],
        };
    }

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
                  res.doc.body[0].substring(0, 200) + "...",
                 ),
            ]
        ));
        return e(
            'div',
            {},
            [
                e('div', {key: 'results'}, children),
                e(
                    'button',
                    {
                        key: 'search',
                        onClick: () => {
                            const qq = document.querySelector('#query');
                            const q = qq.value;

                            reqwest({url: `http://localhost:3000/api/?q=${q}&nhits=20`,  contentType: 'application/json', method: 'GET'}).then(res => {
                                console.log(res);

                                this.setState({ results: res.hits });
                            });
                        }},
                    'Search'
                ),
            ]
        );
    }
}

const resContainer = document.querySelector('#search_result_container');
ReactDOM.render(e(SearchResults), resContainer);
