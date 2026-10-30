"""Extension 14: did the infrastructure law (IIJA) or the Inflation Reduction Act (IRA) cause the inflation?
Both were signed by Biden and neither is in the model's relief lines. Three tests.

A. Same machinery as the relief laws. Each law's year-by-year budget effect, as CBO scored it when it passed, goes
   through the relief chain: GDP effect = multiplier x spending, spread over time with the relief timing
   (geometric, lambda = fiscal_by_law.GEO_LAMBDA) -> unemployment (Okun) -> V/U (log V/U on u, slope b) -> the
   wage-price model. The inflation effect is the model with the law minus the model without it.
   Sources (data/raw/ext/laws/, PDFs via the Internet Archive; cbo.gov refuses automated downloads):
     IIJA  CBO cost estimate, Senate Amendment 2137 to H.R. 3684 (revised Aug 9, 2021), Table 1 (p. 3),
           www.cbo.gov/publication/57406 -> hr3684_infrastructure.pdf
     IRA   CBO, Estimated Budgetary Effects of Public Law 117-169 (Sept 7, 2022), summary pp. 1-3 and Table 1
           pp. 5-13, www.cbo.gov/publication/58455 -> PL117-169_9-7-22.pdf
   Fiscal year y = calendar quarters (y-1)Q4 to yQ3; CBO's yearly dollars are used as the annual rate in each quarter.
   Scenarios, from most realistic to most generous to the "it caused inflation" claim:
     scored     net deficit effect (Table 1 "Total Changes" / summary "Effect on the Deficit"), CBO multipliers
                (IIJA: 0.88, CBO's state-and-local-grant figure, src/fiscal_by_law.CBO_M; IRA: 0.60, CBO's figure for
                payments to households, the most stimulative category the IRA's spending side resembles)
     spending   spending side only: every offset removed (IIJA: discretionary outlays only, plus the $196.5bn of
                highway contract authority above CBO's baseline, spread like those outlays, an assumption made
                here; IRA: the deficit effect with the revenue raisers and the drug-price savings added back),
                multiplier 1.0 (dollar for dollar)
     promise    the "promises raise prices today" case: ALL ten years of the spending-side money treated as if
                paid in the quarter the law was signed (IIJA 2021Q4, IRA 2022Q3), multiplier 1.0
   Uncertainty: 1,000 draws of the wage-price coefficients and Okun's coefficient, as in run_bands.
B. Market expectations on the days each law's fate was decided (breakevens, FRED; method of extension 9).
   Dates: congress.gov bill status XML via govinfo (BILLSTATUS-117hr3684.xml, -117hr5376.xml); Manchin's
   Dec 19, 2021 "no" on Build Back Better and the July 27, 2022 Manchin-Schumer deal: Wikipedia articles
   "Build Back Better Act" and "Inflation Reduction Act" (citing NPR, AP and Politico of those dates).
C. Timing: PCE inflation in the quarter each law was signed.
Writes output/ext/e14_laws.csv, e14_laws_quarterly.csv, e14_events.csv; log = stdout."""
import sys
sys.path.insert(0, __file__.rsplit("/src/", 1)[0] + "/src")
import numpy as np
import pandas as pd
import unified_model as UM, decompose as D, unified_data as U, fiscal_by_law as F

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
FY = list(range(2021, 2032))
# ---- IIJA, CBO Table 1, $ millions, FY2021-2031
IIJA_DEFICIT = [0, -4362, 8970, 29203, 37739, 59701, 53775, 39101, 23451, 16062, -7493]
IIJA_DISC_OUTLAYS = [0, 14044, 33918, 49058, 61144, 69961, 62556, 50082, 34651, 23322, 16712]
IIJA_HIGHWAY_ABOVE_BASELINE = 196_500            # p. 1: contract authority "$196.5 billion more" than baseline
# ---- IRA, CBO PL 117-169, $ millions, FY2022-2031 (FY2021 = 0)
IRA_DEFICIT = [0, -622, -5814, 13777, 23295, 29228, -5881, -36165, -23321, -23327, -29252]
IRA_OFFSETS = {                                   # deficit-reducing lines, added back for the spending-side case
    "corporate minimum tax (rev, sec 10101)": [0, 0, 34679, 34258, 22039, 17702, 18699, 20798, 22756, 24658, 26659],
    "stock buyback tax (rev, sec 10201)": [0, 0, 5697, 7875, 8070, 8581, 8882, 8838, 8603, 8500, 8641],
    "drug rebates (rev, secs 11101-2)": [0, 0, 113, 314, 470, 642, 812, 973, 1100, 1181, 1245],
    "superfund tax (rev, sec 13601)": [0, 0, 902, 1230, 1271, 1304, 1336, 1368, 1402, 1436, 1470],
    "black lung tax (rev, sec 13901)": [0, 0, 103, 135, 131, 130, 130, 131, 132, 133, 134],
    "excess business losses (rev, secs 13903-4)": [0, 0, 0, 0, 0, 0, 17666, 26198, 9453, -274, -284],
    "methane fee (rev, title VI)": [0, 0, 0, 0, 0, 850, 1350, 1400, 1200, 1050, 500],
    "drug price negotiation (outlays, sec 11001)": [0, 0, 0, 0, 0, 3728, 8317, 17535, 21009, 23416, 24516],
    "drug inflation rebates (outlays, secs 11101-2)": [0, 0, 632, 607, 17863, 6024, 5957, 5773, 5968, 6450, 7065],
    "rebate rule moratorium (outlays, sec 11301)": [0, 0, 0, 0, 0, 0, 16290, 25656, 23394, 27561, 29250],
}
SIGNED = {"iija": pd.Timestamp("2021-10-01"), "ira": pd.Timestamp("2022-07-01")}   # quarter of signing (Nov 15, Aug 16)
EVENTS = [("2021-08-10", "IIJA passes Senate (69-30)", +1), ("2021-11-05", "IIJA passes House (228-206, late night)", +1),
          ("2021-11-15", "IIJA signed", +1), ("2021-11-19", "Build Back Better passes House (220-213)", +1),
          ("2021-12-19", "Manchin says no to Build Back Better (Sunday)", -1),
          ("2022-07-27", "Manchin-Schumer deal announced (became the IRA)", +1),
          ("2022-08-07", "IRA passes Senate (51-50, Sunday)", +1), ("2022-08-12", "IRA passes House (220-207)", +1),
          ("2022-08-16", "IRA signed", +1)]


