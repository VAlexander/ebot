#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import sys
import django

os.environ['DJANGO_SETTINGS_MODULE'] = 'ebay_bot.settings'
django.setup()

import urllib2
import time
import json
from ebot_settings import *
from subprocess import Popen
from datetime import datetime
from ebay_bot_config.models import Parameter


PRODUCT_TIMEOUT = int(Parameter.objects.get(name='get_product_items_timeout').value)
EMAIL_TIMEOUT = int(Parameter.objects.get(name='email_results_timeout').value)
UPDATE_ITEMS_TIMEOUT = int(Parameter.objects.get(name='update_items_timeout').value)

last_process_items_run = Parameter.objects.get(name='last_process_items_run')
last_collect_products_run = Parameter.objects.get(name='last_collect_products_run')
last_update_items_run = Parameter.objects.get(name='last_update_items_run')


while True:
	spiders = ["collect_product_items_spider", "process_collected_items_spider", "update_items_spider"]
	x = urllib2.urlopen(SCRAPYD_URL + "listjobs.json?project=ebay_crawler")
	status = json.loads(x.read())

	running_spiders = status["running"]

	if "collect_product_items_spider" not in running_spiders:	
		delta = (datetime.now() - datetime.strptime(last_collect_products_run.value, '%Y-%m-%d %H:%M:%S.%f')).total_seconds()
		if delta > PRODUCT_TIMEOUT:
			last_collect_products_run.value = str(datetime.now())
			last_collect_products_run.save()
			Popen(["curl", "http://localhost:6800/schedule.json", "-d", "project=ebay_crawler", "-d", "spider=collect_product_items_spider"])
			print "running collect_product_items_spider"
		
		
	if "update_items_spider" not in running_spiders:
		delta = (datetime.now() - datetime.strptime(last_update_items_run.value, '%Y-%m-%d %H:%M:%S.%f')).total_seconds()
		if delta > UPDATE_ITEMS_TIMEOUT:
			last_update_items_run.value = str(datetime.now())
			last_update_items_run.save()
			Popen(["curl", "http://localhost:6800/schedule.json", "-d", "project=ebay_crawler", "-d", "spider=update_items_spider"])
			print "running update_items_spider"
		
		
	if "process_collected_items_spider" not in running_spiders:
		delta = (datetime.now() - datetime.strptime(last_process_items_run.value, '%Y-%m-%d %H:%M:%S.%f')).total_seconds()
		if delta > EMAIL_TIMEOUT:
			last_process_items_run.value = str(datetime.now())
			last_process_items_run.save()
			Popen(["curl", "http://localhost:6800/schedule.json", "-d", "project=ebay_crawler", "-d", "spider=process_collected_items_spider"])
			print "running process_collected_items_spider"
	
	
	time.sleep(3)