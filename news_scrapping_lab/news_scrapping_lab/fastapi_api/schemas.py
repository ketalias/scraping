from pydantic import BaseModel

# Схема для новин
class NewsSchema(BaseModel):
    title: str
    date: str
    link: str
    section: str
    image_urls: str
