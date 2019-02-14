import scrapy

class QuotesSpider(scrapy.Spider):
    name = "deliveroo_spider"

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
        # yield scrapy.Request(url=url, callback=self.parse)
        yield scrapy.Request(url='https://deliveroo.co.uk/menu/london/old-street/the-posh-burger-co?day=today&postcode=E18HW&time=ASAP', callback=self.parse_rest)


    def parse_rest(self, response):
        items = response.css('li.menu-index-page__item')
        from scrapy.utils.markup import remove_tags as untag


        import json
        react_data = json.loads(response.css('script.js-react-on-rails-component').xpath('text()').get())
        yield react_data
        # 'menu'
        # restaurant
        # # TODO modifier_group???
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
        # page = response.url.split("/")[-2]
        rests = response.css('ol li a::attr(href)').getall()
        print(f"found {len(rests)} restaurants")
        for r in rests[:5]:
            yield scrapy.Request(url=r, callback=self.parse_rest)


        # TODO shit. some seem to be missing...

        # import ipdb; ipdb.set_trace() 
        # print(page)

        # # ol?? RestaurantsList-8608590270dc6ae3
        # filename = 'quotes-%s.html' % page
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        # self.log('Saved file %s' % filename)
