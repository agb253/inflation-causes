"""Effect of the pandemic relief laws on the level of GDP, by who signed them, quarterly 2020Q1-2024Q4.

  effect_t (% of potential GDP) = 100 / PotGDP_t x sum_p  m_p x sum_h w_p,h x X_p,t-h

X_p,t  federal outlays (or revenue loss) of program p in quarter t, $bn at an annual rate, as recorded in the national accounts:
       BEA, "Effects of Selected Federal Pandemic Response Programs on Federal Government Receipts, Expenditures, and
       Saving", releases 2020Q4 Third, 2021Q4 Third, 2022Q4 Third (data/raw/bea_pandemic/). Each quarter is taken from
       the newest release that covers it. BEA stopped publishing the table after 2022Q4, so payments after 2022 are not
       counted (they were small: the main programs had ended).
m_p    GDP per dollar of budgetary cost, CBO, "The Effects of Pandemic-Related Legislation on Output" (Sept 2020),
       Table 3 (data/raw/cbo/56537-pandemic-legislation.pdf, p. 6). CBO categories -> CBO_M below.
w_p,h  share of the effect that lands h quarters after payment: timing weights in the Hutchins Center Fiscal Impact
       Measure code, R/mpc.R (data/raw/hutchins/repo/mpc.R, commit in COMMIT), rescaled to sum to 1 so that the total
       effect equals CBO's multiplier.
PotGDP CBO real potential GDP (FRED GDPPOT) x GDP price index (FRED GDPDEF) / 100, $bn at an annual rate.

Who signed: a payment made before March 2021 is Trump-signed (FFCRA, CARES Act, PPP and Health Care Enhancement Act,
CRRSA Act of Dec 2020, Aug 2020 lost-wages memorandum); a payment made March 2021 or later is Biden-signed (American
Rescue Plan, signed 2021-03-11). This is deliberately the rule least favourable to the "Trump stimulus mattered too"
case: it credits Biden with every later payment, including money appropriated by Trump-signed laws (for example the
2021 Paycheck Protection Program round funded by CRRSA). In 2021Q1, economic impact payments are split with BEA's
monthly table (Jan+Feb 2021 vs March 2021, April 2021 release); every other program is split 2/3 Trump, 1/3 Biden
(two of the three months; assumes an even monthly flow).
"""
import functools
import numpy as np
import pandas as pd
import unified_data as U

RAW = "data/raw/bea_pandemic/"
FILES = ["effects-of-selected-federal-pandemic-response-programs-on-federal-government-receipts-expenditures-and-saving-2020q4-3rd.xlsx",
         "effects-of-selected-federal-pandemic-response-programs-on-federal-government-receipts-expenditures-and-saving-2021q4-3rd.xlsx",
         "effects-of-selected-federal-pandemic-response-programs-on-federal-government-receipts-expenditures-and-saving-2022q4-3rd.xlsx"]
MONTHLY = "effects-of-selected-federal-pandemic-response-programs-on-personal-income-april-2021.xlsx"

# CBO Table 3, "Cumulative Effect on GDP per Dollar of Effect on the Deficit (Dollars)"
CBO_M = {"ppp": 0.36, "ui": 0.67, "rebates": 0.60, "state_local": 0.88, "other_spending": 0.78, "revenue": 0.37}
# Hutchins FIM R/mpc.R weight vectors (first element = quarter of payment)
W = {"rebate": [0.238, 0.145, 0.11] + [0.079] * 3 + [0.084] * 2 + [0.039] * 2 + [0.023],          # mpc_rebate_checks
     "ui": [0.253] * 2 + [0.161] * 2 + [0.075, 0.05, 0.025, 0.022],                                # mpc_ui_arp
     "business": [0.04] * 2 + [0.017] * 10,                                                        # mpc_small_businesses_arp
     "grants": [0.07] * 2 + [0.049] * 10 + [0.0475] * 7 + [0.0375],                                # mpc_arp_non_health_grants
     "direct": [0.18] + [0.09] * 2 + [0.05] * 7 + [0.03]}                                          # mpc_direct_aid_arp
