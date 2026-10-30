"""Extension 12: one estimate that uses all the independent evidence at once (sequential Bayesian updating by
sampling-importance-resampling; prior = the model's own sampling distributions, as in src/unified_model.run_bands).

Evidence, each data the model's estimates did not use:
  W  wage growth 2020-2024 (employment cost index, yearly averages): the wage equation is estimated on 1990-2019 only.
     Likelihood of each coefficient draw = normal, covariance of the five yearly moments from 2,000 simulations with
     resampled equation residuals (as in src/uncertainty/condition_on_2020_24.py).
  P  the category panel (extension 2): supply-chain pressure's direct effect on PCE inflation, 2021-24, 1.49 (s.e. 0.63)
     points, measured as goods relative to services. Likelihood = normal, on the draw's direct GSCPI term.
  X  the cross-country relief estimate (src/cross_country_relief.py, core CPI 2021-22): likelihood = normal on the
     draw's relief total measured the same way (src/combine_outside_evidence.py).
Steps: 20,000 draws of the wage-price coefficients -> weights W x P -> resample 1,000 -> full model run for each, with
the other uncertain inputs drawn as in run_bands -> weights X -> ranges. Each piece of evidence is also applied alone.
Not used: actual inflation 2020-24 (the price equation is estimated on it), and the out-of-sample and state-level
results (reported separately).
Writes output/ext/e12_all_evidence.csv; log = stdout."""
import sys
sys.path.insert(0, __file__.rsplit("/src/", 1)[0] + "/src")
import numpy as np
import pandas as pd
import unified_model as UM, bb_model as m, decompose as D, unified_data as U, fiscal_by_law as F, pentup as P, fed_svar as S

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
N0, N1 = 20000, 1000
PANEL = pd.read_csv(ROOT + "output/ext/e02_category_panel.csv").set_index("variant").loc["goods exposure"]


