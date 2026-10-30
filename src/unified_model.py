"""One model of the causes of US PCE inflation, 2020Q1-2024Q4. Method and sources: output/METHOD_UNIFIED.md.

Chain (every link is estimated here on public data or taken from a cited official source):
  relief laws (BEA payments x CBO multipliers)  --GDP-->  Okun (est. 1990-2019)  --+
  Fed policy surprises (Bauer-Swanson proxy SVAR)  ---------------------------------+--> unemployment
  everything else that moved unemployment (COVID shutdown, reopening, pent-up demand) +
  unemployment --(log V/U on unemployment, est. 1990-2019)--> job vacancies per unemployed (V/U)
                                                + V/U not explained by unemployment ("worker shortage")
  V/U, energy & food prices, supply chains (GSCPI), productivity --> Bernanke-Blanchard wage-price model on PCE.
Each cause's contribution = model inflation with all causes - model inflation with that cause removed. The model is
linear in every cause, so the contributions plus the starting point ("pre-existing inflation") add up exactly to the
model's inflation; the gap to actual PCE inflation is shown as "not explained by the model".
Run from project root:  python src/unified_model.py
"""
import functools
import sys
import numpy as np
import pandas as pd
import statsmodels.api as sm
sys.path.insert(0, "src")
import bb_model as m
import decompose as D
import unified_data as U
import fiscal_by_law as F
import fed_svar as S
import pentup as P

OUT = "output/"
START, REF = pd.Timestamp("2020-01-01"), pd.Timestamp("2019-10-01")
END = pd.Timestamp("2024-10-01")
WAR = (pd.Timestamp("2022-01-01"), pd.Timestamp("2023-01-01"))   # energy & food spike and fall-back (fig9 window)
FED_FROM = pd.Period("2005-01", "M")                               # surprises counted from here (IRF ~fades in 5 yrs)
NDRAW, SEED = 1000, 20261017
RIDGE = 0.05          # Sims-Zha regularization; band also uses 0.5 (results nearly identical, see METHOD)


# ---------------------------------------------------------------- data
def quarterly():
    d = U.load().assign(cpi=lambda x: x.pce, food_cpi=lambda x: x.pce_food, energy_cpi=lambda x: x.pce_energy)
    u, n = U.qmean(U.fred("UNRATE")), U.qmean(U.fred("NROU"))
    d["u"], d["nrou"] = u.reindex(d.index), n.reindex(d.index)
    d["gdpgap"] = (100 * (np.log(U.qmean(U.fred("GDPC1"))) - np.log(U.qmean(U.fred("GDPPOT"))))).reindex(d.index)
    return d.loc[:END]


def add_greed(x):
    """Greedflation regressor. s = unit profits / price per unit of real gross value added, nonfinancial corporate
    business, BEA NIPA Table 1.15 (A463RD / A455RD, data/raw/bea/NipaDataQ.txt). Price = unit costs / (1 - s), so with
    unit costs held fixed, the margin change alone moves the price by  margin_t = -400 x dlog(1 - s_t)  (annualized %).
    Part of that is caused by things already in the model (shortages, tight labor market, energy, food, wages), so we
    regress margin_t on those (current + 4 lags, 1990Q1-2024Q4) and keep the residual: margin increases that those
    causes do not explain. That residual ('greed') enters the price equation, current + 4 lags."""
    n = U.nipa({"A455RD", "A463RD"})
    sh = (n.A463RD / n.A455RD).reindex(x.index)
    x["margin"] = -400 * np.log(1 - sh).diff()
    Z = pd.concat({f"{v}_{i}": x[v].shift(i) for v in ["shortage", "vu", "grpe", "grpf", "gw"] for i in range(5)}, axis=1)
    df = pd.concat([x.margin, Z], axis=1).loc["1990-01-01":END].dropna()
    r = sm.OLS(df.margin, sm.add_constant(df.drop(columns="margin"))).fit()
    x["greed"] = (x.margin - r.predict(sm.add_constant(Z, has_constant="add"))).fillna(0.0)
    for i in range(1, 5): x[f"greed_l{i}"] = x.greed.shift(i)
    return x, r


