Cause I got sick of clicking through Deliveroo restaurants. Full text search is a basic human right!

<img src="https://user-images.githubusercontent.com/291333/69106349-f82e9b00-0a65-11ea-9b9b-1fd45ebf4446.png"/>

# Setup and usage
## Scraper
Install dependencies: `pip3 install --user -r requirements.txt`

Add something like:

    ./scrape --area 'london/canning-town' --postcode 'E164SA' --json /path/to/menus.jsonl
    
to your crontab to run once a day, e.g. in the morning or something. Presumably, menus don't change often so that's enough.

## Indexer

TODO install py?

    ./index --index /path/to/tantivy-index /path/to/menus.jsonl


## Backend

    ./serve --index /path/to/tantivy-index

## Frontend

NOTE: if you're running page locally, you're gonna need to pass by [CORS](https://stackoverflow.com/a/3177718/706389).

You can do it by e.g. using Chromium with no web security:

    chromium-browser --disable-web-security --user-data-dir=/L/tmp/whatever frontend/index.html
