from setuptools import setup, find_packages
setup(
name="news_scrapping_lab",
entry_points={'scrapy': ['settings = news_scrapping_lab.settings']},
version="1.0.1",
packages=find_packages(),
)