"""output/REPRODUCE_TABLE.md + output/reproduce_long.csv: every cause by quarter, with the data series, equations
and code behind each number, and 68% / 90% ranges. Also the grouped totals, whose ranges are much narrower than the
single lines' because the lines' errors offset (output/uncertainty_groups.csv).
Inputs: output/unified_causes_quarterly.csv, output/unified_draws.npy (both written by src/unified_model.py)."""
import numpy as np
import pandas as pd

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
o = pd.read_csv(ROOT + "output/unified_causes_quarterly.csv", index_col=0)
yd = np.load(ROOT + "output/unified_draws.npy")
cols = list(pd.read_csv(ROOT + "output/unified_draws_columns.csv").line)
Q = list(o.index)
Q4 = [i for i, q in enumerate(Q) if q.endswith("Q4") and int(q[:4]) >= 2021]
CAUSES = [c for c in cols if not c.startswith("memo") and c != "unexplained"]

# Numbered equations. Constants are the estimates printed in output/unified_model_run.log; derivations and sources
# in output/TABLE_UNIFIED.md (items 1-9) and output/METHOD_UNIFIED.md.
EQ = [
    ("E1", "Contribution of cause k: c_k,t = pi_t(all inputs) - pi_t(input k removed). pi is simulated with E10-E12 from "
           "2020Q1 on; quarters before 2020 are actual history.", "unified_model.causes_inflation"),
    ("E2", "Year-over-year number in the table: average of the last 4 quarterly (annualized) c_k, times r_t = percent "
           "change / log change of the PCE price index (DPCERG), so all lines sum to official inflation.", "unified_model.yoy, save"),
    ("E3", "Relief to GDP: G_t = 100/PotGDP_t x sum_p m_p x sum_h (1-lambda) lambda^h X_p,t-h; lambda = 0.74; m_p from "
           "CBO 56537 Table 3 (0.36 PPP, 0.67 unemployment, 0.60 rebates, 0.88 state & local, 0.78 other, 0.37 revenue). "
           "Payments before March 2021 = Trump; from March 2021 = Biden.", "fiscal_by_law.run_variant"),
    ("E4", "GDP to unemployment (Okun): du_t = beta x G_t, beta = -0.815 (s.e. 0.037), estimated 1990-2019.", "unified_model.okun"),
    ("E5", "Pent-up demand: forced saving = sum over 2020-21 of (2015-19 log-linear trend - actual) real PCE = $786 "
           "billion (2017 $); spent evenly 2021Q2-2023Q3; G_t = 0.78 x spending_t / PotGDP_t; then E4.", "pentup.effect"),
    ("E6", "Fed to unemployment: monthly proxy SVAR (12 lags, 1977-2019), instrument MPS (F = 9.5); counterfactual "
           "policy shocks hold the proxy funds rate at its 2019Q4 level (2.35%) in each episode window.", "fed_svar.py, unified_model.fed_effect"),
    ("E7", "COVID shutdown to unemployment: du_t = g0 s_t + g1 s_t-1, g0 = 15.25 (2.33), g1 = -4.28 (2.36), OLS "
           "2020Q1-2022Q4, no constant; s = Oxford stringency / 100, faded to 0 by 2023Q2.", "unified_model.covid_fit"),
    ("E8", "Unemployment to V/U: log(V/U)_t = a + b u_t, b = -0.290 (1990-2019). Cause k's V/U change = "
           "L_t x b x du_k,t with L_t = (V/U_t - V/U_ref) / (log V/U_t - log V/U_ref), so the parts add up exactly.", "unified_model.run_once"),
    ("E9", "Worker shortage: e_t - e_2019Q4, where e_t = log(V/U)_t - a - b u_t (the V/U that unemployment doesn't "
           "explain); weighted as in E8.", "unified_model.run_once"),
    ("E10", "Wage growth (Bernanke-Blanchard): gw_t = c + 4 lags gw + 4 lags V/U + 4 lags 1-yr expectations + 4 lags "
            "catch-up + productivity; own + expectation lags sum to 1; 1990-2019.", "bb_model.estimate"),
    ("E11", "Price inflation: gp_t = c + 4 lags gp + gw (0-4 lags) + energy/ECI, food/ECI, GSCPI, greed (0-4 lags each) "
            "+ productivity; own lags + wage terms sum to 1; 1990-2024.", "bb_model.estimate, unified_model.estimate_with_greed"),
    ("E12", "Expectations: 10-yr on gp (0-4) + own lags; 1-yr on own lags + 10-yr (0-4) + gp (0-4); each sums to 1.", "bb_model.estimate"),
    ("E13", "Greed: residual of margin_t = -400 dlog(1 - unit profits / price) regressed on GSCPI, V/U, energy, food, "
            "wages (0-4 lags each), 1990-2024 (R^2 0.51).", "unified_model.add_greed"),
    ("E14", "Pre-existing: pi_t with every input at its 2019 reference (no relief, no Fed moves after 2019, energy and "
            "food relative prices flat, GSCPI and productivity at 1998/1990-2019 means), plus pre-2020 Fed surprises.", "unified_model.causes_inflation"),
    ("E15", "Not explained: actual - model (E10-E12 with every actual input), plus productivity and energy & food "
            "shocks after 2023Q1.", "unified_model.causes_inflation"),
]

