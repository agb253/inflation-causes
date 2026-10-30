# Causes of US PCE inflation, every quarter 2020-2024: numbers, equations, sources

- **Chart:** `output/fig12_unified_causes.png`. **Machine-readable:** `output/unified_causes_quarterly.csv`.
- **Code:** `src/unified_model.py` (this table: `src/make_unified_table.py`). Long-form method: `output/METHOD_UNIFIED.md`.
- **Units:** percentage points of year-over-year PCE inflation. Each number is the cause's contribution, averaged over
  the four quarters ending in that quarter.

## What these numbers can't support (read first)

- **One model's answer, not a measurement.** Every cause line is what the model says inflation would have been
  without that cause. A different model would give different numbers.
- **The causes don't add up to actual inflation by themselves.** They add up to the model's estimate, which misses
  actual inflation by up to 1.2 points. The gap is its own line, "other & not
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

The causes add up to the model's estimate. "Other & not explained" is the gap between that and actual inflation, so all lines together equal actual inflation (largest rounding difference: 0.002 points).

| Quarter | Trump relief | Biden relief | Fed cuts + QE | Fed hikes | War in Ukraine | Supply chains | Worker shortage | Greedflation | Pent-up demand | COVID shutdown drag (estimated) | Pre-existing | Other & not explained | **Sum of all lines** | **Actual PCE inflation** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2020Q1 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.01 | 0.00 | -0.01 | 0.00 | -0.24 | 1.64 | 0.15 | 1.55 | 1.55 |
| 2020Q2 | 0.00 | 0.00 | -0.00 | 0.00 | 0.00 | 0.21 | -0.01 | 0.05 | 0.00 | -1.29 | 1.40 | 0.23 | 0.57 | 0.57 |
| 2020Q3 | 0.10 | 0.00 | -0.00 | 0.00 | 0.00 | 0.53 | 0.15 | 0.06 | 0.00 | -1.75 | 1.57 | 0.46 | 1.12 | 1.12 |
| 2020Q4 | 0.30 | 0.00 | -0.00 | 0.00 | 0.00 | 0.72 | 0.36 | -0.00 | 0.00 | -2.15 | 1.59 | 0.42 | 1.24 | 1.24 |
| 2021Q1 | 0.50 | 0.00 | -0.00 | 0.00 | 0.00 | 0.88 | 0.43 | -0.00 | 0.00 | -1.86 | 1.56 | 0.47 | 1.98 | 1.98 |
| 2021Q2 | 0.66 | 0.07 | 0.01 | 0.00 | 0.00 | 1.00 | 0.41 | -0.04 | 0.00 | -0.72 | 1.69 | 0.85 | 3.92 | 3.92 |
| 2021Q3 | 0.69 | 0.27 | 0.02 | 0.00 | 0.00 | 1.06 | 0.37 | -0.08 | 0.07 | -0.62 | 1.73 | 1.01 | 4.52 | 4.52 |
| 2021Q4 | 0.64 | 0.54 | 0.05 | 0.00 | 0.00 | 1.33 | 0.50 | -0.01 | 0.20 | -0.22 | 1.79 | 0.94 | 5.73 | 5.73 |
| 2022Q1 | 0.53 | 0.74 | 0.09 | 0.00 | 0.49 | 1.75 | 0.61 | 0.02 | 0.31 | -0.82 | 1.86 | 0.97 | 6.56 | 6.56 |
| 2022Q2 | 0.47 | 0.79 | 0.14 | 0.00 | 1.13 | 1.89 | 0.81 | 0.00 | 0.39 | -1.56 | 1.93 | 0.88 | 6.88 | 6.88 |
| 2022Q3 | 0.47 | 0.74 | 0.19 | 0.01 | 0.95 | 1.98 | 0.94 | 0.03 | 0.40 | -1.61 | 1.98 | 0.67 | 6.75 | 6.75 |
| 2022Q4 | 0.41 | 0.65 | 0.21 | 0.02 | 0.83 | 1.83 | 0.81 | -0.01 | 0.40 | -1.88 | 2.04 | 0.75 | 6.07 | 6.07 |
| 2023Q1 | 0.39 | 0.58 | 0.22 | 0.02 | 0.18 | 1.55 | 0.80 | 0.01 | 0.39 | -1.86 | 2.09 | 0.72 | 5.08 | 5.08 |
| 2023Q2 | 0.39 | 0.58 | 0.22 | -0.01 | -0.37 | 1.23 | 0.81 | -0.02 | 0.42 | -1.67 | 2.12 | 0.27 | 3.99 | 3.99 |
| 2023Q3 | 0.35 | 0.54 | 0.24 | -0.06 | -0.03 | 0.79 | 0.74 | -0.03 | 0.46 | -1.31 | 2.17 | -0.42 | 3.43 | 3.43 |
| 2023Q4 | 0.34 | 0.48 | 0.28 | -0.12 | 0.23 | 0.56 | 0.68 | -0.01 | 0.44 | -1.09 | 2.19 | -1.02 | 2.95 | 2.95 |
| 2024Q1 | 0.33 | 0.44 | 0.31 | -0.17 | 0.50 | 0.39 | 0.65 | -0.07 | 0.38 | -0.96 | 2.20 | -1.16 | 2.84 | 2.84 |
| 2024Q2 | 0.30 | 0.43 | 0.32 | -0.22 | 0.53 | 0.36 | 0.63 | -0.02 | 0.28 | -0.89 | 2.20 | -1.24 | 2.70 | 2.70 |
| 2024Q3 | 0.29 | 0.42 | 0.32 | -0.25 | 0.47 | 0.41 | 0.58 | 0.00 | 0.20 | -1.01 | 2.20 | -1.19 | 2.43 | 2.43 |
| 2024Q4 | 0.28 | 0.39 | 0.30 | -0.29 | 0.42 | 0.48 | 0.54 | -0.00 | 0.17 | -1.15 | 2.21 | -0.83 | 2.52 | 2.52 |

