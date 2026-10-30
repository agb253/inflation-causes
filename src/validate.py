import sys, numpy as np, pandas as pd
sys.path.insert(0, "src")
import bb_model as m

x = m.build(m.load(m.RAW + "data_us.csv"))
print("rows", len(x), x.index[0].date(), x.index[-1].date())
pub = {k: pd.read_excel(f"{m.RAW}published_coefs/coef_{k}.xlsx") for k in ["gp", "gw", "exp10", "exp1"]}
for prod in ["gpty_l1", "gpty"]:
    est = m.estimate(x, prod)
    print(f"\n=== price eq productivity term = {prod} ===")
    for k in ["gw", "gp", "exp10", "exp1"]:
        res, cols, n = est[k]
        b = res.params.values
        pb = pub[k].beta.values
        assert len(pb) == len(b), (k, len(pb), len(b))
        se = np.sqrt(np.diag(res.cov_params()))
        dev = np.abs(b - pb)
        z = dev / np.where(se > 1e-9, se, np.nan)
        print(f"{k:6s} n={n:3d} max|diff|={dev.max():.4f}  max diff/SE={np.nanmax(z):.2f}  sum(published)={pb.sum():.3f} sum(mine)={b.sum():.3f}")
        if k == "gp":
            for c, a, bb, s in zip(cols, b, pb, se): print(f"     {c:12s} mine={a:8.4f} pub={bb:8.4f} se={s:.4f}")
