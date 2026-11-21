# Cleaning note

## File A: ott_cleaned.csv (ratings)
- 24,664 rows, one row per movie-genre pair. Rebuilt as one record per platform and movie: 15,364 records (Prime Video 12,605, Netflix 2,759); 204 movies are on both platforms. Script: `src/prepare_data.py`.
- IMDb 0.0 treated as missing (two values). Text and invalid values in the rating columns treated as missing. "Unknown" age rating treated as missing again. Rotten Tomatoes not used (source unclear).
- A few movies have different rating values in their genre rows; the first value is kept.

## File D: Combined_Dataset.csv (catalog)
Script: `src/clean_catalog.py`. Rows in file: 18,475.

| Step | Result |
|---|---|
| Key | `catalog_key` = N- or P- plus show_id, because show_id repeats across the two platforms |
| Missing titles | 2 rows kept and flagged (`title_missing`) |
| Titles turned into dates (probably by Excel) | 8 rows kept and flagged (`title_damaged`), not restored. Two of them look like "22-Jul" and "15-Aug". |
| Runtime in the rating column | 3 Netflix rows fixed (value moved to duration) |
| Repeated rows (same platform, type, title ignoring case and punctuation, year) | 20 removed, first kept. Examples: Song Of Texas (1943), Girls in Chains (1943), Asintombstonetest-target (2019), Mixed Up (2020) |
| Rows after cleaning | 18,455: Netflix 6,124 movies + 2,673 TV; Prime Video 7,804 movies + 1,854 TV |
| Runtime and seasons | parsed from "113 min" and "2 Seasons" into `runtime_min` and `seasons` |
| Country | first listed country in `country_first`; `origin_group` = India / United States / Other / Unknown; only reliable for Netflix |
| Age rating | mapped to Kids and all ages / Teen and parental guidance / Adult / Not rated with `data/mappings/age_rating_mapping.csv`; unmapped values: 0 |
| Genres | the label "Arts, Entertainment, and Culture" contains commas and is protected before splitting; labels mapped to 13 groups plus "Other / not a genre" with `data/mappings/genre_mapping.csv`; unmapped labels: 0 |
| Titles on both platforms | 195 (same title, year and type), flag `on_both` |
| Link to File A | `catalog_imdb_link.csv`: movies matched by normalised title and year. Netflix 2,135 of 6,124 movies have an IMDb rating; Prime Video 1,191 of 7,804 |

## Decisions that need the team's review
- The genre and age-rating mappings are our proposal. Edit the two CSV files in `data/mappings/` and re-run the scripts if the team disagrees.
- Damaged titles are flagged and not restored.

## Two earlier files that are not used
`amazon_prime_titles.csv` (now inside D) and `netflix_tr2.csv` (goes to 2024, no production country). Only 18% of File A's Netflix movies and 10% of its Prime movies matched them. See `docs/data_notes.md`.
