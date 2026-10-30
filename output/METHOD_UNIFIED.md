# fig12: causes of PCE inflation from one model, 2020–2024 (one chart)

- **Chart:** `output/fig12_unified_causes.png`
- **Table, every quarter, with equations and sources:** `output/TABLE_UNIFIED.md` (from `src/make_unified_table.py`)
- **Machine-readable:** `output/unified_causes_quarterly.csv` (each cause with its 90% band)
- **Unemployment pieces:** `output/unified_unemployment_parts.csv`
- **Code:** `src/unified_model.py`, `src/unified_data.py`, `src/fiscal_by_law.py`, `src/fed_svar.py`, `src/make_unified_figure.py`

## Results and limits

**Current results, limits, robustness and comparison with published studies: `output/REPORT.md`.** This file keeps the
link-by-link notes. Version 2 (2026-10-19) changed: the COVID line is estimated from the Oxford lockdown index instead
of being a leftover; pent-up demand is its own line (`src/pentup.py`); the Fed instrument is MPS (F = 9.5) instead of
MPS_ORTH (F = 3.6); the unemployment the causes miss is shown inside "not explained".

## The chain, link by link

### 1. Relief laws → GDP (`src/fiscal_by_law.py`)

effect_t (% of potential GDP) = 100 / PotGDP_t × Σ_programs m_p × Σ_h w_h × X_p,t−h

