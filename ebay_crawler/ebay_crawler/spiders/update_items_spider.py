# -*- coding: utf-8 -*-
import scrapy
import MySQLdb


price_xpaths = ["//span[@itemprop='price']/text()", "//span[@id='mm-saleDscPrc']/text()"]


class UpdateItemsSpiderSpider(scrapy.Spider):
	name = "update_items_spider"
	allowed_domains = ["ebay.com"]
	start_urls = (
		'http://www.ebay.com/',
	)

	
	def get_items_from_db(self):
		try:
			db = MySQLdb.connect(host="localhost", user="root", passwd="root", db="ebay_bot", charset='utf8')
			cursor = db.cursor()
			
			sql = "SELECT * FROM ebay_items_item WHERE is_active = 1"
			cursor.execute(sql)
			item_rows = cursor.fetchall()
			items = []
			for row in item_rows:
				item_id = row[0]
				item_name = row[1].strip()
				item_url = row[2]
				item_last_checked = row[3]
				item_price = row[4]
				item_product_id = row[5]
				item = {
					"id": item_id,
					"name": item_name,
					"url": item_url,
					"last_checked": item_last_checked,
					"price": item_price,
					"product_id": item_product_id,
					}
				items.append(item)
			db.close()
			return items
		except:
			return None
	
	
	def parse(self, response):
		items = self.get_items_from_db()
		for item in items:
			yield scrapy.Request(url=item["url"], callback=self.update_item_price, meta={"item":item})
		
		
	def update_item_price(self, response):
		
		price = ""
		for price_xpath in price_xpaths:
			if response.xpath(price_xpath):
				price = response.xpath(price_xpath).extract()[0]
			
		if not price:
			return None
			
		item = response.meta["item"]
		item["price"] = price
		return item
