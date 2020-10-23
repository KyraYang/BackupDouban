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
    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String(120), nullable=False, unique=True)
    books = relationship("DoubanBooks")


class DoubanBooks(Base):
    __tablename__ = "douban_books"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(120), nullable=False)
    author = Column(String(120), nullable=False)
    publisher = Column(String(120), nullable=False)
    translators = Column(String(120), nullable=False)
    publication_year = Column(String(120), nullable=False)
    pages = Column(String(120), nullable=False)
    bingding = Column(String(120), nullable=False)
    isbn = Column(String(120), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