# BEA line label (footnote digits stripped) -> (CBO category, timing vector, sign: +1 outlay, -1 receipt reduction)
PROGRAMS = {
    "Aviation tax holiday": ("revenue", "direct", -1),
    "Student loan forbearance": ("other_spending", "direct", -1),       # CBO Table 3 note d: "aid for student loans"
    "Paycheck Protection Program lender processing fees": ("ppp", "business", 1),
    "Child tax credit": ("rebates", "rebate", 1),                        # increase over the pre-ARPA level, see ctc_increment()
    "Economic impact payments": ("rebates", "rebate", 1),
    "Expansion of unemployment programs": ("ui", "ui", 1),
    "Increase in Medicare reimbursement rates": ("other_spending", "direct", 1),
    "Lost wages supplemental payments": ("other_spending", "ui", 1),     # FEMA; CBO note d lists FEMA under other spending
    "Paycheck Protection Program loans to NPISH": ("ppp", "business", 1),
    "Provider Relief Fund to NPISH": ("other_spending", "direct", 1),
    "Coronavirus Relief Fund": ("state_local", "grants", 1),
    "Education Stabilization Fund": ("other_spending", "grants", 1),    # CBO note d lists the education stabilization fund
    "Provider Relief Fund": ("other_spending", "direct", 1),            # appears twice (grants to states, subsidies): both summed
    "Coronavirus Food Assistance Program": ("other_spending", "direct", 1),
    "Economic Injury Disaster Loans": ("ppp", "business", 1),
    "Employee Retention Tax Credit": ("revenue", "business", 1),
    "Grants to air carriers": ("other_spending", "business", 1),
    "Paycheck Protection Program loans to businesses": ("ppp", "business", 1),
    "Restaurant Revitalization Fund": ("ppp", "business", 1),
    "Support for public transit agencies": ("other_spending", "grants", 1),
    "Tax credits to fund paid sick leave": ("revenue", "business", 1),
    "Coronavirus State and Local Fiscal Recovery Funds": ("state_local", "grants", 1),
    "Emergency rental and homeowners assistance": ("state_local", "grants", 1),
}


def read_release(f):
    v = pd.read_excel(RAW + f, header=None)
    hdr = v.iloc[5:7, 2:8].ffill(axis=1)
    qs = [pd.Period(f"{int(float(y))}{q}", freq="Q").to_timestamp() for y, q in zip(hdr.iloc[0], hdr.iloc[1])]
    rows = {}
    for _, r in v.iterrows():
        lab = r[1]
        if not isinstance(lab, str): continue
        lab = lab.strip().rstrip("0123456789 ").strip()
        if lab in PROGRAMS:
            vals = pd.to_numeric(pd.Series(r[2:8].values, index=qs), errors="coerce").fillna(0.0)
            rows[lab] = rows.get(lab, 0) + vals          # Provider Relief Fund appears in two lines
    return pd.DataFrame(rows)


def outlays():
    return _outlays().copy()


@functools.lru_cache(None)
def _outlays():
    """Program x quarter, $bn SAAR; newest release wins for each quarter."""
    out = None
    for f in FILES:
        d = read_release(f)
        out = d if out is None else d.combine_first(out)        # values from the newer release take priority
    out = out.sort_index().fillna(0.0)
    # Child tax credit: BEA's line includes the credit that existed before ARPA; count only the increase over its
    # 2021Q1 level (the last quarter before ARPA's advance payments)
    out["Child tax credit"] = (out["Child tax credit"] - out.loc["2021-01-01", "Child tax credit"]).clip(lower=0)
    out.loc[out.index < "2021-04-01", "Child tax credit"] = 0.0
    for lab, (_, _, sign) in PROGRAMS.items():
        if lab in out: out[lab] = sign * out[lab]
    # Student-loan payment pause after BEA's last table (2022Q4): the Education Department notice quoted in news
    # coverage says "Student loan interest will resume starting on Sept. 1, 2023, and payments will be due starting in
    # October". BEA records the pause as forgone federal interest receipts, flat at its 2022Q4 value since 2020Q3; we
    # hold that value for 2023Q1-Q2 and for 2 of the 3 months of 2023Q3 (July, August).
    sl = out.loc["2022-10-01", "Student loan forbearance"]
    for q, share in [("2023-01-01", 1.0), ("2023-04-01", 1.0), ("2023-07-01", 2 / 3)]:
        out.loc[pd.Timestamp(q)] = 0.0
        out.loc[pd.Timestamp(q), "Student loan forbearance"] = share * sl
    return out.sort_index()


