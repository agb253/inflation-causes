"""Quarterly causes of US CPI inflation 2020Q1-2024Q4, one model per cause. Units: year-over-year CPI inflation, percentage points (yoy), and cumulative price level (percent).
See output/METHODS_quarterly.md for why each model was chosen and every assumption. Run from project root:  python src/build_quarterly_causes.py"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, "src")
import bb_model as m, fiscal_sf_replication as F
OUT = "output/"; RAW = "data/raw/"
Q = pd.date_range("2019-01-01", "2024-10-01", freq="QS"); W = Q >= "2020-01-01"       # 24 quarters; 2020Q1.. is the reporting window
roll4 = lambda a: pd.DataFrame(a).rolling(4).mean().values
yoy = lambda a: roll4(a)[W] if a.ndim > 1 else roll4(a[:, None])[W, 0]
cum_q = lambda a: np.cumsum(a[W], axis=0) / 4          # sum of annualized quarterly rates / 4 = cumulative log points since 2019Q4

# ---------- 1. Bernanke-Blanchard supply side (estimated here): baseline, shortages, energy+food, labor tightness, productivity, unexplained
x = m.build(m.load(m.RAW + "data_us_new.csv")); gp = x["gp"].reindex(Q).values
point = pd.read_csv(OUT + "decomp_point.csv", index_col=0, parse_dates=True).reindex(Q)
draws = np.load(OUT + "draws.npy")                                         # (2000, 20, 7): energy, food, shortages, labor_tightness, productivity, baseline_pre2020, unexplained
cols = ["energy", "food", "shortages", "labor_tightness", "productivity", "baseline_pre2020", "unexplained"]
def ext(a2d, base_col):                                                    # pre-2020: baseline = actual inflation, all shocks 0
    out = np.zeros((len(Q), len(cols))); out[W] = a2d; out[~W, cols.index("baseline_pre2020")] = gp[~W]; return out
pt = ext(point.loc[W, cols].values, 0)
dr = np.stack([ext(draws[i], 0) for i in range(len(draws))])
assert np.allclose(pt.sum(axis=1)[W], gp[W]), "B&B components must sum to actual"
G = {"baseline": ["baseline_pre2020"], "shortages": ["shortages"], "energy_food": ["energy", "food"], "labor": ["labor_tightness"], "bb_other": ["productivity", "unexplained"]}
bb_q = {k: pt[:, [cols.index(c) for c in v]].sum(axis=1) for k, v in G.items()}
bb_d = {k: dr[:, :, [cols.index(c) for c in v]].sum(axis=2) for k, v in G.items()}
res = {}                                                                   # cause -> dict(y=yoy point, lo, hi, L=cum point, Llo, Lhi)
for k in G:
    y = yoy(bb_q[k]); yd = np.stack([yoy(bb_d[k][i]) for i in range(len(dr))]); L = cum_q(bb_q[k][:, None])[:, 0]
    Ld = np.stack([cum_q(bb_d[k][i][:, None])[:, 0] for i in range(len(dr))])
    res[k] = dict(y=y, lo=np.percentile(yd, 5, 0), hi=np.percentile(yd, 95, 0), L=L, Llo=np.percentile(Ld, 5, 0), Lhi=np.percentile(Ld, 95, 0))
actual_y = yoy(gp); actual_L = cum_q(gp[:, None])[:, 0]

# ---------- 2. Fiscal: SF Fed (Jorda et al. 2022) panel local projection, authors' data/code logic; timing from actual disposable-income flows
d = F.load(); c = F.coefs(d)
us = d[d.country == "United States"].set_index("qdate").sort_index()
bea = pd.read_csv(RAW + "fred_via_fetch/bea_real_dpi_per_capita_q.csv", parse_dates=["date"]).set_index("date")["A229RX0Q048SBEA"]
tq = lambda i: i.year * 4 + i.quarter
pool = d[(d.qdate >= "2015-01-01") & (d.qdate <= "2019-10-01")].dropna(subset=["RDI"])     # authors' do-file: `reg RDI qdate` pooled over all 10 countries, 2015Q1-2019Q4
trend_fit = np.polyfit(tq(pd.DatetimeIndex(pool.qdate)), pool.RDI, 1)
chk = us[us.index >= "2020-01-01"].dropna(subset=["linear_trend"])
assert np.allclose(np.polyval(trend_fit, tq(chk.index)), chk.linear_trend.values, atol=1e-3), "trend must match authors'"
last = pd.Timestamp("2021-07-01"); gap = us.gap_RDI.astype("float64").copy()
RDI = us.RDI.astype("float64").copy()
for t in pd.date_range("2021-10-01", "2024-10-01", freq="QS"):             # extension past the authors' sample: chain-link their income index with BEA real DPI per capita
    RDI.loc[t] = RDI.loc[last] + 100 * (np.log(bea[t]) - np.log(bea[last])); gap.loc[t] = RDI.loc[t] - np.polyval(trend_fit, tq(t))
    if t >= pd.Timestamp("2022-01-01"): gap.loc[t] = 0.0        # ASSUMPTION: pandemic support expired with the Dec-2021 child credit; later income-vs-trend gaps (real wage growth, inflation erosion) are not fiscal. Only the model's own 0-3 quarter lags carry fiscal effects into 2022.
gap = gap.reindex(Q).astype(float)
roll = gap.rolling(4, min_periods=1).mean()
pub = us.rolling_avg_rdi.reindex(Q)
assert np.allclose(roll[Q <= "2021-07-01"].dropna().values[-6:], pub[Q <= "2021-07-01"].dropna().values[-6:], atol=1e-6), "rolling avg must reproduce authors'"
def eff(r):                                                                # sum_h c_h * rolling_avg_{t-h}, h=0..3
    r = np.asarray(r, float); e = np.full(len(r), np.nan)
    for t in range(3, len(r)): e[t] = sum(c[h][0] * r[t - h] for h in range(4))
    return e
fe = eff(roll.values); fb = np.full(len(Q), np.nan)
for t in range(3, len(Q)): fb[t] = sum(1.645 * c[h][1] * roll.values[t - h] for h in range(4))
fe = np.nan_to_num(fe); fb = np.nan_to_num(fb)
# who signed the law behind each quarter's income gap: excess transfers (PCTR above its 2019-01..2020-02 trend), months Mar2020-Feb2021 = Trump-signed laws, Mar2021+ = Biden-signed ARP
pc = pd.read_csv(RAW + "fred_via_fetch/bea_pctr_monthly.csv", parse_dates=["date"]).set_index("date")["PCTR_SAAR_bn"]
fit = np.polyfit(np.arange(14), pc.iloc[:14].values, 1); base = np.polyval(fit, np.arange(len(pc)))
exm = (pc.values - base).clip(min=0); exm = pd.Series(exm, index=pc.index)
trump_m = (exm.index >= "2020-03-01") & (exm.index <= "2021-02-01")
exT = exm.where(trump_m, 0).groupby(exm.index.to_period("Q")).sum(); exB = exm.where(~trump_m & (exm.index >= "2021-03-01"), 0).groupby(exm.index.to_period("Q")).sum()
sT = pd.Series(0.0, index=Q); sB = pd.Series(0.0, index=Q)
for t in Q:
    p = t.to_period("Q")
    if p in exT.index and t >= pd.Timestamp("2020-01-01") and t <= pd.Timestamp("2021-10-01"):
        tot = exT[p] + exB[p]
        if tot > 0.01 * base.mean() * 3: sT[t], sB[t] = exT[p] / tot, exB[p] / tot
gT, gB = gap * sT, gap * sB; gU = gap - gT - gB
comp = {}
for nm, g_ in [("trump", gT), ("biden", gB), ("unassigned", gU)]:
    comp[nm] = eff(g_.rolling(4, min_periods=1).mean().values); comp[nm] = np.nan_to_num(comp[nm])
assert np.allclose(sum(comp.values()), fe), "signer split must sum to the total fiscal effect"
def lvl(y):                                                                # yoy effect -> level effect: L_t = y_t + L_{t-4}
    Lv = np.zeros(len(y))
    for t in range(len(y)):
        if Q[t] >= pd.Timestamp("2020-01-01"): Lv[t] = y[t] + (Lv[t - 4] if t >= 4 else 0)
    return Lv
res["fiscal"] = dict(y=fe[W], lo=(fe - fb)[W], hi=(fe + fb)[W], L=lvl(fe)[W], Llo=lvl(fe - fb)[W], Lhi=lvl(fe + fb)[W])
fiscal_split = pd.DataFrame({k: v[W] for k, v in comp.items()}, index=Q[W])

# ---------- 3. Fed policy: Chicago Fed Letter 483 (D'Amico & King 2023), digitized from its Figure 2F (annual-rate effect on CPI inflation); IQR band from the same chart
fd = pd.read_csv(OUT + "fed_policy_effect_digitized.csv"); fd["t"] = pd.PeriodIndex(fd.q, freq="Q").to_timestamp()
fd = fd[fd.t >= "2021-10-01"].set_index("t").reindex(Q)
fq, flo, fhi = [fd[k].fillna(0).values for k in ("median", "band_lo", "band_hi")]
res["fed"] = dict(y=yoy(fq), lo=yoy(flo), hi=yoy(fhi), L=cum_q(fq[:, None])[:, 0], Llo=cum_q(flo[:, None])[:, 0], Lhi=cum_q(fhi[:, None])[:, 0])

# ---------- 4. Corporate profits: BEA nonfinancial-corporate price = unit labor cost + unit nonlabor cost + unit profit (accounting identity), excess over its 2015-2019 pace
b = pd.concat([pd.read_csv(RAW + "fred_via_fetch/bea_nfc_profit_price_2013_2018.csv", parse_dates=["date"]).set_index("date")[["price_A455", "profit_A463"]],
               pd.read_csv(RAW + "fred_via_fetch/bea_nfc_unit_costs_q.csv", parse_dates=["date"]).set_index("date")[["price_A455", "profit_A463"]]])
raw = 400 * b.profit_A463.diff() / b.price_A455.shift(1)                   # quarterly annualized contribution of unit profit to price growth, pp
norm = raw["2015-01-01":"2019-10-01"].mean()
pq = (raw - norm).reindex(Q).fillna(0).values.copy(); pq[~W] = (raw.reindex(Q).values - norm)[~W]
res["profits"] = dict(y=yoy(pq), lo=np.full(W.sum(), np.nan), hi=np.full(W.sum(), np.nan), L=cum_q(pq[:, None])[:, 0], Llo=np.full(W.sum(), np.nan), Lhi=np.full(W.sum(), np.nan))

# ---------- assemble. ADDITIVE causes (one model, sum to actual CPI) vs OVERLAY policy effects (other models' counterfactuals; not summed)
add = ["baseline", "shortages", "energy_food", "labor", "bb_other"]; ovl = ["fiscal", "fed", "profits"]
tot_y = sum(res[k]["y"] for k in add); tot_L = sum(res[k]["L"] for k in add)
assert np.allclose(tot_y, actual_y) and np.allclose(tot_L, actual_L), "additive causes must reproduce actual CPI"
tab = pd.DataFrame(index=Q[W].to_period("Q").astype(str)); tab["actual_cpi_yoy"] = actual_y
for k in add + ovl:
    tab[k] = res[k]["y"]; tab[k + "_lo"] = res[k]["lo"]; tab[k + "_hi"] = res[k]["hi"]
tab.round(3).to_csv(OUT + "quarterly_causes_yoy.csv")
cumtab = pd.DataFrame(index=tab.index); cumtab["actual"] = actual_L
for k in add + ovl: cumtab[k] = res[k]["L"]; cumtab[k + "_lo"] = res[k]["Llo"]; cumtab[k + "_hi"] = res[k]["Lhi"]
cumtab.round(3).to_csv(OUT + "quarterly_causes_cumulative.csv")
fiscal_split.index = tab.index; fiscal_split.round(3).to_csv(OUT + "fiscal_by_signer_yoy.csv")
pd.set_option("display.width", 250); print(tab[["actual_cpi_yoy"] + add + ovl].round(2).to_string())
print(cumtab[["actual"] + add + ovl].iloc[[3, 7, 11, 15, 19]].round(2).to_string()); print(fiscal_split.round(2).to_string())
print("profit-contribution norm 2015-19 (annualized pp):", round(norm, 2))