ROWS = [  # key, label, [draw columns], data series, equations
    ("actual_pce_yoy", "Actual PCE inflation", None, "BEA DPCERG (NIPA 2.3.4)", "100 x (P_t / P_t-4 - 1)"),
    ("pre_existing", "Pre-existing (end-2019 momentum)", ["baseline", "fed_pre2020"], "all model inputs at 2019 reference; data_us_new.csv", "E14, E10-E12, E2"),
    ("trump", "Relief paid under Trump", ["trump"], "BEA pandemic program tables; CBO 56537 T2-3; FRED GDPPOT, UNRATE, NROU, GDPC1; V/U", "E3, E4, E8, E10-E12, E1, E2"),
    ("biden", "Relief paid under Biden", ["biden"], "same as Trump relief", "E3, E4, E8, E10-E12, E1, E2"),
    ("fed_easing", "Fed 2020-21 cuts + QE", ["fed_easing"], "SF Fed MPS + VAR data; SF Fed proxy funds rate; UNRATE", "E6, E8, E10-E12, E1, E2"),
    ("fed_hikes", "Fed 2022-23 hikes", ["fed_hikes"], "same as Fed cuts", "E6, E8, E10-E12, E1, E2"),
    ("pentup", "Pent-up demand", ["pentup"], "BEA DPCERX (NIPA 1.1.6); CBO 56537 T3; GDPPOT", "E5, E4, E8, E10-E12, E1, E2"),
    ("covid_other", "COVID shutdown drag", ["covid_other"], "OxCGRT stringency; UNRATE; plus BEA DNRGRG, DFXARG 2020Q1-2021Q4", "E7, E8, E10-E12 (+E11 energy/food), E1, E2"),
    ("worker_shortage", "Worker shortage", ["worker_shortage"], "V/U (JOLTS via data_us_new.csv); UNRATE", "E9, E8, E10-E12, E1, E2"),
    ("energy_war", "War in Ukraine (energy & food)", ["energy_war"], "BEA DNRGRG, DFXARG / ECI, 2022Q1-2023Q1", "E11, E1, E2"),
    ("shortage", "Supply chains", ["shortage"], "NY Fed GSCPI", "E11, E1, E2"),
    ("greed", "Greedflation", ["greed"], "BEA A463RD, A455RD (NIPA 1.15)", "E13, E11, E1, E2"),
    ("other_unexplained", "Other & not explained", ["gpty", "unexplained", "energy_after"], "everything above", "E15"),
]
GROUPS = [  # sums whose ranges are much tighter than their parts'
    ("grp_labor", "Total: all labor-market causes (relief + pent-up + Fed + COVID + worker shortage)",
     ["trump", "biden", "pentup", "fed_easing", "fed_hikes", "fed_pre2020", "covid_other", "worker_shortage"]),
    ("grp_pandemic", "Total: pandemic and the response to it (relief + pent-up + COVID drag)", ["trump", "biden", "pentup", "covid_other"]),
    ("grp_relief", "Total: Biden + Trump relief", ["trump", "biden"]),
    ("grp_supply", "Total: supply shocks (supply chains + war)", ["shortage", "energy_war"]),
    ("model_total", "Model estimate (sum of all causes + pre-existing)", CAUSES),
]


def series(keys):
    return yd[:, :, [cols.index(k) for k in keys]].sum(axis=2)          # draws x quarters


def point(key, keys):
    if key in o:
        return o[key].values
    return o[keys].sum(axis=1).values


long, wide, cum = [], [], []
for key, label, keys, data, eqs in ROWS + [(k, l, ks, "sum of the lines named", "sum") for k, l, ks in GROUPS]:
    p = point(key, keys) if keys else o[key].values
    s = series(keys) if keys else None
    pc = lambda a, q: np.percentile(a, q, axis=0)
    rng = {q: pc(s, q) for q in (5, 16, 84, 95)} if s is not None else {}
    for j, qq in enumerate(Q):
        long.append(dict(line=key, label=label, quarter=qq, value=round(p[j], 3),
                         **{f"p{q}": round(rng[q][j], 3) for q in rng}, data=data, equations=eqs))
    tot = p[Q4].sum()
    c = dict(line=key, label=label, total_2021_24=round(tot, 3))
    if s is not None:
        st = s[:, Q4].sum(axis=1)
        c.update({f"p{q}": round(np.percentile(st, q), 3) for q in (5, 16, 50, 84, 95)},
                 prob_positive=round(float(np.mean(st > 0)), 2))
    cum.append(c)
    wide.append((label, p, data, eqs, c))

