"""output/REPORT.md: the technical write-up. Every number is read from the model outputs, so the text can't drift
from the data. Run after run_report.sh's other steps (it is the last step there)."""
import re
import pandas as pd

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
o = pd.read_csv(ROOT + "output/unified_causes_quarterly.csv", index_col=0)
cu = pd.read_csv(ROOT + "output/unified_cumulative_2021_2024.csv", index_col=0)
rb = pd.read_csv(ROOT + "output/robustness_unified.csv", header=[0, 1], index_col=[0, 1])
fl = pd.read_csv(ROOT + "output/fed_late.csv").set_index(["scenario", "quarter"])
log = open(ROOT + "output/unified_model_run.log").read()
cmp_ = open(ROOT + "output/COMPARISON.md").read().split("\n", 2)[2]
gr = pd.read_csv(ROOT + "output/uncertainty_groups.csv", index_col=0)
pairs = pd.read_csv(ROOT + "output/uncertainty_pairs.csv")
srcw = pd.read_csv(ROOT + "output/uncertainty_sources.csv", index_col=0)
comb = pd.read_csv(ROOT + "output/combined_cumulative_2021_2024.csv", index_col=0)
cmeta = pd.read_csv(ROOT + "output/combined_meta.csv", index_col=0).value
ccr = pd.read_csv(ROOT + "output/cross_country_relief.csv", index_col=0)
lkd = pd.read_csv(ROOT + "output/shapiro_leakage.csv")
bal = pd.read_csv(ROOT + "output/shapiro_adjusted_balance.csv")
ulog = {k: open(ROOT + f"output/uncertainty_{k}.log").read() for k in ["coefs", "condition", "extend_sample", "relief_scale"]}

F = float(re.search(r"first-stage F ([\d.]+)", log).group(1))
okun = float(re.search(r"Okun: (-?[\d.]+)", log).group(1))
cv = re.search(r"g0 ([\d.]+) \(se ([\d.]+)\), g1 (-?[\d.]+) \(se ([\d.]+)\), R2 ([\d.]+) \(uncentered; centered ([\d.]+)\)", log).groups()
o["pre_existing"] = o.baseline + o.fed_pre2020
o["supply"] = o.shortage + o.energy_war + o.worker_shortage + o.memo_energy_covid
o["demand"] = o.trump + o.biden + o.fed_easing + o.fed_hikes + o.pentup
o["covid_jobs"] = o.covid_other - o.memo_energy_covid
P = "2022Q2"
c = lambda k: cu.loc[k, "total"]
cr = lambda k: f"{c(k):+.1f} [{cu.loc[k, 'lo']:+.1f} to {cu.loc[k, 'hi']:+.1f}]"
q = lambda k, t=P: o.loc[t, k]
qr = lambda k, t=P: f"{q(k, t):+.2f} [{o.loc[t, k + '_lo']:+.2f} to {o.loc[t, k + '_hi']:+.2f}]"
excess = c("actual") - c("baseline") - c("fed_pre2020")
b22, b24 = fl.loc[("barnichon", "2022Q2")], fl.loc[("barnichon", "2024Q4")]
y24 = fl.loc[("year_early", "2024Q4")]

YEARS = ["2021Q4", "2022Q4", "2023Q4", "2024Q4"]
ROWS = [("trump", "Relief paid under Trump"), ("biden", "Relief paid under Biden"), ("fed_easing", "Fed 2020-21 cuts + QE"),
        ("fed_hikes", "Fed 2022-23 hikes"), ("pentup", "Pent-up demand"), ("shortage", "COVID supply chains"),
        ("energy_war", "War in Ukraine (energy & food)"), ("worker_shortage", "Worker shortage"), ("greed", "Greedflation"),
        ("covid_other", "COVID shutdown drag (incl. 2020-21 oil & food)"), ("pre_existing", "Pre-existing (end-2019)"),
        ("other_unexplained", "Other & not explained")]
yt = ["| Cause | " + " | ".join(f"Year to {t}" for t in YEARS) + " | 2021-24 total [90% range] |", "|---|" + "---|" * (len(YEARS) + 1)]
for k, n in ROWS:
    tot = cr(k) if k != "pre_existing" else f"{c('baseline') + c('fed_pre2020'):+.1f}"
    yt.append(f"| {n} | " + " | ".join(f"{q(k, t):+.2f}" for t in YEARS) + f" | {tot} |")
yt.append("| **Model estimate (sum of causes)** | " + " | ".join(f"{q('model_total', t):.2f}" for t in YEARS) + f" | {cr('model_total')} |")
yt.append("| **Actual PCE inflation** | " + " | ".join(f"{q('actual_pce_yoy', t):.2f}" for t in YEARS) + f" | {c('actual'):.1f} |")
yt = "\n".join(yt)

KEYS = [("trump", "Trump relief"), ("biden", "Biden relief"), ("fed_easing", "Fed cuts+QE"), ("fed_hikes", "Fed hikes"),
        ("pentup", "Pent-up"), ("covid_other", "COVID drag"), ("unexplained", "Not explained"), ("model_total", "Model total")]
rt = ["| Variant | " + " | ".join(n for _, n in KEYS) + " |", "|---|" + "---|" * len(KEYS)]
for v, desc in rb.columns:
    rt.append(f"| {desc} | " + " | ".join(f"{rb.loc[(k, P), (v, desc)]:+.2f}" for k, _ in KEYS) + " |")
rt = "\n".join(rt)

LBL = {"bb_coefs": "Wage-price coefficients", "okun": "Okun", "beveridge": "V/U on u", "fiscal": "Relief timing & size",
       "svar": "Fed VAR", "pentup": "Pent-up variants", "covid_gamma": "COVID coefficients", "all": "All together"}
NM = {"shortage": "Supply chains", "covid_other": "COVID drag", "worker_shortage": "Worker shortage", "trump": "Trump relief",
      "biden": "Biden relief", "pentup": "Pent-up demand", "fed_easing": "Fed cuts+QE", "fed_hikes": "Fed hikes",
      "baseline": "Pre-existing", "energy_war": "War"}
srct = "\n".join(["| Cause | " + " | ".join(LBL[k] for k in srcw.columns if k != "point") + " |", "|---|" + "---|" * (len(srcw.columns) - 1)]
                 + [f"| {NM[i]} | " + " | ".join(f"{srcw.loc[i, k]:.1f}" for k in srcw.columns if k != "point") + " |" for i in srcw.index])
GL = [("grp_labor", "All labor-market causes (relief, pent-up, Fed, COVID drag, worker shortage)"),
      ("grp_pandemic", "The pandemic and the response (relief + pent-up + COVID drag)"),
      ("grp_supply", "Supply shocks (supply chains + war)"),
      ("shortage", "for comparison: supply chains alone"), ("covid_other", "for comparison: COVID drag alone"),
      ("model_total", "Model estimate")]
grt = "\n".join(f"| {n} | {gr.loc[k, 'total_2021_24']:+.1f} | {gr.loc[k, 'p16']:+.1f} to {gr.loc[k, 'p84']:+.1f} | "
                f"{gr.loc[k, 'p5']:+.1f} to {gr.loc[k, 'p95']:+.1f} |" for k, n in GL)
sd = float(pairs[pairs.A.str.startswith("Supply shocks")]["P(A > B)"].iloc[0])
pp = lambda a, b="Relief + pent-up + Fed": float(pairs[(pairs.A == a) & (pairs.B == b)]["P(A > B)"].iloc[0])
prt = "\n".join(f"| {r.A} | {r.B} | {r['P(A > B)']:.0%} |" for _, r in pairs.iterrows())
import numpy as _np
_CM = {"cc_us": f"{ccr.us_fiscal.iloc[0]:.1f}%", "m_cpi": float(cmeta.cc_us_effect_cpi), "s_cpi": float(cmeta.cc_se_cpi),
       "m_pce": float(cmeta.m_pce), "s_pce": float(cmeta.s_pce), "model_point": float(cmeta.model_relief_point_same_metric),
       "model_p5": float(cmeta.model_relief_p5), "model_p95": float(cmeta.model_relief_p95), "ess": float(cmeta.ess),
       "cc_r2": float(ccr.loc[cmeta.cc_spec, "r2"])}
