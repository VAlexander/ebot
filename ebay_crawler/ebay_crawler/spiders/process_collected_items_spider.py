# -*- coding: utf-8 -*-
import scrapy
import MySQLdb
from ebay_crawler.items import EbayCrawlerItem
import smtplib
from email.mime.text import MIMEText


class ProcessCollectedItemsSpiderSpider(scrapy.Spider):
	name = "process_collected_items_spider"
	allowed_domains = ["ebay.com"]
	start_urls = (
		'http://www.ebay.com/',
	)

	
	def mail(self, message, to, product_name):
		#try:
		msg = MIMEText(message.encode('utf-8'), 'html','utf-8')
		me = 'ebay_bot@localhost'
		msg['Subject'] = 'Ebay scraping ({0})'.format(product_name)
		msg['From'] = me
		msg['To'] = to

		# Send the message via our own SMTP server, but don't include the
		# envelope header.
		s = smtplib.SMTP('127.0.0.1')
		s.sendmail(me, to, msg.as_string())
		s.quit()
		
		return True
		#except:
		return False
	
	
	def get_items_from_db(self):
		try:
			db = MySQLdb.connect(host="localhost", user="root", passwd="root", db="ebay_bot", charset='utf8')
			cursor = db.cursor()
			
			sql = "SELECT * FROM ebay_items_item WHERE is_active=1"
			cursor.execute(sql)
			item_rows = cursor.fetchall()
			
			sql = "SELECT id, strike_price FROM ebay_items_product"
			cursor.execute(sql)
			product_rows = cursor.fetchall()
			products = {}
			for row in product_rows:
				product_id = row[0]
				strike_price = row[1]
				products[product_id] = {
					"strike_price": strike_price,
				}

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
					"strike_price": products[item_product_id]["strike_price"],
					"product_id": item_product_id,
					}
				items.append(item)
			db.close()

			return items
		except:
			return None
	
	
	def parse(self, response):
		items = self.get_items_from_db()
		messages = {}
		
		db = MySQLdb.connect(host="localhost", user="root", passwd="root", db="ebay_bot", charset='utf8')
		cursor = db.cursor()
		
		for item in items:
			if item["product_id"] not in messages:
				sql = "SELECT product_name FROM ebay_items_product WHERE id=%s"
				arguements = (item["product_id"], )
				cursor.execute(sql, arguements)
				product_name = cursor.fetchone()[0]
				messages[item["product_id"]] = "<h2>{0}</h2><br />".format(product_name)
				
			item_price = float(item["price"])
			strike_price = float(item["strike_price"])
			
			if item_price <= strike_price:
				message = u"<a href='{0}'>{1}</a> is ${2} (strike price is ${3})<br/>".format(
																						item["url"],
																						item["name"],
																						item["price"],
																						item["strike_price"]
																						)
				
				messages[item["product_id"]] += message
				sql = "UPDATE ebay_items_item SET is_active=0 WHERE id=%s"
				arguements = (item["id"], )
				cursor.execute(sql, arguements)
				db.commit()

		
		for product_id in messages:
			if "<a href=" in messages[product_id]:
				sql = "SELECT product_name, email, negative_words FROM ebay_items_product WHERE id=%s"
				arguements = (product_id, )
				cursor.execute(sql, arguements)
				product_name, email, negative_words = cursor.fetchone()
				if negative_words:
					messages[product_id] += "<h3>Negative words: </h3> {0}".format(negative_words)
				if self.mail(messages[product_id], email, product_name):
					print "Success!"
				
		db.close()