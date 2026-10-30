"""Test 1 of narrowing the ranges: weight wage-price coefficient draws by how well they reproduce observed 2020-24 wage (and price) growth (sampling-importance weights). Result: modest narrowing of COVID, none for supply chains; low effective sample. Not adopted."""
import sys; sys.path.insert(0, "src")  # run from project root
import numpy as np, pandas as pd
import unified_model as UM, decompose as D, unified_data as U
d, x, est, point, du, vup, sv, ok, bev = UM.main()
B, b, beta = sv[:3]
pos = x.index.get_loc(UM.START)
ex = {k: x[k].values.copy() for k in ["grpe", "grpf", "shortage", "gpty", "greed", "vu"]}

def sim2(C, shocks=None):
    n = len(x)
    a = {c: x[c].values.copy() for c in ["gp", "gw", "exp1", "exp10", "catch_up"]}
    f = {k: a[k].copy() for k in ["gp", "gw", "exp1", "exp10"]}
    Cw, Cp, C10, C1 = C["gw"], C["gp"], C["exp10"], C["exp1"]
    for t in range(pos, n):
        e = shocks[t - pos] if shocks is not None else np.zeros(4)
        f["gw"][t] = (Cw[0] + Cw[1:5] @ f["gw"][t-1:t-5:-1] + Cw[5:9] @ ex["vu"][t-1:t-5:-1] + Cw[9:13] @ f["exp1"][t-1:t-5:-1]
                      + Cw[13:17] @ a["catch_up"][t-1:t-5:-1] + Cw[17] * ex["gpty"][t-1]) + e[0]
        f["gp"][t] = (Cp[0] + Cp[1:5] @ f["gp"][t-1:t-5:-1] + Cp[5:10] @ f["gw"][t:t-5:-1] + Cp[10:15] @ ex["grpe"][t:t-5:-1]
                      + Cp[15:20] @ ex["grpf"][t:t-5:-1] + Cp[20] * ex["gpty"][t] + Cp[21:26] @ ex["shortage"][t:t-5:-1]
                      + Cp[26:31] @ ex["greed"][t:t-5:-1]) + e[1]
        f["exp10"][t] = C10[0:5] @ f["gp"][t:t-5:-1] + C10[5:9] @ f["exp10"][t-1:t-5:-1] + e[2]
        f["exp1"][t] = C1[0:4] @ f["exp1"][t-1:t-5:-1] + C1[4:9] @ f["exp10"][t:t-5:-1] + C1[9:14] @ f["gp"][t:t-5:-1] + e[3]
    return f["gw"][pos:], f["gp"][pos:]

yrs = x.index[pos:].year
def moments(gw, gp):
    return np.r_[[gw[yrs == y].mean() for y in range(2020, 2025)], [gp[yrs == y].mean() for y in range(2020, 2025)]]
obs = moments(x.gw.values[pos:], x.gp.values[pos:])
C0 = D.coefs(est)
res = {k: est[k][0].resid for k in ["gw", "gp", "exp10", "exp1"]}
rng = np.random.default_rng(5); T = len(x) - pos
sh = []
for i in range(2000):
    e = np.column_stack([rng.choice(np.asarray(res[k]), T) for k in ["gw", "gp", "exp10", "exp1"]])
    sh.append(moments(*sim2(C0, e)) - moments(*sim2(C0)))
Sig = np.cov(np.array(sh).T)
print("shock sd of yearly moments", np.sqrt(np.diag(Sig)).round(2))
print("observed", obs.round(2)); print("point-model", moments(*sim2(C0)).round(2))
N = int(sys.argv[1]); rng = np.random.default_rng(UM.SEED)
pi = U.nipa({"DPCERG"}).DPCERG
f = (100 * (pi / pi.shift(4) - 1)) / (100 * np.log(pi).diff(4))
def cum(tid):
    y = UM.yoy(tid, x).mul(f.reindex(tid.index), axis=0)
    return y[[t.quarter == 4 and t.year >= 2021 for t in y.index]].sum()
cols = ["shortage", "covid_other", "worker_shortage", "trump", "biden", "pentup", "energy_war", "baseline", "unexplained"]
G, R = [], []
for i in range(N):
    C = D.draw(est, rng)
    G.append(obs - moments(*sim2(C)))
    rr, _, _ = UM.run_once(d, x, C, UM.FISCAL, (B, b, beta), ok[0], bev[0].values, UM.RIDGE)
    R.append(cum(UM.tidy(rr))[cols])
G, R = np.array(G), pd.DataFrame(R)
def wq(v, w, q):
    o = np.argsort(v); c = np.cumsum(w[o]) / w.sum(); return v[o][np.searchsorted(c, q)]
for name, idx in [("wages only", slice(0, 5)), ("wages+prices", slice(0, 10))]:
    Si = np.linalg.inv(Sig[idx, idx]); g = G[:, idx]
    ll = -0.5 * np.einsum("ij,jk,ik->i", g, Si, g); w = np.exp(ll - ll.max())
    print(f"\n{name}: ESS {w.sum()**2/(w**2).sum():.0f} of {N}")
    for c in cols:
        v = R[c].values
        print(f"  {c:16s} prior {np.percentile(v,5):6.2f} {np.percentile(v,95):6.2f} | post {wq(v,w,.05):6.2f} {wq(v,w,.5):6.2f} {wq(v,w,.95):6.2f}")
