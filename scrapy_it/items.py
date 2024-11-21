# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

# import scrapy
from scrapy import Item, Field


class ScrapyItItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class VacancyItem(Item):
    vacancy_name = Field()  # Название вакансии
    vacancy_company = Field()  # Название компании
    vacancy_url = Field()  # URL страницы вакансии


class CompanyItem(Item):
    company_name = Field()  # Название компании
    company_description = Field()  # Описание компании
    company_phone = Field()  # Номер телефона компании
    company_website = Field()  # Веб-сайт компании
    company_url = Field()  # URL страницы компании
