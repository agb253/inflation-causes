import json, numpy as np, pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter as CL
import sys; sys.path.insert(0, "src"); import bb_model as m
O = "output/"
pt = pd.read_csv(O + "decomp_point.csv", index_col=0, parse_dates=True)
B = {k: pd.read_csv(O + f"decomp_{k}.csv", index_col=0, parse_dates=True) for k in ["lo90", "hi90", "lo68", "hi68"]}
cum = pd.read_csv(O + "cumulative_2020q1_2024q4.csv", index_col=0)
ann = pd.read_csv(O + "calendar_year_average.csv")
coef = pd.read_csv(O + "coefficients.csv")
rob = pd.read_csv(O + "robustness_point.csv", parse_dates=["date"])
quotes = json.load(open(O + "paper_quotes.json"))
x = m.build(m.load(m.RAW + "data_us_new.csv"))
pre = x.loc[:"2019-10-01"]
ref = {"shortage": pre.shortage.mean(), "vu": x.vu.loc["2019-10-01"], "gpty": pre.gpty.mean()}

PAPER = "Blanchard & Bernanke, 'What Caused the U.S. Pandemic-Era Inflation?', NBER WP 31417 (June 2023) https://www.nber.org/papers/w31417 ; published as Bernanke & Blanchard, AEJ: Macroeconomics (2025) https://www.aeaweb.org/articles?id=10.1257/mac.20230195"
REPL = "Lorenzoni replication package https://github.com/luigilor/bernanke-blanchard23 (commit 7712ad9, files empirics/data/data_us_new.csv, empirics/code/bl_be_us.R)"
SRC = {
 "energy": ("grpe = 400*dlog(CPI energy / ECI wages), actual", "BLS CPI-U energy, SA: https://data.bls.gov/timeseries/CUSR0000SA0E ; ECI: https://data.bls.gov/timeseries/CIS2020000000000I"),
 "food": ("grpf = 400*dlog(CPI food / ECI wages), actual", "BLS CPI-U food, SA: https://data.bls.gov/timeseries/CUSR0000SAF1 ; ECI: https://data.bls.gov/timeseries/CIS2020000000000I"),
 "shortages": ("Google 'shortage' search index, actual", "Google Trends, US, term 'shortage' https://trends.google.com/trends/explore?geo=US&q=shortage (NOT independently re-pulled; PDF p.24 describes it)"),
 "labor_tightness": ("v/u = job openings / unemployed, actual", "BLS JOLTS openings https://data.bls.gov/timeseries/JTS000000000000000JOL ; unemployed https://data.bls.gov/timeseries/LNS13000000"),
 "productivity": ("gpty = 8-quarter avg of 400*dlog(productivity), actual", "BLS nonfarm business productivity (closest match PRS85006093) https://data.bls.gov/timeseries/PRS85006093"),
 "baseline_pre2020": ("simulation with every shock set to its pre-2020 reference value", "Equation intercepts + 1y/10y expectations dynamics (Cleveland Fed https://www.clevelandfed.org/indicators-and-data/inflation-expectations)"),
 "unexplained": ("actual CPI inflation minus the model's simulated baseline path", "BLS CPI-U all items, SA: https://data.bls.gov/timeseries/CUSR0000SA0"),
}
CF = {"energy": "counterfactual: relative energy price growth = 0", "food": "counterfactual: relative food price growth = 0",
      "shortages": f"counterfactual: shortage index = {ref['shortage']:.1f} (1990Q1-2019Q4 mean)", "labor_tightness": f"counterfactual: v/u = {ref['vu']:.3f} (2019Q4 value)",
      "productivity": f"counterfactual: gpty = {ref['gpty']:.2f}% (1990Q1-2019Q4 mean)", "baseline_pre2020": "all five counterfactuals applied at once", "unexplained": "residual; no counterfactual"}
KEYCOL = {"energy": "grpe", "food": "grpf", "shortages": "shortage", "labor_tightness": "vu", "productivity": "gpty"}
CATS = {"energy": "4 Geopolitical events (energy/food shocks)", "food": "4 Geopolitical events (energy/food shocks)",
        "shortages": "1 COVID-19 direct effects (supply disruptions) [partial proxy]", "labor_tightness": "6 Labor market disruptions",
        "productivity": "7 Pre-existing structural issues [partial]", "baseline_pre2020": "7 Pre-existing structural issues [partial]",
        "unexplained": "Not attributed by the model"}