def estimate_with_greed(x, est):
    X = m.price_X(D.PROD) + m.L("greed")
    est = dict(est)
    est["gp"] = m.rls(x, "gp", X, True, m.L("gp", cur=False) + m.L("gw"))
    return est


# ---------------------------------------------------------------- links
def okun(d):
    x = d.loc["1990-01-01":"2019-10-01", ["u", "nrou", "gdpgap"]].dropna()
    r = sm.OLS(x.u - x.nrou, sm.add_constant(x.gdpgap)).fit()
    return r.params["gdpgap"], r.bse["gdpgap"]


def beveridge(d):
    x = d.loc["1990-01-01":"2019-10-01", ["vu", "u"]].dropna()
    r = sm.OLS(np.log(x.vu), sm.add_constant(x.u)).fit()
    return r.params, r.cov_params()


@functools.lru_cache(None)
def surprises(instr=None):
    up = pd.read_excel(S.RAW + "mps/monetary-policy-surprises-data.xlsx", sheet_name="Monthly (update 2023)", header=0)
    up.index = pd.PeriodIndex([f"{int(y)}-{int(mo):02d}" for y, mo in zip(up.Year, up.Month)], freq="M")
    return up[instr or S.INSTR].astype(float)


@functools.lru_cache(None)
def fed_rates():
    p = pd.read_excel(U.RAW + "shadow/proxy-funds-rate-data.xlsx", sheet_name="Monthly", header=0)
    p.index = pd.to_datetime(p.Date).dt.to_period("M")
    return p["Proxy funds rate"].astype(float), p["Effective funds rate"].astype(float)


def episode_shocks(delta, w0, w1, psi, ridge):
    """Sims-Zha: policy shocks, allowed only in months w0..w1, chosen so the proxy funds rate moves by delta there
    (ridge-regularized least squares). After w1 no further shocks: the rate then follows the VAR's usual response."""
    N = len(delta)
    Psi = np.array([[psi[t - k] if t >= k else 0.0 for k in range(N)] for t in range(N)])
    P = Psi[w0:w1 + 1, w0:w1 + 1]
    e = np.zeros(N)
    e[w0:w1 + 1] = np.linalg.solve(P.T @ P + ridge * np.eye(len(P)), P.T @ delta[w0:w1 + 1])
    return e


def fed_effect(d, svar, ridge=RIDGE):
    """Change in unemployment caused by Fed policy, three pieces (SVAR in src/fed_svar.py):
    fed_easing  2020-21 rate cuts + QE: counterfactual proxy funds rate never below its 2019Q4 average, from the first
                month it fell below that level until the month it rose back above it (2020-01 to 2022-02).
    fed_hikes   2022-23 rate hikes: counterfactual proxy funds rate never above its 2019Q4 average, from the first month
                it rose above that level until the month the effective funds rate reached its peak (same SF Fed file).
    fed_pre2020 Bauer-Swanson policy surprises before 2020 (the only pre-2020 measure that is stable; see METHOD).
    The proxy funds rate (SF Fed) is built to capture QE and forward guidance, so 'easing' includes QE."""
    B, b, beta = svar
    R = S.irf(B, b, 240)
    psi, theta = R[:, S.VARS.index("pfr")], R[:, S.VARS.index("unemp")]
    pfr, effr = fed_rates()
    months = pd.period_range(FED_FROM, END.to_period("Q").asfreq("M", "end"), freq="M")
    N = len(months)
    Th = np.array([[theta[t - k] if 0 <= t - k < len(theta) else 0.0 for k in range(N)] for t in range(N)])
    pre = np.array([mo < pd.Period("2020-01", "M") for mo in months])
    e_pre = beta * surprises(S.INSTR).reindex(months).fillna(0.0).values * pre
    a = pfr.reindex(months).values
    ref = pfr.loc["2019-10":"2019-12"].mean()
    i20 = int(np.argmax(~pre))
    below = np.where((a < ref) & ~pre)[0]; w0, w1 = below.min(), below.max()
    e_ease = episode_shocks(np.maximum(a, ref) - a, w0, w1, psi, ridge)
    h0 = w1 + 1
    peak = months.get_loc(effr.loc[months[h0]:months[-1]].idxmax())
    e_hike = episode_shocks(np.minimum(a, ref) - a, h0, peak, psi, ridge)
    # the counterfactual shocks undo the actual policy, so the actual policy's effect is minus their effect
    out = pd.DataFrame({"fed_pre2020": Th @ e_pre, "fed_easing": -(Th @ e_ease), "fed_hikes": -(Th @ e_hike)}, index=months)
    q = out.groupby(out.index.asfreq("Q")).mean(); q.index = q.index.to_timestamp()
    return q.reindex(d.index).fillna(0.0)


