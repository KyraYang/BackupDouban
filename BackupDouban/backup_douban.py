# -*- coding: utf-8 -*-
import click
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.user import UserSpider
from scrapy.signalmanager import dispatcher
from scrapy import signals


@click.command()
@click.argument("account_name")
def main(account_name):
    result = []

    def crawler_results(item):
        result.append(item)

    dispatcher.connect(crawler_results, signal=signals.item_scraped)
    user = CrawlerProcess(get_project_settings())
    user.crawl(UserSpider, account_name=account_name)
    user.start()
    print("information:", result)


if __name__ == "__main__":
    main()