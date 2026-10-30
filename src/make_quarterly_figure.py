"""Quarterly line graph: additive causes (sum to CPI), cumulative price level, and policy overlays. Reads output/quarterly_causes_*.csv (src/build_quarterly_causes.py)."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
O = "output/"
y = pd.read_csv(O + "quarterly_causes_yoy.csv", index_col=0); c = pd.read_csv(O + "quarterly_causes_cumulative.csv", index_col=0)
x = np.arange(len(y)); lab = [q[2:4] + " " + q[4:] if q[4:] != "Q1" else q[:4] + "\nQ1" for q in y.index]
COL = dict(baseline="#7d7c75", shortages="#2a78d6", energy_food="#eb6834", labor="#eda100", bb_other="#8a6fd1", fiscal="#c0392b", fed="#1baf7a", profits="#e87ba4")
NAME = dict(baseline="Normal pre-pandemic inflation trend (B&B baseline)", shortages="Supply chain / shortages", energy_food="Energy & food: COVID oil crash 2020, Ukraine war 2022",
            labor="Labor-market tightness (where fiscal + Fed + pent-up demand show up)", bb_other="Other / unexplained (incl. markups, productivity)",
            fiscal="Fiscal stimulus (SF Fed model)", fed="Fed policy (Chicago Fed model)", profits="Corporate profits / unit-profit accounting (BEA)")
def shade(a):
    a.axvspan(-.5, 3.5, color="#d8504d", alpha=.06, zorder=0); a.axvspan(3.5, len(y) - .5, color="#3a6fd8", alpha=.05, zorder=0)
def line(a, d, k, ls="-", lw=2.1, band=True, tag=""):
    v = d[k].values
    if band and d[k + "_lo"].notna().any():
        a.fill_between(x, d[k + "_lo"], d[k + "_hi"], color=COL[k], alpha=.15, lw=0, zorder=1)
    a.plot(x, v, color=COL[k], lw=lw, ls=ls, marker="o", ms=3, alpha=.92, label=NAME[k] + tag, zorder=3)
fig, ax = plt.subplots(3, 1, figsize=(14, 19), gridspec_kw={"height_ratios": [1.15, 1, 1]})
# ---- A: additive causes
a = ax[0]; shade(a)
for k in ["baseline", "shortages", "energy_food", "labor", "bb_other"]: line(a, y, k)
a.plot(x, y.actual_cpi_yoy, color="black", lw=3.2, label="Actual CPI inflation (BLS, year over year)", zorder=5)
a.axhline(0, color="#444", lw=.8)
for q, t, yy in [("2020Q1", "COVID lockdowns", 9.9), ("2021Q1", "American Rescue Plan\nsigned 3/11/21", 9.9), ("2022Q1", "Russia invades Ukraine 2/24/22;\nFed first hike 3/16/22", 9.9)]:
    i = list(y.index).index(q); a.axvline(i, color="#666", ls=":", lw=1); a.text(i + .1, yy, t.replace("\n", "\n"), fontsize=8.5, va="top", color="#333")
a.text(1.5, 11.2, "Trump administration", ha="center", color="#a02c2a", fontsize=10); a.text(11.5, 11.2, "Biden administration (from Jan 20, 2021)", ha="center", color="#244f9e", fontsize=10)
a.set_ylim(-2.5, 11.6); a.set_ylabel("Percentage points of year-over-year CPI inflation")
a.set_title("A. What the data-based model says pushed prices each quarter (the five lines add up exactly to the black CPI line)", loc="left", fontweight="bold", fontsize=12.5)
a.legend(loc="upper center", bbox_to_anchor=(.5, -.07), ncol=2, fontsize=8.5, frameon=False)
# ---- B: cumulative
b = ax[1]; shade(b)
for k in ["baseline", "shortages", "energy_food", "labor", "bb_other"]: line(b, c, k)
b.plot(x, c.actual, color="black", lw=3.2, label="Actual cumulative CPI (percent since 2019Q4)", zorder=5)
b.axhline(0, color="#444", lw=.8)
for k in ["baseline", "shortages", "energy_food", "labor", "bb_other"]:
    b.text(len(y) - .35, c[k].iloc[-1] + {"energy_food": -.55, "bb_other": .45}.get(k, 0), "%.1f" % c[k].iloc[-1], va="center", fontsize=9, fontweight="bold", color=COL[k])
b.text(len(y) - .35, c.actual.iloc[-1], "%.1f" % c.actual.iloc[-1], va="center", fontsize=9.5, fontweight="bold"); b.set_xlim(-.5, len(y) + .4)
b.set_ylabel("Cumulative CPI rise since 2019Q4 (percent)")
b.set_title("B. Running total since 2019Q4: how much of the price-level rise each cause has added", loc="left", fontweight="bold", fontsize=12.5)
b.legend(loc="upper left", fontsize=8.5, frameon=False)
# ---- C: overlays
o = ax[2]; shade(o)
line(o, y, "fiscal", tag=" - 90% band from authors' regression")
line(o, y, "fed", tag=" - interquartile band read off chart")
line(o, y, "profits", ls="--", lw=1.7, tag=" - overlaps other causes; no band")
o.axhline(0, color="#444", lw=.8)
o.set_ylabel("Percentage points of year-over-year inflation (negative = lowered it)")
o.set_title("C. Policy and profit estimates from separate models (counterfactual effects: NOT additive with A)", loc="left", fontweight="bold", fontsize=12.5)
o.legend(loc="upper center", bbox_to_anchor=(.5, -.07), ncol=1, fontsize=8.5, frameon=False)
for a_ in ax: a_.set_xticks(x); a_.set_xticklabels(lab, fontsize=8); a_.set_xlim(-.5, len(y) + (.4 if a_ is b else -.5))
fig.text(.01, .004, "Sources & assumptions: output/METHODS_quarterly.md.  A,B: Bernanke-Blanchard model re-estimated on Lorenzoni's replication data (bands = 90% from 2,000 coefficient draws; coefficient uncertainty only).\n"
 "C fiscal: SF Fed EL 2022-07 model run on the authors' data to 2021Q3, extended with BEA income to 2021Q4; later quarters = lag tail only.\nC Fed: Chicago Fed Letter 483, Fig 2F, digitized; post-2023Q3 values are model projections.\nC profits: BEA table 1.15 accounting, excess over 2015-19 pace.", fontsize=7.5, color="#444")
plt.tight_layout(rect=(0, .03, 1, 1)); fig.savefig(O + "fig6_quarterly_causes.png", dpi=140); print("saved")
# ---- D: fiscal by who signed the law
f = pd.read_csv(O + "fiscal_by_signer_yoy.csv", index_col=0); fg, fa = plt.subplots(figsize=(13, 5.2))
fa.bar(x, f.trump, color="#d8504d", label="Money from laws Trump signed (CARES Mar 2020; Dec 2020 relief act)", width=.75)
fa.bar(x, f.biden, bottom=f.trump, color="#3a6fd8", label="Money from the law Biden signed (American Rescue Plan, 3/11/21)", width=.75)
fa.plot(x, y.fiscal, color="black", lw=1.5, marker="o", ms=3, label="Total fiscal effect (same as line in panel C)")
fa.axhline(0, color="#444", lw=.8); fa.set_xticks(x); fa.set_xticklabels(lab, fontsize=8); fa.set_ylabel("Percentage points of CPI inflation (yoy)")
fa.set_title("Fiscal-stimulus effect on inflation by quarter, split by who signed the law that paid out the money", loc="left", fontweight="bold")
fa.legend(frameon=False, fontsize=9, loc="upper right"); fg.text(.01, .01, "Split = each quarter's income gap apportioned by share of excess federal transfers (BEA PCTR above 2019 trend) paid Mar2020-Feb2021 vs Mar2021 on; timing of money, not of signing.", fontsize=7.5, color="#444")
plt.tight_layout(rect=(0, .03, 1, 1)); fg.savefig(O + "fig7_fiscal_by_signer.png", dpi=140)