def late_path(scenario):
    """Counterfactual effective funds rate minus actual (pp, monthly), for the 'did the Fed act too late?' test.
    'barnichon': the path in Barnichon, "What If? Monetary Policy in Hindsight", FRBSF Economic Letter 2022-28: "the
        federal funds rate rises immediately by about 1pp in March 2021 and then increases to close to 2% by early 2022";
        here 1.0% in 2021-03 rising linearly to 2.0% in 2022-02, then held at 2.0% until the actual rate passes it.
    'year_early': the actual 2022-23 hiking path (effective funds rate, SF Fed file) started 12 months earlier, from
        2021-03, until the actual rate reaches its peak."""
    pfr, effr = fed_rates()
    months = pd.period_range("2021-03", "2023-12", freq="M")
    a = effr.reindex(months)
    if scenario == "barnichon":
        t = pd.Series(np.nan, index=months)
        ramp = pd.period_range("2021-03", "2022-02", freq="M")
        t[ramp] = np.linspace(1.0, 2.0, len(ramp))
        t[months > ramp[-1]] = 2.0
    else:
        start = pd.Period("2022-03", "M")
        t = pd.Series(effr.reindex([m + 12 for m in months]).values, index=months)
        t[months + 12 > effr.loc[start:"2023-12"].idxmax()] = np.nan
    gap = (t - a).clip(lower=0).dropna()
    return gap[gap.cumsum() > 0].loc[: gap[gap > 0].index.max()]


def fed_late(d, x, C, svar, bev_params, scenario, ridge=RIDGE):
    """Effect on unemployment and on year-over-year PCE inflation of the counterfactual path in late_path(). The
    extra tightening is fed to the proxy funds rate with Sims-Zha shocks inside the window (as fed_effect)."""
    B, b, beta = svar
    R = S.irf(B, b, 240)
    psi, theta = R[:, S.VARS.index("pfr")], R[:, S.VARS.index("unemp")]
    months = pd.period_range("2020-01", END.to_period("Q").asfreq("M", "end"), freq="M")
    g = late_path(scenario).reindex(months).fillna(0.0).values
    w = np.where(g > 0)[0]
    e = episode_shocks(g, w.min(), w.max(), psi, ridge)
    N = len(months)
    Th = np.array([[theta[t - k] if 0 <= t - k < len(theta) else 0.0 for k in range(N)] for t in range(N)])
    du = pd.Series(Th @ e, index=months)
    du = du.groupby(du.index.asfreq("Q")).mean(); du.index = du.index.to_timestamp()
    du = du.reindex(x.index).fillna(0.0)
    full = {k: x[k].values.copy() for k in ["grpe", "grpf", "shortage", "gpty", "greed", "vu"]}
    base = simulate(C, x, full)
    cf = {k: v.copy() for k, v in full.items()}
    cf["vu"] = cf["vu"] * np.exp(bev_params[1] * du.values)
    dq = pd.Series(simulate(C, x, cf) - base, index=x.index[x.index.get_loc(START):])
    return du.loc[START:END], dq


