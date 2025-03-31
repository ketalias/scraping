import scrapy
import requests
from news_scrapping_lab.items import NewsScrappingLab

class ZakarpattyaXPathSpider(scrapy.Spider):
    name = "zakarpattyaxpath"
    allowed_domains = ["zakarpattya.net.ua"]
    start_urls = ["https://zakarpattya.net.ua"]
    api_url = "http://127.0.0.1:8000/news"  # Адреса вашого API для відправки новин

    def parse(self, response):
        news_list = response.xpath("//div[@id='topmenu']")
        
        if news_list:
            for item in news_list.xpath(".//a/@href").getall():
                section_name = item.strip()
                section_url = response.urljoin(item)
                yield scrapy.Request(section_url, callback=self.parse_section, meta={'section_name': section_name})
        else:
            self.logger.error(f"Error: Could not find 'topmenu' on {response.url}")

    def parse_section(self, response):
        section_name = response.meta['section_name']
        
        news_list = response.xpath("//div[contains(@class, 'pubView')]")
        
        if not news_list:
            self.logger.error(f"Error: No elements with class 'pubView' found on {response.url}")
            return

        for post in news_list.xpath(".//div[contains(@class, 'postList')]"):
            title = post.xpath(".//a/text()").get(default="Без заголовка").strip()
            date = post.xpath(".//span[contains(@class, 'pdate')]/text()").get(default="Без дати").strip()
            link = post.xpath(".//a/@href").get(default="Без посилання")
            link = response.urljoin(link) if link != "Без посилання" else link
            
            # Створюємо новину
            news_item = NewsScrappingLab(
                title=title,
                date=date,
                link=link,
                section=section_name
            )
            
            # Відправляємо новину на API
            self.send_news_to_api(news_item)

    def send_news_to_api(self, news_item):
        # Відправлення новини через POST запит на API
        response = requests.post(self.api_url, json={
            "title": news_item["title"],
            "date": news_item["date"],
            "link": news_item["link"],
            "section": news_item["section"]
        })
        
        if response.status_code == 200:
            self.logger.info(f"Новина '{news_item['title']}' успішно надіслана на API.")
        else:
            self.logger.error(f"Помилка при відправці новини '{news_item['title']}' на API.")
