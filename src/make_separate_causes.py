"""Separate causes that should not double-count, summed and checked against actual CPI.
Changes from src/make_user_causes.py (fig8):
 1. Shortages: the Google-search shortage index is replaced in the B&B price equation by the NY Fed Global Supply Chain Pressure Index
    (GSCPI), whose inputs are regressed on PMI new-orders / quantities-purchased to "purge demand factors" (Staff Report 1017, sec. 3.1).
    So the shortage line is supply-side, and demand from relief money or low rates no longer shows up in it.
 2. Ukraine war: only the energy & food relative-price shocks of 2022Q1-2023Q1 (spike and fall back to the pre-war level). Later moves
    are their own line, so the war is no longer charged with 2023-24 energy prices falling relative to wages.
Run from project root:  python src/make_separate_causes.py"""
import sys, runpy, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "src")
import bb_model as m, decompose as D
OUT = "output/"; NDRAW = 2000; SEED = 20261016
WAR0, WAR1 = pd.Timestamp("2022-01-01"), pd.Timestamp("2023-01-01")      # energy relative price (energy CPI / ECI) vs 2021Q4: +17.6% 2022Q2, -1.5% 2023Q1
B = runpy.run_path("src/build_quarterly_causes.py")                     # fiscal (SF Fed) and Fed (Chicago Fed) estimates, unchanged
res, Q, W, yoy, cum_q, lvl, eff, c = (B[k] for k in ["res", "Q", "W", "yoy", "cum_q", "lvl", "eff", "c"])

# ---------- GSCPI, quarterly average of monthly values; before Jan 1998 (start of the index) set to its 1998-2019 mean (same idea as the
# Google index, which the source data holds flat at 5 before 2004)
g = pd.read_excel(m.RAW + "nyfed/gscpi_data.xlsx", sheet_name="GSCPI Monthly Data", usecols=[0, 1]).dropna()
g["Date"] = pd.to_datetime(g.Date, format="%d-%b-%Y"); g = g.set_index("Date").GSCPI.astype(float)
gq = g.groupby(g.index.to_period("Q")).mean(); gq.index = gq.index.to_timestamp()
d = m.load(m.RAW + "data_us_new.csv"); d["shortage"] = gq.reindex(d.index).fillna(gq[:"2019-10-01"].mean())
print("GSCPI 1998-2019 mean (fill value before 1998):", round(gq[:"2019-10-01"].mean(), 3))
x = m.build(d); D.PROD_LAG = 0; est = m.estimate(x, D.PROD)
print("price eq. shortage coefs (GSCPI):", est["gp"][0].params.filter(like="shortage").round(3).to_dict())

# ---------- decomposition with three energy/food windows: COVID (2020-21), war (2022Q1-2023Q1), after (2023Q2-)
def zero(lo, hi):
    xz = x.copy(); msk = (xz.index >= lo) & (xz.index <= hi); xz.loc[msk, ["grpe", "grpf"]] = 0.0; return xz
XW = {"covid_energy": zero("2020-01-01", WAR0 - pd.Timedelta(days=1)), "ukraine": zero(WAR0, WAR1), "energy_after": zero(WAR1 + pd.Timedelta(days=1), "2030-01-01")}
def one(C):
    p = D.decompose(C, x).loc[:"2024-10-01"]; base = D.simulate(C, x, "base")[:len(p)]
    out = {k: base - D.simulate(C, xz, "base")[:len(p)] for k, xz in XW.items()}
    out.update(shortages=p.shortages.values, labor=p.labor_tightness.values, baseline=p.baseline_pre2020.values,
               bb_other=(p.productivity + p.unexplained).values)
    assert np.allclose(out["covid_energy"] + out["ukraine"] + out["energy_after"], p.energy + p.food), "energy windows must add up"
    return out, p.actual_cpi.values
pt, act = one(D.coefs(est)); rng = np.random.default_rng(SEED); dr = [one(D.draw(est, rng))[0] for _ in range(NDRAW)]
def pad(a): o = np.zeros(len(Q)); o[W] = a; return o
BB = ["covid_energy", "ukraine", "energy_after", "shortages", "labor", "baseline", "bb_other"]
for k in BB:
    p = pad(pt[k]); ds = np.stack([pad(r[k]) for r in dr])
    if k == "baseline": p[~W] = B["gp"][~W]; ds[:, ~W] = B["gp"][~W]   # pre-2020 quarters: baseline = actual, as in build script
    yd = np.stack([yoy(r) for r in ds]); Ld = np.stack([cum_q(r[:, None])[:, 0] for r in ds])
    res[k] = dict(y=yoy(p), lo=np.percentile(yd, 5, 0), hi=np.percentile(yd, 95, 0), L=cum_q(p[:, None])[:, 0], Llo=np.percentile(Ld, 5, 0), Lhi=np.percentile(Ld, 95, 0))