# ---------------------------------------------------------------- inflation block (B&B on PCE, explicit paths)
def simulate(C, x, ex):
    """Same equations as decompose.simulate, with every exogenous path supplied in `ex`."""
    n, pos = len(x), x.index.get_loc(START)
    a = {c: x[c].values.copy() for c in ["gp", "gw", "exp1", "exp10", "catch_up"]}
    f = {k: a[k].copy() for k in ["gp", "gw", "exp1", "exp10"]}
    Cw, Cp, C10, C1 = C["gw"], C["gp"], C["exp10"], C["exp1"]
    for t in range(pos, n):
        f["gw"][t] = (Cw[0] + Cw[1:5] @ f["gw"][t-1:t-5:-1] + Cw[5:9] @ ex["vu"][t-1:t-5:-1]
                      + Cw[9:13] @ f["exp1"][t-1:t-5:-1] + Cw[13:17] @ a["catch_up"][t-1:t-5:-1] + Cw[17] * ex["gpty"][t-1])
        if len(Cw) > 18:                                   # kinked wage curve (bb_model.WAGE = "kink2024")
            f["gw"][t] += Cw[18:22] @ np.maximum(ex["vu"][t-1:t-5:-1] - m.TAU, 0.0)
        f["gp"][t] = (Cp[0] + Cp[1:5] @ f["gp"][t-1:t-5:-1] + Cp[5:10] @ f["gw"][t:t-5:-1]
                      + Cp[10:15] @ ex["grpe"][t:t-5:-1] + Cp[15:20] @ ex["grpf"][t:t-5:-1]
                      + Cp[20] * ex["gpty"][t] + Cp[21:26] @ ex["shortage"][t:t-5:-1]
                      + Cp[26:31] @ ex["greed"][t:t-5:-1])
        f["exp10"][t] = C10[0:5] @ f["gp"][t:t-5:-1] + C10[5:9] @ f["exp10"][t-1:t-5:-1]
        f["exp1"][t] = C1[0:4] @ f["exp1"][t-1:t-5:-1] + C1[4:9] @ f["exp10"][t:t-5:-1] + C1[9:14] @ f["gp"][t:t-5:-1]
    return f["gp"][pos:]


def causes_inflation(C, x, vu_parts, vu_ref):
    """Contribution of each cause to quarterly annualized PCE inflation, 2020Q1-end."""
    pos, pre = x.index.get_loc(START), x.index.get_loc(REF)
    full = {k: x[k].values.copy() for k in ["grpe", "grpf", "shortage", "gpty", "greed"]}
    full["vu"] = x.vu.values.copy()
    miss = vu_parts.get("labor_miss", np.zeros(len(x)))
    full["vu"][pos:] = vu_ref + sum(v[pos:] for k, v in vu_parts.items() if k != "labor_miss")
    ref = {"grpe": 0.0, "grpf": 0.0, "shortage": x.shortage.values[:pre + 1].mean(), "gpty": x.gpty.values[:pre + 1].mean(),
           "greed": x.greed.loc["1990-01-01":REF].mean()}
    t = x.index
    win = {"energy_covid": (t >= START) & (t < WAR[0]), "energy_war": (t >= WAR[0]) & (t <= WAR[1]), "energy_after": t > WAR[1]}

    def without(**kill):
        ex = {k: v.copy() for k, v in full.items()}
        for k, sel in kill.items():
            if k in win:
                ex["grpe"][win[k]] = 0.0; ex["grpf"][win[k]] = 0.0
            elif k in vu_parts:
                ex["vu"][pos:] -= vu_parts[k][pos:]
            elif k == "all":
                for c in ["grpe", "grpf", "shortage", "gpty", "greed"]: ex[c][pos:] = ref[c]
                ex["vu"][pos:] = vu_ref
            else:
                ex[k][pos:] = ref[k]
        return simulate(C, x, ex)

    base = simulate(C, x, full)
    causes = [k for k in vu_parts if k != "labor_miss"]
    out = {k: base - without(**{k: 1}) for k in list(win) + causes + ["shortage", "gpty", "greed"]}
    ex = {k: v.copy() for k, v in full.items()}; ex["vu"] = ex["vu"] + miss
    out["labor_miss"] = simulate(C, x, ex) - base       # part of "not explained": unemployment the causes miss
    out["baseline"] = without(all=1)
    out["unexplained"] = x.gp.values[pos:] - base
    return pd.DataFrame(out, index=x.index[pos:])