LAB = {"baseline_pre2020": "Pre-2020 baseline", "shortages": "Shortages", "energy": "Energy prices", "food": "Food prices",
       "labor_tightness": "Labor-market tightness (v/u)", "productivity": "Productivity trend", "unexplained": "Unexplained"}
ORDER = ["shortages", "energy", "food", "labor_tightness", "productivity", "baseline_pre2020", "unexplained"]
qlab = lambda d: f"{d.year} Q{(d.month-1)//3+1}"

hdr = Font(bold=True, color="FFFFFF"); fill = PatternFill("solid", fgColor="2F4858"); wrap = Alignment(wrap_text=True, vertical="top")
def sheet(wb, name, df_or_rows, widths=None, header=None):
    ws = wb.create_sheet(name)
    rows = df_or_rows
    for r in rows: ws.append(r)
    for c in ws[1]: c.font = hdr; c.fill = fill; c.alignment = wrap
    ws.freeze_panes = "A2"
    for i, w in enumerate(widths or [], 1): ws.column_dimensions[CL(i)].width = w
    for row in ws.iter_rows(min_row=2):
        for c in row: c.alignment = wrap
    return ws

wb = Workbook(); wb.remove(wb.active)
# ---- README
ws = wb.create_sheet("README")
readme = [
 ["What this is"], ["Quarterly decomposition of U.S. CPI inflation, 2020Q1-2024Q4, into causes, from the Bernanke-Blanchard model. No coefficient or constant is chosen by hand: every one is an OLS estimate from the data in the 'Inputs' sheet, and the 'Coefficients' sheet compares them with the paper's published values."],
 [""], ["Units"], ["Contributions are percentage points of ANNUALIZED quarterly CPI inflation (400 x quarterly log change). Cumulative figures are log points of the price level (sum of annualized rates / 4)."],
 [""], ["How a number is produced"],
 ["1. Estimate 4 equations (wages, prices, 1-yr and 10-yr expectations) by restricted least squares; wage and expectations equations on 1990Q1-2019Q4, price equation on 1990Q1-2025Q1 (PDF p.13: shortage term needs covid-era variation)."],
 ["2. Simulate the model from 2020Q1 with all actual inputs (baseline path)."],
 ["3. Re-simulate with ONE input set to its pre-2020 reference value (see 'How computed' column). Contribution = baseline path minus counterfactual path. The model is linear, so contributions add exactly."],
 ["4. Unexplained = actual CPI inflation minus baseline path. Check on sheet 'Sum_check' (Excel formulas)."],
 ["5. Error bars: 2,000 draws of every coefficient from its estimated covariance; the full decomposition is re-run per draw. 68% = 16th-84th percentile, 90% = 5th-95th."],
 [""], ["What the error bars do NOT include"], ["Model-specification uncertainty, measurement error in the inputs, and uncertainty in the 'shortage' proxy. See 'Robustness' for how the answer moves under data-vintage and specification changes."],
 [""], ["Categories NOT separately identified by this model"], ["Fiscal stimulus, Federal Reserve policy, corporate profit-taking, and other government interventions have no bar of their own. See 'Category_map' for why, with page-cited quotes from the paper. They are not set to zero; they are absent."],
 [""], ["Primary references"], [PAPER], [REPL],
 [""], ["Reproduce"], ["python src/run_all.py && python src/make_figures.py && python src/build_workbook.py   (inputs in data/raw/, with SHA-256 and sources in data/raw/SOURCE.txt)"],
]
for r in readme: ws.append(r)
ws.column_dimensions["A"].width = 150
for row in ws.iter_rows():
    for c in row: c.alignment = wrap
for r in (1, 4, 6, 12, 15, 17, 20): ws.cell(r + 0, 1).font = Font(bold=True)

# ---- Quarterly table (long)
rows = [["Quarter", "Cause (model component)", "Your category", "Contribution (pp, annualized)", "68% low", "68% high", "90% low", "90% high",
         "Actual CPI inflation (pp, annualized)", "Key input this quarter", "How computed", "Data source (URL)", "Method reference"]]
