"""fig12: causes of PCE inflation from the one unified model (src/unified_model.py), one chart.
Table: output/unified_causes_quarterly.csv
With argument "best": fig16, the same lines with 90% ranges from the best estimate (extension 16, wage data + category
panel + cross-country, output/ext/e16_quarterly.csv) instead of the model's own redraws."""
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
o = pd.read_csv(ROOT + "output/unified_causes_quarterly.csv", index_col=0)
o["pre_existing"] = o.baseline + o.fed_pre2020          # pre-2020 Fed surprises are part of the starting point
BEST = len(sys.argv) > 1 and sys.argv[1] == "best"
BVAR = "W+P + X"
if BEST:
    e = pd.read_csv(ROOT + "output/ext/e16_quarterly.csv")
    e = e[e.variant == BVAR].pivot(index="quarter", columns="cause")
    for k in ["trump", "biden", "energy_war", "shortage", "worker_shortage", "pentup", "covid_other", "greed"]:
        o[k + "_lo"], o[k + "_hi"] = e.p5[k].reindex(o.index), e.p95[k].reindex(o.index)
q = list(o.index); x = np.arange(len(q))
lab = [f"Q1\n{k[:4]}" if k.endswith("Q1") else f"Q{k[-1]}" for k in q]
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
# reference categorical palette, one hue per cause in fixed slot order; every line also gets its own marker shape
LINES = [  # key, label, color, linestyle, marker, band
    ("trump", "Relief paid under Trump (CARES Act, Dec-2020 act; payments before Mar 2021)", "#e34948", "-", "s", True),
    ("biden", "Relief paid under Biden (payments from Mar 2021: American Rescue Plan, plus later payments under Trump-signed laws)", "#2a78d6", "-", "o", True),
    ("fed_easing", "Fed 2020-21 rate cuts + QE (money injection)", "#1baf7a", "-", "^", False),
    ("fed_hikes", "Fed 2022-23 rate hikes", "#6250d6", "-", "v", False),
    ("energy_war", "War in Ukraine (energy & food spike and fall-back 2022Q1-2023Q1, and its lingering effect)", "#eb6834", "-", "D", True),
    ("shortage", "COVID supply chains", "#eda100", "-", "P", True),
    ("worker_shortage", "Worker shortage", "#e87ba4", "-", "X", BEST),
    ("greed", "Greedflation (margin rises beyond costs & shortages)", "#008300", "-", "*", True),
    ("pentup", "Pent-up demand (spending money that couldn't be spent in lockdowns; relief money excluded)", "#8a5a2b", "-", "h", True),
    ("covid_other", "COVID shutdown & reopening (estimated from lockdown stringency, incl. the 2020-21 oil & food crash/rebound)",
     INK, (0, (5, 2)), None, BEST),
    ("pre_existing", "Pre-existing inflation (end-2019, incl. earlier Fed policy)", MUTED, (0, (2, 2)), None, False),
    ("other_unexplained", "Other & not explained (energy & food shocks after 2023Q1 such as OPEC+ cuts, bird flu, drought; unemployment the causes miss; model error)", "#8d8b86", (0, (1, 1.5)), None, False),
]

fig, a = plt.subplots(figsize=(16, 9))
a.grid(axis="y", color=GRID, lw=.8); a.set_axisbelow(True)
for sp in ("top", "right"): a.spines[sp].set_visible(False)
a.axhline(0, color=MUTED, lw=.8)
for yr in range(1, 5): a.axvline(4 * yr - .5, color=GRID, lw=.8)

h = {}
h["actual"] = a.plot(x, o.actual_pce_yoy, color=INK, lw=3, marker="o", ms=5, zorder=6)[0]
h["sum"] = a.plot(x, o.model_total, color="#b9b7b1", lw=8, alpha=.85, zorder=2)[0]
for k, name, col, ls, mk, band in LINES:
    if band and k + "_lo" in o:
        a.fill_between(x, o[k + "_lo"], o[k + "_hi"], color=col, alpha=.12 if BEST else .07, lw=0, zorder=1)
    h[k] = a.plot(x, o[k], color=col, lw=2, ls=ls, marker=mk, ms=6.5 if mk != "*" else 9,
                  markeredgecolor="white", markeredgewidth=.7, zorder=4)[0]
a.set_ylim(-4.2 if BEST else -3, 7.6); a.set_xlim(-.5, len(q) - .5)
a.set_xticks(x); a.set_xticklabels(lab, fontsize=9.5)
a.set_ylabel("Percentage points of year-over-year PCE inflation", color=MUTED)
a.set_title("What caused US inflation, 2020-2024: each cause, and the part the model cannot explain",
            loc="left", fontsize=14, color=INK)
# one legend, right of the plot; causes listed from largest to smallest at the 2022Q2 peak
order = sorted(LINES, key=lambda r: -o.loc["2022Q2", r[0]])
hs = [h["actual"], h["sum"]] + [h[r[0]] for r in order]
ls_ = ["Actual PCE inflation (BEA, % change from a year earlier)", "Model estimate: the model run on all the actual data (its gap to actual inflation is part of 'other & not explained')"] + \
      [f"{r[1]}  [{o.loc['2022Q2', r[0]]:+.1f}]" for r in order]
import textwrap
ls_ = ["\n".join(textwrap.wrap(t, 46)) for t in ls_]
a.legend(hs, ls_, loc="upper left", bbox_to_anchor=(1.01, 1.0), fontsize=9, frameon=False, labelspacing=.9,
         title="[ ] = points at the 2022Q2 peak", title_fontsize=8.5, alignment="left", handlelength=3.2)
rg = lambda k, qq: f"{o.loc[qq, k + '_lo']:+.1f} to {o.loc[qq, k + '_hi']:+.1f}"
fig.text(.01, .005,
         "One model: relief payments (BEA) x CBO multipliers, and pent-up spending (BEA real PCE below trend) -> GDP -> unemployment (Okun); Fed rate path (SF Fed proxy funds rate, "
         "includes QE) -> unemployment (proxy SVAR);\nlockdown stringency (Oxford tracker) -> unemployment, estimated; unemployment -> job openings per unemployed; then the "
         "Bernanke-Blanchard wage-price model on PCE. Each line = model inflation with the cause minus without it.\n"
         f"The lines, including 'other & not explained', add up to actual inflation every quarter. The model itself misses actual inflation by up to {o.unexplained.abs().max():.1f} points; "
         "that miss is inside 'other & not explained'. " + ("Shading: 90% range of the best estimate\n(1,000 model runs weighted by 2020-24 wage growth, the category-price panel "
         "and other countries' relief; extension 16). " if BEST else "Shading: 90% range over 1,000 redraws.\n") +
         (f"\nLines are the model's point estimates, so they add up; a line can sit off-centre in its range. Not shaded: the Fed lines (only their net total was weighted).  " if BEST else
          f"Not shaded (ranges too wide to draw): Fed cuts+QE, 2023Q2 {rg('fed_easing', '2023Q2')}; Fed hikes, 2024Q4 {rg('fed_hikes', '2024Q4')}; COVID, 2022Q2 {rg('covid_other', '2022Q2')}.  ") +
         "Every quarter, equations, sources: output/TABLE_UNIFIED.md",
         fontsize=8.3, color=MUTED, va="bottom")
fig.tight_layout(rect=(0, .115 if BEST else .085, 1, 1))
fig.savefig(ROOT + ("output/fig16_best_ranges.png" if BEST else "output/fig12_unified_causes.png"), dpi=150)
print("saved")
