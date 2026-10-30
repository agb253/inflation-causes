"""Which uncertainty source drives each cause's 2021-24 90% range? Vary one source at a time (others at point values). Run: python src/uncertainty/sources.py 150 output/uncertainty_sources.csv"""
import sys; sys.path.insert(0, "src")  # run from project root
import numpy as np, pandas as pd
import unified_model as UM, decompose as D, fed_svar as S, fiscal_by_law as F, pentup as P, unified_data as U
d, x, est, point, du, vup, sv, ok, bev = UM.main()
B, b, beta, Ures, sidx, md, z = sv
N = int(sys.argv[1]) if len(sys.argv) > 1 else 150
boots = S.bootstrap(md, z, N, UM.SEED)
pi = U.nipa({"DPCERG"}).DPCERG
f = (100 * (pi / pi.shift(4) - 1)) / (100 * np.log(pi).diff(4))
C0 = D.coefs(est)
variants = [(t, s_) for t in ("geometric", "hutchins") for s_ in (1.0, F.CBO_SCALE)]
def cum(tid):
    y = UM.yoy(tid, x).mul(f.reindex(tid.index), axis=0)
    return y[[t.quarter == 4 and t.year >= 2021 for t in y.index]].sum()
cols = ["shortage", "covid_other", "worker_shortage", "trump", "biden", "pentup", "fed_easing", "fed_hikes", "baseline", "energy_war"]
p0 = cum(UM.tidy(point))
rows = {}
for src in ["bb_coefs", "okun", "beveridge", "fiscal", "svar", "pentup", "covid_gamma", "all"]:
    rng = np.random.default_rng(1)
    out = []
    for i in range(N):
        C = D.draw(est, rng) if src in ("bb_coefs", "all") else C0
        ob = rng.normal(*ok) if src in ("okun", "all") else ok[0]
        bp = rng.multivariate_normal(bev[0].values, bev[1].values) if src in ("beveridge", "all") else bev[0].values
        fv = variants[rng.integers(4)] if src in ("fiscal", "all") else UM.FISCAL
        svi = boots[i] if src in ("svar", "all") else (B, b, beta)
        pv = ((P.M_POINT, P.M_ALT)[rng.integers(2)], ("2023-07-01", "2024-10-01")[rng.integers(2)], P.TREND) if src in ("pentup", "all") else None
        r, _, _ = UM.run_once(d, x, C, fv, svi, ob, bp, UM.RIDGE, pv, rng if src in ("covid_gamma", "all") else None)
        out.append(cum(UM.tidy(r))[cols])
    o = pd.DataFrame(out)
    rows[src] = (o.quantile(.95) - o.quantile(.05))
    print(src, "done", flush=True)
res = pd.DataFrame(rows).round(2)
res.insert(0, "point", p0[cols].round(2))
print(res.to_string())
res.to_csv(sys.argv[2] if len(sys.argv) > 2 else "/dev/null")
