# -*- coding: utf-8 -*-
import click
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.user import UserSpider
from spiders.wishes_book import WishesBookSpider
from scrapy.signalmanager import dispatcher
from scrapy import signals


def crawl_user(account_name):
    result = []

    def crawler_reciever(item):
        result.append(item)

    dispatcher.connect(crawler_reciever, signal=signals.item_scraped)
    user = CrawlerProcess(get_project_settings())
    user.crawl(UserSpider, account_name=account_name)
    user.start()
    if not result:
        print("No this user.")
        return
    return result[0]


def crawl_wishes_books(url):
    result = []

    def crawler_reciever(item):
        result.append(item)

    dispatcher.connect(crawler_reciever, signal=signals.item_scraped)
    user = CrawlerProcess(get_project_settings())
    user.crawl(WishesBookSpider, url=url)
    user.start()


@click.command()
@click.argument("account_name")
def main(account_name):
    user_info = crawl_user(account_name)
    # doing_url = (result[0])["doing"]
    print("name:", user_info["name"])
    wishes_url = user_info["wishes"]
    # done_url = (result[0])["done"]
    if wishes_url:
        crawl_wishes_books(wishes_url)


if __name__ == "__main__":
    main()