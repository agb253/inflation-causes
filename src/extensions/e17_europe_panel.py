"""Extension 17: the model's wage and price equations estimated on European countries, data the US estimates never saw.
The two estimates that set nearly all the width of the US ranges (extension 15 E) are the wage equation's response to
job openings per unemployed and the price equation's response to supply-chain pressure plus inflation's persistence.
Each European country is another episode of the same 2021-23 shock, with its own labor market.

Data (Eurostat SDMX API, data/raw/ext/eurostat/): wages = labour cost index, wages and salaries (lc_lci_r2_q, D11,
business economy B-S, seasonally and calendar adjusted); job vacancies (jvs_q_nace2, B-S, all sizes, not seasonally
adjusted: 4-quarter moving average); unemployed persons 15-74 (une_rt_q, seasonally adjusted); prices = HICP all items,
energy, food incl. alcohol and tobacco (prc_hicp_midx, monthly -> quarterly mean). Supply chains = the NY Fed GSCPI,
the same quarterly series as the US model (it is global).
Equations, as in src/bb_model.py (Bernanke-Blanchard), with country fixed effects:
  wage:  gw = c_i + sum_1-4 a gw + sum_1-4 b vu + sum_1-4 c exp1 + sum_1-4 d catch_up,   sum a + sum c = 1
  price: gp = c_i + sum_1-4 gp + sum_0-4 gw + sum_0-4 grpe + sum_0-4 grpf + sum_0-4 shortage,   sum gp lags + sum gw = 1
  gw, gp = 400 dlog; grpe, grpf = 400 dlog(energy or food price / wage index), as in the US model.
Differences from the US model, forced by the data: no survey expectations, so exp1 = average inflation over the past
four quarters (catch_up = that average minus its value a year earlier); no productivity term (absorbed by the country
effects); vu = V/U divided by the country's own 2010-19 average (vacancy surveys differ in coverage across countries;
the US comparison multiplies the US coefficients by the US 2010-19 average V/U, 0.62). Sample 2010Q1-2024Q4, dropping
2020Q2-2021Q2, when job-retention schemes distorted hourly labour costs. Errors clustered by country.
Variants: with year-quarter fixed effects in the wage equation (slope from differences across countries only);
2010-2019 only; for the price equation also dropping all of 2020-21, and western vs central & eastern Europe.
Part B, value of better supply-chain price data: would a sharper estimate of the DIRECT supply-chain effect (what
category- or industry-level price data measure, extension 2) narrow the supply-chain line? 6,000 redraws of the US
coefficients; supply-chain total 2021-24 = model inflation minus model inflation with the index at its 1990-2019 mean;
weighted by the category-panel estimate (1.49) with its s.e., half, a quarter, and 0.05 (known almost exactly).
Writes output/ext/e17_europe_panel.csv (sums of coefficients and their covariances), output/ext/e17_value_of_direct.csv;
log = stdout."""
import sys
sys.path.insert(0, __file__.rsplit("/src/", 1)[0] + "/src")
import numpy as np
import pandas as pd
import statsmodels.api as sm
import unified_model as UM, bb_model as m, decompose as D

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
E = ROOT + "data/raw/ext/eurostat/"
DROP = ("2020-04-01", "2021-04-01")
AGG = ("EA", "EA19", "EA20", "EA21", "EU", "EU27_2020", "EU28")


def es(f, **sel):
    d = pd.read_csv(E + f)
    for k, v in sel.items(): d = d[d[k] == v]
    d = d[d.OBS_VALUE.notna() & ~d.geo.isin(AGG)]
    if d.TIME_PERIOD.str.contains("-Q").any():
        d["t"] = pd.PeriodIndex(d.TIME_PERIOD.str.replace("-", ""), freq="Q").to_timestamp()
    else:
        d["t"] = pd.PeriodIndex(d.TIME_PERIOD, freq="M").to_timestamp()
    return d.pivot_table(index="t", columns="geo", values="OBS_VALUE")


def build():
    lci = es("lc_lci_r2_q.csv")
    vac = es("jvs_q_nace2.csv").rolling(4).mean()
    une = es("une_rt_q.csv")
    q = lambda w: w.resample("QS").mean()
    h = es("prc_hicp_midx_cp00.csv"); hn = es("prc_hicp_midx_nrg_food.csv", coicop="NRG"); hf = es("prc_hicp_midx_nrg_food.csv", coicop="FOOD")
    p, pe, pf = q(h), q(hn), q(hf)
    cs = sorted(set(lci) & set(vac) & set(une) & set(p) & set(pe) & set(pf))
    d0 = UM.quarterly(); gscpi = d0.shortage
    rows = []
    for c in cs:
        x = pd.DataFrame({"lci": lci[c], "v": vac[c], "u": une[c] * 1000, "p": p[c], "pe": pe[c], "pf": pf[c]}).dropna()
        if len(x) < 40: continue
        x = x.asfreq("QS")
        x["gw"] = 400 * np.log(x.lci).diff(); x["gp"] = 400 * np.log(x.p).diff()
        x["grpe"] = 400 * np.log(x.pe / x.lci).diff(); x["grpf"] = 400 * np.log(x.pf / x.lci).diff()
        vu = x.v / x.u; x["vu"] = vu / vu["2010":"2019"].mean()
        x["exp1"] = x.gp.rolling(4).mean(); x["catch_up"] = x.exp1 - x.exp1.shift(4)
        x["shortage"] = gscpi.reindex(x.index)
        for v in ["gw", "gp", "vu", "exp1", "catch_up", "grpe", "grpf", "shortage"]:
            for i in range(1, 5): x[f"{v}_l{i}"] = x[v].shift(i)
        x["c"] = c
        rows.append(x)
    return pd.concat(rows), cs