pd.DataFrame(long).to_csv(ROOT + "output/reproduce_long.csv", index=False)
cumdf = pd.DataFrame(cum).set_index("line")
cumdf.to_csv(ROOT + "output/uncertainty_groups.csv")

# pairwise "A added more than B" probabilities over the 2021-24 total
tot = {k: series([k])[:, Q4].sum(axis=1) for k in CAUSES}
PAIRS = [("shortage", "biden"), ("shortage", "trump"), ("biden", "trump"), ("shortage", "worker_shortage"),
         ("worker_shortage", "biden"), ("energy_war", "pentup")]
NAMES = dict((k, l) for k, l, *_ in ROWS)
prob = [(NAMES[a], NAMES[b], float(np.mean(tot[a] > tot[b]))) for a, b in PAIRS]
sup = series(["shortage", "energy_war"])[:, Q4].sum(1)
dem = series(["trump", "biden", "pentup", "fed_easing", "fed_hikes", "fed_pre2020"])[:, Q4].sum(1)
prob.append(("Supply shocks (group)", "Relief + pent-up + Fed", float(np.mean(sup > dem))))
sup2 = series(["shortage", "energy_war", "worker_shortage"])[:, Q4].sum(1)
prob.append(("Supply shocks + worker shortage", "Relief + pent-up + Fed", float(np.mean(sup2 > dem))))
prob.append(("Supply chains", "All relief (Trump + Biden)", float(np.mean(tot["shortage"] > tot["trump"] + tot["biden"]))))
pd.DataFrame(prob, columns=["A", "B", "P(A > B)"]).round(2).to_csv(ROOT + "output/uncertainty_pairs.csv", index=False)

f2 = lambda v: f"{v:+.2f}" if abs(v) >= 0.005 else "0.00"
hdr = "| Line | " + " | ".join(Q) + " | 2021-24 total | 68% range | 90% range | Data | Equations |"
lines = [hdr, "|" + "---|" * (len(Q) + 6)]
for label, p, data, eqs, c in wide:
    r68 = f"{c['p16']:+.1f} to {c['p84']:+.1f}" if "p16" in c else ""
    r90 = f"{c['p5']:+.1f} to {c['p95']:+.1f}" if "p5" in c else ""
    lines.append(f"| {label} | " + " | ".join(f2(v) for v in p) + f" | {c['total_2021_24']:+.1f} | {r68} | {r90} | {data} | {eqs} |")
tbl = "\n".join(lines)
eqt = "\n".join(f"| {k} | {t} | `src/{c.split(',')[0].split('.')[0]}.py` ({c}) |" for k, t, c in EQ)
pr = "\n".join(f"| {a} | {b} | {p:.0%} |" for a, b, p in prob)
src = pd.read_csv(ROOT + "output/uncertainty_sources.csv", index_col=0) if __import__("os").path.exists(ROOT + "output/uncertainty_sources.csv") else None

doc = f"""# Every cause, every quarter: values, data and equations

Units: percentage points of year-over-year PCE inflation (each quarter = the four quarters ending then; equation E2).
Rows are causes; the last columns give the 2021-24 total (the four Q4-over-Q4 rates added up), its 68% and 90% ranges
from 1,000 redraws, the data series used and the equations (numbered below). Every line except the groups adds up, with
pre-existing and "other & not explained", to actual inflation in every quarter.

- **Same numbers, one row per cause and quarter, with 68% and 90% ranges for each quarter:** `output/reproduce_long.csv`.
- **Rebuild:** `bash run_report.sh` (all numbers); this table alone: `python src/make_reproduce_table.py`.
- **Data files, links, download dates:** `output/TABLE_UNIFIED.md`, section "Data sources".

## Table R1. Contribution of each cause, by quarter

{tbl}

## Equations

| # | Equation | Code |
|---|---|---|
{eqt}

To reproduce one cell: run `src/unified_model.py` (it prints every estimated constant to
`output/unified_model_run.log`), then for cause k compute E1 for each quarter, average the last four quarters, and
multiply by r_t (E2). The point values above are `output/unified_causes_quarterly.csv`, column k.

## Which comparisons the data settle (share of 1,000 redraws, 2021-24 totals)

| A | B | A added more than B in |
|---|---|---|
{pr}
"""
open(ROOT + "output/REPRODUCE_TABLE.md", "w").write(doc)
print(cumdf.to_string())
print(pd.DataFrame(prob).to_string())
