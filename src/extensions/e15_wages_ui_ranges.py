"""Extension 15: three questions about the wage and relief links, and new data aimed at narrowing the ranges.

A. Were wages held down before COVID, so that 2021-24 wage growth was a catch-up? (a) Labor share, real hourly
   compensation and productivity, nonfarm business (BLS via FRED PRS85006173, COMPRNFB, OPHNFB), 2019Q4 to 2021Q4,
   2022Q4, 2024Q4. (b) Atlanta Fed Wage Growth Tracker by wage quartile (FRED FRBATLWGT12MMUMHWGWD{1,26,51,76}WP,
   12-month moving average of median wage growth of the same workers), deflated by the PCE price index (PCEPI).
   (c) Catch-up term in the model's wage equation: add last quarter's labor-share gap, 100 x log(labor share / its
   1990-2019 mean) or its gap from a 1990-2019 log-linear trend, estimate 1990-2019 under the model's restriction.
   A negative coefficient on the level gap = wages grow faster when labor's share is low.
B. Unemployment checks. (a) Where they are in the model: BEA's "Expansion of unemployment programs" line is one of
   the relief payments (src/fiscal_by_law.py, CBO multiplier 0.67). (b) Did the extra $300 a week keep people out of
   work? 25 states ended it early (June 12 - July 31, 2021; Opportunity Insights state policy file, as in
   extension 6). Difference-in-differences, April-September 2021, state and week (month) fixed effects, 2019 population
   weights, errors clustered by state: employment (Opportunity Insights / Paychex-Intuit-Earnin, change vs January 2020,
   all and lowest wage quartile), unemployment rate (FRED {ST}UR) and average hourly earnings (FRED
   SMU{fips}000000500000003) by month.
C. State wage curve on job openings per unemployed: JOLTS state job openings (BLS JTS000000{fips}0000000JOL) over LAUS
   unemployed (BLS LASST{fips}0000000000004), both seasonally adjusted, quarterly means; 4-quarter growth of average
   hourly earnings on the average of the four previous quarters' V/U, state and quarter fixed effects, 2009-2024
   excluding 2020Q2-2021Q4. Compared with the model's long-run wage slope, sum(V/U coefs) / sum(expectations coefs).
D. Relief size from the unemployment data. For each relief timing and size (scale x the BEA-payments-based effect,
   0.25 to 4), unemployment the model leaves unexplained, 2020Q1-2022Q4, after the lockdown term is re-fitted
   (exactly as in the model). Log-likelihood -n_eff/2 log(SSR), n_eff = n (1-rho)/(1+rho) with rho the residuals'
   first-order autocorrelation at the best fit; flat prior on log scale. The earlier test of this
   (src/uncertainty/relief_scale_fit.py) compared centred R2, which is computed on a different left-hand side for
   each scale and so cannot rank them; the sum of squared misses is in the same units (unemployment) for all.
E. Which equation sets the width of each line: 150 redraws of one equation's coefficients at a time (others at their
   point estimates, every other input at its point), 90% width of the 2021-24 total.
Writes output/ext/e15_*.csv; log = stdout."""
import sys, json, glob
sys.path.insert(0, __file__.rsplit("/src/", 1)[0] + "/src")
import numpy as np
import pandas as pd
import statsmodels.api as sm
import unified_model as UM, bb_model as m, decompose as D, fiscal_by_law as F, pentup as P

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
R = ROOT + "data/raw/ext/"
geo = pd.read_csv(R + "oi/GeoIDs_-_State.csv")
ST = list(geo.stateabbrev); POP = geo.set_index("stateabbrev").state_pop2019
FIPS = {int(f): s for f, s in zip(geo.statefips, geo.stateabbrev)}
SCALES = np.exp(np.linspace(np.log(0.25), np.log(4.0), 41))


def fq(path, freq="QS"):
    f = pd.read_csv(path, index_col=0, parse_dates=True).iloc[:, 0]
    return pd.to_numeric(f, errors="coerce").resample(freq).mean()


def did(w, ycol, end, unit="st", time="date", default_post="2021-06-26"):
    w = w[w[ycol].notna()].copy()
    w["post"] = [float(t > end.get(s, pd.Timestamp(default_post))) for s, t in zip(w[unit], w[time])]
    w["tp"] = w[unit].isin(end.index).astype(float) * w.post
    X = pd.concat([w[["tp"]], pd.get_dummies(w[unit], prefix="s", dtype=float),
                   pd.get_dummies(w[time].astype(str), prefix="t", drop_first=True, dtype=float)], axis=1)
    r = sm.WLS(w[ycol].values, X.values, weights=w[unit].map(POP).values).fit(
        cov_type="cluster", cov_kwds={"groups": w[unit].factorize()[0]})
    return float(r.params[0]), float(r.bse[0]), len(w)


