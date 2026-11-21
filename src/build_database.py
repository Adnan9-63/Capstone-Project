"""
Load the processed tables into a SQLite database so SQL queries can be run on them.

Run from the repository root (after python src/prepare_data.py):
    python src/build_database.py
Creates ott.db with tables: titles, genres, catalog_titles, catalog_genre_groups
Then run the queries in sql/queries.sql, for example with DB Browser for SQLite.
"""
import sqlite3
import pandas as pd

con = sqlite3.connect("ott.db")
pd.read_csv("data/processed/titles.csv").to_sql("titles", con, if_exists="replace", index=False)
pd.read_csv("data/processed/genres.csv").to_sql("genres", con, if_exists="replace", index=False)
pd.read_csv("data/processed/catalog_titles.csv").to_sql("catalog_titles", con, if_exists="replace", index=False)
pd.read_csv("data/processed/catalog_genre_groups.csv").to_sql("catalog_genre_groups", con, if_exists="replace", index=False)
for t in ("titles", "genres", "catalog_titles", "catalog_genre_groups"):
    print(t, con.execute("SELECT COUNT(*) FROM " + t).fetchone()[0], "rows")
con.close()
