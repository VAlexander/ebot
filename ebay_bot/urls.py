"""ebay_bot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
	url(r'^$', 'ebay_items.views.show_main_page', name='show_main_page'),
	url(r'^products/$', 'ebay_items.views.list_products', name='list_products'),
	url(r'^products/(\d+)/$', 'ebay_items.views.product_details', name='product_details'),
	url(r'^products/(\d+)/delete', 'ebay_items.views.delete_product', name='delete_product'),
	url(r'^items/(\d+)/activate', 'ebay_items.views.activate_item', name='activate_item'),
	url(r'^items/(\d+)/deactivate', 'ebay_items.views.deactivate_item', name='deactivate_item'),
    url(r'^upload/', 'ebay_items.views.upload', name='upload'),
	url(r'^run-collect/', 'ebay_items.views.run_collect_product_items_spider', name='run_collect_product_items_spider'),
	url(r'^run-update/', 'ebay_items.views.run_update_items_spider', name='run_update_items_spider'),
	url(r'^run-process/', 'ebay_items.views.run_process_collected_items_spider', name='run_process_collected_items_spider'),
	url(r'^all-active/(\d+)/$', 'ebay_items.views.make_all_items_active', name='make_all_items_active'),
	url(r'^delete-all-products/', 'ebay_items.views.delete_all_products', name='delete_all_products'),
]
