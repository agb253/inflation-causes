"""Extension 5: evidence from differences between US states.

A. Lockdowns and unemployment. du_st = unemployment rate minus its 2019Q4 value (FRED {ST}UR, quarterly mean);
   s_st = Oxford tracker state stringency index / 100 (OxCGRT compact subnational, StringencyIndex_Average, state-wide
   rows, quarterly mean). du_st = d_t + g0 s_st + g1 s_s,t-1 + e_st, 2020Q1-2022Q4, weighted by 2019 population,
   errors clustered by state. The quarter effects d_t absorb everything national (relief, the Fed, pent-up demand),
   so g0, g1 come only from states that locked down harder or longer. Compared with the model's national fit
   (unified_model.covid_fit), which cannot separate lockdowns from anything else that moved unemployment in 2020-22.
B. Wage curve. w_st = 4-quarter growth of average hourly earnings, total private (FRED SMU{fips}000000500000003, from
   2007); w_st = a_s + d_t + c1 u_s,t-1 + c2 max(u_s,t-1 - 6, 0) + e, 2008-2024 excluding 2020Q2-2021Q4 (when layoffs
   of low-wage workers distorted average earnings). Is wage growth flatter when unemployment is high? (c2 < 0)
Writes output/ext/e05_states.csv; log = stdout."""
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
R = ROOT + "data/raw/ext/states/"
geo = pd.read_csv(ROOT + "data/raw/ext/oi/GeoIDs_-_State.csv")
ST = list(geo.stateabbrev)
POP = geo.set_index("stateabbrev").state_pop2019


def fred(path):
    f = pd.read_csv(path, index_col=0, parse_dates=True).iloc[:, 0]
    return pd.to_numeric(f, errors="coerce").resample("QS").mean()


ur = pd.DataFrame({s: fred(R + f"{s}UR.csv") for s in ST})
ahe = pd.DataFrame({s: fred(R + f"AHE_{s}.csv") for s in ST})

ox = pd.read_csv(ROOT + "data/raw/ext/oxcgrt_sub/OxCGRT_compact_subnational_v1.csv",
                 usecols=["CountryCode", "RegionCode", "Jurisdiction", "Date", "StringencyIndex_Average"])
ox = ox[(ox.CountryCode == "USA") & (ox.Jurisdiction == "STATE_TOTAL") & ox.RegionCode.notna()]
ox["st"] = ox.RegionCode.str[3:]
ox["date"] = pd.to_datetime(ox.Date.astype(str), format="%Y%m%d")
s = ox.pivot_table(index="date", columns="st", values="StringencyIndex_Average").resample("QS").mean() / 100
s = s.reindex(columns=ST)
print("states with stringency data:", s.notna().any().sum(), " quarters:", s.index[0].date(), "to", s.index[-1].date())

# ---- A
du = ur.sub(ur.loc["2019-10-01"], axis=1)
q = pd.date_range("2020-01-01", "2022-10-01", freq="QS")
lagS = s.shift(1).fillna(0.0)
lagS.loc["2020-01-01"] = 0.0
long = pd.DataFrame({"du": du.loc[q].stack(), "s0": s.reindex(q).stack(), "s1": lagS.reindex(q).stack()}).dropna()
long.index.names = ["q", "st"]; long = long.reset_index()
T = pd.get_dummies(long.q.astype(str), prefix="t", drop_first=False, dtype=float)
X = pd.concat([long[["s0", "s1"]], T], axis=1)
w = long.st.map(POP).values
ra = sm.WLS(long.du.values, X.values, weights=w).fit(cov_type="cluster", cov_kwds={"groups": long.st.factorize()[0]})
g0, g1 = ra.params[0], ra.params[1]; V = ra.cov_params()[:2, :2]
# no quarter effects (closest to the national fit, but now with 51 states)
rb = sm.WLS(long.du.values, long[["s0", "s1"]].values, weights=w).fit(cov_type="cluster", cov_kwds={"groups": long.st.factorize()[0]})
print(f"A. state panel, quarter effects: g0 {g0:.2f} ({np.sqrt(V[0,0]):.2f}), g1 {g1:.2f} ({np.sqrt(V[1,1]):.2f}); "
      f"no quarter effects: g0 {rb.params[0]:.2f} ({rb.bse[0]:.2f}), g1 {rb.params[1]:.2f} ({rb.bse[1]:.2f}); n {len(long)}")

# ---- B
wg = 100 * np.log(ahe).diff(4)
qb = [t for t in wg.index if pd.Timestamp("2008-01-01") <= t <= pd.Timestamp("2024-10-01")
      and not (pd.Timestamp("2020-04-01") <= t <= pd.Timestamp("2021-10-01"))]
ul = ur.shift(1)
lb = pd.DataFrame({"w": wg.loc[qb].stack(), "u": ul.loc[qb].stack()}).dropna()
lb.index.names = ["q", "st"]; lb = lb.reset_index()
lb["u_hi"] = (lb.u - 6).clip(lower=0)
Xb = pd.concat([lb[["u", "u_hi"]], pd.get_dummies(lb.q.astype(str), prefix="t", dtype=float),
                pd.get_dummies(lb.st, prefix="s", drop_first=True, dtype=float)], axis=1)
rw = sm.WLS(lb.w.values, Xb.values, weights=lb.st.map(POP).values).fit(cov_type="cluster", cov_kwds={"groups": lb.st.factorize()[0]})
print(f"B. state wage curve: slope below 6% unemployment {rw.params[0]:.3f} ({rw.bse[0]:.3f}); change in slope above 6% "
      f"{rw.params[1]:.3f} ({rw.bse[1]:.3f}); slope above 6% {rw.params[0] + rw.params[1]:.3f}; n {len(lb)}")
out = pd.DataFrame({"estimate": [g0, g1, rb.params[0], rb.params[1], rw.params[0], rw.params[1]],
                    "se": [np.sqrt(V[0, 0]), np.sqrt(V[1, 1]), rb.bse[0], rb.bse[1], rw.bse[0], rw.bse[1]]},
                   index=["covid_g0_state_quarterFE", "covid_g1_state_quarterFE", "covid_g0_state_noFE", "covid_g1_state_noFE",
                          "wage_slope_u_below6", "wage_slope_change_above6"])
out.attrs["cov_g"] = V
out.round(4).to_csv(ROOT + "output/ext/e05_states.csv")
np.save(ROOT + "output/ext/e05_covid_cov.npy", V)