def part_a(x):
    q = lambda s: fq(R + "fred2b/" + s + ".csv")
    ls, rc, pr = q("PRS85006173"), q("COMPRNFB"), q("OPHNFB")
    rows = []
    for b in ["2021-10-01", "2022-10-01", "2024-10-01"]:
        a = "2019-10-01"
        rows.append(dict(item=f"2019Q4 to {b[:4]}Q4, % (log points)", real_comp_per_hour=100 * np.log(rc[b] / rc[a]),
                         productivity=100 * np.log(pr[b] / pr[a]), labor_share=100 * np.log(ls[b] / ls[a])))
    facts = pd.DataFrame(rows).set_index("item")
    era = pd.Series({"1990-99": ls["1990":"1999"].mean(), "2000-07": ls["2000":"2007"].mean(), "2010-19": ls["2010":"2019"].mean(),
                     "2019Q4": ls["2019-10-01"], "2022": ls["2022"].mean(), "2024": ls["2024"].mean()}, name="labor share index (2017=100)")
    pce = fq(R + "fred2b/PCEPI.csv", "MS")
    qrt = {}
    for lab, s in [("lowest quarter of wages", "WD1WP"), ("second", "WD26WP"), ("third", "WD51WP"), ("top quarter", "WD76WP")]:
        g = fq(R + "fred2b/" + f"FRBATLWGT12MMUMHWG{s}.csv", "MS")
        nom = sum(np.log1p(g[f"{y}-12-01"] / 100) for y in range(2020, 2025)) * 100
        qrt[lab] = dict(nominal=nom, real=nom - 100 * np.log(pce["2024-12-01"] / pce["2019-12-01"]))
    qrt = pd.DataFrame(qrt).T
    z = 100 * np.log(ls / ls["1990":"2019"].mean())
    t = np.arange(len(ls)); sel = (ls.index >= "1990") & (ls.index <= "2019-10-01")
    bt = np.polyfit(t[sel], np.log(ls.values[sel]), 1)
    zt = pd.Series(100 * (np.log(ls.values) - np.polyval(bt, t)), index=ls.index)
    ecm = []
    for name, g in [("gap from 1990-2019 average", z), ("gap from 1990-2019 trend", zt)]:
        x["lsg_l1"] = g.shift(1).reindex(x.index)
        r, cols, n = m.rls(x.loc[:"2019-10-01"], "gw", m.wage_X() + ["lsg_l1"], True, m.L("gw", cur=False) + m.L("exp1", cur=False))
        c = r.params["lsg_l1"]; se = float(np.sqrt(r.cov_params().loc["lsg_l1", "lsg_l1"]))
        term = c * g.shift(1).reindex(x.index)["2020-01-01":"2024-10-01"]
        ecm.append(dict(gap=name, coef=c, se=se, gap_2019Q4=g["2019-10-01"], gap_2024Q4=g["2024-10-01"],
                        term_2020_24_mean=term.mean(), term_2020_24_max=term.abs().max(), nobs=n))
    x.drop(columns="lsg_l1", inplace=True)
    return facts, era, qrt, pd.DataFrame(ecm).set_index("gap")


