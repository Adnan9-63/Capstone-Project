"""
Check how well the two extra datasets match our main file.

Run from the repository root:
    python src/dataset_overlap_check.py
Reads  data/raw/ott_cleaned.csv
       data/raw/extra/amazon_prime_titles.csv
       data/raw/extra/netflix_tr2.csv
Writes outputs/overlap_check.json
"""
import json, re
import numpy as np
import pandas as pd

def norm(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())

main = pd.read_csv("data/raw/ott_cleaned.csv")
main["platform"] = np.where(main["Netflix"] == 1, "Netflix", "Prime Video")
u = main.groupby(["platform", "Title", "Year"], as_index=False).size()
u["k"] = u["Title"].map(norm)

prime = pd.read_csv("data/raw/extra/amazon_prime_titles.csv")
nflx = pd.read_csv("data/raw/extra/netflix_tr2.csv")
prime["k"] = prime["title"].map(norm)
nflx["k"] = nflx["title"].map(norm)

def match_rate(left, right, ycol):
    r = right[["k", ycol]].drop_duplicates()
    m = left.merge(r, left_on=["k", "Year"], right_on=["k", ycol], how="left", indicator=True)
    return int((m["_merge"] == "both").sum()), int(len(left))

un, up = u[u.platform == "Netflix"], u[u.platform == "Prime Video"]
mn = match_rate(un, nflx, "releaseYear")
mp = match_rate(up, prime, "release_year")

res = {
    "main_file": {"rows": int(len(main)), "title_records": int(len(u)),
                  "netflix": int(len(un)), "prime": int(len(up)),
                  "year_range": [int(main.Year.min()), int(main.Year.max())]},
    "amazon_prime_titles": {"rows": int(len(prime)),
                            "movies": int((prime.type == "Movie").sum()),
                            "tv_shows": int((prime.type == "TV Show").sum()),
                            "year_range": [int(prime.release_year.min()), int(prime.release_year.max())],
                            "country_filled": int(prime.country.notna().sum()),
                            "age_rating_filled": int(prime.rating.notna().sum()),
                            "has_imdb_rating": False},
    "netflix_tr2": {"rows": int(len(nflx)),
                    "movies": int((nflx.type == "movie").sum()),
                    "tv_shows": int((nflx.type == "tv").sum()),
                    "year_range": [int(nflx.releaseYear.min()), int(nflx.releaseYear.max())],
                    "has_imdb_rating": True, "has_votes": True,
                    "available_in_india_share": float(nflx.availableCountries.astype(str).str.contains(r"\bIN\b").mean())},
    "match_title_and_year": {
        "netflix_matched": mn[0], "netflix_total": mn[1], "netflix_share": mn[0] / mn[1],
        "prime_matched": mp[0], "prime_total": mp[1], "prime_share": mp[0] / mp[1]},
}
with open("outputs/overlap_check.json", "w") as f:
    json.dump(res, f, indent=2)
print(json.dumps(res, indent=2))
