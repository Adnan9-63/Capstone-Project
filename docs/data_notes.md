# Data notes

## The four files we looked at
| File | Rows | Content | Problems | Use |
|---|---|---|---|---|
| A: ott_cleaned.csv | 24,664 rows = 15,364 movies (Prime 12,605, Netflix 2,759) | IMDb rating, year, genre, platform. Movies only. Early-2021 snapshot. | One row per movie-genre pair. Age rating blank for 59%. Genre labels differ. No vote counts. Rotten Tomatoes column unclear (not used). | Ratings analysis |
| B: amazon_prime_titles.csv | 9,668 | 7,814 movies, 1,854 TV shows, years 1920 to 2021 | No IMDb. Country filled for only 672 rows. | Now inside D |
| C: netflix_tr2.csv | 6,025 | 3,857 movies, 2,168 TV shows, years 1951 to 2024, IMDb and votes | Goes to 2024 while Prime stops at 2021. Countries are where a title is available. Only 18% of A's Netflix movies match. | Not used |
| D: Combined_Dataset.csv (Alka) | 18,475 (18,455 after cleaning) | Prime 9,668 + Netflix 8,807 titles (Netflix half is a different file from C), both to 2021. Type, country, age rating, genre, duration, cast, director. | No IMDb. Prime country blank for 93%. Different genre and age-rating scales. show_id repeats across platforms. 8 titles turned into dates, 2 missing titles, 20 repeated rows. | Catalog analysis |

## How they fit
- A answers quality (IMDb). D answers catalog content (movies vs TV, years, genres, age ratings, runtime, Netflix origin). They are kept as two sources and labelled on every chart.
- Link (optional): 78% of A's Netflix movies appear in D (2,135 get an IMDb rating after linking), but only about 9% of A's Prime movies do. So IMDb by origin is possible for Netflix only, as an exploratory extra.

## Known limits
Early-2021 snapshots, not specific to India. No price data yet. Genre and age-rating mappings are our proposal (data/mappings/). Details of every cleaning step: docs/cleaning_note.md.