def main():
    d, x, est, point, du, vup, sv, ok, bev = UM.main()
    B, b, beta, Ures, sidx, md, z = sv
    pos = x.index.get_loc(UM.START)
    ex = {k: x[k].values.copy() for k in ["grpe", "grpf", "shortage", "gpty", "greed", "vu"]}
    yrs = x.index[pos:].year

    def sim(C, e=None):
        n = len(x); a = {c: x[c].values.copy() for c in ["gp", "gw", "exp1", "exp10", "catch_up"]}
        f = {k: a[k].copy() for k in ["gp", "gw", "exp1", "exp10"]}
        Cw, Cp, C10, C1 = C["gw"], C["gp"], C["exp10"], C["exp1"]
        for t in range(pos, n):
            s = e[t - pos] if e is not None else np.zeros(4)
            f["gw"][t] = (Cw[0] + Cw[1:5] @ f["gw"][t-1:t-5:-1] + Cw[5:9] @ ex["vu"][t-1:t-5:-1] + Cw[9:13] @ f["exp1"][t-1:t-5:-1]
                          + Cw[13:17] @ a["catch_up"][t-1:t-5:-1] + Cw[17] * ex["gpty"][t-1]) + s[0]
            f["gp"][t] = (Cp[0] + Cp[1:5] @ f["gp"][t-1:t-5:-1] + Cp[5:10] @ f["gw"][t:t-5:-1] + Cp[10:15] @ ex["grpe"][t:t-5:-1]
                          + Cp[15:20] @ ex["grpf"][t:t-5:-1] + Cp[20] * ex["gpty"][t] + Cp[21:26] @ ex["shortage"][t:t-5:-1]
                          + Cp[26:31] @ ex["greed"][t:t-5:-1]) + s[1]
            f["exp10"][t] = C10[0:5] @ f["gp"][t:t-5:-1] + C10[5:9] @ f["exp10"][t-1:t-5:-1] + s[2]
            f["exp1"][t] = C1[0:4] @ f["exp1"][t-1:t-5:-1] + C1[4:9] @ f["exp10"][t:t-5:-1] + C1[9:14] @ f["gp"][t:t-5:-1] + s[3]
        gw = f["gw"][pos:]
        return np.array([gw[yrs == y].mean() for y in range(2020, 2025)])

    obs = np.array([x.gw.values[pos:][yrs == y].mean() for y in range(2020, 2025)])
    C0 = D.coefs(est); rng = np.random.default_rng(11); T = len(x) - pos
    res = {k: np.asarray(est[k][0].resid) for k in ["gw", "gp", "exp10", "exp1"]}
    sh = [sim(C0, np.column_stack([rng.choice(res[k], T) for k in ["gw", "gp", "exp10", "exp1"]])) - sim(C0) for _ in range(2000)]
    Si = np.linalg.inv(np.cov(np.array(sh).T))
    i0 = list(est["gp"][0].params.index).index("shortage")
    gq = (x.shortage - x.shortage[:UM.REF].mean()).values
    lag = np.column_stack([np.r_[np.full(k, np.nan), gq[:len(gq) - k]] for k in range(5)])
    q4 = [j for j, t in enumerate(x.index) if t.month == 10 and 2021 <= t.year <= 2024]
    rng = np.random.default_rng(12)
    Cs, lw, lp = [], np.zeros(N0), np.zeros(N0)
    for i in range(N0):
        C = D.draw(est, rng); Cs.append(C)
        g = obs - sim(C); lw[i] = -0.5 * g @ Si @ g
        dq = pd.Series(lag @ C["gp"][i0:i0 + 5]).rolling(4).mean().values
        lp[i] = -0.5 * ((dq[q4].sum() - PANEL.effect_2021_24) / PANEL.effect_se) ** 2
    ess = lambda l: float(np.exp(l - l.max()).sum() ** 2 / (np.exp(l - l.max()) ** 2).sum())
    print(f"stage 1: ESS wages {ess(lw):.0f}, panel {ess(lp):.0f}, both {ess(lw + lp):.0f} of {N0}", flush=True)

    boots = S.bootstrap(md, z, N1, UM.SEED)
    variants = [(t, s_) for t in ("geometric", "hutchins") for s_ in (1.0, F.CBO_SCALE)]
    pi = U.nipa({"DPCERG"}).DPCERG; f = (100 * (pi / pi.shift(4) - 1)) / (100 * np.log(pi).diff(4))
    cmeta = pd.read_csv(ROOT + "output/combined_meta.csv", index_col=0).value
    mx, sx = float(cmeta.m_pce), float(cmeta.s_pce)
    out = {}
    for name, l in [("model alone", np.zeros(N0)), ("+ wages", lw), ("+ category panel", lp), ("+ wages + panel", lw + lp)]:
        p = np.exp(l - l.max()); p /= p.sum()
        idx = rng.choice(N0, N1, p=p)
        tots, rel = [], []
        for k, i in enumerate(idx):
            r = np.random.default_rng(1000 + k)
            ob = r.normal(*ok); bp = r.multivariate_normal(bev[0].values, bev[1].values)
            fv = variants[r.integers(4)]; rd = (UM.RIDGE, 0.5)[r.integers(2)]
            pv = ((P.M_POINT, P.M_ALT)[r.integers(2)], ("2023-07-01", "2024-10-01")[r.integers(2)], P.TREND)
            rr, _, _ = UM.run_once(d, x, Cs[i], fv, boots[k], ob, bp, rd, pv, r)
            yy = UM.tidy(rr)
            yq = UM.yoy(yy, x).mul(f.reindex(yy.index), axis=0)
            tots.append(yq[[t.quarter == 4 and t.year >= 2021 for t in yq.index]].sum())
            ann = sum(yq.loc[[t for t in yq.index if t.year == y], ["trump", "biden"]].sum(axis=1).mean() for y in (2021, 2022))
            rel.append(ann)
        tots = pd.DataFrame(tots); rel = np.array(rel)
        tots["relief_all"] = tots.trump + tots.biden
        tots["fed_net"] = tots.fed_easing + tots.fed_hikes + tots.fed_pre2020
        tots["grp_supply"] = tots.shortage + tots.energy_war
        tots["grp_demand"] = tots.trump + tots.biden + tots.pentup + tots.fed_easing + tots.fed_hikes + tots.fed_pre2020
        tots["grp_labor"] = tots.grp_demand + tots.covid_other + tots.worker_shortage
        for xname, wx in [("", np.ones(N1)), (" + cross-country", np.exp(-0.5 * ((rel - mx) / sx) ** 2))]:
            wx = wx / wx.sum()

            def wq(v, q):
                o_ = np.argsort(v); c_ = np.cumsum(wx[o_]); return float(v[o_][np.searchsorted(c_, q)])
            key = name + xname
            out[key] = {}
            for c in ["shortage", "covid_other", "worker_shortage", "trump", "biden", "relief_all", "pentup", "fed_net", "energy_war",
                      "grp_supply", "grp_demand", "grp_labor"]:
                v = tots[c].values
                out[key][(c, "p5")], out[key][(c, "p50")], out[key][(c, "p95")] = wq(v, .05), wq(v, .5), wq(v, .95)
            out[key][("P(supply chains+war+worker > demand)", "share")] = float(wx @ (tots.grp_supply + tots.worker_shortage > tots.grp_demand))
            out[key][("P(supply chains+war > demand)", "share")] = float(wx @ (tots.grp_supply > tots.grp_demand))
            out[key][("ESS", "")] = float(1 / (wx ** 2).sum())
        print(name, "done", flush=True)
    o = pd.DataFrame(out)
    o.round(3).to_csv(ROOT + "output/ext/e12_all_evidence.csv")
    pd.set_option("display.width", 250); print(o.round(2).to_string())


if __name__ == "__main__":
    main()
