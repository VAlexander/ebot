# -*- coding: utf-8 -*-
import scrapy
import MySQLdb
import urllib
from ebay_crawler.items import EbayCrawlerItem


class CollectProductItemsSpider(scrapy.Spider):
	name = "collect_product_items_spider"
	allowed_domains = ["ebay.com"]
	start_urls = (
		'http://www.ebay.com/',
	)
	
	item_xpath = "//a[@class='vip']/@href"
	title_xpath = "//h1[@class='it-ttl']/text()"
	price_xpaths = ["//span[@itemprop='price']/text()", "//span[@id='mm-saleDscPrc']/text()"]
	next_page_xpath = "//a[@class='gspr next']/@href"

	def get_products_from_db(self):
		try:
			db = MySQLdb.connect(host="localhost", user="root", passwd="root", db="ebay_bot", charset='utf8')
			cursor = db.cursor()
			sql = "SELECT id, product_name FROM ebay_items_product"
			cursor.execute(sql)
			rows = cursor.fetchall()
			
			products = []
			for row in rows:
				product_id = row[0]
				product_name = row[1]
				product = {"id": product_id, "name": product_name}
				products.append(product)
			db.close()
			return products
		except:
			return None
	
	def parse(self, response):
		products_from_db = self.get_products_from_db()
		if products_from_db:
			items_per_page = 200
			for product in products_from_db:
				params = urllib.urlencode({
						"_sacat": 0,
						"_nkw": product["name"],
						"_ipg": items_per_page,
						"rt": "nc"
					})
				yield scrapy.Request(
					url="http://www.ebay.com/sch/i.html?{0}".format(params),
					callback=self.parse_search_results,
					meta = {"product_id": product["id"]},
					)

	def parse_search_results(self, response):
		for i in response.xpath("//a[@class='vip']"):
			url = i.xpath("./@href").extract()[0]	
			yield scrapy.Request(
				url=url,
				callback=self.parse_item,
				meta = {"product_id": response.meta["product_id"]}
				)
		if response.xpath(self.next_page_xpath):
			next_page_url = response.xpath(self.next_page_xpath).extract()[0]
			yield scrapy.Request(url=next_page_url, callback=self.parse_search_results)
			
	def parse_item(self, response):
		#try:
		title = ''.join(response.xpath(self.title_xpath).extract())
		
		for price_xpath in self.price_xpaths:
			if response.xpath(price_xpath):
				price = response.xpath(price_xpath).extract()[0]
		
		item = EbayCrawlerItem()
		item["name"] = title
		item["product_id"] = response.meta["product_id"]
		item["price"] = price
		item["url"] = response.url
		
		yield item
		#except:
		#	pass #Enable logging for this one