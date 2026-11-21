# Findings (draft)

How to use: every finding below is written as claim, number, limitation. Re-run the scripts before quoting a number
(`python src/rating_analysis.py`, `more_findings.py`, `catalog_analysis.py`). All statements describe the datasets, not the platforms today.

## Part A. Ratings (IMDb file, movies only, early-2021 snapshot)

**A1. Netflix movies are rated slightly higher than Prime Video movies.**
Median IMDb 6.3 vs 6.0; mean 6.23 vs 5.82 (difference 0.41, 95% interval 0.36 to 0.46).
27.3% of rated Netflix movies score 7.0 or higher against 20.7% for Prime Video. Effect size is small (rank-biserial r = 0.18); a random Netflix movie beats a random Prime movie about 59% of the time.
Limit: popular movies only, no vote counts.

**A2. The difference is not explained by release period.**
Netflix has the higher median in all four release periods (effect sizes 0.16 to 0.50). Re-weighting Prime Video to Netflix's era mix leaves its mean at 5.80 (unadjusted 5.82).
Limit: Netflix has only 46 movies before 1980.

**A3. The Netflix advantage differs by genre.**
Medians shown as (Netflix vs Prime Video). After correcting for many tests (Holm), Netflix is higher in: Action & Adventure (6.2 vs 5.6), Comedy (6.2 vs 5.9), Crime (6.3 vs 5.7), Drama (6.4 vs 6.1). Prime Video is higher in: Documentary (6.9 vs 7.1). No clear difference in: Animation, Biography, Family.
Limit: genre labels differ between the platforms; small groups: Biography (Netflix n = 32), Family (Netflix n = 61).

**A4. Prime Video's lower average comes mainly from a larger group of low-rated movies.**
24.3% of Prime movies are rated below 5.0 against 12.0% for Netflix. At the top the gap is small: rated 8.0 or higher is 4.3% vs 3.5%.
Limit: description only, not a cause.

**A5. The result does not depend on the 7.0 cut-off.**
Share rated 6.5 or higher: 45.7% vs 35.0%; 7.5 or higher: 12.2% vs 9.3% (Netflix vs Prime Video).

## Part B. Catalog content (combined file, movies and TV shows, both early-2021)

**B1. Prime Video's catalog has a larger share of movies.**
Movies are 70% of Netflix titles and 81% of Prime Video titles (6,124 + 2,673 Netflix; 7,804 + 1,854 Prime). Chi-square p < 0.001, Cramer's V = 0.13 (small).

**B2. Netflix titles are somewhat newer.**
Median release year 2017 vs 2016; released 2015 or later: 71% vs 56%. Effect size is small (r = 0.08).

**B3. Genre mix differs (descriptive).**
Movies: Netflix has more Reality, Talk & Stand-up (6 points), Documentary & Factual (5 points), Music & Concerts (4 points); Prime Video has more Thriller, Crime & Mystery (8 points), Action & Adventure (6 points), Horror (5 points). TV shows: Netflix has more Thriller, Crime & Mystery (15 points), Romance (9 points), Comedy (7 points); Prime Video has more Animation & Anime (10 points), Sports & Fitness (4 points), Kids, Family & Teen (3 points). (Differences in share of titles, Netflix minus Prime.)
Limit: genre labels were mapped by us (data/mappings/genre_mapping.csv). "Other / not a genre" (for example "International Movies") is 57% of Netflix movies and 21% of Prime movies and is left out of the comparison. A title can have several genres, so shares do not add to 100%.

**B4. Netflix has more adult-rated titles.**
Adult group among movies: 47% (Netflix) vs 27% (Prime); among TV shows: 43% vs 12%. Cramer's V 0.22 (movies), 0.32 (TV).
Limit: the platforms use different rating scales, mapped by us to Kids / Teen / Adult (data/mappings/age_rating_mapping.csv). Prime has 7% of movies without a usable rating.

**B5. Netflix movies are longer.**
Median runtime 98 vs 91 minutes (r = 0.20, small to moderate).

**B6. TV shows are mostly short on both platforms.**
One-season shows: 67% (Netflix) vs 72% (Prime); the difference is tiny (r = 0.05).

**B7. Origin, Netflix only.**
Among Netflix movies with a country, 16% list India first, 42% the United States and 42% another country; for TV shows 4%, 37% and 59%.
Limit: country is filled for 91% of Netflix titles but only 7% of Prime titles, so Prime is not analysed. First listed country is used.

## Part C. Combining the files (exploratory, Netflix only)

**C1. Indian and US movies on Netflix are rated about the same.**
Linked movies with a known country: India n = 427 (median 6.4, 32% rated 7.0+), United States n = 774 (median 6.3, 27% rated 7.0+). No clear difference (p = 0.47, r = 0.03).
Limit: only 2,135 Netflix movies could be linked by title and year; Prime has just 186 linked movies with a known country, so it is not analysed.

## What we cannot say
- That one platform is better, or why the differences exist.
- Anything about today's catalogs, or about India in general (the files are early-2021 snapshots, not India-specific).
- Anything about Prime Video origin (country is blank for most titles), or about ratings of TV shows (no IMDb for TV).
- Anything about viewers' preferences (no survey results yet).