- **X_p,t: payments by program and quarter**, $bn at an annual rate, as BEA recorded them. Source: BEA, *Effects of Selected Federal Pandemic Response Programs on Federal Government Receipts, Expenditures, and Saving*, releases 2020Q4 Third, 2021Q4 Third and 2022Q4 Third (`data/raw/bea_pandemic/`, from BEA's COVID-19 and Recovery Archive, https://www.bea.gov/federal-recovery-programs-and-bea-statistics/covid-19-recovery).
  - Each quarter comes from the newest release that covers it. 23 program lines are used.
  - Child tax credit: only the increase over its 2021Q1 level counts.
  - Revenue items (aviation tax holiday, student-loan forbearance) are entered as positive support.
- **Who signed.** Payments made before March 2021 are Trump-signed; payments from March 2021 on are Biden-signed (ARP signed 2021-03-11).
  - This rule is deliberately the one least favourable to "Trump's stimulus mattered too". It credits Biden with every later payment, including money from Trump-signed laws, such as the 2021 Paycheck Protection Program round funded by the December 2020 act.
  - 2021Q1 split: economic impact payments use BEA's monthly table (April 2021 release). January + February = 30.3% go to Trump, March = 69.7% to Biden. Every other program is split 2/3 Trump, 1/3 Biden.
  - Totals counted: **$2,095bn Trump-signed, $1,813bn Biden-signed.**
- **m_p: GDP per dollar of budgetary cost.** Source: CBO, *The Effects of Pandemic-Related Legislation on Output*, Sept 2020, Table 3 (`data/raw/cbo/56537-pandemic-legislation.pdf`, p. 6; retrieved via the Internet Archive because cbo.gov refuses automated downloads). Rows copied:

  ```
  Paycheck Protection Program and Related Provisionsb   628   226   0.36
  Enhanced Unemployment Compensation                    442   297   0.67
  Recovery Rebates for Individualsc                     292   175   0.60
  Direct Assistance for State and Local Governments     150   132   0.88
  Other Spending Provisionsd                            700   548   0.78
  Other Revenue Provisionse                             425   157   0.37
  ```

  Program → row:
  - **0.36 (PPP row):** PPP lines, Economic Injury Disaster Loans, Restaurant Revitalization Fund.
  - **0.67:** unemployment programs.
  - **0.60:** economic impact payments, child tax credit.
  - **0.88:** Coronavirus Relief Fund and State and Local Fiscal Recovery Funds, emergency rental and homeowners assistance.
  - **0.78:** Provider Relief Fund, Medicare rate increase, Education Stabilization Fund, transit, air carriers, food assistance, FEMA lost-wages payments, student-loan forbearance. CBO's note d lists "aid for student loans, credit assistance for airlines… the education stabilization fund, and increased funding for … the Federal Emergency Management Agency … and the Department of Transportation".
  - **0.37:** Employee Retention Tax Credit, paid sick leave credits, aviation tax holiday. CBO's note e: "payroll tax credits for employers".
- **w_h: timing.** A share (1−λ)λ^h of a dollar's effect lands h quarters after payment, with λ = 0.74.
  - λ is the value whose path best matches the shape of CBO's own quarter-by-quarter estimate for the 2020 laws (Table 2, "Total" minus the Fed-facilities row: 5.0, 7.9, 6.1, 4.6, 3.7, 2.2, 1.1 percent, 2020Q2–2021Q4), when applied to BEA's 2020 payments (`fit_cbo_timing()`).
  - Band variant: the timing weights in the Hutchins Center Fiscal Impact Measure code (`R/mpc.R`, github.com/Hutchins-Center/Fiscal-Impact-Measure, commit in `data/raw/hutchins/repo/COMMIT`), rescaled to sum to 1.
- **Coverage.** The same fit says CBO's estimate for the 2020 laws is 2.04× what BEA-listed payments × CBO multipliers give. CBO also counts provisions BEA's table does not list. The point estimate uses 1×; the band includes 2.04× for both signers.
- **PotGDP:** CBO real potential GDP (FRED GDPPOT) × GDP price index (FRED GDPDEF) / 100.
- **Result:** GDP raised by up to 3.4% (Trump-signed, 2020Q3) and 2.7% (Biden-signed, 2021Q3).

### 2. GDP → unemployment (Okun's law)

u − u* = c + β × output gap, OLS 1990Q1–2019Q4.
- Data: FRED UNRATE and NROU (CBO), GDPC1 and GDPPOT.
- β = −0.815 (s.e. 0.037). A law's effect on unemployment is β × its GDP effect.

### 3. Fed policy → unemployment (`src/fed_svar.py`, `fed_effect()` in `src/unified_model.py`)

- **The VAR.** Monthly, 12 lags, 1977-06 to 2019-12, seven variables:
  - log industrial production, unemployment, log CPI, log commodity prices, excess bond premium and 2-year Treasury yield, from the authors' SVAR data sheet in the SF Fed's `data/raw/mps/monetary-policy-surprises-data.xlsx`, "Monthly (original)";
  - the SF Fed proxy funds rate (`data/raw/shadow/proxy-funds-rate-data.xlsx`). It is built to capture QE and forward guidance, which is how "money injection" enters the model.
- **Identification.** External instrument = Bauer–Swanson raw surprise MPS, scaled so the 2-year yield rises 1 point on impact.
  - First-stage F = 9.5 (heteroskedasticity-robust 8.2). The orthogonalized MPS_ORTH, which the SF Fed data page calls a better
    measure of new policy information, gives F = 3.6 (weak) and Fed effects several times larger; it is a robustness variant.
  - Bands come from a wild bootstrap of VAR and instrument (1,000 draws).
- **Counterfactuals (Sims–Zha).** Choose policy shocks, only inside a window, so that the proxy funds rate follows the counterfactual path there. Ridge-regularized least squares with λ = 0.05; the band also uses 0.5, which gives nearly identical paths.
  - **Fed 2020–21 rate cuts + QE:** the proxy funds rate never falls below its 2019Q4 average (2.35%). Window: 2020-01 to 2022-02, the months it was below that level.
  - **Fed 2022–23 hikes:** the proxy funds rate never rises above 2.35%. Window: 2022-03 to the month the effective funds rate peaked.
  - After each window, no more shocks: the rate follows the VAR's usual response.
  - The line = minus the effect of those shocks on unemployment.
- **Pre-2020 policy:** Bauer–Swanson surprises before 2020 (−0.03 point; those surprises were slightly tightening). Shown inside "pre-existing".
- **Unregularized version:** the shocks explode. Long, sustained gaps (a Taylor rule, or holding rates down through 2024) also explode; see "Abandoned".

### 4. Unemployment → job openings per unemployed (V/U)

log(V/U) = a + b × u, OLS 1990Q1–2019Q4, with b = −0.290.
- Data: V/U from the Bernanke–Blanchard / Lorenzoni data file (`data/raw/data_us_new.csv`); u = FRED UNRATE.
- **Unemployment pieces.** u_t − u_ref = Trump + Biden + Fed (pre-2020) + Fed (2020–24) + pent-up demand + COVID + miss.
  - COVID = g0 s_t + g1 s_t−1 (Oxford stringency / 100), OLS 2020Q1–2022Q4 on what the other pieces leave unexplained.
  - "Miss" is not a cause: it is excluded from the model's V/U path, and its effect on inflation is inside "not explained".
- **Worker shortage** = change since 2019Q4 in the part of log V/U that unemployment does not explain. In 2022 actual V/U was 1.9 against 1.0 predicted.
- **From logs to levels.** The change in log V/U is split into levels with logarithmic-mean (LMDI) weights, which makes the split exact.

### 5. V/U and supply shocks → PCE inflation (Bernanke–Blanchard)

- **The model.** Wage, price and two expectations equations, with structure, samples and restrictions copied from Lorenzoni's R replication (`src/bb_model.py`, github.com/luigilor/bernanke-blanchard23).
- **Re-based on PCE.** Price inflation = 400 × Δlog PCE price index (BEA DPCERG). Relative energy and food prices = PCE energy (DNRGRG) and PCE food at home (DFXARG) price indexes divided by the employment cost index.
  - Expectations stay the CPI-based series in the source data, since no long PCE-expectations series exists.
  - Shortages = NY Fed GSCPI, whose inputs are purged of demand (Staff Report 1017).
- **Energy & food are inputs, not causes, so they are assigned by date (not estimated):**
  - 2020Q1–2021Q4 (the COVID crash and rebound, including the 2020 OPEC+ cuts made in response) goes into the COVID line.
  - 2022Q1–2023Q1 (the war spike and its fall-back) goes into the war line. The October 2022 OPEC+ cut and the late-2022 bird-flu egg spike fall inside this window and can't be separated with this model's data.
  - After 2023Q1 (OPEC+ 2023 cuts, bird flu, drought and the rest) goes into "other & not explained", since no named cause covers it.

### 6. Greedflation (`add_greed()`)

- **Margin series.** s = unit profits / price per unit of real gross value added, nonfinancial corporate business. Source: BEA NIPA Table 1.15 (A463RD / A455RD).
- **Price effect of margins alone.** Price = unit costs / (1 − s), so the margin change alone moves the price by margin_t = −400 Δlog(1 − s_t), in annualized percent.
- **Removing the overlap.** Regress margin_t on supply chains, V/U, energy, food and wage growth (current + 4 lags each), 1990Q1–2024Q4 (R² = 0.51). The residual is "greed": margin increases those causes don't explain. That removes the overlap with the supply-chain and demand lines by construction.
- **In the price equation.** "Greed", current + 4 lags, enters the price equation, estimated jointly. Coefficient sum −0.011 (s.e. 0.036). With the raw margin series instead: 0.031 (s.e. 0.035).

### 7. Student-loan pause and rental assistance

- **Both are in the BEA program table:** forgone federal interest receipts, and emergency rental and homeowner assistance (a capital transfer, 2021Q1).
- **Loan pause after 2022.** The Education Department notice, as quoted in news coverage ([WJLA](https://wjla.com/news/nation-world/student-loan-payments-set-to-resume-in-october-after-three-year-pause-department-of-education-student-aid-due-date-interest-accrual-loan-forgiveness)): "Student loan interest will resume starting on Sept. 1, 2023, and payments will be due starting in October". BEA's 2022Q4 value is held for 2023Q1–Q2 and for 2/3 of 2023Q3.
- **Who signed.** Same payment-date rule as the other programs, so the pause counts as Trump's before March 2021 and Biden's after.
- They are computed separately and reported as memo lines. In the chart they are inside the Trump and Biden lines.

## Bands

Each of 1,000 draws redraws:
- the Bernanke–Blanchard coefficients (from their estimated covariance);
- Okun β;
- the V/U equation coefficients;
- one SVAR bootstrap replication;
- one of four fiscal variants: timing {CBO-fitted, Hutchins} × coverage {1, 2.04};
- the Sims–Zha ridge {0.05, 0.5};
- the COVID coefficients;
- pent-up demand: multiplier {0.78, 1.0} × spending period {to 2023Q3, to 2024Q4}.

Bands are the 5th–95th percentile of each line.

## Abandoned (kept so it isn't re-tried blind)

1. **Plain regression of V/U on stimulus spending, a Taylor-rule gap and the Oxford stringency index, 1990–2024.** Every effect came out near zero and insignificant. Relief money arrived in the same quarter jobs collapsed, so the regression cannot separate cause from response. Replaced by the CBO-multiplier chain.
2. **Fed measured against a policy rule, or rates held down through 2024.** We tried to make the proxy funds rate follow the Fed Board's rules ("Policy Rules and How Policymakers Use Them", `data/raw/fed_rules/policy-rules.txt`) by feeding in a sequence of SVAR policy shocks (the Sims–Zha method).
   - Taylor rule: unemployment effects of −45 points.
   - Inertial rule: effects that kept growing to −3 points even after the Fed was tighter than the rule in 2023–24.
   - Holding the 2019 rate for all of 2020–24: unemployment effects of +5 points that kept growing.
   - Cause: the SVAR's policy rate falls back after about 18 months, so holding a gap open for years needs ever-larger shocks. Not usable. Only the shorter episode windows in section 3 are used, and even they have very wide bands. The Fed Board's formulas are quoted in the saved page text.
3. **Hutchins FIM as the fiscal measure.** The model behind its program-level effects reads a non-public spreadsheet (`mock-forecast.xlsx` in github.com/lorae/fim-shiny), so it can't be reproduced. Only its timing weights are used, as a band variant.

## Rerun

```
python src/unified_model.py        # ~2 min, writes output/unified_causes_quarterly.csv
python src/make_unified_figure.py
python src/make_unified_table.py
```
