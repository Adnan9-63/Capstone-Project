"""
Step 1: build one-record-per-title tables from the cleaned CSV.

Run from the repository root:
    python src/prepare_data.py
Reads  data/raw/ott_cleaned.csv
Writes data/processed/titles.csv and data/processed/genres.csv
"""
import re, sys
import numpy as np
import pandas as pd

CSV = sys.argv[1] if len(sys.argv) > 1 else "data/raw/ott_cleaned.csv"
OUT = sys.argv[2] if len(sys.argv) > 2 else "data/processed"

def norm(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())

raw = pd.read_csv(CSV)
raw = raw.drop(columns=[c for c in raw.columns if c.startswith("Unnamed")], errors="ignore")
raw["platform"] = np.where(raw["Netflix"] == 1, "Netflix", "Prime Video")
raw["imdb"] = pd.to_numeric(raw["IMDb"], errors="coerce").replace(0, np.nan)   # 0.0 is a placeholder
raw["rt"] = pd.to_numeric(raw["Rotten Tomatoes"], errors="coerce")
raw["age_rating"] = raw["Rating"].replace("Unknown", np.nan)

# the file has one row per title-genre pair, so keep one record per platform, title and year
titles = (raw.groupby(["platform", "Title", "Year"], as_index=False)
             .agg(imdb=("imdb", "first"), rt=("rt", "first"), age_rating=("age_rating", "first")))
titles.insert(0, "title_key", titles["Title"].map(norm) + "|" + titles["Year"].astype(str))
titles = titles.rename(columns={"Title": "title", "Year": "year"})
titles["release_period"] = pd.cut(titles["year"], [0, 1979, 1999, 2009, 3000],
                                  labels=["Before 1980", "1980-1999", "2000-2009", "2010-2021"]).astype(str)
titles["period_order"] = titles["release_period"].map({"Before 1980": 1, "1980-1999": 2, "2000-2009": 3, "2010-2021": 4})

genres = raw[["platform", "Title", "Year", "Genre"]].drop_duplicates()
genres.insert(0, "title_key", genres["Title"].map(norm) + "|" + genres["Year"].astype(str))
genres = genres[["title_key", "platform", "Genre"]].rename(columns={"Genre": "genre"})

titles.to_csv(f"{OUT}/titles.csv", index=False)
genres.to_csv(f"{OUT}/genres.csv", index=False)
print("rows in file:", len(raw))
print("title records (one per platform and title):", len(titles))
print(titles.platform.value_counts().to_string())
print("title-genre rows:", len(genres))
print("titles on both platforms:", int((titles.groupby("title_key").platform.nunique() > 1).sum()))
