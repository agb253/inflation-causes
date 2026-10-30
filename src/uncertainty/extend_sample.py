"""Test 2: wage and expectations equations re-estimated through 2024Q4 instead of 2019Q4. Result: ranges barely change. Not adopted."""
import sys; sys.path.insert(0, "src")  # run from project root
import numpy as np, pandas as pd
import unified_model as UM, decompose as D, unified_data as U, bb_model as m
d, x, est, point, du, vup, sv, ok, bev = UM.main()
B, b, beta = sv[:3]
ext = dict(est)
ext["gw"] = m.rls(x, "gw", m.wage_X(), True, m.L("gw", cur=False) + m.L("exp1", cur=False))
ext["exp10"] = m.rls(x, "exp10", m.exp10_X(), False, m.exp10_X())
ext["exp1"] = m.rls(x, "exp1", m.exp1_X(), False, m.exp1_X())
for k in ["gw"]:
    for e, nm in [(est, "pre2020"), (ext, "to2024")]:
        p = e[k][0].params; cv = e[k][0].cov_params()
        vc = [c for c in p.index if c.startswith("vu")]
        print(nm, "V/U coef sum", round(p[vc].sum(), 3), "se", round(float(np.sqrt(cv.loc[vc, vc].values.sum())), 3), "nobs", e[k][2])
pi = U.nipa({"DPCERG"}).DPCERG
f = (100 * (pi / pi.shift(4) - 1)) / (100 * np.log(pi).diff(4))
def cum(tid):
    y = UM.yoy(tid, x).mul(f.reindex(tid.index), axis=0)
    return y[[t.quarter == 4 and t.year >= 2021 for t in y.index]].sum()
cols = ["shortage", "covid_other", "worker_shortage", "trump", "biden", "pentup", "energy_war", "baseline", "unexplained"]
for nm, e in [("pre2020", est), ("to2024", ext)]:
    p0 = cum(UM.tidy(UM.run_once(d, x, D.coefs(e), UM.FISCAL, (B, b, beta), ok[0], bev[0].values)[0]))[cols]
    rng = np.random.default_rng(3); R = []
    for i in range(300):
        R.append(cum(UM.tidy(UM.run_once(d, x, D.draw(e, rng), UM.FISCAL, (B, b, beta), ok[0], bev[0].values)[0]))[cols])
    R = pd.DataFrame(R)
    print(nm); print(pd.DataFrame({"point": p0, "lo": R.quantile(.05), "hi": R.quantile(.95)}).round(2).to_string(), flush=True)
