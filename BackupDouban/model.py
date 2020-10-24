from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def db_connect():
    return create_engine("sqlite:///douban.db", echo=True)


def create_channel_table(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


class User(Base):
    __tablename__ = "users"
    user = Column(String(120), primary_key=True)
    books = relationship("UserBook")


class DoubanBook(Base):
    __tablename__ = "douban_books"
    id = Column(Integer, primary_key=True)  # douban id
    title = Column(String(120), nullable=False)
    author = Column(String(120), nullable=False)
    publisher = Column(String(120), nullable=False)
    translators = Column(String(120), nullable=False)
    publication_year = Column(String(120), nullable=False)
    pages = Column(String(120), nullable=False)
    bingding = Column(String(120), nullable=False)
    isbn = Column(String(120), nullable=False)
    userbook = relationship("UserBook")


class UserBook(Base):
    __tablename__ = "user_books"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(120), nullable=False)
    info = Column(String(120), nullable=False)
    short_note = Column(String(500), nullable=False)
    user_id = Column(String(120), ForeignKey("users.user"))
    douban_id = Column(Integer, ForeignKey("douban_books.id"))
    status = Column(String(120), nullable=False)