def fy_to_q(v, index):
    s = pd.Series(0.0, index=index)
    for y, a in zip(FY, v):
        for q in pd.date_range(f"{y - 1}-10-01", f"{y}-07-01", freq="QS"):
            if q in s.index: s[q] = a / 1000.0         # $bn at an annual rate
    return s


def gdp_effect(X, index, mult):
    pot = (U.qmean(U.fred("GDPPOT")) * U.qmean(U.fred("GDPDEF")) / 100).reindex(index)
    w = np.array([(1 - F.GEO_LAMBDA) * F.GEO_LAMBDA ** h for h in range(40)])
    x_ = X.reindex(index).fillna(0.0).values
    conv = np.array([sum(w[h] * x_[t - h] for h in range(len(w)) if t - h >= 0) for t in range(len(x_))])
    return 100 * mult * conv / pot


def paths(index):
    q = lambda v: fy_to_q(v, index)
    disc = q(IIJA_DISC_OUTLAYS)
    hw = disc / disc.sum() * IIJA_HIGHWAY_ABOVE_BASELINE / 1000 * 4      # same shape, $196.5bn in total (x4: annual rate)
    iija_sp = disc + hw
    ira_sp = q(np.array(IRA_DEFICIT) + np.sum(list(IRA_OFFSETS.values()), axis=0))
    out = {"iija scored": (q(IIJA_DEFICIT), F.CBO_M["state_local"]), "ira scored": (q(IRA_DEFICIT), F.CBO_M["rebates"]),
           "iija spending side": (iija_sp, 1.0), "ira spending side": (ira_sp, 1.0)}
    for k, sp in [("iija", iija_sp), ("ira", ira_sp)]:
        p = pd.Series(0.0, index=index); p[SIGNED[k]] = sp.sum()      # all ten years in one quarter (see main)
        out[f"{k} promise = payment"] = (p, 1.0)
    return out, iija_sp, ira_sp


