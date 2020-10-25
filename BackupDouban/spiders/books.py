# -*- coding: utf-8 -*-
import scrapy
import re


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["douban.com"]
    # eaders = {"User-Agent": user_agent.random}
    cookies = {
        "Cookie": 'gr_user_id=81e9b4b7-e480-4aa2-a106-33d3e7886f12; _vwo_uuid_v2=D81AB8817D3DAA7036B6AF8ADFE7D6B88|b77c350070cd48b1e53a8ffec068377e; douban-profile-remind=1; douban-fav-remind=1; _ga=GA1.2.663498264.1591154206; __gads=ID=65c30802bc9ef71b:T=1597200790:S=ALNI_Ma7UuO8WAdpP7fPAJ1EMuTr_h32Rw; viewed="26259304_25909107_26860965_4268921_6722883_1311655_26871302_27081369_34863798_6516782"; bid=9OiP8Ix4GNY; ll="108288"; __utmz=30149280.1603472866.375.83.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/people/KyraYang/; push_noty_num=0; __utmc=30149280; ap_v=0,6.0; push_doumail_num=0; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03=a7d042a7-4678-4d86-b96e-b1fc272d750d; gr_cs1_a7d042a7-4678-4d86-b96e-b1fc272d750d=user_id%3A1; __utma=30149280.663498264.1591154206.1603550809.1603553848.380; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03_a7d042a7-4678-4d86-b96e-b1fc272d750d=true; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1603554493%2C%22https%3A%2F%2Fbook.douban.com%2F%22%5D; _pk_ses.100001.8cb4=*; __utmt=1; __utmt_douban=1; dbcl2="225451546:EvLAI0ttdEQ"; ck=2NUm; __utmv=30149280.22545; _pk_id.100001.8cb4=72087ca87adcde96.1591154128.155.1603554571.1603536581.; __utmb=30149280.11.10.1603553848'
    }
    headers = {
        "Referer": "https://www.douban.com/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6",
    }

    def start_requests(self):
        yield scrapy.Request(
            url="https://www.douban.com/people/{}/".format(self.account_name),
            callback=self.parse,
            headers=self.headers,
            cookies=self.cookies,
            meta={"dont_redirect": True, "handle_httpstatus_list": [302]},
        )

    def parse(self, response):
        print(response.request.headers)
        account = response.xpath("normalize-space(//h1/text())").get()
        if not account:
            return "No this account."
        yield {"user_name": self.account_name}
        doing_url = response.xpath(
            '//div[@id="book"]/h2/span/a[contains(@href, "/do")]/@href'
        ).get()
        wishes_url = response.xpath(
            '//div[@id="book"]/h2/span/a[contains(@href, "wish")]/@href'
        ).get()
        done_url = response.xpath(
            '//div[@id="book"]/h2/span/a[contains(@href, "collect")]/@href'
        ).get()
        if doing_url:
            yield scrapy.Request(
                url=doing_url,
                callback=self.parse_doing,
                # headers=self.headers,
                cookies=self.cookies,
            )
        if wishes_url:
            yield scrapy.Request(
                url=wishes_url,
                callback=self.parse_wishes,
                # headers=self.headers,
                cookies=self.cookies,
            )
        if done_url:
            yield scrapy.Request(
                url=done_url,
                callback=self.parse_done,
                # headers=self.headers,
                cookies=self.cookies,
            )

    def list_books_parse(self, book, status):
        title = book.xpath("normalize-space(.//h2/a/text())").get()
        subtitle = book.xpath(".//h2/a/span/text()").get()
        if subtitle:
            title = title + subtitle
        book_url = book.xpath(".//h2/a/@href").get()
        douban_id = re.search(r"\d+", book_url).group(0)
        rating = book.xpath('.//span[contains(@class, "rating")]/@class').get()
        date = book.xpath('.//span[@class="date"]/text()').get()
        added_date = date.split()[0]
        from BackupDouban.model import (
            DoubanBook,
            db_connect,
        )
        from sqlalchemy.orm import sessionmaker

        engine = db_connect()
        Session = sessionmaker(bind=engine)
        session = Session()
        to_fetch = False
        if not session.query(DoubanBook).get(douban_id):
            to_fetch = True
        return {
            "name": self.account_name,
            "title": title,
            "rating": rating[6] if rating else "",
            "added_date": added_date,
            "short_note": book.xpath(
                "normalize-space(.//div[@class='short-note']/p/text())"
            ).get(),
            "douban_id": douban_id,
            "status": status,
            "book_url": book_url,
            "to_fetch": to_fetch,
        }

    def next_page(self, response):
        next_page = response.xpath('//span[@class="next"]/a/@href').get()
        if not next_page:
            return
        return f"https://book.douban.com{next_page}"

    def parse_doing(self, response):
        books = response.xpath('//li[@class="subject-item"]/div[@class="info"]')
        for book in books:
            book_dict = self.list_books_parse(book, "doing")
            if book_dict["to_fetch"]:
                yield scrapy.Request(
                    url=book_dict["book_url"],
                    callback=self.parse_book,
                    # headers=self.headers,
                    cookies=self.cookies,
                    meta=book_dict,
                )
            yield book_dict
        next_page = self.next_page(response)
        if next_page:
            yield scrapy.Request(
                url=next_page,
                callback=self.parse_doing,
                # headers=self.headers,
                cookies=self.cookies,
            )

    def parse_wishes(self, response):
        books = response.xpath('//li[@class="subject-item"]/div[@class="info"]')
        for book in books:
            book_dict = self.list_books_parse(book, "wishes")

            if book_dict["to_fetch"]:
                yield scrapy.Request(
                    url=book_dict["book_url"],
                    callback=self.parse_book,
                    # headers=self.headers,
                    cookies=self.cookies,
                    meta=book_dict,
                )
            yield book_dict
        next_page = self.next_page(response)
        if next_page:
            yield scrapy.Request(
                url=next_page,
                callback=self.parse_wishes,
                # headers=self.headers,
                cookies=self.cookies,
            )

    def parse_done(self, response):
        books = response.xpath('//li[@class="subject-item"]/div[@class="info"]')
        for book in books:
            book_dict = self.list_books_parse(book, "done")
            if book_dict["to_fetch"]:
                yield scrapy.Request(
                    url=book_dict["book_url"],
                    callback=self.parse_book,
                    # headers=self.headers,
                    cookies=self.cookies,
                    meta=book_dict,
                )
            yield book_dict
        next_page = self.next_page(response)
        if next_page:
            yield scrapy.Request(
                url=next_page,
                callback=self.parse_done,
                # headers=self.headers,
                cookies=self.cookies,
            )

    def parse_book(self, response):
        book_info = response.xpath("//div[@id='info']")
        authors = book_info.xpath(
            ".//descendant::span[contains(text(), '作者')]/following-sibling::a[count(preceding-sibling::span)=1]/text()"
        ).getall()
        if not authors:
            authors = book_info.xpath(
                ".//span[contains(text(), '作者')]/following-sibling::a[count(preceding-sibling::span)=1]/text()"
            ).getall()
        translators = book_info.xpath(
            ".//descendant::span[contains(text(), '译者')]/following-sibling::a[count(preceding-sibling::span)=1]/text()"
        ).getall()
        if not translators:
            translators = book_info.xpath(
                ".//span[contains(text(), '译者')]/following-sibling::a[count(preceding-sibling::span)=1]/text()"
            ).getall()
        intro = response.xpath(
            '//span[@class="all hidden"]/descendant::div[@class="intro"]/p/text()'
        ).getall()
        if not intro:
            intro = response.xpath('//div[@class="intro"]/p/text()').getall()
        yield {
            "id": response.meta["douban_id"],
            "book_title": response.meta["title"],
            "author": authors,
            "publisher": book_info.xpath(
                "normalize-space(.//span[contains(text(), '出版社')]/following-sibling::text()[1])"
            ).get(),
            "original_name": book_info.xpath(
                "normalize-space(.//span[contains(text(), '原作名')]/following-sibling::text()[1])"
            ).get(),
            "translator": translators,
            "publication_year": book_info.xpath(
                "normalize-space(.//span[contains(text(), '出版年')]/following-sibling::text()[1])"
            ).get(),
            "pages": book_info.xpath(
                "normalize-space(.//span[contains(text(), '页数')]/following-sibling::text()[1])"
            ).get(),
            "price": book_info.xpath(
                "normalize-space(.//span[contains(text(), '定价')]/following-sibling::text()[1])"
            ).get(),
            "binding": book_info.xpath(
                "normalize-space(.//span[contains(text(), '装帧')]/following-sibling::text()[1])"
            ).get(),
            "isbn": book_info.xpath(
                "normalize-space(.//span[contains(text(), 'ISBN')]/following-sibling::text()[1])"
            ).get(),
            "unified_number": book_info.xpath(
                "normalize-space(.//span[contains(text(), '统一书号')]/following-sibling::text()[1])"
            ).get(),
            "intro": intro,
        }
