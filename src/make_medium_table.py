"""Table image for the Medium version (docs/medium_table.png): 2021-24 totals from the article's chart table."""
import pathlib; ROOT = str(pathlib.Path(__file__).resolve().parent.parent)
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
rows = [("Pre-existing inflation (where end-2019 trends led)†", "+8.2", "+6.1 to +8.2†"),
        ("COVID supply chains*", "+4.2", "+2.5 to +9.3"), ("Worker shortage", "+2.5", "+1.4 to +3.7"),
        ("Relief paid under Biden (from Mar 2021)", "+2.1", "+1.2 to +4.6"), ("Relief paid under Trump (before Mar 2021)", "+1.7", "+1.1 to +4.4"),
        ("War in Ukraine (energy & food)", "+1.5", "+0.2 to +2.2"), ("Pent-up demand", "+1.2", "+0.7 to +1.8"),
        ("Fed, net (2020–21 cuts +0.8, 2022–23 hikes −0.4)", "+0.4", "0.0 to +1.5"),
        ("Profit margins (“greedflation”)*", "0.0 to +0.6", "−0.2 to +0.1 for the 0.0"),
        ("COVID shutdown drag", "−4.3", "−10.6 to −1.9"),
        ("Other & not explained", "−0.2", "leftover, no range"), ("Actual inflation, 2021–24 added up", "17.3", "measured")]
NOTE = ("* Profit's share of corporate prices rose from about 13% to 17–18% in 2021 and stayed there. Part of the supply-chain\n"
        "   line reached prices through those higher margins. 0.0 counts only margin rises that shortages and demand don't\n"
        "   explain; +0.6 counts every margin rise. Rows add up to actual inflation using 0.0.\n"
        "† Scenarios, not a 90% range: 6.1 if inflation had stayed at its 2010–19 average (1.5% a year), 6.8 at end-2019\n"
        "   expectations (1.7%), 8.2 from the model. A lower value adds the difference to 'other & not explained'.")
n = len(rows); H = 0.36 * n + 2.5
fig = plt.figure(figsize=(8, H), dpi=200); ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off")
y = lambda i: 1 - (0.85 + 0.36 * i) / H
ax.text(0.03, 1 - 0.35 / H, "What added to US inflation, 2021–2024", fontsize=13, weight="bold", va="center")
for x, s, ha in [(0.03, "Cause", "left"), (0.66, "Points", "right"), (0.71, "90% range", "left")]:
    ax.text(x, y(0), s, weight="bold", fontsize=10.5, va="center", ha=ha)
for i, (a, b, c) in enumerate(rows, 1):
    w = "bold" if i == n else "normal"; it = "italic" if c in ("leftover, no range", "measured") else "normal"
    ax.text(0.03, y(i), a, fontsize=10.5, va="center", weight=w)
    ax.text(0.66, y(i), b, fontsize=10.5, va="center", ha="right", weight=w)
    ax.text(0.71, y(i), c, fontsize=9.5, va="center", color="#444", style=it)
    ax.plot([0.03, 0.97], [y(i) + 0.18 / H] * 2, color="#ddd", lw=0.8)
ax.text(0.03, 1.0 / H, NOTE, fontsize=7.5, color="#333", va="center")
ax.text(0.03, 0.22 / H, "PCE price index, four yearly rates added up. Code and data: github.com/agb253/inflation-causes", fontsize=7.5, color="#555", va="center")
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
plt.savefig(ROOT + "/docs/medium_table.png", facecolor="white")