# ---------------------------------------------------------------- one full run
PENT = (P.M_POINT, "2023-07-01", P.TREND)     # pent-up demand: multiplier, end of spending, trend window
COVID_MODE = "stringency"
FIT_END = pd.Timestamp("2022-10-01")
FISCAL = ("geometric", 1.0)                    # relief timing and coverage (src/fiscal_by_law.py run_variant)                      # "stringency" = estimated (default); "residual" = old leftover


def covid_fit(y, d):
    """COVID shutdown & reopening effect on unemployment, estimated: y_t = g0 s_t + g1 s_t-1 + e_t, OLS,
    no constant (no lockdown, no effect). s = Oxford stringency index / 100 (data/raw/oxcgrt/), y = unemployment change
    since 2019Q4 not explained by relief, the Fed and pent-up demand. Fit 2020Q1-2022Q4, the quarters the tracker
    covers; 2023-24 values use the faded index (src/unified_data.py). e_t is NOT assigned to any cause: it is the
    labor-market part of 'not explained'."""
    st = d.stringency / 100
    X = pd.concat({"s0": st, "s1": st.shift(1).fillna(0.0)}, axis=1).loc[START:FIT_END]
    r = sm.OLS(y.loc[START:FIT_END], X).fit()
    return r, st


def run_once(d, x, C, fiscal_variant, svar, ok_beta, bev_params, ridge=RIDGE, pent=None, rng=None):
    idx = d.index
    eff = F.run_variant(idx, *fiscal_variant)                          # % of potential GDP
    du = {k: ok_beta * v for k, v in eff.items()}
    fed = fed_effect(d, svar, ridge)
    for k in ["fed_pre2020", "fed_easing", "fed_hikes"]: du[k] = fed[k]
    m_, end_, tr_ = pent or PENT
    du["pentup"] = ok_beta * P.effect(idx, end_, m_, tr_)
    u_ref = d.u[REF] - du["fed_pre2020"][REF]
    y = (d.u - u_ref) - sum(du.values())
    if COVID_MODE == "residual":
        du["covid_other"] = y
    else:
        r, st = covid_fit(y, d)
        g = r.params.values if rng is None else rng.multivariate_normal(r.params.values, r.cov_params().values)
        du["covid_other"] = (g[0] * st + g[1] * st.shift(1).fillna(0.0)).where(d.index >= START, 0.0)
        du["labor_miss"] = (y - du["covid_other"]).where(d.index >= START, 0.0)
    a, b = bev_params
    e = np.log(d.vu) - (a + b * d.u)
    logvu_ref = np.log(d.vu[REF]) - b * du["fed_pre2020"][REF]
    parts_log = {k: b * v for k, v in du.items()}
    parts_log["worker_shortage"] = e - e[REF]
    lvu = np.log(d.vu)
    vu_ref = np.exp(logvu_ref)
    # exact split of the level change: logarithmic-mean weights (LMDI)
    dl = lvu - logvu_ref
    L = np.where(np.abs(dl) > 1e-9, (d.vu - vu_ref) / dl.where(np.abs(dl) > 1e-9, 1), d.vu)
    vu_parts = {k: pd.Series(L * v, index=d.index).fillna(0.0).reindex(x.index).fillna(0.0).to_numpy(copy=True) for k, v in parts_log.items()}
    for k in vu_parts: vu_parts[k][: x.index.get_loc(START)] = 0.0
    res = causes_inflation(C, x, vu_parts, vu_ref)
    return res, pd.DataFrame(du).loc[START:END], pd.DataFrame({k: v for k, v in vu_parts.items()}, index=x.index).loc[START:]


