"""Greedflation check: BEA NIPA Table 1.15, price per unit of real gross value added of
nonfinancial corporate business = unit labor cost + unit nonlabor cost + unit profits.
Read from BEA's quarterly flat file data/raw/bea/NipaDataQ.txt (downloaded 2026-10-17
from https://apps.bea.gov/national/Release/TXT/NipaDataQ.txt).
Contribution of each part to year-over-year price growth (pp) = (x_t - x_t-4) / price_t-4 * 100.
"Above normal" = minus its 2015-2019 average. This is an accounting split, not a cause:
it says how much of the price rise ended up as profit, not why.
Output: output/unit_profits_quarterly.csv
"""
import csv
import pandas as pd

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
S = {"A455RD": "price", "A460RD": "labor", "A467RD": "nonlabor", "A463RD": "profit"}
rows = []
with open(ROOT + "data/raw/bea/NipaDataQ.txt") as f:
    next(f)
    for code, per, val in csv.reader(f):
        if code in S:
            rows.append((S[code], per, float(val.replace(",", ""))))
d = pd.DataFrame(rows, columns=["s", "q", "v"]).pivot(index="q", columns="s", values="v")
d.index = pd.PeriodIndex(d.index, freq="Q")
gap = (d.price - d.labor - d.nonlabor - d.profit).abs().max()
print(f"identity check: max |price - labor - nonlabor - profit| = {gap:.4f}")
c = pd.DataFrame({k: 100 * (d[k] - d[k].shift(4)) / d.price.shift(4) for k in ("labor", "nonlabor", "profit")})
c["price_growth"] = 100 * (d.price / d.price.shift(4) - 1)
norm = c.loc["2015Q1":"2019Q4"].mean()
for k in ("labor", "nonlabor", "profit"):
    c[k + "_above_normal"] = c[k] - norm[k]
c["profit_share_of_price"] = 100 * d.profit / d.price
c = c.loc["2019Q1":"2024Q4"]
c.index = c.index.astype(str)
c.round(3).to_csv(ROOT + "output/unit_profits_quarterly.csv")
print("2015-19 normal:", norm.round(2).to_dict())
print(c.loc["2020Q1":].round(2).to_string())
