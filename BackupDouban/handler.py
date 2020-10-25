# -*- coding: utf-8 -*-
from model import (
    db_connect,
)
from json import loads
import pandas as pd


def main():
    account_name = "KyraYang"
    engine = db_connect()
    sql = """
			SELECT
			db.title,
			db.author,
			db.publisher,
			db.original_name,
			db.translator,
			db.intro,
			ub.short_note,
			ub.rating,
			ub.added_date,
			db.publication_year,
			db.pages,
			db.price,
			db.binding,
			db.isbn
			FROM
			user_books AS ub
			JOIN douban_books AS db ON ub.douban_id = db.id
			WHERE
			ub.user_id = (?)
		"""
    books = pd.read_sql_query(sql, engine, params=(account_name,))
    books["author"] = [", ".join(loads(author)) for author in books["author"]]
    books["translator"] = [
        ", ".join(loads(translator)) for translator in books["translator"]
    ]
    books.to_excel("books.xlsx", encoding="utf-8")


if __name__ == "__main__":
    main()