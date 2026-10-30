"""Pent-up demand: spending of the money households could not spend during the lockdowns, % of potential GDP.

Only the part of pandemic excess savings that came from spending *less* (forced saving) is counted here. The part that
came from relief payments is already inside the relief lines: the CBO multipliers in src/fiscal_by_law.py count each
relief dollar being spent over time, so counting its later spending again would double-count it.

  gap_t     = real PCE_t - trend_t                     BEA NIPA T1.1.6 line 2 (DPCERX, chained 2017 $, SAAR),
                                                       trend = log-linear fit over TREND (default 2015Q1-2019Q4)
  stock     = sum over 2020Q1..last quarter with gap<0 (through 2021Q4) of -gap_t / 4        (forced saving, real $)
  flow_t    = stock spent evenly from the first quarter real PCE is back at trend, over SPEND quarters
  effect_t  = m x flow_t / real potential GDP_t x 100                                       (CBO GDPPOT)
m (GDP per dollar spent): CBO "other spending" multiplier 0.78 (CBO 56537 Table 3, same file as the relief lines) in
the point estimate; the band also uses 1.0 (a dollar of domestic spending is a dollar of GDP before leakage/feedback).

Method follows the Federal Reserve Board note: Aladangady, Cho, Feiveson & Pinto, "Excess Savings during the COVID-19
Pandemic", FEDS Notes, 2022-10-21 ("We add the amount that the components of DPI exceed their trend with the amount
that PCE and other outlays are below their trend"); here only the PCE part, in real terms (nominal PCE above trend in
2022 is partly inflation itself, which would make the estimate circular).
Spending period: the SF Fed (Abdelrahman & Oliveira, "Excess No More? Dwindling Pandemic Savings", 2023-08-16) put
remaining excess savings near zero by 2023Q3, so the point estimate spends the stock by then; the band also spreads
it to 2024Q4 (slower).
"""
import functools
import numpy as np
import pandas as pd
import unified_data as U

TREND = ("2015-01-01", "2019-10-01")
M_POINT, M_ALT = 0.78, 1.0


@functools.lru_cache(None)
def pieces(trend=TREND):
    c = U.nipa({"DPCERX"}).DPCERX / 1000                                   # $ billions, chained 2017, SAAR
    pre = c[trend[0]:trend[1]]
    t = np.arange(len(c)); t0 = c.index.get_loc(pre.index[0])
    fit = np.polyfit(t[t0:t0 + len(pre)], np.log(pre.values), 1)
    tr = pd.Series(np.exp(np.polyval(fit, t)), index=c.index)
    gap = c - tr
    win = gap["2020-01-01":"2021-10-01"]
    short = win[win < 0]
    stock = float(-(short / 4).sum())
    back = win[(win.index > short.index[0]) & (win >= 0)]
    start = back.index[0] if len(back) else pd.Timestamp("2022-01-01")
    return c, tr, gap, stock, start


@functools.lru_cache(None)
def _pot():
    return U.qmean(U.fred("GDPPOT"))


def effect(index, spend_end="2023-07-01", m=M_POINT, trend=TREND):
    """Pent-up demand effect on the level of GDP, % of potential GDP, on `index` (quarterly timestamps)."""
    c, tr, gap, stock, start = pieces(trend)
    q = pd.date_range(start, spend_end, freq="QS")
    flow = pd.Series(0.0, index=index)
    flow[flow.index.isin(q)] = stock / len(q) * 4                           # $bn at an annual rate
    pot = _pot().reindex(index)
    return (100 * m * flow / pot).fillna(0.0)


if __name__ == "__main__":
    c, tr, gap, stock, start = pieces()
    print(f"forced-saving stock (real PCE below 2015-19 trend, 2020-21): ${stock:,.0f} bn chained 2017; spending starts {start.date()}")
    print((100 * gap / tr)["2019-10-01":"2024-10-01"].round(2).to_string())
    print(effect(pd.date_range("2020-01-01", "2024-10-01", freq="QS")).round(2).to_string())
