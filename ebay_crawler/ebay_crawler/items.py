# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EbayCrawlerItem(scrapy.Item):
	id = scrapy.Field()
	product_id = scrapy.Field()
	name = scrapy.Field()
	price = scrapy.Field()
	url = scrapy.Field()
	last_checked = scrapy.Field()
