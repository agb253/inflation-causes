"""Extra shipping cost on US imports, 2020-2024, as a share of consumer spending.

Input: data/raw/census/import_charges_monthly.csv (src/fetch_census_freight.py),
       data/raw/fred/PCE.csv (nominal PCE, SAAR $bn).
Extra cost = charges - (2019 charges/value rate) * customs value, so it measures
the higher freight rate, not the larger volume of imports.
Divided by PCE it is the most this could have raised consumer prices: it assumes
every extra dollar was passed on, with no markup on top.
"""
import pandas as pd

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
d = pd.read_csv(ROOT + "data/raw/census/import_charges_monthly.csv")
d["q"] = pd.PeriodIndex(d.month, freq="M").asfreq("Q")
q = d.groupby("q")[["customs_value_usd", "charges_usd"]].sum() / 1e9
p = pd.read_csv(ROOT + "data/raw/fred/PCE.csv", parse_dates=[0])
pce = p.groupby(p.observation_date.dt.to_period("Q")).PCE.mean() / 4  # quarterly $bn

y19 = q.loc["2019Q1":"2019Q4"].sum()
r19 = y19.charges_usd / y19.customs_value_usd
q["charge_rate_pct"] = 100 * q.charges_usd / q.customs_value_usd
q["extra_bn"] = q.charges_usd - r19 * q.customs_value_usd
q["pce_bn"] = pce.reindex(q.index)
q["max_price_level_pct"] = 100 * q.extra_bn / q.pce_bn
# contribution to year-over-year inflation = change in the price-level effect over 4 quarters
q["max_yoy_inflation_pts"] = q.max_price_level_pct.diff(4)
q.index = q.index.astype(str)
q.round(3).to_csv(ROOT + "output/shipping_cost_quarterly.csv")

a = q.groupby(q.index.str[:4])[["customs_value_usd", "charges_usd", "extra_bn", "pce_bn"]].sum()
a["max_price_level_pct"] = 100 * a.extra_bn / a.pce_bn
a["max_yoy_inflation_pts"] = a.max_price_level_pct.diff()
a.round(3).to_csv(ROOT + "output/shipping_cost_annual.csv")
print(f"2019 charge rate {100 * r19:.2f}% of customs value")
print(a.round(2).to_string())
print(q.loc["2020Q1":, ["charge_rate_pct", "extra_bn", "max_price_level_pct", "max_yoy_inflation_pts"]].round(2).to_string())
