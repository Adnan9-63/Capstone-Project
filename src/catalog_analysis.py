"""
Catalog analysis: what is in the Netflix and Prime Video catalogs (movies vs TV, years, genres, age ratings, runtime, origin).

Run from the repository root (after prepare_data.py and clean_catalog.py):
    python src/catalog_analysis.py
Writes outputs/catalog/catalog_results.json, outputs/catalog/*.csv and outputs/catalog/figures/*.png
"""
import json, os
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "outputs/catalog"
os.makedirs(OUT + "/figures", exist_ok=True)
T = pd.read_csv("data/processed/catalog_titles.csv")
GG = pd.read_csv("data/processed/catalog_genre_groups.csv")
LK = pd.read_csv("data/processed/catalog_imdb_link.csv")
PL = ["Netflix", "Prime Video"]
COL = {"Netflix": "#B3261E", "Prime Video": "#1F5FA8"}
res = {}

def cramers_v(table):
    chi2, p, dof, _ = stats.chi2_contingency(table)
    n = table.values.sum()
    return float(chi2), float(p), float(np.sqrt(chi2 / (n * (min(table.shape) - 1))))

def mwu(a, b):
    """Mann-Whitney U (a = Netflix, b = Prime). Returns p and rank-biserial r (positive: a tends to be higher)."""
    u, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    return float(p), float(2 * u / (len(a) * len(b)) - 1)

# ---------------------------------------------------------------- 1 movies vs TV shows
ct = pd.crosstab(T["platform"], T["type"])
chi2, p, v = cramers_v(ct)
res["type_mix"] = {"counts": {pl: {t: int(ct.loc[pl, t]) for t in ct.columns} for pl in PL},
                   "share_movies": {pl: float(ct.loc[pl, "Movie"] / ct.loc[pl].sum()) for pl in PL},
                   "chi2": chi2, "p": p, "cramers_v": v}

# ---------------------------------------------------------------- 2 release years
res["years"] = {}
for label, sub in [("all", T), ("movies", T[T["type"] == "Movie"])]:
    a = sub[sub.platform == "Netflix"]["release_year"].values
    b = sub[sub.platform == "Prime Video"]["release_year"].values
    pv, r = mwu(a, b)
    res["years"][label] = {"median": {"Netflix": float(np.median(a)), "Prime Video": float(np.median(b))},
                           "share_2015_plus": {"Netflix": float((a >= 2015).mean()), "Prime Video": float((b >= 2015).mean())},
                           "p": pv, "rank_biserial": r}
ORDER = ["Before 1980", "1980-1999", "2000-2009", "2010-2021"]
per = pd.crosstab(T["platform"], T["release_period"], normalize="index")[ORDER]
per.round(4).to_csv(OUT + "/release_period_share.csv")
res["release_period_share"] = {pl: {k: float(per.loc[pl, k]) for k in ORDER} for pl in PL}

# ---------------------------------------------------------------- 3 genres (mapped groups)
den = T.groupby(["platform", "type"]).size()
gs = GG.groupby(["platform", "type", "genre_group"]).size().reset_index(name="titles")
gs["share"] = [r.titles / den[(r.platform, r.type)] for r in gs.itertuples()]
gs.round(4).to_csv(OUT + "/genre_group_share.csv", index=False)
res["genre_share"] = {f"{r.platform}|{r.type}|{r.genre_group}": float(r.share) for r in gs.itertuples()}
res["no_real_genre_share"] = {f"{pl}|{t}": float(((T.platform == pl) & (T.type == t) & (T.n_genre_groups == 0)).sum() / den[(pl, t)])
                              for pl in PL for t in ["Movie", "TV Show"]}

# ---------------------------------------------------------------- 4 age rating groups
AGE = ["Kids and all ages", "Teen and parental guidance", "Adult", "Not rated"]
ag = T.groupby(["platform", "type", "age_group"]).size().reset_index(name="titles")
ag["share"] = [r.titles / den[(r.platform, r.type)] for r in ag.itertuples()]
ag.round(4).to_csv(OUT + "/age_group_share.csv", index=False)
res["age_share"] = {f"{r.platform}|{r.type}|{r.age_group}": float(r.share) for r in ag.itertuples()}
res["age_tests"] = {}
for t in ["Movie", "TV Show"]:
    sub = T[(T["type"] == t) & (T.age_group != "Not rated")]
    c2, pv, vv = cramers_v(pd.crosstab(sub["platform"], sub["age_group"]))
    res["age_tests"][t] = {"chi2": c2, "p": pv, "cramers_v": vv}

