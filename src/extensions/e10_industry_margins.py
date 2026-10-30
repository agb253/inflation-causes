"""Extension 10: profit margins industry by industry.
BEA input-output use tables (before redefinitions, producers' prices, summary level, 1997-2023; data/raw/ext/bea_io/
AllTablesIO.zip). For each industry: margin = gross operating surplus (V003) / total industry output, labor share =
compensation (V001) / output, input share = total intermediate / output. Change from the 2015-2019 average to 2021,
2022 and 2023, in points of output: a rise in the margin share of 1 point means prices rose 1% more than costs would
explain (holding the other shares' levels). Economy-wide line = output-weighted sum.
Note: gross operating surplus includes depreciation and the return on capital as well as profits, and is not only
'greed'; this is accounting, not a causal estimate.
Writes output/ext/e10_industry_margins.csv; log = stdout."""
import zipfile
import numpy as np
import pandas as pd

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
z = zipfile.ZipFile(ROOT + "data/raw/ext/bea_io/AllTablesIO.zip")
YEARS = list(range(2015, 2024))
rows = {}
with z.open("IOUse_Before_Redefinitions_PRO_1997-2023_Summary.xlsx") as fh:
    xl = pd.ExcelFile(fh)
    for y in YEARS:
        d = xl.parse(str(y), header=None)
        codes, names = d.iloc[5, 2:73].tolist(), d.iloc[6, 2:73].tolist()
        lab = d.iloc[:, 1].astype(str).str.strip()
        get = lambda key: pd.to_numeric(d.loc[lab == key].iloc[0, 2:73], errors="coerce").values
        V = {k: get(n) for k, n in [("comp", "Compensation of employees"), ("tax", "Taxes on production and imports, less subsidies"),
                                    ("gos", "Gross operating surplus"), ("inter", "Total Intermediate"), ("out", "Total Industry Output")]}
        for i, (c, n) in enumerate(zip(codes, names)):
            rows[(y, c)] = dict(year=y, code=c, industry=n, **{k: v[i] for k, v in V.items()})
df = pd.DataFrame(rows.values())
for k in ["gos", "comp", "inter"]:
    df[k + "_share"] = 100 * df[k] / df.out
base = df[df.year <= 2019].groupby("code")[["gos_share", "comp_share", "inter_share"]].mean()
out = df[df.year >= 2021].set_index(["code", "year"])[["industry", "out", "gos_share", "comp_share", "inter_share"]]
for k in ["gos_share", "comp_share", "inter_share"]:
    out["d_" + k] = out[k] - base[k].reindex(out.index.get_level_values(0)).values
tot = df.groupby("year")[["gos", "comp", "inter", "out"]].sum()
econ = pd.DataFrame({k + "_share": 100 * tot[k] / tot.out for k in ["gos", "comp", "inter"]})
econ_change = econ.loc[[2021, 2022, 2023]] - econ.loc[2015:2019].mean()
out.round(3).to_csv(ROOT + "output/ext/e10_industry_margins.csv")
econ_change.round(3).to_csv(ROOT + "output/ext/e10_economy_margins.csv")
print("Economy-wide change from 2015-19 average (points of output):"); print(econ_change.round(2).to_string())
for y in (2021, 2022):
    t = out.xs(y, level="year").sort_values("d_gos_share", ascending=False)
    t["weight"] = 100 * t.out / t.out.sum()
    print(f"\n{y}: largest margin rises (points of output; weight = % of total output)")
    print(t[["industry", "d_gos_share", "d_comp_share", "d_inter_share", "weight"]].head(8).round(2).to_string())
