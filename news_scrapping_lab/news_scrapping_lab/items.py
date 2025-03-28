# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsScrappingLab(scrapy.Item):
    title = scrapy.Field()     
    date = scrapy.Field()        
    link = scrapy.Field()        
    section = scrapy.Field() 
    image_urls = scrapy.Field()