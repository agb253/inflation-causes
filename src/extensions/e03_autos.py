"""Extension 3: cars, the most measurable supply-chain case (the chip shortage).
Motor-vehicle categories (new vehicles, used vehicles, parts; BEA Table 2.4.4U/2.4.5U lines 5, 12, 20) contribution to
headline PCE inflation, measured like the model's lines (year-over-year, sum of the four Q4 values 2021-24), as the
excess over each category's own 2015-19 average contribution; split by the Shapiro labels of this project's
replication (supply-driven / demand-driven / ambiguous, L4t). Production context: FRED IPG3361T3S (industrial
production, motor vehicles and parts), DAUTOSAAR (domestic auto sales, SAAR).
Writes output/ext/e03_autos.csv; log = stdout."""
import numpy as np
import pandas as pd

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
LINES = {5: "New motor vehicles", 12: "Used motor vehicles", 20: "Parts and accessories"}

lab = pd.read_csv(ROOT + "output/sf_replication_by_category_L4t.csv.gz")
lab = lab[lab.line.isin(LINES)]
lab["month"] = pd.PeriodIndex(lab.month, freq="M")
c = lab.pivot(index="month", columns="line", values="contrib")            # monthly pp contribution to headline PCE
l = lab.pivot(index="month", columns="line", values="label")


def q4sum(yoy):
    return sum(yoy[[pd.Period(f"{y}-{m:02d}", "M") for m in (10, 11, 12)]].mean() for y in range(2021, 2025))


rows = []
for line, name in LINES.items():
    yoy = c[line].rolling(12).sum()
    base = c[line]["2015-01":"2019-12"].sum() / 5                           # average yearly contribution, 2015-19
    r = dict(category=name, excess_2021_24=q4sum(yoy) - 4 * base)
    for g in ("supply", "demand", "ambiguous"):
        r[g] = q4sum(c[line].where(l[line] == g, 0.0).rolling(12).sum()) - 4 * c[line].where(l[line] == g, 0.0)["2015-01":"2019-12"].sum() / 5
    rows.append(r)
out = pd.DataFrame(rows).set_index("category")
out.loc["All motor vehicles"] = out.sum()
out.round(3).to_csv(ROOT + "output/ext/e03_autos.csv")
print(out.round(2).to_string())
ip = pd.read_csv(ROOT + "data/raw/ext/fred/IPG3361T3S.csv", index_col=0, parse_dates=True).iloc[:, 0]
print("motor-vehicle production index, 2019 avg = 100:",
      (100 * ip.resample("YE").mean() / ip["2019"].mean())["2019":"2024"].round(1).to_dict())
