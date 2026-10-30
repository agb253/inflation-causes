"""Cross-check: the same causes run through the Federal Reserve Board's FRB/US model instead of our chain.

FRB/US (PyFRB/US 1.1.1 and the Aug 2026 LONGBASE data, data/raw/frbus/SOURCE.txt) is first made to reproduce
2020Q1-2024Q4 exactly (init_trac: tracking residuals). Each cause is then removed by changing the SAME input our model
uses, and its contribution = actual 4-quarter PCE inflation (pic4) - FRB/US inflation without it (as E1).

Settings for every run: federal funds rate exogenous at its actual path (dmpex = 1), no fiscal feedback rule
(dfpdbt = dfpsrp = 0), VAR-based expectations (PyFRB/US default). So, as in our model, the Fed does not react to the
causes; only the Fed lines move the funds rate.

Causes and how each input enters FRB/US:
  relief (trump/biden)  BEA program payments (src/fiscal_by_law.py, payments before March 2021 = Trump), $bn SAAR:
      - to households as paid -> federal transfers gtn (household transfer income yhtn = uyhtn x gtn):
        rebate checks, unemployment programs, FEMA lost wages, child tax credit increase, student-loan pause;
      - rental assistance -> gtn, at the pace states paid it out (Hutchins grant weights, as our model);
      - grants to state & local governments (Coronavirus Relief Fund, State & Local Fiscal Recovery Funds, education
        and transit funds) -> S&L purchases egse, at the Hutchins grant pace, deflated by the S&L price index;
      - business and provider aid (PPP, EIDL, ERTC, Restaurant fund, air carriers, sick-leave credits, Medicare rates,
        Provider Relief, farm aid): FRB/US has no business-transfer channel. BUS = "household" (default) routes it to
        gtn (PPP mostly paid wages and proprietors' income); BUS = "none" leaves it out (lower bound).
  fed_easing / fed_hikes  the same counterfactual as E6: SF Fed proxy funds rate held at its 2019Q4 average (2.35%)
      inside each episode window; the funds rate in FRB/US moves by the same amount as the proxy rate (proxy minus
      counterfactual, quarterly mean). After the window the funds rate is back on its actual path (our VAR instead
      lets it follow the usual response). The proxy rate includes QE, so this treats QE as an equivalent rate cut.
  energy_war  PCE energy and food prices (pcer, pcfr, relative to core) and the real oil price (poilr) held at their
      2021Q4 levels 2022Q1-2023Q1 (mcontrol on their add-factors); afterwards they grow as they actually did.
  shortage  the DIRECT effect of supply-chain pressure in our price equation (E11: GSCPI terms x their coefficients,
      relative to the 1990-2019 mean) taken out of core PCE inflation (picxfe add-factor). FRB/US supplies the knock-on.
  pentup  the same forced-saving spending as E5 (real $, 2021Q2-2023Q3) taken out of consumption of nondurables and
      services (eco forced to its actual path minus the flow, mcontrol). Durables and housing still respond.
No FRB/US counterpart (they stay in the remainder): worker shortage (FRB/US has no job-openings variable), COVID
shutdown drag, greedflation, pre-existing.

Run from project root:  python src/frbus/frbus_decomp.py   (PyFRB/US environment: pandas < 3, see SOURCE.txt)
Writes output/frbus/frbus_causes_quarterly.csv, frbus_vs_model.csv, frbus_unemployment.csv, frbus_run.log
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, "src")
from pyfrbus.frbus import Frbus
from pyfrbus.load_data import load_data
import fiscal_by_law as F
import pentup as P
import bb_model as m
import decompose as D
import unified_model as UM

RAW, OUT = "data/raw/frbus/", "output/frbus/"
S, E = pd.Period("2020Q1"), pd.Period("2024Q4")
BUS = os.environ.get("BUS", "household")
HOUSEHOLD = ["Economic impact payments", "Expansion of unemployment programs", "Lost wages supplemental payments",
             "Child tax credit", "Student loan forbearance"]
RENT = ["Emergency rental and homeowners assistance"]
STATE = ["Coronavirus Relief Fund", "Coronavirus State and Local Fiscal Recovery Funds", "Education Stabilization Fund",
         "Support for public transit agencies"]
REF_PFR = None


def q(ts):
    return pd.PeriodIndex(ts, freq="Q")


def baseline():
    d = load_data(RAW + "LONGBASE.TXT")
    d.loc[S:E, "dmpex"] = 1
    d.loc[S:E, ["dmpintay", "dmptay", "dmptlr", "dmpalt", "dmprr", "dmpgen", "dmptrsh"]] = 0
    d.loc[S:E, "rfffix"] = d.loc[S:E, "rff"]
    d.loc[S:E, ["dfpdbt", "dfpsrp"]] = 0
    return d


def paced(X, weights):
    """Spread each quarter's payment over later quarters with the given weights (rescaled to sum to 1)."""
    w = np.array(weights) / sum(weights); x = X.values
    return pd.Series([sum(w[h] * x[t - h] for h in range(len(w)) if t - h >= 0) for t in range(len(x))], index=X.index)


