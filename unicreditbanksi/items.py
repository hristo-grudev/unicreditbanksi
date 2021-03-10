import scrapy


class UnicreditbanksiItem(scrapy.Item):
    title = scrapy.Field()
    description = scrapy.Field()
