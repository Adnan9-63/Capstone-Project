# Comparative Analysis of Different OTT Platforms (Netflix and Amazon Prime Video)

Capstone-I project, Group 03, IIT Patna.

We compare Netflix and Amazon Prime Video using public Kaggle data (early-2021 snapshots) and present the results in a Power BI dashboard and a website.
Two data sources are used and kept separate:

- **A, ratings:** `data/raw/ott_cleaned.csv`. 15,364 movies with IMDb ratings (movies only).
- **D, catalog:** `data/raw/Combined_Dataset.csv` (combined by Alka from the Prime and Netflix title files). 18,455 titles after cleaning, movies and TV shows, with type, country, age rating, genre and runtime.

## Team

| Member | Work |
|---|---|
| Kumari Alka Singh | SQL queries and website |
| Md. Adnan | Statistical analysis of ratings, Power BI dashboard, repository |
| Fahim Alam | Data cleaning and preparation, presentation |
| Rathod Ajeet Vinod | Analysis and data collection |
| Praanshi Agrawal | Feature engineering, project findings, presentation design |

See `docs/contributions.md` for who prepared and reviewed each file.

## How to run

```
pip install -r requirements.txt
python src/prepare_data.py        # A: one record per movie -> data/processed/titles.csv, genres.csv
python src/rating_analysis.py     # A: IMDb comparison -> outputs/results.json, outputs/figures/
python src/more_findings.py       # A: genre-wise, cut-off and other checks -> outputs/more_findings.json
python src/clean_catalog.py       # D: clean catalog -> data/processed/catalog_*.csv
python src/catalog_analysis.py    # D: catalog analysis -> outputs/catalog/
python src/write_docs.py          # findings, cleaning note and Power BI guide -> docs/, powerbi/
python src/build_database.py      # optional: ott.db for SQL
python src/dataset_overlap_check.py   # optional: needs data/raw/extra/ (see data/raw/README.md)
```

## Folders

| Folder | What is in it |
|---|---|
| `data/raw/` | Original CSV files (never edit) |
| `data/mappings/` | Genre mapping (13 groups) and age-rating mapping (4 groups). Our proposal, editable. |
| `data/processed/` | Clean tables used by the analysis, the dashboard and SQL |
| `src/` | Python scripts |
| `outputs/` | Results (JSON, CSV) and figures for ratings; `outputs/catalog/` for the catalog |
| `docs/` | Findings, cleaning note, data notes, plan, roles, contributions |
| `powerbi/` | Dashboard guide (page-by-page, measures, check values) and the .pbix |
| `sql/`, `site/` | Kumari's SQL queries and website |
| `reports/` | Each member's reports (one folder per member) |

## Main results so far (re-run the scripts to confirm)

- **Ratings (A):** Netflix movies are rated slightly higher than Prime Video movies (median IMDb 6.3 vs 6.0; 27.3% vs 20.7% rated 7.0 or higher). The effect is small and appears in every release period.
- **Catalog (D):** Movies are 70% of Netflix titles and 81% of Prime Video titles. Netflix titles are somewhat newer, its movies are longer (median 98 vs 91 minutes) and it has more adult-rated titles.
- Full list with limits: `docs/findings.md`.

## Important notes

- The files are early-2021 snapshots and are not specific to India. Results describe the data, not the platforms today.
- File A has one row per movie-genre pair; always use `titles.csv` for counts.
- Prime Video country is blank for most titles, so origin is analysed for Netflix only.
- Ratings exist only for movies in file A. Price data template in `data/processed/prices_template.csv`.
- Data details: `docs/data_notes.md` and `docs/cleaning_note.md`.