def part_b():
    pm = pd.read_csv(R + "oi/Policy_Milestones_-_State.csv")
    e = pm[pm.policy_description.str.contains("FPUC", na=False)]
    end = e.assign(date=pd.to_datetime(e.date)).groupby("statefips").date.min()
    end.index = end.index.map(FIPS)
    rows = []
    emp = pd.read_csv(R + "oi/Employment_-_State_-_Weekly.csv", na_values=".")
    emp["date"] = pd.to_datetime(dict(year=emp.year, month=emp.month, day=emp.day_endofweek))
    emp["st"] = emp.statefips.map(FIPS)
    w = emp[(emp.date >= "2021-04-01") & (emp.date <= "2021-09-30")]
    for col, lab in [("emp", "employment, all (share of Jan 2020)"), ("emp_wage_q1", "employment, lowest wage quarter (share of Jan 2020)")]:
        w_ = w.assign(**{col: pd.to_numeric(w[col], errors="coerce")})
        rows.append(dict(outcome=lab, data="weekly", **dict(zip(["estimate", "se", "n"], did(w_, col, end)))))
    ur = pd.DataFrame({s: fq(R + f"states/{s}UR.csv", "MS") for s in ST})
    ahe = pd.DataFrame({s: fq(R + f"states/AHE_{s}.csv", "MS") for s in ST})
    mo = pd.date_range("2021-04-01", "2021-09-01", freq="MS")
    endm = end.dt.to_period("M").dt.to_timestamp()   # month the supplement ended: counted as after only from the next month
    for df, lab in [(ur, "unemployment rate (points)"), (100 * np.log(ahe / ahe.loc["2021-04-01":"2021-05-01"].mean()), "average hourly earnings (% vs Apr-May 2021)")]:
        l = df.loc[mo].stack().rename("y").reset_index(); l.columns = ["date", "st", "y"]
        rows.append(dict(outcome=lab, data="monthly", **dict(zip(["estimate", "se", "n"], did(l, "y", endm, default_post="2021-06-01")))))
    return pd.DataFrame(rows), len(end)


def part_c(est):
    rows = {}
    for f in glob.glob(R + "bls_states/*.json"):
        for s in json.load(open(f))["Results"]["series"]:
            for o in s["data"]:
                if o["period"].startswith("M") and o["period"] != "M13":
                    rows.setdefault(s["seriesID"], {})[pd.Timestamp(f"{o['year']}-{o['period'][1:]}-01")] = float(o["value"])
    jo = pd.DataFrame({FIPS[int(k[9:11])]: pd.Series(v) for k, v in rows.items() if k.startswith("JTS")}).sort_index()
    un = pd.DataFrame({FIPS[int(k[5:7])]: pd.Series(v) for k, v in rows.items() if k.startswith("LAS")}).sort_index()
    vu = (jo * 1000 / un).resample("QS").mean()
    ahe = pd.DataFrame({s: fq(R + f"states/AHE_{s}.csv") for s in ST})
    wg = 100 * np.log(ahe).diff(4); vl = sum(vu.shift(k) for k in range(1, 5)) / 4
    out = []
    for lab, last in [("2009-2024 excl. 2020Q2-2021Q4", "2024-10-01"), ("2009-2019", "2019-10-01")]:
        qb = [t for t in wg.index if pd.Timestamp("2009-01-01") <= t <= pd.Timestamp(last)
              and not (pd.Timestamp("2020-04-01") <= t <= pd.Timestamp("2021-10-01"))]
        lb = pd.DataFrame({"w": wg.loc[qb].stack(), "v": vl.loc[qb].stack()}).dropna()
        lb.index.names = ["q", "st"]; lb = lb.reset_index()
        X = pd.concat([lb[["v"]], pd.get_dummies(lb.q.astype(str), prefix="t", dtype=float),
                       pd.get_dummies(lb.st, prefix="s", drop_first=True, dtype=float)], axis=1)
        r = sm.WLS(lb.w.values, X.values, weights=lb.st.map(POP).values).fit(cov_type="cluster", cov_kwds={"groups": lb.st.factorize()[0]})
        out.append(dict(estimate=f"state slope, {lab}", value=r.params[0], se=r.bse[0], n=len(lb)))
    lr = lambda Cw: Cw[5:9].sum() / Cw[9:13].sum()
    rng = np.random.default_rng(15); L = np.array([lr(D.draw(est, rng)["gw"]) for _ in range(5000)])
    out.append(dict(estimate="model long-run slope, point", value=lr(D.coefs(est)["gw"]), se=np.nan, n=np.nan))
    for p_ in (5, 50, 95):
        out.append(dict(estimate=f"model long-run slope, redraws p{p_}", value=np.percentile(L, p_), se=np.nan, n=np.nan))
    return pd.DataFrame(out).set_index("estimate"), vu


