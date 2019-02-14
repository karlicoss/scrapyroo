from scrapy.utils.markup import remove_tags as untag

import scrapy

# from scrapy_splash import SplashRequest

from kython.scrape import scrape_dynamic

class QuotesSpider(scrapy.Spider):
    name = "deliveroo_spider"
    user_agent = 'Mozilla/5.0'
    @property
    def postcode(self):
        return self.settings.attributes['POSTCODE'].value

    @property
    def area(self):
        return self.settings.attributes['AREA'].value

    def start_requests(self):
        url = f'https://deliveroo.co.uk/restaurants/{self.area}?postcode={self.postcode}'
        # urls = [
        #     'http://quotes.toscrape.com/page/1/',
        #     'http://quotes.toscrape.com/page/2/',
        # ]
        # for url in urls:

        print("Hang on... parsing initial restaurants list via headless browser...")
        main = scrape_dynamic(url, headless=True, wait=5)
        from bs4 import BeautifulSoup # TODO can we reuse scrapy's selectors for that???
        # TODO scrapy module from headless chromium? There must be something..
        soup = BeautifulSoup(main, "html.parser")
        rest_tags = list(soup.find('ol').children)
        links = list(sorted(x.find('a').attrs['href'] for x in rest_tags))
        # TODO still some sort of discrepancy, 492 vs 500? but at least it's very close now
        print(f"Total restaurants: {len(links)}")
        # TODO if 0, try again with biggger timestamp?

        for l in links:
            yield scrapy.Request(url=l, callback=self.parse_rest)
        # yield SplashRequest(url=url, callback=self.parse, args={
        #     'wait': 3.0,
        # })
        # yield scrapy.Request(url='https://deliveroo.co.uk/menu/london/old-street/the-posh-burger-co?day=today&postcode=E18HW&time=ASAP', callback=self.parse_rest)


    def parse_rest(self, response):
        print(f"Procssing: {response.url}")
        items = response.css('li.menu-index-page__item')


        import json
        react_data = json.loads(response.css('script.js-react-on-rails-component').xpath('text()').get())
        yield react_data
        # yield {'r': react_data['restaurant']['name']}
        # 'menu'
        # restaurant
        # # TODO modifier_group???

        # TODO shit. with splash doesn't find anything at all! :(
        # import ipdb; ipdb.set_trace()
        return
        for i in items:
            try:
                title = i.css('*.menu-index-page__item-title').get()
                desc  = i.css('*.menu-index-page__item-desc').get()
                # TODO shit. it must be binded by react...
                import ipdb; ipdb.set_trace() 
                price = i.css('*.menu-index-page__item-price').get()
                yield {
                    'title': None if title is None else untag(title),
                    'desc': None if desc is None else untag(desc),
                    'price': None if price is None else untag(price),
                }
            except Exception as e:
                # import ipdb; ipdb.set_trace()
                raise e

    def parse(self, response):
        """
        # TODO shit. this returns 45 results as well...
        sss = response.xpath("//*[contains(text(), 'NEXT_DATA')]").xpath('text()').get()
        first = sss.index('{')
        last = sss.rfind(';__NEXT_LOADED_PAGES')
        ddd = sss[first: last]
        import json
        js = json.loads(ddd)
        len(js['props']['initialState']['restaurants']['results']['all'])
        """
        # docker run -p 9050:8050 scrapinghub/splash

        # page = response.url.split("/")[-2]
        rests = response.css('ol li a::attr(href)').getall()
        # import ipdb; ipdb.set_trace() 
        print(f"found {len(rests)} restaurants")
        for r in rests:
            yield scrapy.Request(url=r, callback=self.parse_rest)


        # TODO shit. some seem to be missing...

        # import ipdb; ipdb.set_trace() 
        # print(page)

        # # ol?? RestaurantsList-8608590270dc6ae3
        # filename = 'quotes-%s.html' % page
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        # self.log('Saved file %s' % filename)