def fit(z, y, free, fixed_to_one, base, tfe=False):
    """OLS of y on regressors with sum(coefs on `fixed_to_one` + coef on base) = 1, by substitution:
    y - base = sum_k b_k (x_k - base) + free terms; the coef on base = 1 - sum b_k. Country (and quarter) effects."""
    cols = fixed_to_one + free
    ok = z[[y, base] + cols].notna().all(axis=1); ok &= ~z.index.to_series().between(*DROP).values
    w = z[ok]
    X = pd.concat([w[fixed_to_one].sub(w[base], axis=0), w[free]], axis=1)
    X = pd.concat([X, pd.get_dummies(w.c, prefix="c", dtype=float)], axis=1)
    if tfe: X = pd.concat([X, pd.get_dummies(w.index.astype(str), prefix="t", drop_first=True, dtype=float).set_index(w.index)], axis=1)
    r = sm.OLS((w[y] - w[base]).values, X.values).fit(cov_type="cluster", cov_kwds={"groups": w.c.factorize()[0]})
    k = len(cols)
    return pd.Series(r.params[:k], index=cols), pd.DataFrame(r.cov_params()[:k, :k], index=cols, columns=cols), len(w), w.c.nunique()


def sums(b, V, groups):
    """sums of coefficient groups and their covariance (linear combinations)."""
    A = np.array([[1.0 if n in g else 0.0 for n in b.index] for g in groups.values()])
    return pd.Series(A @ b.values, index=list(groups)), pd.DataFrame(A @ V.values @ A.T, index=list(groups), columns=list(groups))


def value_of_direct(x, est):
    panel = pd.read_csv(ROOT + "output/ext/e02_category_panel.csv").set_index("variant").loc["goods exposure"]
    pos = x.index.get_loc(UM.START); pre = x.index.get_loc(UM.REF)
    full = {k: x[k].values.copy() for k in ["grpe", "grpf", "shortage", "gpty", "greed", "vu"]}
    nos = {k: v.copy() for k, v in full.items()}; nos["shortage"][pos:] = x.shortage.values[:pre + 1].mean()
    q4 = [j for j, t in enumerate(x.index[pos:]) if t.month == 10 and t.year >= 2021]
    i0 = list(est["gp"][0].params.index).index("shortage")
    gq = (x.shortage - x.shortage[:UM.REF].mean()).values
    lag = np.column_stack([np.r_[np.full(k, np.nan), gq[:len(gq) - k]] for k in range(5)])
    q4a = [j for j, t in enumerate(x.index) if t.month == 10 and 2021 <= t.year <= 2024]
    rng = np.random.default_rng(12); tot, dr = [], []
    for _ in range(6000):
        C = D.draw(est, rng)
        tot.append(pd.Series(UM.simulate(C, x, full) - UM.simulate(C, x, nos)).rolling(4).mean().values[q4].sum())
        dr.append(pd.Series(lag @ C["gp"][i0:i0 + 5]).rolling(4).mean().values[q4a].sum())
    tot, dr = np.array(tot), np.array(dr)

    def wq(w, q):
        o = np.argsort(tot); c = np.cumsum(w[o]) / w.sum(); return float(tot[o][np.searchsorted(c, q)])
    rows = []
    for lab, se in [("no panel", None), ("category panel as estimated", panel.effect_se), ("panel s.e. halved", panel.effect_se / 2),
                    ("panel s.e. quartered", panel.effect_se / 4), ("direct effect known almost exactly (s.e. 0.05)", 0.05)]:
        w = np.ones_like(tot) if se is None else np.exp(-0.5 * ((dr - panel.effect_2021_24) / se) ** 2)
        rows.append(dict(evidence=lab, p5=wq(w, .05), p50=wq(w, .5), p95=wq(w, .95), ess=float(w.sum() ** 2 / (w ** 2).sum())))
    return pd.DataFrame(rows).set_index("evidence"), float(np.corrcoef(dr, tot)[0, 1])


