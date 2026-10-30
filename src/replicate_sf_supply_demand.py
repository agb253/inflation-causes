"""Recompute the SF Fed supply-/demand-driven PCE inflation split from raw BEA data.

Method: Shapiro, "A Simple Framework to Monitor Inflation", FRBSF WP 2020-29,
section 6 (data/raw/sf_fed/paper/wp2020-29.pdf, pp. 18-19):
  eq. 20  p_i,t = Z_t-1 g + e^p_i,t     (log price index of category i)
  eq. 21  q_i,t = Z_t-1 g + e^q_i,t     (log quantity index of category i)
  Z_t-1 = constant + 12 lags of p_i and 12 lags of q_i; rolling 120-month window,
  keep the month-T residual.
  eq. 22  supply-driven if e^p and e^q have opposite signs, demand-driven if same sign.
  Ambiguous if either residual is "sufficiently close to zero", which the paper
  defines as "the middle 20% of the residuals in the respective regression sample
  distributions", excluding post-2020 residuals from that distribution.
  Contribution = most recent expenditure weight x monthly price change;
  year-over-year = 12-month rolling sum of monthly contributions.
Data: BEA NIPA underlying detail, Tables 2.4.3U (quantity), 2.4.4U (price),
2.4.5U (spending), monthly, from data/raw/bea/Section2All_xls.xlsx.
Categories: BEA's fourth level of detail (paper, p. 5), counting goods/services as
level 1; any branch that ends above level 4 is used at its last level.
Output: output/sf_replication_monthly.csv, output/sf_replication_categories.csv
"""
import sys

import numpy as np
import pandas as pd

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
XL = ROOT + "data/raw/bea/Section2All_xls.xlsx"
LAGS, WIN = 12, 120
LEVEL = int(sys.argv[1]) if len(sys.argv) > 1 else 4
AMB = sys.argv[2] if len(sys.argv) > 2 else "t"
FOOD_ENERGY = ("Food and beverages purchased for off-premises consumption",
               "Gasoline and other energy goods", "Electricity and gas")


def sheet(name):
    x = pd.read_excel(XL, sheet_name=name, header=None, skiprows=7, dtype=str)
    hdr = pd.read_excel(XL, sheet_name=name, header=None, skiprows=7, nrows=1).iloc[0]
    x = x[x[0].str.fullmatch(r"\d+", na=False)].copy()
    x.columns = ["line", "label", "code"] + [str(h) for h in hdr[3:]]
    x["line"] = x.line.astype(int)
    return x.set_index("line")


def categories(spend):
    """Lines 1-342: household goods and services, plus the NPISH line (342) as one category."""
    t = spend.loc[1:342, ["label"]].copy()
    t["ind"] = t.label.str.len() - t.label.str.lstrip().str.len()
    t["label"] = t.label.str.strip()
    svc = t.index >= 150
    t["lvl"] = t.ind // 2 + 1 - svc.astype(int)  # services sit under an extra "household consumption" line
    t.loc[[1, 151], "lvl"] = 0  # line 1 (total PCE) is indented 6 spaces in BEA's file; it is the root, not a category
    nxt = t.ind.shift(-1, fill_value=0)
    t["leaf"] = ~(nxt > t.ind)
    t.loc[342, ["lvl", "leaf"]] = [1, True]
    t = t.loc[:342]
    keep = (t.lvl == LEVEL) | ((t.lvl >= 1) & (t.lvl < LEVEL) & t.leaf)
    # drop rows nested under the NPISH line
    keep &= ~((t.index > 342))
    fe = set()
    for name in FOOD_ENERGY:
        i = t.index[t.label.str.startswith(name)][0]
        j = i + 1
        fe.add(i)
        while j in t.index and t.ind[j] > t.ind[i]:
            fe.add(j); j += 1
    c = t[keep].copy()
    c["food_energy"] = c.index.isin(fe)
    return c


def num(df, lines):
    d = df.loc[lines].drop(columns=["label", "code"]).T
    d.index = pd.PeriodIndex(d.index.str.replace("M", "-"), freq="M")
    return d.apply(pd.to_numeric, errors="coerce")


