# Every cause, every quarter: values, data and equations

Units: percentage points of year-over-year PCE inflation (each quarter = the four quarters ending then; equation E2).
Rows are causes; the last columns give the 2021-24 total (the four Q4-over-Q4 rates added up), its 68% and 90% ranges
from 1,000 redraws, the data series used and the equations (numbered below). Every line except the groups adds up, with
pre-existing and "other & not explained", to actual inflation in every quarter.

- **Same numbers, one row per cause and quarter, with 68% and 90% ranges for each quarter:** `output/reproduce_long.csv`.
- **Rebuild:** `bash run_report.sh` (all numbers); this table alone: `python src/make_reproduce_table.py`.
- **Data files, links, download dates:** `output/TABLE_UNIFIED.md`, section "Data sources".

## Table R1. Contribution of each cause, by quarter

| Line | 2020Q1 | 2020Q2 | 2020Q3 | 2020Q4 | 2021Q1 | 2021Q2 | 2021Q3 | 2021Q4 | 2022Q1 | 2022Q2 | 2022Q3 | 2022Q4 | 2023Q1 | 2023Q2 | 2023Q3 | 2023Q4 | 2024Q1 | 2024Q2 | 2024Q3 | 2024Q4 | 2021-24 total | 68% range | 90% range | Data | Equations |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Actual PCE inflation | +1.55 | +0.57 | +1.12 | +1.24 | +1.98 | +3.92 | +4.52 | +5.73 | +6.56 | +6.88 | +6.75 | +6.07 | +5.08 | +3.99 | +3.43 | +2.95 | +2.84 | +2.70 | +2.43 | +2.52 | +17.3 |  |  | BEA DPCERG (NIPA 2.3.4) | 100 x (P_t / P_t-4 - 1) |
| Pre-existing (end-2019 momentum) | +1.64 | +1.40 | +1.57 | +1.59 | +1.56 | +1.69 | +1.73 | +1.79 | +1.86 | +1.93 | +1.98 | +2.04 | +2.09 | +2.12 | +2.17 | +2.19 | +2.20 | +2.20 | +2.20 | +2.21 | +8.2 | +5.8 to +10.6 | +4.5 to +11.9 | all model inputs at 2019 reference; data_us_new.csv | E14, E10-E12, E2 |
| Relief signed by Trump | 0.00 | 0.00 | +0.10 | +0.30 | +0.50 | +0.66 | +0.69 | +0.64 | +0.53 | +0.47 | +0.47 | +0.41 | +0.39 | +0.39 | +0.35 | +0.34 | +0.33 | +0.30 | +0.29 | +0.28 | +1.7 | +1.2 to +4.0 | +0.7 to +5.1 | BEA pandemic program tables; CBO 56537 T2-3; FRED GDPPOT, UNRATE, NROU, GDPC1; V/U | E3, E4, E8, E10-E12, E1, E2 |
| Relief signed by Biden | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | +0.07 | +0.27 | +0.54 | +0.74 | +0.79 | +0.74 | +0.65 | +0.58 | +0.58 | +0.54 | +0.48 | +0.44 | +0.43 | +0.42 | +0.39 | +2.1 | +1.4 to +4.4 | +1.0 to +5.6 | same as Trump relief | E3, E4, E8, E10-E12, E1, E2 |
| Fed 2020-21 cuts + QE | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | +0.01 | +0.02 | +0.05 | +0.09 | +0.14 | +0.19 | +0.21 | +0.22 | +0.22 | +0.24 | +0.28 | +0.31 | +0.32 | +0.32 | +0.30 | +0.8 | +0.2 to +1.9 | -0.2 to +3.2 | SF Fed MPS + VAR data; SF Fed proxy funds rate; UNRATE | E6, E8, E10-E12, E1, E2 |
| Fed 2022-23 hikes | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | +0.01 | +0.02 | +0.02 | -0.01 | -0.06 | -0.12 | -0.17 | -0.22 | -0.25 | -0.29 | -0.4 | -1.1 to +0.1 | -2.0 to +0.4 | same as Fed cuts | E6, E8, E10-E12, E1, E2 |
| Pent-up demand | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | +0.07 | +0.20 | +0.31 | +0.39 | +0.40 | +0.40 | +0.39 | +0.42 | +0.46 | +0.44 | +0.38 | +0.28 | +0.20 | +0.17 | +1.2 | +0.8 to +1.7 | +0.5 to +2.1 | BEA DPCERX (NIPA 1.1.6); CBO 56537 T3; GDPPOT | E5, E4, E8, E10-E12, E1, E2 |
| COVID shutdown drag | -0.24 | -1.29 | -1.75 | -2.15 | -1.86 | -0.72 | -0.62 | -0.22 | -0.82 | -1.56 | -1.61 | -1.88 | -1.86 | -1.67 | -1.31 | -1.09 | -0.96 | -0.89 | -1.01 | -1.15 | -4.3 | -9.2 to -2.1 | -12.5 to -0.3 | OxCGRT stringency; UNRATE; plus BEA DNRGRG, DFXARG 2020Q1-2021Q4 | E7, E8, E10-E12 (+E11 energy/food), E1, E2 |
| Worker shortage | 0.00 | -0.01 | +0.15 | +0.36 | +0.43 | +0.41 | +0.37 | +0.50 | +0.61 | +0.81 | +0.94 | +0.81 | +0.80 | +0.81 | +0.74 | +0.68 | +0.65 | +0.63 | +0.58 | +0.54 | +2.5 | +1.5 to +3.4 | +1.0 to +4.1 | V/U (JOLTS via data_us_new.csv); UNRATE | E9, E8, E10-E12, E1, E2 |
| War in Ukraine (energy & food) | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | +0.49 | +1.13 | +0.95 | +0.83 | +0.18 | -0.37 | -0.03 | +0.23 | +0.50 | +0.53 | +0.47 | +0.42 | +1.5 | +0.9 to +2.1 | +0.5 to +2.5 | BEA DNRGRG, DFXARG / ECI, 2022Q1-2023Q1 | E11, E1, E2 |
| Supply chains | +0.01 | +0.21 | +0.53 | +0.72 | +0.88 | +1.00 | +1.06 | +1.33 | +1.75 | +1.89 | +1.98 | +1.83 | +1.55 | +1.23 | +0.79 | +0.56 | +0.39 | +0.36 | +0.41 | +0.48 | +4.2 | +2.3 to +6.6 | +0.8 to +8.3 | NY Fed GSCPI | E11, E1, E2 |
| Greedflation | -0.01 | +0.05 | +0.06 | 0.00 | 0.00 | -0.04 | -0.08 | -0.01 | +0.02 | 0.00 | +0.03 | -0.01 | +0.01 | -0.02 | -0.03 | -0.01 | -0.07 | -0.02 | 0.00 | 0.00 | -0.0 | -0.1 to +0.1 | -0.2 to +0.1 | BEA A463RD, A455RD (NIPA 1.15) | E13, E11, E1, E2 |
| Other & not explained | +0.15 | +0.23 | +0.46 | +0.42 | +0.47 | +0.85 | +1.01 | +0.94 | +0.97 | +0.88 | +0.67 | +0.75 | +0.72 | +0.27 | -0.42 | -1.02 | -1.16 | -1.24 | -1.19 | -0.83 | -0.2 | -3.5 to +2.0 | -5.7 to +3.7 | everything above | E15 |
| Total: all labor-market causes (relief + pent-up + Fed + COVID + worker shortage) | -0.24 | -1.30 | -1.49 | -1.48 | -0.93 | +0.42 | +0.80 | +1.69 | +1.47 | +1.05 | +1.14 | +0.62 | +0.54 | +0.74 | +0.96 | +1.00 | +0.97 | +0.86 | +0.53 | +0.23 | +3.5 | +2.9 to +5.3 | +2.2 to +6.3 | sum of the lines named | sum |
| Total: pandemic and the response to it (relief + pent-up + COVID drag) | -0.24 | -1.29 | -1.65 | -1.85 | -1.36 | 0.00 | +0.41 | +1.15 | +0.77 | +0.09 | 0.00 | -0.42 | -0.51 | -0.28 | +0.03 | +0.17 | +0.19 | +0.13 | -0.11 | -0.31 | +0.6 | -0.4 to +2.3 | -1.5 to +3.0 | sum of the lines named | sum |
| Total: Biden + Trump relief | 0.00 | 0.00 | +0.10 | +0.30 | +0.50 | +0.72 | +0.95 | +1.17 | +1.28 | +1.26 | +1.21 | +1.06 | +0.97 | +0.97 | +0.89 | +0.81 | +0.77 | +0.74 | +0.71 | +0.67 | +3.7 | +2.7 to +8.5 | +1.8 to +10.8 | sum of the lines named | sum |
| Total: supply shocks (supply chains + war) | +0.01 | +0.21 | +0.53 | +0.72 | +0.88 | +1.00 | +1.06 | +1.33 | +2.25 | +3.02 | +2.93 | +2.66 | +1.73 | +0.86 | +0.76 | +0.79 | +0.89 | +0.89 | +0.88 | +0.90 | +5.7 | +3.9 to +7.8 | +2.7 to +9.3 | sum of the lines named | sum |
| Model estimate (sum of all causes + pre-existing) | +1.40 | +0.34 | +0.64 | +0.78 | +1.46 | +3.02 | +3.48 | +4.77 | +5.57 | +6.01 | +6.11 | +5.36 | +4.41 | +3.43 | +3.65 | +3.61 | +3.46 | +3.60 | +2.81 | +2.49 | +16.2 | +14.0 to +19.6 | +12.3 to +21.8 | sum of the lines named | sum |

