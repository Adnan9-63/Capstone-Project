"""
Write the findings draft, the cleaning note and the Power BI guide from the result files.

Run from the repository root after all other scripts:
    python src/write_docs.py
Writes docs/findings.md, docs/cleaning_note.md, powerbi/README.md
"""
import json

R = json.load(open("outputs/results.json"))
M = json.load(open("outputs/more_findings.json"))
C = json.load(open("outputs/catalog/catalog_results.json"))
L = json.load(open("outputs/catalog/cleaning_log.json"))
try:
    O = json.load(open("outputs/overlap_check.json"))      # made by dataset_overlap_check.py (needs data/raw/extra/)
except FileNotFoundError:
    O = None

pc = lambda x: f"{x * 100:.1f}%"
pc0 = lambda x: f"{x * 100:.0f}%"
f1 = lambda x: f"{x:.1f}"
f2 = lambda x: f"{x:.2f}"
num = lambda x: f"{int(round(x)):,}"
N, P = R["desc"]["Netflix"], R["desc"]["Prime Video"]
NF, PV = "Netflix", "Prime Video"

# ------------------------------------------------------------------ genre-wise ratings sentence
up, down, flat = [], [], []
for g in M["genre_tests"]:
    txt = f"{g['genre']} ({f1(g['median_netflix'])} vs {f1(g['median_prime'])})"
    if g["p_holm"] < 0.05:
        (up if g["r"] > 0 else down).append(txt)
    else:
        flat.append(g["genre"])
small = [f"{g['genre']} (Netflix n = {g['n_netflix']})" for g in M["genre_tests"] if g["n_netflix"] < 100]

# ------------------------------------------------------------------ catalog genre differences
gs = {}
for k, v in C["genre_share"].items():
    pl, t, gname = k.split("|")
    gs.setdefault((t, gname), {})[pl] = v
def top_diff(t):
    rows = [(g, d.get(NF, 0) - d.get(PV, 0)) for (tt, g), d in gs.items() if tt == t and g != "Other / not a genre"]
    rows.sort(key=lambda x: x[1])
    more_prime = ", ".join(f"{g} ({abs(d) * 100:.0f} points)" for g, d in rows[:3])
    more_nf = ", ".join(f"{g} ({d * 100:.0f} points)" for g, d in rows[::-1][:3])
    return more_nf, more_prime
mv_nf, mv_pr = top_diff("Movie"); tv_nf, tv_pr = top_diff("TV Show")
other_share = {f"{pl}|{t}": gs.get((t, "Other / not a genre"), {}).get(pl, 0) for pl in (NF, PV) for t in ("Movie", "TV Show")}

age = lambda pl, t, k: C["age_share"].get(f"{pl}|{t}|{k}", 0)
org = C["netflix_known_origin_share"]
ib = C["netflix_imdb_by_origin"]
ind = next(r for r in ib["rows"] if r["origin"] == "India"); us = next(r for r in ib["rows"] if r["origin"] == "United States")

