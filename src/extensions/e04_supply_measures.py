"""Extension 4: other measures of supply-chain pressure in place of the NY Fed GSCPI (which starts in 1998; the model
fills 1990-97 with its mean, so those years carry no information).
  delivery  Philadelphia Fed Manufacturing Business Outlook Survey, future-independent current delivery times
            diffusion index, seasonally adjusted (FRED DTCDFSA066MSFRBPHI), monthly from 1968
  unfilled  same survey, current unfilled orders (FRED NOCDFSA066MSFRBPHI)
  composite first principal component of the standardized GSCPI, delivery and unfilled (each over its own sample;
            1990-97 from delivery and unfilled only)
Each is put in the Bernanke-Blanchard price equation in place of GSCPI (quarterly mean, minus its 1990-2019 mean, scaled
to GSCPI's 2020-23 standard deviation so coefficients are comparable), and the full model is re-run (point estimate +
300 redraws of the wage-price coefficients) for the supply-chain line, 2021-24 total.
Writes output/ext/e04_supply_measures.csv."""
import sys
sys.path.insert(0, "src")
import numpy as np
import pandas as pd
import unified_model as UM, bb_model as m, decompose as D, unified_data as U

ROOT = __file__.rsplit("/src/", 1)[0] + "/"


def fred_q(s):
    f = pd.read_csv(ROOT + f"data/raw/ext/fred/{s}.csv", index_col=0, parse_dates=True).iloc[:, 0]
    return pd.to_numeric(f, errors="coerce").resample("QS").mean()


def main():
    d0 = UM.quarterly()
    g = d0.shortage.copy(); g[:"1997-10-01"] = np.nan            # GSCPI as the model uses it, without the fill
    alt = {"delivery": fred_q("DTCDFSA066MSFRBPHI"), "unfilled": fred_q("NOCDFSA066MSFRBPHI")}
    Z = pd.DataFrame({"gscpi": g, **{k: v.reindex(d0.index) for k, v in alt.items()}})
    zs = (Z - Z[:"2019"].mean()) / Z[:"2019"].std()
    # first principal component on the common sample, applied with available series (mean of available loadings x z)
    common = zs.dropna()
    w, V = np.linalg.eigh(np.cov(common.T)); pc = V[:, -1] * np.sign(V[:, -1].sum())
    comp = (zs * pc).sum(axis=1, min_count=1) / (zs.notna() * np.abs(pc)).sum(axis=1).replace(0, np.nan) * np.abs(pc).sum()
    meas = {"GSCPI (model)": d0.shortage, "delivery times": alt["delivery"].reindex(d0.index),
            "unfilled orders": alt["unfilled"].reindex(d0.index), "composite": comp}
    sdg = d0.shortage["2020":"2023"].std()
    pi = U.nipa({"DPCERG"}).DPCERG; f = (100 * (pi / pi.shift(4) - 1)) / (100 * np.log(pi).diff(4))
    rows = []
    for name, s in meas.items():
        s = s.copy()
        s = (s - s[:"2019"].mean()) / s["2020":"2023"].std() * sdg if name != "GSCPI (model)" else s
        d = d0.copy(); d["shortage"] = s.fillna(0.0) if name != "GSCPI (model)" else s
        x = m.build(d); D.PROD_LAG = 0; x, _ = UM.add_greed(x)
        est = UM.estimate_with_greed(x, m.estimate(x, D.PROD))
        r = est["gp"][0]; c = [k for k in r.params.index if k.startswith("shortage")]
        cs, cse = r.params[c].sum(), float(np.sqrt(r.cov_params().loc[c, c].values.sum()))
        md, z = UM.S.data(); B, b, Ures, sidx, Fs, beta = UM.S.estimate(md, z)
        ok, _ = UM.okun(d); bev, _ = UM.beveridge(d)

        def cum(C):
            res, _, _ = UM.run_once(d, x, C, UM.FISCAL, (B, b, beta), ok, bev.values)
            yy = UM.yoy(UM.tidy(res), x).mul(f.reindex(res.index), axis=0)
            return float(yy.shortage[[t.quarter == 4 and t.year >= 2021 for t in yy.index]].sum())
        pt = cum(D.coefs(est)); rng = np.random.default_rng(4)
        dr = [cum(D.draw(est, rng)) for _ in range(300)]
        rows.append(dict(measure=name, coef_sum=cs, coef_se=cse, t=cs / cse, line_2021_24=pt,
                         p5=np.percentile(dr, 5), p95=np.percentile(dr, 95), width=np.percentile(dr, 95) - np.percentile(dr, 5)))
        print(rows[-1], flush=True)
    out = pd.DataFrame(rows).set_index("measure")
    out.round(3).to_csv(ROOT + "output/ext/e04_supply_measures.csv")
    print(out.round(2).to_string()); print("composite loadings (gscpi, delivery, unfilled):", pc.round(2))


if __name__ == "__main__":
    main()
