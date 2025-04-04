from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import re
import requests


class NewsScrappingLabPipeline:
    API_URL = "http://localhost:8000/add-news/"

    def process_item(self, item, spider):
        try:
            # Обробка дати
            date_str = item.get("date")
            if date_str:
                item["date"] = date_str.strip()

            # Форматування для API
            news_data = {
                "title": item["title"],
                "date": item["date"],
                "link": item["link"],
                "section": item["section"],
                "image_urls": ','.join(item.get("image_urls", []))
            }

            # Надсилання до API
            self.send_to_api([news_data])
            return item
        except Exception as e:
            raise DropItem(f"Error processing item: {e}")

    def send_to_api(self, data):
        try:
            response = requests.post(self.API_URL, json=data)
            if response.status_code == 200:
                print("Дані успішно надіслані до API")
            else:
                print(f"Помилка API: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Помилка з'єднання з API: {e}")