assert np.allclose(sum(res[k]["y"] for k in BB), B["actual_y"]), "B&B pieces must sum to actual CPI"
for nm, g_ in [("trump", B["gT"]), ("biden", B["gB"])]:                 # fiscal split by who signed the law that paid the money (as fig8)
    r = g_.rolling(4, min_periods=1).mean().values; e = np.nan_to_num(eff(r)); bd = np.zeros(len(Q))
    for t in range(3, len(Q)): bd[t] = sum(1.645 * c[h][1] * r[t - h] for h in range(4))
    res[nm] = dict(y=e[W], lo=(e - bd)[W], hi=(e + bd)[W], L=lvl(e)[W], Llo=lvl(e - bd)[W], Lhi=lvl(e + bd)[W])

# ---------- the check: separately estimated causes, added, vs actual CPI. bb_other is the model's unexplained remainder, so it is not a cause.
PLOT = ["ukraine", "shortages", "trump", "biden", "fed", "labor", "covid_energy", "energy_after", "baseline"]
NAME = {"ukraine": "War in Ukraine: energy & food price spike and fall-back, 2022Q1-2023Q1",
        "shortages": "Supply-chain shortages of goods (NY Fed index, demand stripped out)",
        "trump": "Laws Trump signed: CARES Act, Dec 2020 relief",
        "biden": "Law Biden signed: American Rescue Plan",
        "fed": "Fed interest-rate hikes (vs. holding rates near zero)",
        "labor": "Pent-up demand & hot labor market (job vacancies per unemployed)",
        "covid_energy": "COVID oil crash & reopening rebound (energy & food, 2020-21)",
        "energy_after": "Energy & food after the war spike (2023-24)",
        "baseline": "Pre-existing inflation (trend before 2020)"}
SOLID = {"ukraine", "shortages", "labor", "covid_energy", "energy_after", "baseline"}
idx = Q[W].to_period("Q").astype(str)
ty = pd.DataFrame({"actual_cpi_yoy": B["actual_y"]}, index=idx); tl = pd.DataFrame({"actual_cpi_cum": B["actual_L"]}, index=idx)
for k in PLOT + ["bb_other"]:
    for s, t in [("", "y"), ("_lo", "lo"), ("_hi", "hi")]: ty[k + s] = res[k][t]
    for s, t in [("", "L"), ("_lo", "Llo"), ("_hi", "Lhi")]: tl[k + s] = res[k][t]
ty["sum_of_causes"] = ty[PLOT].sum(axis=1); tl["sum_of_causes"] = tl[PLOT].sum(axis=1)
ty.round(3).to_csv(OUT + "separate_causes_yoy.csv"); tl.round(3).to_csv(OUT + "separate_causes_cumulative.csv")
pd.set_option("display.width", 250)
print(ty[["actual_cpi_yoy", "sum_of_causes"] + PLOT + ["bb_other"]].round(2).to_string())
print(tl[["actual_cpi_cum", "sum_of_causes"] + PLOT + ["bb_other"]].round(2).to_string())

# ---------- figure (same layout as fig8)
COL = {"ukraine": "#eb6834", "trump": "#d8504d", "biden": "#2f5fd0", "shortages": "#17a2b8", "labor": "#eda100", "fed": "#1baf7a",
       "covid_energy": "#8c5a2b", "energy_after": "#c9a27e", "baseline": "#7d7c75", "sum_of_causes": "#5a2d82"}
