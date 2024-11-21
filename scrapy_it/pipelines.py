# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import sqlite3

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class ScrapyItPipeline:
    def process_item(self, item, spider):
        return item


class SQLitePipeline:
    def open_spider(self, spider):
        # Подключаемся к базе данных SQLite
        self.connection = sqlite3.connect("jobs.sqlite3")
        self.cursor = self.connection.cursor()

        # Создаем таблицы, если их еще нет
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
        """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS companies_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER UNIQUE,
                description TEXT,
                phone TEXT,
                website TEXT,
                url TEXT,
                FOREIGN KEY (company_id) REFERENCES companies (id)
            )
        """
        )
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS vacancies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER,
                name TEXT,
                url TEXT,
                FOREIGN KEY (company_id) REFERENCES companies (id)
            )
        """
        )
        self.connection.commit()

    def close_spider(self, spider):
        # Закрываем соединение с базой данных
        self.connection.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Обработка вакансии
        if "vacancy_name" in adapter:
            self.cursor.execute(
                "INSERT OR IGNORE INTO companies (name) VALUES (?)",
                (adapter["vacancy_company"],),
            )
            self.connection.commit()

            self.cursor.execute(
                "SELECT id FROM companies WHERE name = ?", (adapter["vacancy_company"],)
            )
            company_id = self.cursor.fetchone()[0]

            self.cursor.execute(
                "INSERT INTO vacancies (name, company_id, url) VALUES (?, ?, ?)",
                (adapter["vacancy_name"], company_id, adapter["vacancy_url"]),
            )
            self.connection.commit()

        # Обработка информации о компании
        elif "company_name" in adapter:
            self.cursor.execute(
                "SELECT id FROM companies WHERE name = ?", (adapter["company_name"],)
            )
            company_id = self.cursor.fetchone()

            if company_id:
                company_id = company_id[0]
                self.cursor.execute(
                    """
                    INSERT OR REPLACE INTO companies_info (company_id, description, phone, website, url)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        company_id,
                        adapter["company_description"],
                        adapter["company_phone"],
                        adapter["company_website"],
                        adapter["company_url"],
                    ),
                )
                self.connection.commit()

        return item
