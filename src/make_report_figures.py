"""Headline figures for the report (output/REPORT.md, web page), from output/unified_causes_quarterly.csv and
output/unified_cumulative_2021_2024.csv (both written by src/unified_model.py).
  fig13_stacked_causes.png   stacked contributions by quarter (the format of the SF Fed and Bernanke-Blanchard charts)
  fig14_cumulative.png       each cause's total 2021-2024 with its 90% range
  fig15_fed_late.png         'did the Fed act too late?': earlier-hike scenarios (output/fed_late.csv)"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
o = pd.read_csv(ROOT + "output/unified_causes_quarterly.csv", index_col=0)
cu = pd.read_csv(ROOT + "output/unified_cumulative_2021_2024.csv", index_col=0)
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
o["pre_existing"] = o.baseline + o.fed_pre2020
o["supply"] = o.shortage + o.energy_war + o.worker_shortage
o["fed"] = o.fed_easing + o.fed_hikes
GROUPS = [  # key, label, color (same hue as the cause in fig12 where one exists)
    ("pre_existing", "Pre-existing inflation (end-2019)", "#b9b7b1"),
    ("shortage", "COVID supply chains", "#eda100"),
    ("energy_war", "War in Ukraine (energy & food)", "#eb6834"),
    ("worker_shortage", "Worker shortage", "#e87ba4"),
    ("trump", "Relief paid under Trump", "#e34948"),
    ("biden", "Relief paid under Biden", "#2a78d6"),
    ("fed", "Fed (2020-21 cuts + QE, 2022-23 hikes)", "#6250d6"),
    ("pentup", "Pent-up demand", "#8a5a2b"),
    ("covid_other", "COVID shutdown drag (and 2020-21 oil & food crash/rebound)", "#3b3a37"),
    ("other_unexplained", "Other & not explained", "#d9d7d2"),
]
q = list(o.index); x = np.arange(len(q))
lab = [f"Q1\n{k[:4]}" if k.endswith("Q1") else f"Q{k[-1]}" for k in q]


def style(a):
    a.grid(axis="y", color=GRID, lw=.8); a.set_axisbelow(True)
    for sp in ("top", "right"): a.spines[sp].set_visible(False)
    a.axhline(0, color=MUTED, lw=.8)


# ---- fig13: stacked bars
fig, a = plt.subplots(figsize=(15, 8.2)); style(a)
pos, neg = np.zeros(len(q)), np.zeros(len(q))
for k, name, col in GROUPS:
    v = o[k].values
    base = np.where(v >= 0, pos, neg)
    a.bar(x, v, .78, bottom=base, color=col, edgecolor="white", linewidth=.6, label=f"{name}  [{o.loc['2022Q2', k]:+.1f}]")
    pos, neg = pos + np.maximum(v, 0), neg + np.minimum(v, 0)
a.plot(x, o.actual_pce_yoy, color=INK, lw=2.6, marker="o", ms=5, zorder=5, label="Actual PCE inflation (BEA)  [%.1f]" % o.loc["2022Q2", "actual_pce_yoy"])
a.set_xticks(x); a.set_xticklabels(lab, fontsize=9.5); a.set_xlim(-.6, len(q) - .4)
a.set_ylabel("Percentage points of year-over-year PCE inflation", color=MUTED)
a.set_title("What made up US inflation each quarter, 2020-2024", loc="left", fontsize=14, color=INK)
h, l = a.get_legend_handles_labels()
a.legend(h[::-1], l[::-1], loc="upper left", bbox_to_anchor=(1.01, 1), frameon=False, fontsize=9.2, labelspacing=.9,
         title="[ ] = points at the 2022Q2 peak", title_fontsize=8.5, alignment="left")
fig.text(.01, .01, "Bars above zero push inflation up, below zero push it down; they add up to actual inflation because 'other & not explained' is the gap "
         f"between the model and actual (largest: {o.other_unexplained.abs().max():.1f} points).\nGreedflation is estimated at about zero in every quarter "
         f"(largest {o.greed.abs().max():.2f}) and is not drawn. Source: output/unified_causes_quarterly.csv; method: output/REPORT.md.",
         fontsize=8.5, color=MUTED, va="bottom")
fig.tight_layout(rect=(0, .05, 1, 1)); fig.savefig(ROOT + "output/fig13_stacked_causes.png", dpi=150); plt.close(fig)

# ---- fig14: totals 2021-2024 with 90% ranges
ROWS = [("pre_existing", "Pre-existing inflation (end-2019)"), ("shortage", "COVID supply chains"),
        ("energy_war", "War in Ukraine (energy & food)"), ("worker_shortage", "Worker shortage"),
        ("trump", "Relief paid under Trump"), ("biden", "Relief paid under Biden"),
        ("fed_easing", "Fed 2020-21 cuts + QE"), ("fed_hikes", "Fed 2022-23 hikes"), ("pentup", "Pent-up demand"),
        ("greed", "Greedflation"), ("covid_other", "COVID shutdown drag (incl. 2020-21 oil & food)"),
        ("other_unexplained", "Other & not explained")]
cu.loc["pre_existing"] = cu.loc["baseline"] + cu.loc["fed_pre2020"]; cu.loc["pre_existing", ["lo", "hi"]] = np.nan
fig, a = plt.subplots(figsize=(12, 7.2)); style(a); a.axhline(0, lw=0); a.axvline(0, color=MUTED, lw=.8)
for i, (k, name) in enumerate(ROWS[::-1]):
    r = cu.loc[k]
    a.barh(i, r.total, .62, color="#2a78d6" if k in ("trump", "biden", "fed_easing", "fed_hikes", "pentup") else "#eda100"
           if k in ("shortage", "energy_war", "worker_shortage") else "#9a9893")
    if not np.isnan(r.lo): a.plot([r.lo, r.hi], [i, i], color=INK, lw=1.4)
    a.text(max(0, r.total, r.hi if not np.isnan(r.hi) else r.total) + .15, i, f"{r.total:+.1f}" + ("" if np.isnan(r.lo) else f"  [{r.lo:+.1f} to {r.hi:+.1f}]"),
           va="center", fontsize=9, color=INK)
a.set_yticks(range(len(ROWS))); a.set_yticklabels([n for _, n in ROWS[::-1]], fontsize=9.5)
a.set_xlabel("Points of inflation, 2021-2024 total (the four Q4-over-Q4 rates added up)", color=MUTED)
a.set_title(f"Each cause's share of 2021-2024 inflation (actual total {cu.loc['actual', 'total']:.1f} points; model {cu.loc['model_total', 'total']:.1f})",
            loc="left", fontsize=13)
fig.text(.01, .01, "Blue = demand (policy and pent-up spending), amber = supply, gray = other. Lines = 90% range over 1,000 redraws. "
         "The Fed rows' ranges are wide; see the report.", fontsize=8.5, color=MUTED)
fig.tight_layout(rect=(0, .03, 1, 1)); fig.savefig(ROOT + "output/fig14_cumulative.png", dpi=150); plt.close(fig)

# ---- fig15: Fed late
fl = pd.read_csv(ROOT + "output/fed_late.csv")
fig, ax = plt.subplots(1, 2, figsize=(14, 5.6))
NAMES = {"barnichon": "Hike from Mar 2021 to ~2% by early 2022 (SF Fed letter's path)",
         "year_early": "Start the actual 2022-23 hikes a year earlier (Mar 2021)"}
for sc, col in [("barnichon", "#2a78d6"), ("year_early", "#e34948")]:
    f = fl[fl.scenario == sc].set_index("quarter").loc["2021Q1":]
    xx = np.arange(len(f))
    for a, v, t in [(ax[0], "infl", "Change in PCE inflation (points, year over year)"), (ax[1], "unemp", "Change in unemployment rate (points)")]:
        c = "infl_yoy" if v == "infl" else "unemp"
        a.fill_between(xx, f[v + "_lo"], f[v + "_hi"], color=col, alpha=.12, lw=0)
        a.plot(xx, f[c], color=col, lw=2.2, marker="o", ms=4, label=NAMES[sc])
        a.set_title(t, loc="left", fontsize=11); style(a)
        a.set_xticks(xx); a.set_xticklabels([k if k.endswith("Q1") else k[-2:] for k in f.index], fontsize=8)
ax[0].errorbar([5], [-1.0], yerr=[[1.0], [0.8]], fmt="D", color=INK, capsize=4, label="SF Fed letter (Barnichon 2022): core PCE ~1 point lower by June 2022 (95%: 0.2-2)")
ax[1].errorbar([5], [2.0], yerr=[[1.0], [1.0]], fmt="D", color=INK, capsize=4, label="SF Fed letter: ~2 points higher (95%: 1-3)")
ax[0].legend(fontsize=8, frameon=False, loc="lower right"); ax[1].legend(fontsize=8, frameon=False, loc="upper left")
fig.suptitle("Did the Fed act too late? What earlier hikes would have done (this model, 90% range shaded; published estimate as diamond)",
             x=.01, ha="left", fontsize=12.5)
fig.tight_layout(rect=(0, 0, 1, .94)); fig.savefig(ROOT + "output/fig15_fed_late.png", dpi=150)
print("saved")
