"""Compare the recomputed split (replicate_sf_supply_demand.py) with the SF Fed's published file."""
import sys
import pandas as pd

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
sf = pd.read_excel(ROOT + "data/raw/sf_fed/supply-demand-pce-inflation.xlsx", sheet_name="Data")
sf.index = pd.PeriodIndex(sf.time_month.astype(str).str.strip().str.replace("m", "-"), freq="M").astype(str)
for lvl in sys.argv[1:] or ["4t"]:
    me = pd.read_csv(ROOT + f"output/sf_replication_monthly_L{lvl}.csv", index_col=0)
    print(f"\n== level {lvl}")
    for kind in ("headline", "core"):
        for g, sfcol in (("supply", "Supply-driven"), ("demand", "Demand-driven"), ("ambiguous", "Ambiguous")):
            a = sf[f"{sfcol} Inflation ({kind}, y/y)" if g != "ambiguous" else f"Ambiguous ({kind}, y/y)"]
            b = me[f"{g}_{kind}_yoy"]
            j = pd.concat([a, b], axis=1, keys=["sf", "me"]).dropna().loc["2000-01":]
            d = j.me - j.sf
            print(f"{kind:8} {g:9} corr {j.sf.corr(j.me):.3f}  mean abs gap {d.abs().mean():.2f} pts  "
                  f"2022-06: SF {j.sf.get('2022-06', float('nan')):.2f} vs ours {j.me.get('2022-06', float('nan')):.2f}")
