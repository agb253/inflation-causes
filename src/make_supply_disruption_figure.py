"""fig10: supply-driven PCE inflation, SF Fed published vs our recomputation from BEA data."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
sf = pd.read_excel(ROOT + "data/raw/sf_fed/supply-demand-pce-inflation.xlsx", sheet_name="Data")
sf.index = pd.PeriodIndex(sf.time_month.astype(str).str.strip().str.replace("m", "-"), freq="M").to_timestamp()
me = pd.read_csv(ROOT + "output/sf_replication_monthly_L4t.csv", index_col=0)
me.index = pd.PeriodIndex(me.index, freq="M").to_timestamp()
a, b = "2018-01", "2024-12"
fig, ax = plt.subplots(figsize=(11, 6))
ax.plot(me.total_headline_yoy[a:b], color="black", lw=2.6, label="Total PCE inflation (BEA)")
ax.plot(sf["Supply-driven Inflation (headline, y/y)"][a:b], color="#c0392b", lw=2.4, label="Supply-driven, SF Fed published")
ax.plot(me.supply_headline_yoy[a:b], color="#c0392b", lw=1.8, ls="--", label="Supply-driven, our recomputation from BEA data")
ax.plot(sf["Demand-driven Inflation (headline, y/y)"][a:b], color="#2c6fbb", lw=2.4, label="Demand-driven, SF Fed published")
ax.plot(me.demand_headline_yoy[a:b], color="#2c6fbb", lw=1.8, ls="--", label="Demand-driven, our recomputation from BEA data")
ax.axhline(0, color="#555", lw=.8)
ax.set_ylabel("Percentage points of year-over-year PCE inflation")
ax.set_title("How much of inflation was supply-driven vs demand-driven (PCE, year over year)")
ax.legend(loc="upper left", fontsize=9, frameon=False)
fig.text(.01, .01, "Method: Shapiro (FRBSF WP 2020-29, eqs. 20-22). Data: BEA Tables 2.4.3U, 2.4.4U, 2.4.5U. "
         "Supply-driven = price and quantity surprises in opposite directions. Includes energy/war shocks.", fontsize=8)
fig.tight_layout(rect=(0, .03, 1, 1))
fig.savefig(ROOT + "output/fig10_supply_vs_demand_driven.png", dpi=150)
print("saved")