@functools.lru_cache(None)
def eip_trump_share_2021q1():
    v = pd.read_excel(RAW + MONTHLY, header=None)
    row = v[v[1].astype(str).str.strip().str.startswith("Economic impact payments")].iloc[0]
    jan, feb, mar = (float(row[i]) for i in (5, 6, 7))            # columns: Oct Nov Dec Jan Feb Mar Apr
    return (jan + feb) / (jan + feb + mar)


def by_signer(X):
    tr = pd.DataFrame(0.0, index=X.index, columns=X.columns)
    tr.loc[X.index < "2021-01-01"] = 1.0
    tr.loc["2021-01-01"] = 2 / 3
    tr.loc["2021-01-01", "Economic impact payments"] = eip_trump_share_2021q1()
    return X * tr, X * (1 - tr)


def gdp_effect(X, index):
    pot = (U.qmean(U.fred("GDPPOT")) * U.qmean(U.fred("GDPDEF")) / 100).reindex(index)
    X = X.reindex(index).fillna(0.0)
    eff = pd.Series(0.0, index=index)
    for lab in X:
        cat, wk, _ = PROGRAMS[lab]
        w = np.array(W[wk]); w = w / w.sum()
        x = X[lab].values
        conv = np.array([sum(w[h] * x[t - h] for h in range(len(w)) if t - h >= 0) for t in range(len(x))])
        eff += CBO_M[cat] * conv
    return 100 * eff / pot


GROUPS = {"student_loans": ["Student loan forbearance"],
          "rental_assist": ["Emergency rental and homeowners assistance"]}   # reported separately inside each signer


def run(index):
    X = outlays()
    T, B = by_signer(X)
    out = {}
    for nm, M in [("trump", T), ("biden", B)]:
        for g, cols in GROUPS.items():
            out[f"{nm}_{g}"] = gdp_effect(M[cols], index)
        out[nm] = gdp_effect(M.drop(columns=sum(GROUPS.values(), [])), index)
    return out, X, T, B


# Timing variants. "geometric": share (1-L) L^h of the effect lands h quarters after payment, L = GEO_LAMBDA, the value
# whose shape best fits CBO's own quarterly path for the 2020 laws (Table 2 of the CBO report, minus the Federal
# Reserve facilities row), with the level left free (fit_cbo_timing()). "hutchins": the FIM weight vectors above.
# scale: 1 = bottom-up (BEA-recorded payments only); CBO_SCALE = the factor that makes the bottom-up effect of 2020
# payments match CBO's quarterly estimate for the 2020 laws (CBO counts provisions BEA's table does not list).
GEO_LAMBDA, CBO_SCALE = 0.74, 2.04
CBO_TABLE2 = pd.Series([5.0 - 0.0, 8.1 - 0.2, 6.4 - 0.3, 5.0 - 0.4, 4.0 - 0.3, 2.4 - 0.2, 1.3 - 0.2],
                       index=pd.date_range("2020-04-01", "2021-10-01", freq="QS"))    # Total minus Fed facilities row


def run_variant(index, timing, scale):
    keep = dict(W)
    if timing == "geometric":
        for k in W: W[k] = [(1 - GEO_LAMBDA) * GEO_LAMBDA ** h for h in range(40)]
    try:
        e, *_ = run(index)
    finally:
        W.update(keep)
    return {k: scale * v for k, v in e.items()}


def fit_cbo_timing(index):
    X = outlays(); X20 = X.copy(); X20.loc[X20.index >= "2021-01-01"] = 0.0
    keep = dict(W); best = None
    for lam in np.arange(0.30, 0.91, 0.01):
        for k in W: W[k] = [(1 - lam) * lam ** h for h in range(40)]
        e = gdp_effect(X20, index).reindex(CBO_TABLE2.index)
        s = (e @ CBO_TABLE2) / (e @ e); r = np.sqrt(((s * e - CBO_TABLE2) ** 2).mean())
        if best is None or r < best[0]: best = (r, round(lam, 2), round(s, 2))
    W.update(keep)
    return best