## Table 2. 90% ranges (5th to 95th percentile of 1,000 redraws)

\* Pre-existing range excludes the pre-2020 Fed surprises piece (at most 0.04 points).

| Quarter | Trump relief | Biden relief | Fed cuts + QE | Fed hikes | War in Ukraine | Supply chains | Worker shortage | Greedflation | Pent-up demand | COVID shutdown drag (estimated) | Pre-existing* | Other & not explained | Model estimate (sum of causes) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2020Q1 | 0.00 to 0.00 | 0.00 to 0.00 | 0.00 to 0.00 | 0.00 to 0.00 | 0.00 to 0.00 | -0.06 to 0.08 | 0.00 to 0.00 | -0.05 to 0.02 | 0.00 to 0.00 | -0.25 to -0.22 | 1.55 to 1.72 | 0.06 to 0.25 | 1.30 to 1.49 |
| 2020Q2 | 0.00 to 0.00 | 0.00 to 0.00 | -0.00 to 0.00 | 0.00 to 0.00 | 0.00 to 0.00 | 0.02 to 0.40 | -0.02 to -0.00 | 0.00 to 0.10 | 0.00 to 0.00 | -1.54 to -1.08 | 1.26 to 1.53 | -0.06 to 0.53 | 0.04 to 0.62 |
| 2020Q3 | 0.01 to 0.31 | 0.00 to 0.00 | -0.01 to 0.01 | 0.00 to 0.00 | 0.00 to 0.00 | 0.26 to 0.82 | 0.01 to 0.33 | 0.01 to 0.11 | 0.00 to 0.00 | -2.46 to -1.23 | 1.37 to 1.77 | -0.01 to 0.99 | 0.12 to 1.12 |
| 2020Q4 | 0.11 to 0.83 | 0.00 to 0.00 | -0.02 to 0.02 | 0.00 to 0.00 | 0.00 to 0.00 | 0.35 to 1.08 | 0.12 to 0.62 | -0.06 to 0.05 | 0.00 to 0.00 | -3.31 to -1.36 | 1.30 to 1.86 | -0.18 to 1.10 | 0.11 to 1.39 |
| 2021Q1 | 0.21 to 1.38 | 0.00 to 0.00 | -0.04 to 0.04 | 0.00 to 0.00 | 0.00 to 0.00 | 0.46 to 1.31 | 0.17 to 0.74 | -0.06 to 0.05 | 0.00 to 0.00 | -3.58 to -0.84 | 1.22 to 1.88 | -0.25 to 1.27 | 0.63 to 2.18 |
| 2021Q2 | 0.29 to 1.86 | 0.01 to 0.22 | -0.05 to 0.10 | 0.00 to 0.00 | 0.00 to 0.00 | 0.54 to 1.48 | 0.12 to 0.71 | -0.10 to 0.02 | 0.00 to 0.00 | -2.80 to 0.41 | 1.28 to 2.08 | 0.11 to 1.76 | 2.15 to 3.77 |
| 2021Q3 | 0.29 to 1.99 | 0.09 to 0.76 | -0.07 to 0.19 | 0.00 to 0.00 | 0.00 to 0.00 | 0.51 to 1.66 | 0.07 to 0.69 | -0.13 to -0.02 | 0.01 to 0.15 | -3.07 to 0.53 | 1.26 to 2.19 | 0.16 to 1.98 | 2.52 to 4.31 |
| 2021Q4 | 0.23 to 1.93 | 0.20 to 1.43 | -0.09 to 0.31 | 0.00 to 0.00 | 0.00 to 0.00 | 0.61 to 2.11 | 0.19 to 0.85 | -0.07 to 0.03 | 0.06 to 0.34 | -2.79 to 1.01 | 1.24 to 2.32 | -0.17 to 1.95 | 3.74 to 5.86 |
| 2022Q1 | 0.16 to 1.75 | 0.30 to 2.02 | -0.10 to 0.47 | 0.00 to 0.00 | 0.43 to 0.56 | 0.93 to 2.63 | 0.26 to 0.96 | -0.03 to 0.06 | 0.10 to 0.54 | -3.47 to 0.48 | 1.23 to 2.50 | -0.19 to 1.92 | 4.59 to 6.72 |
| 2022Q2 | 0.13 to 1.59 | 0.29 to 2.17 | -0.10 to 0.65 | -0.00 to 0.01 | 0.98 to 1.28 | 0.96 to 2.89 | 0.36 to 1.28 | -0.03 to 0.04 | 0.13 to 0.67 | -4.35 to -0.27 | 1.20 to 2.64 | -0.34 to 1.84 | 4.95 to 7.20 |
| 2022Q3 | 0.18 to 1.59 | 0.26 to 2.13 | -0.11 to 0.83 | -0.01 to 0.03 | 0.72 to 1.19 | 0.98 to 3.05 | 0.45 to 1.44 | 0.00 to 0.05 | 0.12 to 0.70 | -4.48 to -0.27 | 1.18 to 2.81 | -0.66 to 1.81 | 4.92 to 7.49 |
| 2022Q4 | 0.12 to 1.45 | 0.18 to 1.92 | -0.12 to 0.95 | -0.05 to 0.07 | 0.50 to 1.16 | 0.75 to 3.01 | 0.33 to 1.34 | -0.02 to 0.02 | 0.12 to 0.72 | -4.68 to -0.56 | 1.14 to 2.96 | -0.66 to 1.99 | 4.14 to 6.83 |
| 2023Q1 | 0.09 to 1.39 | 0.17 to 1.79 | -0.13 to 1.01 | -0.13 to 0.14 | -0.20 to 0.56 | 0.41 to 2.82 | 0.30 to 1.34 | -0.02 to 0.03 | 0.11 to 0.69 | -4.46 to -0.59 | 1.09 to 3.10 | -0.89 to 1.99 | 3.13 to 6.06 |
| 2023Q2 | 0.10 to 1.40 | 0.20 to 1.72 | -0.11 to 1.04 | -0.27 to 0.18 | -0.80 to 0.05 | 0.04 to 2.58 | 0.32 to 1.36 | -0.05 to 0.02 | 0.13 to 0.72 | -4.17 to -0.42 | 1.03 to 3.24 | -1.53 to 1.63 | 2.07 to 5.22 |
| 2023Q3 | 0.04 to 1.32 | 0.18 to 1.64 | -0.08 to 1.09 | -0.48 to 0.20 | -0.47 to 0.42 | -0.41 to 2.19 | 0.26 to 1.27 | -0.07 to 0.01 | 0.16 to 0.77 | -3.81 to -0.02 | 1.04 to 3.33 | -2.35 to 0.99 | 2.27 to 5.56 |
| 2023Q4 | 0.03 to 1.29 | 0.13 to 1.57 | -0.06 to 1.09 | -0.68 to 0.20 | -0.22 to 0.69 | -0.62 to 1.96 | 0.18 to 1.19 | -0.09 to 0.06 | 0.15 to 0.76 | -3.52 to 0.32 | 1.03 to 3.38 | -2.99 to 0.37 | 2.20 to 5.57 |
| 2024Q1 | 0.00 to 1.25 | 0.10 to 1.49 | -0.03 to 1.06 | -0.89 to 0.20 | 0.08 to 0.92 | -0.69 to 1.75 | 0.15 to 1.17 | -0.15 to 0.00 | 0.13 to 0.70 | -3.36 to 0.56 | 1.02 to 3.39 | -3.14 to 0.26 | 2.07 to 5.52 |
| 2024Q2 | -0.03 to 1.18 | 0.08 to 1.46 | -0.01 to 1.06 | -1.03 to 0.21 | 0.15 to 0.92 | -0.62 to 1.66 | 0.13 to 1.16 | -0.10 to 0.05 | 0.07 to 0.65 | -3.22 to 0.67 | 1.02 to 3.38 | -3.31 to 0.15 | 2.25 to 5.60 |
| 2024Q3 | -0.03 to 1.11 | 0.05 to 1.46 | -0.01 to 1.03 | -1.20 to 0.22 | 0.13 to 0.82 | -0.44 to 1.59 | 0.06 to 1.13 | -0.08 to 0.08 | -0.04 to 0.61 | -3.31 to 0.56 | 1.03 to 3.38 | -3.18 to 0.18 | 1.51 to 4.78 |
| 2024Q4 | -0.03 to 1.07 | 0.04 to 1.41 | -0.02 to 1.00 | -1.30 to 0.22 | 0.12 to 0.75 | -0.26 to 1.61 | 0.01 to 1.07 | -0.08 to 0.07 | -0.07 to 0.62 | -3.25 to 0.32 | 1.05 to 3.37 | -2.86 to 0.49 | 1.23 to 4.50 |

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

