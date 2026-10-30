"""One line per cause, named the way the question names them (Ukraine war, Trump policies, Biden policies, greedflation, supply chain,
pent-up demand, Fed, COVID, pre-existing trend). Reuses every estimate from src/build_quarterly_causes.py and adds one new split:
the B&B energy+food effect is divided at 2022Q1 into shocks before the invasion (COVID crash/reopening) and shocks from 2022Q1 on (war era).
B&B is linear in its exogenous inputs, so  effect(all energy/food shocks) = effect(2020-21 shocks) + effect(2022+ shocks)  exactly.
Run from project root:  python src/make_user_causes.py"""
import sys, runpy, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "src")
import bb_model as m, decompose as D
B = runpy.run_path("src/build_quarterly_causes.py")                     # res, comp, gT, gB, c, eff, lvl, Q, W, yoy, cum_q ...
res, Q, W, yoy, cum_q, lvl, eff, c = (B[k] for k in ["res", "Q", "W", "yoy", "cum_q", "lvl", "eff", "c"])
OUT = "output/"; WAR = pd.Timestamp("2022-01-01")                       # ASSUMPTION: energy & food relative-price shocks from 2022Q1 on = war era (invasion 2/24/22)

# ---------- 1. war-era vs pre-war energy & food, same model, same 2,000 coefficient draws as output/draws.npy (same seed, same order)
x = m.build(m.load(m.RAW + "data_us_new.csv")); D.PROD_LAG = 0
est = m.estimate(x, D.PROD)
xw = x.copy(); xw.loc[xw.index >= WAR, ["grpe", "grpf"]] = 0.0          # remove only the 2022Q1+ energy/food relative-price shocks
def war(C): return D.simulate(C, x, "base") - D.simulate(C, xw, "base")
def pad(a): out = np.zeros(len(Q)); out[W] = a[:W.sum()]; return out   # 2019 quarters = 0
rng = np.random.default_rng(20261016); wd = []
for i in range(len(np.load(OUT + "draws.npy", mmap_mode="r"))):
    wd.append(pad(war(D.draw(est, rng))))
wd = np.array(wd); wp = pad(war(D.coefs(est)))
draws = np.load(OUT + "draws.npy"); ef = draws[:, :, 0] + draws[:, :, 1]   # energy + food, per draw
efp = pd.read_csv(OUT + "decomp_point.csv", index_col=0, parse_dates=True).loc[:"2024-10-01"]
efp = pad((efp.energy + efp.food).values)
pre_p = efp - wp; pre_d = np.stack([pad(ef[i]) for i in range(len(ef))]) - wd
def pack(p, d):
    y = yoy(p); yd = np.stack([yoy(r) for r in d]); L = cum_q(p[:, None])[:, 0]; Ld = np.stack([cum_q(r[:, None])[:, 0] for r in d])
    return dict(y=y, lo=np.percentile(yd, 5, 0), hi=np.percentile(yd, 95, 0), L=L, Llo=np.percentile(Ld, 5, 0), Lhi=np.percentile(Ld, 95, 0))
res["ukraine"] = pack(wp, wd); res["covid_energy"] = pack(pre_p, pre_d)
assert np.allclose(res["ukraine"]["y"] + res["covid_energy"]["y"], res["energy_food"]["y"]), "war + pre-war must equal energy+food"

# ---------- 2. fiscal effect split by who signed the law that paid the money (same formula as build script, band per component)
for nm, g_ in [("trump", B["gT"]), ("biden", B["gB"])]:
    r = g_.rolling(4, min_periods=1).mean().values; e = np.nan_to_num(eff(r)); bd = np.zeros(len(Q))
    for t in range(3, len(Q)): bd[t] = sum(1.645 * c[h][1] * r[t - h] for h in range(4))
    res[nm] = dict(y=e[W], lo=(e - bd)[W], hi=(e + bd)[W], L=lvl(e)[W], Llo=lvl(e - bd)[W], Lhi=lvl(e + bd)[W])
assert np.allclose(res["trump"]["y"] + res["biden"]["y"] + np.nan_to_num(eff(B["gap"].sub(B["gT"] + B["gB"]).rolling(4, min_periods=1).mean().values))[W], res["fiscal"]["y"])