def main():
    d = quarterly()
    x = m.build(d); D.PROD_LAG = 0
    x, greed_fit = add_greed(x)
    est = estimate_with_greed(x, m.estimate(x, D.PROD))
    C = D.coefs(est)
    md, z = S.data()
    B, b, Ures, sidx, Fstat, beta = S.estimate(md, z)
    ok_beta, ok_se = okun(d)
    bev, bev_cov = beveridge(d)
    g = est["gp"][0].params.filter(like="greed")
    print(f"Okun: {ok_beta:.3f} (se {ok_se:.3f});  log V/U on u: {bev['u']:.3f};  SVAR first-stage F {Fstat:.1f};  "
          f"margin purge R2 {greed_fit.rsquared:.2f};  price-eq greed coefs {g.round(3).to_dict()} sum {g.sum():.3f}")
    point, du, vup = run_once(d, x, C, FISCAL, (B, b, beta), ok_beta, bev.values, RIDGE)
    if COVID_MODE != "residual":
        y = du["covid_other"] + du["labor_miss"]
        r, _ = covid_fit(y.reindex(d.index).fillna(0.0), d)
        yy = y.loc[START:FIT_END]
        rc = 1 - (r.resid ** 2).sum() / ((yy - yy.mean()) ** 2).sum()
        print(f"COVID on unemployment: g0 {r.params.s0:.2f} (se {r.bse.s0:.2f}), g1 {r.params.s1:.2f} (se {r.bse.s1:.2f}), "
              f"R2 {r.rsquared:.2f} (uncentered; centered {rc:.2f}); labor-market miss max |{du['labor_miss'].abs().max():.2f}| pts")
    # variant: every margin change counts as greed (no purge), re-estimated; point estimate only
    x2 = x.copy(); x2["greed"] = x2.margin.fillna(0.0)
    for i in range(1, 5): x2[f"greed_l{i}"] = x2.greed.shift(i)
    est2 = estimate_with_greed(x2, m.estimate(x2, D.PROD))
    g2 = est2["gp"][0].params.filter(like="greed")
    print(f"unpurged margin: price-eq coef sum {g2.sum():.3f}")
    p2, _, _ = run_once(d, x2, D.coefs(est2), FISCAL, (B, b, beta), ok_beta, bev.values, RIDGE)
    point["greed_unpurged"] = p2["greed"]
    print("fiscal timing fit to CBO (rmse, lambda, scale):", F.fit_cbo_timing(d.index))
    return d, x, est, point, du, vup, (B, b, beta, Ures, sidx, md, z), (ok_beta, ok_se), (bev, bev_cov)


LABELS = {  # additive lines: the causes sum to the model estimate; with "unexplained" they sum to actual inflation
    "trump": "Relief signed/ordered by Trump (FFCRA, CARES, Dec-2020 CRRSA; paid before Mar 2021)",
    "biden": "Relief signed/ordered by Biden (American Rescue Plan, loan-pause extensions; paid from Mar 2021)",
    "fed_easing": "Fed 2020-21 rate cuts + QE",
    "fed_hikes": "Fed 2022-23 rate hikes",
    "fed_pre2020": "Fed policy surprises before 2020",
    "energy_war": "War in Ukraine: energy & food price spike and fall-back, 2022Q1-2023Q1",
    "energy_after": "Energy & food shocks after 2023Q1 (OPEC+ 2023 cuts, bird flu, drought, ...), not tied to a cause",
    "shortage": "COVID supply chains (NY Fed GSCPI)",
    "greed": "Greedflation: profit-margin rises not explained by shortages, labor market or costs",
    "pentup": "Pent-up demand: spending of money households could not spend in the lockdowns (relief money excluded)",
    "covid_other": "COVID shutdown & reopening (estimated from lockdown stringency) and the energy & food price crash "
                   "and rebound of 2020Q1-2021Q4",
    "worker_shortage": "Worker shortage (job openings beyond what unemployment implies)",
    "gpty": "Productivity",
    "baseline": "Pre-existing inflation (where the economy stood at end-2019)",
    "unexplained": "Not explained by the model",
}
MEMO = {  # parts of the trump/biden lines, reported separately (NOT added again)
    "memo_student_loans": "Student-loan payment pause (inside the Trump and Biden lines)",
    "memo_rental_assist": "Emergency rental & homeowner assistance (inside the Trump and Biden lines)",
    "memo_energy_covid": "Energy & food price crash and rebound, 2020Q1-2021Q4 (inside the COVID line)",
    "memo_greed_unpurged": "Greedflation if EVERY margin change counts as greed (raw margin series; replaces the greed line)",
    "memo_labor_miss": "Unemployment the causes do not explain, its effect on inflation (inside 'not explained')",
}


