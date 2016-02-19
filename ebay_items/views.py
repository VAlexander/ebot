from django.shortcuts import render, redirect
from django.template import RequestContext, loader
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from ebay_items.models import Product, Item
from ebay_bot_config.models import Parameter
from datetime import datetime, timedelta
from subprocess import Popen
import json
import csv
import urllib2


def show_main_page(request):
	template = loader.get_template('index.html')
	
	last_process_items_run = Parameter.objects.get(name='last_process_items_run')
	last_collect_products_run = Parameter.objects.get(name='last_collect_products_run')
	last_update_items_run = Parameter.objects.get(name='last_update_items_run')
	
	get_product_items_timeout = Parameter.objects.get(name='get_product_items_timeout')
	get_product_items_timeout = int(get_product_items_timeout.value)
	email_results_timeout = Parameter.objects.get(name='email_results_timeout')
	email_results_timeout = int(email_results_timeout.value)
	update_items_timeout = Parameter.objects.get(name='update_items_timeout')
	update_items_timeout = int(update_items_timeout.value)
	
	next_process_items_run = str(datetime.strptime(last_process_items_run.value, '%Y-%m-%d %H:%M:%S.%f') + timedelta(seconds=email_results_timeout))
	next_collect_products_run = str(datetime.strptime(last_collect_products_run.value, '%Y-%m-%d %H:%M:%S.%f') + timedelta(seconds=get_product_items_timeout))
	next_update_items_run = str(datetime.strptime(last_update_items_run.value, '%Y-%m-%d %H:%M:%S.%f') + timedelta(seconds=update_items_timeout))
	
	x = urllib2.urlopen("http://localhost:6800/listjobs.json?project=ebay_crawler")
	status = json.loads(x.read())

	running_spiders = status["running"]
	
	context = RequestContext(request, {
			"time_now": str(datetime.now()),
			"last_process_items_run": last_process_items_run.value,
			"last_collect_products_run": last_collect_products_run.value,
			"last_update_items_run": last_update_items_run.value,
			"next_process_items_run": next_process_items_run,
			"next_collect_products_run": next_collect_products_run,
			"next_update_items_run": next_update_items_run,
			"running_spiders": running_spiders
		})
	
	return HttpResponse(template.render(context))


def list_products(request):
	template = loader.get_template('products.html')
	
	products = Product.objects.all()
	
	context = RequestContext(request, {
		'products': products,
	})
	return HttpResponse(template.render(context))
	
def product_details(request, id):
	
	template = loader.get_template('product_details.html')
	
	product = Product.objects.get(id=id)
	items = Item.objects.filter(product_id=id)
	
	context = RequestContext(request, {
		'items': items,
		'id': id,
	})
	
	return HttpResponse(template.render(context))


def activate_item(request, item_id):
	item = Item.objects.get(id=item_id)
	item.is_active = True
	item.save()
	return redirect(request.META["HTTP_REFERER"])
	
def deactivate_item(request, item_id):
	item = Item.objects.get(id=item_id)
	item.is_active = False
	item.save()
	return redirect(request.META["HTTP_REFERER"])
	
def delete_product(request, product_id):
	try:
		product = Product.objects.get(id=product_id)
		product.delete()
	except:
		pass
		
	return list_products(request)


def run_collect_product_items_spider(request):
	x = urllib2.urlopen("http://localhost:6800/listjobs.json?project=ebay_crawler")
	status = json.loads(x.read())
	last_collect_products_run = Parameter.objects.get(name='last_collect_products_run')
	running_spiders = status["running"]
	if "collect_product_items_spider" not in running_spiders:	
		last_collect_products_run.value = str(datetime.now())
		last_collect_products_run.save()
		Popen(["curl", "http://localhost:6800/schedule.json", "-d", "project=ebay_crawler", "-d", "spider=collect_product_items_spider"])
		return redirect('show_main_page')
		

def run_update_items_spider(request):
	x = urllib2.urlopen("http://localhost:6800/listjobs.json?project=ebay_crawler")
	status = json.loads(x.read())
	running_spiders = status["running"]
	last_update_items_run = Parameter.objects.get(name='last_update_items_run')
	if "update_items_spider" not in running_spiders:
		last_update_items_run.value = str(datetime.now())
		last_update_items_run.save()
		Popen(["curl", "http://localhost:6800/schedule.json", "-d", "project=ebay_crawler", "-d", "spider=update_items_spider"])
		return redirect('show_main_page')
		
		
def run_process_collected_items_spider(request):
	x = urllib2.urlopen("http://localhost:6800/listjobs.json?project=ebay_crawler")
	status = json.loads(x.read())
	running_spiders = status["running"]
	last_process_items_run = Parameter.objects.get(name='last_process_items_run')
	running_spiders = status["running"]
	if "process_collected_items_spider" not in running_spiders:
		last_process_items_run.value = str(datetime.now())
		last_process_items_run.save()
		Popen(["curl", "http://localhost:6800/schedule.json", "-d", "project=ebay_crawler", "-d", "spider=process_collected_items_spider"])
		return redirect('show_main_page')
	

def make_all_items_active(request, product_id):
	items = Item.objects.filter(product_id=product_id)
	for item in items:
		item.is_active = 1
		item.save()
	return redirect('product_details', product_id)

	
def delete_all_products(request):
	products = Product.objects.all()
	for product in products:
		product.delete()
	return redirect('show_main_page')
	
	
@csrf_protect
def upload(request):
	if request.method == 'GET':
		template = loader.get_template('upload.html')
		context = RequestContext(request, {})
		return HttpResponse(template.render(context))
	elif request.method == 'POST':
		file = request.FILES['csvFile']
		data = [row for row in csv.reader(file.read().splitlines())]
		file.close()
		
		imported_products = []
		for row in data:
			new_product = Product()
			new_product.product_name = row[0]
			new_product.strike_price = row[1]
			new_product.email = row[2]
			new_product.negative_words = row[3]
			new_product.save()
			imported_products.append(new_product)
		
		template = loader.get_template('upload_result.html')
		context = RequestContext(request, {
			'imported_products': imported_products,
		})
		return HttpResponse(template.render(context))