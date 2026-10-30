"""Extension 16: the best estimate (extension 12) with two more pieces of evidence aimed at the wage equation, which
sets most of the width of the relief, COVID, worker-shortage and pent-up lines (the price equation sets the width of the
supply-chain and war lines; see the log of src/extensions/e15_wages_ui_ranges.py and REPORT.md section 7).

Evidence already in extension 12: W (2020-24 wage growth), P (category panel), X (cross-country relief).
New:
  I  2020-24 PCE inflation, yearly averages, for the wage and expectations equations only. Those equations are
     estimated on 1990-2019, so 2020-24 inflation is new data for them; the price equation is estimated on 1990-2024 and
     already uses it, so in this likelihood the price equation is held at its point estimate and its redraws are not
     weighted by I. W and I are scored jointly (10 yearly moments), covariance from 2,000 simulations with resampled
     residuals of all four equations, as in extension 12.
  S  the state wage curve (extension 15 C): 4-quarter wage growth on job openings per unemployed, state and quarter
     fixed effects, 0.58 (s.e. 0.46). Scored on each redraw's long-run wage slope, sum(V/U coefs) / sum(expectations
     coefs). This assumes the regional slope equals the national one; see extension 15's caveats.
Variants: W+P (= extension 12's best estimate, rerun to keep every quarter), W+P+I, W+P+I+S; each also with X.
Writes output/ext/e16_narrower.csv (2021-24 totals) and output/ext/e16_quarterly.csv (90% ranges each quarter);
log = stdout."""
import sys
sys.path.insert(0, __file__.rsplit("/src/", 1)[0] + "/src")
import numpy as np
import pandas as pd
import unified_model as UM, decompose as D, unified_data as U, fiscal_by_law as F, pentup as P, fed_svar as S

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
N0, N1 = 20000, 1000
PANEL = pd.read_csv(ROOT + "output/ext/e02_category_panel.csv").set_index("variant").loc["goods exposure"]
STATE = pd.read_csv(ROOT + "output/ext/e15_state_vu_wage_curve.csv", index_col=0).loc["state slope, 2009-2024 excl. 2020Q2-2021Q4"]
COLS = ["shortage", "energy_war", "worker_shortage", "biden", "trump", "pentup", "fed_net", "covid_other", "greed",
        "baseline", "fed_pre2020", "unexplained", "memo_labor_miss"]


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
        gw, gp = f["gw"][pos:], f["gp"][pos:]
        return np.r_[[gw[yrs == y].mean() for y in range(2020, 2025)], [gp[yrs == y].mean() for y in range(2020, 2025)]]

    obs = np.r_[[x.gw.values[pos:][yrs == y].mean() for y in range(2020, 2025)], [x.gp.values[pos:][yrs == y].mean() for y in range(2020, 2025)]]
    C0 = D.coefs(est); rng = np.random.default_rng(11); T = len(x) - pos
    res = {k: np.asarray(est[k][0].resid) for k in ["gw", "gp", "exp10", "exp1"]}
    sh = np.array([sim(C0, np.column_stack([rng.choice(res[k], T) for k in ["gw", "gp", "exp10", "exp1"]])) - sim(C0) for _ in range(2000)])
    Sw, Swi = np.linalg.inv(np.cov(sh[:, :5].T)), np.linalg.inv(np.cov(sh.T))
    i0 = list(est["gp"][0].params.index).index("shortage")
    gq = (x.shortage - x.shortage[:UM.REF].mean()).values
    lag = np.column_stack([np.r_[np.full(k, np.nan), gq[:len(gq) - k]] for k in range(5)])
    q4 = [j for j, t in enumerate(x.index) if t.month == 10 and 2021 <= t.year <= 2024]
    rng = np.random.default_rng(12)
    Cs = []; lw, lwi, lp, ls_ = (np.zeros(N0) for _ in range(4)); slope = np.zeros(N0)
    for i in range(N0):
        C = D.draw(est, rng); Cs.append(C)
        g = obs[:5] - sim(C)[:5]; lw[i] = -0.5 * g @ Sw @ g                          # W exactly as in extension 12
        Cm = dict(C, gp=C0["gp"]); g2 = obs - sim(Cm); lwi[i] = -0.5 * g2 @ Swi @ g2   # W + I, price equation at its point
        dq = pd.Series(lag @ C["gp"][i0:i0 + 5]).rolling(4).mean().values
        lp[i] = -0.5 * ((dq[q4].sum() - PANEL.effect_2021_24) / PANEL.effect_se) ** 2
        slope[i] = C["gw"][5:9].sum() / C["gw"][9:13].sum()
        ls_[i] = -0.5 * ((slope[i] - STATE.value) / STATE.se) ** 2
    ess = lambda l: float(np.exp(l - l.max()).sum() ** 2 / (np.exp(l - l.max()) ** 2).sum())
    print(f"stage 1 ESS of {N0}: W+P {ess(lw + lp):.0f}, W+I+P {ess(lwi + lp):.0f}, W+I+P+S {ess(lwi + lp + ls_):.0f}", flush=True)
    for nm, l in [("prior", np.zeros(N0)), ("W+P", lw + lp), ("W+I+P", lwi + lp), ("W+I+P+S", lwi + lp + ls_)]:
        p = np.exp(l - l.max()); p /= p.sum(); o = np.argsort(slope); c = np.cumsum(p[o])
        print(f"  long-run wage slope, {nm}: " + " ".join(f"p{int(100*q)} {slope[o][np.searchsorted(c, q)]:.2f}" for q in (.05, .5, .95)), flush=True)

    boots = S.bootstrap(md, z, N1, UM.SEED)
    variants = [(t, s_) for t in ("geometric", "hutchins") for s_ in (1.0, F.CBO_SCALE)]
    pi = U.nipa({"DPCERG"}).DPCERG; f = (100 * (pi / pi.shift(4) - 1)) / (100 * np.log(pi).diff(4))
    cmeta = pd.read_csv(ROOT + "output/combined_meta.csv", index_col=0).value
    mx, sx = float(cmeta.m_pce), float(cmeta.s_pce)
    out, qrows = {}, []
    for name, l in [("W+P", lw + lp), ("W+I+P", lwi + lp), ("W+I+P+S", lwi + lp + ls_)]:
        p = np.exp(l - l.max()); p /= p.sum()
        idx = rng.choice(N0, N1, p=p)
        tots, rel, paths = [], [], []
        for k, i in enumerate(idx):
            r = np.random.default_rng(1000 + k)
            ob = r.normal(*ok); bp = r.multivariate_normal(bev[0].values, bev[1].values)
            fv = variants[r.integers(4)]; rd = (UM.RIDGE, 0.5)[r.integers(2)]
            pv = ((P.M_POINT, P.M_ALT)[r.integers(2)], ("2023-07-01", "2024-10-01")[r.integers(2)], P.TREND)
            rr, _, _ = UM.run_once(d, x, Cs[i], fv, boots[k], ob, bp, rd, pv, r)
            yy = UM.tidy(rr)
            yq = UM.yoy(yy, x).mul(f.reindex(yy.index), axis=0)
            yq["fed_net"] = yq.fed_easing + yq.fed_hikes + yq.fed_pre2020
            paths.append(yq[COLS].values)
            tots.append(yq[[t.quarter == 4 and t.year >= 2021 for t in yq.index]].sum())
            rel.append(sum(yq.loc[[t for t in yq.index if t.year == y], ["trump", "biden"]].sum(axis=1).mean() for y in (2021, 2022)))
        tots = pd.DataFrame(tots); rel = np.array(rel); paths = np.stack(paths)
        tots["grp_supply"] = tots.shortage + tots.energy_war
        tots["grp_demand"] = tots.trump + tots.biden + tots.pentup + tots.fed_easing + tots.fed_hikes + tots.fed_pre2020
        for xname, wx in [("", np.ones(N1)), (" + X", np.exp(-0.5 * ((rel - mx) / sx) ** 2))]:
            wx = wx / wx.sum()

            def wq(v, q):
                o_ = np.argsort(v); c_ = np.cumsum(wx[o_]); return float(v[o_][min(np.searchsorted(c_, q), len(v) - 1)])
            key = name + xname; out[key] = {}
            for c in ["shortage", "energy_war", "worker_shortage", "biden", "trump", "pentup", "fed_net", "covid_other", "grp_supply", "grp_demand"]:
                v = tots[c].values
                out[key][(c, "p5")], out[key][(c, "p50")], out[key][(c, "p95")] = wq(v, .05), wq(v, .5), wq(v, .95)
            out[key][("P(supply > demand)", "share")] = float(wx @ (tots.grp_supply > tots.grp_demand))
            out[key][("ESS", "")] = float(1 / (wx ** 2).sum())
            for j, qq in enumerate(yy.index):
                for ci, c in enumerate(COLS):
                    v = paths[:, j, ci]
                    qrows.append(dict(variant=key, quarter=f"{qq.year}Q{qq.quarter}", cause=c, p5=wq(v, .05), p50=wq(v, .5), p95=wq(v, .95)))
        print(name, "done", flush=True)
    o = pd.DataFrame(out)
    o.round(3).to_csv(ROOT + "output/ext/e16_narrower.csv")
    pd.DataFrame(qrows).round(4).to_csv(ROOT + "output/ext/e16_quarterly.csv", index=False)
    pd.set_option("display.width", 250); print(o.round(2).to_string())


if __name__ == "__main__":
    main()
