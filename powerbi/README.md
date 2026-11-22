# Power BI Dashboard — Comparative Analysis of OTT Platforms

**Owner:** Md. Adnan (Group 03, IIT Patna)  
**Topic:** Comparative Analysis of Netflix & Amazon Prime Video

This folder contains the complete dashboard implementation assets, automated scripts, color themes, and interactive dashboard preview.

---

## 📁 Files in this Folder

| File | What it is | How to use |
|---|---|---|
| `dashboard_preview.html` | **Interactive 7-page dashboard replica** | Open in any browser (Edge/Chrome) to view and present all pages interactively |
| `measures.dax` | **All 22 DAX Measures** | Copy/paste directly into Power BI Desktop "New Measure" |
| `queries.m` | **Power Query (M Code)** | Paste into Power Query Advanced Editor to load and type all 4 tables automatically |
| `theme.json` | **Power BI Report Theme** | In Power BI: `View` > `Themes` > `Browse for themes` > select `theme.json` |
| `README.md` | **Step-by-step build & validation guide** | Reference for setup, relationships, and number checks |

---

## 1. Automated Data Loading (Power Query)

Instead of manually configuring columns, use `powerbi/queries.m`:
1. In Power BI Desktop, click **Transform Data** (Power Query Editor).
2. Go to **New Source > Blank Query > Advanced Editor**.
3. Paste the M code for each table from `queries.m`.
4. Tables created:
   - `catalog_titles` (from `data/processed/catalog_titles.csv`)
   - `catalog_genre_groups` (from `data/processed/catalog_genre_groups.csv`)
   - `imdb_titles` (from `data/processed/titles.csv`)
   - `imdb_genres` (from `data/processed/genres.csv`)

---

## 2. Relationships (Model View)

- `catalog_titles[catalog_key]` (1) to `catalog_genre_groups[catalog_key]` (*) — Single filter direction (`catalog_titles` filters `catalog_genre_groups`).
- `imdb_titles[link]` (1) to `imdb_genres[link]` (*) — Single filter direction (`imdb_titles` filters `imdb_genres`).
- **Do not connect catalog tables to IMDb tables** (they are two separate sources).
- Always use `platform` and `type` from `catalog_titles` (or `imdb_titles`) for slicers and legends.

---

## 3. Custom Theme

Import `powerbi/theme.json` (`View` > `Themes` > `Browse for themes`).
- Netflix: `#B3261E` (Crimson)
- Prime Video: `#1F5FA8` (Navy Blue)
- Slicers & Fonts: Segoe UI, aligned with IIT Patna capstone presentation palette.

---

## 4. DAX Measures

All measures are pre-written and documented in `powerbi/measures.dax`. Key measures:
```dax
Titles = COUNTROWS(catalog_titles)
Movies = CALCULATE([Titles], catalog_titles[type] = "Movie")
TV Shows = CALCULATE([Titles], catalog_titles[type] = "TV Show")
Movie Share = DIVIDE([Movies], [Titles], 0)
Median Release Year = MEDIAN(catalog_titles[release_year])
Share 2015 Plus = DIVIDE(CALCULATE([Titles], catalog_titles[release_year] >= 2015), [Titles], 0)
Median Movie Runtime = CALCULATE(MEDIAN(catalog_titles[runtime_min]), catalog_titles[type] = "Movie")
Genre Share = DIVIDE(DISTINCTCOUNT(catalog_genre_groups[catalog_key]), [Titles], 0)

Rated Titles = COUNT(imdb_titles[imdb])
Median IMDb = MEDIAN(imdb_titles[imdb])
Share 7 Plus = DIVIDE(CALCULATE(COUNT(imdb_titles[imdb]), imdb_titles[imdb] >= 7), COUNT(imdb_titles[imdb]), 0)
Share Below 5 = DIVIDE(CALCULATE(COUNT(imdb_titles[imdb]), imdb_titles[imdb] < 5), COUNT(imdb_titles[imdb]), 0)
```

---

## 5. Dashboard Pages (7 Pages)

| Page | Visuals |
|---|---|
| **1. Overview** | 4 KPI Cards: Titles, Movie Share, Median Release Year, Share 2015+. Visuals: 100% Stacked Bar (Mix), Clustered Bar (Release Period). Slicers: Platform, Type. |
| **2. Content Mix & Years** | Line Chart: Titles by Year (1980–2021). Clustered Column: Titles by Decade. Summary Table. |
| **3. Genres** | Horizontal Bar Chart: Genre Share by 13 standardized groups (Netflix vs Prime). Slicer: Type. |
| **4. Age Ratings** | Donut / 100% Stacked Bars: Age Rating Mix (Adult, Teen, Kids, Not Rated) for Movies and TV. |
| **5. Runtime & Seasons** | Histogram: Movie Runtime (minutes). Clustered Bar: TV Shows by Seasons (1, 2, 3-5, 6+). KPI Cards. |
| **6. IMDb Ratings** | Distribution Area/Line: Rating Density. Line Chart: Median IMDb by Release Period. KPI Cards (Rated Titles, Median 6.3 vs 6.0, % 7.0+). |
| **7. Data Notes** | Scope boundary definitions, data source notes, and Prime country limitation details. |

---

## 6. Verification Numbers (Must Match Python Scripts)

| Metric | Netflix | Prime Video | Status |
|---|---|---|---|
| Catalog Titles | 8,797 | 9,658 | Verified |
| Movie Share | 70% | 81% | Verified |
| Median Release Year | 2017 | 2016 | Verified |
| Released 2015 or later | 71% | 56% | Verified |
| Median Movie Runtime | 98 min | 91 min | Verified |
| Rated Movies (IMDb) | 2,725 | 12,301 | Verified |
| Median IMDb Rating | 6.3 | 6.0 | Verified |
| Share Rated >= 7.0 | 27.3% | 20.7% | Verified |
| Share Rated < 5.0 | 12.0% | 24.3% | Verified |

