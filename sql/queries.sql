-- OTT Capstone SQL Queries
-- Group 03, IIT Patna — Capstone-I
-- Database: ott.db  (created by: python src/build_database.py)
--
-- Tables:
--   titles(title_key, platform, title, year, imdb, rt, age_rating, release_period, period_order)
--   genres(title_key, platform, genre)
--   catalog_titles(catalog_key, platform, type, title, release_year, ...)
--   catalog_genre_groups(catalog_key, platform, type, genre_group)
--
-- Source A (titles, genres)         = data/raw/ott_cleaned.csv       = ratings, movies only
-- Source D (catalog_titles, etc.)   = data/raw/Combined_Dataset.csv  = catalog, movies + TV
--
-- NOTE: SQLite has no MEDIAN function. True medians are in outputs/results.json and
--       outputs/catalog/catalog_results.json (computed by the Python scripts).
-- How to run: open ott.db in DB Browser for SQLite, paste a query and press Run.

-- =============================================================
-- SECTION 1: RATINGS (Source A — IMDb file, movies only)
-- =============================================================

-- Q1. Number of movies per platform
SELECT platform, COUNT(*) AS total_movies
FROM titles
GROUP BY platform;

-- Q2. Number of movies with an IMDb rating per platform
SELECT platform, COUNT(imdb) AS rated_movies
FROM titles
GROUP BY platform;

-- Q3. Average IMDb rating per platform
SELECT platform,
       ROUND(AVG(imdb), 2) AS mean_imdb
FROM titles
WHERE imdb IS NOT NULL
GROUP BY platform;

-- Q4. Share of movies rated 7.0 or higher per platform
SELECT platform,
       ROUND(100.0 * SUM(CASE WHEN imdb >= 7.0 THEN 1 ELSE 0 END)
             / COUNT(imdb), 1) AS pct_7_or_higher
FROM titles
WHERE imdb IS NOT NULL
GROUP BY platform;

-- Q5. Share of movies rated below 5.0 per platform
SELECT platform,
       ROUND(100.0 * SUM(CASE WHEN imdb < 5.0 THEN 1 ELSE 0 END)
             / COUNT(imdb), 1) AS pct_below_5
FROM titles
WHERE imdb IS NOT NULL
GROUP BY platform;

-- Q6. Movies per release period and platform
SELECT platform, release_period, COUNT(*) AS movies
FROM titles
GROUP BY platform, release_period
ORDER BY period_order, platform;

-- Q7. Average IMDb by release period and platform
SELECT platform, release_period,
       COUNT(imdb) AS rated,
       ROUND(AVG(imdb), 2) AS mean_imdb
FROM titles
WHERE imdb IS NOT NULL
GROUP BY platform, release_period
ORDER BY period_order, platform;

-- Q8. Number of movies per genre and platform
SELECT g.platform, g.genre, COUNT(DISTINCT g.title_key) AS movies
FROM genres g
GROUP BY g.platform, g.genre
ORDER BY g.platform, movies DESC;

-- Q9. Average IMDb per genre and platform
SELECT g.platform, g.genre,
       COUNT(t.imdb) AS rated,
       ROUND(AVG(t.imdb), 2) AS mean_imdb
FROM genres g
JOIN titles t ON g.title_key = t.title_key AND g.platform = t.platform
WHERE t.imdb IS NOT NULL
GROUP BY g.platform, g.genre
ORDER BY g.platform, mean_imdb DESC;

-- Q10. Movies that appear on both platforms (same title and year)
SELECT title, year,
       MAX(CASE WHEN platform = 'Netflix' THEN imdb END) AS netflix_imdb,
       MAX(CASE WHEN platform = 'Prime Video' THEN imdb END) AS prime_imdb
FROM titles
GROUP BY title_key
HAVING COUNT(DISTINCT platform) = 2
ORDER BY title;