def tidy(res):
    r = res.copy()
    # energy & food relative-price swings are inputs, not causes: assign them to the cause active at the time
    r["memo_energy_covid"] = r.pop("energy_covid")
    r["covid_other"] = r["covid_other"] + r["memo_energy_covid"]
    r["memo_greed_unpurged"] = r.get("greed_unpurged", np.nan)
    r["memo_labor_miss"] = r.get("labor_miss", 0.0)
    for g in F.GROUPS:
        r["memo_" + g] = r[f"trump_{g}"] + r[f"biden_{g}"]
    for nm in ["trump", "biden"]:
        r[nm] = r[nm] + sum(r[f"{nm}_{g}"] for g in F.GROUPS)
    return r[list(LABELS) + list(MEMO)]


def run_bands(ndraw=NDRAW, seed=SEED):
    d, x, est, point, du, vup, sv, ok, bev = main()
    B, b, beta, Ures, sidx, md, z = sv
    rng = np.random.default_rng(seed)
    boots = S.bootstrap(md, z, ndraw, seed)
    variants = [(t, s_) for t in ("geometric", "hutchins") for s_ in (1.0, F.CBO_SCALE)]
    draws, params = [], []
    i0 = list(est["gp"][0].params.index).index("shortage")
    gq = (x.shortage - x.shortage[:REF].mean()).values
    lagged = np.column_stack([np.r_[np.full(k, np.nan), gq[:len(gq) - k]] for k in range(5)])
    q4 = [j for j, t in enumerate(x.index) if t.month == 10 and 2021 <= t.year <= 2024]
    for i in range(ndraw):
        C = D.draw(est, rng)
        ob = rng.normal(ok[0], ok[1])
        bp = rng.multivariate_normal(bev[0].values, bev[1].values)
        fv = variants[rng.integers(len(variants))]
        rd = (RIDGE, 0.5)[rng.integers(2)]
        pv = ((P.M_POINT, P.M_ALT)[rng.integers(2)], ("2023-07-01", "2024-10-01")[rng.integers(2)], P.TREND)
        res, _, _ = run_once(d, x, C, fv, boots[i], ob, bp, rd, pv, rng)
        draws.append(tidy(res).values)
        dq = pd.Series(lagged @ C["gp"][i0:i0 + 5]).rolling(4).mean().values      # direct GSCPI term, y/y (log pts)
        vc = [j for j, c in enumerate(est["gw"][0].params.index) if c.startswith("vu_")]
        params.append(dict(gscpi_direct_2021_24=float(dq[q4].sum()), gscpi_coef_sum=float(C["gp"][i0:i0 + 5].sum()),
                           wage_vu_sum=float(C["gw"][vc].sum()), okun=ob, fiscal_timing=fv[0], fiscal_scale=fv[1],
                           ridge=rd, pent_m=pv[0], pent_end=pv[1]))
    pd.DataFrame(params).to_csv(OUT + "unified_draw_params.csv", index=False)
    return d, x, tidy(point), np.stack(draws), du, vup, sv


def yoy(q, x):
    """Year-over-year contribution = mean of the last four annualized quarterly contributions. 2019 quarters: every
    cause 0 and 'baseline' = actual inflation, as in the earlier figures."""
    pre = x.loc["2019-01-01":"2019-10-01"]
    full = pd.concat([pd.DataFrame(0.0, index=pre.index, columns=q.columns).assign(baseline=pre.gp.values), q])
    return full.rolling(4).mean().loc[START:]


