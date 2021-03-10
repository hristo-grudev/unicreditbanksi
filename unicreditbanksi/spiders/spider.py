import json

import scrapy

from scrapy.loader import ItemLoader
from w3lib.html import remove_tags

from ..items import UnicreditbanksiItem
from itemloaders.processors import TakeFirst

import requests

base_url = "https://www.unicreditbank.si/show.pws.financialarticles.html"

base_payload="number={}&appName=cee2020-pws-si&pagePath=%2Fcontent%2Fcee2020-pws-si%2Fsi%2Fprebivalstvo%2Fclanki&componentType=allArticles"
headers = {
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'sec-ch-ua': '"Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"',
  'Accept': 'application/json, text/javascript, */*; q=0.01',
  'CSRFToken': '0gx43bDycux1itQJJkT0',
  'X-Requested-With': 'XMLHttpRequest',
  'sec-ch-ua-mobile': '?0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36',
  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'Origin': 'https://www.unicreditbank.si',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Dest': 'empty',
  'Referer': 'https://www.unicreditbank.si/si/prebivalstvo/clanki.html',
  'Accept-Language': 'en-US,en;q=0.9,bg;q=0.8',
  'Cookie': 'renderid=rend6019; _ga=GA1.2.1679256525.1615376845; _gid=GA1.2.1754664406.1615376845; __mauuid=ef5bec3e-1f32-4c77-8b90-15231ffcdd7c; __mauuid=ef5bec3e-1f32-4c77-8b90-15231ffcdd7c; __mauuid=ef5bec3e-1f32-4c77-8b90-15231ffcdd7c; zarget_visitor_info=%7B%7D; zarget_user_id=a737f1e3-3871-464e-bdfc-4fe51fbcc28e; hideLN=yes; JSESSIONID=0000uri7AXhlRa-Ex6c3U8Z724p:1cp6kae20; TS01b45e18=01117f0e611f551bd06f7b57cdac65047b66e92ca68842cae0976ab045b23dbf614fc32cf7018245c7afbd895069783f102262c802ff79f5ec1addc8144e1bb77e6ee358c0; _gat_UA-62423961-11=1; _gat_UA-62423961-19=1; TS01b45e18=01357f8a032908f15b60937121195695e82cfb56055aeb04ec57ae2a7052c21f29286cca85b634ec118e5217ceac6e6dac30c19ca8'
}


class UnicreditbanksiSpider(scrapy.Spider):
	name = 'unicreditbanksi'
	start_urls = ['https://www.unicreditbank.si/si/prebivalstvo/clanki.html']
	page = 1

	def parse(self, response):
		data = requests.request("POST", base_url, headers=headers, data=base_payload.format(self.page))
		raw_data = json.loads(data.text)
		for post in raw_data['resultsJSON']:
			url = post['articlePath']
			yield response.follow(url, self.parse_post)

		if self.page < raw_data['numberOfPages']:
			self.page += 1
			yield response.follow(response.url, self.parse, dont_filter=True)

	def parse_post(self, response):
		title = response.xpath('//div[@class="col-xs-24"]/h2/text()').get()
		description = response.xpath('//div[@class="col-xs-24 large"]//text()[normalize-space()]').getall()
		description = [remove_tags(p).strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=UnicreditbanksiItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)

		return item.load_item()
