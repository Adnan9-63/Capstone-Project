"""
IMDb rating comparison: Netflix vs Prime Video (unique titles).

Usage:
    python src/rating_analysis.py

Works on the original Kaggle file or on the cleaned file (ott_cleaned.csv).
Every number used in the report is written to results.json by this script.
"""
import sys, os, json
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CSV = sys.argv[1] if len(sys.argv) > 1 else "data/raw/ott_cleaned.csv"
OUT = sys.argv[2] if len(sys.argv) > 2 else "outputs"
os.makedirs(os.path.join(OUT, "figures"), exist_ok=True)
rng = np.random.default_rng(42)
B = 10000          # bootstrap resamples
HIGH = 7.0         # "highly rated" cut-off used by the whole team

# ---------------------------------------------------------------- load and prepare
raw = pd.read_csv(CSV)
raw = raw.drop(columns=[c for c in raw.columns if c.startswith("Unnamed")], errors="ignore")
raw["platform"] = np.where(raw["Netflix"] == 1, "Netflix", "Prime Video")
raw["imdb"] = pd.to_numeric(raw["IMDb"], errors="coerce").replace(0, np.nan)   # 0.0 is a placeholder

# the file has one row per title-genre pair; keep one record per platform, title and year
titles = (raw.groupby(["platform", "Title", "Year"], as_index=False)
             .agg(imdb=("imdb", "first"), n_genres=("Genre", "nunique")))

def era(y):
    if y < 1980: return "Before 1980"
    if y < 2000: return "1980-1999"
    if y < 2010: return "2000-2009"
    return "2010-2021"
titles["era"] = titles["Year"].apply(era)
ERAS = ["Before 1980", "1980-1999", "2000-2009", "2010-2021"]

res = {"file": os.path.basename(CSV), "rows_in_file": int(len(raw)),
       "records_unique": int(len(titles)),
       "title_year_pairs_unique": int(titles.drop_duplicates(["Title", "Year"]).shape[0]),
       "on_both_platforms": int((titles.groupby(["Title", "Year"]).platform.nunique() > 1).sum()),
       "year_min": int(titles.Year.min()), "year_max": int(titles.Year.max())}

# ---------------------------------------------------------------- descriptive statistics
def describe(s_all, s):
    return {"records": int(len(s_all)), "rated": int(len(s)), "missing": int(len(s_all) - len(s)),
            "mean": float(s.mean()), "median": float(s.median()), "sd": float(s.std(ddof=1)),
            "q1": float(s.quantile(.25)), "q3": float(s.quantile(.75)),
            "min": float(s.min()), "max": float(s.max()), "share_high": float((s >= HIGH).mean())}

grp = {p: titles[titles.platform == p] for p in ["Netflix", "Prime Video"]}
rated = {p: g.imdb.dropna() for p, g in grp.items()}
res["desc"] = {p: describe(grp[p].imdb, rated[p]) for p in grp}
res["median_year"] = {p: float(grp[p].Year.median()) for p in grp}
res["share_since_2010"] = {p: float((grp[p].Year >= 2010).mean()) for p in grp}

# ---------------------------------------------------------------- platform comparison
a, b = rated["Netflix"].values, rated["Prime Video"].values
U, p = stats.mannwhitneyu(a, b, alternative="two-sided")
res["mwu"] = {"U": float(U), "p": float(p),
              "rank_biserial": float(2 * U / (len(a) * len(b)) - 1),
              "prob_netflix_higher": float(U / (len(a) * len(b)))}

def boot_ci(fn, x, y, reps=B):
    d = np.empty(reps)
    for i in range(reps):
        d[i] = fn(rng.choice(x, len(x)), rng.choice(y, len(y)))
    return [float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))]

res["median_diff"] = {"value": float(np.median(a) - np.median(b)),
                      "ci": boot_ci(lambda x, y: np.median(x) - np.median(y), a, b)}
res["share_diff"] = {"value": float((a >= HIGH).mean() - (b >= HIGH).mean()),
                     "ci": boot_ci(lambda x, y: (x >= HIGH).mean() - (y >= HIGH).mean(), a, b)}

res["mean_diff"] = {"value": float(a.mean() - b.mean()),
                    "ci": boot_ci(lambda x, y: x.mean() - y.mean(), a, b)}

