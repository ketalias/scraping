from fastapi import FastAPI, HTTPException
from typing import List
from .schemas import NewsSchema
from .storage import storage

# Ініціалізація FastAPI
app = FastAPI()

# Кореневий маршрут для перевірки сервера
@app.get("/")
def read_root():
    return {"message": "API для новин працює!"}

# Отримати всі новини
@app.get("/news", response_model=List[NewsSchema])
def get_news():
    return storage

# Додати одну новину
@app.post("/news", response_model=NewsSchema)
def create_news(news: NewsSchema):
    storage.append(news)
    return news

# Додати декілька новин
@app.post("/news/bulk")
def create_bulk_news(news_list: List[NewsSchema]):
    storage.extend(news_list)
    return {"message": "Новини успішно додано", "total": len(news_list)}
