# Power BI dashboard guide

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
| Titles, Netflix | 8,797 |
| Titles, Prime Video | 9,658 |
| Movie share, Netflix / Prime | 70% / 81% |
| Median release year, Netflix / Prime | 2017 / 2016 |
| Released 2015 or later, Netflix / Prime | 71% / 56% |
| Median movie runtime, Netflix / Prime | 98 / 91 min |
| Rated movies (IMDb), Netflix / Prime | 2,725 / 12,301 |
| Median IMDb, Netflix / Prime | 6.3 / 6.0 |
| Share rated 7.0 or higher, Netflix / Prime | 27.3% / 20.7% |

## 7. Notes
- Power BI stores file paths. If the file is opened on another computer, change the data source to the local copy of each CSV.
- Every visual should say which source it uses (catalog file or IMDb file).
