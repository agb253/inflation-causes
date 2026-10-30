"""Quarterly data for the unified causes model (src/unified_model.py). Every series is read from a file in data/raw/.

Inflation block (Bernanke-Blanchard, re-based on PCE):
  gp    400 x dlog PCE price index                BEA NIPA T2.3.4 line 1 (DPCERG), data/raw/bea/NipaDataQ.txt
  grpe  400 x dlog(PCE energy price / ECI)        BEA DNRGRG / lci (ECI, B&B data file)
  grpf  400 x dlog(PCE food-at-home price / ECI)  BEA DFXARG / lci
  gw, exp1, exp10, vu, productivity               B&B / Lorenzoni data file data/raw/data_us_new.csv (unchanged)
  shortage                                        NY Fed GSCPI, quarterly mean (as fig9)
Demand block (what moves job vacancies per unemployed, vu):
  fed_fiscal  federal social benefits to persons + current grants to states/localities + subsidies
              (BEA T3.2 lines 28, 31, 36: B087RC, B089RC, B096RC), % of nominal potential GDP
              (CBO GDPPOT x GDPDEF/100), minus its own 1990-2019 linear trend
  policy_gap  [used only by the abandoned first test, see METHOD_UNIFIED.md] SF Fed proxy funds rate (Choi, Doh, Foerster & Martinez, FRBSF EL 2022-30; captures QE and forward
              guidance) minus the Taylor (1993) rule rate (constants in TAYLOR below, source in METHOD_UNIFIED.md)
  stringency  Oxford COVID-19 Government Response Tracker, US national StringencyIndex_Average, quarterly mean;
              0 before 2020; the tracker ends 2022-12-31. After it (STRINGENCY_AFTER = "fade", default): falls linearly
              from the 2022Q4 value to 0 in 2023Q2, the quarter the federal COVID-19 Public Health Emergency expired
              (May 11, 2023: HHS, https://www.hhs.gov/coronavirus/covid-19-public-health-emergency/index.html).
              "hold" = keep the 2022Q4 value (robustness variant).
"""
import csv
import numpy as np
import pandas as pd
import bb_model as m

RAW = "data/raw/"
STRINGENCY_AFTER = "fade"
TAYLOR = dict(r_star=2.0, pi_star=2.0, a_pi=0.5, a_gap=0.5)   # Taylor (1993); see METHOD_UNIFIED.md for the quote


def nipa(codes):
    rows = [(c, p, float(v.replace(",", ""))) for c, p, v in csv.reader(open(RAW + "bea/NipaDataQ.txt")) if c in codes]
    d = pd.DataFrame(rows, columns=["s", "q", "v"]).pivot(index="q", columns="s", values="v")
    d.index = pd.PeriodIndex(d.index, freq="Q").to_timestamp()
    return d


def fred(s):
    d = pd.read_csv(RAW + f"fred2/{s}.csv", parse_dates=[0], index_col=0).iloc[:, 0]
    return d


def qmean(s):
    q = s.groupby(s.index.to_period("Q")).mean(); q.index = q.index.to_timestamp(); return q


def load():
    d = m.load(RAW + "data_us_new.csv")
    n = nipa({"DPCERG", "DNRGRG", "DFXARG", "B087RC", "B089RC", "B096RC"})
    d["pce"], d["pce_energy"], d["pce_food"] = n.DPCERG, n.DNRGRG, n.DFXARG
    # GSCPI
    g = pd.read_excel(RAW + "nyfed/gscpi_data.xlsx", sheet_name="GSCPI Monthly Data", usecols=[0, 1]).dropna()
    g["Date"] = pd.to_datetime(g.Date, format="%d-%b-%Y"); gq = qmean(g.set_index("Date").GSCPI.astype(float))
    d["shortage"] = gq.reindex(d.index).fillna(gq[:"2019-10-01"].mean())     # before 1998: 1998-2019 mean (as fig9)
    # fiscal
    pot = qmean(fred("GDPPOT")) * qmean(fred("GDPDEF")) / 100
    f = 100 * (n.B087RC + n.B089RC + n.B096RC) / 1000 / pot.reindex(n.index)      # NIPA in $ millions, GDPPOT in $ billions
    pre = f["1990-01-01":"2019-10-01"]; t = np.arange(len(f)); t0 = f.index.get_loc(pre.index[0])
    fit = np.polyfit(t[t0:t0 + len(pre)], pre.values, 1)
    d["fed_fiscal_raw"] = f.reindex(d.index)
    d["fed_fiscal"] = (f - np.polyval(fit, t)).reindex(d.index)
    # monetary stance
    p = pd.read_excel(RAW + "shadow/proxy-funds-rate-data.xlsx", sheet_name="Monthly", header=0)
    p["Date"] = pd.to_datetime(p.Date); pfr = qmean(p.set_index("Date")["Proxy funds rate"].astype(float))
    core = qmean(fred("PCEPILFE")); infl = 100 * np.log(core).diff(4)
    gap = 100 * (qmean(fred("GDPC1")) - qmean(fred("GDPPOT"))) / qmean(fred("GDPPOT"))
    T = TAYLOR
    taylor = T["r_star"] + infl + T["a_pi"] * (infl - T["pi_star"]) + T["a_gap"] * gap
    d["pfr"], d["taylor"] = pfr.reindex(d.index), taylor.reindex(d.index)
    d["policy_gap"] = d.pfr - d.taylor
    # COVID restrictions
    o = pd.read_csv(RAW + "oxcgrt/OxCGRT_USA_national_stringency.csv")
    o["D"] = pd.to_datetime(o.Date.astype(str)); s = qmean(o.set_index("D").StringencyIndex_Average)
    d["stringency"] = s.reindex(d.index)
    d.loc[d.index < "2020-01-01", "stringency"] = 0.0
    last = d.stringency.last_valid_index()
    if STRINGENCY_AFTER == "fade":
        tail = d.index[d.index > last]
        for i, t in enumerate(tail):
            d.loc[t, "stringency"] = max(0.0, d.stringency[last] * (1 - (i + 1) / 2))
    d["stringency"] = d.stringency.ffill()
    return d