for d in pt.index:
    for c in ORDER:
        ki = f"{KEYCOL[c]} = {x.loc[d, KEYCOL[c]]:.2f}" if c in KEYCOL else ""
        rows.append([qlab(d), LAB[c], CATS[c], round(pt.loc[d, c], 3), round(B["lo68"].loc[d, c], 3), round(B["hi68"].loc[d, c], 3),
                     round(B["lo90"].loc[d, c], 3), round(B["hi90"].loc[d, c], 3), round(pt.loc[d, "actual_cpi"], 3), ki,
                     f"{SRC[c][0]}; {CF[c]}", SRC[c][1], PAPER if c != "unexplained" else "Residual of the same model"])
sheet(wb, "Quarterly_table", rows, [9, 24, 34, 14, 9, 9, 9, 9, 14, 20, 60, 70, 50])
pd.DataFrame(rows[1:], columns=rows[0]).to_csv(O + "quarterly_table.csv", index=False)

# ---- Sum check with live formulas
ws = wb.create_sheet("Sum_check")
ws.append(["Quarter", "Actual CPI"] + [LAB[c] for c in ORDER[:-1]] + ["Unexplained (= actual - sum of causes)", "Sum of all parts", "Check (should be 0)"])
for i, d in enumerate(pt.index, start=2):
    ws.append([qlab(d), round(pt.loc[d, "actual_cpi"], 4)] + [round(pt.loc[d, c], 4) for c in ORDER[:-1]] +
              [f"=B{i}-SUM(C{i}:H{i})", f"=SUM(C{i}:I{i})", f"=B{i}-J{i}"])
for c in ws[1]: c.font = hdr; c.fill = fill; c.alignment = wrap
ws.freeze_panes = "B2"
for i in range(1, 12): ws.column_dimensions[CL(i)].width = 16
ws.cell(len(pt) + 3, 1, "Unexplained is computed by formula from the rounded causes; the model's own unrounded residual is in Quarterly_table.")

# ---- Calendar year and cumulative
rows = [["Period", "Cause", "Point (pp)", "68% low", "68% high", "90% low", "90% high", "Note"]]
for _, r in ann.iterrows():
    nm = "Actual CPI inflation" if r.component == "actual_cpi" else LAB[r.component]
    rows.append([int(r.year), nm, round(r.point, 3), *(round(r[k], 3) if pd.notna(r[k]) else "" for k in ["lo68", "hi68", "lo90", "hi90"]),
                 "mean of the four quarterly annualized rates (~Q4/Q4 log change)"])
for c, r in cum.iterrows():
    rows.append(["2020Q1-2024Q4 cumulative", LAB[c], round(r.point, 3), round(r.lo68, 3), round(r.hi68, 3), round(r.lo90, 3), round(r.hi90, 3), "log points of price level; actual total = %.2f" % r.actual])
sheet(wb, "Annual_and_cumulative", rows, [24, 28, 11, 10, 10, 10, 10, 60])

