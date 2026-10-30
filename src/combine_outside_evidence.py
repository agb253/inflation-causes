"""Bring two outside sources of evidence to bear on the model's 1,000 redraws (output/unified_draws.npy).

1. Cross-country relief estimate (src/cross_country_relief.py, spec CC_SPEC): an independent measurement of what all
   US relief did to inflation in 2021-22. Each redraw is weighted by how well its relief total matches it:
       w_i ~ exp(-0.5 ((R_i - m) / s)^2)
   R_i = redraw i's Trump + Biden relief, as the sum over 2021 and 2022 of the annual mean of its year-over-year
   contributions (annual averages, the timing of the cross-country data); m, s = the cross-country estimate and its
   standard error, converted from core CPI to PCE points by the ratio of US excess core PCE to excess core CPI inflation
   over 2021-22. Since all lines in a redraw move together, the weights also update the other lines (the COVID drag
   most, correlation -0.92 with relief).
2. Shapiro (SF Fed) supply/demand labels: a reconciliation, not a weighting. Shapiro labels each category's price
   change supply- or demand-driven (or ambiguous); the model assigns inflation to causes. Matching them needs two
   unknown shares (below), so the result is an estimate of how much of the model's supply lines his data label as
   demand ("leakage" L), with its range:
       Shapiro supply + a x ambiguous = model supply lines - L + c x (lines with no Shapiro counterpart)
   model supply lines = supply chains + war + worker shortage + energy & food 2020-21 and after 2023Q1;
   no counterpart = COVID drag on jobs + pre-existing momentum above 2019 + productivity, greed, not explained;
   a = share of 'ambiguous' that is really supply-driven, c = share of the no-counterpart lines that his method labels
   supply-driven. Central: a = c = his supply share of labelled inflation; range: a, c each from 0 to 1.
   All measured as 2021-24 totals (sum of Q4 values of year-over-year rates) of change from the 2019 average.
Writes output/combined_cumulative_2021_2024.csv, output/combined_pairs.csv, output/shapiro_leakage.csv.
"""
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import unified_data as U

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
CC_SPEC = "core_advanced_2021_22"   # relief effects peak in 2021-22; 2023-24 cross-country variation is dominated by
                                    # Europe's energy shock (see output/cross_country_relief.csv for every spec)

yd = np.load(ROOT + "output/unified_draws.npy")
cols = list(pd.read_csv(ROOT + "output/unified_draws_columns.csv").line)
q = pd.read_csv(ROOT + "output/unified_causes_quarterly.csv", index_col=0)
Q = list(q.index)
Q4 = [i for i, t in enumerate(Q) if t.endswith("Q4") and int(t[:4]) >= 2021]
col = lambda ks: [cols.index(k) for k in ks]
tot = lambda ks: yd[:, Q4][:, :, col(ks)].sum(axis=(1, 2))        # 2021-24 total per redraw
pt = lambda ks: q.iloc[Q4][ks].sum().sum()                          # point estimate


def annual_mean_sum(ks, years=(2021, 2022)):
    v = yd[:, :, col(ks)].sum(axis=2)
    return sum(v[:, [i for i, t in enumerate(Q) if int(t[:4]) == y]].mean(axis=1) for y in years)


# ---------------------------------------------------------------- 1. cross-country weights
cc = pd.read_csv(ROOT + "output/cross_country_relief.csv", index_col=0).loc[CC_SPEC]
n = U.nipa({"DPCCRG"}).DPCCRG                                       # core PCE price index (BEA T2.3.4)
ann = n.groupby(n.index.year).mean(); pce_core = 100 * ann.pct_change()
oecd = pd.read_csv(ROOT + "data/raw/oecd/cpi_annual.csv")
cpi_core = oecd[(oecd.REF_AREA == "USA") & (oecd.EXPENDITURE == "_TXCP01_NRG")].set_index("TIME_PERIOD").OBS_VALUE
ex = lambda p: p[[2021, 2022]].sum() - 2 * p[list(range(2015, 2020))].mean()
ratio = ex(pce_core) / ex(cpi_core)
m, s = cc.us_effect * ratio, cc.us_effect_se * ratio
R = annual_mean_sum(["trump", "biden"])
R_point = sum(q.loc[[t for t in Q if t.startswith(str(y))], ["trump", "biden"]].sum(axis=1).mean() for y in (2021, 2022))
w = np.exp(-0.5 * ((R - m) / s) ** 2); w /= w.sum()
ess = 1 / (w ** 2).sum()


