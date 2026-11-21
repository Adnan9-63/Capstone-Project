# SQL (owner: Kumari Alka Singh)

Queries for the OTT capstone project using SQLite.

## How to run

1. Install DB Browser for SQLite: https://sqlitebrowser.org/ (free)
2. From the repo root, run: `python src/build_database.py` — creates `ott.db`
3. Open `ott.db` in DB Browser for SQLite
4. Open `sql/queries.sql`, paste queries into the Execute SQL tab and run

## Tables in ott.db

| Table | Source | Rows | Content |
|---|---|---|---|
| `titles` | data/processed/titles.csv | 15,364 | One row per movie with IMDb rating |
| `genres` | data/processed/genres.csv | 24,660 | One row per movie-genre pair |
| `catalog_titles` | data/processed/catalog_titles.csv | 18,455 | One row per title (movies + TV) |
| `catalog_genre_groups` | data/processed/catalog_genre_groups.csv | 50,xxx | One row per title-genre group |

## queries.sql

24 queries covering both datasets:
- Section 1 (Q1–Q13): Ratings analysis — counts, averages, genres, decades, top movies
- Section 2 (Q14–Q24): Catalog analysis — type mix, age ratings, genres, runtime, country

Note: SQLite has no MEDIAN function. True medians are in `outputs/results.json` and `outputs/catalog/catalog_results.json`.
