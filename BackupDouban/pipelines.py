# -*- coding: utf-8 -*-
from json import dumps
from BackupDouban.model import (
    User,
    DoubanBook,
    UserBook,
    db_connect,
    create_channel_table,
)
from sqlalchemy.orm import sessionmaker
from scrapy.exceptions import DropItem

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class StartSQLlitePipeline(object):
    def open_spider(self, spider):
        engine = db_connect()
        create_channel_table(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def process_item(self, item, spider):
        user_name = item.get("user_name")
        if not user_name:
            return item
        user = User(user=user_name)
        self.session.add(user)
        self.session.commit()
        return item

    def close_spider(self, spider):
        self.session.close()


class DoubanBookPipline(object):
    def open_spider(self, spider):
        engine = db_connect()
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def process_item(self, item, spider):
        isbn = item.get("isbn")
        if not isbn:
            return item
        douban_book = DoubanBook(
            id=item.get("id"),
            title=item.get("book_title"),
            author=dumps(item.get("author")),
            publisher=item.get("publisher"),
            original_name=item.get("original_name"),
            translator=dumps(item.get("translator")),
            publication_year=item.get("publication_year"),
            pages=item.get("pages"),
            price=item.get("price"),
            binding=item.get("binding"),
            isbn=item.get("isbn"),
            unified_number=item.get("unified_number"),
            intro=dumps(item.get("intro")),
        )
        self.session.add(douban_book)
        self.session.commit()
        return item


class UserBookPipeline(object):
    def open_spider(self, spider):
        engine = db_connect()
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def process_item(self, item, spider):
        title = item.get("title")
        if not title:
            return item
        isbn = item.get("isbn")
        if isbn:
            return item
        user_book = UserBook(
            title=title,
            info=item.get("info"),
            short_note=item.get("short_note"),
            user_id=item.get("name"),
            douban_id=item.get("douban_id"),
            status=item.get("status"),
        )
        self.session.add(user_book)
        self.session.commit()
        return item