def main():
    z, cs = build()
    L = lambda v, cur=False: m.L(v, cur=cur)
    out, cov = {}, {}
    wvar = [("wage, 2010-24", None, False), ("wage, 2010-24, quarter effects", None, True), ("wage, 2010-19", "2019-10-01", False)]
    for name, end, tfe in wvar:
        zz = z if end is None else z[z.index <= end]
        # restriction: sum gw lags + sum exp1 lags = 1; base = exp1_l4
        b, V, n, nc = fit(zz, "gw", L("vu") + L("catch_up"), L("gw") + ["exp1_l1", "exp1_l2", "exp1_l3"], "exp1_l4", tfe)
        s, S = sums(b, V, {"vu_sum": L("vu"), "gw_lag_sum": L("gw")})
        out[name] = dict(s, n=n, countries=nc); cov[name] = S
    global DROP
    CEE = ["BG", "CZ", "EE", "HR", "HU", "LT", "LV", "PL", "RO", "SK", "SI"]
    for name, end, keep, drop in [("price, 2010-24", None, None, DROP), ("price, 2010-19", "2019-10-01", None, DROP),
                                  ("price, 2010-24, dropping 2020Q1-2021Q4", None, None, ("2020-01-01", "2021-10-01")),
                                  ("price, 2010-24, western Europe only", None, lambda c: ~c.isin(CEE), DROP),
                                  ("price, 2010-24, central & eastern Europe only", None, lambda c: c.isin(CEE), DROP)]:
        zz = z if end is None else z[z.index <= end]
        if keep is not None: zz = zz[keep(zz.c).values]
        DROP, keep_drop = drop, DROP
        # restriction: sum gp lags + sum gw (0-4) = 1; base = gw_l4
        b, V, n, nc = fit(zz, "gp", L("grpe", True) + L("grpf", True) + L("shortage", True), L("gp") + ["gw", "gw_l1", "gw_l2", "gw_l3"], "gw_l4")
        s, S = sums(b, V, {"shortage_sum": L("shortage", True), "gp_lag_sum": L("gp")})
        out[name] = dict(s, n=n, countries=nc); cov[name] = S
        DROP = keep_drop
    # the US model's own estimates of the same sums, in the same units
    d, x, est, *_ = UM.main()
    C = D.coefs(est); vbar = x.vu["2010":"2019"].mean()
    wn, pn = list(est["gw"][0].params.index), list(est["gp"][0].params.index)
    Vw, Vp = est["gw"][0].cov_params(), est["gp"][0].cov_params()
    uw = sums(pd.Series(C["gw"], index=wn), Vw, {"vu_sum": L("vu"), "gw_lag_sum": L("gw")})
    up = sums(pd.Series(C["gp"], index=pn), Vp, {"shortage_sum": L("shortage", True), "gp_lag_sum": L("gp")})
    out["US model, wage"] = dict(vu_sum=uw[0].vu_sum * vbar, gw_lag_sum=uw[0].gw_lag_sum, n=est["gw"][0].nobs, countries=1)
    cov["US model, wage"] = uw[1] * np.outer([vbar, 1], [vbar, 1])
    out["US model, price"] = dict(up[0], n=est["gp"][0].nobs, countries=1); cov["US model, price"] = up[1]
    rows = []
    for k, v in out.items():
        r = dict(estimate=k, **v)
        S = cov[k]
        for a in S.index:
            r[f"se_{a}"] = float(np.sqrt(S.loc[a, a]))
        if len(S) == 2:
            r["corr"] = float(S.iloc[0, 1] / np.sqrt(S.iloc[0, 0] * S.iloc[1, 1]))
        if "vu_sum" in v:
            r["long_run_slope"] = v["vu_sum"] / (1 - v["gw_lag_sum"])
        if "shortage_sum" in v:     # long-run effect of the supply-chain index with wages held fixed; s.e. by the delta method
            a, g = v["shortage_sum"], v["gp_lag_sum"]; J = np.array([1 / (1 - g), a / (1 - g) ** 2])
            r["long_run_supply"] = a / (1 - g); r["se_long_run_supply"] = float(np.sqrt(J @ S.values @ J))
        if "vu_sum" in v:
            a, g = v["vu_sum"], v["gw_lag_sum"]; J = np.array([1 / (1 - g), a / (1 - g) ** 2])
            r["se_long_run_slope"] = float(np.sqrt(J @ S.values @ J))
        rows.append(r)
    o = pd.DataFrame(rows).set_index("estimate")
    print("countries:", " ".join(cs))
    print(f"US 2010-19 average V/U {vbar:.3f} (US wage sums are per 1 x that average)")
    pd.set_option("display.width", 250); print(o.round(3).to_string())
    o.round(5).to_csv(ROOT + "output/ext/e17_europe_panel.csv")
    v, rho = value_of_direct(x, est)
    print(f"B. supply-chain total 2021-24 (log points, log-change units) by how well the direct effect is known; corr(direct, total) {rho:.2f}")
    print(v.round(2).to_string()); v.round(3).to_csv(ROOT + "output/ext/e17_value_of_direct.csv")


if __name__ == "__main__":
    main()
