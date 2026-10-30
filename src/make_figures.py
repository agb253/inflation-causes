import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
O = "output/"
pt = pd.read_csv(O + "decomp_point.csv", index_col=0, parse_dates=True)
B = {k: pd.read_csv(O + f"decomp_{k}.csv", index_col=0, parse_dates=True) for k in ["lo90", "hi90", "lo68", "hi68"]}
cum = pd.read_csv(O + "cumulative_2020q1_2024q4.csv", index_col=0)
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
LAB = {"baseline_pre2020": "Pre-2020 baseline (trend + expectations)", "shortages": "Shortages (supply bottlenecks / demand shift)",
       "energy": "Energy prices", "food": "Food prices", "labor_tightness": "Labor-market tightness (vacancies/unemployed)",
       "productivity": "Productivity trend", "unexplained": "Unexplained by model"}
COL = {"baseline_pre2020": "#d6d5cf", "shortages": "#2a78d6", "energy": "#eb6834", "food": "#1baf7a",
       "labor_tightness": "#eda100", "productivity": "#e87ba4", "unexplained": "#8a8983"}
ORDER = ["baseline_pre2020", "shortages", "energy", "food", "labor_tightness", "productivity", "unexplained"]
lab = [f"{d.year}\nQ{(d.month-1)//3+1}" if (d.month == 1) else f"Q{(d.month-1)//3+1}" for d in pt.index]
x = np.arange(len(pt))
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": GRID, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2})

# ---- Figure 1: stacked decomposition
fig, ax = plt.subplots(figsize=(15, 7.5), facecolor=SURF); ax.set_facecolor(SURF)
pos = np.zeros(len(pt)); neg = np.zeros(len(pt))
for c in ORDER:
    v = pt[c].values; bot = np.where(v >= 0, pos, neg)
    ax.bar(x, v, bottom=bot, width=0.78, color=COL[c], edgecolor=SURF, linewidth=1.5, label=LAB[c], hatch="//" if c == "unexplained" else None)
    pos += np.where(v >= 0, v, 0); neg += np.where(v < 0, v, 0)
ax.plot(x, pt.actual_cpi, color=INK, marker="o", ms=6, lw=2, mfc=SURF, mec=INK, mew=2, label="Actual CPI inflation (annualized quarterly)", zorder=5)
ax.axhline(0, color=INK2, lw=0.8)
ax.set_xticks(x); ax.set_xticklabels(lab, fontsize=9); ax.set_ylabel("Percentage points of annualized quarterly CPI inflation")
ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
for s in ["top", "right"]: ax.spines[s].set_visible(False)
ax.set_title("What drove U.S. CPI inflation each quarter, 2020Q1-2024Q4", loc="left", fontsize=15, color=INK, fontweight="bold", pad=34)
ax.text(0, 1.035, "Bernanke-Blanchard (2025) model, coefficients estimated by OLS; components sum exactly to actual inflation. Error bars: see Figure 2.",
        transform=ax.transAxes, fontsize=10, color=INK2)
ax.legend(ncol=4, frameon=False, fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.10))
fig.text(0.01, 0.005, "Sources: BLS CPI/ECI/JOLTS; Cleveland Fed expectations; Google Trends 'shortage'; model: Blanchard & Bernanke, NBER WP 31417; replication data/code: github.com/luigilor/bernanke-blanchard23. "
         "Reproduce: python src/run_all.py", fontsize=7.5, color=INK2)
fig.tight_layout(rect=(0, 0.03, 1, 1)); fig.savefig(O + "fig1_quarterly_decomposition.png", dpi=170, facecolor=SURF); plt.close(fig)

# ---- Figure 2: per-cause panels with 68% (thick) and 90% (thin) bands
fig, axs = plt.subplots(4, 2, figsize=(15, 15), facecolor=SURF)
axs = axs.ravel()
for ax, c in zip(axs, ORDER):
    ax.set_facecolor(SURF)
    ax.vlines(x, B["lo90"][c], B["hi90"][c], color=COL[c] if c != "baseline_pre2020" else "#a9a8a0", lw=1.2, zorder=2)
    ax.vlines(x, B["lo68"][c], B["hi68"][c], color=COL[c] if c != "baseline_pre2020" else "#a9a8a0", lw=4.5, zorder=3)
    ax.plot(x, pt[c], "o", ms=6, mfc=SURF, mec=INK, mew=1.6, zorder=4)
    ax.axhline(0, color=INK2, lw=0.8); ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)
    ax.set_title(LAB[c], loc="left", fontsize=11, color=INK, fontweight="bold")
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.set_ylabel("pp, annualized", fontsize=8)
    ax.set_xticks(x); ax.set_xticklabels(lab, fontsize=7.5)
ax = axs[7]; ax.set_facecolor(SURF)
yy = np.arange(len(ORDER))[::-1]
for yv, c in zip(yy, ORDER):
    r = cum.loc[c]
    ax.hlines(yv, r.lo90, r.hi90, color=COL[c] if c != "baseline_pre2020" else "#a9a8a0", lw=1.4)
    ax.hlines(yv, r.lo68, r.hi68, color=COL[c] if c != "baseline_pre2020" else "#a9a8a0", lw=5)
    ax.plot(r.point, yv, "o", ms=6, mfc=SURF, mec=INK, mew=1.6)
    ax.text(r.hi90 + 0.3, yv, f"{r.point:.1f}  [{r.lo90:.1f}, {r.hi90:.1f}]", va="center", fontsize=8, color=INK2)
ax.set_yticks(yy); ax.set_yticklabels([LAB[c].split(" (")[0] for c in ORDER], fontsize=8)
ax.set_xlabel("log points of the price level, 2020Q1-2024Q4", fontsize=8); ax.tick_params(axis="x", labelsize=8)
ax.axvline(0, color=INK2, lw=0.8); ax.grid(axis="x", color=GRID, lw=0.8); ax.set_axisbelow(True)
ax.set_xlim(None, cum.hi90.max() + 6)
ax.set_title(f"Cumulative 2020Q1-2024Q4 (log points; actual = {cum.actual.iloc[0]:.1f})", loc="left", fontsize=11, color=INK, fontweight="bold")
for s in ["top", "right"]: ax.spines[s].set_visible(False)
fig.suptitle("Each cause by quarter, with uncertainty", x=0.01, ha="left", fontsize=15, fontweight="bold", color=INK, y=0.995)
fig.text(0.01, 0.962, "Dot = point estimate. Thick bar = 68% range, thin bar = 90% range across 2,000 draws of the estimated coefficients. Ranges reflect coefficient uncertainty only, not model or data error.",
         fontsize=9.5, color=INK2)
fig.tight_layout(rect=(0, 0, 1, 0.955)); fig.savefig(O + "fig2_cause_panels_with_error_bars.png", dpi=150, facecolor=SURF); plt.close(fig)
print("ok")
