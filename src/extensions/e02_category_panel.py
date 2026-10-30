"""Extension 2: supply chains estimated from differences across spending categories, not just over time.

dp_it = a_i + d_t + sum_{k=0..11} b_k x (GSCPI_t-k - mean 1998-2019) x E_i + e_it          (weighted least squares)
  dp_it  = 1200 x monthly log change of the PCE price index of category i (BEA Table 2.4.4U, level 4 as in the
           Shapiro replication, food & energy excluded), weight = previous month's spending share (Table 2.4.5U)
  d_t    = a separate effect for every month: absorbs everything that hits all categories alike (relief, the Fed,
           pent-up demand, wages, expectations), so b is identified only by how much MORE exposed categories moved
  E_i    = exposure: (a) goods = 1, services = 0; (b) import share of the category's commodity, 2019 (BEA input-output
           use table, summary level: imports / (domestic output + imports); mapping below; services 0)
Implied direct effect on headline PCE inflation = sum_i w_i E_i x sum_k b_k (GSCPI_t-k - mean): what supply-chain
pressure added to exposed categories relative to services, i.e. assuming services were unaffected (a lower bound).
Measured like the model's lines: year-over-year, 2021-24 total = sum of the four Q4 values. Standard errors clustered
two ways (category and month). Compared with the model's direct supply-chain term (price-equation GSCPI coefficients x
GSCPI, before the feedback through wages and expectations).
Variants: + goods-demand control (E_i x 12-month growth of real goods spending, lags 0-11); estimated on 1998-2019
only (identification without the pandemic episode); dependent variable = supply-labelled price changes only (Shapiro
labels, src/replicate_sf_supply_demand.py L4t); import-share exposure.
Writes output/ext/e02_category_panel.csv and .log (stdout)."""
import sys, zipfile
sys.path.insert(0, "src")
import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
XL = ROOT + "data/raw/bea/Section2All_xls.xlsx"
K = 12

IO = {5: "3361MV", 12: "3361MV", 20: "3361MV", 24: "337", 29: "335", 32: "327", 35: "333", 39: "334", 52: "339",
      53: "3364OT", 60: "511", 61: "339", 63: "339", 66: "339", 69: "511", 70: "315AL", 71: "334", 105: "315AL",
      109: "315AL", 121: "325", 126: "339", 131: "325", 137: "325", 141: "311FT", 142: "511"}   # goods line -> IO commodity


def sheet(name):   # as in src/replicate_sf_supply_demand.py
    x = pd.read_excel(XL, sheet_name=name, header=None, skiprows=7, dtype=str)
    hdr = pd.read_excel(XL, sheet_name=name, header=None, skiprows=7, nrows=1).iloc[0]
    x = x[x[0].str.fullmatch(r"\d+", na=False)].copy()
    x.columns = ["line", "label", "code"] + [str(h) for h in hdr[3:]]
    x["line"] = x.line.astype(int)
    return x.set_index("line")


def num(df, lines):
    d = df.loc[lines].drop(columns=["label", "code"]).T
    d.index = pd.PeriodIndex(d.index.str.replace("M", "-"), freq="M")
    return d.apply(pd.to_numeric, errors="coerce")


def import_shares():
    z = zipfile.ZipFile(ROOT + "data/raw/ext/bea_io/AllTablesIO.zip")
    with z.open("IOUse_Before_Redefinitions_PRO_1997-2023_Summary.xlsx") as f:
        d = pd.read_excel(f, "2019", header=None)
    assert str(d.iloc[5, 81]) == "F050" and str(d.iloc[6, 95]).startswith("Total Commod")
    rows = d.iloc[7:80].set_index(0)
    imp = -pd.to_numeric(rows[81], errors="coerce").fillna(0)
    out = pd.to_numeric(rows[95], errors="coerce")
    return imp / (out + imp)


def gscpi_monthly():
    g = pd.read_excel(ROOT + "data/raw/nyfed/gscpi_data.xlsx", sheet_name="GSCPI Monthly Data", usecols=[0, 1]).dropna()
    g["Date"] = pd.to_datetime(g.Date, format="%d-%b-%Y")
    s = g.set_index("Date").GSCPI.astype(float); s.index = s.index.to_period("M")
    return s - s[:"2019-12"].mean()


def real_goods_growth():
    q = sheet("U20403-M")            # quantity indexes; line 2 = goods
    g = num(q, [2])[2]
    return 100 * np.log(g).diff(12)