## Equations

| # | Equation | Code |
|---|---|---|
| E1 | Contribution of cause k: c_k,t = pi_t(all inputs) - pi_t(input k removed). pi is simulated with E10-E12 from 2020Q1 on; quarters before 2020 are actual history. | `src/unified_model.py` (unified_model.causes_inflation) |
| E2 | Year-over-year number in the table: average of the last 4 quarterly (annualized) c_k, times r_t = percent change / log change of the PCE price index (DPCERG), so all lines sum to official inflation. | `src/unified_model.py` (unified_model.yoy, save) |
| E3 | Relief to GDP: G_t = 100/PotGDP_t x sum_p m_p x sum_h (1-lambda) lambda^h X_p,t-h; lambda = 0.74; m_p from CBO 56537 Table 3 (0.36 PPP, 0.67 unemployment, 0.60 rebates, 0.88 state & local, 0.78 other, 0.37 revenue). Payments before March 2021 = Trump; from March 2021 = Biden. | `src/fiscal_by_law.py` (fiscal_by_law.run_variant) |
| E4 | GDP to unemployment (Okun): du_t = beta x G_t, beta = -0.815 (s.e. 0.037), estimated 1990-2019. | `src/unified_model.py` (unified_model.okun) |
| E5 | Pent-up demand: forced saving = sum over 2020-21 of (2015-19 log-linear trend - actual) real PCE = $786 billion (2017 $); spent evenly 2021Q2-2023Q3; G_t = 0.78 x spending_t / PotGDP_t; then E4. | `src/pentup.py` (pentup.effect) |
| E6 | Fed to unemployment: monthly proxy SVAR (12 lags, 1977-2019), instrument MPS (F = 9.5); counterfactual policy shocks hold the proxy funds rate at its 2019Q4 level (2.35%) in each episode window. | `src/fed_svar.py` (fed_svar.py, unified_model.fed_effect) |
| E7 | COVID shutdown to unemployment: du_t = g0 s_t + g1 s_t-1, g0 = 15.25 (2.33), g1 = -4.28 (2.36), OLS 2020Q1-2022Q4, no constant; s = Oxford stringency / 100, faded to 0 by 2023Q2. | `src/unified_model.py` (unified_model.covid_fit) |
| E8 | Unemployment to V/U: log(V/U)_t = a + b u_t, b = -0.290 (1990-2019). Cause k's V/U change = L_t x b x du_k,t with L_t = (V/U_t - V/U_ref) / (log V/U_t - log V/U_ref), so the parts add up exactly. | `src/unified_model.py` (unified_model.run_once) |
| E9 | Worker shortage: e_t - e_2019Q4, where e_t = log(V/U)_t - a - b u_t (the V/U that unemployment doesn't explain); weighted as in E8. | `src/unified_model.py` (unified_model.run_once) |
| E10 | Wage growth (Bernanke-Blanchard): gw_t = c + 4 lags gw + 4 lags V/U + 4 lags 1-yr expectations + 4 lags catch-up + productivity; own + expectation lags sum to 1; 1990-2019. | `src/bb_model.py` (bb_model.estimate) |
| E11 | Price inflation: gp_t = c + 4 lags gp + gw (0-4 lags) + energy/ECI, food/ECI, GSCPI, greed (0-4 lags each) + productivity; own lags + wage terms sum to 1; 1990-2024. | `src/bb_model.py` (bb_model.estimate, unified_model.estimate_with_greed) |
| E12 | Expectations: 10-yr on gp (0-4) + own lags; 1-yr on own lags + 10-yr (0-4) + gp (0-4); each sums to 1. | `src/bb_model.py` (bb_model.estimate) |
| E13 | Greed: residual of margin_t = -400 dlog(1 - unit profits / price) regressed on GSCPI, V/U, energy, food, wages (0-4 lags each), 1990-2024 (R^2 0.51). | `src/unified_model.py` (unified_model.add_greed) |
| E14 | Pre-existing: pi_t with every input at its 2019 reference (no relief, no Fed moves after 2019, energy and food relative prices flat, GSCPI and productivity at 1998/1990-2019 means), plus pre-2020 Fed surprises. | `src/unified_model.py` (unified_model.causes_inflation) |
| E15 | Not explained: actual - model (E10-E12 with every actual input), plus productivity and energy & food shocks after 2023Q1. | `src/unified_model.py` (unified_model.causes_inflation) |

To reproduce one cell: run `src/unified_model.py` (it prints every estimated constant to
`output/unified_model_run.log`), then for cause k compute E1 for each quarter, average the last four quarters, and
multiply by r_t (E2). The point values above are `output/unified_causes_quarterly.csv`, column k.

## Which comparisons the data settle (share of 1,000 redraws, 2021-24 totals)

| A | B | A added more than B in |
|---|---|---|
| Supply chains | Relief signed by Biden | 72% |
| Supply chains | Relief signed by Trump | 76% |
| Relief signed by Biden | Relief signed by Trump | 76% |
| Supply chains | Worker shortage | 78% |
| Worker shortage | Relief signed by Biden | 49% |
| War in Ukraine (energy & food) | Pent-up demand | 62% |
| Supply shocks (group) | Relief + pent-up + Fed | 39% |
| Supply shocks + worker shortage | Relief + pent-up + Fed | 67% |
| Supply chains | All relief (Trump + Biden) | 41% |