cm = lambda k: _CM[k]
CCN = {"core_advanced": "Core CPI, 2021-24, advanced economies", "core_advanced_euro_dummy": "same + euro-area dummy",
       "core_advanced_2021_22": "**Core CPI, 2021-22, advanced economies (used below)**",
       "core_advanced_2021_22_euro_dummy": "Core, 2021-22 + euro-area dummy", "core_advanced_2021_22_energy_control": "Core, 2021-22 + energy exposure (headline minus core, 2022)",
       "core_plus_oecd_emerging_2021_22": "Core, 2021-22, + Poland, Chile, Colombia, Mexico",
       "headline_advanced_incl_japan_2021_22": "Headline (IMF), 2021-22, incl. Japan & Singapore",
       "core_plus_oecd_emerging": "Core, 2021-24, + 4 emerging", "headline_advanced_incl_japan": "Headline (IMF), 2021-24, incl. Japan & Singapore",
       "headline_advanced_euro_dummy": "Headline, 2021-24 + euro-area dummy"}
cct = "\n".join(["| Specification | Countries | Slope per % of GDP (s.e.) | US relief effect, points (s.e.) |", "|---|---|---|---|"]
                 + [f"| {CCN[i]} | {r.n} | {r.b:.3f} ({r.se:.3f}) | {r.us_effect:+.1f} ({r.us_effect_se:.1f}) |" for i, r in ccr.iterrows()])
CBN = {"biden": "Relief paid under Biden", "trump": "Relief paid under Trump", "covid_other": "COVID drag",
       "shortage": "Supply chains", "worker_shortage": "Worker shortage",
       "relief_all": "*Total:* Biden + Trump relief (what the cross-country comparison measures)",
       "grp_pandemic": "*Total:* Biden + Trump relief + pent-up demand + COVID drag"}
cbt = "\n".join(["| 2021-24 total | Model alone, 90% range | With cross-country evidence, 90% range |", "|---|---|---|"]
                 + [f"| {n} | {comb.loc[k, 'before_p5']:+.1f} to {comb.loc[k, 'before_p95']:+.1f} | {comb.loc[k, 'after_p5']:+.1f} to {comb.loc[k, 'after_p95']:+.1f} |" for k, n in CBN.items()])
_lc = lkd[lkd.case == "central"]
lkt = "\n".join(["| Shapiro series | Supply | Demand | Ambiguous | Leakage L, median [90% over redraws] |", "|---|---|---|---|---|"]
                 + [f"| {r.shapiro} | {r.S:.1f} | {r.D:.1f} | {r.A:.1f} | {r.L_p50:+.1f} [{r.L_p5:+.1f} to {r.L_p95:+.1f}] |" for _, r in _lc.iterrows()])
lk_c = float(_lc[_lc.shapiro == "SF Fed published"].L_p50.iloc[0])
lk_lo, lk_hi = float(lkd[lkd.case.isin(["a=0,c=0", "a=1,c=1"])].L_p50.min()), float(lkd[lkd.case.isin(["a=0,c=0", "a=1,c=1"])].L_p50.max())
_b = bal[(bal.shapiro == "SF Fed published") & (bal.case == "central")].iloc[0]
bal_s, bal_d = float(_b.supply_after), float(_b.demand_after)
_yd = _np.load(ROOT + "output/unified_draws.npy"); _cols = list(pd.read_csv(ROOT + "output/unified_draws_columns.csv").line)
_q4 = [i for i, t in enumerate(o.index) if t.endswith("Q4") and int(t[:4]) >= 2021]
_t = lambda ks: _yd[:, _q4][:, :, [_cols.index(k) for k in ks]].sum(axis=(1, 2))
corr = _np.corrcoef(_t(["covid_other"]), _t(["trump", "biden"]))[0, 1]
ess = re.search(r"wages only: (ESS \d+ of \d+)", ulog["condition"]).group(1)
_r2 = [float(v) for v in re.findall(r"centered R2 ([\d.]+)", ulog["relief_scale"])]
r2lo, r2hi = f"{min(_r2):.2f}", f"{max(_r2):.2f}"

_E = ROOT + "output/ext/"
e02 = pd.read_csv(_E + "e02_category_panel.csv").set_index("variant")
e02m = pd.read_csv(_E + "e02_model_direct.csv", index_col=0).iloc[:, 0]
e03 = pd.read_csv(_E + "e03_autos.csv", index_col=0)
e04 = pd.read_csv(_E + "e04_supply_measures.csv", index_col=0)
e05 = pd.read_csv(_E + "e05_states.csv", index_col=0)
e06 = pd.read_csv(_E + "e06_relief_spending.csv")
e07 = pd.read_csv(_E + "e07_cross_country_quarterly.csv", index_col=0)
e08 = pd.read_csv(_E + "e08_fed_alternatives.csv", index_col=0)
e09 = pd.read_csv(_E + "e09_fed_credibility.csv"); e09l = pd.read_csv(_E + "e09_fed_credibility_levels.csv").iloc[0]
e10 = pd.read_csv(_E + "e10_economy_margins.csv", index_col=0)
e11 = pd.read_csv(_E + "e11_out_of_sample.csv", index_col=0)
e12 = pd.read_csv(_E + "e12_all_evidence.csv", index_col=[0, 1])
e13 = pd.read_csv(_E + "e13_wage_tracker.csv", index_col=0)
e14 = pd.read_csv(_E + "e14_laws.csv", index_col=0)
e14ev = pd.read_csv(_E + "e14_events.csv")
e14w = pd.read_csv(_E + "e14_deal_week.csv")
_14 = lambda k: f"{e14.loc[k, 'total_2021_24']:+.2f} [{e14.loc[k, 'p5']:+.2f} to {e14.loc[k, 'p95']:+.2f}]"
E14ROWS = [("scored", "As CBO scored it (net of offsets, CBO multipliers)"),
           ("spending side", "Spending side only (offsets removed, $1 of GDP per $1)"),
           ("promise = payment", "All ten years of spending paid the quarter it was signed")]
e14t = "\n".join(["| 2021-24 total, model point [90% range] | Infrastructure law | Inflation Reduction Act | Both |", "|---|---|---|---|"]
                  + [f"| {n} | {_14('iija ' + k)} | {_14('ira ' + k)} | {_14('both ' + k)} |" for k, n in E14ROWS])
_ev = e14ev[e14ev.series == "T5YIFR"]
e14evt = "\n".join(["| News | Window | 5y5y change | 5y | 10y | Ordinary range (5y5y) |", "|---|---|---|---|---|---|"]
    + [f"| {r.event} | {r.window} | {r.change:+.2f} | {e14ev[(e14ev.series == 'T5YIE') & (e14ev.date == r.date)].change.iloc[0]:+.2f} | "
       f"{e14ev[(e14ev.series == 'T10YIE') & (e14ev.date == r.date)].change.iloc[0]:+.2f} | {r.ordinary_p5:+.2f} to {r.ordinary_p95:+.2f} |"
       for r in _ev.itertuples()])
_dw = e14w[e14w.series == "T5YIE"].set_index("day").change_1day
e15f = pd.read_csv(_E + "e15_wages_productivity.csv", index_col=0)
_ls = pd.read_csv(ROOT + "data/raw/ext/fred2b/PRS85006173.csv", index_col=0, parse_dates=True).iloc[:, 0]
e15q = pd.read_csv(_E + "e15_wage_quartiles.csv", index_col=0)
e15c = pd.read_csv(_E + "e15_catchup_term.csv", index_col=0)
e15u = pd.read_csv(_E + "e15_ui_early_end.csv")
e15s = pd.read_csv(_E + "e15_state_vu_wage_curve.csv", index_col=0)
e15w = pd.read_csv(_E + "e15_width_by_equation.csv", index_col=0)
e16 = pd.read_csv(_E + "e16_narrower.csv", index_col=[0, 1])
e17 = pd.read_csv(_E + "e17_europe_panel.csv", index_col=0)
e17v = pd.read_csv(_E + "e17_value_of_direct.csv", index_col=0)
_w17 = e17[e17.vu_sum.notna()]; _p17 = e17[e17.shortage_sum.notna()]
e17wt = "\n".join(["| Wage equation | Countries | Long-run slope (s.e.) |", "|---|---|---|"]
                   + [f"| {i} | {r.countries:.0f} | {r.long_run_slope:.2f} ({r.se_long_run_slope:.2f}) |" for i, r in _w17.iterrows()])
e17pt = "\n".join(["| Price equation | Countries | Supply-chain terms | Inflation persistence | Long-run supply-chain effect (s.e.) |", "|---|---|---|---|---|"]
                   + [f"| {i} | {r.countries:.0f} | {r.shortage_sum:.3f} | {r.gp_lag_sum:.2f} | {r.long_run_supply:.2f} ({r.se_long_run_supply:.2f}) |" for i, r in _p17.iterrows()])
