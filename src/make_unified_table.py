"""output/TABLE_UNIFIED.md: every quarter, every cause, with the equations and data sources behind each line.
Numbers come from output/unified_causes_quarterly.csv (written by src/unified_model.py)."""
import pandas as pd

ROOT = __file__.rsplit("/src/", 1)[0] + "/"
o = pd.read_csv(ROOT + "output/unified_causes_quarterly.csv", index_col=0)
o["pre_existing"] = o.baseline + o.fed_pre2020

COLS = [  # key, short header
    ("trump", "Trump relief"), ("biden", "Biden relief"), ("fed_easing", "Fed cuts + QE"), ("fed_hikes", "Fed hikes"),
    ("energy_war", "War in Ukraine"), ("shortage", "Supply chains"), ("worker_shortage", "Worker shortage"),
    ("greed", "Greedflation"), ("pentup", "Pent-up demand"), ("covid_other", "COVID shutdown drag (estimated)"), ("pre_existing", "Pre-existing"),
    ("other_unexplained", "Other & not explained"),
]
MEMO = [
    ("memo_student_loans", "Student-loan pause (in Trump + Biden)"),
    ("memo_rental_assist", "Rental & homeowner aid (in Trump + Biden)"),
    ("memo_energy_covid", "2020-21 oil & food crash/rebound (in COVID)"),
    ("energy_after", "Energy & food after 2023Q1 (in other & not explained)"),
    ("memo_labor_miss", "Unemployment the causes miss (in other & not explained)"),
    ("memo_greed_unpurged", "Greed, every margin change counted"),
    ("acct_profit_share_pct", "Corporate profit share of price, %"),
    ("acct_margin_effect_on_corp_prices_yoy", "Margin effect on corporate prices"),
    ("acct_corp_price_yoy", "Corporate price growth"),
]


def table(cols, fmt):
    h = "| Quarter | " + " | ".join(c[1] for c in cols) + " |"
    rows = [h, "|" + "---|" * (len(cols) + 1)]
    for q in o.index:
        rows.append(f"| {q} | " + " | ".join(fmt(q, k) for k, _ in cols) + " |")
    return "\n".join(rows)


pt = lambda q, k: f"{o.loc[q, k]:.2f}"
rng = lambda q, k: (f"{o.loc[q, k + '_lo']:.2f} to {o.loc[q, k + '_hi']:.2f}" if k + "_lo" in o else "")
check = (o[[k for k, _ in COLS]].sum(axis=1) - o.actual_pce_yoy).abs().max()

t1 = table(COLS + [("sum_all_lines", "**Sum of all lines**"), ("actual_pce_yoy", "**Actual PCE inflation**")], pt)
bcols = [c if c[0] != "pre_existing" else ("baseline", "Pre-existing*") for c in COLS]
t2 = table(bcols + [("model_total", "Model estimate (sum of causes)")], rng)
t3 = table(MEMO, pt)