def relief_inputs(M):
    """$bn SAAR to households (gtn) and to S&L purchases (nominal), by FRB/US quarter."""
    M = M.reindex(columns=F.PROGRAMS, fill_value=0.0)
    bus = [c for c in M if c not in HOUSEHOLD + RENT + STATE]
    hh = M[HOUSEHOLD].sum(axis=1) + paced(M[RENT].sum(axis=1), F.W["grants"])
    if BUS == "household": hh = hh + M[bus].sum(axis=1)
    sl = paced(M[STATE].sum(axis=1), F.W["grants"])
    hh.index, sl.index = q(hh.index), q(sl.index)
    return hh, sl


def shortage_direct():
    """Direct effect of GSCPI on quarterly annualized PCE inflation in our price equation (E11), 2020Q1-2024Q4."""
    d = UM.quarterly(); x = m.build(d); D.PROD_LAG = 0
    x, _ = UM.add_greed(x)
    C = D.coefs(UM.estimate_with_greed(x, m.estimate(x, D.PROD)))
    ref = x.shortage.loc[:UM.REF].mean()
    dev = (x.shortage - ref).values
    pos = x.index.get_loc(UM.START)
    eff = [C["gp"][21:26] @ dev[t:t - 5:-1] for t in range(pos, len(x))]
    return pd.Series(eff, index=q(x.index[pos:])), C["gp"][21:26]


def fed_deltas():
    """Quarterly change to the funds rate that removes each episode (same windows as unified_model.fed_effect)."""
    pfr, effr = UM.fed_rates()
    ref = pfr.loc["2019-10":"2019-12"].mean()
    a = pfr.loc["2020-01":]
    below = a[a < ref].index; w0, w1 = below.min(), below.max()
    ease = (np.maximum(a, ref) - a).where((a.index >= w0) & (a.index <= w1), 0.0)
    peak = effr.loc[w1 + 1:].idxmax()
    hike = (np.minimum(a, ref) - a).where((a.index > w1) & (a.index <= peak), 0.0)
    f = lambda s: s.groupby(s.index.asfreq("Q")).mean().reindex(pd.period_range(S, E, freq="Q")).fillna(0.0)
    return f(ease), f(hike), ref, (w0, w1, peak)