findings = f"""# Findings (draft)

How to use: every finding below is written as claim, number, limitation. Re-run the scripts before quoting a number
(`python src/rating_analysis.py`, `more_findings.py`, `catalog_analysis.py`). All statements describe the datasets, not the platforms today.

## Part A. Ratings (IMDb file, movies only, early-2021 snapshot)

**A1. Netflix movies are rated slightly higher than Prime Video movies.**
Median IMDb {f1(N['median'])} vs {f1(P['median'])}; mean {f2(N['mean'])} vs {f2(P['mean'])} (difference {f2(R['mean_diff']['value'])}, 95% interval {f2(R['mean_diff']['ci'][0])} to {f2(R['mean_diff']['ci'][1])}).
{pc(N['share_high'])} of rated Netflix movies score 7.0 or higher against {pc(P['share_high'])} for Prime Video. Effect size is small (rank-biserial r = {f2(R['mwu']['rank_biserial'])}); a random Netflix movie beats a random Prime movie about {pc0(R['mwu']['prob_netflix_higher'])} of the time.
Limit: popular movies only, no vote counts.

**A2. The difference is not explained by release period.**
Netflix has the higher median in all four release periods (effect sizes {f2(min(e['rank_biserial'] for e in R['era']))} to {f2(max(e['rank_biserial'] for e in R['era']))}). Re-weighting Prime Video to Netflix's era mix leaves its mean at {f2(R['standardised_prime']['mean'])} (unadjusted {f2(R['standardised_prime']['prime_mean'])}).
Limit: Netflix has only {R['era'][0]['n_netflix_titles']} movies before 1980.

**A3. The Netflix advantage differs by genre.**
Medians shown as (Netflix vs Prime Video). After correcting for many tests (Holm), Netflix is higher in: {', '.join(up) if up else 'none'}. Prime Video is higher in: {', '.join(down) if down else 'none'}. No clear difference in: {', '.join(flat) if flat else 'none'}.
Limit: genre labels differ between the platforms; small groups: {', '.join(small) if small else 'none'}.

**A4. Prime Video's lower average comes mainly from a larger group of low-rated movies.**
{pc(M['share_below_5']['Prime'] if 'Prime' in M['share_below_5'] else M['share_below_5']['Prime Video'])} of Prime movies are rated below 5.0 against {pc(M['share_below_5']['Netflix'])} for Netflix. At the top the gap is small: rated 8.0 or higher is {pc(M['share_at_least']['8.0']['Netflix'])} vs {pc(M['share_at_least']['8.0']['Prime Video'])}.
Limit: description only, not a cause.

**A5. The result does not depend on the 7.0 cut-off.**
Share rated 6.5 or higher: {pc(M['share_at_least']['6.5']['Netflix'])} vs {pc(M['share_at_least']['6.5']['Prime Video'])}; 7.5 or higher: {pc(M['share_at_least']['7.5']['Netflix'])} vs {pc(M['share_at_least']['7.5']['Prime Video'])} (Netflix vs Prime Video).

## Part B. Catalog content (combined file, movies and TV shows, both early-2021)

**B1. Prime Video's catalog has a larger share of movies.**
Movies are {pc0(C['type_mix']['share_movies'][NF])} of Netflix titles and {pc0(C['type_mix']['share_movies'][PV])} of Prime Video titles ({num(C['type_mix']['counts'][NF]['Movie'])} + {num(C['type_mix']['counts'][NF]['TV Show'])} Netflix; {num(C['type_mix']['counts'][PV]['Movie'])} + {num(C['type_mix']['counts'][PV]['TV Show'])} Prime). Chi-square p < 0.001, Cramer's V = {f2(C['type_mix']['cramers_v'])} (small).

**B2. Netflix titles are somewhat newer.**
Median release year {int(C['years']['all']['median'][NF])} vs {int(C['years']['all']['median'][PV])}; released 2015 or later: {pc0(C['years']['all']['share_2015_plus'][NF])} vs {pc0(C['years']['all']['share_2015_plus'][PV])}. Effect size is small (r = {f2(C['years']['all']['rank_biserial'])}).

**B3. Genre mix differs (descriptive).**
Movies: Netflix has more {mv_nf}; Prime Video has more {mv_pr}. TV shows: Netflix has more {tv_nf}; Prime Video has more {tv_pr}. (Differences in share of titles, Netflix minus Prime.)
Limit: genre labels were mapped by us (data/mappings/genre_mapping.csv). "Other / not a genre" (for example "International Movies") is {pc0(other_share['Netflix|Movie'])} of Netflix movies and {pc0(other_share['Prime Video|Movie'])} of Prime movies and is left out of the comparison. A title can have several genres, so shares do not add to 100%.

**B4. Netflix has more adult-rated titles.**
Adult group among movies: {pc0(age(NF, 'Movie', 'Adult'))} (Netflix) vs {pc0(age(PV, 'Movie', 'Adult'))} (Prime); among TV shows: {pc0(age(NF, 'TV Show', 'Adult'))} vs {pc0(age(PV, 'TV Show', 'Adult'))}. Cramer's V {f2(C['age_tests']['Movie']['cramers_v'])} (movies), {f2(C['age_tests']['TV Show']['cramers_v'])} (TV).
Limit: the platforms use different rating scales, mapped by us to Kids / Teen / Adult (data/mappings/age_rating_mapping.csv). Prime has {pc0(age(PV, 'Movie', 'Not rated'))} of movies without a usable rating.

**B5. Netflix movies are longer.**
Median runtime {num(C['runtime']['median'][NF])} vs {num(C['runtime']['median'][PV])} minutes (r = {f2(C['runtime']['rank_biserial'])}, small to moderate).

**B6. TV shows are mostly short on both platforms.**
One-season shows: {pc0(C['seasons']['share_one_season'][NF])} (Netflix) vs {pc0(C['seasons']['share_one_season'][PV])} (Prime); the difference is tiny (r = {f2(C['seasons']['rank_biserial'])}).

**B7. Origin, Netflix only.**
Among Netflix movies with a country, {pc0(org['Movie']['India'])} list India first, {pc0(org['Movie']['United States'])} the United States and {pc0(org['Movie']['Other'])} another country; for TV shows {pc0(org['TV Show']['India'])}, {pc0(org['TV Show']['United States'])} and {pc0(org['TV Show']['Other'])}.
Limit: country is filled for {pc0(C['country_known_share'][NF])} of Netflix titles but only {pc0(C['country_known_share'][PV])} of Prime titles, so Prime is not analysed. First listed country is used.

## Part C. Combining the files (exploratory, Netflix only)

**C1. Indian and US movies on Netflix are rated about the same.**
Linked movies with a known country: India n = {ind['n']} (median {f1(ind['median'])}, {pc0(ind['share_7_plus'])} rated 7.0+), United States n = {us['n']} (median {f1(us['median'])}, {pc0(us['share_7_plus'])} rated 7.0+). No clear difference (p = {ib['india_vs_us_p']:.2f}, r = {f2(ib['india_vs_us_r'])}).
Limit: only {num(ib['linked_movies'])} Netflix movies could be linked by title and year; Prime has just {ib['prime_linked_with_known_origin']} linked movies with a known country, so it is not analysed.

## What we cannot say
- That one platform is better, or why the differences exist.
- Anything about today's catalogs, or about India in general (the files are early-2021 snapshots, not India-specific).
- Anything about Prime Video origin (country is blank for most titles), or about ratings of TV shows (no IMDb for TV).
- Anything about viewers' preferences (no survey results yet).
"""
open("docs/findings.md", "w").write(findings)

