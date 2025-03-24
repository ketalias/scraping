import scrapy
import requests
from bs4 import BeautifulSoup
from news_scrapping_lab.items import NewsScrappingLab

class ZakarpattyaSpider(scrapy.Spider):
    name = "zakarpattya"
    allowed_domains = ["zakarpattya.net.ua"]
    start_urls = ["https://zakarpattya.net.ua"]

    def parse(self, response):
        page = requests.get(response.url)
        soup = BeautifulSoup(page.text, "html.parser")
        news_list = soup.find(id="topmenu")
        
        if news_list:
            for item in news_list.find_all("a", href=True):
                section_name = item.text.strip()
                section_url = response.urljoin(item.get("href"))
                yield scrapy.Request(
                    section_url,
                    callback=self.parse_section,
                    meta={'section_name': section_name}
                )
        else:
            self.logger.error(f"Error: Could not find 'topmenu' on {response.url}")

    def parse_section(self, response):
        section_name = response.meta['section_name']
        page = requests.get(response.url)
        soup = BeautifulSoup(page.text, "html.parser")
        news_list = soup.find(class_="pubView")
        
        if news_list is None:
            self.logger.error(f"Error: No elements with class 'pubView' found on {response.url}")
            return

        for post in news_list.find_all(class_="postList"):
            title_tag = post.find("h3")
            link_tag = post.find("a")
            date_tag = post.find(class_="pdate")
            img_tag = post.find("img")
            
            title = title_tag.text.strip() if title_tag else "Без заголовка"
            date = date_tag.text.strip() if date_tag else "Без дати"
            link = response.urljoin(link_tag["href"]) if link_tag else "Без посилання"
            img_url = img_tag.get("src") if img_tag else ""
            
            yield NewsScrappingLab(
                title=title,
                date=date,
                link=link,
                section=section_name,
                image_urls=[f"https://zakarpattya.net.ua{img_url}"] if img_url else []
            )