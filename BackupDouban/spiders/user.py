# -*- coding: utf-8 -*-
import scrapy
import re


class UserSpider(scrapy.Spider):
    name = "user"
    allowed_domains = ["douban.com"]

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36",
    }
    cookies = {
        "Cookie": 'gr_user_id=81e9b4b7-e480-4aa2-a106-33d3e7886f12; _vwo_uuid_v2=D81AB8817D3DAA7036B6AF8ADFE7D6B88|b77c350070cd48b1e53a8ffec068377e; douban-profile-remind=1; douban-fav-remind=1; _ga=GA1.2.663498264.1591154206; push_doumail_num=0; __gads=ID=65c30802bc9ef71b:T=1597200790:S=ALNI_Ma7UuO8WAdpP7fPAJ1EMuTr_h32Rw; viewed="26259304_25909107_26860965_4268921_6722883_1311655_26871302_27081369_34863798_6516782"; push_noty_num=0; __utmz=30149280.1600839872.361.82.utmcsr=accounts.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/passport/login; bid=9OiP8Ix4GNY; __utma=30149280.663498264.1591154206.1603266055.1603348701.369; __utmc=30149280; ll="108288"; dbcl2="225451546:amQVsruKABM"; ck=gV23; ap_v=0,6.0; _pk_ref.100001.8cb4=%5B%22%22%2C%22%22%2C1603358310%2C%22https%3A%2F%2Fbook.douban.com%2Fsubject%2F25981424%2F%22%5D; _pk_ses.100001.8cb4=*; __utmv=30149280.22545; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03=3e44d9e4-3784-4f47-ad9c-857a83d2fc97; gr_cs1_3e44d9e4-3784-4f47-ad9c-857a83d2fc97=user_id%3A1; gr_session_id_22c937bbd8ebd703f2d8e9445f7dfd03_3e44d9e4-3784-4f47-ad9c-857a83d2fc97=true; _pk_id.100001.8cb4=72087ca87adcde96.1591154128.145.1603359923.1603352518.; __utmb=30149280.80.10.1603348701'
    }

    def start_requests(self):
        yield scrapy.Request(
            url="https://www.douban.com/people/{}/".format(self.account_name),
            callback=self.parse,
            headers=self.headers,
            cookies=self.cookies,
        )

    def parse(self, response):
        account = response.xpath("normalize-space(//h1/text())").get()
        if account:
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
                headers=self.headers,
                cookies=self.cookies,
            )
        if wishes_url:
            yield scrapy.Request(
                url=wishes_url,
                callback=self.parse_wishes,
                headers=self.headers,
                cookies=self.cookies,
            )
        if done_url:
            yield scrapy.Request(
                url=done_url,
                callback=self.parse_done,
                headers=self.headers,
                cookies=self.cookies,
            )

    def list_books_parse(self, book, status):
        title = book.xpath("normalize-space(.//h2/a/text())").get()
        subtitle = book.xpath(".//h2/a/span/text()").get()
        if subtitle:
            title = title + subtitle
        book_url = book.xpath(".//h2/a/@href").get()
        douban_id = re.search(r"\d+", book_url).group(0)
        return {
            "name": self.account_name,
            "title": title,
            "info": book.xpath("normalize-space(.//div[@class='pub']/text())").get(),
            "short_note": book.xpath(
                "normalize-space(.//div[@class='short-note']/p/text())"
            ).get(),
            "douban_id": douban_id,
            "status": status,
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
            yield book_dict
        next_page = self.next_page(response)
        if next_page:
            yield scrapy.Request(
                url=next_page,
                callback=self.parse_doing,
                headers=self.headers,
                cookies=self.cookies,
            )

    def parse_wishes(self, response):
        books = response.xpath('//li[@class="subject-item"]/div[@class="info"]')
        for book in books:
            book_dict = self.list_books_parse(book, "wishes")
            yield book_dict
        next_page = self.next_page(response)
        if next_page:
            yield scrapy.Request(
                url=next_page,
                callback=self.parse_wishes,
                headers=self.headers,
                cookies=self.cookies,
            )

    def parse_done(self, response):
        books = response.xpath('//li[@class="subject-item"]/div[@class="info"]')
        for book in books:
            book_dict = self.list_books_parse(book, "done")
            yield book_dict
        next_page = self.next_page(response)
        if next_page:
            yield scrapy.Request(
                url=next_page,
                callback=self.parse_done,
                headers=self.headers,
                cookies=self.cookies,
            )
