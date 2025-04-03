import scrapy
from news_scrapping_lab.items import NewsScrappingLab
from scrapy.http import Request
import json


class ZakarpattyaXPathSpider(scrapy.Spider):
    name = "zakarpattyaxpath"
    allowed_domains = ["zakarpattya.net.ua", "localhost"]
    start_urls = ["https://zakarpattya.net.ua"]


    # API URL для надсилання новин
    API_URL = "http://localhost:8000/add-news/"

    def parse(self, response):
        news_list = response.xpath("//div[@id='topmenu']")

        if news_list:
            for item in news_list.xpath(".//a/@href").getall():
                section_url = response.urljoin(item)
                yield scrapy.Request(section_url, callback=self.parse_section)
        else:
            self.logger.error(f"Error: Could not find 'topmenu' on {response.url}")

    def parse_section(self, response):
        news_list = response.xpath("//div[contains(@class, 'pubView')]")

        if not news_list:
            self.logger.error(f"Error: No elements with class 'pubView' found on {response.url}")
            return

        for post in news_list.xpath(".//div[contains(@class, 'postList')]"):
            title = post.xpath(".//a/text()").get(default="Без заголовка").strip()
            date = post.xpath(".//span[contains(@class, 'pdate')]/text()").get(default="Без дати").strip()
            link = post.xpath(".//a/@href").get(default="Без посилання")
            link = response.urljoin(link) if link != "Без посилання" else link

            # Отримання зображень
            image_urls = post.xpath(".//img/@src").getall()
            image_urls = [response.urljoin(img_url) for img_url in image_urls]

            # Форматування новини для відправки
            news_item = {
                "title": title,
                "date": date,
                "link": link,
                "section": response.url,
                "image_urls": image_urls
            }

            # Надсилання новини на FastAPI
            yield Request(
                url=self.API_URL,
                method='POST',
                body=json.dumps([news_item]),  # Перетворення новини в JSON
                headers={'Content-Type': 'application/json'},
                callback=self.handle_api_response
            )

    def handle_api_response(self, response):
        # Обробка відповіді від API
        if response.status == 200:
            self.logger.info("News successfully sent to the API.")
        else:
            self.logger.error(f"Failed to send news to the API. Status code: {response.status}")
