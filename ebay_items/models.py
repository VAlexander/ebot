from __future__ import unicode_literals

from django.db import models

class Product(models.Model):
	product_name = models.CharField(max_length=255)
	strike_price = models.CharField(max_length=30)
	email = models.CharField(max_length=255)
	negative_words = models.TextField()
	

class Item(models.Model):
	product = models.ForeignKey('Product')
	name = models.CharField(max_length=255)
	url = models.CharField(max_length=255, unique=True)
	last_checked = models.DateTimeField()
	price = models.CharField(max_length=30)
	is_active = models.BooleanField()
