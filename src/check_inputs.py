"""Compare the model's input series with official BLS CPI data fetched by api.bls.gov."""
import sys, json, glob, numpy as np, pandas as pd
sys.path.insert(0, "src"); import bb_model as m
rows = []
for f in glob.glob("data/raw/bls_api/cpi_*.json"):
    for s in json.load(open(f))["Results"]["series"]:
        for r in s["data"]:
            if r["period"].startswith("M") and r["value"] != "-":
                rows.append((s["seriesID"], pd.Timestamp(int(r["year"]), int(r["period"][1:]), 1), float(r["value"])))
b = pd.DataFrame(rows, columns=["s", "d", "v"]).pivot(index="d", columns="s", values="v").sort_index()
b.to_csv("data/raw/bls_api/cpi_monthly_combined.csv")
q = b.resample("QS").mean(); qe = b.resample("QS").last()
d = m.load(m.RAW + "data_us_new.csv")
for name, col, ser in [("all-items", "cpi", "SA0"), ("energy", "energy_cpi", "SA0E"), ("food", "food_cpi", "SAF1")]:
    print(f"\n{name}: dataset column '{col}' vs BLS")
    for v in ["CUSR0000" + ser, "CUUR0000" + ser]:
        for how, qq in [("qtr-avg", q), ("qtr-end-month", qe)]:
            x = pd.concat([d[col], qq[v]], axis=1, keys=["ds", "bls"]).dropna()
            diff = (x.ds - x.bls).abs()
            print(f"  {v} {how:14s} n={len(x)} mean|diff|={diff.mean():.4f} max|diff|={diff.max():.3f}  within 0.05: {(diff<0.05).mean():.0%}")