def main():
    os.makedirs(OUT, exist_ok=True)
    model = Frbus(RAW + "model.xml")
    base = model.init_trac(S, E, baseline())
    act = model.solve(S, E, base)
    assert (act.loc[S:E, "pic4"] - base.loc[S:E, "pic4"]).abs().max() < 1e-8
    log = [f"FRB/US tracking check: max |solved - actual| 4-qtr PCE inflation = "
           f"{(act.loc[S:E, 'pic4'] - base.loc[S:E, 'pic4']).abs().max():.1e}", f"business aid treated as: {BUS}"]
    runs = {}

    def run(name, data):
        runs[name] = model.solve(S, E, data)

    def run_ctrl(name, data, targ, inst):
        """Force each target onto its '<target>_t' path (where not NaN) by adjusting its add-factor, quarter by
        quarter. Every target equation is in log changes with an additive add-factor, so the update is exact up to
        the model's feedback; repeated until the miss is below 1e-9. (PyFRB/US mcontrol did not converge here.)"""
        x = data.copy()
        quarters = sorted({p for t in targ for p in x.loc[S:E].index[x.loc[S:E, t + "_t"].notna()]})
        for p in quarters:
            for _ in range(20):
                sol = model.solve(S, E, x); worst = 0.0
                for t, a in zip(targ, inst):
                    tg = x.loc[p, t + "_t"]
                    if np.isnan(tg): continue
                    err = np.log(tg) - np.log(sol.loc[p, t]); worst = max(worst, abs(err))
                    x.loc[p, a] += err
                if worst < 1e-9: break
            assert worst < 1e-6, (name, p, worst)
        runs[name] = model.solve(S, E, x)

    # relief
    X = F.outlays(); T, B = F.by_signer(X)
    for nm, M in [("trump", T), ("biden", B)]:
        hh, sl = relief_inputs(M)
        x = base.copy()
        x.loc[S:E, "gtn_aerr"] -= hh.reindex(x.loc[S:E].index).fillna(0.0).values
        price = base.egsen / base.egse
        sl_real = (sl.reindex(x.loc[S:E].index).fillna(0.0) / price.loc[S:E]).values
        x["egse_t"] = np.nan
        x.loc[S:E, "egse_t"] = base.loc[S:E, "egse"].values - sl_real
        x.loc[S:E, "egse_t"] = x.loc[S:E, "egse_t"].where(sl_real != 0)
        run_ctrl(nm, x, ["egse"], ["egse_aerr"])
        log.append(f"{nm}: to households {hh.sum() / 4:,.0f} $bn, S&L purchases {sl.sum() / 4:,.0f} $bn (2020-24 total)")

    # Fed
    ease, hike, ref, wins = fed_deltas()
    for nm, dl in [("fed_easing", ease), ("fed_hikes", hike)]:
        x = base.copy(); x.loc[S:E, "rfffix"] = base.loc[S:E, "rff"].values + dl.values
        run(nm, x)
    log.append(f"Fed: proxy rate held at {ref:.2f}; easing window {wins[0]}..{wins[1]}, hikes to {wins[2]}; "
               f"max funds-rate change easing +{ease.max():.2f}, hikes {hike.min():.2f}")

    # war: energy, food, oil held at 2021Q4 levels in the window
    x = base.copy(); w = pd.period_range("2022Q1", "2023Q1", freq="Q")
    for v in ["pcer", "pcfr", "poilr"]:
        x[v + "_t"] = np.nan; x.loc[w, v + "_t"] = base.loc[pd.Period("2021Q4"), v]
    run_ctrl("energy_war", x, ["pcer", "pcfr", "poilr"], ["pcer_aerr", "pcfr_aerr", "poilr_aerr"])

    # supply chains: direct effect out of core inflation
    dir_, coefs = shortage_direct()
    x = base.copy(); x.loc[S:E, "picxfe_aerr"] -= dir_.reindex(x.loc[S:E].index).values
    run("shortage", x)
    log.append(f"supply chains: GSCPI coefficients (lags 0-4) {np.round(coefs, 3).tolist()}; direct effect on "
               f"annualized PCE inflation, max {dir_.max():.2f} pts ({dir_.idxmax()})")

    # pent-up demand
    c, tr, gap, stock, start = P.pieces()
    qs = pd.date_range(start, "2023-07-01", freq="QS")
    flow17 = pd.Series(stock / len(qs) * 4, index=q(qs))                       # $bn SAAR, chained 2017
    c17 = c.copy(); c17.index = q(c17.index)
    flow12 = flow17 * (base.ecnia / c17).reindex(flow17.index)                  # rescale to FRB/US chained 2012 $
    x = base.copy(); x["eco_t"] = np.nan
    x.loc[flow12.index, "eco_t"] = base.loc[flow12.index, "eco"] - flow12
    run_ctrl("pentup", x, ["eco"], ["eco_aerr"])
    log.append(f"pent-up: stock {stock:,.0f} $bn (2017 $), spent {qs[0].date()}..{qs[-1].date()}")

    # what FRB/US's wage and core-price equations cannot explain: their tracking residuals, 2020-24
    for nm, cols in [("resid_core_price", ["picxfe_trac"]), ("resid_wage", ["pieci_trac"])]:
        x = base.copy(); x.loc[S:E, cols] = 0.0
        run(nm, x)

    idx = pd.period_range(S, E, freq="Q")
    pi = pd.DataFrame({k: act.loc[idx, "pic4"] - r.loc[idx, "pic4"] for k, r in runs.items()})
    du = pd.DataFrame({k: act.loc[idx, "lur"] - r.loc[idx, "lur"] for k, r in runs.items()})
    pi["actual_pce_yoy"] = act.loc[idx, "pic4"]
    pi.index = pi.index.astype(str); du.index = du.index.astype(str)
    pi.round(4).to_csv(OUT + "frbus_causes_quarterly.csv"); du.round(4).to_csv(OUT + "frbus_unemployment.csv")

    ours = pd.read_csv("output/unified_causes_quarterly.csv", index_col=0)
    our_u = pd.read_csv("output/unified_unemployment_parts.csv", index_col=0) if os.path.exists(
        "output/unified_unemployment_parts.csv") else None
    q4 = [p for p in pi.index if p.endswith("Q4") and p >= "2021"]
    rows = []
    for k in runs:
        mine = ours[k] if k in ours else pd.Series(np.nan, index=ours.index)
        r = {"cause": k, "frbus_2021_24": pi.loc[q4, k].sum(), "model_2021_24": mine.loc[q4].sum(min_count=1),
             "frbus_2022Q2": pi.loc["2022Q2", k], "model_2022Q2": mine.loc["2022Q2"],
             "frbus_peak_unemp_effect": du[k].loc[du[k].abs().idxmax()]}
        rows.append(r)
    cmp_ = pd.DataFrame(rows).set_index("cause")
    cmp_.round(3).to_csv(OUT + "frbus_vs_model.csv")
    log += ["", "2021-24 totals (sum of the four Q4 year-over-year values) and the 2022Q2 peak, points of PCE inflation:",
            cmp_.round(2).to_string(), "", "Quarterly, FRB/US (points of 4-quarter PCE inflation):",
            pi.round(2).to_string(), "", "Unemployment effect (points; minus = cause lowered unemployment):",
            du.round(2).to_string()]
    if our_u is not None: log += ["", "Our model's unemployment parts (same sign convention as its file):",
                                  our_u.round(2).to_string()]
    open(OUT + f"frbus_run{'' if BUS == 'household' else '_' + BUS}.log", "w").write("\n".join(log) + "\n")
    print("\n".join(log))


if __name__ == "__main__":
    main()