# ------------------------------------------------------------------ cleaning note
ovtxt = (f"Only {pc0(O['match_title_and_year']['netflix_share'])} of File A's Netflix movies and {pc0(O['match_title_and_year']['prime_share'])} of its Prime movies matched them."
         if O else "They matched File A poorly (run src/dataset_overlap_check.py to get the numbers).")
f = L["final"]["by_platform_type"]
note = f"""# Cleaning note

## File A: ott_cleaned.csv (ratings)
- {num(R['rows_in_file'])} rows, one row per movie-genre pair. Rebuilt as one record per platform and movie: {num(R['records_unique'])} records (Prime Video {num(P['records'])}, Netflix {num(N['records'])}); {R['on_both_platforms']} movies are on both platforms. Script: `src/prepare_data.py`.
- IMDb 0.0 treated as missing (two values). Text and invalid values in the rating columns treated as missing. "Unknown" age rating treated as missing again. Rotten Tomatoes not used (source unclear).
- A few movies have different rating values in their genre rows; the first value is kept.

## File D: Combined_Dataset.csv (catalog)
Script: `src/clean_catalog.py`. Rows in file: {num(L['rows_in_file'])}.

| Step | Result |
|---|---|
| Key | `catalog_key` = N- or P- plus show_id, because show_id repeats across the two platforms |
| Missing titles | {L['titles_missing']} rows kept and flagged (`title_missing`) |
| Titles turned into dates (probably by Excel) | {L['titles_damaged_into_dates']} rows kept and flagged (`title_damaged`), not restored. Two of them look like "22-Jul" and "15-Aug". |
| Runtime in the rating column | {L['rating_cells_with_runtime_fixed']} Netflix rows fixed (value moved to duration) |
| Repeated rows (same platform, type, title ignoring case and punctuation, year) | {L['repeated_rows_removed']} removed, first kept. Examples: {', '.join(f'{t} ({y})' for _, t, y in L['repeated_rows_examples'][:4])} |
| Rows after cleaning | {num(L['rows_after_cleaning'])}: Netflix {num(f['Netflix|Movie'])} movies + {num(f['Netflix|TV Show'])} TV; Prime Video {num(f['Prime Video|Movie'])} movies + {num(f['Prime Video|TV Show'])} TV |
| Runtime and seasons | parsed from "113 min" and "2 Seasons" into `runtime_min` and `seasons` |
| Country | first listed country in `country_first`; `origin_group` = India / United States / Other / Unknown; only reliable for Netflix |
| Age rating | mapped to Kids and all ages / Teen and parental guidance / Adult / Not rated with `data/mappings/age_rating_mapping.csv`; unmapped values: {len(L['unmapped_age_ratings'])} |
| Genres | the label "Arts, Entertainment, and Culture" contains commas and is protected before splitting; labels mapped to 13 groups plus "Other / not a genre" with `data/mappings/genre_mapping.csv`; unmapped labels: {len(L['unmapped_genre_labels'])} |
| Titles on both platforms | {L['titles_on_both_platforms']} (same title, year and type), flag `on_both` |
| Link to File A | `catalog_imdb_link.csv`: movies matched by normalised title and year. Netflix {num(L['imdb_link']['Netflix']['with_imdb'])} of {num(L['imdb_link']['Netflix']['movies'])} movies have an IMDb rating; Prime Video {num(L['imdb_link']['Prime Video']['with_imdb'])} of {num(L['imdb_link']['Prime Video']['movies'])} |

## Decisions that need the team's review
- The genre and age-rating mappings are our proposal. Edit the two CSV files in `data/mappings/` and re-run the scripts if the team disagrees.
- Damaged titles are flagged and not restored.

## Two earlier files that are not used
`amazon_prime_titles.csv` (now inside D) and `netflix_tr2.csv` (goes to 2024, no production country). {ovtxt} See `docs/data_notes.md`.
"""
open("docs/cleaning_note.md", "w").write(note)