| Quarter | Student-loan pause (in Trump + Biden) | Rental & homeowner aid (in Trump + Biden) | 2020-21 oil & food crash/rebound (in COVID) | Energy & food after 2023Q1 (in other & not explained) | Unemployment the causes miss (in other & not explained) | Greed, every margin change counted | Corporate profit share of price, % | Margin effect on corporate prices | Corporate price growth |
|---|---|---|---|---|---|---|---|---|---|
| 2020Q1 | 0.00 | 0.00 | -0.24 | 0.00 | 0.00 | -0.03 | 12.01 | -0.61 | 2.02 |
| 2020Q2 | 0.00 | 0.00 | -1.09 | 0.00 | 0.19 | 0.01 | 12.78 | 0.16 | 0.39 |
| 2020Q3 | 0.00 | 0.00 | -0.99 | 0.00 | 0.24 | 0.09 | 17.46 | 5.08 | 1.24 |
| 2020Q4 | 0.01 | 0.00 | -0.83 | 0.00 | 0.11 | -0.06 | 14.68 | 1.49 | 1.71 |
| 2021Q1 | 0.01 | 0.00 | -0.14 | 0.00 | 0.11 | -0.01 | 16.65 | 5.42 | 2.45 |
| 2021Q2 | 0.01 | 0.01 | 1.21 | 0.00 | 0.14 | 0.08 | 18.39 | 6.65 | 4.87 |
| 2021Q3 | 0.02 | 0.03 | 1.31 | 0.00 | 0.11 | -0.01 | 17.61 | 0.19 | 4.91 |
| 2021Q4 | 0.03 | 0.04 | 1.71 | 0.00 | -0.15 | 0.15 | 17.21 | 3.02 | 5.85 |
| 2022Q1 | 0.03 | 0.04 | 1.27 | 0.00 | -0.07 | 0.23 | 16.49 | -0.19 | 6.92 |
| 2022Q2 | 0.04 | 0.03 | 0.85 | 0.00 | 0.07 | 0.20 | 17.39 | -1.22 | 7.57 |
| 2022Q3 | 0.04 | 0.02 | 0.69 | 0.00 | -0.07 | 0.21 | 17.41 | -0.25 | 7.15 |
| 2022Q4 | 0.04 | 0.01 | 0.15 | 0.00 | 0.09 | 0.23 | 17.36 | 0.18 | 6.11 |
| 2023Q1 | 0.04 | 0.02 | 0.16 | 0.00 | 0.13 | 0.14 | 17.51 | 1.22 | 5.00 |
| 2023Q2 | 0.04 | 0.02 | 0.13 | -0.34 | -0.20 | 0.09 | 17.64 | 0.30 | 3.34 |
| 2023Q3 | 0.04 | 0.01 | 0.12 | -0.23 | -0.45 | 0.11 | 17.97 | 0.68 | 3.39 |
| 2023Q4 | 0.05 | 0.01 | 0.13 | -0.39 | -0.54 | 0.12 | 18.51 | 1.40 | 3.20 |
| 2024Q1 | 0.04 | 0.02 | 0.12 | -0.55 | -0.56 | 0.08 | 17.35 | -0.19 | 2.77 |
| 2024Q2 | 0.04 | 0.01 | 0.11 | -0.34 | -0.49 | 0.09 | 17.69 | 0.06 | 2.91 |
| 2024Q3 | 0.04 | 0.01 | 0.11 | -0.80 | -0.21 | 0.10 | 17.65 | -0.39 | 2.25 |
| 2024Q4 | 0.03 | 0.01 | 0.11 | -0.84 | 0.02 | 0.08 | 17.64 | -1.06 | 2.16 |

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

**1. Relief signed by Trump / by Biden.**
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
