"""Robustness of the unified model (src/unified_model.py): re-run the point estimate under each alternative choice and
report every cause at the 2022Q2 peak and averaged over 2021Q1-2023Q4. Writes output/robustness_unified.csv.
Run from project root:  python src/robustness.py"""
import sys
import numpy as np
import pandas as pd
sys.path.insert(0, "src")
import unified_model as M
import unified_data as U
import fed_svar as S
import pentup as P
import fiscal_by_law as F

VARIANTS = [  # name, what changes, setter
    ("baseline", "As published", {}),
    ("fed_mps_orth", "Fed instrument = MPS_ORTH (weak, F 3.6)", {"S.INSTR": "MPS_ORTH"}),
    ("covid_residual", "COVID = leftover (forced to match unemployment), the old method", {"M.COVID_MODE": "residual"}),
    ("stringency_hold", "Lockdown index held at its 2022Q4 value after the tracker ends", {"U.STRINGENCY_AFTER": "hold"}),
    ("no_pentup", "No pent-up demand", {"M.PENT": (0.0, "2023-07-01", P.TREND)}),
    ("pentup_high", "Pent-up demand: multiplier 1.0, spent by 2023Q3", {"M.PENT": (1.0, "2023-07-01", P.TREND)}),
    ("pentup_slow", "Pent-up demand spent over 2021Q2-2024Q4", {"M.PENT": (P.M_POINT, "2024-10-01", P.TREND)}),
    ("pentup_trend1719", "Pent-up demand: spending trend fit 2017-2019", {"M.PENT": (P.M_POINT, "2023-07-01", ("2017-01-01", "2019-10-01"))}),
    ("fiscal_hutchins", "Relief timing = Hutchins Center weights", {"M.FISCAL": ("hutchins", 1.0)}),
    ("fiscal_cbo_scale", f"Relief scaled to CBO's 2020 total (x{F.CBO_SCALE})", {"M.FISCAL": ("geometric", F.CBO_SCALE)}),
    ("ridge_05", "Fed counterfactual ridge 0.5", {"M.RIDGE": 0.5}),
]
MODS = {"M": M, "U": U, "S": S}


def pct_factor(index):
    pi = U.nipa({"DPCERG"}).DPCERG
    return ((100 * (pi / pi.shift(4) - 1)) / (100 * np.log(pi).diff(4))).reindex(index)


def run(name, sets):
    keep = {k: getattr(MODS[k[0]], k[2:]) for k in sets}
    for k, v in sets.items(): setattr(MODS[k[0]], k[2:], v)
    M.surprises.cache_clear()
    try:
        d, x, est, point, du, vup, sv, ok, bev = M.main()
    finally:
        for k, v in keep.items(): setattr(MODS[k[0]], k[2:], v)
    t = M.tidy(point)
    y = M.yoy(t, x).mul(pct_factor(t.index), axis=0)
    q = t.loc["2021-01-01":"2023-10-01"].mean()
    rows = {}
    for c in M.LABELS:
        rows[(c, "2022Q2")] = y.loc["2022-04-01", c]
        rows[(c, "avg 2021-23")] = q[c]
    causes = [c for c in M.LABELS if c != "unexplained"]
    rows[("model_total", "2022Q2")] = y.loc["2022-04-01", causes].sum()
    rows[("model_total", "avg 2021-23")] = q[causes].sum()
    rows[("max_abs_unexplained", "2020-24")] = y.unexplained.abs().max()
    return pd.Series(rows, name=name)


if __name__ == "__main__":
    out = pd.concat([run(n, s) for n, _, s in VARIANTS], axis=1)
    out.columns = pd.MultiIndex.from_tuples([(n, w) for n, w, _ in VARIANTS])
    out.round(3).to_csv("output/robustness_unified.csv")
    pd.set_option("display.width", 300); pd.set_option("display.max_columns", 30)
    print(out.droplevel(1, axis=1).round(2).to_string())
