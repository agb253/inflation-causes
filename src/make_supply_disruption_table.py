"""Supply-driven PCE inflation, 2019-2024: SF Fed published numbers next to our
recomputation from raw BEA data (replicate_sf_supply_demand.py, level 4, t-rule).
"Above normal" = minus the 2015-2019 average, i.e. the extra supply-driven inflation.
Output: output/supply_disruption_quarterly.csv
"""
import pandas as pd

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
sf = pd.read_excel(ROOT + "data/raw/sf_fed/supply-demand-pce-inflation.xlsx", sheet_name="Data")
sf.index = pd.PeriodIndex(sf.time_month.astype(str).str.strip().str.replace("m", "-"), freq="M")
me = pd.read_csv(ROOT + "output/sf_replication_monthly_L4t.csv", index_col=0)
me.index = pd.PeriodIndex(me.index, freq="M")
d = pd.DataFrame({
    "sf_supply_headline": sf["Supply-driven Inflation (headline, y/y)"],
    "sf_demand_headline": sf["Demand-driven Inflation (headline, y/y)"],
    "sf_ambiguous_headline": sf["Ambiguous (headline, y/y)"],
    "ours_supply_headline": me.supply_headline_yoy,
    "ours_supply_food_energy": me.supply_food_energy_yoy,
    "ours_total_pce": me.total_headline_yoy,
})
d["ours_supply_excl_food_energy"] = d.ours_supply_headline - d.ours_supply_food_energy
base = d.loc["2015-01":"2019-12"].mean()
for c in ("sf_supply_headline", "ours_supply_headline", "ours_supply_excl_food_energy", "ours_supply_food_energy"):
    d[c + "_above_normal"] = d[c] - base[c]
q = d.groupby(d.index.asfreq("Q")).last().loc["2019Q4":"2024Q4"]  # y/y as of the quarter's last month
q.index = q.index.astype(str)
q.round(2).to_csv(ROOT + "output/supply_disruption_quarterly.csv")
print("2015-2019 averages:", base.round(2).to_dict())
print(q[["sf_supply_headline", "sf_supply_headline_above_normal", "ours_supply_headline",
         "ours_supply_excl_food_energy_above_normal", "ours_supply_food_energy_above_normal", "ours_total_pce"]].round(2).to_string())
