import sys; sys.path.insert(0, "src")
import numpy as np, pandas as pd, bb_model as m, decompose as D
x = m.build(m.load(m.RAW + "data_us.csv")); est = m.estimate(x, D.PROD)
p = D.decompose(D.coefs(est), x)
comp = ["energy","food","shortages","labor_tightness","productivity","baseline_pre2020","unexplained"]
print("additivity: max |actual - sum(parts)| =", np.abs(p.actual_cpi - p[comp].sum(axis=1)).max())
print(p.round(2).to_string())
