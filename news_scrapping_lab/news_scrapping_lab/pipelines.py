from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import psycopg2
import re
from scrapy.pipelines.images import ImagesPipeline
import os

# Pipeline для обробки даних і збереження в PostgreSQL
class NewsScrappingLabPipeline:
    def open_spider(self, spider):
        try:
            self.conn = psycopg2.connect(
                dbname="news_db",
                 user="postgres",
                password="07042006",
                host="localhost",
                port="5432"
            )
            self.cur = self.conn.cursor()
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS news (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    date VARCHAR(50),
                    link VARCHAR(255) UNIQUE,
                    section VARCHAR(100),
                    image_urls TEXT
                );
            """)
            self.conn.commit()
        except Exception as e:
            spider.logger.error(f"Error connecting to PostgreSQL: {e}")
            raise

    def is_duplicate(self, link):
        self.cur.execute("SELECT EXISTS(SELECT 1 FROM news WHERE link = %s)", (link,))
        return self.cur.fetchone()[0]

    def process_item(self, item, spider):
        try:
            date_str = item.get("date")
            if date_str:
                year = date_str.split('.')[2].split(',')[0]
                item["date"] = year

            title = item.get("title")
            if title:
                item["title"] = re.sub(r'\s*\(.*\)', '', title)

            adapter = ItemAdapter(item)
            link = adapter.get("link")

            if self.is_duplicate(link):
                self.cur.execute("""
                    UPDATE news 
                    SET title = %s, date = %s, section = %s, image_urls = %s
                    WHERE link = %s
                """, (
                    adapter.get("title"),
                    adapter.get("date"),
                    adapter.get("section"),
                    ','.join(adapter.get("image_urls", [])),
                    link
                ))
            else:
                self.cur.execute("""
                    INSERT INTO news (title, date, link, section, image_urls)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    adapter.get("title"),
                    adapter.get("date"),
                    link,
                    adapter.get("section"),
                    ','.join(adapter.get("image_urls", []))
                ))

            self.conn.commit()
            return item
        except Exception as e:
            self.conn.rollback()
            raise DropItem(f"Error processing item: {e}")

    def close_spider(self, spider):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

# Pipeline для завантаження зображень
class NewsImagesPipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        image_name = request.url.split('/')[-1]  # Отримуємо ім'я файлу з URL
        return f"img/{image_name}"  # Зберігаємо в папку img

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]  # Отримуємо шляхи завантажених зображень
        if image_paths:
            adapter = ItemAdapter(item)
            adapter['image_paths'] = image_paths  # Додаємо шляхи до айтема
        return item