-- Q11. Top 10 highest rated Netflix movies
SELECT title, year, ROUND(imdb, 1) AS imdb
FROM titles
WHERE platform = 'Netflix' AND imdb IS NOT NULL
ORDER BY imdb DESC
LIMIT 10;

-- Q12. Top 10 highest rated Prime Video movies
SELECT title, year, ROUND(imdb, 1) AS imdb
FROM titles
WHERE platform = 'Prime Video' AND imdb IS NOT NULL
ORDER BY imdb DESC
LIMIT 10;

-- Q13. Movies per decade and platform
SELECT platform,
       (year / 10) * 10 AS decade,
       COUNT(*) AS movies
FROM titles
GROUP BY platform, decade
ORDER BY decade, platform;

-- =============================================================
-- SECTION 2: CATALOG (Source D — Combined Dataset, movies + TV)
-- =============================================================

-- Q14. Total titles per platform and type
SELECT platform, type, COUNT(*) AS titles
FROM catalog_titles
GROUP BY platform, type
ORDER BY platform, type;

-- Q15. Share of movies vs TV shows per platform
SELECT platform,
       ROUND(100.0 * SUM(CASE WHEN type = 'Movie' THEN 1 ELSE 0 END) / COUNT(*), 1) AS movie_pct,
       ROUND(100.0 * SUM(CASE WHEN type = 'TV Show' THEN 1 ELSE 0 END) / COUNT(*), 1) AS tvshow_pct
FROM catalog_titles
GROUP BY platform;

-- Q16. Average release year per platform and type
-- (SQLite has no MEDIAN; true median is 2017 Netflix / 2016 Prime from Python)
SELECT platform, type, ROUND(AVG(release_year), 0) AS avg_year
FROM catalog_titles
GROUP BY platform, type;

-- Q17. Share of titles released 2015 or later
SELECT platform,
       ROUND(100.0 * SUM(CASE WHEN release_year >= 2015 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_2015_plus
FROM catalog_titles
GROUP BY platform;

-- Q18. Age rating distribution per platform and type
SELECT platform, type, age_group, COUNT(*) AS titles
FROM catalog_titles
GROUP BY platform, type, age_group
ORDER BY platform, type, age_order;

-- Q19. Genre distribution per platform and type (excluding catch-all label)
SELECT platform, type, genre_group, COUNT(DISTINCT catalog_key) AS titles
FROM catalog_genre_groups
WHERE genre_group != 'Other / not a genre'
GROUP BY platform, type, genre_group
ORDER BY platform, type, titles DESC;

-- Q20. Titles that appear on both platforms (catalog)
SELECT title, release_year, type
FROM catalog_titles
WHERE on_both = 1
  AND title_missing = 0
GROUP BY title_key, type
ORDER BY title;

-- Q21. Average movie runtime per platform
-- (SQLite has no MEDIAN; true median is 98 Netflix / 91 Prime from Python)
SELECT platform,
       COUNT(runtime_min) AS movies_with_runtime,
       ROUND(AVG(runtime_min), 1) AS avg_runtime_min
FROM catalog_titles
WHERE type = 'Movie' AND runtime_min IS NOT NULL
GROUP BY platform;

-- Q22. Netflix titles by country of origin
SELECT type, origin_group, COUNT(*) AS titles
FROM catalog_titles
WHERE platform = 'Netflix'
GROUP BY type, origin_group
ORDER BY type, titles DESC;

-- Q23. How much of Prime Video's country data is filled?
SELECT
    SUM(CASE WHEN country_known = 1 THEN 1 ELSE 0 END) AS known,
    SUM(CASE WHEN country_known = 0 THEN 1 ELSE 0 END) AS unknown,
    ROUND(100.0 * SUM(CASE WHEN country_known = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_known
FROM catalog_titles
WHERE platform = 'Prime Video';

-- Q24. Release period breakdown per platform (catalog)
SELECT platform, release_period, COUNT(*) AS titles
FROM catalog_titles
GROUP BY platform, release_period
ORDER BY period_order, platform;
