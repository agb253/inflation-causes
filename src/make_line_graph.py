import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
O = "output/"
pt = pd.read_csv(O + "decomp_point.csv", index_col=0, parse_dates=True)
arr = np.load(O + "draws.npy")  # (draw, quarter, component)
cols = [c for c in pt.columns if c != "actual_cpi"]
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
LAB = {"baseline_pre2020": "Pre-2020 baseline", "shortages": "Shortages", "energy": "Energy prices", "food": "Food prices",
       "labor_tightness": "Labor-market tightness", "productivity": "Productivity trend", "unexplained": "Unexplained by model"}
COL = {"baseline_pre2020": "#7d7c75", "shortages": "#2a78d6", "energy": "#eb6834", "food": "#1baf7a",
       "labor_tightness": "#eda100", "productivity": "#e87ba4", "unexplained": "#b9b8b0"}
ORDER = ["baseline_pre2020", "shortages", "energy", "food", "labor_tightness", "productivity", "unexplained"]
x = np.arange(len(pt))
lab = [f"{d.year}\nQ{(d.month-1)//3+1}" if d.month == 1 else f"Q{(d.month-1)//3+1}" for d in pt.index]
cum_act = pt.actual_cpi.cumsum() / 4
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2})

def panel(ax, getter, actual, ylabel, title, direct):
    for c in ORDER:
        i = cols.index(c); d = getter(arr[:, :, i]); p = getter(pt[c].values[None, :])[0]
        lo90, hi90, lo68, hi68 = [np.percentile(d, q, axis=0) for q in (5, 95, 16, 84)]
        ax.fill_between(x, lo90, hi90, color=COL[c], alpha=0.12, lw=0)
        ax.fill_between(x, lo68, hi68, color=COL[c], alpha=0.22, lw=0)
        ax.plot(x, p, color=COL[c], lw=2.2, ls="--" if c == "unexplained" else "-", marker="o", ms=4, mfc=SURF, mew=1.5, label=LAB[c], zorder=3)
    ax.plot(x, actual, color=INK, lw=3, marker="o", ms=5, mfc=SURF, mec=INK, mew=1.8, label="Actual CPI (BLS)", zorder=5)
    ax.axhline(0, color=INK2, lw=0.8); ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.set_ylabel(ylabel); ax.set_facecolor(SURF)
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.set_title(title, loc="left", fontsize=12.5, color=INK, fontweight="bold")
    ax.set_xticks(x); ax.set_xticklabels(lab, fontsize=9)

fig, (a1, a2) = plt.subplots(2, 1, figsize=(15, 13.5), facecolor=SURF)
panel(a1, lambda v: v, pt.actual_cpi.values, "Percentage points, annualized quarterly rate",
      "Quarterly: contribution of each cause to CPI inflation", None)
panel(a2, lambda v: np.cumsum(v, axis=-1) / 4, cum_act.values, "Log points of the price level since 2019Q4",
      "Cumulative: running total of each cause (the lines sum to the actual CPI line)", None)
h, l = a1.get_legend_handles_labels()
fig.legend(h, l, ncol=8, frameon=False, fontsize=9.5, loc="upper center", bbox_to_anchor=(0.5, 0.955))
fig.suptitle("Causes of U.S. CPI inflation, 2020Q1-2024Q4", x=0.01, ha="left", fontsize=16, fontweight="bold", color=INK, y=0.992)
fig.text(0.01, 0.962, "Lines = point estimates. Shading = 68% (darker) and 90% (lighter) ranges across 2,000 draws of the estimated model coefficients; coefficient uncertainty only, not model or data error.",
         fontsize=9.5, color=INK2)
fig.text(0.01, 0.006, "Model: Blanchard & Bernanke, NBER WP 31417, estimated by OLS from github.com/luigilor/bernanke-blanchard23 data; inputs checked against BLS and Cleveland Fed. Fiscal stimulus, Fed policy and corporate profits are not separately identified (see workbook, Category_map).",
         fontsize=7.5, color=INK2)
fig.tight_layout(rect=(0, 0.015, 1, 0.945)); fig.savefig(O + "fig3_line_graph_causes_cumulative.png", dpi=150, facecolor=SURF)
print("cumulative actual end:", round(cum_act.iloc[-1], 2), "| sum of cause lines end:", round(pt[cols].sum().sum() / 4, 2))