def main():
    d, x, est, point, du, vup, sv, ok, bev = UM.main()
    a_, b_ = bev[0].values
    idx = d.index
    P, iija_sp, ira_sp = paths(idx)
    # promise case: a quarter at annual rate R pays R/4 dollars; to pay the whole ten-year total T in one quarter the
    # annual rate is 4T. sum of quarterly annual rates = 4 x dollars, so p (= sum of rates) is already 4T.
    tot10 = {"iija": iija_sp.sum() / 4, "ira": ira_sp.sum() / 4}
    print(f"spending side, 10-year dollars: IIJA ${tot10['iija']:.0f}bn, IRA ${tot10['ira']:.0f}bn")
    print(f"scored 10-year deficit: IIJA ${sum(IIJA_DEFICIT) / 1000:.0f}bn, IRA ${sum(IRA_DEFICIT) / 1000:.0f}bn")
    pos = x.index.get_loc(UM.START)
    ex0 = {k: x[k].values.copy() for k in ["grpe", "grpf", "shortage", "gpty", "greed", "vu"]}
    pi = U.nipa({"DPCERG"}).DPCERG; fct = (100 * (pi / pi.shift(4) - 1)) / (100 * np.log(pi).diff(4))
    q4 = [t for t in x.index[pos:] if t.month == 10 and 2021 <= t.year <= 2024]

    def effect(C, okb, gdp):
        dvu = (x.vu * (1 - np.exp(-b_ * okb * gdp.reindex(x.index).fillna(0.0)))).values   # V/U the law added
        ex = {k: v.copy() for k, v in ex0.items()}; ex["vu"] = ex["vu"] - dvu
        q = pd.Series(UM.simulate(C, x, ex0) - UM.simulate(C, x, ex), index=x.index[pos:])
        yq = pd.concat([pd.Series(0.0, index=pd.date_range("2019-01-01", "2019-10-01", freq="QS")), q]).rolling(4).mean().loc[UM.START:]
        return yq * fct.reindex(yq.index)

    C0 = D.coefs(est)
    pt, qrows = {}, {}
    gdp = {k: gdp_effect(v[0], idx, v[1]) for k, v in P.items()}
    for s in ["scored", "spending side", "promise = payment"]:
        gdp[f"both {s}"] = gdp[f"iija {s}"] + gdp[f"ira {s}"]
    for k, g in gdp.items():
        e = effect(C0, ok[0], g); qrows[k] = e
        pt[k] = dict(total_2021_24=float(e[q4].sum()), peak_gdp_pct=float(g.max()),
                     max_yoy=float(e.max()), yoy_2022q2=float(e[pd.Timestamp("2022-04-01")]))
    rng = np.random.default_rng(14)
    dr = {k: [] for k in gdp}
    for i in range(1000):
        C = D.draw(est, rng); okb = rng.normal(*ok)
        for k, g in gdp.items():
            dr[k].append(float(effect(C, okb, g)[q4].sum()))
    out = pd.DataFrame(pt).T
    for k in gdp:
        out.loc[k, "p5"], out.loc[k, "p50"], out.loc[k, "p95"] = np.percentile(dr[k], [5, 50, 95])
    out.round(3).to_csv(ROOT + "output/ext/e14_laws.csv")
    pd.DataFrame(qrows).round(3).to_csv(ROOT + "output/ext/e14_laws_quarterly.csv")
    pd.set_option("display.width", 220)
    print(out.round(2).to_string())
    # for comparison: the relief lines, same units (point run)
    yy = UM.yoy(UM.tidy(point), x).mul(fct.reindex(UM.tidy(point).index), axis=0)
    print("relief, same units: trump %.2f, biden %.2f" % (yy.loc[q4, "trump"].sum(), yy.loc[q4, "biden"].sum()))

    # ---- B. market expectations
    S = {k: pd.to_numeric(pd.read_csv(ROOT + f"data/raw/ext/fred/{k}.csv", index_col=0, parse_dates=True).iloc[:, 0],
                          errors="coerce").dropna() for k in ["T5YIE", "T10YIE", "T5YIFR"]}
    rows = []
    for k, s in S.items():
        for dt, what, sign in EVENTS:
            t = pd.Timestamp(dt)
            i0 = s.index.searchsorted(t) - 1                 # last close before the news day
            i1 = s.index.searchsorted(t, side="right")       # first close after the news day
            n = i1 - i0
            ch = s.diff(n).dropna()["2015":"2019"]
            lo, hi = np.percentile(ch, [5, 95])
            c = float(s.iloc[i1] - s.iloc[i0])
            rows.append(dict(series=k, date=dt, event=what, expected_sign=sign, window=f"{s.index[i0].date()} to {s.index[i1].date()}",
                             change=c, ordinary_p5=lo, ordinary_p95=hi, outside_ordinary=bool(c < lo or c > hi)))
    ev = pd.DataFrame(rows)
    ev.round(3).to_csv(ROOT + "output/ext/e14_events.csv", index=False)
    print(ev.round(3).to_string())
    deal_week()

    # ---- C. timing
    gp4 = 100 * (pi / pi.shift(4) - 1)
    for k, t in [("IIJA signed (2021Q4)", "2021-10-01"), ("BBB House / Manchin no (2021Q4)", "2021-10-01"),
                 ("IRA signed (2022Q3)", "2022-07-01"), ("peak", gp4["2020":"2024"].idxmax())]:
        print(f"{k}: PCE inflation, 4-quarter, {pd.Timestamp(t).date()} = {gp4[pd.Timestamp(t)]:.2f}")


def deal_week():
    """The July 27, 2022 window holds two pieces of news: the FOMC's 3/4-point hike (statement at 2:00 p.m. EDT, Fed
    press release monetary20220727a, data/raw/ext/laws/fomc_pr_20220727.html) and the Manchin-Schumer deal, announced
    "hours after the Senate passed the CHIPS and Science Act" that day (Wikipedia; exact time not verified). Day-by-day
    1-day changes, July 25-29, against ordinary 1-day changes in 2015-2019."""
    rows = []
    for k in ["T5YIE", "T10YIE", "T5YIFR"]:
        s = pd.to_numeric(pd.read_csv(ROOT + f"data/raw/ext/fred/{k}.csv", index_col=0, parse_dates=True).iloc[:, 0],
                          errors="coerce").dropna()
        lo, hi = np.percentile(s.diff().dropna()["2015":"2019"], [5, 95])
        w = s["2022-07-22":"2022-07-29"]
        for t, c in w.diff().dropna().items():
            rows.append(dict(series=k, day=str(t.date()), change_1day=float(c), ordinary_p5=lo, ordinary_p95=hi))
    o = pd.DataFrame(rows)
    o.round(3).to_csv(ROOT + "output/ext/e14_deal_week.csv", index=False)
    print(o.round(3).to_string())


if __name__ == "__main__":
    main()