def main():
    cats = pd.read_csv(ROOT + "output/sf_replication_categories_L4.csv", index_col=0)
    core = [c for c in cats.index if not cats.food_energy[c] and c not in (145, 334, 338, 342)]
    spend, price = sheet("U20405-M"), sheet("U20404-M")
    P, S = num(price, core), num(spend, core)
    tot = num(spend, [1])[1]                                   # total PCE: headline weights
    w = S.div(tot, axis=0).shift(1)
    dp = 1200 * np.log(P).diff()
    G = gscpi_monthly()
    imp = import_shares()
    E = {"goods": pd.Series({c: float(c < 150) for c in core}),
         "import_share": pd.Series({c: (imp[IO[c]] if c in IO else 0.0) for c in core})}
    lab = pd.read_csv(ROOT + "output/sf_replication_by_category_L4t.csv.gz")
    lab = lab.pivot(index="month", columns="line", values="label"); lab.index = pd.PeriodIndex(lab.index, freq="M")
    rg = real_goods_growth()
    print("import shares (2019):", {c: round(v, 2) for c, v in E["import_share"].items() if v > 0})

    def run(name, expo, end="2024-12", dep="all", demand_ctrl=False):
        e = E[expo]
        y = dp.copy()
        if dep == "supply":
            y = y.where(lab.reindex(index=y.index, columns=y.columns) == "supply", 0.0)
        long = y.stack().rename("dp").to_frame()
        long["w"] = w.stack()
        long = long.reset_index(); long.columns = ["month", "line", "dp", "w"]
        long = long[(long.month >= pd.Period("1999-01", "M")) & (long.month <= pd.Period(end, "M"))].dropna()
        for k in range(K):
            long[f"z{k}"] = G.shift(k).reindex(long.month).values * e.reindex(long.line).values
            if demand_ctrl:
                long[f"c{k}"] = rg.shift(k).reindex(long.month).values * e.reindex(long.line).values
        long = long.dropna()
        Xf = pd.get_dummies(long.line.astype(str), prefix="i", drop_first=True, dtype=float)
        Xt = pd.get_dummies(long.month.astype(str), prefix="t", drop_first=True, dtype=float)
        zc = [c for c in long if c[0] in "zc" and c[1:].isdigit()]
        X = pd.concat([long[zc], Xf, Xt], axis=1); X.insert(0, "const", 1.0)
        groups = np.column_stack([long.line.values, long.month.astype(str).factorize()[0]])
        r = sm.WLS(long.dp.values, X.values, weights=long.w.values).fit(cov_type="cluster", cov_kwds={"groups": groups})
        bz = [f"z{k}" for k in range(K)]; ix = [list(X.columns).index(c) for c in bz]
        b, V = r.params[ix], r.cov_params()[np.ix_(ix, ix)]
        # implied direct effect on headline PCE: monthly annualized, then year-over-year (12-month average), Q4 sums
        months = pd.period_range("2019-01", "2024-12", freq="M")
        wE = (w.reindex(months) * e).sum(axis=1)                # exposure-weighted spending share
        A = np.column_stack([G.shift(k).reindex(months).values * wE.values for k in range(K)])   # month x lag
        Ay = pd.DataFrame(A, index=months).rolling(12).mean()
        sel = [m for m in months if m.month in (10, 11, 12) and 2021 <= m.year <= 2024]
        a_tot = Ay.loc[sel].groupby([m.year for m in sel]).mean().sum().values     # Q4 average of y/y, summed
        eff, se = float(a_tot @ b), float(np.sqrt(a_tot @ V @ a_tot))
        pk = Ay.mean(axis=1).idxmax()
        yy = Ay.values @ b
        return dict(variant=name, exposure=expo, sample_end=end, dependent=dep, demand_control=demand_ctrl, nobs=int(r.nobs),
                    lag_sum=float(b.sum()), lag_sum_se=float(np.sqrt(V.sum())), effect_2021_24=eff, effect_se=se,
                    peak_yoy=float(np.nanmax(yy)), peak_month=str(pd.Series(yy, index=months).idxmax()))

    rows = [run("goods exposure", "goods"),
            run("import-share exposure", "import_share"),
            run("goods + goods-demand control", "goods", demand_ctrl=True),
            run("goods, estimated 1999-2019 only", "goods", end="2019-12"),
            run("goods, supply-labelled price changes only", "goods", dep="supply")]
    out = pd.DataFrame(rows)

    # the model's direct supply-chain term, same metric (point and 1,000 coefficient redraws)
    import unified_model as UM, bb_model as m, decompose as D
    d = UM.quarterly(); x = m.build(d); D.PROD_LAG = 0; x, _ = UM.add_greed(x)
    est = UM.estimate_with_greed(x, m.estimate(x, D.PROD))
    gq = x.shortage - x.shortage[:"2019-10-01"].mean()
    lagged = np.column_stack([gq.shift(k).values for k in range(5)])
    names = ["shortage"] + [f"shortage_l{k}" for k in range(1, 5)]
    pr = est["gp"][0].params
    i0 = list(pr.index).index("shortage")
    rng = np.random.default_rng(1)

    def metric(cs):
        q = pd.Series(lagged @ cs, index=x.index).rolling(4).mean()
        return float(sum(q[f"{y}-10-01"] for y in range(2021, 2025)))
    pt = metric(pr[names].values)
    dr = [metric(D.draw(est, rng)["gp"][i0:i0 + 5]) for _ in range(1000)]
    model = dict(point=pt, p5=np.percentile(dr, 5), p95=np.percentile(dr, 95), sd=np.std(dr))
    out.round(4).to_csv(ROOT + "output/ext/e02_category_panel.csv", index=False)
    pd.Series(model).round(4).to_csv(ROOT + "output/ext/e02_model_direct.csv")
    pd.set_option("display.width", 250)
    print(out.round(3).to_string())
    print("model direct supply-chain term, 2021-24 total (log points, before wage/expectation feedback):",
          {k: round(v, 3) for k, v in model.items()})


if __name__ == "__main__":
    main()
