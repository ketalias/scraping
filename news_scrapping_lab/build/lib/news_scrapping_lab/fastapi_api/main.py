from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Модель для новини
class NewsItem(BaseModel):
    title: str
    date: str
    link: str
    section: str
    image_urls: List[str]

# Тимчасове сховище для новин (поки без бази даних)
news_storage = []

# API для отримання новин
@app.post("/add-news/")
async def add_news(news: List[NewsItem]):
    # Додаємо новини до локального сховища
    news_storage.extend(news)
    return {"message": "News received successfully", "data": news}

# API для отримання всіх новин
@app.get("/get-news/")
async def get_news():
    # Повертаємо всі новини зі сховища
    return {"news": news_storage}
