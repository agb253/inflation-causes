"""Run everything: estimate, decompose 2020Q1-2024Q4, bootstrap bands, robustness variants.
Usage (from project root):  python src/run_all.py"""
import sys, json, numpy as np, pandas as pd
sys.path.insert(0, "src")
import bb_model as m, decompose as D

NDRAW, END = 2000, "2024-10-01"
OUT = "output/"


def pipeline(x, prod, plag, ndraw=0):
    D.PROD_LAG = plag
    est = m.estimate(x, prod)
    if ndraw:
        return est, *D.run(x, est, ndraw)
    return est, D.decompose(D.coefs(est), x)


# ---- primary: Lorenzoni dataset through 2025Q1
x = m.build(m.load(m.RAW + "data_us_new.csv"))
est, point, cols, arr = pipeline(x, D.PROD, 0, NDRAW)
keep = point.index <= END
point, arr = point[keep], arr[:, keep, :]
q = {"lo90": 5, "hi90": 95, "lo68": 16, "hi68": 84}
bands = {k: pd.DataFrame(np.percentile(arr, p, axis=0), index=point.index, columns=cols) for k, p in q.items()}
bands["mean"] = pd.DataFrame(arr.mean(axis=0), index=point.index, columns=cols)
point.to_csv(OUT + "decomp_point.csv")
for k, v in bands.items(): v.to_csv(OUT + f"decomp_{k}.csv")
np.save(OUT + "draws.npy", arr)  # (draw, quarter, component) for anyone who wants to re-slice

# ---- cumulative (2020Q1-2024Q4): sum of annualized quarterly rates / 4 = log points of price level
cum = pd.DataFrame({"point": point[cols].sum() / 4, "actual": point.actual_cpi.sum() / 4}).assign(
    **{n: np.percentile(arr.sum(axis=1) / 4, p, axis=0) for n, p in q.items()})
cum.to_csv(OUT + "cumulative_2020q1_2024q4.csv")
# ---- calendar-year averages (annualized quarterly rates averaged over the four quarters ~ Q4/Q4 log change)
yr = point.index.year
ann = {}
for y in sorted(set(yr)):
    msk = yr == y
    pt = point.loc[msk, cols].mean()
    dr = arr[:, msk, :].mean(axis=1)
    ann[y] = pd.DataFrame({"point": pt, "lo90": np.percentile(dr, 5, axis=0), "hi90": np.percentile(dr, 95, axis=0),
                           "lo68": np.percentile(dr, 16, axis=0), "hi68": np.percentile(dr, 84, axis=0)})
    ann[y].loc["actual_cpi", "point"] = point.loc[msk, "actual_cpi"].mean()
pd.concat(ann, names=["year", "component"]).to_csv(OUT + "calendar_year_average.csv")

# ---- coefficients table
rows = []
pub = {k: pd.read_excel(f"{m.RAW}published_coefs/coef_{k}.xlsx") for k in ["gp", "gw", "exp10", "exp1"]}
# validation fit on the ORIGINAL dataset (what the paper estimated on) for the published comparison
xo = m.build(m.load(m.RAW + "data_us.csv")); D.PROD_LAG = 0; eo = m.estimate(xo, D.PROD)
for k in ["gw", "gp", "exp10", "exp1"]:
    r, c, n = est[k]; ro, _, no = eo[k]
    se = np.sqrt(np.diag(r.cov_params())); seo = np.sqrt(np.diag(ro.cov_params()))
    for i, name in enumerate(c):
        rows.append(dict(equation=k, term=name, published_label=pub[k].coef.iloc[i - (0 if "const" in c else 0)] if len(pub[k]) == len(c) else "",
                         published_beta=pub[k].beta.iloc[i] if len(pub[k]) == len(c) else np.nan,
                         est_original_data=ro.params.iloc[i], se_original=seo[i], est_used=r.params.iloc[i], se_used=se[i],
                         n_used=n, n_original=no))
coef = pd.DataFrame(rows); coef["abs_diff_vs_published_in_SE"] = (coef.est_original_data - coef.published_beta).abs() / coef.se_original.replace(0, np.nan)
coef.to_csv(OUT + "coefficients.csv", index=False)

# ---- robustness variants (point estimates, same quarters)
rob = {"primary": point[cols]}
_, p = pipeline(m.build(m.load(m.RAW + "data_us.csv")), D.PROD, 0); rob["original_dataset_to_2023Q1"] = p[cols]
_, p = pipeline(x, D.PROD, 1); rob["authors_R_script_lagged_productivity"] = p.loc[:END, cols]
b = pd.read_csv("data/raw/bls_api/cpi_monthly_combined.csv", index_col=0, parse_dates=True).resample("QS").last()
dd = m.load(m.RAW + "data_us_new.csv")
for c_, s in [("cpi", "CUSR0000SA0"), ("energy_cpi", "CUSR0000SA0E"), ("food_cpi", "CUSR0000SAF1")]:
    dd[c_] = b[s].reindex(dd.index).fillna(dd[c_])
_, p = pipeline(m.build(dd), D.PROD, 0); rob["current_BLS_CPI_energy_food"] = p.loc[:END, cols]
D.PROD_LAG = 0
pd.concat(rob, names=["variant", "date"]).to_csv(OUT + "robustness_point.csv")
pd.concat({k: v.sum() / 4 for k, v in rob.items()}, axis=1).to_csv(OUT + "robustness_cumulative.csv")
print("done"); print(cum.round(2).to_string())