e17vt = "\n".join(["| How well the direct effect is known | Supply-chain total 2021-24, median [90% range] |", "|---|---|"]
                   + [f"| {i} | {r.p50:+.1f} [{r.p5:+.1f} to {r.p95:+.1f}] |" for i, r in e17v.iterrows()])
_f = lambda r, c: e15f.iloc[r][c]
e15ft = "\n".join(["| 2019Q4 to | Real pay per hour | Productivity | Labor share |", "|---|---|---|---|"]
                   + [f"| {i[10:16]} | {r.real_comp_per_hour:+.1f}% | {r.productivity:+.1f}% | {r.labor_share:+.1f}% |" for i, r in e15f.iterrows()])
e15qt = "\n".join(["| Wage level, Atlanta Fed tracker | Nominal | After PCE inflation |", "|---|---|---|"]
                   + [f"| {i} | {r.nominal:+.1f}% | {r.real:+.1f}% |" for i, r in e15q.iterrows()])
e15ut = "\n".join(["| Outcome, early-ending states vs others | Estimate | s.e. |", "|---|---|---|"]
                   + [f"| {r.outcome} | {r.estimate:+.3f} | {r.se:.3f} |" for _, r in e15u.iterrows()])
_wn = {"shortage": "Supply chains", "energy_war": "War in Ukraine", "worker_shortage": "Worker shortage", "biden": "Biden relief",
       "trump": "Trump relief", "pentup": "Pent-up demand", "covid_other": "COVID drag"}
e15wt = "\n".join(["| 90% width, 2021-24 total | Wage equation | Price equation | Expectations | All four |", "|---|---|---|---|---|"]
                   + [f"| {_wn[i]} | {r['wage equation']:.1f} | {r['price equation']:.1f} | {r['expectations equations']:.1f} | {r['all four']:.1f} |" for i, r in e15w.iterrows()])
_r16 = lambda c, k: f"{e16.loc[(c, 'p50'), k]:+.1f} [{e16.loc[(c, 'p5'), k]:+.1f} to {e16.loc[(c, 'p95'), k]:+.1f}]"
e01 = open(_E + "e01_kinked_phillips.log").read()
_k = re.search(r"tau 1.0: WAGE eq: V/U ([^,]+), above-threshold ([^,]+), .*PRICE eq: V/U ([^,]+), above-threshold ([^,]+),", e01).groups()
f2 = lambda v: f"{v:+.1f}"
r_ = lambda c, s=None: f"{e12.loc[(c, 'p50'), s or BEST]:+.1f} [{e12.loc[(c, 'p5'), s or BEST]:+.1f} to {e12.loc[(c, 'p95'), s or BEST]:+.1f}]"
BEST = "+ wages + panel + cross-country"
BASE = "model alone"
E12ROWS = [("shortage", "Supply chains"), ("energy_war", "War in Ukraine"), ("worker_shortage", "Worker shortage"),
           ("biden", "Relief paid under Biden"), ("trump", "Relief paid under Trump"), ("pentup", "Pent-up demand"),
           ("fed_net", "The Fed (net)"), ("covid_other", "COVID drag")]
E12TOT = [("grp_supply", "Supply total = supply chains + war"),
          ("grp_demand", "Demand total = Biden relief + Trump relief + pent-up demand + the Fed")]
_e12r = lambda c, n: f"| {n} | {r_(c, BASE)} | {r_(c, '+ wages')} | {r_(c, '+ category panel')} | {r_(c)} |"
e12t = "\n".join(["| 2021-24 total, median [90% range] | Model alone | + wage data | + category panel | + wages + panel + cross-country |",
                  "|---|---|---|---|---|"] + [_e12r(c, n) for c, n in E12ROWS]
                 + ["| *Totals: sums of rows above, not extra causes* | | | | |"] + [_e12r(c, n) for c, n in E12TOT]
                 + [f"| Supply chains + war + worker shortage beat the demand total, share of redraws | "
                    + " | ".join(f"{e12.loc[('P(supply chains+war+worker > demand)', 'share'), k]:.0%}" for k in [BASE, '+ wages', '+ category panel', BEST]) + " |",
                    f"| Effective redraws (of 1,000) | " + " | ".join(f"{e12.xs('ESS', level=0).iloc[0][k]:.0f}" for k in [BASE, '+ wages', '+ category panel', BEST]) + " |"])
e16t = "\n".join(["| 2021-24 total, median [90% range] | Best estimate (E12's evidence, rerun) | + 2020-24 inflation (I) | + I + state wage curve (S) |", "|---|---|---|---|"]
                  + [f"| {n} | {_r16(c, 'W+P + X')} | {_r16(c, 'W+I+P + X')} | {_r16(c, 'W+I+P+S + X')} |" for c, n in E12ROWS])
e11t = "\n".join(["| Version | Error, quarterly | Error, 4-quarter | Average error |", "|---|---|---|---|"]
                 + [f"| {i} | {r.rmse_quarterly:.2f} | {r.rmse_4q:.2f} | {r.mean_error:+.2f} |" for i, r in e11.iterrows()])
e04t = "\n".join(["| Supply-chain measure | Coefficient sum (s.e.) | Supply-chain line, 2021-24 [90%] | 2022-24 forecast error (4-quarter) |", "|---|---|---|---|"]
                 + [f"| {i} | {r.coef_sum:.3f} ({r.coef_se:.3f}) | {r.line_2021_24:+.1f} [{r.p5:+.1f} to {r.p95:+.1f}] | "
                    f"{e11.loc[{'GSCPI (model)': 'model (GSCPI)', 'delivery times': 'supply = delivery times', 'unfilled orders': 'supply = unfilled orders', 'composite': 'supply = composite'}[i], 'rmse_4q']:.2f} |"
                    for i, r in e04.iterrows()])
e02t = "\n".join(["| Variant | Direct effect, 2021-24 (s.e.) | Peak, year-over-year |", "|---|---|---|"]
                 + [f"| {i} | {r.effect_2021_24:+.1f} ({r.effect_se:.1f}) | {r.peak_yoy:+.1f} ({r.peak_month}) |" for i, r in e02.iterrows()]
                 + [f"| *The model's own direct term* | {e02m.point:+.2f} (90%: {e02m.p5:+.2f} to {e02m.p95:+.2f}) | |"])
_FN = dict(svar_mps="VAR, Bauer-Swanson surprise (model)", svar_jk="VAR, Jarocinski-Karadi shock",
           lp_mps="Local projections, Bauer-Swanson", lp_jk="Local projections, Jarocinski-Karadi")
e08t = "\n".join(["| Fed identification | First-stage F | Cuts + QE, 2021-24 | Hikes, 2021-24 | Net |", "|---|---|---|---|---|"]
                 + [f"| {_FN[i]} | {r.first_stage_F:.1f} | {r.fed_easing_2021_24:+.1f} | {r.fed_hikes_2021_24:+.1f} | {r.fed_net_2021_24:+.1f} |" for i, r in e08.iterrows()])

