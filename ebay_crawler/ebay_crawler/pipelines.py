# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
import MySQLdb
from scrapy.exceptions import DropItem


EUR_MULT = 1.1139
GBP_MULT = 1.4535
AU_MULT = 0.7114


class EbayCrawlerPipeline(object):
	def __init__(self):	
		#Initiate MySQL connection
		self.conn = MySQLdb.connect(
			host="localhost",
			user="root",
			passwd="root",
			db="ebay_bot",
			charset='utf8'
			)
		self.curs = self.conn.cursor()

		
	def clean_price(self, price_string):
		price = "".join([x for x in price_string if x.isdigit()])
		price = float("{0}.{1}".format(price[:-2], price[-2:]))
		if "EUR" in price_string:
			price *= EUR_MULT
		elif "GBP" in price_string:
			price *= GBP_MULT
		elif "AU" in price_string:
			price *= AU_MULT
		return price
		
		
	def process_item(self, item, spider):
		## Got item. Set last crawled time
		item['last_checked'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		sql = "SELECT product_name, negative_words FROM ebay_items_product WHERE id=%s"
		arguements = (item["product_id"], )
		self.curs.execute(sql, arguements)
		result = self.curs.fetchone()
		print result
		product_name, product_negative_words = result
		
		## If product words are not in the title of the item
		for word in product_name.split():
			if word.lower() not in item["name"].lower():
				## Then discard it
				raise DropItem
		
		## If there are negative words in the title of the item
		if product_negative_words:
			for word in product_negative_words.split():
				if word.lower() in item["name"].lower():
					## Then discard it
					raise DropItem
		
		## Cleaning price field of an item
		item["price"] = self.clean_price(item["price"])
		
		## Try to insert URL. If the row exists, update updated_time and last_crawled_time
		sql = "INSERT INTO ebay_items_item (name, url, last_checked, product_id, price, is_active) VALUES (%s, %s, %s, %s, %s, True) ON DUPLICATE KEY UPDATE name=%s, last_checked=%s, product_id=%s, price=%s"
		
		arguements = (
			## For insertion
			item['name'],
			item['url'],
			item['last_checked'],
			item['product_id'],
			item['price'],
			
			## For updating
			item['name'],
			item['last_checked'],
			item['product_id'],
			item['price'],
			)
			
		self.curs.execute(sql, arguements)
		self.conn.commit()
		return item
