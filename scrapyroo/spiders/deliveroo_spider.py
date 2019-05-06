import json

import scrapy # type: ignore
from scrapy.utils.markup import remove_tags as untag # type: ignore
from scrapy.selector import Selector # type: ignore

class DeliverooSpider(scrapy.Spider):
    name = "deliveroo_spider"
    user_agent = 'Mozilla/5.0'
    @property
    def postcode(self):
        return self.settings.attributes['POSTCODE'].value

    @property
    def area(self):
        return self.settings.attributes['AREA'].value

    @property
    def base_url(self):
        return self.settings.attributes['BASE_URL'].value

    def start_requests(self):
        url = f'{self.base_url}/restaurants/{self.area}?postcode={self.postcode}'
        yield scrapy.Request(url=url, callback=self.parse_main)

    def parse_main(self, response):
        # TODO maybe, worth moving selector in config so it's easier to fix it?
        links = response.xpath("//a[contains(@href, '/menu/')]/@href").getall()
        # TODO still some sort of discrepancy, 492 vs 500? but at least it's very close now
        print(f"Total restaurants: {len(links)}")

        for l in links[:3]:
            yield scrapy.Request(url=l, callback=self.parse_rest)

    def parse_rest(self, response):
        print(f"Processing: {response.url}")
        items = response.css('li.menu-index-page__item')
        react_data = json.loads(response.css('script.js-react-on-rails-component').xpath('text()').get())
        yield react_data

    def parse(self, response):
        """
        # TODO shit. this returns 45 results instead of 500 as well...
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
        print(f"found {len(rests)} restaurants")
        for r in rests:
            yield scrapy.Request(url=r, callback=self.parse_rest)
