import scrapy


class NewsScrappingLab(scrapy.Item):
    title = scrapy.Field()
    date = scrapy.Field()
    link = scrapy.Field()
    section = scrapy.Field()
    image_urls = scrapy.Field()