# ---- Category map
cm = [["Your category", "How this model treats it", "Shown in chart as", "Evidence (quote copied from paper; PDF page)"],
 ["1 COVID-19 direct effects (shutdowns, supply disruptions)", "Partly captured: the 'shortage' index is a proxy for 'the combined effects of the shift in demand towards durable goods and the disruptions of and limits on supply'. It is not a clean measure of lockdowns or layoffs.", "Shortages", f"\"{quotes['google']['quote']}\" ... (PDF p.{quotes['google']['pdf_page'][0]})"],
 ["2 Government fiscal stimulus", "NOT separately identified. In this model fiscal policy acts upstream, through labor-market tightness and demand for goods. A third-party extension (Lorenzoni) estimates a fiscal channel, but its fiscal series is undocumented in the repo and could not be traced to a source, so it is not charted.", "(no bar)", f"\"{quotes['fiscal_not_needed']['quote']}\" (PDF p.{quotes['fiscal_not_needed']['pdf_page'][0]}); \"{quotes['vu_given']['quote']}\" (PDF p.{quotes['vu_given']['pdf_page'][0]}) [paper uses math-italic v/u]"],
 ["3 Federal Reserve monetary policy", "NOT separately identified. Same reason as fiscal: policy works through v/u and demand, which the model takes as given.", "(no bar)", f"\"{quotes['vu_given']['quote']}\" (PDF p.{quotes['vu_given']['pdf_page'][0]}); \"{quotes['overall']['quote']}\" (PDF p.{quotes['overall']['pdf_page'][0]})"],
 ["4 Geopolitical events (Ukraine war, energy/food shocks)", "Captured as energy and food prices relative to wages. These bars include ALL energy/food price movement (e.g. the 2020 collapse and the 2021 reopening rebound), not only the Ukraine war; the model cannot separate causes of the price move.", "Energy prices; Food prices", "Variable definitions: PDF p.14 (grpe, grpf = CPI energy/food relative to ECI)"],
 ["5 Corporate profit-taking / margins", "NOT an independent variable. The paper says markups rise endogenously when demand meets limited supply, so profit effects are inside the Shortages bar, not separate from it. This is a modelling choice, not evidence that profits did not matter.", "(no bar; inside Shortages)", f"\"{quotes['markup']['quote']}\" (PDF p.{quotes['markup']['pdf_page'][0]})"],
 ["6 Labor market disruptions (Great Resignation, wage pressure)", "Captured as vacancy/unemployment tightness plus its pass-through to wages and prices. Reasons for the tightness (resignations, benefits, layoffs) are not separated.", "Labor-market tightness (v/u)", "Wage equation, ECI and v/u definitions: PDF p.15"],
 ["7 Pre-existing structural issues (housing, healthcare)", "Only partly: the 'pre-2020 baseline' is what the model produces with no 2020+ shocks (trend, expectations), and the productivity trend. Housing and healthcare costs are not modelled.", "Pre-2020 baseline; Productivity trend", f"Productivity definition: \"{quotes['gpty_def']['quote']}\" (PDF p.{quotes['gpty_def']['pdf_page'][0]})"],
 ["8 Other government interventions (student loans, eviction moratoria)", "NOT identified.", "(no bar)", "Absent from the paper's model."]]
sheet(wb, "Category_map", cm, [40, 80, 28, 100])

# ---- Coefficients
cr = [["Equation", "Term", "Published beta (authors' coefficient file)", "My estimate on the ORIGINAL data (to 2023Q1)", "Std. error", "|diff| / SE", "Estimate used (data to 2025Q1)", "Std. error (used)", "N (original)", "N (used)"]]
for _, r in coef.iterrows():
    cr.append([{"gp": "price", "gw": "wage", "exp10": "10y expectations", "exp1": "1y expectations"}[r.equation], r.term, round(r.published_beta, 4), round(r.est_original_data, 4), round(r.se_original, 4),
               round(r.abs_diff_vs_published_in_SE, 2) if pd.notna(r.abs_diff_vs_published_in_SE) else "", round(r.est_used, 4), round(r.se_used, 4), int(r.n_original), int(r.n_used)])
ws = sheet(wb, "Coefficients", cr, [18, 14, 22, 22, 10, 10, 20, 14, 10, 10])
ws.cell(len(cr) + 2, 1, "Restrictions (copied from bl_be_us.R): wage eq: own lags + 1y-expectation lags sum to 1; price eq: own lags + wage (current+lags) sum to 1; expectations eqs: all coefficients sum to 1. Source of published betas: auxil/coef_*.xlsx in the replication repo.")
ws.cell(len(cr) + 3, 1, "Price-equation productivity: the paper's Table 3 prints 'lag -1' with sum -0.143 (PDF p.25), but the authors' own coefficient file labels it unlagged (magpty) and only the same-row term reproduces -0.143. The R script's lagged version gives -0.076. Cause unresolved (original Stata code not available); effect on results is small (see Robustness).")

