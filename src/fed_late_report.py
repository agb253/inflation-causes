"""'Did the Fed act too late?': what earlier hikes would have done, in this project's model (fed_late() in
src/unified_model.py), with 90% ranges, next to the published estimate it is checked against. Writes output/fed_late.csv.
Run from project root:  python src/fed_late_report.py"""
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, "src")
import unified_model as M
import bb_model as m
import decompose as D
import fed_svar as S
from robustness import pct_factor

NDRAW, SEED = 300, 20261019
SCEN = {"barnichon": "Hikes from March 2021 to ~2% by early 2022 (path of Barnichon, FRBSF EL 2022-28)",
        "year_early": "The actual 2022-23 hikes, started 12 months earlier (March 2021)"}

if __name__ == "__main__":
    d = M.quarterly(); x = m.build(d); D.PROD_LAG = 0
    x, _ = M.add_greed(x)
    est = M.estimate_with_greed(x, m.estimate(x, D.PROD)); C = D.coefs(est)
    md, z = S.data(); B, b, U_, si, F_, beta = S.estimate(md, z)
    bev, bev_cov = M.beveridge(d)
    boots = S.bootstrap(md, z, NDRAW, SEED)
    rng = np.random.default_rng(SEED)
    rows = []
    for sc in SCEN:
        du, dq = M.fed_late(d, x, C, (B, b, beta), bev.values, sc)
        f = pct_factor(dq.index)
        yi = dq.rolling(4).mean() * f
        DU, DY = [], []
        for i in range(NDRAW):
            Ci = D.draw(est, rng); bp = rng.multivariate_normal(bev.values, bev_cov.values)
            a, q = M.fed_late(d, x, Ci, boots[i], bp, sc)
            DU.append(a.values); DY.append((q.rolling(4).mean() * f).values)
        DU, DY = np.array(DU), np.array(DY)
        for j, t in enumerate(du.index):
            rows.append(dict(scenario=sc, quarter=f"{t.year}Q{t.quarter}", unemp=du.iloc[j],
                             unemp_lo=np.nanpercentile(DU[:, j], 5), unemp_hi=np.nanpercentile(DU[:, j], 95),
                             infl_yoy=yi.iloc[j], infl_lo=np.nanpercentile(DY[:, j], 5), infl_hi=np.nanpercentile(DY[:, j], 95)))
    out = pd.DataFrame(rows)
    out.round(3).to_csv("output/fed_late.csv", index=False)
    pd.set_option("display.width", 200)
    print(out[out.quarter.str.endswith(("Q2", "Q4"))].round(2).to_string(index=False))
