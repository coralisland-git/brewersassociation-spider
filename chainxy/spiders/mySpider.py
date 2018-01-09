import scrapy
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem
from lxml import html
import pdb

class mySpider(scrapy.Spider):
	name='myspider'
	def start_requests(self):
		init_url = 'https://www.brewersassociation.org/directories/breweries/'
		yield scrapy.Request(url=init_url, callback=self.body)

	def body(self, response):
		country_list = response.xpath('//ul[@id="country_select"]//li/@data-country-id').extract()
		for country in country_list:
			url = 'https://www.brewersassociation.org/wp-admin/admin-ajax.php'
			formdata={
				"action":"get_breweries",
				"_id":country,
				"types[]":"Micro",
				"search_by":"country"
			}
			header = {
				"accept":"*/*",
				"accept-encoding":"gzip, deflate, br",
				"content-type":"application/x-www-form-urlencoded; charset=UTF-8",
				"x-requested-with":"XMLHttpRequest"
			}
			yield scrapy.FormRequest(url=url, headers=header, method="post", formdata=formdata, callback=self.parse, meta={'country':country} )

	def parse(self, response):
		locations = response.xpath('//div[@class="brewery"]//ul[@class="vcard simple brewery-info"]')
		for location in locations:
			item = ChainItem()
			item['name'] = location.xpath('.//li[@class="name"]/text()').extract_first()
			item['country'] = response.meta['country']
			item['address'] = location.xpath('.//li[@class="address"]/text()').extract_first()
			item['phone'] = location.xpath('.//li[@class="telephone"]/text()').extract_first()
			item['website'] = location.xpath('.//li[@class="brewery_type"]/a/@href').extract_first()
			yield item

	def validate(self, param):
		try:
			return param.strip()
		except:
			return ''