# ---- Data sources & verification
vr = [["Model column", "What it is (per paper)", "Independent check done here", "Result", "Source URL"],
 ["cpi", "CPI-U all items, SA, last month of quarter (identified by comparison)", "Pulled BLS API CUSR0000SA0, compared quarter-end values, 154 quarters", "90% of quarters within 0.05 index pts; max gap 0.24 (0.08%), consistent with later seasonal-factor revisions", "https://data.bls.gov/timeseries/CUSR0000SA0"],
 ["energy_cpi", "CPI-U energy, SA, last month of quarter", "BLS API CUSR0000SA0E", "84% within 0.05; max gap 3.2 pts (1.1%) - larger seasonal revisions in energy", "https://data.bls.gov/timeseries/CUSR0000SA0E"],
 ["food_cpi", "CPI-U food, SA, last month of quarter", "BLS API CUSR0000SAF1", "90% within 0.05; max gap 0.45 (0.14%)", "https://data.bls.gov/timeseries/CUSR0000SAF1"],
 ["lci", "ECI wages & salaries; pre-2001 spliced series ECS10001I (PDF p.15, fn.6)", "Compared quarterly growth with BLS ECI series, 2001Q1+, 96 quarters", "Best match CIS2020000000000I (private industry): growth correlation 0.9974, max gap 0.0007 log pts. Civilian wages CIS1020000000000I: 0.964. Pre-2001 splice not checked.", "https://data.bls.gov/timeseries/CIS2020000000000I"],
 ["vu", "JOLTS openings / unemployed; pre-2001 from Barnichon (2010)", "Pulled JTS000000000000000JOL and LNS13000000, quarterly mean of monthly ratio, 2001+", "98% of quarters within 0.02; max gap 0.044. Pre-2001 not checked.", "https://data.bls.gov/timeseries/JTS000000000000000JOL"],
 ["productivity", "Nonfarm business value added / hours (PDF p.15)", "Compared growth with BLS PRS85006093, 2001+", "Correlation 0.9962, max gap 0.004 log pts; not an exact match to the paper's exact series", "https://data.bls.gov/timeseries/PRS85006093"],
 ["exp1, exp10", "Cleveland Fed 1-yr and 10-yr expected inflation (paper Table A1, PDF p.42)", "Downloaded Cleveland Fed workbook; compared with quarter-end month", "95% of quarters within 0.02 pp (both series); max gap 0.86 (exp1)", "https://www.clevelandfed.org/indicators-and-data/inflation-expectations"],
 ["shortage", "Quarterly average of Google searches for 'shortage', US (PDF p.24)", "NOT checked - Google Trends not re-pulled; value taken as given from the replication data", "Unverified", "https://trends.google.com/trends/explore?geo=US&q=shortage"],
 ["post-2023Q1 rows", "Lorenzoni extended the series to 2025Q1; README gives no sources", "CPI, energy, food, ECI, v/u, productivity, expectations all checked against the same sources including 2023Q2-2025Q1", "see rows above (checks span the whole sample)", REPL]]
sheet(wb, "Data_verification", vr, [16, 50, 55, 70, 60])

# ---- Robustness
w1 = rob[rob.variant == "primary"].set_index("date")
rr = [["Variant", "Window", *[LAB[c] for c in ORDER]]]
for v in rob.variant.unique():
    d = rob[rob.variant == v].set_index("date")
    for lab_, end in [("2020Q1-2023Q1 (13 q, common window)", "2023-01-01"), ("2020Q1-2024Q4 (20 q)", "2024-10-01")]:
        dd = d.loc[:end]
        if lab_.startswith("2020Q1-2024") and dd.index.max() < pd.Timestamp("2024-10-01"): continue
        rr.append([v, lab_, *[round(dd[c].sum() / 4, 2) for c in ORDER]])
ws = sheet(wb, "Robustness", rr, [42, 36] + [14] * 7)
ws.cell(len(rr) + 2, 1, "Cumulative log points of the price level. Variants: primary = Lorenzoni data to 2025Q1; original dataset = data_us.csv (to 2023Q1, what the paper used); lagged productivity = authors' R script; current BLS = CPI/energy/food replaced with today's BLS seasonally adjusted values.")

# ---- Inputs
inp = x.loc["2019-01-01":, ["cpi", "lci", "exp1", "exp10", "energy_cpi", "food_cpi", "vu", "shortage", "productivity", "gp", "gw", "grpe", "grpf", "gpty"]].reset_index()
inp["date"] = inp.date.dt.strftime("%Y-%m-%d")
sheet(wb, "Inputs_2019on", [list(inp.columns)] + inp.round(4).values.tolist(), [12] + [11] * 14)
wb.save(O + "inflation_causes_2020-2024.xlsx"); print("saved")
