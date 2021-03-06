# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-28 12:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('url', models.CharField(max_length=255, unique=True)),
                ('last_checked', models.DateTimeField()),
                ('price', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=255)),
                ('strike_price', models.CharField(max_length=30)),
                ('email', models.CharField(max_length=255)),
                ('negative_words', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='item',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ebay_items.Product'),
        ),
    ]
