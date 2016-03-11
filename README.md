## EBot
Automatic EBay crawling and monitoring tool.
## UI Example
![image](https://cloud.githubusercontent.com/assets/7872919/13694722/6bf79c7c-e782-11e5-8613-c9150e6e5389.png)
## Requirements
EBot is built with Django as Web framework and Scrapy as Web scraping framework. It also requires scrapyd for Scrapy spiders deployment and scrapyd-client to control them.
Requirements are installed using PIP.
```sh
pip install scrapy scrapyd scrapyd-client django
```
## Features
* Supports import from CSV file;
* Monitors ebay.com for predefined products;
* Supports stop-words in title to exclude products from monitoring;
* Sends email alerts to user-specified email address;
