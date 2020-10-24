# -*- coding: utf-8 -*-
import click
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.signalmanager import dispatcher
from crawl_wishes import crawl_wishes
from crawl_user import crawl_user


@click.command()
@click.argument("account_name")
def main(account_name):
    crawl_user()
    # doing_url = (result[0])["doing"]
    # done_url = (result[0])["done"]
    crawl_wishes(account_name)


if __name__ == "__main__":
    main()