# ------------------------------------------------------------------ Power BI guide with check values
chk = [
 ("Titles, Netflix", num(f['Netflix|Movie'] + f['Netflix|TV Show'])),
 ("Titles, Prime Video", num(f['Prime Video|Movie'] + f['Prime Video|TV Show'])),
 ("Movie share, Netflix / Prime", f"{pc0(C['type_mix']['share_movies'][NF])} / {pc0(C['type_mix']['share_movies'][PV])}"),
 ("Median release year, Netflix / Prime", f"{int(C['years']['all']['median'][NF])} / {int(C['years']['all']['median'][PV])}"),
 ("Released 2015 or later, Netflix / Prime", f"{pc0(C['years']['all']['share_2015_plus'][NF])} / {pc0(C['years']['all']['share_2015_plus'][PV])}"),
 ("Median movie runtime, Netflix / Prime", f"{num(C['runtime']['median'][NF])} / {num(C['runtime']['median'][PV])} min"),
 ("Rated movies (IMDb), Netflix / Prime", f"{num(N['rated'])} / {num(P['rated'])}"),
 ("Median IMDb, Netflix / Prime", f"{f1(N['median'])} / {f1(P['median'])}"),
 ("Share rated 7.0 or higher, Netflix / Prime", f"{pc(N['share_high'])} / {pc(P['share_high'])}"),
]
chk_md = "\n".join(f"| {a} | {b} |" for a, b in chk)
pbi = f"""# Power BI dashboard guide

Owner: Md. Adnan. Build the dashboard from the files in `data/processed/`. Save the .pbix and screenshots in this folder.

## 1. Load these files (Get data > Text/CSV)
Rename the tables as shown.

| File | Table name |
|---|---|
| catalog_titles.csv | catalog_titles |
| catalog_genre_groups.csv | catalog_genre_groups |
| titles.csv | imdb_titles |
| genres.csv | imdb_genres |

In Power Query, check these types: release_year, runtime_min, seasons, decade, period_order, age_order are numbers; the True/False columns are True/False; imdb is a decimal number.

## 2. Relationships (Model view)
- catalog_titles[catalog_key] (one) to catalog_genre_groups[catalog_key] (many), filter direction single (titles filter genres).
- imdb_titles[title_key] and imdb_genres[title_key] (one to many) the same way. Because a title_key can occur on both platforms, create the relationship on platform + title_key (add a column `link` = platform & "|" & title_key in both tables) or skip imdb_genres and use only imdb_titles.
- Do not connect the catalog tables to the IMDb tables. They are two separate sources.
- **Always take platform and type for slicers and legends from catalog_titles (or imdb_titles), not from the genre table.** Otherwise the shares below are wrong.

## 3. Sort order
- catalog_titles[release_period]: Sort by column > period_order. Same for imdb_titles[release_period].
- catalog_titles[age_group]: Sort by column > age_order.

## 4. Measures (New measure)
```
Titles = COUNTROWS(catalog_titles)
Movies = CALCULATE([Titles], catalog_titles[type] = "Movie")
TV Shows = CALCULATE([Titles], catalog_titles[type] = "TV Show")
Movie Share = DIVIDE([Movies], [Titles])
Median Release Year = MEDIAN(catalog_titles[release_year])
Share 2015 Plus = DIVIDE(CALCULATE([Titles], catalog_titles[release_year] >= 2015), [Titles])
Median Movie Runtime = CALCULATE(MEDIAN(catalog_titles[runtime_min]), catalog_titles[type] = "Movie")
Genre Share = DIVIDE(DISTINCTCOUNT(catalog_genre_groups[catalog_key]), [Titles])

Rated Titles = COUNT(imdb_titles[imdb])
Median IMDb = MEDIAN(imdb_titles[imdb])
Share 7 Plus = DIVIDE(CALCULATE(COUNT(imdb_titles[imdb]), imdb_titles[imdb] >= 7), COUNT(imdb_titles[imdb]))
```
Format shares as percentages.

## 5. Pages
| Page | Visuals |
|---|---|
| 1 Overview | Cards: Titles, Movie Share, Median Release Year, Share 2015 Plus (by platform). Slicers: platform, type. |
| 2 Content mix and years | 100% stacked bar of type by platform. Column chart of release_period (sorted) by platform, measure Titles as % of column total. Line chart of Titles by release_year. |
| 3 Genres | Bar chart: axis catalog_genre_groups[genre_group] (remove "Other / not a genre" with a filter), legend catalog_titles[platform], value Genre Share. Slicer: type. |
| 4 Age ratings | 100% stacked bar: axis platform, legend age_group, filter type. Note on the page that the scales differ and were mapped. |
| 5 Runtime and seasons | Box-style view: histogram of runtime_min by platform (movies), card Median Movie Runtime, table of seasons share. |
| 6 Ratings (IMDb file) | Cards Rated Titles, Median IMDb, Share 7 Plus by platform. Column chart Median IMDb by release_period. Histogram of imdb. Label: "source: IMDb file". |
| 7 Data notes | Text box: snapshot early 2021, Prime country blank for most titles, genre and age mapping, flagged titles. |
Optional page: Netflix origin (India / United States / Other / Unknown by type). Filter platform = Netflix and say that Prime is not shown because its country is blank.

## 6. Check your numbers (before you freeze)
These come from the Python scripts. The dashboard should show the same values.

| Check | Expected |
|---|---|
{chk_md}

## 7. Notes
- Power BI stores file paths. If the file is opened on another computer, change the data source to the local copy of each CSV.
- Every visual should say which source it uses (catalog file or IMDb file).
"""
open("powerbi/README.md", "w").write(pbi)
print("docs written")