def residuals(lp, lq):
    """Month-T residuals of eqs. 20-21 and the ambiguous flag, for one category."""
    n = len(lp)
    X = np.column_stack([np.ones(n)] + [np.roll(lp, k) for k in range(1, LAGS + 1)]
                        + [np.roll(lq, k) for k in range(1, LAGS + 1)])
    X[:LAGS] = np.nan
    out = np.full((n, 4), np.nan)  # ep, eq, amb_p, amb_q
    for T in range(LAGS + WIN - 1, n):
        rows = slice(T - WIN + 1, T + 1)
        Xw = X[rows]
        if not (np.isfinite(Xw).all() and np.isfinite(lp[rows]).all() and np.isfinite(lq[rows]).all()):
            continue
        for k, y in enumerate((lp[rows], lq[rows])):
            b, *_ = np.linalg.lstsq(Xw, y, rcond=None)
            r = y - Xw @ b
            pre = r[:-1][IDX[rows][:-1] < 2020]
            out[T, k] = r[-1]
            if AMB == "t":  # |residual| / sd of pre-2020 window residuals < 0.125
                out[T, 2 + k] = abs(r[-1]) < 0.125 * pre.std(ddof=1) if len(pre) > 20 else False
            else:           # inside the middle 20% of the pre-2020 window residuals
                lo, hi = np.percentile(pre, [40, 60]) if len(pre) > 20 else (0, 0)
                out[T, 2 + k] = lo <= r[-1] <= hi
    return out


spend, price, qty = sheet("U20405-M"), sheet("U20404-M"), sheet("U20403-M")
cats = categories(spend)
L = list(cats.index)
assert (price.loc[L, "label"].str.strip() == cats.label).all(), "line numbers differ across tables"
P, Q, S = num(price, L), num(qty, L), num(spend, L)
IDX = np.array([p.year for p in P.index])
print(f"level {LEVEL}: {len(L)} categories ({(~cats.food_energy).sum()} core)")

weight = S.div(S.sum(axis=1), axis=0).shift(1)        # most recent (previous-month) spending share
dp = np.log(P).diff()                                  # monthly price change
lab = pd.DataFrame(index=P.index, columns=L, dtype=object)
for c in L:
    with np.errstate(divide="ignore", invalid="ignore"):
        r = residuals(np.log(P[c].values), np.log(Q[c].values))
    ok = ~np.isnan(r[:, 0])
    amb = (r[:, 2] == 1) | (r[:, 3] == 1)
    same = np.sign(r[:, 0]) == np.sign(r[:, 1])
    lab.loc[ok, c] = np.where(amb[ok], "ambiguous", np.where(same[ok], "demand", "supply"))

contrib = (weight * dp) * 100                          # percentage points, monthly
rows = {}
for name, cols in (("headline", L), ("core", [c for c in L if not cats.food_energy[c]])):
    w = weight[cols].div(weight[cols].sum(axis=1), axis=0) if name == "core" else weight[cols]
    cc = (w * dp[cols]) * 100
    for g in ("supply", "demand", "ambiguous"):
        rows[f"{g}_{name}_mm"] = cc.where(lab[cols] == g).sum(axis=1, min_count=1)
    rows[f"total_{name}_mm"] = cc.sum(axis=1)
# supply-driven split into food & energy vs everything else (headline weights)
fe = [c for c in L if cats.food_energy[c]]
rows["supply_food_energy_mm"] = contrib[fe].where(lab[fe] == "supply").sum(axis=1)  # 0 when none labeled supply
out = pd.DataFrame(rows)
start = lab.notna().any(axis=1).idxmax()
out = out.loc[start:]
for col in list(out):
    out[col.replace("_mm", "_yoy")] = out[col].rolling(12).sum()
out.index = out.index.astype(str)
out.round(4).to_csv(ROOT + f"output/sf_replication_monthly_L{LEVEL}{AMB}.csv")
cats.to_csv(ROOT + f"output/sf_replication_categories_L{LEVEL}.csv")
# per-category monthly contribution (pp, headline weights) and label, for grouping by cause
long = pd.concat({"contrib": contrib.loc[start:], "label": lab.loc[start:]}, axis=1).stack(level=1, future_stack=True)
long.index.names = ["month", "line"]
long.reset_index().assign(month=lambda d: d.month.astype(str)).to_csv(
    ROOT + f"output/sf_replication_by_category_L{LEVEL}{AMB}.csv.gz", index=False)
print("wrote", len(out), "months from", start)
