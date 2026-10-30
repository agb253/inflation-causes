"""Extension 1: Benigno-Eggertsson inverse-L idea. Does wage growth (or price inflation) respond more steeply to V/U
above a threshold? Adds max(V/U - tau, 0) (lags 1-4 in the wage equation; current + 4 lags, with V/U itself, in the
price equation), estimated 1990-2024, for tau = 0.6 ... 1.4. Prints coefficient sums (s.e.) and residual sums of squares.
Run from project root; log: output/ext/e01_kinked_phillips.log."""
import sys; sys.path.insert(0, "src")
import numpy as np, bb_model as m, unified_model as UM, decompose as D
m.WAGE = "linear2024"
d = UM.quarterly(); x0 = m.build(d); D.PROD_LAG = 0; x0, _ = UM.add_greed(x0)
gpX = m.price_X(D.PROD) + m.L("greed")


def s(r, pre):
    c = [k for k in r.params.index if k.startswith(pre)]; cv = r.cov_params().loc[c, c].values
    return f"{r.params[c].sum():+.3f} ({np.sqrt(cv.sum()):.3f})"


print("V/U range 1990-2019:", round(x0.vu[:"2019"].min(), 2), "to", round(x0.vu[:"2019"].max(), 2), "; 2020Q2:", round(x0.vu["2020-04-01"], 2))
for tau in [0.6, 0.8, 1.0, 1.2, 1.4]:
    x = x0.copy(); x["vuk"] = (x.vu - tau).clip(lower=0)
    for i in range(1, 5): x[f"vuk_l{i}"] = x.vuk.shift(i)
    rw, _, _ = m.rls(x, "gw", m.wage_X() + m.L("vuk", cur=False), True, m.L("gw", cur=False) + m.L("exp1", cur=False))
    rp, _, _ = m.rls(x, "gp", gpX + m.L("vu") + m.L("vuk"), True, m.L("gp", cur=False) + m.L("gw"))
    print(f"tau {tau}: WAGE eq: V/U {s(rw, 'vu_')}, above-threshold {s(rw, 'vuk')}, RSS {np.sum(rw.resid**2):.1f} | "
          f"PRICE eq: V/U {s(rp, 'vu')}, above-threshold {s(rp, 'vuk')}, RSS {np.sum(rp.resid**2):.1f}")