xx = np.arange(len(idx)); lab = [q[:4] + "\nQ1" if q.endswith("Q1") else q[4:] for q in idx]
fig, ax = plt.subplots(2, 1, figsize=(15, 15.5), gridspec_kw={"height_ratios": [1.2, 1]})
for a, dd, cpi, ylab in [(ax[0], ty, "actual_cpi_yoy", "Percentage points of year-over-year CPI inflation"),
                         (ax[1], tl, "actual_cpi_cum", "Cumulative rise in prices since end of 2019 (percent)")]:
    a.axvspan(-.5, 3.5, color="#d8504d", alpha=.06, zorder=0); a.axvspan(3.5, len(idx) - .5, color="#2f5fd0", alpha=.05, zorder=0)
    over = dd.sum_of_causes > dd[cpi]
    a.fill_between(xx, dd[cpi], dd.sum_of_causes, where=over, interpolate=True, color="#d62728", alpha=.22, hatch="///", lw=0, zorder=2, label="Sum ABOVE actual: the estimates disagree (claim more inflation than happened)")
    a.fill_between(xx, dd[cpi], dd.sum_of_causes, where=~over, interpolate=True, color="#9a9a9a", alpha=.28, lw=0, zorder=2, label="Sum below actual: not explained by these estimates")
    for k in PLOT:
        a.fill_between(xx, dd[k + "_lo"], dd[k + "_hi"], color=COL[k], alpha=.08, lw=0, zorder=1)
        if k in SOLID: a.plot(xx, dd[k], color=COL[k], lw=2.2, marker="o", ms=3.5, alpha=.9, label=NAME[k], zorder=3)
        else: a.plot(xx, dd[k], color=COL[k], lw=2.6, ls=(0, (6, 3)), alpha=.95, label=NAME[k], zorder=3)
    a.plot(xx, dd.sum_of_causes, color=COL["sum_of_causes"], lw=3, ls=(0, (1, 1.2)), label="Sum of all the causes", zorder=4)
    a.plot(xx, dd[cpi], color="black", lw=3.3, label="Actual CPI inflation (BLS)", zorder=5)
    a.axhline(0, color="#444", lw=.8); a.set_ylabel(ylab); a.set_xticks(xx); a.set_xticklabels(lab, fontsize=8.5)
    bot, top = a.get_ylim()
    a.text(1.5, top * .97, "Trump", ha="center", va="top", color="#a02c2a", fontsize=11, fontweight="bold")
    a.text(11.5, top * .97, "Biden (from Jan 20, 2021)", ha="center", va="top", color="#244f9e", fontsize=11, fontweight="bold")
    for q, t in [("2021Q1", "ARP signed 3/11/21"), ("2022Q1", "Invasion 2/24/22\nFed first hike 3/16/22")]:
        i = list(idx).index(q); a.axvline(i, color="#666", ls=":", lw=1); a.text(i + .1, bot + (top - bot) * .03, t, fontsize=8.5, va="bottom", color="#333")
ax[0].set_xlim(-.5, len(idx) - .5); ax[1].set_xlim(-.5, len(idx) + .6)
ends = sorted(((tl[k].iloc[-1], k) for k in PLOT + ["actual_cpi_cum", "sum_of_causes"]), reverse=True); ypos = []
for v, k in ends:
    p = v if not ypos else min(v, ypos[-1] - 1.0); ypos.append(p)
    ax[1].text(len(idx) - .35, p, "%.1f" % v, va="center", fontsize=8.5, fontweight="bold", color=COL.get(k, "black"))
ax[0].set_title("Causes of US inflation by quarter, 2020-2024: each cause's contribution to year-over-year CPI inflation", loc="left", fontweight="bold", fontsize=13)
ax[1].set_title("Cumulative (running total): how much each cause has added to the price level since end of 2019", loc="left", fontweight="bold", fontsize=13)
h, l = ax[0].get_legend_handles_labels(); H = dict(zip(l, h))
g1 = ax[0].legend([H[NAME[k]] for k in PLOT if k in SOLID], [NAME[k] for k in PLOT if k in SOLID], title="SOLID lines with dots: Bernanke-Blanchard model",
                  loc="upper left", bbox_to_anchor=(0, -.09), fontsize=9.3, frameon=True, handlelength=4.5, title_fontproperties={"weight": "bold", "size": 9.5})
ax[0].add_artist(g1)
ax[0].legend([H[NAME[k]] for k in PLOT if k not in SOLID] + [h[-2], h[-1], h[0], h[1]], [NAME[k] for k in PLOT if k not in SOLID] + [l[-2], l[-1], l[0], l[1]],
             title="DASHED lines: separate studies (SF Fed, Chicago Fed)", loc="upper right", bbox_to_anchor=(1, -.09), fontsize=9.3,
             frameon=True, handlelength=4.5, title_fontproperties={"weight": "bold", "size": 9.5})
fig.text(.01, .005,
 "Check: separate, correct estimates should add up to at or a little below actual CPI.  Red hatching = above: the relief-money study (SF Fed) and the Bernanke-Blanchard model cannot both be right about 2020-22.\n"
 "Shortages use the NY Fed supply-chain index, built to strip out demand.  Light bands = 90% (Fed: interquartile).  Not estimated: quantitative easing, greedflation as a cause, international pressures,\n"
 "tariffs, other Trump/Biden policies, housing/healthcare trends.  Every model, number and assumption: output/SEPARATE_CAUSES_NOTES.md.", fontsize=8.5, color="#333")
plt.tight_layout(rect=(0, .04, 1, 1)); plt.subplots_adjust(hspace=.55)
fig.savefig(OUT + "fig9_separate_causes.png", dpi=140); print("saved")
