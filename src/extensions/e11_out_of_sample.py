"""Extension 11: out-of-sample test. Which version of the model forecasts 2022-24 inflation best?
Each version's price equation is estimated on 1990Q1-2021Q4 only (wage and expectations equations as in the model,
1990-2019), then simulated 2022Q1-2024Q4 from actual history, given the actual paths of its inputs (V/U, energy and
food prices, the supply-chain measure, productivity, margins): a conditional forecast, the standard test of a
structural inflation model. Scored by root-mean-square error of quarterly (annualized) and 4-quarter PCE inflation.
Versions: supply-chain measure = GSCPI (model), Philly Fed delivery times, composite (extension 4); wage equation
re-estimated through 2021Q4. Benchmarks: no change (2021Q4's 4-quarter rate held), and an AR(4) on inflation.
Writes output/ext/e11_out_of_sample.csv; log = stdout."""
import sys
sys.path.insert(0, __file__.rsplit("/src/", 1)[0] + "/src")
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import numpy as np
import pandas as pd
import statsmodels.api as sm
import unified_model as UM, bb_model as m, decompose as D

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
CUT = "2021-10-01"
F0 = pd.Timestamp("2022-01-01")


def fit(x, wage_to=None):
    xe = x.loc[:CUT]
    est = m.estimate(xe, D.PROD)
    if wage_to:
        est["gw"] = m.rls(xe, "gw", m.wage_X(), True, m.L("gw", cur=False) + m.L("exp1", cur=False))
    return UM.estimate_with_greed(xe, est)


def forecast(x, C):
    old = UM.START; UM.START = F0
    ex = {k: x[k].values.copy() for k in ["grpe", "grpf", "shortage", "gpty", "greed", "vu"]}
    g = UM.simulate(C, x, ex); UM.START = old
    return pd.Series(g, index=x.index[x.index >= F0])


def score(f, x):
    a = x.gp[x.index >= F0]
    yo = lambda s: pd.concat([x.gp[x.index < F0].iloc[-3:], s]).rolling(4).mean().iloc[3:]
    return dict(rmse_quarterly=float(np.sqrt(((f - a) ** 2).mean())), rmse_4q=float(np.sqrt(((yo(f) - yo(a)) ** 2).mean())),
                mean_error=float((f - a).mean()))


def main():
    import e04_supply_measures as E4
    d0 = UM.quarterly()
    rows = []
    alt = {"delivery": E4.fred_q("DTCDFSA066MSFRBPHI").reindex(d0.index), "unfilled": E4.fred_q("NOCDFSA066MSFRBPHI").reindex(d0.index)}
    g_ = d0.shortage.copy(); g_[:"1997-10-01"] = np.nan
    Z = pd.DataFrame({"gscpi": g_, **alt}); zs = (Z - Z[:"2019"].mean()) / Z[:"2019"].std()
    w_, V_ = np.linalg.eigh(np.cov(zs.dropna().T)); pc = V_[:, -1] * np.sign(V_[:, -1].sum())
    alt["composite"] = (zs * pc).sum(axis=1, min_count=1) / (zs.notna() * np.abs(pc)).sum(axis=1).replace(0, np.nan) * np.abs(pc).sum()
    sdg = d0.shortage["2020":"2023"].std()
    for name, sh, wage in [("model (GSCPI)", None, None), ("supply = delivery times", "delivery", None),
                           ("supply = unfilled orders", "unfilled", None), ("supply = composite", "composite", None),
                           ("wage equation through 2021", None, "2021")]:
        d = d0.copy()
        if sh:
            s = alt[sh]; d["shortage"] = ((s - s[:"2019"].mean()) / s["2020":"2023"].std() * sdg).fillna(0.0)
        x = m.build(d); D.PROD_LAG = 0; x, _ = UM.add_greed(x)
        est = fit(x, wage)
        rows.append(dict(version=name, **score(forecast(x, D.coefs(est)), x)))
    # benchmarks
    x = m.build(d0)
    a = x.gp[x.index >= F0]
    rw = pd.Series(x.gp.loc[:CUT].iloc[-4:].mean(), index=a.index)
    rows.append(dict(version="no change (2021Q4 4-quarter rate)", **score(rw, x)))
    g = x.gp.loc["1990":CUT]
    ar = sm.OLS(g.values[4:], sm.add_constant(np.column_stack([g.shift(k).values[4:] for k in range(1, 5)]))).fit()
    hist = list(g.values); fc = []
    for _ in range(len(a)):
        v = ar.params[0] + ar.params[1:] @ np.array(hist[-1:-5:-1]); fc.append(v); hist.append(v)
    rows.append(dict(version="AR(4) on inflation", **score(pd.Series(fc, index=a.index), x)))
    out = pd.DataFrame(rows).set_index("version")
    out.round(3).to_csv(ROOT + "output/ext/e11_out_of_sample.csv")
    print(out.round(2).to_string())


if __name__ == "__main__":
    main()