doc = f"""# Causes of US PCE inflation, every quarter 2020-2024: numbers, equations, sources

- **Chart:** `output/fig12_unified_causes.png`. **Machine-readable:** `output/unified_causes_quarterly.csv`.
- **Code:** `src/unified_model.py` (this table: `src/make_unified_table.py`). Long-form method: `output/METHOD_UNIFIED.md`.
- **Units:** percentage points of year-over-year PCE inflation. Each number is the cause's contribution, averaged over
  the four quarters ending in that quarter.

## What these numbers can't support (read first)

- **One model's answer, not a measurement.** Every cause line is what the model says inflation would have been
  without that cause. A different model would give different numbers.
- **The causes don't add up to actual inflation by themselves.** They add up to the model's estimate, which misses
  actual inflation by up to {o.other_unexplained.abs().max():.1f} points. The gap is its own line, "other & not
  explained", so all lines together equal actual inflation only because that line is defined as the gap.
- **The COVID line is estimated from the lockdown index, on the same 2020-22 data.** It is fitted to the unemployment
  that relief, the Fed and pent-up demand don't explain, so a bigger relief estimate gives a deeper COVID drag (see
  output/robustness_unified.csv). What the fit misses is not assigned to any cause; it goes into "other & not
  explained" (Table 3, "unemployment the causes miss"). The tracker ends in 2022; after it, the index is faded to 0
  by 2023Q2, when the federal Public Health Emergency ended.
- **Pent-up demand rests on two assumptions:** how fast the forced savings were spent (by 2023Q3, following the SF
  Fed's estimate that excess savings were about used up then; the range also uses 2024Q4) and GDP per dollar spent
  (CBO's 0.78; the range also uses 1.0).
- **The Fed lines are the least certain.** Their 90% ranges (Table 2) are wide. With the cleaner but weak
  instrument (MPS_ORTH, F = 3.6), the Fed lines are several times larger (output/robustness_unified.csv).
- **Energy & food are assigned to causes by date, not estimated.**
  - 2020Q1-2021Q4 goes to COVID; that includes the 2020 OPEC+ cuts made in response to the COVID collapse.
  - 2022Q1-2023Q1 goes to the war. The October 2022 OPEC+ cut and the late-2022 bird-flu egg spike fall inside that
    window and can't be separated with this model's data, so the war line still contains them.
  - After 2023Q1 (OPEC+ 2023 cuts, bird flu, drought and the rest) goes to "other & not explained".
- **Supply chains and demand overlap.** The supply-chain index is built to remove demand effects, but its
  authors' method can't remove all of them; some of the supply-chain line may belong to the relief and Fed lines.

## Table 1. Contribution of each cause, every quarter (points)

The causes add up to the model's estimate. "Other & not explained" is the gap between that and actual inflation, so all lines together equal actual inflation (largest rounding difference: {check:.3f} points).

{t1}

## Table 2. 90% ranges (5th to 95th percentile of 1,000 redraws)

\\* Pre-existing range excludes the pre-2020 Fed surprises piece (at most 0.04 points).

{t2}

## Table 3. Memo items (points; NOT added again, already inside the lines named)

- **Student-loan pause, rental aid:** parts of the Trump and Biden relief lines, computed separately.
- **Energy & food pieces:** the 2020-21 piece inside the COVID line, and the after-2023Q1 piece inside "other & not explained".
- **Greed, every margin change counted:** the model re-estimated with the raw margin series instead of
  the version with shortages, labor market and costs removed. It's an upper bound for the greedflation line; use
  it *instead of* the greedflation column, not in addition.
- **Last three columns are accounting, not the model, and are in corporate-price points, not PCE points.**
  Nonfinancial corporate price per unit = unit costs / (1 - profit share). The margin effect is how much the price
  rose from the change in the profit share alone, holding costs fixed. Corporate prices are not PCE: PCE also covers
  housing, health care and imports.

{t3}

## Equations, line by line

Notation: t = quarter; u = unemployment rate; V/U = job openings per unemployed person. Every constant below is
either estimated in this project's code on the data listed (estimate and standard error shown) or copied from the
cited source.

**Every cause line.** Contribution_t = pi_t(all causes) - pi_t(that cause removed), where pi is the Bernanke-Blanchard
price equation simulated forward from 2020Q1. Because the model is linear, the cause lines add up exactly to model
inflation (not to actual inflation). "Other & not explained" = actual - model, plus productivity and post-2023Q1 energy &
food shocks.

**Units.** The model works in log changes. Official inflation is the percent change from a year earlier (6.88% at the
2022Q2 peak, against a log change of 6.65). Every line is multiplied by the same ratio in each quarter, percent change /
log change of the PCE price index (at most 1.035), so each cause's share is unchanged.

**1. Relief paid under Trump / by Biden.**
- GDP effect_t (% of potential GDP) = 100 / PotGDP_t x sum over programs p of m_p x sum over h of w_h x X_p,t-h
  - X_p,t: payments by program and quarter, BEA program table (23 programs).
  - m_p: GDP per dollar, CBO Table 3: 0.36 PPP, 0.67 unemployment, 0.60 rebates, 0.88 state & local,
    0.78 other spending, 0.37 revenue.
  - w_h = (1 - lambda) x lambda^h with lambda = 0.74, fitted to CBO Table 2's timing.
  - Signer: payments before March 2021 count as Trump's; from March 2021, Biden's.
- Unemployment effect = beta x GDP effect, with Okun beta = -0.815 (s.e. 0.037). Estimated from
  u - u* = c + beta x output gap, 1990Q1-2019Q4.
- V/U: log(V/U) = a + b x u, b = -0.290 (est. 1990Q1-2019Q4). The cause's share of the V/U change uses
  logarithmic-mean weights, so the shares add up exactly.
- V/U drives wages, and wages drive prices (equations 7 and 8).

**2. Fed 2020-21 cuts + QE; Fed 2022-23 hikes.**
- Monthly 7-variable VAR, 12 lags, 1977-06 to 2019-12. Fed shock identified with the Bauer-Swanson monetary-policy
  surprise MPS as instrument (first-stage F = 9.5; heteroskedasticity-robust 8.2). The orthogonalized MPS_ORTH gives
  F = 3.6 (weak) and is a robustness variant.
- Counterfactual: policy shocks inside a window chosen so the proxy funds rate (which includes QE) stays:
  - at or above its 2019Q4 average, 2.35%, during 2020-01 to 2022-02 (cuts + QE);
  - at or below 2.35%, from 2022-03 to the funds-rate peak (hikes).
  - Shocks are chosen by ridge least squares, ridge 0.05.
- Line = minus the counterfactual's unemployment effect, then through V/U as in item 1.

**3. War in Ukraine.**
- PCE energy and food-at-home prices relative to the employment cost index enter the price equation (current + 4 lags).
- Line = inflation minus inflation with those relative price changes set to 0 during 2022Q1-2023Q1 (the spike and its
  fall-back). The effect lingers after 2023Q1 through wages and expectations.
- Energy & food changes after 2023Q1 are computed the same way and go into "other & not explained".

**4. COVID supply chains.**
- NY Fed GSCPI (current + 4 lags) in the price equation. Removed = held at its 1998-2019 mean.

**5. Worker shortage.**
- The part of log(V/U) that unemployment doesn't explain, measured as its change since 2019Q4. In 2022
  actual V/U was 1.9 against 1.0 predicted from unemployment.

**6. Greedflation.**
- margin_t = -400 x dlog(1 - s_t), with s = unit profits / price, nonfinancial corporations.
- Regress margin_t on supply chains, V/U, energy, food and wage growth (current + 4 lags each),
  1990Q1-2024Q4, R^2 = 0.51. The residual ("greed", current + 4 lags) enters the price equation.
  - Coefficient sum -0.011 (s.e. 0.036).
  - With raw margins, 0.031 (s.e. 0.035), which gives the Table 3 upper bound.

**7. Pent-up demand.**
- Real PCE (BEA DPCERX) against its log-linear 2015-2019 trend. Forced saving = real spending below trend, 2020-21,
  summed: $786 billion (2017 dollars).
- Spent evenly from the first quarter spending was back at trend (2021Q2) through 2023Q3. GDP effect = 0.78 (CBO
  "other spending" multiplier) x spending / potential GDP; then Okun and V/U as in item 1.
- Relief money is excluded: it is already counted, and spent over time, in the relief lines.

**8. COVID shutdown drag (estimated).**
- y_t = g0 s_t + g1 s_t-1 + e_t, OLS 2020Q1-2022Q4, no constant. s = Oxford stringency index / 100;
  y = unemployment change since 2019Q4 not explained by relief, the Fed and pent-up demand.
- The line is g0 s_t + g1 s_t-1 through V/U as in item 1, plus the energy & food price changes of 2020Q1-2021Q4.
  e_t is not a cause; its effect on inflation is inside "other & not explained".

**9. Pre-existing.**
- Model inflation with every cause removed: the 2019Q4 starting point and its built-in momentum, plus the
  pre-2020 Fed surprises.

**Wage and price equations (Bernanke-Blanchard, re-estimated on PCE).**
- Wage growth_t = const + sum of 4 lags of wage growth + 4 lags of V/U + 4 lags of 1-year inflation
  expectations + 4 lags of catch-up + productivity.
- Price inflation_t = const + 4 lags of price inflation + wage growth (current + 4 lags) + energy, food,
  supply chains and greed (current + 4 lags each) + productivity.
  - Restriction: own lags + wage-growth terms sum to 1.
- Two expectations equations as in the original. Structure and restrictions copied from Lorenzoni's replication
  code; coefficients re-estimated here.

**Ranges.** Each of the 1,000 redraws varies:
- the wage-price coefficients;
- Okun beta;
- the V/U coefficients;
- one bootstrap replication of the Fed VAR;
- fiscal timing (CBO-fitted or Hutchins) x coverage (1 or 2.04);
- the ridge (0.05 or 0.5);
- the COVID coefficients (from their estimated covariance);
- pent-up demand: multiplier (0.78 or 1.0) x spending period (to 2023Q3 or 2024Q4).

## Data sources

| Series | Used for | Source | File |
|---|---|---|---|
| PCE price index; PCE energy; PCE food at home | inflation, energy & food shocks | BEA NIPA Table 2.3.4 (DPCERG, DNRGRG, DFXARG), [NipaDataQ.txt](https://apps.bea.gov/national/Release/TXT/NipaDataQ.txt) | `data/raw/bea/NipaDataQ.txt` |
| Unit profits, price per unit, nonfinancial corporations | greedflation, Table 3 accounting | BEA NIPA Table 1.15 (A463RD, A455RD), same file | same |
| Pandemic relief payments by program | Trump & Biden lines, memos | BEA, Effects of Selected Federal Pandemic Response Programs (2020Q4, 2021Q4, 2022Q4 third releases; personal-income table Apr 2021), [BEA COVID-19 and Recovery archive](https://www.bea.gov/federal-recovery-programs-and-bea-statistics/covid-19-recovery) | `data/raw/bea_pandemic/` |
| GDP per dollar of relief; timing | Trump & Biden lines | CBO, *The Effects of Pandemic-Related Legislation on Output*, Sept 2020, Tables 2-3, [CBO 56537](https://www.cbo.gov/publication/56537) (PDF via [Internet Archive](http://web.archive.org/web/20201017045106id_/https://www.cbo.gov/system/files/2020-09/56537-pandemic-legislation.pdf)) | `data/raw/cbo/` |
| Alternative timing weights | ranges | Hutchins Center Fiscal Impact Measure, `R/mpc.R`, [GitHub](https://github.com/Hutchins-Center/Fiscal-Impact-Measure) | `data/raw/hutchins/` |
| Student-loan pause end date | loan-pause memo | Education Department notice as quoted by [WJLA](https://wjla.com/news/nation-world/student-loan-payments-set-to-resume-in-october-after-three-year-pause-department-of-education-student-aid-due-date-interest-accrual-loan-forgiveness) | (quoted in METHOD_UNIFIED.md) |
| Unemployment, natural rate, real GDP, potential GDP, GDP deflator, PCE price index | Okun, V/U link, scaling, actual inflation | FRED: UNRATE, NROU, GDPC1, GDPPOT, GDPDEF, PCEPI (fred.stlouisfed.org/graph/fredgraph.csv?id=SERIES) | `data/raw/fred2/` |
| Proxy funds rate (includes QE) | Fed lines | SF Fed, [Proxy Funds Rate](https://www.frbsf.org/research-and-insights/data-and-indicators/proxy-funds-rate/) | `data/raw/shadow/` |
| Monetary policy surprises; VAR data | Fed lines | SF Fed, [Monetary Policy Surprises](https://www.frbsf.org/research-and-insights/data-and-indicators/monetary-policy-surprises/) (Bauer & Swanson) | `data/raw/mps/` |
| Global Supply Chain Pressure Index | supply chains | NY Fed GSCPI (method: NY Fed Staff Report 1017, saved alongside) | `data/raw/nyfed/` |
| Real PCE | pent-up demand | BEA NIPA Table 1.1.6 (DPCERX), same file as above | `data/raw/bea/NipaDataQ.txt` |
| Excess-savings method | pent-up demand | Aladangady, Cho, Feiveson & Pinto, [Excess Savings during the COVID-19 Pandemic](https://www.federalreserve.gov/econres/notes/feds-notes/excess-savings-during-the-covid-19-pandemic-20221021.html), FEDS Notes, Oct 21 2022 | (method only) |
| When excess savings ran out | pent-up demand timing | Abdelrahman & Oliveira, [Excess No More? Dwindling Pandemic Savings](https://www.frbsf.org/research-and-insights/blog/sf-fed-blog/2023/08/16/excess-no-more-dwindling-pandemic-savings/), SF Fed blog, Aug 16 2023 | (timing only) |
| Lockdown stringency | COVID line | Oxford COVID-19 Government Response Tracker, US national StringencyIndex_Average, [OxCGRT](https://github.com/OxCGRT/covid-policy-dataset) | `data/raw/oxcgrt/` |
| End of the Public Health Emergency | fading the index after 2022 | [HHS](https://www.hhs.gov/coronavirus/covid-19-public-health-emergency/index.html): expired May 11, 2023 | (date only) |
| Wages (ECI), V/U, expectations, productivity | wage-price model | Bernanke-Blanchard data as updated by Lorenzoni, [GitHub](https://github.com/luigilor/bernanke-blanchard23) (commit 7712ad9) | `data/raw/data_us_new.csv` |
"""
open(ROOT + "output/TABLE_UNIFIED.md", "w").write(doc)
print("saved; max |sum - actual| =", round(check, 4))
