"""Images for the web article: peak bar chart and every-quarter table (Medium can't show HTML tables).
Usage: python src/make_web_images.py OUTDIR"""
import sys
import shutil
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image

W = sys.argv[1].rstrip("/") + "/"
o = pd.read_csv("output/unified_causes_quarterly.csv", index_col=0)
o["pre_existing"] = o.baseline + o.fed_pre2020
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#e4e3df"
C = [("pre_existing", "Pre-existing inflation (end-2019)", MUTED), ("shortage", "COVID supply chains", "#eda100"),
     ("energy_war", "War in Ukraine", "#eb6834"), ("worker_shortage", "Worker shortage", "#e87ba4"),
     ("biden", "Relief signed by Biden", "#2a78d6"), ("other_unexplained", "Other & not explained by the model", "#8d8b86"),
     ("fed_easing", "Fed 2020-21 rate cuts + QE", "#1baf7a"), ("trump", "Relief signed by Trump", "#e34948"),
     ("greed", "Greedflation", "#008300"), ("fed_hikes", "Fed 2022-23 rate hikes", "#6250d6"),
     ("covid_other", "COVID & everything else that moved jobs (leftover)", "#3a3936")]
r = sorted([(o.loc["2022Q2", k], n, c) for k, n, c in C], key=lambda t: t[0])
fig, a = plt.subplots(figsize=(10, 6.4))
y = list(range(len(r)))
a.barh(y, [t[0] for t in r], color=[t[2] for t in r], height=.62)
for i, (v, n, c) in enumerate(r):
    a.text(v + (.06 if v >= 0 else -.08), i, f"{v:+.2f}", va="center", ha="left" if v >= 0 else "right", fontsize=10, color=INK)
a.set_yticks(y); a.set_yticklabels([t[1] for t in r], fontsize=10.5, color=INK); a.tick_params(axis="y", length=0)
a.axvline(0, color=MUTED, lw=.8); a.grid(axis="x", color=GRID); a.set_axisbelow(True)
for sp in ("top", "right", "left"): a.spines[sp].set_visible(False)
a.set_xlim(-2.6, 2.6); a.set_xlabel("Percentage points of year-over-year PCE inflation", color=MUTED)
fig.suptitle(f"At the peak (2022Q2), PCE inflation was {o.loc['2022Q2', 'actual_pce_yoy']:.2f}%. "
             f"The causes account for {o.loc['2022Q2', 'model_total']:.2f}; 'other & not explained' is the rest.",
             x=.01, ha="left", fontsize=12, color=INK)
fig.tight_layout(); fig.savefig(W + "peak.png", dpi=150)

cols = [("trump", "Trump\nrelief"), ("biden", "Biden\nrelief"), ("fed_easing", "Fed cuts\n+ QE"), ("fed_hikes", "Fed\nhikes"),
        ("energy_war", "War in\nUkraine"), ("shortage", "Supply\nchains"), ("worker_shortage", "Worker\nshortage"),
        ("greed", "Greed-\nflation"), ("covid_other", "COVID &\nall else\n(leftover)"), ("pre_existing", "Pre-\nexisting"),
        ("model_total", "Model\nestimate\n(sum)"), ("other_unexplained", "Other &\nnot\nexplained"), ("actual_pce_yoy", "Actual\nPCE\ninflation")]
cell = [[f"{o.loc[q, k]:.2f}" for k, _ in cols] for q in o.index]
fig, a = plt.subplots(figsize=(14, 8.6)); a.axis("off")
t = a.table(cellText=cell, rowLabels=list(o.index), colLabels=[c[1] for c in cols], loc="upper center", cellLoc="right")
t.auto_set_font_size(False); t.set_fontsize(9.5); t.scale(1, 1.32)
for (i, j), c in t.get_celld().items():
    c.set_edgecolor(GRID)
    if i == 0:
        c.set_height(c.get_height() * 2.6); c.set_text_props(color=INK, weight="bold", fontsize=8.8, ha="center"); c.set_facecolor("#f4f3f0")
    elif j in (10, 12):
        c.set_text_props(weight="bold")
    if i > 0 and i % 2 == 0: c.set_facecolor("#faf9f7")
a.set_title("Contribution of each cause, every quarter (percentage points of PCE inflation, % change from a year earlier).\n"
            "Model estimate = sum of the causes. Model estimate + other & not explained = actual.", loc="left", fontsize=11, color=INK)
fig.tight_layout(); p = W + "quarterly_table.png"; fig.savefig(p, dpi=150, bbox_inches="tight")
im = Image.open(p).convert("RGB"); arr = np.asarray(im); last = np.where((arr < 245).any(axis=(1, 2)))[0].max()
im.crop((0, 0, im.width, last + 20)).save(p)
shutil.copy("output/fig12_unified_causes.png", W + "causes_chart.png")
print("ok")