# ---------------------------------------------------------------- 5 runtime and seasons
mv = T[(T["type"] == "Movie") & T.runtime_min.notna()]
a = mv[mv.platform == "Netflix"].runtime_min.values; b = mv[mv.platform == "Prime Video"].runtime_min.values
pv, r = mwu(a, b)
res["runtime"] = {"n": {"Netflix": int(len(a)), "Prime Video": int(len(b))},
                  "median": {"Netflix": float(np.median(a)), "Prime Video": float(np.median(b))},
                  "mean": {"Netflix": float(a.mean()), "Prime Video": float(b.mean())},
                  "q1": {"Netflix": float(np.percentile(a, 25)), "Prime Video": float(np.percentile(b, 25))},
                  "q3": {"Netflix": float(np.percentile(a, 75)), "Prime Video": float(np.percentile(b, 75))},
                  "p": pv, "rank_biserial": r}
tv = T[(T["type"] == "TV Show") & T.seasons.notna()]
a = tv[tv.platform == "Netflix"].seasons.values; b = tv[tv.platform == "Prime Video"].seasons.values
pv, r = mwu(a, b)
res["seasons"] = {"n": {"Netflix": int(len(a)), "Prime Video": int(len(b))},
                  "median": {"Netflix": float(np.median(a)), "Prime Video": float(np.median(b))},
                  "share_one_season": {"Netflix": float((a == 1).mean()), "Prime Video": float((b == 1).mean())},
                  "share_three_plus": {"Netflix": float((a >= 3).mean()), "Prime Video": float((b >= 3).mean())},
                  "p": pv, "rank_biserial": r}

# ---------------------------------------------------------------- 6 origin (Netflix only; Prime country is blank for most titles)
ORIG = ["India", "United States", "Other", "Unknown"]
og = T.groupby(["platform", "type", "origin_group"]).size().reset_index(name="titles")
og["share"] = [r.titles / den[(r.platform, r.type)] for r in og.itertuples()]
og.round(4).to_csv(OUT + "/origin_share.csv", index=False)
res["country_known_share"] = {pl: float(T[T.platform == pl].country_known.mean()) for pl in PL}
res["origin_share"] = {f"{r.platform}|{r.type}|{r.origin_group}": float(r.share) for r in og.itertuples()}
kn = T[(T.platform == "Netflix") & T.country_known]
res["netflix_known_origin_share"] = {t: {o: float((kn[kn["type"] == t].origin_group == o).mean()) for o in ["India", "United States", "Other"]}
                                     for t in ["Movie", "TV Show"]}

# ---------------------------------------------------------------- 7 IMDb for Netflix movies by origin (exploratory, linked subset)
nl = LK[(LK.platform == "Netflix") & LK.matched & (LK.origin_group != "Unknown")]
rows = []
for o in ["India", "United States", "Other"]:
    x = nl[nl.origin_group == o].imdb
    rows.append({"origin": o, "n": int(len(x)), "median": float(x.median()), "mean": float(x.mean()), "share_7_plus": float((x >= 7).mean())})
pd.DataFrame(rows).round(3).to_csv(OUT + "/netflix_imdb_by_origin.csv", index=False)
pv, r = mwu(nl[nl.origin_group == "India"].imdb.values, nl[nl.origin_group == "United States"].imdb.values)
res["netflix_imdb_by_origin"] = {"rows": rows, "india_vs_us_p": pv, "india_vs_us_r": r,
                                 "linked_movies": int(LK[(LK.platform == "Netflix")].matched.sum()),
                                 "prime_linked_with_known_origin": int(((LK.platform == "Prime Video") & LK.matched & (LK.origin_group != "Unknown")).sum())}

with open(OUT + "/catalog_results.json", "w") as f:
    json.dump(res, f, indent=2)

# ---------------------------------------------------------------- figures
plt.rcParams.update({"font.family": "serif", "font.size": 10})
def clean(ax): ax.spines[["top", "right"]].set_visible(False)

fig, ax = plt.subplots(figsize=(6.2, 2.4))
for i, pl in enumerate(PL):
    m = res["type_mix"]["share_movies"][pl]
    ax.barh(i, m * 100, color=COL[pl], alpha=0.8); ax.barh(i, (1 - m) * 100, left=m * 100, color="#B8BEC4")
    ax.text(m * 50, i, "Movies %.0f%%" % (m * 100), ha="center", va="center", color="white", fontsize=9)
    ax.text(m * 100 + (1 - m) * 50, i, "TV %.0f%%" % ((1 - m) * 100), ha="center", va="center", fontsize=9)
