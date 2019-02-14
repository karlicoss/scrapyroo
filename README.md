Cause I got sick of clicking through Deliveroo restaurants. Full text search is a basic human right!

# Dependencies

* headless chrome/chromium
    
    Necessary to scrape deliveroo main page. Sadly, it's fool of dynamic shit, so can't get away with using http requests.
    If you know how to avoid it please let me know!

* `pip3 install --user -r requirements.txt`
    

# Setup

Add something like 

    scrapyroo/run --area 'london/canning-town' --postcode 'E164SA' --json /path/to/intermediate/json.jl --output /path/to/output.html
    
to your crontab to run once a day, e.g. in the morning or something. Presumably, menus don't change often so that's enough.

# Usage

Open `output.html` mentioned above and search. Yes, that easy.