def wq(v, p):
    o = np.argsort(v); c = np.cumsum(w[o]); return v[o][np.searchsorted(c, p)]


LINES = {"trump": ["trump"], "biden": ["biden"], "relief_all": ["trump", "biden"], "pentup": ["pentup"],
         "fed_all": ["fed_easing", "fed_hikes", "fed_pre2020"], "covid_other": ["covid_other"],
         "worker_shortage": ["worker_shortage"], "shortage": ["shortage"], "energy_war": ["energy_war"],
         "greed": ["greed"], "grp_pandemic": ["trump", "biden", "pentup", "covid_other"],
         "grp_labor": ["trump", "biden", "pentup", "fed_easing", "fed_hikes", "fed_pre2020", "covid_other", "worker_shortage"],
         "grp_supply": ["shortage", "energy_war"],
         "model_total": [c for c in cols if not c.startswith("memo") and c != "unexplained"]}
rows = {}
for k, ks in LINES.items():
    v = tot(ks)
    rows[k] = dict(point=pt(ks), before_p5=np.percentile(v, 5), before_p50=np.percentile(v, 50), before_p95=np.percentile(v, 95),
                   after_p5=wq(v, .05), after_p16=wq(v, .16), after_p50=wq(v, .5), after_p84=wq(v, .84), after_p95=wq(v, .95))
comb = pd.DataFrame(rows).T
comb["width_before"] = comb.before_p95 - comb.before_p5
comb["width_after"] = comb.after_p95 - comb.after_p5
comb.attrs = {}
meta = pd.DataFrame({"value": {"cc_spec": CC_SPEC, "cc_us_effect_cpi": cc.us_effect, "cc_se_cpi": cc.us_effect_se,
                               "cpi_to_pce_ratio": ratio, "m_pce": m, "s_pce": s, "model_relief_point_same_metric": R_point,
                               "model_relief_p5": np.percentile(R, 5), "model_relief_p95": np.percentile(R, 95),
                               "ess": ess, "ndraw": len(w), "cc_n": cc.n}})
comb.round(3).to_csv(ROOT + "output/combined_cumulative_2021_2024.csv")
meta.to_csv(ROOT + "output/combined_meta.csv")

# pairwise shares, before and after
PAIRS = [("Supply chains", ["shortage"], "Relief signed by Biden", ["biden"]),
         ("Supply chains", ["shortage"], "All relief (Trump + Biden)", ["trump", "biden"]),
         ("Relief signed by Biden", ["biden"], "Relief signed by Trump", ["trump"]),
         ("Supply chains + war + worker shortage", ["shortage", "energy_war", "worker_shortage"], "Relief + pent-up + Fed",
          ["trump", "biden", "pentup", "fed_easing", "fed_hikes", "fed_pre2020"]),
         ("Supply chains + war", ["shortage", "energy_war"], "Relief + pent-up + Fed",
          ["trump", "biden", "pentup", "fed_easing", "fed_hikes", "fed_pre2020"])]
pr = [(a, b, float(np.mean(tot(ka) > tot(kb))), float(w @ (tot(ka) > tot(kb)))) for a, ka, b, kb in PAIRS]
pd.DataFrame(pr, columns=["A", "B", "before", "after"]).round(3).to_csv(ROOT + "output/combined_pairs.csv", index=False)

# ---------------------------------------------------------------- 2. Shapiro reconciliation
sf = pd.read_excel(ROOT + "data/raw/sf_fed/supply-demand-pce-inflation.xlsx", sheet_name="Data")
sf.index = pd.PeriodIndex(sf.time_month.astype(str).str.strip().str.replace("m", "-"), freq="M")
SFC = {"S": "Supply-driven Inflation (headline, y/y)", "D": "Demand-driven Inflation (headline, y/y)", "A": "Ambiguous (headline, y/y)"}


