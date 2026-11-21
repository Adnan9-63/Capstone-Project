"""
Clean the combined catalog file (Netflix + Prime Video titles) for the dashboard.

Run from the repository root:
    python src/prepare_data.py       (first, builds data/processed/titles.csv)
    python src/clean_catalog.py

Reads   data/raw/Combined_Dataset.csv, data/mappings/*.csv
Writes  data/processed/catalog_titles.csv        one row per title
        data/processed/catalog_genres.csv        one row per title and original genre label
        data/processed/catalog_genre_groups.csv  one row per title and mapped genre group
        data/processed/catalog_imdb_link.csv     IMDb rating for movies that match the IMDb file (optional)
        outputs/catalog/cleaning_log.json        counts for every step
"""
import json, os, re
import numpy as np
import pandas as pd

RAW = "data/raw/Combined_Dataset.csv"
OUT = "data/processed"
log = {}

def norm(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())

d = pd.read_csv(RAW)
log["rows_in_file"] = int(len(d))
d["platform"] = d["Platform"].replace({"Prime": "Prime Video"})
d["catalog_key"] = np.where(d["platform"] == "Netflix", "N-", "P-") + d["show_id"].astype(str)   # show_id repeats across platforms
assert d["catalog_key"].is_unique

# --- titles: missing and damaged (some titles were turned into dates, probably by Excel)
pat = r"^\d{4}-\d{2}-\d{2}( 00:00:00)?$"
d["title_missing"] = d["title"].isna()
d["title_damaged"] = d["title"].astype(str).str.match(pat) & ~d["title_missing"]
d["title"] = d["title"].fillna("(missing)")
log["titles_missing"] = int(d["title_missing"].sum())
log["titles_damaged_into_dates"] = int(d["title_damaged"].sum())

# --- three Netflix rows have the runtime in the rating column
slip = d["rating"].astype(str).str.contains("min", na=False) & d["duration"].isna()
d.loc[slip, "duration"] = d.loc[slip, "rating"]
d.loc[slip, "rating"] = np.nan
log["rating_cells_with_runtime_fixed"] = int(slip.sum())

# --- repeated rows: same platform, type, title (ignoring case and punctuation) and year
d["k"] = d["title"].map(norm)
dup = (~d["title_missing"]) & d.duplicated(["platform", "type", "k", "release_year"], keep="first")
log["repeated_rows_removed"] = int(dup.sum())
log["repeated_rows_examples"] = d.loc[dup, ["platform", "title", "release_year"]].head(8).values.tolist()
d = d[~dup].copy()
log["rows_after_cleaning"] = int(len(d))

# --- runtime and seasons from the duration text ("113 min", "2 Seasons")
d["runtime_min"] = pd.to_numeric(d["duration"].str.extract(r"(\d+)\s*min", expand=False), errors="coerce")
d["seasons"] = pd.to_numeric(d["duration"].str.extract(r"(\d+)\s*Season", expand=False), errors="coerce")

# --- country: first listed country is used for origin; only reliable for Netflix
def tokens(s):
    return [t.strip() for t in str(s).split(",") if t.strip()] if pd.notna(s) else []
tk = d["country"].map(tokens)
d["country_known"] = tk.map(bool)
d["country_first"] = tk.map(lambda t: t[0] if t else np.nan)
d["india_any"] = tk.map(lambda t: "India" in t)
d["us_any"] = tk.map(lambda t: "United States" in t)
d["origin_group"] = np.select([~d["country_known"], d["country_first"] == "India", d["country_first"] == "United States"],
                              ["Unknown", "India", "United States"], default="Other")

# --- age rating groups
am = pd.read_csv("data/mappings/age_rating_mapping.csv")
d["age_rating_raw"] = d["rating"]
d["age_group"] = d["rating"].map(dict(zip(am.raw_rating, am.age_group)))
log["unmapped_age_ratings"] = sorted(d.loc[d["age_group"].isna() & d["rating"].notna(), "rating"].unique().tolist())
d["age_group"] = d["age_group"].fillna("Not rated")

# --- release period (same bands as the IMDb analysis) and decade
def period(y):
    return "Before 1980" if y < 1980 else "1980-1999" if y < 2000 else "2000-2009" if y < 2010 else "2010-2021"
