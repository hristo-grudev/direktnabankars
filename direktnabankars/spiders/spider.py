import scrapy
from scrapy import Selector

from scrapy.loader import ItemLoader
from w3lib.html import remove_tags

from ..items import DirektnabankarsItem
from itemloaders.processors import TakeFirst

import requests

url = "https://www.direktnabanka.rs/ajaxHelper.php"

base_payload = "func=getListModulesCommon&start_from={}&PageParent=News"
headers = {
  'authority': 'www.direktnabanka.rs',
  'pragma': 'no-cache',
  'cache-control': 'no-cache',
  'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
  'accept': '*/*',
  'x-requested-with': 'XMLHttpRequest',
  'sec-ch-ua-mobile': '?0',
  'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
  'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'origin': 'https://www.direktnabanka.rs',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-mode': 'cors',
  'sec-fetch-dest': 'empty',
  'referer': 'https://www.direktnabanka.rs/o-nama/vesti/',
  'accept-language': 'en-US,en;q=0.9,bg;q=0.8',
  'cookie': '_ga=GA1.3.219116889.1614689361; _fbp=fb.1.1614689361084.490641123; PHPSESSID=jn0ot65ja94hl6lhe0rk44dg03; resolution=1920,1; _gid=GA1.3.1840749038.1615205120; show-notification=true; _gat=1; _mcnc=1'
}


class DirektnabankarsSpider(scrapy.Spider):
	name = 'direktnabankars'
	start_urls = ['https://www.direktnabanka.rs/o-nama/vesti/']
	page = 0

	def parse(self, response):
		payload = base_payload.format(self.page)
		data = requests.request("POST", url, headers=headers, data=payload)
		raw_data = data.text
		post_links = Selector(text=raw_data).xpath('//a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		if_next = raw_data[-3:]
		if if_next == 'yes':
			self.page += 10
			print(self.page)
			yield response.follow(response.url, self.parse, dont_filter=True)


	def parse_post(self, response):
		title = response.xpath('//h1/text()').get()
		description = response.xpath('//div[@class="post"]//text()[normalize-space()]').getall()
		description = [remove_tags(p).strip() for p in description]
		description = ' '.join(description).strip()
		date = response.xpath('//article[@class="intro center"]/time/text()').get()

		item = ItemLoader(item=DirektnabankarsItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
