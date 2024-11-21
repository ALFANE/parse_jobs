import scrapy
from scrapy import Request

from scrapy_it.items import VacancyItem, CompanyItem


class WorkuaSpider(scrapy.Spider):
    name = "workua"
    allowed_domains = ["work.ua"]
    start_urls = ["https://www.work.ua/jobs-it/?advs=1"]

    site_url = "https://work.ua"

    def parse(self, response):
        # Парсинг вакансий на стартовой странице
        for vacancy in response.css("div.card-hover"):
            vacancy_name = vacancy.css("h2 a::text").get()
            vacancy_link = vacancy.css("h2 a::attr(href)").get()
            if vacancy.css("span.mr-xs  span.strong-600::text").get():
                company_name = vacancy.css("span.mr-xs  span.strong-600::text").get()
            else:
                company_name = vacancy.css("div.mt-xs  span  span::text").get()
            # print(vacancy_name, vacancy_link, company_name)

            if vacancy_link:
                vacancy_link = self.site_url + vacancy_link
                yield Request(
                    vacancy_link,
                    callback=self.parse_vacancy_page,
                    meta={
                        "vacancy_name": vacancy_name.strip(),
                        "company_name": company_name.strip() if company_name else None,
                    },
                )

        # Переход на следующую страницу
        next_page_url = response.css(
            "ul.pagination > li.add-left-default > a::attr(href)"
        ).get()
        if next_page_url:
            yield Request(self.site_url + next_page_url, callback=self.parse)

    def parse_vacancy_page(self, response):
        # Парсинг информации о вакансии
        vacancy_name = response.meta["vacancy_name"]
        company_name = response.meta["company_name"]
        company_link = response.css("ul.list-unstyled li a.inline::attr(href)").get()
        # print(vacancy_name, company_name, company_link)

        vacancy_item = VacancyItem()
        vacancy_item["vacancy_name"] = vacancy_name
        vacancy_item["vacancy_company"] = company_name
        vacancy_item["vacancy_url"] = response.url

        yield vacancy_item

        if company_link:
            company_link = self.site_url + company_link
            yield Request(
                company_link,
                callback=self.parse_company_page,
                meta={"company_name": company_name},
            )

    def parse_company_page(self, response):
        # Парсинг информации о компании
        company_name = response.meta["company_name"]
        company_description = response.css("div.company-description *::text").getall()
        company_phone = response.css("li.text-indent.mt-sm a.nowrap::attr(href)").get()
        company_phone = (
            company_phone.replace("tel:", "").strip() if company_phone else None
        )
        company_website = response.css(
            'li.text-indent.mb-0 a[href^="http"]::attr(href)'
        ).get()

        # print(company_name, company_phone, company_website)

        company_item = CompanyItem()
        company_item["company_name"] = company_name
        company_item["company_description"] = (
            " ".join(company_description).strip() if company_description else None
        )
        company_item["company_phone"] = company_phone.strip() if company_phone else None
        company_item["company_website"] = (
            company_website.strip() if company_website else None
        )
        company_item["company_url"] = response.url

        yield company_item