def shapiro_excess(frame, cols_):
    out = {}
    for g, c in cols_.items():
        qq = frame[c].groupby(frame.index.asfreq("Q")).mean()
        base = frame.loc["2019-01":"2019-12", c].mean()
        out[g] = sum(qq[pd.Period(f"{y}Q4")] - base for y in range(2021, 2025))
    return out


variants = {"SF Fed published": shapiro_excess(sf, SFC)}
for lv in ["L4t", "L4pct", "L5t", "L5pct"]:          # this project's recomputations (src/replicate_sf_supply_demand.py)
    me = pd.read_csv(ROOT + f"output/sf_replication_monthly_{lv}.csv", index_col=0)
    me.index = pd.PeriodIndex(me.index, freq="M")
    variants[f"recomputed {lv}"] = shapiro_excess(me, {"S": "supply_headline_yoy", "D": "demand_headline_yoy", "A": "ambiguous_headline_yoy"})

pce = U.nipa({"DPCERG"}).DPCERG
pyoy = 100 * (pce / pce.shift(4) - 1)
base19 = 100 * (pce["2019"].mean() / pce["2018"].mean() - 1)        # annual-average 2019 inflation, close to the monthly-y/y average
SUP = ["shortage", "energy_war", "worker_shortage", "energy_after", "memo_energy_covid"]
supply_i = tot(SUP)
# no-counterpart lines: COVID drag on jobs, pre-existing above 2019, productivity, greed, not explained (energy_after
# and the 2020-21 energy are in SUP; covid_other contains memo_energy_covid, so it is taken out)
pre_above = tot(["baseline", "fed_pre2020"]) - 4 * base19
none_i = (tot(["covid_other"]) - tot(["memo_energy_covid"])) + pre_above + tot(["gpty", "unexplained", "greed"])
lk = []
for name, v in variants.items():
    share = v["S"] / (v["S"] + v["D"])
    for a_, c_, lab in [(share, share, "central"), (0, 0, "a=0,c=0"), (1, 1, "a=1,c=1"), (0, 1, "a=0,c=1"), (1, 0, "a=1,c=0")]:
        L = supply_i + c_ * none_i - (v["S"] + a_ * v["A"])
        lk.append(dict(shapiro=name, case=lab, S=v["S"], D=v["D"], A=v["A"], a=a_, c=c_,
                       L_p5=wq(L, .05), L_p50=wq(L, .5), L_p95=wq(L, .95)))
lk = pd.DataFrame(lk)
lk.round(3).to_csv(ROOT + "output/shapiro_leakage.csv", index=False)

if __name__ == "__main__":
    pd.set_option("display.width", 250)
    print(meta.to_string()); print(comb.round(2).to_string()); print(pd.DataFrame(pr).round(2).to_string())
    print(lk.round(2).to_string())
    print("mean no-counterpart lines", none_i.mean().round(2), " model supply lines", supply_i.mean().round(2), " 2019 base", round(base19, 2))

# supply vs demand after moving the leakage from the supply lines to demand. Not a probability: moving L makes the
# model's split match Shapiro's by construction, so the spread comes from the label shares a, c, not from the redraws.
sup3, dem3 = tot(["shortage", "energy_war", "worker_shortage"]), tot(["trump", "biden", "pentup", "fed_easing", "fed_hikes", "fed_pre2020"])
adj = []
for name, v in variants.items():
    sh = v["S"] / (v["S"] + v["D"])
    for a_, c_, lab in [(sh, sh, "central"), (0, 0, "a=0,c=0"), (1, 1, "a=1,c=1")]:
        L = supply_i + c_ * none_i - (v["S"] + a_ * v["A"])
        adj.append(dict(shapiro=name, case=lab, supply_after=wq(sup3 - L, .5), demand_after=wq(dem3 + L, .5)))
adj = pd.DataFrame(adj)
adj.round(3).to_csv(ROOT + "output/shapiro_adjusted_balance.csv", index=False)
if __name__ == "__main__":
    print(adj.round(2).to_string())
