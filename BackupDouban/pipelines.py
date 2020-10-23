# -*- coding: utf-8 -*-
from BackupDouban.model import (
    User,
    DoubanBook,
    UserBook,
    db_connect,
    create_channel_table,
)
from sqlalchemy.orm import sessionmaker

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class SQLlitePipeline(object):
    def open_spider(self, spider):
        engine = db_connect()
        create_channel_table(engine)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def process_item(self, item, spider):
        user = User(user=item.get("name"))
        self.session.add(user)
        user_book = UserBook(
            title=item.get("title"),
            info=item.get("info"),
            shot_note=item.get("shot_note"),
            user_id=user.id,
            douban_id=item.get("douban_id"),
        )
        self.session.add(user_book)
        self.session.commit()
        return item

    def close_spider(self, spider):
        self.session.close()