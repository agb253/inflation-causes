"""fig11: causes of PCE inflation by quarter, 2020-2024.

Panel A adds up to actual PCE inflation (build_pce_causes.py).
Panel B: published estimates of the policy pieces inside the demand line (fig9 inputs,
CPI-based studies); they are not added to panel A.
Panel C: profit's share of nonfinancial corporate prices (build_unit_profits.py).
"""
import matplotlib
matplotlib.use("Agg")
import csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
p = pd.read_csv(ROOT + "output/pce_causes_quarterly.csv", index_col=0)
s = pd.read_csv(ROOT + "output/separate_causes_yoy.csv", index_col=0).reindex(p.index)
q = list(p.index); x = np.arange(len(q))
lab = [f"Q1\n{k[:4]}" if k.endswith("Q1") else f"Q{k[-1]}" for k in q]
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"

A = [  # key, label, color, linestyle
    ("demand", "Demand: relief laws (Trump & Biden), low rates, reopening", "#6250d6", "-"),
    ("goods_supply", "COVID supply chains: goods", "#1baf7a", "-"),
    ("war", "War in Ukraine: food & energy supply shock (2022Q1-2023Q1)", "#eb6834", "-"),
    ("energy_other", "Other food & energy supply shocks (COVID 2020-21, later)", "#eda100", "-"),
    ("svc_supply", "Supply limits in services (incl. staff shortages)", "#e87ba4", "-"),
    ("housing", "Housing (rent & owners' rent)", "#008300", "-"),
    ("ambiguous", "Too small to label supply or demand", "#9a9893", "-"),
    ("baseline", "Pre-existing inflation (2015-19 average)", "#52514e", (0, (6, 3))),
]

fig, ax = plt.subplots(3, 1, figsize=(13, 16), sharex=True, gridspec_kw={"height_ratios": [3.2, 1.9, 1.2]})
for a in ax:
    a.grid(axis="y", color=GRID, lw=.8); a.set_axisbelow(True)
    for sp in ("top", "right"): a.spines[sp].set_visible(False)
    a.axhline(0, color=MUTED, lw=.8)
    for yr in range(1, 5): a.axvline(4 * yr - .5, color=GRID, lw=.8)

a = ax[0]
for k, name, col, ls in A:
    a.plot(x, p[k], color=col, lw=2.2, ls=ls, marker="o" if ls == "-" else None, ms=3.5, label=name, zorder=3)
    if k + "_lo" in p:
        a.fill_between(x, p[k + "_lo"], p[k + "_hi"], color=col, alpha=.18, lw=0, zorder=2)
a.plot(x, p.total, color="#b0aea8", lw=6, alpha=.7, label="Sum of all the causes above", zorder=4)
a.plot(x, p.official_pce_yoy, color=INK, lw=2.4, label="Actual PCE inflation (BEA)", zorder=5)
a.set_ylabel("Percentage points of year-over-year PCE inflation", color=MUTED)
a.set_title("A.  What PCE inflation was made of, 2020-2024  (the causes add up to actual inflation)",
            loc="left", fontsize=13, color=INK)
a.legend(loc="upper left", fontsize=9.3, frameon=False, ncol=2)
a.set_ylim(-2.2, 8.2)

a = ax[1]
B = [("trump", "Relief laws signed by Trump (CARES, Dec-2020 act)", "#e34948"),
     ("biden", "Relief laws signed by Biden (American Rescue Plan)", "#2a78d6"),
     ("fed", "Fed rate hikes (vs. holding rates at zero)", "#0b0b0b")]
a.plot(x, p.demand, color="#6250d6", lw=2.6, marker="o", ms=3.5, label="Demand line from panel A (measured)", zorder=4)
for k, name, col in B:
    a.plot(x, s[k], color=col, lw=2, ls=(0, (5, 2)), label=name + "  [published estimate]", zorder=3)
    a.fill_between(x, s[k + "_lo"], s[k + "_hi"], color=col, alpha=.12, lw=0, zorder=2)
a.set_ylabel("Percentage points of inflation", color=MUTED)
a.set_title("B.  Inside the demand line: what published studies estimate for each policy  (not added to panel A)",
            loc="left", fontsize=13, color=INK)
a.legend(loc="lower left", fontsize=9.3, frameon=False)
a.text(.995, .97, "These studies use CPI and their own models. Their combined effects do not fit inside\n"
       "the measured demand line, so they are shown for size and timing only.",
       transform=a.transAxes, ha="right", va="top", fontsize=9, color=MUTED)

a = ax[2]
u = pd.read_csv(ROOT + "output/unit_profits_quarterly.csv", index_col=0).reindex(q)
rows = [(c, per, float(v.replace(",", ""))) for c, per, v in csv.reader(open(ROOT + "data/raw/bea/NipaDataQ.txt"))
        if c in ("A455RD", "A463RD")]
d = pd.DataFrame(rows, columns=["s", "q", "v"]).pivot(index="q", columns="s", values="v")
norm = (100 * d.A463RD / d.A455RD).loc["2015Q1":"2019Q4"].mean()
a.plot(x, u.profit_share_of_price, color=INK, lw=2.4, marker="o", ms=3.5)
a.axhline(norm, color=MUTED, lw=1.2, ls=(0, (6, 3)))
a.text(len(q) - .6, norm - .55, f"2015-19 average {norm:.1f}%", ha="right", fontsize=9.5, color=MUTED)
a.set_ylim(10, 20)
a.set_ylabel("Profit, % of price", color=MUTED)
a.set_title("C.  Greedflation check: profit's share of the price of what US corporations make  (BEA Table 1.15)",
            loc="left", fontsize=13, color=INK)
a.set_xticks(x); a.set_xticklabels(lab, fontsize=9.5)

fig.text(.01, .005,
         "Panel A: every PCE spending category (98, BEA Tables 2.4.3U-2.4.5U) is labeled supply- or demand-driven each month with the SF Fed method "
         "(Shapiro, FRBSF WP 2020-29, eqs. 20-22),\nthen assigned to exactly one cause, so nothing is counted twice. Each cause is shown minus its 2015-19 average; "
         "those averages make up 'pre-existing inflation'. Bands: range over four labeling variants.\n"
         "Panel B: fiscal = SF Fed EL 2022-07 model re-run, split by when relief money was paid; Fed = Chicago Fed Letter 483, Fig. 2F. "
         "Full method: output/METHOD_PCE_CAUSES.md", fontsize=8.3, color=MUTED, va="bottom")
fig.tight_layout(rect=(0, .045, 1, 1))
fig.savefig(ROOT + "output/fig11_pce_causes.png", dpi=150)
print("saved")
