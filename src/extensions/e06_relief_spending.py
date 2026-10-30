"""Extension 6: what relief recipients actually spent, from card-spending data (Opportunity Insights Economic Tracker,
Affinity Solutions; spend_* = change in seasonally adjusted card spending relative to January 2020).

A. Third stimulus checks (American Rescue Plan, enacted March 11, 2021; IRS began issuing the third round in March 2021;
   Treasury: nearly $390 billion in 163.5 million payments through June 3, 2021). National daily spending, 7-day
   average: extra spending in the 6 weeks after March 15, 2021 above a linear trend fitted to January 4 - March 7,
   2021, for all cardholders and the lowest-income quartile (spend_all_q1).
   Rough dollar conversion: extra share x January-2020 monthly PCE (BEA DPCERC, SAAR / 12) x 1.4 months (6 weeks), over the $390 billion paid.
   This assumes card spending moves like all consumer spending; card data miss rent, utilities, health and much
   cash spending, so read it as an order of magnitude.
B. Early end of the $300/week federal unemployment supplement (25 states, June 12 - July 31, 2021; dates from the
   tracker's state policy file). Difference-in-differences on state weekly spending (7-day average of daily values):
   (ending states - other states) x (after the state's end date - April-May 2021), lowest-income quartile and all,
   weighted by 2019 population, errors clustered by state. Coombs et al. (AEA P&P 2022) find average cumulative UI
   benefits fell by $2,529 per recipient in the ending states.
Writes output/ext/e06_relief_spending.csv; log = stdout."""
import numpy as np
import pandas as pd
import statsmodels.api as sm
import sys
sys.path.insert(0, __file__.rsplit("/src/", 1)[0] + "/src")
import unified_data as U

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
OI = ROOT + "data/raw/ext/oi/"


def daily(path):
    d = pd.read_csv(path, na_values=".", low_memory=False)
    d["date"] = pd.to_datetime(d[["year", "month", "day"]])
    return d


rows = []
# ---- A
n = daily(OI + "Affinity_National_Daily.csv").set_index("date").sort_index()
pce_m = pd.read_csv(ROOT + "data/raw/bea/NipaDataM.txt", dtype=str)
pce_m.columns = [c.strip() for c in pce_m.columns]
p = pce_m[pce_m.iloc[:, 0].str.strip().str.replace('"', '') == "DPCERC"]
p = pd.Series(p.iloc[:, 2].str.replace(",", "").astype(float).values / 12 / 1000,      # $ billions per month (SAAR / 12)
              index=pd.PeriodIndex(p.iloc[:, 1].str.strip().str.replace("M", "-"), freq="M"))
for col in ["spend_all", "spend_all_q1"]:
    s = n[col].astype(float).rolling(7).mean()
    pre = s["2021-01-04":"2021-03-07"]
    t = (pre.index - pre.index[0]).days.values
    b = np.polyfit(t, pre.values, 1)
    post = s["2021-03-15":"2021-04-25"]
    tp = (post.index - pre.index[0]).days.values
    extra = float((post.values - np.polyval(b, tp)).mean())               # average extra (share of Jan-2020 level)
    rows.append(dict(item="A. third checks, extra spending vs trend, 6 weeks", series=col, estimate=extra, se=np.nan))
mpc_all = rows[0]["estimate"] * p[pd.Period("2020-01", "M")] * 1.4 / 390
rows.append(dict(item="A. implied share of the $390bn spent within 6 weeks (all cards, rough)", series="spend_all",
                 estimate=mpc_all, se=np.nan))

# ---- B
pm = pd.read_csv(OI + "Policy_Milestones_-_State.csv")
end = pm[pm.policy_description.str.contains("FPUC", na=False)]
end = end.assign(date=pd.to_datetime(end.date)).groupby("statefips").date.min()
st = daily(OI + "Affinity_-_State_-_Daily.csv")
geo = pd.read_csv(OI + "GeoIDs_-_State.csv").set_index("statefips")
for col in ["spend_all_q1", "spend_all"]:
    st[col] = pd.to_numeric(st[col], errors="coerce")
    w = st.set_index("date").groupby("statefips")[col].resample("W-SUN").mean().reset_index()
    w = w[(w.date >= "2021-04-01") & (w.date <= "2021-09-05")]
    w["treat"] = w.statefips.isin(end.index).astype(float)
    w["post"] = [float(d > end.get(f, pd.Timestamp("2021-06-12"))) if f in end.index else float(d > pd.Timestamp("2021-06-26"))
                 for f, d in zip(w.statefips, w.date)]
    w["tp"] = w.treat * w.post
    X = pd.concat([w[["tp"]], pd.get_dummies(w.statefips.astype(str), prefix="s", dtype=float),
                   pd.get_dummies(w.date.astype(str), prefix="t", drop_first=True, dtype=float)], axis=1)
    ok = w[col].notna()
    r = sm.WLS(w.loc[ok, col].values, X[ok].values, weights=w.loc[ok, "statefips"].map(geo.state_pop2019).values).fit(
        cov_type="cluster", cov_kwds={"groups": w.loc[ok, "statefips"].values})
    rows.append(dict(item="B. early UI end: spending change in ending states (share of Jan-2020 level)", series=col,
                     estimate=r.params[0], se=r.bse[0]))
out = pd.DataFrame(rows)
out.round(4).to_csv(ROOT + "output/ext/e06_relief_spending.csv", index=False)
pd.set_option("display.width", 200); pd.set_option("display.max_colwidth", 90)
print("ending states:", len(end)); print(out.round(3).to_string())
