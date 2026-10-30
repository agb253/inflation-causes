"""Causes of PCE inflation by quarter, 2020-2024, built so the causes cannot double count.

PCE inflation is, by BEA's own construction, the spending-weighted sum of the price
changes of its categories. replicate_sf_supply_demand.py labels every category in
every month as supply-driven, demand-driven or ambiguous (SF Fed method, Shapiro
WP 2020-29). Here every category-month goes to exactly one cause, so the causes add
up to actual PCE inflation by construction:

  war            food & energy, supply-driven, Jan 2022 - Mar 2023 (the spike and its
                 fall back; window from fig9: energy CPI / ECI rose from 0 at 2021Q4
                 to +17.6% at 2022Q2 and was back to -1.5% by 2023Q1)
  energy_other   food & energy, supply-driven, outside that window (COVID oil crash
                 and rebound, later moves)
  goods_supply   goods other than food & energy, supply-driven (COVID supply chains)
  svc_supply     services other than housing & energy, supply-driven (incl. staff shortages)
  housing        rent and owner-equivalent rent, every label (pre-existing housing shortage)
  demand         demand-driven, everything except housing
  ambiguous      price or quantity surprise too small to label
Each cause is shown minus its own 2015-2019 average; those averages together are
"pre-existing inflation". Year over year = 12-month sum of monthly contributions;
quarterly value = mean of the quarter's three monthly y/y readings.
Bands: min-max across four variants of the labeling (category level 4 or 5; two
readings of the paper's "ambiguous" rule).
Output: output/pce_causes_quarterly.csv
"""
import numpy as np
import pandas as pd

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
VARIANTS = ["4t", "4pct", "5t", "5pct"]
MAIN = "4t"
WAR = ("2022-01", "2023-03")
HOUSING_LINES = range(153, 165)   # "Housing" and its sub-lines in Table 2.4.5U (line 153-164)
CAUSES = ["war", "energy_other", "goods_supply", "svc_supply", "housing", "demand", "ambiguous"]


def by_cause(v):
    cats = pd.read_csv(ROOT + f"output/sf_replication_categories_L{v[0]}.csv", index_col=0)
    d = pd.read_csv(ROOT + f"output/sf_replication_by_category_L{v}.csv.gz")
    d = d.join(cats[["food_energy"]], on="line")
    m = d.month
    fe, sup = d.food_energy, d.label == "supply"
    housing = d.line.isin(HOUSING_LINES)
    goods = d.line < 151
    inwar = (m >= WAR[0]) & (m <= WAR[1])
    d["cause"] = np.select(
        [housing, fe & sup & inwar, fe & sup, goods & sup, sup, d.label == "demand", d.label == "ambiguous"],
        ["housing", "war", "energy_other", "goods_supply", "svc_supply", "demand", "ambiguous"], "unlabeled")
    mm = d.pivot_table(index="month", columns="cause", values="contrib", aggfunc="sum").fillna(0)
    yoy = mm.rolling(12).sum()
    yoy.index = pd.PeriodIndex(yoy.index, freq="M")
    return yoy


yo = {v: by_cause(v) for v in VARIANTS}
out = {}
for v, y in yo.items():
    for c in CAUSES + ["unlabeled"]:
        if c not in y: y[c] = 0.0
    norm = y.loc["2015-01":"2019-12"].mean()
    ex = y[CAUSES] - norm[CAUSES]
    ex["baseline"] = norm[CAUSES].sum()
    ex["unlabeled"] = y["unlabeled"]
    ex["total"] = y[CAUSES + ["unlabeled"]].sum(axis=1)
    out[v] = ex.groupby(ex.index.asfreq("Q")).mean().loc["2020Q1":"2024Q4"]

main = out[MAIN].copy()
stack = pd.concat(out, axis=1)
for c in CAUSES:
    vals = stack.xs(c, axis=1, level=1)
    main[c + "_lo"], main[c + "_hi"] = vals.min(axis=1), vals.max(axis=1)

# official PCE price index y/y, quarterly mean, for the check
pi = pd.read_csv(ROOT + "data/raw/fred/PCEPI.csv", parse_dates=[0], index_col=0).iloc[:, 0]
pi.index = pi.index.to_period("M")
off = (100 * np.log(pi).diff(12))
main["official_pce_yoy"] = off.groupby(off.index.asfreq("Q")).mean().reindex(main.index)
main.index = main.index.astype(str)
main.round(3).to_csv(ROOT + "output/pce_causes_quarterly.csv")
print("2015-19 normal (pre-existing):", round(out[MAIN].baseline.iloc[0], 2))
print(main[CAUSES + ["baseline", "unlabeled", "total", "official_pce_yoy"]].round(2).to_string())