# ---------- 3. table
ORDER = ["ukraine", "trump", "biden", "profits", "shortages", "labor", "fed", "covid_energy", "baseline", "bb_other"]
NAME = {"ukraine": "War in Ukraine: energy & food price shocks from 2022Q1 on",
        "trump": "Trump-signed relief laws (CARES Act, Dec 2020 relief)",
        "biden": "Biden-signed relief law (American Rescue Plan)",
        "profits": "Greedflation: growth in profit per unit (accounting, not causal)",
        "shortages": "Supply-chain shortages",
        "labor": "Pent-up demand & hot labor market (job vacancies per unemployed)",
        "fed": "Fed interest-rate hikes",
        "covid_energy": "COVID oil crash & reopening rebound (energy & food, 2020-21)",
        "baseline": "Pre-existing inflation trend (before 2020)",
        "bb_other": "Other / unexplained"}
SOLID = {"ukraine", "shortages", "labor", "covid_energy", "baseline", "bb_other"}   # one model (B&B): these six sum exactly to CPI
assert np.allclose(sum(res[k]["y"] for k in SOLID), B["actual_y"]) and np.allclose(sum(res[k]["L"] for k in SOLID), B["actual_L"]), "solid lines must sum to CPI"
idx = Q[W].to_period("Q").astype(str)
ty = pd.DataFrame({"actual_cpi_yoy": B["actual_y"]}, index=idx); tl = pd.DataFrame({"actual_cpi_cum": B["actual_L"]}, index=idx)
for k in ORDER:
    for s, t in [("", "y"), ("_lo", "lo"), ("_hi", "hi")]: ty[k + s] = res[k][t]
    for s, t in [("", "L"), ("_lo", "Llo"), ("_hi", "Lhi")]: tl[k + s] = res[k][t]
# The check the chart is built around: separately estimated causes, added up, should come to no more than actual CPI.
# Left out of the sum: profits (an accounting split of every price rise into wages, other costs and profit, so it overlaps every cause)
# and B&B "other/unexplained" (a residual, i.e. whatever the model could not attribute). Whatever is left between the sum and CPI is drawn as the gap.
PLOT = ["ukraine", "trump", "biden", "shortages", "labor", "fed", "covid_energy", "baseline"]
ty["sum_of_causes"] = ty[PLOT].sum(axis=1); tl["sum_of_causes"] = tl[PLOT].sum(axis=1)
ty.round(3).to_csv(OUT + "user_causes_yoy.csv"); tl.round(3).to_csv(OUT + "user_causes_cumulative.csv")
pd.set_option("display.width", 250); print(ty[["actual_cpi_yoy", "sum_of_causes"] + ORDER].round(2).to_string()); print(tl[["actual_cpi_cum"] + ORDER].iloc[[-1]].round(2).to_string())

# ---------- 4. figure
COL = {"ukraine": "#eb6834", "trump": "#d8504d", "biden": "#2f5fd0", "profits": "#e87ba4", "shortages": "#17a2b8", "labor": "#eda100",
       "fed": "#1baf7a", "covid_energy": "#8c5a2b", "baseline": "#7d7c75", "bb_other": "#8a6fd1"}
SUMLAB = "Sum of all the causes above"
xx = np.arange(len(idx)); lab = [q[:4] + "\nQ1" if q.endswith("Q1") else q[4:] for q in idx]
fig, ax = plt.subplots(2, 1, figsize=(15, 15.5), gridspec_kw={"height_ratios": [1.2, 1]})
for a, d, cpi, ylab in [(ax[0], ty, "actual_cpi_yoy", "Percentage points of year-over-year CPI inflation"),
                        (ax[1], tl, "actual_cpi_cum", "Cumulative rise in prices since end of 2019 (percent)")]:
    a.axvspan(-.5, 3.5, color="#d8504d", alpha=.06, zorder=0); a.axvspan(3.5, len(idx) - .5, color="#2f5fd0", alpha=.05, zorder=0)
    over = d.sum_of_causes > d[cpi]
    a.fill_between(xx, d[cpi], d.sum_of_causes, where=over, interpolate=True, color="#d62728", alpha=.22, hatch="///", lw=0, zorder=2, label="Sum ABOVE actual: the estimates overlap (same inflation counted twice)")
    a.fill_between(xx, d[cpi], d.sum_of_causes, where=~over, interpolate=True, color="#9a9a9a", alpha=.28, lw=0, zorder=2, label="Sum below actual: not explained by these estimates")
    for k in PLOT:
        if d[k + "_lo"].notna().any(): a.fill_between(xx, d[k + "_lo"], d[k + "_hi"], color=COL[k], alpha=.08, lw=0, zorder=1)
        if k in SOLID: a.plot(xx, d[k], color=COL[k], lw=2.2, marker="o", ms=3.5, alpha=.9, label=NAME[k], zorder=3)
        else: a.plot(xx, d[k], color=COL[k], lw=2.6, ls=(0, (6, 3)), alpha=.95, label=NAME[k], zorder=3)   # no markers, so the dashes stay visible in the legend
    a.plot(xx, d.sum_of_causes, color="#5a2d82", lw=3, ls=(0, (1, 1.2)), label=SUMLAB, zorder=4)
    a.plot(xx, d[cpi], color="black", lw=3.3, label="Actual CPI inflation (BLS)" if a is ax[0] else "Actual CPI (BLS)", zorder=5)
    a.axhline(0, color="#444", lw=.8); a.set_ylabel(ylab); a.set_xticks(xx); a.set_xticklabels(lab, fontsize=8.5)
    bot, top = a.get_ylim()
    a.text(1.5, top * .97, "Trump", ha="center", va="top", color="#a02c2a", fontsize=11, fontweight="bold")
    a.text(11.5, top * .97, "Biden (from Jan 20, 2021)", ha="center", va="top", color="#244f9e", fontsize=11, fontweight="bold")
    for q, t in [("2021Q1", "ARP signed 3/11/21"), ("2022Q1", "Invasion 2/24/22\nFed first hike 3/16/22")]:
        i = list(idx).index(q); a.axvline(i, color="#666", ls=":", lw=1); a.text(i + .1, bot + (top - bot) * .03, t, fontsize=8.5, va="bottom", color="#333")   # bottom edge, clear of the lines
