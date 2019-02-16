Cause I got sick of clicking through Deliveroo restaurants. Full text search is a basic human right!

<img src="https://user-images.githubusercontent.com/291333/52899011-dd7c7c80-31dc-11e9-834d-668a5cc872f7.png"/>

# Dependencies

* headless chromium (should be bundled with chromium by default)
    
    Necessary to scrape deliveroo main page. Sadly, it's fool of dynamic shit, so can't get away with using http requests.
    If you know how to avoid it please let me know!

* `pip3 install --user -r requirements.txt`
    

# Setup

Add something like 

    scrapyroo/run --area 'london/canning-town' --postcode 'E164SA' --json /path/to/intermediate/json.jl --output /path/to/output.html
    
to your crontab to run once a day, e.g. in the morning or something. Presumably, menus don't change often so that's enough.

# Usage

Open `output.html` mentioned above and search. Yes, that easy.
