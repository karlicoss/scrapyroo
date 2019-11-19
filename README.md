Cause I got sick of clicking through Deliveroo restaurants. Full text search is a basic human right!

<img src="https://user-images.githubusercontent.com/291333/52899011-dd7c7c80-31dc-11e9-834d-668a5cc872f7.png"/>

# Setup
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

    # TODO
    # run chromium without cors
    chromium-browser --disable-web-security --user-data-dir /L/tmp/whatever

# Usage

TODO

# TODO tantivy 

    # run indexer
    tantivy serve -i scrapyroo-index

    
    # open search
    file:///L/zzz_syncthing/coding/scrapyroo/index.html
