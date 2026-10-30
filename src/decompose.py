"""Historical decomposition (port of the 'HISTORICAL DECOMPOSITION' block of bl_be_us.R)
plus parameter-uncertainty bands by Monte Carlo over the estimated coefficients."""
import numpy as np, pandas as pd
import bb_model as m

PROD = "gpty"  # price-equation productivity term is CURRENT productivity (matches the published coefficient file)
PROD_LAG = 0   # set to 1 to reproduce the authors' R script (lagged productivity in the price equation)
START = pd.Timestamp("2020-01-01")
SCEN = ["base", "energy", "food", "short", "prod", "vu", "init"]


def coefs(est):
    return {k: est[k][0].params.values.copy() for k in ["gw", "gp", "exp10", "exp1"]}


def simulate(C, x, scen):
    """Simulate the 4-equation model from START to the end of the sample.
    scen: which exogenous series are set to their pre-2020 reference value."""
    n, pos = len(x), x.index.get_loc(START)
    a = {c: x[c].values.copy() for c in ["gp", "gw", "exp1", "exp10", "grpe", "grpf", "vu", "shortage", "gpty", "catch_up"]}
    pre = x.index.get_loc(pd.Timestamp("2019-10-01"))
    ex = {k: a[k].copy() for k in ["grpe", "grpf", "vu", "shortage", "gpty"]}
    kill = {"energy": ["energy"], "food": ["food"], "short": ["short"], "prod": ["prod"], "vu": ["vu"],
            "init": ["energy", "food", "short", "prod", "vu"], "base": []}[scen]
    if "energy" in kill: ex["grpe"][pos:] = 0.0
    if "food" in kill: ex["grpf"][pos:] = 0.0
    if "short" in kill: ex["shortage"][pos:] = a["shortage"][:pre + 1].mean()
    if "prod" in kill: ex["gpty"][pos:] = a["gpty"][:pre + 1].mean()
    if "vu" in kill: ex["vu"][pos:] = a["vu"][pre]
    f = {k: a[k].copy() for k in ["gp", "gw", "exp1", "exp10"]}  # history = actual
    Cw, Cp, C10, C1 = C["gw"], C["gp"], C["exp10"], C["exp1"]
    for t in range(pos, n):
        f["gw"][t] = (Cw[0] + Cw[1:5] @ f["gw"][t-1:t-5:-1] + Cw[5:9] @ ex["vu"][t-1:t-5:-1]
                      + Cw[9:13] @ f["exp1"][t-1:t-5:-1] + Cw[13:17] @ a["catch_up"][t-1:t-5:-1] + Cw[17] * ex["gpty"][t-1])
        f["gp"][t] = (Cp[0] + Cp[1:5] @ f["gp"][t-1:t-5:-1] + Cp[5:10] @ f["gw"][t:t-5:-1]
                      + Cp[10:15] @ ex["grpe"][t:t-5:-1] + Cp[15:20] @ ex["grpf"][t:t-5:-1]
                      + Cp[20] * ex["gpty"][t - PROD_LAG] + Cp[21:26] @ ex["shortage"][t:t-5:-1])
        f["exp10"][t] = C10[0:5] @ f["gp"][t:t-5:-1] + C10[5:9] @ f["exp10"][t-1:t-5:-1]
        f["exp1"][t] = C1[0:4] @ f["exp1"][t-1:t-5:-1] + C1[4:9] @ f["exp10"][t:t-5:-1] + C1[9:14] @ f["gp"][t:t-5:-1]
    return f["gp"][pos:]


def decompose(C, x):
    sim = {s: simulate(C, x, s) for s in SCEN}
    actual = x["gp"].values[x.index.get_loc(START):]
    out = pd.DataFrame(index=x.index[x.index >= START])
    out["actual_cpi"] = actual
    for s, lab in [("energy", "energy"), ("food", "food"), ("short", "shortages"), ("vu", "labor_tightness"), ("prod", "productivity")]:
        out[lab] = sim["base"] - sim[s]
    out["baseline_pre2020"] = sim["init"]
    out["unexplained"] = actual - sim["base"]
    return out


def draw(est, rng):
    out = {}
    for k in ["gw", "gp", "exp10", "exp1"]:
        r = est[k][0]
        S = r.cov_params().values
        w, V = np.linalg.eigh((S + S.T) / 2)
        w = np.clip(w, 0, None)  # restricted cov is singular along the restriction direction
        out[k] = r.params.values + V @ (np.sqrt(w) * rng.standard_normal(len(w)))
    return out


def run(x, est, ndraw=2000, seed=20261016):
    point = decompose(coefs(est), x)
    rng = np.random.default_rng(seed)
    cols = [c for c in point.columns if c != "actual_cpi"]
    arr = np.empty((ndraw, len(point), len(cols)))
    for i in range(ndraw):
        arr[i] = decompose(draw(est, rng), x)[cols].values
    return point, cols, arr