def save(d, x, point, draws, du):
    idx = point.index
    yp = yoy(point, x)
    yd = np.stack([yoy(pd.DataFrame(dr, index=idx, columns=point.columns), x).values for dr in draws])
    # The model works in log changes (400 x dlog). Official inflation is the percent change. Every contribution is
    # scaled by the same ratio (percent change / log change of the PCE price index, BEA DPCERG) in each quarter, so
    # shares are unchanged and all lines together equal the official year-over-year percent change.
    pi = U.nipa({"DPCERG"}).DPCERG
    logc, pctc = 100 * np.log(pi).diff(4), 100 * (pi / pi.shift(4) - 1)
    f = (pctc / logc).reindex(yp.index)
    yp = yp.mul(f, axis=0); yd = yd * f.values[None, :, None]
    np.save(OUT + "unified_draws.npy", yd)          # draws x quarters x lines (official % change), for group bands
    pd.Series(point.columns).to_csv(OUT + "unified_draws_columns.csv", index=False, header=["line"])
    out = yp.copy()
    for j, c in enumerate(point.columns):
        out[c + "_lo"], out[c + "_hi"] = np.percentile(yd[:, :, j], 5, 0), np.percentile(yd[:, :, j], 95, 0)
    out["model_total"] = yp[[c for c in LABELS if c != "unexplained"]].sum(axis=1)
    cols = list(point.columns); keep = [cols.index(c) for c in LABELS if c != "unexplained"]
    tot = yd[:, :, keep].sum(axis=2)
    out["model_total_lo"], out["model_total_hi"] = np.percentile(tot, 5, 0), np.percentile(tot, 95, 0)
    for nm, grp in {"fed_all": ["fed_pre2020", "fed_easing", "fed_hikes"], "other_unexplained": ["gpty", "unexplained", "energy_after"]}.items():
        g = yd[:, :, [cols.index(c) for c in grp]].sum(axis=2)
        out[nm] = yp[grp].sum(axis=1); out[nm + "_lo"], out[nm + "_hi"] = np.percentile(g, 5, 0), np.percentile(g, 95, 0)
    out["sum_all_lines"] = yp[list(LABELS)].sum(axis=1)
    n = U.nipa({"A455RD", "A463RD"}); sh = n.A463RD / n.A455RD
    out["acct_profit_share_pct"] = (100 * sh).reindex(out.index)
    out["acct_margin_effect_on_corp_prices_yoy"] = (-100 * np.log(1 - sh).diff(4)).reindex(out.index)
    out["acct_corp_price_yoy"] = (100 * np.log(n.A455RD).diff(4)).reindex(out.index)
    out["actual_pce_yoy"] = pctc.reindex(out.index)                    # official: percent change from a year earlier
    out["actual_pce_logchange"] = logc.reindex(out.index)
    out["log_to_pct_factor"] = f
    out["model_bb_quarterly_actual"] = x.gp.rolling(4).mean().reindex(out.index)
    # 2021-2024 total: the four Q4-over-Q4 rates added up (official percent change), with 90% ranges
    q4 = [i for i, t in enumerate(yp.index) if t.quarter == 4 and t.year >= 2021]
    grp = {"model_total": [c for c in LABELS if c != "unexplained"], "fed_all": ["fed_pre2020", "fed_easing", "fed_hikes"],
           "other_unexplained": ["gpty", "unexplained", "energy_after"], "relief_all": ["trump", "biden"]}
    cum = {}
    for c in list(point.columns) + list(grp):
        js = [cols.index(k) for k in grp.get(c, [c])]
        dr = yd[:, q4][:, :, js].sum(axis=(1, 2))
        cum[c] = dict(total=yp.iloc[q4][grp.get(c, [c])].sum().sum(), lo=np.percentile(dr, 5), hi=np.percentile(dr, 95))
    cum["actual"] = dict(total=pctc.reindex(yp.index).iloc[q4].sum(), lo=np.nan, hi=np.nan)
    pd.DataFrame(cum).T.round(3).to_csv(OUT + "unified_cumulative_2021_2024.csv")
    out.index = [f"{t.year}Q{t.quarter}" for t in out.index]
    out.round(3).to_csv(OUT + "unified_causes_quarterly.csv")
    du.index = [f"{t.year}Q{t.quarter}" for t in du.index]
    du.round(3).to_csv(OUT + "unified_unemployment_parts.csv")
    return out


if __name__ == "__main__":
    d, x, point, draws, du, vup, sv = run_bands()
    out = save(d, x, point, draws, du)
    pd.set_option("display.width", 250)
    print(out[list(LABELS) + list(MEMO) + ["sum_all_lines", "actual_pce_yoy"]].iloc[::2].round(2).T.to_string())
