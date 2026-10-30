"""Sum of the price equation's GSCPI coefficients (current + 4 lags) and its standard error: the number that sets the
width of the supply-chain range. Also the wage equation's V/U coefficient sum (sets most of the COVID range)."""
import sys; sys.path.insert(0, "src")  # run from project root
import numpy as np
import unified_model as UM, bb_model as m, decompose as D
d = UM.quarterly(); x = m.build(d); D.PROD_LAG = 0
x, _ = UM.add_greed(x)
est = UM.estimate_with_greed(x, m.estimate(x, D.PROD))
for eq, pre in [("gp", "shortage"), ("gw", "vu")]:
    r = est[eq][0]; c = [k for k in r.params.index if k.startswith(pre)]
    cv = r.cov_params().loc[c, c].values
    print(f"{eq} {pre} coefficient sum {r.params[c].sum():.3f} (se {np.sqrt(cv.sum()):.3f}), nobs {est[eq][2]}")