ax.set_yticks([0, 1]); ax.set_yticklabels(PL); ax.set_xlim(0, 100); ax.set_xlabel("Share of titles (%)"); clean(ax)
fig.tight_layout(); fig.savefig(OUT + "/figures/fig1_type_mix.png", dpi=200); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.4, 3.3)); x = np.arange(4); w = 0.36
for j, pl in enumerate(PL):
    ax.bar(x + (j - 0.5) * w, [per.loc[pl, k] * 100 for k in ORDER], w, color=COL[pl], alpha=0.8, label=pl)
ax.set_xticks(x); ax.set_xticklabels(ORDER); ax.set_ylabel("Share of titles (%)"); ax.legend(frameon=False); clean(ax)
fig.tight_layout(); fig.savefig(OUT + "/figures/fig2_release_period.png", dpi=200); plt.close(fig)

REAL = [g for g in gs.genre_group.unique() if g != "Other / not a genre"]
fig, axes = plt.subplots(1, 2, figsize=(9, 4.4), sharey=True)
for ax, t in zip(axes, ["Movie", "TV Show"]):
    sub = gs[(gs["type"] == t) & gs.genre_group.isin(REAL)].pivot(index="genre_group", columns="platform", values="share").reindex(REAL).fillna(0)
    sub = sub.loc[sub.sum(axis=1).sort_values().index]
    y = np.arange(len(sub))
    for j, pl in enumerate(PL):
        ax.barh(y + (j - 0.5) * 0.38, sub[pl] * 100, 0.38, color=COL[pl], alpha=0.8, label=pl)
    ax.set_yticks(y); ax.set_yticklabels(sub.index); ax.set_title(t + "s"); ax.set_xlabel("Share of titles with the genre (%)"); clean(ax)
axes[0].legend(frameon=False, loc="lower right")
fig.tight_layout(); fig.savefig(OUT + "/figures/fig3_genres.png", dpi=200); plt.close(fig)

AC = ["#7BAE7F", "#E0B050", "#B3261E", "#B8BEC4"]
fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.2), sharey=True)
for ax, t in zip(axes, ["Movie", "TV Show"]):
    for i, pl in enumerate(PL):
        left = 0
        for k, c in zip(AGE, AC):
            s = res["age_share"].get(f"{pl}|{t}|{k}", 0) * 100
            ax.barh(i, s, left=left, color=c, label=k if i == 0 and t == "Movie" else None); left += s
    ax.set_yticks([0, 1]); ax.set_yticklabels(PL); ax.set_xlim(0, 100); ax.set_title(t + "s"); ax.set_xlabel("Share of titles (%)"); clean(ax)
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=4, frameon=False, fontsize=8)
fig.tight_layout(rect=(0, 0.1, 1, 1)); fig.savefig(OUT + "/figures/fig4_age_groups.png", dpi=200); plt.close(fig)

fig, ax = plt.subplots(figsize=(4.8, 3.3))
bp = ax.boxplot([mv[mv.platform == pl].runtime_min for pl in PL], patch_artist=True, showfliers=False, medianprops={"color": "black"})
for patch, pl in zip(bp["boxes"], PL): patch.set_facecolor(COL[pl]); patch.set_alpha(0.6)
ax.set_xticklabels(PL); ax.set_ylabel("Movie runtime (minutes)"); clean(ax)
fig.tight_layout(); fig.savefig(OUT + "/figures/fig5_runtime.png", dpi=200); plt.close(fig)

fig, ax = plt.subplots(figsize=(6.0, 2.8))
for i, t in enumerate(["Movie", "TV Show"]):
    left = 0
    for o, c in zip(ORIG, ["#E0A030", "#1F5FA8", "#7BAE7F", "#B8BEC4"]):
        s = res["origin_share"].get(f"Netflix|{t}|{o}", 0) * 100
        ax.barh(i, s, left=left, color=c, label=o if i == 0 else None); left += s
ax.set_yticks([0, 1]); ax.set_yticklabels(["Netflix movies", "Netflix TV shows"]); ax.set_xlim(0, 100)
ax.set_xlabel("Share of titles (%), first listed country"); ax.legend(frameon=False, fontsize=8, ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.28)); clean(ax)
fig.tight_layout(); fig.savefig(OUT + "/figures/fig6_netflix_origin.png", dpi=200, bbox_inches="tight"); plt.close(fig)

print(json.dumps({k: res[k] for k in ["type_mix", "years", "runtime", "seasons", "country_known_share", "netflix_known_origin_share", "age_tests", "netflix_imdb_by_origin"]}, indent=1))