ax[0].set_xlim(-.5, len(idx) - .5); ax[1].set_xlim(-.5, len(idx) + .6)
COL["sum_of_causes"] = "#5a2d82"
ends = sorted(((tl[k].iloc[-1], k) for k in PLOT + ["actual_cpi_cum", "sum_of_causes"]), reverse=True); ypos = []
for v, k in ends:                                                       # end labels, pushed apart so they don't overprint
    p = v if not ypos else min(v, ypos[-1] - 1.0); ypos.append(p)
    ax[1].text(len(idx) - .35, p, "%.1f" % v, va="center", fontsize=8.5, fontweight="bold", color=COL.get(k, "black"))
ax[0].set_title("Causes of US inflation by quarter, 2020-2024: each cause's contribution to year-over-year CPI inflation", loc="left", fontweight="bold", fontsize=13)
ax[1].set_title("Cumulative (running total): how much each cause has added to the price level since end of 2019", loc="left", fontweight="bold", fontsize=13)
h, l = ax[0].get_legend_handles_labels(); H = dict(zip(l, h))   # h[0], h[1] = the two gap fills; h[-2], h[-1] = sum and CPI
g1 = ax[0].legend([H[NAME[k]] for k in PLOT if k in SOLID], [NAME[k] for k in PLOT if k in SOLID], title="SOLID lines with dots: Bernanke-Blanchard model",
                  loc="upper left", bbox_to_anchor=(0, -.09), fontsize=9.5, frameon=True, handlelength=4.5, title_fontproperties={"weight": "bold", "size": 9.5})
ax[0].add_artist(g1)
ax[0].legend([H[NAME[k]] for k in PLOT if k not in SOLID] + [h[-2], h[-1], h[0], h[1]], [NAME[k] for k in PLOT if k not in SOLID] + [l[-2], l[-1], l[0], l[1]],
             title="DASHED lines: separate studies (SF Fed, Chicago Fed)", loc="upper right", bbox_to_anchor=(1, -.09), fontsize=9.5,
             frameon=True, handlelength=4.5, title_fontproperties={"weight": "bold", "size": 9.5})
fig.text(.01, .005,
 "Check: if each cause is estimated correctly and separately, their sum should be at or a little below actual CPI.  Red hatching = where it is above: the relief-money study and the\n"
 "Bernanke-Blanchard supply lines both claim the same 2020-22 inflation.  Light bands = 90% (Fed: interquartile).  Greedflation is not a separate line: profit data only split each price rise\n"
 "into wages, other costs and profit, which is not a cause; any excess markup sits in the gray gap.\n"
 "Not on chart (no verifiable quarterly estimate): international pressures (SF Fed: ~2 pp total, 2021Q1-2022Q4), tariffs, other Trump/Biden policies, housing/healthcare trends.\n"
 "Every model, number and assumption: output/METHODS_quarterly.md and output/USER_CAUSES_NOTES.md.", fontsize=8.5, color="#333")
plt.tight_layout(rect=(0, .05, 1, 1)); plt.subplots_adjust(hspace=.55)
fig.savefig(OUT + "fig8_causes_as_named.png", dpi=140); print("saved")
