"""Extension 7: the cross-country relief comparison on quarterly data, timed like the model's lines.
excess_i = year-over-year core CPI inflation (OECD, all items less food and energy, quarterly) in 2021Q4 and 2022Q4,
added up, minus 2 x the 2015-2019 average; regressed on IMF pandemic fiscal measures (% of GDP), advanced economies,
HC1 errors. Also 2021Q4 alone (the timing of Jorda et al.). US effect = slope x US relief. The model's relief lines are
measured the same way (sum of 2021Q4 and 2022Q4 year-over-year contributions), so the two can be compared directly.
Writes output/ext/e07_cross_country_quarterly.csv; log = stdout."""
import sys
sys.path.insert(0, __file__.rsplit("/src/", 1)[0] + "/src")
import numpy as np
import pandas as pd
import statsmodels.api as sm
import cross_country_relief as CC

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
o = pd.read_csv(ROOT + "data/raw/oecd/cpi_quarterly.csv")
core = o[o.EXPENDITURE == "_TXCP01_NRG"].pivot_table(index="REF_AREA", columns="TIME_PERIOD", values="OBS_VALUE")
F = CC.fiscal()
base = core[[c for c in core if "2015" <= c[:4] <= "2019"]].mean(axis=1)
rows = []
for name, qs, ctry in [("2021Q4 + 2022Q4, advanced", ["2021-Q4", "2022-Q4"], CC.ADVANCED),
                       ("2021Q4 only, advanced", ["2021-Q4"], CC.ADVANCED),
                       ("2021Q4 + 2022Q4, + 4 emerging", ["2021-Q4", "2022-Q4"], CC.ADVANCED + ["POL", "CHL", "COL", "MEX"])]:
    y = (core[qs].sum(axis=1) - len(qs) * base).reindex(ctry)
    X = sm.add_constant(F.reindex(ctry).rename("fiscal"))
    ok = y.notna() & X.notna().all(axis=1)
    r = sm.OLS(y[ok], X[ok]).fit(cov_type="HC1")
    rows.append(dict(spec=name, n=int(ok.sum()), b=r.params.fiscal, se=r.bse.fiscal, r2=r.rsquared,
                     us_effect=r.params.fiscal * F["USA"], us_effect_se=r.bse.fiscal * F["USA"]))
q = pd.read_csv(ROOT + "output/unified_causes_quarterly.csv", index_col=0)
model = q.loc[["2021Q4", "2022Q4"], ["trump", "biden"]].sum().sum()
out = pd.DataFrame(rows).set_index("spec")
out["model_relief_same_metric"] = [model, q.loc["2021Q4", ["trump", "biden"]].sum(), model]
out.round(3).to_csv(ROOT + "output/ext/e07_cross_country_quarterly.csv")
pd.set_option("display.width", 200)
print(out.round(2).to_string())
