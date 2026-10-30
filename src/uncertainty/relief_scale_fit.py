"""Test 3: does the unemployment data prefer a relief size (multiplier scale)? Stringency fit R2 is flat across scales, so the data cannot tell. Not adopted."""
import sys; sys.path.insert(0, "src")  # run from project root
import numpy as np, pandas as pd
import unified_model as UM, fiscal_by_law as F, pentup as P
d, x, est, point, du, vup, sv, ok, bev = UM.main()
fed = UM.fed_effect(d, sv[:3])
for t in ("geometric", "hutchins"):
    for s_ in (0.5, 1.0, 1.5, F.CBO_SCALE, 3.0):
        eff = F.run_variant(d.index, t, s_)
        du_ = {k: ok[0] * v for k, v in eff.items()}
        for k in ["fed_pre2020", "fed_easing", "fed_hikes"]: du_[k] = fed[k]
        du_["pentup"] = ok[0] * P.effect(d.index, *UM.PENT[1:2], UM.PENT[0], UM.PENT[2]) if False else ok[0] * P.effect(d.index, UM.PENT[1], UM.PENT[0], UM.PENT[2])
        u_ref = d.u[UM.REF] - du_["fed_pre2020"][UM.REF]
        y = (d.u - u_ref) - sum(du_.values())
        r, st = UM.covid_fit(y, d)
        yy = y.loc[UM.START:UM.FIT_END]; rc = 1 - (r.resid**2).sum() / ((yy - yy.mean())**2).sum()
        # also post-fit years 2023-24: how far is unemployment left unexplained
        miss = (y - (r.params.s0 * st + r.params.s1 * st.shift(1).fillna(0))).loc["2023-01-01":"2024-10-01"]
        print(f"{t:9s} scale {s_:4.2f}  SSR {(r.resid**2).sum():6.2f}  centered R2 {rc:.2f}  2023-24 mean miss {miss.mean():5.2f}  g0 {r.params.s0:.1f}")