def part_d(d, sv, ok):
    fed = UM.fed_effect(d, sv[:3])
    rows = []
    for t in ("geometric", "hutchins"):
        base = F.run_variant(d.index, t, 1.0)
        for s_ in SCALES:
            du_ = {k: ok[0] * s_ * v for k, v in base.items()}
            for k in ["fed_pre2020", "fed_easing", "fed_hikes"]: du_[k] = fed[k]
            du_["pentup"] = ok[0] * P.effect(d.index, UM.PENT[1], UM.PENT[0], UM.PENT[2])
            u_ref = d.u[UM.REF] - du_["fed_pre2020"][UM.REF]
            y = (d.u - u_ref) - sum(du_.values())
            r, st = UM.covid_fit(y, d)
            e = r.resid.values
            rows.append(dict(timing=t, scale=s_, ssr=float(e @ e), rho=float(np.corrcoef(e[1:], e[:-1])[0, 1]), n=len(e), g0=r.params.s0))
    g = pd.DataFrame(rows)
    best = g.loc[g.ssr.idxmin()]
    neff = best.n * (1 - best.rho) / (1 + best.rho) if best.rho > 0 else best.n
    g["loglik"] = -neff / 2 * np.log(g.ssr)
    g["post"] = np.exp(g.loglik - g.loglik.max()); g["post"] /= g.post.sum()     # flat on log scale and on timing
    return g, neff


def scale_quantiles(g):
    s = g.groupby("scale").post.sum().sort_index()
    c = s.cumsum()
    return {q: float(s.index[np.searchsorted(c.values, q)]) for q in (0.05, 0.5, 0.95)}, s


def part_e(d, x, est, sv, ok, bev):
    C0 = D.coefs(est); rng = np.random.default_rng(3)
    cols = ["shortage", "energy_war", "worker_shortage", "biden", "trump", "pentup", "covid_other"]

    def tot(C):
        rr, _, _ = UM.run_once(d, x, C, UM.FISCAL, sv[:3], ok[0], bev[0].values, UM.RIDGE, None, None)
        yq = UM.yoy(UM.tidy(rr), x)
        return yq[[t.quarter == 4 and t.year >= 2021 for t in yq.index]].sum()[cols]
    out = {}
    for lab, grp in [("wage equation", ["gw"]), ("price equation", ["gp"]), ("expectations equations", ["exp10", "exp1"]),
                     ("all four", ["gw", "gp", "exp10", "exp1"])]:
        T = pd.DataFrame([tot({k: (v if k in grp else C0[k]) for k, v in D.draw(est, rng).items()}) for _ in range(150)])
        out[lab] = T.quantile(.95) - T.quantile(.05)
    return pd.DataFrame(out)


def main():
    d, x, est, point, du, vup, sv, ok, bev = UM.main()
    facts, era, qrt, ecm = part_a(x)
    ui, nend = part_b()
    cst, _ = part_c(est)
    g, neff = part_d(d, sv, ok)
    qs, s = scale_quantiles(g)
    wid = part_e(d, x, est, sv, ok, bev)
    pd.set_option("display.width", 220); pd.set_option("display.max_colwidth", 60)
    print("A. wages vs productivity\n", facts.round(1).to_string(), "\n", era.round(1).to_string())
    print("A. wage tracker 2019-12 to 2024-12, cumulative %, approximate (sum of December 12-month values)\n", qrt.round(1).to_string())
    print("A. catch-up term in the wage equation\n", ecm.round(3).to_string())
    print(f"B. early end of the $300 supplement ({nend} states)\n", ui.round(4).to_string())
    print("C. state wage curve\n", cst.round(3).to_string())
    print(f"D. relief size: n_eff {neff:.1f}; scale posterior p5 {qs[0.05]:.2f} p50 {qs[0.5]:.2f} p95 {qs[0.95]:.2f}; "
          f"P(scale >= {F.CBO_SCALE}) {float(s[s.index >= F.CBO_SCALE - 1e-9].sum()):.3f}; P(timing geometric) {g[g.timing == 'geometric'].post.sum():.2f}")
    print(g[g.scale.round(2).isin([0.25, 0.5, 0.71, 1.0, 1.41, 2.0, 2.83, 4.0])].round(3).to_string(index=False))
    print("E. 90% width of the 2021-24 total (log points), redrawing one equation at a time\n", wid.round(2).to_string())
    wid.round(3).to_csv(ROOT + "output/ext/e15_width_by_equation.csv")
    facts.round(3).to_csv(ROOT + "output/ext/e15_wages_productivity.csv")
    qrt.round(3).to_csv(ROOT + "output/ext/e15_wage_quartiles.csv")
    ecm.round(4).to_csv(ROOT + "output/ext/e15_catchup_term.csv")
    ui.round(5).to_csv(ROOT + "output/ext/e15_ui_early_end.csv", index=False)
    cst.round(4).to_csv(ROOT + "output/ext/e15_state_vu_wage_curve.csv")
    g.round(5).to_csv(ROOT + "output/ext/e15_relief_scale_likelihood.csv", index=False)


if __name__ == "__main__":
    main()