doc = f"""# What caused US inflation, 2020-2024: a cause-by-cause decomposition with an explicit error term

Technical report. Plain-language version: the web page. Code and data: this folder (`run_report.sh` rebuilds every number
and figure from `data/raw/`; Python and package versions in `requirements.txt`).

## 1. What this can't show (read first)

- **The split between demand and supply is the least settled part.** In this model, demand (relief, the Fed, pent-up
  spending) raises inflation only through the labor market: more demand, fewer unemployed, more job openings per
  unemployed person, faster wage growth, higher prices. Bernanke and Blanchard, whose wage-price model this is, write
  that the price shocks of 2021-22 included "sharp increases in commodity prices, reflecting strong aggregate demand,
  and sectoral price spikes, resulting from changes in the level and sectoral composition of demand together with
  constraints on sectoral supply" (NBER w31417, abstract). That part of demand is counted here under supply chains and
  energy. **So the demand lines are lower bounds and the supply lines upper bounds.** The SF Fed's category-level
  labels put the size of this at about {lk_c:.1f} points of the 2021-24 total (range {lk_lo:+.1f} to {lk_hi:+.1f} depending on
  how labels are shared out; Section 6), which would make supply and demand about equal.
- **Single lines are imprecise; groups of lines are not.** The 90% range for supply chains is
  {gr.loc['shortage', 'p5']:+.1f} to {gr.loc['shortage', 'p95']:+.1f} points and for the COVID drag
  {gr.loc['covid_other', 'p5']:+.1f} to {gr.loc['covid_other', 'p95']:+.1f}. That width is real: it comes from the
  wage-price model's own coefficients, and three attempts to narrow it with more data failed (Section 5). Sums of lines
  are much tighter, because their errors offset: all labor-market causes together,
  {gr.loc['grp_labor', 'p5']:+.1f} to {gr.loc['grp_labor', 'p95']:+.1f}. Read single lines as orders of magnitude and
  the group totals and the comparisons in Section 5 as the findings.
- **The relief lines depend most on one assumption:** how much GDP each relief dollar produced. Scaling the relief
  effects up to CBO's 2020 total (x2.04) roughly doubles both relief lines; the COVID drag deepens by about the same
  amount (Section 9). The 90% ranges include this.
- **The COVID drag is estimated on the same 2020-22 data** as everything else (no outside estimate exists). It is fitted
  to the unemployment that relief, the Fed and pent-up demand leave unexplained, so it partly mirrors their size.
- **The Fed is identified with a borderline instrument** (first-stage F = {F:.1f}; robust 8.2; the usual threshold is 10).
  The cleaner version (MPS_ORTH, which the SF Fed calls a better measure of new policy information because it removes
  predictable variation) is a weak instrument (F = 3.6) and gives Fed effects several times larger.
- **Energy & food are assigned to causes by date,** not estimated: 2020Q1-2021Q4 to COVID, 2022Q1-2023Q1 to the war in
  Ukraine (which therefore also contains the October 2022 OPEC+ cut and the late-2022 bird-flu egg spike), after 2023Q1
  to "other & not explained".
- **One model family.** A model with a steeper Phillips curve, or one where Fed credibility or the dollar matter
  directly, would give demand and the Fed larger roles.

## 2. Main results

*These are the model's own estimates. Section 8 updates them with independent evidence the model doesn't use
(wage data, differences across spending categories, other countries); that is the best estimate.*

PCE inflation added up to {c('actual'):.1f} points over 2021-2024 (the four Q4-over-Q4 rates). The model explains
{c('model_total'):.1f} of them. The economy's pre-2020 momentum accounts for {c('baseline') + c('fed_pre2020'):.1f}
(about 2% a year); the other **{excess:.1f} points** are what needs explaining.

| Cause | 2021-24 total [90% range] | At the 2022Q2 peak [90% range] |
|---|---|---|
| COVID supply chains | {cr('shortage')} | {qr('shortage')} |
| Worker shortage | {cr('worker_shortage')} | {qr('worker_shortage')} |
| Relief paid under Biden | {cr('biden')} | {qr('biden')} |
| Relief paid under Trump | {cr('trump')} | {qr('trump')} |
| War in Ukraine (energy & food) | {cr('energy_war')} | {qr('energy_war')} |
| Pent-up demand | {cr('pentup')} | {qr('pentup')} |
| Fed 2020-21 cuts + QE | {cr('fed_easing')} | {qr('fed_easing')} |
| Fed 2022-23 hikes | {cr('fed_hikes')} | {qr('fed_hikes')} |
| Greedflation | {cr('greed')} | {qr('greed')} |
| COVID shutdown drag (incl. 2020-21 oil & food crash and rebound) | {cr('covid_other')} | {qr('covid_other')} |
| Other & not explained | {cr('other_unexplained')} | {qr('other_unexplained')} |
| *Model estimate (sum of causes)* | {cr('model_total')} | {qr('model_total')} |
| *Actual* | {c('actual'):.1f} | {q('actual_pce_yoy'):.2f} |

Ranges are 5th-95th percentiles of 1,000 redraws (Section 5). Figures: `fig14_cumulative.png` (totals),
`fig13_stacked_causes.png` (every quarter, stacked), `fig12_unified_causes.png` (every cause as a line).

**Findings the ranges support:**
1. **Supply shocks were probably the largest new force, but the model doesn't settle it.** Supply chains, the war, the
   worker shortage and the 2021 energy rebound add up to {q('supply'):.1f} of the {q('actual_pce_yoy'):.1f} points in 2022Q2 (an
   upper bound; see Section 1). Over 2021-24, supply chains + war + worker shortage exceed relief + pent-up + Fed in
   {pp('Supply shocks + worker shortage'):.0%} of redraws; without the worker shortage, in {pp('Supply shocks (group)'):.0%} (Section 5).
2. **Relief laws mattered, under both presidents, and probably neither was the largest single cause** (supply chains
   exceed Biden-signed relief in {pp('Supply chains', 'Relief paid under Biden'):.0%} of redraws, but all relief together in only
   {pp('Supply chains', 'All relief (Trump + Biden)'):.0%}). Biden-signed relief:
   {cr('biden')} points over 2021-24; Trump-signed: {cr('trump')}. Together {cr('relief_all')}, against
   {excess:.1f} points of inflation beyond the pre-2020 pace. Much of relief's effect offset the COVID drag ({c('covid_other'):+.1f}):
   the shutdown pushed unemployment up and inflation down, and relief pushed the other way.
3. **The Fed's net effect over 2021-24 was small:** {cr('fed_all')} points. Its 2022-23 hikes were still working
   their way through at the end of 2024.
4. **Greedflation is about zero in the model** ({cr('greed')}), although profit margins did rise in 2021 by
   accounting (Table 3 of `TABLE_UNIFIED.md`). Margin moves beyond what costs, shortages and demand explain don't
   predict PCE inflation in 1990-2024.
5. **Pent-up demand added {c('pentup'):.1f} points** [{cu.loc['pentup', 'lo']:.1f} to {cu.loc['pentup', 'hi']:.1f}].

Each year (points of year-over-year PCE inflation, official percent change):

{yt}

## 3. Did the Fed act too late?

Tested directly: the model is re-run with earlier hikes and compared with actual policy (`src/fed_late_report.py`,
`fig15_fed_late.png`).

| Counterfactual | Inflation, 2022Q2 | Inflation, 2024Q4 | Unemployment, 2022Q2 | Unemployment, 2024Q4 |
|---|---|---|---|---|
| Hikes from March 2021, to ~2% by early 2022 (the path in Barnichon, FRBSF EL 2022-28) | {b22.infl_yoy:+.2f} [{b22.infl_lo:+.2f}, {b22.infl_hi:+.2f}] | {b24.infl_yoy:+.2f} [{b24.infl_lo:+.2f}, {b24.infl_hi:+.2f}] | {b22.unemp:+.2f} [{b22.unemp_lo:+.2f}, {b22.unemp_hi:+.2f}] | {b24.unemp:+.2f} [{b24.unemp_lo:+.2f}, {b24.unemp_hi:+.2f}] |
| The actual 2022-23 hikes, a year earlier | {fl.loc[('year_early', '2022Q2')].infl_yoy:+.2f} | {y24.infl_yoy:+.2f} [{y24.infl_lo:+.2f}, {y24.infl_hi:+.2f}] | {fl.loc[('year_early', '2022Q2')].unemp:+.2f} | {y24.unemp:+.2f} [{y24.unemp_lo:+.2f}, {y24.unemp_hi:+.2f}] |

The published estimate for the first path (Barnichon, FRBSF Economic Letter 2022-28, Oct 11 2022): "inflation would have
been about 1 percentage point lower as of June 2022, while unemployment would be about 2 percentage points higher"
(95%: 0.2-2 lower; 1-3 higher). Its measure is core inflation; it uses rate effects estimated on 1990-2007.

**What this supports:** starting a year earlier would have lowered inflation, by 0.2 to 1 point depending on the
model, and every estimate puts the price at roughly 2 to 3.5 points of extra unemployment for each point of inflation removed. Starting earlier would not have prevented most of the surge. **What it can't settle:**
whether the Fed's framework at the time (flexible average inflation targeting) and its forward guidance raised inflation
expectations in ways a model like this one, where expectations follow past inflation, doesn't capture.

## 4. Method

One chain, every link estimated on public data or taken from a cited official source. Equations line by line, every
quarter, and every data source with links: `TABLE_UNIFIED.md`. Long-form notes: `METHOD_UNIFIED.md`.

1. **Relief laws → GDP.** BEA payments by program (23 programs) x CBO's GDP-per-dollar multipliers (CBO 56537, Table 3),
   spread over time with geometric weights fitted to CBO's timing (lambda = 0.74). Payments before March 2021 are
   Trump's; from March 2021, Biden's (the rule least favourable to "Trump's relief mattered too").
2. **Pent-up demand → GDP.** Real PCE (BEA DPCERX) below its 2015-2019 log-linear trend in 2020-21, summed: forced
   saving of $786 billion (2017 dollars). Spent evenly from 2021Q2 through 2023Q3 (the SF Fed's date for excess
   savings running out), x 0.78 GDP per dollar (CBO "other spending"). Relief money is excluded, since the relief lines
   already count its spending. The method follows Aladangady, Cho, Feiveson & Pinto (FEDS Notes, Oct 21 2022), whose
   Table 1 shows transfers, not reduced spending, were the main source of excess savings.
3. **GDP → unemployment:** Okun's law, beta = {okun:.3f}, estimated 1990-2019.
4. **Fed → unemployment.** Monthly proxy SVAR (Bauer-Swanson data, 1977-2019), instrument = monetary-policy surprise
   MPS, F = {F:.1f}. Counterfactual rate paths via Sims-Zha policy shocks inside each episode window.
5. **COVID shutdown → unemployment, estimated:** u-change not explained above = g0 s_t + g1 s_t-1 + e_t, OLS
   2020Q1-2022Q4, no constant; s = Oxford stringency index / 100. g0 = {cv[0]} (s.e. {cv[1]}), g1 = {cv[2]} (s.e. {cv[3]}),
   R^2 = {cv[5]} (uncentered, since there is no constant: {cv[4]}). After the tracker ends (2022) the index fades to 0 by 2023Q2, when the federal Public Health Emergency
   ended (HHS). The residual e_t is not assigned to any cause; it is part of "other & not explained".
6. **Unemployment → V/U:** log(V/U) on u, 1990-2019. V/U beyond what unemployment implies = worker shortage.
7. **V/U, energy, food, supply chains (NY Fed GSCPI), margins → PCE inflation:** Bernanke-Blanchard wage-price model,
   re-estimated on PCE.
8. **Attribution:** each cause = model inflation with every cause minus model inflation without that cause. The model
   is linear, so the causes add up to the model's estimate; the gap to actual inflation is reported, not assigned.

**What changed from the previous version, and why.** (a) The COVID line was a leftover forced to match unemployment;
it is now estimated, and what it misses is shown as error. (b) The Fed instrument was MPS_ORTH (F = 3.6, weak), which
implied the 2022-23 hikes raised 2024 unemployment by about 4 points; it is now MPS (F = {F:.1f}). (c) Pent-up demand is
estimated instead of sitting inside the leftover. (d) The "did the Fed act too late?" test is new.

## 5. Uncertainty: why some ranges are wide, and what the data do pin down

Each of 1,000 redraws varies: the wage-price coefficients; Okun beta; the V/U coefficients; one wild-bootstrap
replication of the Fed VAR and instrument; relief timing (CBO-fitted or Hutchins) x coverage (1 or 2.04); the
Sims-Zha ridge; the COVID coefficients; pent-up demand's multiplier (0.78 or 1.0) and spending period (to 2023Q3 or
2024Q4). Half the redraws use relief coverage 2.04, so the relief and COVID ranges are not centred on the point
estimate (Biden and Trump relief combined: median {gr.loc['grp_relief', 'p50']:+.1f} against point {gr.loc['grp_relief', 'total_2021_24']:+.1f}).
Ranges are reported at 68% (16th-84th percentile) and 90% (5th-95th); every cause, every quarter:
`output/reproduce_long.csv`.

**Where the width comes from** (width of the 2021-24 90% range when only that source varies, 150 redraws each,
`src/uncertainty/sources.py`):

{srct}

- **Supply chains:** almost all from the price equation's GSCPI coefficients. Their sum is
  {ulog['coefs'].split('shortage coefficient sum ')[1].split(',')[0]}: the effect is identified by one episode
  (2021-23), because the index barely moved before.
- **COVID drag:** mostly the wage equation, whose V/U coefficients (sum
  {ulog['coefs'].split('vu coefficient sum ')[1].split(',')[0]}) are estimated on 1990-2019 and applied to the 2020 collapse in V/U (not outside that range: V/U was 0.16 in
  2009 and 0.27 in 2020Q2, but never before did it fall so far in one quarter), and wages did not slow as the
  equation predicts (Section 7, extension 13);
  next, relief coverage, because the COVID line is fitted to the unemployment that relief leaves unexplained (a
  bigger relief effect means a deeper COVID drag; correlation across redraws {corr:.2f}).

**What the data pin down: sums whose errors offset** (2021-24 totals, `output/uncertainty_groups.csv`). Each group is a
sum of causes listed in Section 2, not an extra cause, and the groups overlap, so they don't add up to anything:

| Group | Point | 68% range | 90% range |
|---|---|---|---|
{grt}

**Which comparisons the data settle** (share of redraws in which A added more than B over 2021-24,
`output/uncertainty_pairs.csv`):

| A | B | Share |
|---|---|---|
{prt}

So the model says with confidence that supply chains, the war, relief, pent-up demand and the worker shortage each
raised inflation, and that the COVID shutdown lowered it. It does not settle whether supply shocks or demand were the
bigger force overall ({sd:.0%} of redraws put supply first), and because the demand lines are lower bounds
(Section 1), the true balance leans further toward demand than that share suggests.

**Three attempts to narrow the single lines, none adopted** (code in `src/uncertainty/`, logs in `output/`):
1. *Weight the coefficient redraws by how well they reproduce observed 2020-24 wage growth* (data the wage equation
   never saw). The COVID range narrows only modestly, the supply-chain range not at all, and too few redraws carry the
   weight ({ess}) for the result to be stable. Log: `uncertainty_condition.log`.
2. *Re-estimate the wage and expectations equations through 2024 instead of 2019.* The ranges barely change. Log:
   `uncertainty_extend_sample.log`.
3. *Let the unemployment data choose the relief multiplier.* An earlier version of this report said the lockdown fit
   was equally good at every relief size (centred R^2 {r2lo} to {r2hi}). That comparison was wrong: each relief size
   leaves a different series for the lockdown term to explain, so their R^2 values can't be ranked. Compared properly,
   on unemployment the model misses (E15 D), the fit gets steadily better as relief gets smaller, all the way down to a
   quarter of the CBO-based effect. That happens because 12 quarters can't separate relief from the lockdown term:
   the lockdown term absorbs whatever relief doesn't explain. It also conflicts with the cross-country evidence
   (Section 6), which puts relief near the model's own size. Not adopted. Logs: `uncertainty_relief_scale.log`,
   `ext/e15_wages_ui_ranges.log`.

Narrowing these lines needs information this model doesn't use: category-level price and quantity data (the
Shapiro method), or cross-country variation in relief size (the Jorda et al. method). Both are tried in Section 6.

## 6. Two outside checks: other countries' relief, and the SF Fed's supply/demand labels

**Cross-country relief** (`src/cross_country_relief.py`, `output/cross_country_relief.csv`). Data the model never uses:
how much each country spent on pandemic relief (IMF Fiscal Monitor database, October 2021: above-the-line spending and
forgone revenue, % of GDP; US {cm('cc_us')}) and how much its inflation rose (OECD core CPI; IMF WEO headline). Regression
across countries of excess inflation (sum of annual rates minus the 2015-19 pace) on relief size; the US effect is the
slope times US relief, which asks the same question as the relief lines (relief against none).

{cct}

- Over 2021-24 the cross-country slope is close to zero and very imprecise: Europe's 2022-23 energy shock dominates the
  differences between countries in those years. Over 2021-22, when relief's effect peaked,
  the estimate is {cm('m_cpi'):.1f} points (s.e. {cm('s_cpi'):.1f}) of core CPI, {cm('m_pce'):.1f} ({cm('s_pce'):.1f}) in PCE terms. Published
  cross-country estimates are close, though their measures and periods differ: de Soyres, Santacreu & Young (FEDS Note,
  July 2022) roughly 2.6 points; Jorda et al. (FRBSF EL 2022-07) about 3 by 2021Q4 (core CPI).
- The model's relief, measured the same way (2021-22 annual averages): {cm('model_point'):.1f} (90% range {cm('model_p5'):.1f} to
  {cm('model_p95'):.1f}). **The two agree.**
- Combining them (each redraw weighted by its fit to the cross-country estimate, `src/combine_outside_evidence.py`)
  trims the high-relief redraws, the ones that use CBO's larger multiplier scale. The effective number of redraws stays
  {cm('ess'):.0f} of 1,000: the cross-country evidence is weak (18 countries, R^2 {cm('cc_r2'):.2f}), so the narrowing is modest:

{cbt}

**SF Fed supply/demand labels** (Shapiro; `output/shapiro_leakage.csv`). Shapiro labels each spending category's price
change as supply-driven (price and quantity move opposite ways), demand-driven (same way) or ambiguous. That is a
different question from "which cause", so the two can't be weighted against each other directly. Three of the model's
lines have no counterpart in his labels: the lingering COVID drag on jobs, the pre-existing momentum above its 2019
level, and "not explained"; his method spreads them over all labels. With c = the share of those lines his method labels
supply, and a = the share of "ambiguous" that is really supply:

    leakage L = model supply lines + c x (no-counterpart lines) - (Shapiro supply + a x ambiguous)

L is the part of the model's supply lines that Shapiro's data label as demand: the "demand meeting limited supply" of
Section 1. Setting a and c to his supply share of labelled inflation:

{lkt}

So Shapiro's data say roughly {lk_c:.1f} points of what the model calls supply (supply chains, war, worker shortage) was
demand, but the range runs from about {lk_lo:+.1f} to {lk_hi:+.1f} depending on the label shares, which no data pin down. Moving the
central amount gives supply (supply chains + war + worker shortage) {bal_s:.1f} and demand (relief + pent-up + Fed)
{bal_d:.1f}: **about equal.** This doesn't narrow the supply-chain line; it sizes the lower-bound problem.

## 7. Better data and models: seventeen extensions (`src/extensions/`, `output/ext/`)

Each extension adds data or a method the model above doesn't use, and keeps its log. Two could not be done and are
listed at the end.

**Supply chains**
- *E2. Differences across spending categories.* Category PCE prices, monthly 1999-2024, with a separate effect for
  every month (which absorbs relief, the Fed, pent-up demand, wages and expectations), so only how much MORE
  supply-chain-exposed categories moved identifies the effect:

{e02t}

  The direct effect is 1 to 2.5 points, larger than the model's own direct term ({e02m.point:+.2f}). Estimated on
  1999-2019 alone, without the pandemic, it is {e02.loc['goods, estimated 1999-2019 only', 'effect_2021_24']:+.1f}
  ({e02.loc['goods, estimated 1999-2019 only', 'effect_se']:.1f}): the effect does not rest on one episode. The model's
  supply-chain line ({c('shortage'):+.1f}) is mostly not this direct effect but its knock-on through wages and
  expectations, which the model's unit-root dynamics make large.
- *E3. Cars.* New and used vehicles and parts added {e03.loc['All motor vehicles', 'excess_2021_24']:+.1f} points over
  2021-24 (direct), {e03.loc['All motor vehicles', 'supply']:+.2f} of it labelled supply-driven by Shapiro's method.
- *E4. Other supply measures* (each in place of the GSCPI; line = full model; forecast error from E11):

{e04t}

  The supply-chain line depends on which measure stands for supply problems. The measures that forecast 2022-24 best
  give smaller lines.

**COVID drag and wages**
- *E1. Kinked Phillips curve* (Benigno-Eggertsson): with a threshold at V/U = 1, the extra slope above it is
  {_k[1]} in the wage equation and {_k[3]} in the price equation; no threshold from 0.6 to 1.4 is significant. Not
  adopted.
- *E13. Did wages slow in 2020?* The model's wage equation predicts 4-quarter wage growth of
  {e13.loc['2020-10-01', 'eci_predicted_4q']:.1f}% by 2020Q4; actual ECI growth was {e13.loc['2020-10-01', 'eci_actual_4q']:.1f}%,
  and the Atlanta Fed Wage Growth Tracker (same workers, so no layoff distortion) {e13.loc['2020-10-01', 'atlanta_fed_tracker']:.1f}%,
  unchanged from 2019. The COVID drag works mainly through that predicted slowdown, so it is overstated.
- *E5. States.* Lockdowns: with quarter effects (which remove everything national), each unit of stringency raised a
  state's unemployment by {e05.loc['covid_g0_state_quarterFE', 'estimate']:.1f} ({e05.loc['covid_g0_state_quarterFE', 'se']:.1f})
  points at once and {e05.loc['covid_g1_state_quarterFE', 'estimate']:.1f} ({e05.loc['covid_g1_state_quarterFE', 'se']:.1f}) a
  quarter later: about the same total as the national fit, which supports it. Wage curve: state wage growth falls
  {-e05.loc['wage_slope_u_below6', 'estimate']:.2f} per point of unemployment below 6% and less above it (change
  {e05.loc['wage_slope_change_above6', 'estimate']:+.2f}, s.e. {e05.loc['wage_slope_change_above6', 'se']:.2f}), flatter at high
  unemployment, as the COVID evidence suggests, but not significantly.

**Relief**
- *E7. Cross-country, quarterly* (core CPI, 2021Q4): US relief effect {e07.loc['2021Q4 only, advanced', 'us_effect']:+.1f}
  ({e07.loc['2021Q4 only, advanced', 'us_effect_se']:.1f}) against the model's {e07.loc['2021Q4 only, advanced', 'model_relief_same_metric']:.1f}
  for the same quarter; 2021Q4 + 2022Q4 is uninformative ({e07.loc['2021Q4 + 2022Q4, advanced', 'us_effect']:+.1f}, s.e.
  {e07.loc['2021Q4 + 2022Q4, advanced', 'us_effect_se']:.1f}).
- *E6. What recipients spent* (Opportunity Insights card data). Third stimulus checks: card spending ran
  {100 * e06.estimate.iloc[0]:.1f}% above trend in the six weeks after March 15, 2021 ({100 * e06.estimate.iloc[1]:.1f}% for the
  lowest-income quarter); scaled to all spending, about {100 * e06.estimate.iloc[2]:.0f}% of the $390 billion within six weeks
  (rough: card data miss rent, utilities and health). States that ended the $300 unemployment supplement early
  (25 states, June-July 2021): low-income card spending fell {-100 * e06.estimate.iloc[3]:.1f}% (s.e. {100 * e06.se.iloc[3]:.1f}) relative
  to other states. Too coarse to replace CBO's multipliers; nothing here suggests they are too low.

**The other Biden laws: the infrastructure law (IIJA) and the Inflation Reduction Act (IRA)**
- *E14.* Neither is in the relief lines. Each law's year-by-year budget effect as CBO scored it (IIJA: cost estimate
  for Senate Amendment 2137, Table 1; IRA: Estimated Budgetary Effects of P.L. 117-169, Sept 2022) is put through the
  same chain as the relief laws. CBO scored the IIJA at +$256 billion of deficits over 2021-31 and the IRA at -$58
  billion (it raised more than it spent). Three versions, each more generous to the claim that they caused inflation:

{e14t}

  The third row tests "promises of future money raise prices today" in its strongest form: every dollar of ten years
  of spending is treated as if it reached the economy the quarter the law was signed. Even then the two laws together
  add less than either relief law (Biden {c('biden'):+.1f}, Trump {c('trump'):+.1f} in the same units). Timing: PCE
  inflation (4-quarter) was already 5.7% in 2021Q4, when the IIJA was signed; the IRA was signed in 2022Q3, after the
  2022Q2 peak. CBO's August 4, 2022 letter to Senator Graham (cbo.gov/publication/58357): "In calendar year 2022,
  enacting the bill would have a negligible effect on inflation ... In calendar year 2023, inflation would probably be
  between 0.1 percentage point lower and 0.1 percentage point higher under the bill than it would be under current law."
  Market expectations on the days the laws' fate was decided (change from the last close before the news to the first
  close after; ordinary range = 5th-95th percentile of same-length changes 2015-19):

{e14evt}

  No consistent pattern. Expectations fell when Build Back Better passed the House and did not fall when Manchin killed
  it. They rose in the window of the Manchin-Schumer deal (July 27, 2022), but that afternoon the FOMC also raised rates
  by 3/4 point (statement at 2:00 p.m.), and 5-year breakevens kept rising by similar amounts on the following days
  ({_dw['2022-07-27']:+.2f}, {_dw['2022-07-28']:+.2f}, {_dw['2022-07-29']:+.2f}), so the deal can't be isolated. Breakevens
  also contain risk and liquidity premia. Limits: CBO's scores are projections made at passage, not outlays as they
  happened. Actual spending by quarter was not checked; the third row is the bound that covers any timing.

**The Fed**
- *E8. Other ways to identify the Fed's effect:*

{e08t}

  Every credible alternative gives the Fed a larger effect than the model (net {e08.fed_net_2021_24.iloc[1]:+.1f} to
  {e08.fed_net_2021_24.iloc[2]:+.1f} against {e08.fed_net_2021_24.iloc[0]:+.1f}), but all rest on instruments at or below the usual strength
  threshold (F 10). The last row is a weak-instrument artifact and is not used.
- *E9. Credibility.* On the day of the new framework (Aug 27, 2020) the 5-year, 5-year forward breakeven rose
  {e09[(e09.series == 'T5YIFR') & (e09.date == '2020-08-27')].change_2day.iloc[0]:+.2f} points over two days, inside the range of
  ordinary 2015-19 moves; it went from {e09l.T5YIFR_2020_08_26:.2f}% the day before to {e09l.T5YIFR_2021_12_31:.2f}% at end-2021 (2015-19
  range {e09l.T5YIFR_2015_19_min:.2f}-{e09l.T5YIFR_2015_19_max:.2f}%; 2021-22 peak {e09l.T5YIFR_2021_22_max:.2f}%). Market measures show
  long-run expectations drifting up toward the top of their pre-COVID range, not a break. Breakevens also contain
  risk and liquidity premia.

**Greed**
- *E10. Margins by industry* (BEA input-output accounts): economy-wide, gross operating surplus rose
  {e10.loc[2021, 'gos_share']:+.1f} points of output in 2021, {e10.loc[2022, 'gos_share']:+.1f} in 2022 and {e10.loc[2023, 'gos_share']:+.1f}
  in 2023 from its 2015-19 average. The largest rises were in water transportation, mining, farms, wood and chemical
  products, where supply was tight: scarcity rents, which Bernanke and Blanchard (2024, footnote 6) also suspect, rather
  than broad-based markups. (Restaurants and hotels rise partly because PPP loans count as subsidies.)

**Testing the whole model**
- *E11. Out of sample.* Price equation estimated through 2021Q4 only, then 2022-24 inflation forecast from the actual
  inputs:

{e11t}

  The model beats simple benchmarks by half or more, but over-forecasts 2022-24 (too much persistence), least when
  supply problems are measured by delivery times or unfilled orders.

**Wages, unemployment checks, and why the ranges are wide** (`src/extensions/e15_wages_ui_ranges.py`)
- *E15 A. Were wages held down before COVID, and did 2021-24 correct it?* Labor's share of nonfarm business income
  averaged {_ls['1990':'1999'].mean():.0f} (index, 2017 = 100) in the 1990s and {_ls['2010':'2019'].mean():.1f} in the 2010s (BLS via FRED PRS85006173): pay
  did fall behind productivity. But 2020-24 did not reverse it:

{e15ft}

  Real pay rose about half as fast as productivity, so labor's share fell further. A catch-up term in the wage
  equation (last quarter's labor-share gap, 1990-2019) is small and not significant: {e15c.coef.iloc[0]:+.3f} (s.e.
  {e15c.se.iloc[0]:.3f}) on the gap from the 1990-2019 average, {e15c.coef.iloc[1]:+.3f} ({e15c.se.iloc[1]:.3f}) on the gap from trend;
  either way it adds at most {e15c.term_2020_24_max.max():.1f} points to any quarter's wage growth. Where catch-up did
  happen is at the bottom: the lowest-paid quarter of workers gained the most after inflation (Atlanta Fed Wage Growth
  Tracker, same workers a year apart; cumulative from December 2019 to December 2024, approximate):

{e15qt}

  So COVID gave low-wage workers leverage, but across all workers prices rose faster than pay, not the reverse. Wage
  catch-up is not a separate cause of the inflation; the low-wage gains are part of the worker-shortage and V/U lines.
- *E15 B. Unemployment checks.* The expanded benefits (the $600 and $300 weekly supplements, pandemic assistance for
  gig workers, extended weeks) are BEA's "Expansion of unemployment programs" line, one of the relief payments,
  with CBO's multiplier for unemployment benefits (0.67); they sit in the Trump and Biden relief lines by signing
  date. Their other possible effect, keeping people out of work, would show up in the worker-shortage line. Test: 25
  states ended the $300 supplement early (June 12 to July 31, 2021), the rest in September:

{e15ut}

  None of these is the sign the "benefits kept people home" story predicts at a size that matters: employment in the
  ending states did not rise relative to the others (all workers {e15u.estimate.iloc[0]:+.1%}, s.e. {e15u.se.iloc[0]:.1%}),
  unemployment did not fall, and wages did not fall. Limits: one summer, and the 95% ranges can't exclude a
  small effect.
- *E15 E. What makes the ranges wide.* Redraw one equation's coefficients at a time:

{e15wt}

  Two estimates set almost all the width. The price equation's response to supply-chain pressure sets the
  supply-chain and war ranges. The wage equation's response to job openings per unemployed sets the relief, COVID,
  worker-shortage and pent-up ranges. Okun's law, the Beveridge curve, the Fed model and the relief timing add little
  (`output/uncertainty_sources.log`).
- *E15 C, D. Two new sources of data tried, neither adopted.* (C) A state wage curve on job openings per unemployed
  (JOLTS state openings over LAUS unemployed, 51 states, 2009-2024, state and quarter fixed effects):
  {e15s.value.iloc[0]:.2f} (s.e. {e15s.se.iloc[0]:.2f}); 2009-19 only {e15s.value.iloc[1]:.2f} ({e15s.se.iloc[1]:.2f}). The model's
  long-run slope is {e15s.value.iloc[2]:.2f} (redraws {e15s.value.iloc[3]:.2f} to {e15s.value.iloc[5]:.2f}). The state estimate is
  too imprecise, and too dependent on matching a one-year state regression to a long-run national slope, to adopt;
  E16 shows what it would do. (D) Relief size from the unemployment data: see Section 5, item 3.

**Other countries' data, aimed at the two estimates that set the width** (`src/extensions/e17_europe_panel.py`)
- *E17 A. The model's wage and price equations estimated on 25 European countries*, 2010-24 (Eurostat: labour cost
  index, job vacancies, unemployed persons, HICP), same lags and restrictions as the US model, country fixed effects,
  errors clustered by country. Expectations are proxied by the past year's inflation (no comparable survey). V/U is
  measured relative to each country's 2010-19 average because vacancy surveys differ in coverage. The US rows use the
  same units.

{e17wt}

{e17pt}

  Neither is adopted. The wage slope runs from {_w17.long_run_slope.min():.2f} to {_w17.long_run_slope.max():.2f}
  depending on the specification, a wider spread than the US model's own uncertainty. Pooled over all 25 countries, the
  long-run supply-chain effect ({_p17.long_run_supply.iloc[0]:.2f}) matches the US model's
  ({e17.loc['US model, price', 'long_run_supply']:.2f}). But it falls to {_p17.long_run_supply.iloc[3]:.2f} for western Europe and
  {_p17.long_run_supply.iloc[2]:.2f} when all of 2020-21 is dropped, and rises to {_p17.long_run_supply.iloc[4]:.2f} for central and
  eastern Europe. The reason: the supply-chain index is one global series, so every country sees the same single
  episode. More countries average out country noise, but not whatever else happened worldwide at the same time.
  Nothing guarantees European wage-setting responds like American wage-setting, so the wage slopes need not match.
- *E17 B. Would sharper supply-chain price data help?* Category- or industry-level price data (E2) measure the
  DIRECT effect of supply-chain pressure on prices. Suppose that effect were known more and more precisely:

{e17vt}

  Even knowing it almost exactly leaves a range about {e17v.p95.iloc[-1] - e17v.p5.iloc[-1]:.0f} points wide, against
  {e17v.p95.iloc[1] - e17v.p5.iloc[1]:.0f} now. The rest comes from how persistent inflation is (the price equation's own lags),
  which category or industry data can't measure. It also moves the line up: the category panel's direct effect is
  larger than the model's. (Units here are the model's log changes, so they differ slightly from Section 8.) Monthly
  US price data were not used: they are the same US inflation the price equation is already estimated on, so they
  would count it twice.

**Not done**
- *Pooling the supply-chain effect across countries:* Bernanke & Blanchard's 11-economy study uses a different
  shortage measure in each country (Google searches, the GSCPI, surveys) and posts no data, so coefficients can't be pooled.
- *Splitting relief into household transfers vs loans across countries:* the IMF table gives only health vs non-health.
- *Formal model averaging by forecast record:* 12 forecast quarters are too few for stable weights; E11 is shown instead.
- *A full joint estimation of every link:* replaced by sequential updating (Section 8), which uses the same evidence
  but keeps each link's own estimate as the starting point.

## 8. The best estimate: the model updated with all the independent evidence

`src/extensions/e12_all_evidence.py`. Start from the model's own uncertainty (its 1,000-redraw ranges), then weight
the redraws by how well they match three pieces of evidence the model never used: actual wage growth 2020-24 (the wage
equation stops in 2019), the category-panel supply-chain effect (E2), and the cross-country relief effect (Section 6).
20,000 coefficient draws, resampled to 1,000 full model runs.

{e12t}

**E16: two more pieces of evidence** (`src/extensions/e16_narrower.py`). (I) 2020-24 PCE inflation, used only to
weight the wage and expectations equations, which stop in 2019 (the price equation already uses it). (S) The state
wage curve (E15 C), on each redraw's long-run wage slope.

{e16t}

The first column repeats Section 8's best estimate with a different set of 1,000 runs; it differs from the table
above by up to 0.1 point (simulation noise). Inflation adds nothing beyond the wage data. The state wage curve narrows
the relief, COVID and worker-shortage ranges by about a tenth to a sixth. It lowers the relief and worker-shortage
medians by about 0.4 to 0.5 points and shrinks the COVID drag by 1.5. It is not adopted, for the reasons in E15 C.
Neither touches the supply-chain line.

**The chart** (`output/fig16_best_ranges.png`, `src/make_unified_figure.py best`): every quarter's line from the model,
shaded with the 90% range of this best estimate rather than the model's own redraws. At the 2022Q2 peak the relief
ranges are about 40% narrower than on fig12.

**What the evidence changes.** Read with the out-of-sample and state results above:
1. **Supply chains: {r_('shortage')}.** The category panel finds a larger direct effect than the model's own, which raises the bottom of the range (from about 1 to 2.5). But the out-of-sample test (E11) and the other supply measures (E4) point the other way: most of this line is knock-on through wages and expectations, and the model's knock-on looks too persistent. Supply chains were clearly a major cause; the size is still uncertain by a factor of about three.
2. **COVID drag: {r_('covid_other')}.** Narrower by about a third. The cross-country evidence removes the deepest drags (which come with the largest relief effects). The wage data remove the shallowest: a model in which wages follow V/U in a straight line needs a strong V/U effect to explain the 2021-22 wage surge, and that same strength implies a deep 2020 drag. E13 shows wages did not in fact slow in 2020, so the true drag may be smaller than any version of this linear model can produce; the state wage curve (E5) hints that wages respond less when unemployment is high, though not significantly.
3. **Relief paid under Biden: {r_('biden')}; signed by Trump: {r_('trump')}.** The cross-country evidence trims the high-multiplier cases and the wage data the smallest; each president's relief is now about 1 to 4.6 points, median about 2.4.
4. **Supply versus demand:** with the category panel, supply chains + war and relief + pent-up demand + the Fed come out even ({e12.loc[('P(supply chains+war > demand)', 'share'), BEST]:.0%} of weighted redraws put supply first); counting the worker shortage as supply, {e12.loc[('P(supply chains+war+worker > demand)', 'share'), BEST]:.0%}. The SF Fed labels (Section 6) also say about even. The data support "both, in similar measure", not "mostly supply" or "mostly demand".
5. **The Fed:** the evidence above doesn't touch the Fed lines; E8 says they are more likely too small than too large.

## 9. Robustness (points at the 2022Q2 peak; `output/robustness_unified.csv`, `src/robustness.py`)

{rt}

Holding the lockdown index at its 2022Q4 value changes only 2023-24 (the fit ends in 2022): averaged over 2021-23 the COVID drag goes from {rb.loc[('covid_other', 'avg 2021-23')].iloc[0]:+.2f} to {rb.loc[('covid_other', 'avg 2021-23'), 'stringency_hold'].iloc[0]:+.2f} and 'not explained' from {rb.loc[('unexplained', 'avg 2021-23')].iloc[0]:+.2f} to {rb.loc[('unexplained', 'avg 2021-23'), 'stringency_hold'].iloc[0]:+.2f} (quarterly annualized log points). The model total stays between {rb.loc[('model_total', '2022Q2')].min():.2f} and {rb.loc[('model_total', '2022Q2')].max():.2f} at the peak under every variant.

## 10. Against published estimates (`output/COMPARISON.md`)

{cmp_}
## 11. References

- Aladangady, A., D. Cho, L. Feiveson, E. Pinto (2022). [Excess Savings during the COVID-19 Pandemic](https://www.federalreserve.gov/econres/notes/feds-notes/excess-savings-during-the-covid-19-pandemic-20221021.html). FEDS Notes, Oct 21.
- Abdelrahman, H., L. Oliveira (2023). [Excess No More? Dwindling Pandemic Savings](https://www.frbsf.org/research-and-insights/blog/sf-fed-blog/2023/08/16/excess-no-more-dwindling-pandemic-savings/). SF Fed Blog, Aug 16.
- Barnichon, R. (2022). [What If? Monetary Policy in Hindsight](https://www.frbsf.org/research-and-insights/publications/economic-letter/2022/10/what-if-monetary-policy-in-hindsight/). FRBSF Economic Letter 2022-28.
- Bauer, M., E. Swanson (2023). Monetary policy surprises data: [SF Fed](https://www.frbsf.org/research-and-insights/data-and-indicators/monetary-policy-surprises/).
- Beckworth, D., P. Horan (2025). Mercatus Center working paper (not peer reviewed); see `CAUSES_SOURCES.md`.
- Blanchard, O. J., B. S. Bernanke (2023). [What Caused the US Pandemic-Era Inflation?](https://www.nber.org/papers/w31417) NBER WP 31417, June; replication by L. Lorenzoni, [GitHub](https://github.com/luigilor/bernanke-blanchard23).
- Congressional Budget Office (2020). [The Effects of Pandemic-Related Legislation on Output](https://www.cbo.gov/publication/56537).
- Glover, A., J. Mustre-del-Río, A. von Ende-Becker (2023). KC Fed Economic Review, Jan 12 ([RePEc](https://ideas.repec.org/a/fip/fedker/95477.html)); quotes in `CAUSES_SOURCES.md`.
- Oxford COVID-19 Government Response Tracker, [data](https://github.com/OxCGRT/covid-policy-dataset).
- HHS. [COVID-19 Public Health Emergency](https://www.hhs.gov/coronavirus/covid-19-public-health-emergency/index.html) (expired May 11, 2023).
- Jordà, Ò., C. Liu, F. Nechio, F. Rivera-Reyes (2022). [Why Is U.S. Inflation Higher than in Other Countries?](https://www.frbsf.org/research-and-insights/publications/economic-letter/2022/03/why-is-us-inflation-higher-than-in-other-countries/) FRBSF EL 2022-07.
- Liu, Z., T. Nguyen (2023). [Global Supply Chain Pressures and U.S. Inflation](https://www.frbsf.org/research-and-insights/publications/economic-letter/2023/06/global-supply-chain-pressures-and-us-inflation). FRBSF EL 2023-14.
- Shapiro, A. H. (2022). [How Much Do Supply and Demand Drive Inflation?](https://www.frbsf.org/research-and-insights/publications/economic-letter/2022/06/how-much-do-supply-and-demand-drive-inflation/) FRBSF EL 2022-15; [data](https://www.frbsf.org/research-and-insights/data-and-indicators/supply-and-demand-driven-pce-inflation/).
- de Soyres, F., A. M. Santacreu, H. Young (2022). [Fiscal policy and excess inflation during Covid-19: a cross-country view](https://www.federalreserve.gov/econres/notes/feds-notes/fiscal-policy-and-excess-inflation-during-covid-19-a-cross-country-view-20220715.htm). FEDS Notes, July 15.
- IMF (2021). [Database of Fiscal Policy Responses to COVID-19](https://www.imf.org/en/Topics/imf-and-covid19/Fiscal-Policies-Database-in-Response-to-COVID-19), October 2021 edition. OECD, [Consumer price indices](https://sdmx.oecd.org/public/rest/data/OECD.SDD.TPS,DSD_PRICES@DF_PRICES_ALL,1.0) (DF_PRICES_ALL). IMF, World Economic Outlook inflation (PCPIPCH), [DataMapper API](https://www.imf.org/external/datamapper/api/v1/PCPIPCH). Downloaded October 22, 2026.
- Data: BEA NIPA ([NipaDataQ.txt](https://apps.bea.gov/national/Release/TXT/NipaDataQ.txt)), BEA pandemic program tables, FRED, NY Fed GSCPI, SF Fed proxy funds rate. Download dates: October 16-17, 2026 (file dates in `data/raw/`).
"""
open(ROOT + "output/REPORT.md", "w").write(doc)
print("saved", len(doc))
