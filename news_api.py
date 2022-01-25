import json, pprint
from requests import get
from datetime import datetime
from bs4 import BeautifulSoup, element

class TheHinduReader:
	# pub_date (str) : YYYY/MM/DD
	# pub_type (str) : print | web
	def __init__(self, pub_date, pub_type = 'print'):
		self.__url = f"https://www.thehindu.com/archive/{pub_type}/{pub_date}/"
		self.__response = get(self.__url)
		self.__soup = BeautifulSoup(self.__response.text, features="html.parser")
		self.__sections = self.__soup.select(".tpaper-container section")
		self.__section_urls = []
		
	def get_articles(self):
		for section in self.__sections:
			tmp = {"title" : '', "url" : '', "articles" : []}

			section_heading = section.select_one('.section-header .section-heading .section-list-heading')
			tmp['title'] = section_heading.text.strip()
			tmp['url'] = section_heading.attrs['href']

			articles = section.select('ul.archive-list a')
			for article in articles:
				tmp['articles'].append({"title" : article.text, "url" : article.attrs['href']})

			self.__section_urls.append(tmp)
			
		return json.dumps(self.__section_urls)


# reader = TheHinduReader('2022/01/18', 'web')
# pprint.pprint(json.loads(reader.get_articles()))