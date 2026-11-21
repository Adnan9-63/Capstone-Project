"""
Extra checks for Report 2: genre-wise ratings, overlap titles, decade trend, cut-off robustness, age rating, low-rated tail.
Usage: python src/more_findings.py
"""
import sys, os, json
import numpy as np, pandas as pd
from scipy import stats

CSV = sys.argv[1] if len(sys.argv) > 1 else "data/raw/ott_cleaned.csv"
OUT = sys.argv[2] if len(sys.argv) > 2 else "outputs"
raw = pd.read_csv(CSV)
raw = raw.drop(columns=[c for c in raw.columns if c.startswith("Unnamed")], errors="ignore")
raw["platform"] = np.where(raw["Netflix"] == 1, "Netflix", "Prime Video")
raw["imdb"] = pd.to_numeric(raw["IMDb"], errors="coerce").replace(0, np.nan)
raw["Rating"] = raw["Rating"].replace("Unknown", np.nan)

t = (raw.groupby(["platform", "Title", "Year"], as_index=False)
        .agg(imdb=("imdb", "first"), age=("Rating", "first"), n_genres=("Genre", "nunique")))
g = raw[["platform", "Title", "Year", "Genre", "imdb"]].drop_duplicates(["platform", "Title", "Year", "Genre"])
res = {}

# 1. genre-wise rating comparison (genres present on both platforms), Holm correction
common = sorted(set(g[g.platform == "Netflix"].Genre) & set(g[g.platform == "Prime Video"].Genre))
rows = []
for gen in common:
    a = g[(g.platform == "Netflix") & (g.Genre == gen)].imdb.dropna().values
    b = g[(g.platform == "Prime Video") & (g.Genre == gen)].imdb.dropna().values
    u, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    rows.append({"genre": gen, "n_netflix": len(a), "n_prime": len(b), "median_netflix": float(np.median(a)),
                 "median_prime": float(np.median(b)), "mean_netflix": float(a.mean()), "mean_prime": float(b.mean()),
                 "r": float(2 * u / (len(a) * len(b)) - 1), "p": float(p)})
order = np.argsort([r["p"] for r in rows]); m = len(rows); run = 0
for rank, i in enumerate(order):
    run = max(run, min(1.0, rows[i]["p"] * (m - rank)))
    rows[i]["p_holm"] = float(run)
res["genres_common"] = common
res["genre_tests"] = rows

# genre share of titles (title counts per genre / titles on platform)
tot = t.groupby("platform").size()
share = {}
for pl in ["Netflix", "Prime Video"]:
    gg = g[g.platform == pl].groupby("Genre").size() / tot[pl]
    share[pl] = {k: float(v) for k, v in gg.items()}
res["genre_share"] = share
res["genres_only_netflix"] = sorted(set(g[g.platform == "Netflix"].Genre) - set(g[g.platform == "Prime Video"].Genre))
res["genres_only_prime"] = sorted(set(g[g.platform == "Prime Video"].Genre) - set(g[g.platform == "Netflix"].Genre))
res["avg_genres_per_title"] = {pl: float(t[t.platform == pl].n_genres.mean()) for pl in tot.index}
res["multi_genre_share"] = {pl: float((t[t.platform == pl].n_genres > 1).mean()) for pl in tot.index}

# 2. titles on both platforms
both = t.groupby(["Title", "Year"]).platform.nunique()
bk = both[both > 1].index
pv = t.set_index(["Title", "Year"]).loc[bk].reset_index().pivot_table(index=["Title", "Year"], columns="platform", values="imdb", aggfunc="first")
res["overlap"] = {"titles": int(len(pv)), "same_rating": float((pv["Netflix"] == pv["Prime Video"]).mean()),
                  "median_rating": float(pv.stack().median()),
                  "median_year": float(pd.Series([k[1] for k in pv.index]).median())}
# do overlap titles rate higher than the rest?
ov = t.set_index(["Title", "Year"]).index.isin(bk)
res["overlap"]["median_rating_rest"] = float(t[~ov].imdb.median())

# 3. decade trend (decades with at least 30 rated titles on a platform)
t["decade"] = (t.Year // 10 * 10).astype(int)
tr = []
for d in sorted(t.decade.unique()):
    row = {"decade": int(d)}
    for pl in ["Netflix", "Prime Video"]:
        x = t[(t.platform == pl) & (t.decade == d)].imdb.dropna()
        row[pl] = {"n": int(len(x)), "median": float(x.median()) if len(x) else None}
    tr.append(row)
res["decade_trend"] = tr

# 4. robustness: other cut-offs and tails
rt = {}
for cut in [6.0, 6.5, 7.0, 7.5, 8.0]:
    rt[str(cut)] = {pl: float((t[t.platform == pl].imdb.dropna() >= cut).mean()) for pl in tot.index}
res["share_at_least"] = rt
res["share_below_5"] = {pl: float((t[t.platform == pl].imdb.dropna() < 5).mean()) for pl in tot.index}

# 5. age rating availability and mix
res["age_known_share"] = {pl: float(t[t.platform == pl].age.notna().mean()) for pl in tot.index}
mix = {}
for pl in tot.index:
    k = t[(t.platform == pl) & t.age.notna()].age.value_counts(normalize=True)
    mix[pl] = {a: float(v) for a, v in k.items()}
res["age_mix_among_known"] = mix

# 6. size and recency
res["titles"] = {pl: int(tot[pl]) for pl in tot.index}
res["share_2015_plus"] = {pl: float((t[t.platform == pl].Year >= 2015).mean()) for pl in tot.index}

with open(os.path.join(OUT, "more_findings.json"), "w") as f:
    json.dump(res, f, indent=2)
print(json.dumps(res, indent=1))