# ---------------------------------------------------------------- effect of release era
era_rows = []
for e in ERAS:
    ra = titles[(titles.platform == "Netflix") & (titles.era == e)]
    rb = titles[(titles.platform == "Prime Video") & (titles.era == e)]
    xa, xb = ra.imdb.dropna().values, rb.imdb.dropna().values
    row = {"era": e,
           "n_netflix_titles": int(len(ra)), "n_prime_titles": int(len(rb)),
           "share_of_netflix": float(len(ra) / len(grp["Netflix"])),
           "share_of_prime": float(len(rb) / len(grp["Prime Video"])),
           "n_netflix": int(len(xa)), "n_prime": int(len(xb)),
           "median_netflix": float(np.median(xa)) if len(xa) else None,
           "median_prime": float(np.median(xb)) if len(xb) else None,
           "mean_netflix": float(xa.mean()) if len(xa) else None,
           "mean_prime": float(xb.mean()) if len(xb) else None,
           "high_netflix": float((xa >= HIGH).mean()) if len(xa) else None,
           "high_prime": float((xb >= HIGH).mean()) if len(xb) else None}
    if len(xa) >= 30 and len(xb) >= 30:
        u, pv = stats.mannwhitneyu(xa, xb, alternative="two-sided")
        row.update({"p": float(pv), "rank_biserial": float(2 * u / (len(xa) * len(xb)) - 1)})
    else:
        row.update({"p": None, "rank_biserial": None})
    era_rows.append(row)
res["era"] = era_rows

# Prime Video re-weighted to Netflix's era mix (direct standardisation)
w = {r["era"]: r["share_of_netflix"] for r in era_rows}
std_mean = sum(w[r["era"]] * r["mean_prime"] for r in era_rows if r["mean_prime"] is not None)
std_high = sum(w[r["era"]] * r["high_prime"] for r in era_rows if r["high_prime"] is not None)
res["standardised_prime"] = {"mean": float(std_mean), "share_high": float(std_high),
                             "netflix_mean": res["desc"]["Netflix"]["mean"],
                             "netflix_share_high": res["desc"]["Netflix"]["share_high"],
                             "prime_mean": res["desc"]["Prime Video"]["mean"],
                             "prime_share_high": res["desc"]["Prime Video"]["share_high"]}

# ---------------------------------------------------------------- figures
plt.rcParams.update({"font.family": "serif", "font.size": 10})
COL = {"Netflix": "#B3261E", "Prime Video": "#1F5FA8"}
bins = np.arange(0, 10.5, 0.5)

fig, ax = plt.subplots(figsize=(6.4, 3.4))
for pl in ["Netflix", "Prime Video"]:
    ax.hist(rated[pl], bins=bins, density=True, alpha=0.55, color=COL[pl], label="%s (n = %d)" % (pl, len(rated[pl])))
ax.axvline(HIGH, color="black", ls="--", lw=1)
ax.set_xlabel("IMDb rating"); ax.set_ylabel("Share of titles (density)")
ax.legend(frameon=False); ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "figures", "fig1_rating_histogram.png"), dpi=200); plt.close(fig)

fig, ax = plt.subplots(figsize=(4.6, 3.4))
bp = ax.boxplot([rated["Netflix"], rated["Prime Video"]], patch_artist=True,
                medianprops={"color": "black"}, flierprops={"marker": ".", "markersize": 2, "alpha": 0.4})
for patch, pl in zip(bp["boxes"], ["Netflix", "Prime Video"]):
    patch.set_facecolor(COL[pl]); patch.set_alpha(0.55)
ax.set_xticklabels(["Netflix", "Prime Video"])
ax.set_ylabel("IMDb rating"); ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "figures", "fig2_rating_boxplot.png"), dpi=200); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.4, 3.4))
x = np.arange(len(ERAS))
mn = [r["median_netflix"] for r in era_rows]
mp = [r["median_prime"] for r in era_rows]
ax.plot(x, mn, "o-", color=COL["Netflix"], label="Netflix", lw=1.6, ms=6)
ax.plot(x, mp, "s-", color=COL["Prime Video"], label="Prime Video", lw=1.6, ms=6)
for xi, a_, b_ in zip(x, mn, mp):
    ax.annotate("%.1f" % (np.floor(a_ * 10 + 0.5 + 1e-9) / 10), (xi, a_), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=9, color=COL["Netflix"])
    ax.annotate("%.1f" % (np.floor(b_ * 10 + 0.5 + 1e-9) / 10), (xi, b_), textcoords="offset points", xytext=(0, -14), ha="center", fontsize=9, color=COL["Prime Video"])
ax.set_xticks(x); ax.set_xticklabels(ERAS); ax.set_ylabel("Median IMDb rating"); ax.set_ylim(5, 7.5)
ax.legend(frameon=False, loc="upper right"); ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(OUT, "figures", "fig3_median_by_era.png"), dpi=200); plt.close(fig)

with open(os.path.join(OUT, "results.json"), "w") as f:
    json.dump(res, f, indent=2)
print(json.dumps(res, indent=2))