d["release_period"] = d["release_year"].map(period)
d["decade"] = (d["release_year"] // 10 * 10).astype(int)
d["period_order"] = d["release_period"].map({"Before 1980": 1, "1980-1999": 2, "2000-2009": 3, "2010-2021": 4})
d["age_order"] = d["age_group"].map({"Kids and all ages": 1, "Teen and parental guidance": 2, "Adult": 3, "Not rated": 4})

# --- genres: the label "Arts, Entertainment, and Culture" contains commas, protect it before splitting
gm = pd.read_csv("data/mappings/genre_mapping.csv")
gmap = dict(zip(gm.raw_label, gm.genre_group))
txt = d["listed_in"].fillna("").str.replace("Arts, Entertainment, and Culture", "Arts Entertainment and Culture", regex=False)
rows = []
for key, plat, typ, t in zip(d["catalog_key"], d["platform"], d["type"], txt):
    for lab in [x.strip() for x in t.split(",") if x.strip()]:
        rows.append((key, plat, typ, lab, gmap.get(lab)))
g = pd.DataFrame(rows, columns=["catalog_key", "platform", "type", "raw_genre", "genre_group"])
log["unmapped_genre_labels"] = sorted(g.loc[g["genre_group"].isna(), "raw_genre"].unique().tolist())
g["genre_group"] = g["genre_group"].fillna("Other / not a genre")
gg = g.drop_duplicates(["catalog_key", "genre_group"])[["catalog_key", "platform", "type", "genre_group"]]
real = gg[gg["genre_group"] != "Other / not a genre"].groupby("catalog_key").size()
d["n_genre_groups"] = d["catalog_key"].map(real).fillna(0).astype(int)

# --- titles on both platforms (same title, year and type)
okt = d[~d["title_missing"]]
nb = okt.groupby(["k", "release_year", "type"])["platform"].nunique()
both = set(nb[nb > 1].index)
d["on_both"] = [(k, y, t) in both for k, y, t in zip(d["k"], d["release_year"], d["type"])]
log["titles_on_both_platforms"] = int(len(both))

d["title_key"] = d["k"] + "|" + d["release_year"].astype(str)
d["director_known"] = d["director"].notna()
d["cast_known"] = d["cast"].notna()

cols = ["catalog_key", "platform", "type", "title", "release_year", "title_key", "title_missing", "title_damaged",
        "country_known", "country_first", "origin_group", "india_any", "us_any", "age_rating_raw", "age_group",
        "age_order", "runtime_min", "seasons", "n_genre_groups", "release_period", "period_order", "decade", "on_both", "director_known", "cast_known"]
d[cols].to_csv(f"{OUT}/catalog_titles.csv", index=False)
g.to_csv(f"{OUT}/catalog_genres.csv", index=False)
gg.to_csv(f"{OUT}/catalog_genre_groups.csv", index=False)

# --- optional link to the IMDb file (movies only)
link_path = f"{OUT}/titles.csv"
if os.path.exists(link_path):
    a = pd.read_csv(link_path)[["platform", "title_key", "imdb"]]
    mv = d[d["type"] == "Movie"][["catalog_key", "platform", "title_key", "origin_group"]]
    lk = mv.merge(a, on=["platform", "title_key"], how="left")
    lk["matched"] = lk["imdb"].notna()
    lk.to_csv(f"{OUT}/catalog_imdb_link.csv", index=False)
    log["imdb_link"] = {p: {"movies": int((lk.platform == p).sum()), "with_imdb": int(lk[lk.platform == p]["matched"].sum())}
                        for p in ["Netflix", "Prime Video"]}

log["final"] = {"titles": int(len(d)),
                "by_platform_type": {f"{p}|{t}": int(n) for (p, t), n in d.groupby(["platform", "type"]).size().items()},
                "genre_rows": int(len(g)), "genre_group_rows": int(len(gg))}
os.makedirs("outputs/catalog", exist_ok=True)
with open("outputs/catalog/cleaning_log.json", "w") as f:
    json.dump(log, f, indent=2)
print(json.dumps(log, indent=2))
