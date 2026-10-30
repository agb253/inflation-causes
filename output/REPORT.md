# What caused US inflation, 2020-2024: a cause-by-cause decomposition with an explicit error term

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
  labels put the size of this at about 1.2 points of the 2021-24 total (range -1.9 to +5.0 depending on
  how labels are shared out; Section 6), which would make supply and demand about equal.
- **Single lines are imprecise; groups of lines are not.** The 90% range for supply chains is
  +0.8 to +8.3 points and for the COVID drag
  -12.5 to -0.3. That width is real: it comes from the
  wage-price model's own coefficients, and three attempts to narrow it with more data failed (Section 5). Sums of lines
  are much tighter, because their errors offset: all labor-market causes together,
  +2.2 to +6.3. Read single lines as orders of magnitude and
  the group totals and the comparisons in Section 5 as the findings.
- **The relief lines depend most on one assumption:** how much GDP each relief dollar produced. Scaling the relief
  effects up to CBO's 2020 total (x2.04) roughly doubles both relief lines; the COVID drag deepens by about the same
  amount (Section 9). The 90% ranges include this.
- **The COVID drag is estimated on the same 2020-22 data** as everything else (no outside estimate exists). It is fitted
  to the unemployment that relief, the Fed and pent-up demand leave unexplained, so it partly mirrors their size.
- **The Fed is identified with a borderline instrument** (first-stage F = 9.5; robust 8.2; the usual threshold is 10).
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

PCE inflation added up to 17.3 points over 2021-2024 (the four Q4-over-Q4 rates). The model explains
16.2 of them. The economy's pre-2020 momentum accounts for 8.2
(about 2% a year); the other **9.0 points** are what needs explaining.

| Cause | 2021-24 total [90% range] | At the 2022Q2 peak [90% range] |
|---|---|---|
| COVID supply chains | +4.2 [+0.8 to +8.3] | +1.89 [+0.96 to +2.89] |
| Worker shortage | +2.5 [+1.0 to +4.1] | +0.81 [+0.36 to +1.28] |
| Relief signed by Biden | +2.1 [+1.0 to +5.6] | +0.79 [+0.29 to +2.17] |
| Relief signed by Trump | +1.7 [+0.7 to +5.1] | +0.47 [+0.13 to +1.59] |
| War in Ukraine (energy & food) | +1.5 [+0.5 to +2.5] | +1.13 [+0.98 to +1.28] |
| Pent-up demand | +1.2 [+0.5 to +2.1] | +0.39 [+0.13 to +0.67] |
| Fed 2020-21 cuts + QE | +0.8 [-0.2 to +3.2] | +0.14 [-0.10 to +0.65] |
| Fed 2022-23 hikes | -0.4 [-2.0 to +0.4] | +0.00 [-0.00 to +0.01] |
| Greedflation | -0.0 [-0.2 to +0.1] | +0.00 [-0.03 to +0.04] |
| COVID shutdown drag (incl. 2020-21 oil & food crash and rebound) | -4.3 [-12.5 to -0.3] | -1.56 [-4.35 to -0.27] |
| Other & not explained | -0.2 [-5.7 to +3.7] | +0.88 [-0.34 to +1.84] |
| *Model estimate (sum of causes)* | +16.2 [+12.3 to +21.8] | +6.01 [+4.95 to +7.20] |
| *Actual* | 17.3 | 6.88 |

Ranges are 5th-95th percentiles of 1,000 redraws (Section 5). Figures: `fig14_cumulative.png` (totals),
`fig13_stacked_causes.png` (every quarter, stacked), `fig12_unified_causes.png` (every cause as a line).

**Findings the ranges support:**
1. **Supply shocks were probably the largest new force, but the model doesn't settle it.** Supply chains, the war, the
   worker shortage and the 2021 energy rebound add up to 4.7 of the 6.9 points in 2022Q2 (an
   upper bound; see Section 1). Over 2021-24, supply chains + war + worker shortage exceed relief + pent-up + Fed in
   67% of redraws; without the worker shortage, in 39% (Section 5).
2. **Relief laws mattered, under both presidents, and probably neither was the largest single cause** (supply chains
   exceed Biden-signed relief in 72% of redraws, but all relief together in only
   41%). Biden-signed relief:
   +2.1 [+1.0 to +5.6] points over 2021-24; Trump-signed: +1.7 [+0.7 to +5.1]. Together +3.7 [+1.8 to +10.8], against
   9.0 points of inflation beyond the pre-2020 pace. Much of relief's effect offset the COVID drag (-4.3):
   the shutdown pushed unemployment up and inflation down, and relief pushed the other way.
3. **The Fed's net effect over 2021-24 was small:** +0.4 [-0.1 to +1.5] points. Its 2022-23 hikes were still working
   their way through at the end of 2024.
4. **Greedflation is about zero in the model** (-0.0 [-0.2 to +0.1]), although profit margins did rise in 2021 by
   accounting (Table 3 of `TABLE_UNIFIED.md`). Margin moves beyond what costs, shortages and demand explain don't
   predict PCE inflation in 1990-2024.
5. **Pent-up demand added 1.2 points** [0.5 to 2.1].

Each year (points of year-over-year PCE inflation, official percent change):

| Cause | Year to 2021Q4 | Year to 2022Q4 | Year to 2023Q4 | Year to 2024Q4 | 2021-24 total [90% range] |
|---|---|---|---|---|---|
| Relief signed by Trump | +0.64 | +0.41 | +0.34 | +0.28 | +1.7 [+0.7 to +5.1] |
| Relief signed by Biden | +0.54 | +0.65 | +0.48 | +0.39 | +2.1 [+1.0 to +5.6] |
| Fed 2020-21 cuts + QE | +0.05 | +0.21 | +0.28 | +0.30 | +0.8 [-0.2 to +3.2] |
| Fed 2022-23 hikes | +0.00 | +0.02 | -0.12 | -0.29 | -0.4 [-2.0 to +0.4] |
| Pent-up demand | +0.20 | +0.40 | +0.44 | +0.17 | +1.2 [+0.5 to +2.1] |
| COVID supply chains | +1.33 | +1.83 | +0.56 | +0.48 | +4.2 [+0.8 to +8.3] |
| War in Ukraine (energy & food) | +0.00 | +0.83 | +0.23 | +0.42 | +1.5 [+0.5 to +2.5] |
| Worker shortage | +0.50 | +0.81 | +0.68 | +0.54 | +2.5 [+1.0 to +4.1] |
| Greedflation | -0.01 | -0.01 | -0.01 | -0.00 | -0.0 [-0.2 to +0.1] |
| COVID shutdown drag (incl. 2020-21 oil & food) | -0.22 | -1.88 | -1.09 | -1.15 | -4.3 [-12.5 to -0.3] |
| Pre-existing (end-2019) | +1.79 | +2.04 | +2.19 | +2.21 | +8.2 |
| Other & not explained | +0.94 | +0.75 | -1.02 | -0.83 | -0.2 [-5.7 to +3.7] |
| **Model estimate (sum of causes)** | 4.77 | 5.36 | 3.61 | 2.49 | +16.2 [+12.3 to +21.8] |
| **Actual PCE inflation** | 5.73 | 6.07 | 2.95 | 2.52 | 17.3 |

## 3. Did the Fed act too late?

Tested directly: the model is re-run with earlier hikes and compared with actual policy (`src/fed_late_report.py`,
`fig15_fed_late.png`).

| Counterfactual | Inflation, 2022Q2 | Inflation, 2024Q4 | Unemployment, 2022Q2 | Unemployment, 2024Q4 |
|---|---|---|---|---|
| Hikes from March 2021, to ~2% by early 2022 (the path in Barnichon, FRBSF EL 2022-28) | -0.02 [-0.18, +0.08] | -0.18 [-0.51, +0.03] | +0.20 [-0.16, +0.80] | +0.41 [+0.02, +0.95] |
| The actual 2022-23 hikes, a year earlier | +0.01 | -0.40 [-1.08, +0.09] | +0.29 | +1.34 [-0.00, +2.81] |

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
3. **GDP → unemployment:** Okun's law, beta = -0.815, estimated 1990-2019.
4. **Fed → unemployment.** Monthly proxy SVAR (Bauer-Swanson data, 1977-2019), instrument = monetary-policy surprise
   MPS, F = 9.5. Counterfactual rate paths via Sims-Zha policy shocks inside each episode window.
5. **COVID shutdown → unemployment, estimated:** u-change not explained above = g0 s_t + g1 s_t-1 + e_t, OLS
   2020Q1-2022Q4, no constant; s = Oxford stringency index / 100. g0 = 15.25 (s.e. 2.33), g1 = -4.28 (s.e. 2.36),
   R^2 = 0.80 (uncentered, since there is no constant: 0.95). After the tracker ends (2022) the index fades to 0 by 2023Q2, when the federal Public Health Emergency
   ended (HHS). The residual e_t is not assigned to any cause; it is part of "other & not explained".
6. **Unemployment → V/U:** log(V/U) on u, 1990-2019. V/U beyond what unemployment implies = worker shortage.
7. **V/U, energy, food, supply chains (NY Fed GSCPI), margins → PCE inflation:** Bernanke-Blanchard wage-price model,
   re-estimated on PCE.
8. **Attribution:** each cause = model inflation with every cause minus model inflation without that cause. The model
   is linear, so the causes add up to the model's estimate; the gap to actual inflation is reported, not assigned.

**What changed from the previous version, and why.** (a) The COVID line was a leftover forced to match unemployment;
it is now estimated, and what it misses is shown as error. (b) The Fed instrument was MPS_ORTH (F = 3.6, weak), which
implied the 2022-23 hikes raised 2024 unemployment by about 4 points; it is now MPS (F = 9.5). (c) Pent-up demand is
estimated instead of sitting inside the leftover. (d) The "did the Fed act too late?" test is new.

## 5. Uncertainty: why some ranges are wide, and what the data do pin down

Each of 1,000 redraws varies: the wage-price coefficients; Okun beta; the V/U coefficients; one wild-bootstrap
replication of the Fed VAR and instrument; relief timing (CBO-fitted or Hutchins) x coverage (1 or 2.04); the
Sims-Zha ridge; the COVID coefficients; pent-up demand's multiplier (0.78 or 1.0) and spending period (to 2023Q3 or
2024Q4). Half the redraws use relief coverage 2.04, so the relief and COVID ranges are not centred on the point
estimate (Biden and Trump relief combined: median +4.8 against point +3.7).
Ranges are reported at 68% (16th-84th percentile) and 90% (5th-95th); every cause, every quarter:
`output/reproduce_long.csv`.

**Where the width comes from** (width of the 2021-24 90% range when only that source varies, 150 redraws each,
`src/uncertainty/sources.py`):

| Cause | Wage-price coefficients | Okun | V/U on u | Relief timing & size | Fed VAR | Pent-up variants | COVID coefficients | All together |
|---|---|---|---|---|---|---|---|---|
| Supply chains | 7.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 6.5 |
| COVID drag | 9.1 | 0.5 | 0.5 | 4.1 | 1.4 | 0.4 | 1.5 | 13.0 |
| Worker shortage | 3.3 | 0.0 | 0.1 | 0.0 | 0.0 | 0.0 | 0.0 | 3.1 |
| Trump relief | 2.3 | 0.2 | 0.1 | 1.9 | 0.0 | 0.0 | 0.0 | 4.7 |
| Biden relief | 2.4 | 0.3 | 0.2 | 2.5 | 0.0 | 0.0 | 0.0 | 4.5 |
| Pent-up demand | 1.5 | 0.1 | 0.1 | 0.0 | 0.0 | 0.5 | 0.0 | 1.5 |
| Fed cuts+QE | 1.1 | 0.0 | 0.1 | 0.0 | 2.8 | 0.0 | 0.0 | 3.2 |
| Fed hikes | 0.5 | 0.0 | 0.0 | 0.0 | 2.2 | 0.0 | 0.0 | 2.2 |
| Pre-existing | 6.6 | 0.0 | 0.0 | 0.0 | 0.1 | 0.0 | 0.0 | 7.5 |
| War | 2.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.8 |

- **Supply chains:** almost all from the price equation's GSCPI coefficients. Their sum is
  0.135 (se 0.069): the effect is identified by one episode
  (2021-23), because the index barely moved before.
- **COVID drag:** mostly the wage equation, whose V/U coefficients (sum
  0.720 (se 0.325)) are estimated on 1990-2019 and applied to the 2020 collapse in V/U (not outside that range: V/U was 0.16 in
  2009 and 0.27 in 2020Q2, but never before did it fall so far in one quarter), and wages did not slow as the
  equation predicts (Section 7, extension 13);
  next, relief coverage, because the COVID line is fitted to the unemployment that relief leaves unexplained (a
  bigger relief effect means a deeper COVID drag; correlation across redraws -0.92).

**What the data pin down: sums whose errors offset** (2021-24 totals, `output/uncertainty_groups.csv`). Each group is a
sum of causes listed in Section 2, not an extra cause, and the groups overlap, so they don't add up to anything:

| Group | Point | 68% range | 90% range |
|---|---|---|---|
| All labor-market causes (relief, pent-up, Fed, COVID drag, worker shortage) | +3.5 | +2.9 to +5.3 | +2.2 to +6.3 |
| The pandemic and the response (relief + pent-up + COVID drag) | +0.6 | -0.4 to +2.3 | -1.5 to +3.0 |
| Supply shocks (supply chains + war) | +5.7 | +3.9 to +7.8 | +2.7 to +9.3 |
| for comparison: supply chains alone | +4.2 | +2.3 to +6.6 | +0.8 to +8.3 |
| for comparison: COVID drag alone | -4.3 | -9.2 to -2.1 | -12.5 to -0.3 |
| Model estimate | +16.2 | +14.0 to +19.6 | +12.3 to +21.8 |

**Which comparisons the data settle** (share of redraws in which A added more than B over 2021-24,
`output/uncertainty_pairs.csv`):

| A | B | Share |
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

So the model says with confidence that supply chains, the war, relief, pent-up demand and the worker shortage each
raised inflation, and that the COVID shutdown lowered it. It does not settle whether supply shocks or demand were the
bigger force overall (39% of redraws put supply first), and because the demand lines are lower bounds
(Section 1), the true balance leans further toward demand than that share suggests.

**Three attempts to narrow the single lines, none adopted** (code in `src/uncertainty/`, logs in `output/`):
1. *Weight the coefficient redraws by how well they reproduce observed 2020-24 wage growth* (data the wage equation
   never saw). The COVID range narrows only modestly, the supply-chain range not at all, and too few redraws carry the
   weight (ESS 47 of 600) for the result to be stable. Log: `uncertainty_condition.log`.
2. *Re-estimate the wage and expectations equations through 2024 instead of 2019.* The ranges barely change. Log:
   `uncertainty_extend_sample.log`.
3. *Let the unemployment data choose the relief multiplier.* An earlier version of this report said the lockdown fit
   was equally good at every relief size (centred R^2 0.77 to 0.80). That comparison was wrong: each relief size
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
forgone revenue, % of GDP; US 25.5%) and how much its inflation rose (OECD core CPI; IMF WEO headline). Regression
across countries of excess inflation (sum of annual rates minus the 2015-19 pace) on relief size; the US effect is the
slope times US relief, which asks the same question as the relief lines (relief against none).

| Specification | Countries | Slope per % of GDP (s.e.) | US relief effect, points (s.e.) |
|---|---|---|---|
| Core CPI, 2021-24, advanced economies | 18 | 0.022 (0.136) | +0.6 (3.5) |
| same + euro-area dummy | 18 | 0.006 (0.168) | +0.2 (4.3) |
| **Core CPI, 2021-22, advanced economies (used below)** | 18 | 0.098 (0.059) | +2.5 (1.5) |
| Core, 2021-22 + euro-area dummy | 18 | 0.074 (0.078) | +1.9 (2.0) |
| Core, 2021-22 + energy exposure (headline minus core, 2022) | 18 | 0.092 (0.071) | +2.3 (1.8) |
| Core, 2021-22, + Poland, Chile, Colombia, Mexico | 22 | 0.091 (0.064) | +2.3 (1.6) |
| Headline (IMF), 2021-22, incl. Japan & Singapore | 20 | -0.016 (0.087) | -0.4 (2.2) |
| Core, 2021-24, + 4 emerging | 20 | -0.052 (0.148) | -1.3 (3.8) |
| Headline (IMF), 2021-24, incl. Japan & Singapore | 20 | 0.053 (0.103) | +1.4 (2.6) |
| Headline, 2021-24 + euro-area dummy | 20 | 0.103 (0.129) | +2.6 (3.3) |

- Over 2021-24 the cross-country slope is close to zero and very imprecise: Europe's 2022-23 energy shock dominates the
  differences between countries in those years. Over 2021-22, when relief's effect peaked,
  the estimate is 2.5 points (s.e. 1.5) of core CPI, 2.5 (1.5) in PCE terms. Published
  cross-country estimates are close, though their measures and periods differ: de Soyres, Santacreu & Young (FEDS Note,
  July 2022) roughly 2.6 points; Jorda et al. (FRBSF EL 2022-07) about 3 by 2021Q4 (core CPI).
- The model's relief, measured the same way (2021-22 annual averages): 2.0 (90% range 1.0 to
  5.7). **The two agree.**
- Combining them (each redraw weighted by its fit to the cross-country estimate, `src/combine_outside_evidence.py`)
  trims the high-relief redraws, the ones that use CBO's larger multiplier scale. The effective number of redraws stays
  865 of 1,000: the cross-country evidence is weak (18 countries, R^2 0.05), so the narrowing is modest:

| 2021-24 total | Model alone, 90% range | With cross-country evidence, 90% range |
|---|---|---|
| Relief signed by Biden | +1.0 to +5.6 | +1.1 to +4.5 |
| Relief signed by Trump | +0.7 to +5.1 | +0.7 to +4.5 |
| COVID drag | -12.5 to -0.3 | -10.6 to -0.4 |
| Supply chains | +0.8 to +8.3 | +0.8 to +8.4 |
| Worker shortage | +1.0 to +4.1 | +1.0 to +4.0 |
| *Total:* Biden + Trump relief (what the cross-country comparison measures) | +1.8 to +10.8 | +1.9 to +8.9 |
| *Total:* Biden + Trump relief + pent-up demand + COVID drag | -1.5 to +3.0 | -1.5 to +2.9 |

**SF Fed supply/demand labels** (Shapiro; `output/shapiro_leakage.csv`). Shapiro labels each spending category's price
change as supply-driven (price and quantity move opposite ways), demand-driven (same way) or ambiguous. That is a
different question from "which cause", so the two can't be weighted against each other directly. Three of the model's
lines have no counterpart in his labels: the lingering COVID drag on jobs, the pre-existing momentum above its 2019
level, and "not explained"; his method spreads them over all labels. With c = the share of those lines his method labels
supply, and a = the share of "ambiguous" that is really supply:

    leakage L = model supply lines + c x (no-counterpart lines) - (Shapiro supply + a x ambiguous)

L is the part of the model's supply lines that Shapiro's data label as demand: the "demand meeting limited supply" of
Section 1. Setting a and c to his supply share of labelled inflation:

| Shapiro series | Supply | Demand | Ambiguous | Leakage L, median [90% over redraws] |
|---|---|---|---|---|
| SF Fed published | 5.0 | 4.7 | 1.8 | +1.2 [-1.4 to +3.6] |
| recomputed L4t | 4.3 | 5.3 | 1.4 | +2.4 [+0.0 to +4.8] |
| recomputed L4pct | 4.5 | 3.9 | 2.6 | +1.1 [-1.6 to +3.5] |
| recomputed L5t | 5.1 | 4.1 | 1.9 | +0.8 [-2.0 to +3.2] |
| recomputed L5pct | 4.1 | 3.8 | 3.2 | +1.3 [-1.3 to +3.7] |

So Shapiro's data say roughly 1.2 points of what the model calls supply (supply chains, war, worker shortage) was
demand, but the range runs from about -1.9 to +5.0 depending on the label shares, which no data pin down. Moving the
central amount gives supply (supply chains + war + worker shortage) 7.0 and demand (relief + pent-up + Fed)
7.6: **about equal.** This doesn't narrow the supply-chain line; it sizes the lower-bound problem.

## 7. Better data and models: seventeen extensions (`src/extensions/`, `output/ext/`)

Each extension adds data or a method the model above doesn't use, and keeps its log. Two could not be done and are
listed at the end.

**Supply chains**
- *E2. Differences across spending categories.* Category PCE prices, monthly 1999-2024, with a separate effect for
  every month (which absorbs relief, the Fed, pent-up demand, wages and expectations), so only how much MORE
  supply-chain-exposed categories moved identifies the effect:

| Variant | Direct effect, 2021-24 (s.e.) | Peak, year-over-year |
|---|---|---|
| goods exposure | +1.5 (0.6) | +1.0 (2022-05) |
| import-share exposure | +1.3 (0.4) | +0.8 (2022-07) |
| goods + goods-demand control | +1.6 (0.6) | +1.1 (2022-07) |
| goods, estimated 1999-2019 only | +2.5 (0.9) | +1.3 (2022-10) |
| goods, supply-labelled price changes only | +1.1 (0.4) | +0.6 (2022-08) |
| *The model's own direct term* | +0.54 (90%: -0.15 to +1.36) | |

  The direct effect is 1 to 2.5 points, larger than the model's own direct term (+0.54). Estimated on
  1999-2019 alone, without the pandemic, it is +2.5
  (0.9): the effect does not rest on one episode. The model's
  supply-chain line (+4.2) is mostly not this direct effect but its knock-on through wages and
  expectations, which the model's unit-root dynamics make large.
- *E3. Cars.* New and used vehicles and parts added +0.8 points over
  2021-24 (direct), +0.46 of it labelled supply-driven by Shapiro's method.
- *E4. Other supply measures* (each in place of the GSCPI; line = full model; forecast error from E11):

| Supply-chain measure | Coefficient sum (s.e.) | Supply-chain line, 2021-24 [90%] | 2022-24 forecast error (4-quarter) |
|---|---|---|---|
| GSCPI (model) | 0.135 (0.069) | +4.2 [+0.6 to +8.4] | 1.08 |
| delivery times | 0.181 (0.081) | +2.9 [+0.7 to +5.7] | 0.71 |
| unfilled orders | 0.065 (0.079) | +0.0 [-0.2 to +0.3] | 0.74 |
| composite | 0.167 (0.072) | +4.6 [+1.6 to +8.9] | 1.14 |

  The supply-chain line depends on which measure stands for supply problems. The measures that forecast 2022-24 best
  give smaller lines.

**COVID drag and wages**
- *E1. Kinked Phillips curve* (Benigno-Eggertsson): with a threshold at V/U = 1, the extra slope above it is
  -0.451 (0.842) in the wage equation and +0.913 (0.800) in the price equation; no threshold from 0.6 to 1.4 is significant. Not
  adopted.
- *E13. Did wages slow in 2020?* The model's wage equation predicts 4-quarter wage growth of
  1.4% by 2020Q4; actual ECI growth was 2.8%,
  and the Atlanta Fed Wage Growth Tracker (same workers, so no layoff distortion) 3.7%,
  unchanged from 2019. The COVID drag works mainly through that predicted slowdown, so it is overstated.
- *E5. States.* Lockdowns: with quarter effects (which remove everything national), each unit of stringency raised a
  state's unemployment by 4.7 (1.6)
  points at once and 4.3 (1.3) a
  quarter later: about the same total as the national fit, which supports it. Wage curve: state wage growth falls
  0.35 per point of unemployment below 6% and less above it (change
  +0.15, s.e. 0.20), flatter at high
  unemployment, as the COVID evidence suggests, but not significantly.

**Relief**
- *E7. Cross-country, quarterly* (core CPI, 2021Q4): US relief effect +1.9
  (1.0) against the model's 1.2
  for the same quarter; 2021Q4 + 2022Q4 is uninformative (+0.7, s.e.
  2.5).
- *E6. What recipients spent* (Opportunity Insights card data). Third stimulus checks: card spending ran
  1.5% above trend in the six weeks after March 15, 2021 (8.3% for the
  lowest-income quarter); scaled to all spending, about 7% of the $390 billion within six weeks
  (rough: card data miss rent, utilities and health). States that ended the $300 unemployment supplement early
  (25 states, June-July 2021): low-income card spending fell 1.0% (s.e. 0.5) relative
  to other states. Too coarse to replace CBO's multipliers; nothing here suggests they are too low.

**The other Biden laws: the infrastructure law (IIJA) and the Inflation Reduction Act (IRA)**
- *E14.* Neither is in the relief lines. Each law's year-by-year budget effect as CBO scored it (IIJA: cost estimate
  for Senate Amendment 2137, Table 1; IRA: Estimated Budgetary Effects of P.L. 117-169, Sept 2022) is put through the
  same chain as the relief laws. CBO scored the IIJA at +$256 billion of deficits over 2021-31 and the IRA at -$58
  billion (it raised more than it spent). Three versions, each more generous to the claim that they caused inflation:

| 2021-24 total, model point [90% range] | Infrastructure law | Inflation Reduction Act | Both |
|---|---|---|---|
| As CBO scored it (net of offsets, CBO multipliers) | +0.01 [+0.01 to +0.03] | -0.00 [-0.00 to +0.00] | +0.01 [+0.01 to +0.03] |
| Spending side only (offsets removed, $1 of GDP per $1) | +0.24 [+0.12 to +0.39] | +0.07 [+0.03 to +0.11] | +0.31 [+0.14 to +0.50] |
| All ten years of spending paid the quarter it was signed | +0.59 [+0.29 to +0.97] | +0.18 [+0.09 to +0.29] | +0.76 [+0.37 to +1.24] |

  The third row tests "promises of future money raise prices today" in its strongest form: every dollar of ten years
  of spending is treated as if it reached the economy the quarter the law was signed. Even then the two laws together
  add less than either relief law (Biden +2.1, Trump +1.7 in the same units). Timing: PCE
  inflation (4-quarter) was already 5.7% in 2021Q4, when the IIJA was signed; the IRA was signed in 2022Q3, after the
  2022Q2 peak. CBO's August 4, 2022 letter to Senator Graham (cbo.gov/publication/58357): "In calendar year 2022,
  enacting the bill would have a negligible effect on inflation ... In calendar year 2023, inflation would probably be
  between 0.1 percentage point lower and 0.1 percentage point higher under the bill than it would be under current law."
  Market expectations on the days the laws' fate was decided (change from the last close before the news to the first
  close after; ordinary range = 5th-95th percentile of same-length changes 2015-19):

| News | Window | 5y5y change | 5y | 10y | Ordinary range (5y5y) |
|---|---|---|---|---|---|
| IIJA passes Senate (69-30) | 2021-08-09 to 2021-08-11 | +0.05 | +0.05 | +0.05 | -0.07 to +0.07 |
| IIJA passes House (228-206, late night) | 2021-11-04 to 2021-11-08 | +0.06 | +0.06 | +0.06 | -0.07 to +0.07 |
| IIJA signed | 2021-11-12 to 2021-11-16 | -0.06 | +0.06 | +0.00 | -0.07 to +0.07 |
| Build Back Better passes House (220-213) | 2021-11-18 to 2021-11-22 | -0.11 | -0.13 | -0.12 | -0.07 to +0.07 |
| Manchin says no to Build Back Better (Sunday) | 2021-12-17 to 2021-12-20 | +0.02 | +0.00 | +0.01 | -0.06 to +0.05 |
| Manchin-Schumer deal announced (became the IRA) | 2022-07-26 to 2022-07-28 | +0.13 | +0.11 | +0.12 | -0.07 to +0.07 |
| IRA passes Senate (51-50, Sunday) | 2022-08-05 to 2022-08-08 | +0.03 | +0.01 | +0.02 | -0.06 to +0.05 |
| IRA passes House (220-207) | 2022-08-11 to 2022-08-15 | -0.01 | -0.05 | -0.03 | -0.07 to +0.07 |
| IRA signed | 2022-08-15 to 2022-08-17 | +0.01 | +0.03 | +0.02 | -0.07 to +0.07 |

  No consistent pattern. Expectations fell when Build Back Better passed the House and did not fall when Manchin killed
  it. They rose in the window of the Manchin-Schumer deal (July 27, 2022), but that afternoon the FOMC also raised rates
  by 3/4 point (statement at 2:00 p.m.), and 5-year breakevens kept rising by similar amounts on the following days
  (+0.05, +0.06, +0.06), so the deal can't be isolated. Breakevens
  also contain risk and liquidity premia. Limits: CBO's scores are projections made at passage, not outlays as they
  happened. Actual spending by quarter was not checked; the third row is the bound that covers any timing.

**The Fed**
- *E8. Other ways to identify the Fed's effect:*

| Fed identification | First-stage F | Cuts + QE, 2021-24 | Hikes, 2021-24 | Net |
|---|---|---|---|---|
| VAR, Bauer-Swanson surprise (model) | 9.5 | +0.8 | -0.4 | +0.4 |
| VAR, Jarocinski-Karadi shock | 5.1 | +1.3 | -0.4 | +0.9 |
| Local projections, Bauer-Swanson | 7.0 | +1.5 | +0.4 | +1.7 |
| Local projections, Jarocinski-Karadi | 2.4 | +10.7 | -1.2 | +9.5 |

  Every credible alternative gives the Fed a larger effect than the model (net +0.9 to
  +1.7 against +0.4), but all rest on instruments at or below the usual strength
  threshold (F 10). The last row is a weak-instrument artifact and is not used.
- *E9. Credibility.* On the day of the new framework (Aug 27, 2020) the 5-year, 5-year forward breakeven rose
  +0.05 points over two days, inside the range of
  ordinary 2015-19 moves; it went from 1.81% the day before to 2.25% at end-2021 (2015-19
  range 1.41-2.35%; 2021-22 peak 2.67%). Market measures show
  long-run expectations drifting up toward the top of their pre-COVID range, not a break. Breakevens also contain
  risk and liquidity premia.

**Greed**
- *E10. Margins by industry* (BEA input-output accounts): economy-wide, gross operating surplus rose
  +1.1 points of output in 2021, +0.4 in 2022 and +1.4
  in 2023 from its 2015-19 average. The largest rises were in water transportation, mining, farms, wood and chemical
  products, where supply was tight: scarcity rents, which Bernanke and Blanchard (2024, footnote 6) also suspect, rather
  than broad-based markups. (Restaurants and hotels rise partly because PPP loans count as subsidies.)

**Testing the whole model**
- *E11. Out of sample.* Price equation estimated through 2021Q4 only, then 2022-24 inflation forecast from the actual
  inputs:

| Version | Error, quarterly | Error, 4-quarter | Average error |
|---|---|---|---|
| model (GSCPI) | 1.31 | 1.08 | +1.09 |
| supply = delivery times | 1.02 | 0.71 | +0.66 |
| supply = unfilled orders | 1.04 | 0.74 | +0.60 |
| supply = composite | 1.37 | 1.14 | +1.16 |
| wage equation through 2021 | 1.81 | 1.56 | +1.62 |
| no change (2021Q4 4-quarter rate) | 2.54 | 2.09 | +1.81 |
| AR(4) on inflation | 2.24 | 1.95 | -1.70 |

  The model beats simple benchmarks by half or more, but over-forecasts 2022-24 (too much persistence), least when
  supply problems are measured by delivery times or unfilled orders.

**Wages, unemployment checks, and why the ranges are wide** (`src/extensions/e15_wages_ui_ranges.py`)
- *E15 A. Were wages held down before COVID, and did 2021-24 correct it?* Labor's share of nonfarm business income
  averaged 109 (index, 2017 = 100) in the 1990s and 99.5 in the 2010s (BLS via FRED PRS85006173): pay
  did fall behind productivity. But 2020-24 did not reverse it:

| 2019Q4 to | Real pay per hour | Productivity | Labor share |
|---|---|---|---|
| 2021Q4 | +5.5% | +6.0% | -0.0% |
| 2022Q4 | +1.0% | +4.6% | -2.7% |
| 2024Q4 | +5.1% | +10.2% | -2.7% |

  Real pay rose about half as fast as productivity, so labor's share fell further. A catch-up term in the wage
  equation (last quarter's labor-share gap, 1990-2019) is small and not significant: -0.026 (s.e.
  0.019) on the gap from the 1990-2019 average, +0.066 (0.058) on the gap from trend;
  either way it adds at most 0.4 points to any quarter's wage growth. Where catch-up did
  happen is at the bottom: the lowest-paid quarter of workers gained the most after inflation (Atlanta Fed Wage Growth
  Tracker, same workers a year apart; cumulative from December 2019 to December 2024, approximate):

| Wage level, Atlanta Fed tracker | Nominal | After PCE inflation |
|---|---|---|
| lowest quarter of wages | +26.8% | +8.7% |
| second | +24.7% | +6.7% |
| third | +22.3% | +4.2% |
| top quarter | +20.8% | +2.8% |

  So COVID gave low-wage workers leverage, but across all workers prices rose faster than pay, not the reverse. Wage
  catch-up is not a separate cause of the inflation; the low-wage gains are part of the worker-shortage and V/U lines.
- *E15 B. Unemployment checks.* The expanded benefits (the $600 and $300 weekly supplements, pandemic assistance for
  gig workers, extended weeks) are BEA's "Expansion of unemployment programs" line, one of the relief payments,
  with CBO's multiplier for unemployment benefits (0.67); they sit in the Trump and Biden relief lines by signing
  date. Their other possible effect, keeping people out of work, would show up in the worker-shortage line. Test: 25
  states ended the $300 supplement early (June 12 to July 31, 2021), the rest in September:

| Outcome, early-ending states vs others | Estimate | s.e. |
|---|---|---|
| employment, all (share of Jan 2020) | -0.005 | 0.003 |
| employment, lowest wage quarter (share of Jan 2020) | -0.014 | 0.014 |
| unemployment rate (points) | +0.124 | 0.101 |
| average hourly earnings (% vs Apr-May 2021) | +0.682 | 0.344 |

  None of these is the sign the "benefits kept people home" story predicts at a size that matters: employment in the
  ending states did not rise relative to the others (all workers -0.5%, s.e. 0.3%),
  unemployment did not fall, and wages did not fall. Limits: one summer, and the 95% ranges can't exclude a
  small effect.
- *E15 E. What makes the ranges wide.* Redraw one equation's coefficients at a time:

| 90% width, 2021-24 total | Wage equation | Price equation | Expectations | All four |
|---|---|---|---|---|
| Supply chains | 0.5 | 6.8 | 1.1 | 7.8 |
| War in Ukraine | 0.1 | 1.7 | 0.2 | 2.0 |
| Worker shortage | 2.8 | 0.9 | 0.5 | 3.0 |
| Biden relief | 2.1 | 0.8 | 0.3 | 2.3 |
| Trump relief | 2.0 | 0.6 | 0.4 | 2.1 |
| Pent-up demand | 1.2 | 0.5 | 0.2 | 1.4 |
| COVID drag | 7.8 | 2.5 | 1.5 | 8.3 |

  Two estimates set almost all the width. The price equation's response to supply-chain pressure sets the
  supply-chain and war ranges. The wage equation's response to job openings per unemployed sets the relief, COVID,
  worker-shortage and pent-up ranges. Okun's law, the Beveridge curve, the Fed model and the relief timing add little
  (`output/uncertainty_sources.log`).
- *E15 C, D. Two new sources of data tried, neither adopted.* (C) A state wage curve on job openings per unemployed
  (JOLTS state openings over LAUS unemployed, 51 states, 2009-2024, state and quarter fixed effects):
  0.58 (s.e. 0.46); 2009-19 only -0.00 (0.58). The model's
  long-run slope is 1.29 (redraws 0.43 to 2.30). The state estimate is
  too imprecise, and too dependent on matching a one-year state regression to a long-run national slope, to adopt;
  E16 shows what it would do. (D) Relief size from the unemployment data: see Section 5, item 3.

**Other countries' data, aimed at the two estimates that set the width** (`src/extensions/e17_europe_panel.py`)
- *E17 A. The model's wage and price equations estimated on 25 European countries*, 2010-24 (Eurostat: labour cost
  index, job vacancies, unemployed persons, HICP), same lags and restrictions as the US model, country fixed effects,
  errors clustered by country. Expectations are proxied by the past year's inflation (no comparable survey). V/U is
  measured relative to each country's 2010-19 average because vacancy surveys differ in coverage. The US rows use the
  same units.

| Wage equation | Countries | Long-run slope (s.e.) |
|---|---|---|
| wage, 2010-24 | 25 | 0.28 (0.21) |
| wage, 2010-24, quarter effects | 25 | 1.27 (0.42) |
| wage, 2010-19 | 25 | 2.22 (0.96) |
| US model, wage | 1 | 0.81 (0.31) |

| Price equation | Countries | Supply-chain terms | Inflation persistence | Long-run supply-chain effect (s.e.) |
|---|---|---|---|---|
| price, 2010-24 | 25 | 0.208 | 0.57 | 0.49 (0.27) |
| price, 2010-19 | 25 | -0.132 | 0.65 | -0.37 (0.34) |
| price, 2010-24, dropping 2020Q1-2021Q4 | 25 | 0.059 | 0.57 | 0.14 (0.29) |
| price, 2010-24, western Europe only | 14 | 0.104 | 0.51 | 0.22 (0.24) |
| price, 2010-24, central & eastern Europe only | 11 | 0.293 | 0.71 | 1.00 (0.48) |
| US model, price | 1 | 0.135 | 0.73 | 0.49 (0.30) |

  Neither is adopted. The wage slope runs from 0.28 to 2.22
  depending on the specification, a wider spread than the US model's own uncertainty. Pooled over all 25 countries, the
  long-run supply-chain effect (0.49) matches the US model's
  (0.49). But it falls to 0.22 for western Europe and
  0.14 when all of 2020-21 is dropped, and rises to 1.00 for central and
  eastern Europe. The reason: the supply-chain index is one global series, so every country sees the same single
  episode. More countries average out country noise, but not whatever else happened worldwide at the same time.
  Nothing guarantees European wage-setting responds like American wage-setting, so the wage slopes need not match.
- *E17 B. Would sharper supply-chain price data help?* Category- or industry-level price data (E2) measure the
  DIRECT effect of supply-chain pressure on prices. Suppose that effect were known more and more precisely:

| How well the direct effect is known | Supply-chain total 2021-24, median [90% range] |
|---|---|
| no panel | +4.0 [+0.9 to +8.3] |
| category panel as estimated | +5.3 [+2.5 to +9.4] |
| panel s.e. halved | +6.4 [+3.9 to +10.2] |
| panel s.e. quartered | +7.1 [+4.7 to +10.4] |
| direct effect known almost exactly (s.e. 0.05) | +7.3 [+5.1 to +10.9] |

  Even knowing it almost exactly leaves a range about 6 points wide, against
  7 now. The rest comes from how persistent inflation is (the price equation's own lags),
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

| 2021-24 total, median [90% range] | Model alone | + wage data | + category panel | + wages + panel + cross-country |
|---|---|---|---|---|
| Supply chains | +4.1 [+1.1 to +8.0] | +4.0 [+0.9 to +8.4] | +5.4 [+2.5 to +9.6] | +5.4 [+2.5 to +9.2] |
| War in Ukraine | +1.5 [+0.5 to +2.5] | +1.5 [+0.5 to +2.4] | +1.2 [+0.3 to +2.2] | +1.2 [+0.2 to +2.2] |
| Worker shortage | +2.4 [+0.8 to +4.3] | +2.5 [+1.3 to +3.9] | +2.4 [+1.0 to +4.1] | +2.5 [+1.3 to +3.8] |
| Relief signed by Biden | +2.5 [+0.9 to +5.7] | +2.5 [+1.2 to +5.3] | +2.5 [+1.0 to +5.5] | +2.4 [+1.2 to +4.6] |
| Relief signed by Trump | +2.3 [+0.6 to +5.2] | +2.3 [+1.0 to +5.0] | +2.2 [+0.8 to +5.2] | +2.3 [+1.1 to +4.5] |
| Pent-up demand | +1.2 [+0.5 to +2.1] | +1.2 [+0.6 to +2.0] | +1.2 [+0.6 to +2.1] | +1.2 [+0.6 to +1.9] |
| The Fed (net) | +0.5 [-0.1 to +1.6] | +0.5 [-0.0 to +1.5] | +0.5 [-0.1 to +1.6] | +0.5 [+0.0 to +1.5] |
| COVID drag | -5.3 [-12.4 to +0.2] | -5.6 [-12.2 to -1.7] | -5.2 [-12.4 to -0.5] | -5.6 [-10.7 to -1.8] |
| *Totals: sums of rows above, not extra causes* | | | | |
| Supply total = supply chains + war | +5.6 [+2.9 to +9.4] | +5.5 [+2.7 to +9.3] | +6.7 [+4.1 to +10.8] | +6.7 [+4.1 to +10.4] |
| Demand total = Biden relief + Trump relief + pent-up demand + the Fed | +6.7 [+2.3 to +13.3] | +6.7 [+3.3 to +12.7] | +6.5 [+2.8 to +13.4] | +6.6 [+3.5 to +11.2] |
| Supply chains + war + worker shortage beat the demand total, share of redraws | 65% | 64% | 76% | 78% |
| Effective redraws (of 1,000) | 1000 | 1000 | 1000 | 940 |

**E16: two more pieces of evidence** (`src/extensions/e16_narrower.py`). (I) 2020-24 PCE inflation, used only to
weight the wage and expectations equations, which stop in 2019 (the price equation already uses it). (S) The state
wage curve (E15 C), on each redraw's long-run wage slope.

| 2021-24 total, median [90% range] | Best estimate (E12's evidence, rerun) | + 2020-24 inflation (I) | + I + state wage curve (S) |
|---|---|---|---|
| Supply chains | +5.3 [+2.5 to +9.3] | +5.5 [+2.5 to +9.5] | +5.7 [+2.6 to +9.3] |
| War in Ukraine | +1.3 [+0.2 to +2.2] | +1.2 [+0.2 to +2.2] | +1.2 [+0.2 to +2.1] |
| Worker shortage | +2.5 [+1.4 to +3.7] | +2.5 [+1.4 to +3.6] | +2.0 [+0.9 to +2.8] |
| Relief signed by Biden | +2.5 [+1.2 to +4.6] | +2.5 [+1.3 to +4.6] | +2.1 [+0.9 to +4.0] |
| Relief signed by Trump | +2.3 [+1.1 to +4.4] | +2.3 [+1.1 to +4.5] | +1.9 [+0.8 to +3.6] |
| Pent-up demand | +1.2 [+0.7 to +1.8] | +1.2 [+0.7 to +1.8] | +1.0 [+0.5 to +1.5] |
| The Fed (net) | +0.5 [-0.0 to +1.5] | +0.5 [-0.0 to +1.5] | +0.4 [-0.0 to +1.2] |
| COVID drag | -5.7 [-10.6 to -1.9] | -5.7 [-10.6 to -1.8] | -4.2 [-8.3 to -0.8] |

The first column repeats Section 8's best estimate with a different set of 1,000 runs; it differs from the table
above by up to 0.1 point (simulation noise). Inflation adds nothing beyond the wage data. The state wage curve narrows
the relief, COVID and worker-shortage ranges by about a tenth to a sixth. It lowers the relief and worker-shortage
medians by about 0.4 to 0.5 points and shrinks the COVID drag by 1.5. It is not adopted, for the reasons in E15 C.
Neither touches the supply-chain line.

**The chart** (`output/fig16_best_ranges.png`, `src/make_unified_figure.py best`): every quarter's line from the model,
shaded with the 90% range of this best estimate rather than the model's own redraws. At the 2022Q2 peak the relief
ranges are about 40% narrower than on fig12.

**What the evidence changes.** Read with the out-of-sample and state results above:
1. **Supply chains: +5.4 [+2.5 to +9.2].** The category panel finds a larger direct effect than the model's own, which raises the bottom of the range (from about 1 to 2.5). But the out-of-sample test (E11) and the other supply measures (E4) point the other way: most of this line is knock-on through wages and expectations, and the model's knock-on looks too persistent. Supply chains were clearly a major cause; the size is still uncertain by a factor of about three.
2. **COVID drag: -5.6 [-10.7 to -1.8].** Narrower by about a third. The cross-country evidence removes the deepest drags (which come with the largest relief effects). The wage data remove the shallowest: a model in which wages follow V/U in a straight line needs a strong V/U effect to explain the 2021-22 wage surge, and that same strength implies a deep 2020 drag. E13 shows wages did not in fact slow in 2020, so the true drag may be smaller than any version of this linear model can produce; the state wage curve (E5) hints that wages respond less when unemployment is high, though not significantly.
3. **Relief signed by Biden: +2.4 [+1.2 to +4.6]; signed by Trump: +2.3 [+1.1 to +4.5].** The cross-country evidence trims the high-multiplier cases and the wage data the smallest; each president's relief is now about 1 to 4.6 points, median about 2.4.
4. **Supply versus demand:** with the category panel, supply chains + war and relief + pent-up demand + the Fed come out even (51% of weighted redraws put supply first); counting the worker shortage as supply, 78%. The SF Fed labels (Section 6) also say about even. The data support "both, in similar measure", not "mostly supply" or "mostly demand".
5. **The Fed:** the evidence above doesn't touch the Fed lines; E8 says they are more likely too small than too large.

## 9. Robustness (points at the 2022Q2 peak; `output/robustness_unified.csv`, `src/robustness.py`)

| Variant | Trump relief | Biden relief | Fed cuts+QE | Fed hikes | Pent-up | COVID drag | Not explained | Model total |
|---|---|---|---|---|---|---|---|---|
| As published | +0.47 | +0.79 | +0.14 | +0.00 | +0.39 | -1.56 | +0.87 | +6.01 |
| Fed instrument = MPS_ORTH (weak, F 3.6) | +0.48 | +0.80 | +0.71 | +0.00 | +0.39 | -1.94 | +0.65 | +6.23 |
| COVID = leftover (forced to match unemployment), the old method | +0.47 | +0.79 | +0.14 | +0.00 | +0.39 | -1.49 | +0.80 | +6.08 |
| Lockdown index held at its 2022Q4 value after the tracker ends | +0.47 | +0.79 | +0.14 | +0.00 | +0.39 | -1.56 | +0.87 | +6.01 |
| No pent-up demand | +0.47 | +0.79 | +0.14 | +0.00 | +0.00 | -1.36 | +1.06 | +5.82 |
| Pent-up demand: multiplier 1.0, spent by 2023Q3 | +0.47 | +0.79 | +0.14 | +0.00 | +0.49 | -1.61 | +0.82 | +6.06 |
| Pent-up demand spent over 2021Q2-2024Q4 | +0.47 | +0.79 | +0.14 | +0.00 | +0.26 | -1.49 | +0.93 | +5.95 |
| Pent-up demand: spending trend fit 2017-2019 | +0.47 | +0.79 | +0.14 | +0.00 | +0.38 | -1.55 | +0.87 | +6.01 |
| Relief timing = Hutchins Center weights | +0.48 | +0.55 | +0.14 | +0.00 | +0.39 | -1.36 | +0.91 | +5.97 |
| Relief scaled to CBO's 2020 total (x2.04) | +0.96 | +1.61 | +0.14 | +0.00 | +0.39 | -2.70 | +0.70 | +6.18 |
| Fed counterfactual ridge 0.5 | +0.47 | +0.79 | +0.14 | +0.00 | +0.39 | -1.56 | +0.87 | +6.01 |

Holding the lockdown index at its 2022Q4 value changes only 2023-24 (the fit ends in 2022): averaged over 2021-23 the COVID drag goes from -1.04 to -1.38 and 'not explained' from +0.32 to +0.67 (quarterly annualized log points). The model total stays between 5.82 and 6.23 at the peak under every variant.

## 10. Against published estimates (`output/COMPARISON.md`)

Each row compares like with like as closely as the sources allow. The measures differ (headline vs core, PCE vs CPI, GDP deflator), so a difference under about half a point is not meaningful.

| Question | Published estimate | This project | Comment |
|---|---|---|---|
| Supply vs demand, mid-2022 | SF Fed, Shapiro (EL 2022-15 method, data file): change in headline PCE inflation from 2019 average to 2022m6: supply-driven +2.8, demand-driven +2.2, ambiguous +0.6 | 2022Q2: supply (supply chains + war + worker shortage + 2020-21 energy) +4.7; demand (relief + Fed + pent-up) +1.8; COVID drag on jobs -2.4 | Different method (price-quantity signs by category). Both find supply larger than demand in mid-2022. Our demand is close to theirs, but here the COVID drag offsets it; their split has no separate COVID term. |
| Supply chains, peak | Liu & Nguyen, FRBSF EL 2023-14: GSCPI shocks' contribution peaked at 2.5 points (headline inflation) | Peak 2.0 (2022Q3) | Same index (GSCPI); our estimate is somewhat lower. |
| Relief payments, end-2021 | Jordà, Liu, Nechio & Rivera-Reyes, FRBSF EL 2022-07: US transfers added about 3 points by 2021Q4 (core CPI; 'considerable uncertainty') | 2021Q4 Trump + Biden relief 1.2 [ranges 0.2-1.9 and 0.2-1.4]; at CBO's full 2020 scale about twice that (output/robustness_unified.csv) | Ours counts relief only through the labor market; theirs is a cross-country comparison. Ours is lower. |
| All demand, 2022 | Beckworth & Horan, Mercatus WP 2025 (not peer reviewed): demand 4.40 of 2022 GDP-deflator inflation | 2022Q4 relief + Fed + pent-up +1.7 | Ours is much lower. Theirs counts demand's effect on commodity and sectoral prices too; ours counts only demand through the labor market (see limits). |
| Earlier Fed hikes | Barnichon, FRBSF EL 2022-28: hikes from March 2021 to ~2% by early 2022 -> core inflation about 1 point lower by June 2022 (95%: 0.2-2), unemployment about 2 points higher (1-3) | Same path, 2022Q2: headline PCE -0.02 [-0.18 to +0.08], unemployment +0.20 [-0.16 to +0.80]; by 2024Q4 inflation -0.18, unemployment +0.41 | Ours is much smaller and slower. Trade-off per point of inflation removed: theirs about 2 points of unemployment, ours about 2 by 2024. Our model has no channel through Fed credibility or the dollar. |
| Markups / greed, 2021 | Glover, Mustre-del-Rio & von Ende-Becker, KC Fed 2023: markups grew 3.4% in 2021, 'could account for more than half' of 2021 PCE inflation (5.8) | Model greed line 2021Q4 -0.01; accounting: margin change alone raised corporate prices 3.0% in the year to 2021Q4 | Accounting agrees margins rose in 2021; the model finds margin moves beyond costs, shortages and demand don't predict PCE inflation (1990-2024). The authors themselves point to firms pricing in expected cost increases. |
| Supply-side shocks, the surge | Bernanke & Blanchard (NBER w31417 / AEJ Macro): 'most of the inflation surge that began in 2021 was the result of shocks to prices given wages' | 2021Q4: supply +3.5 vs labor-market demand +1.4 | Same model family, so agreement is expected; it is not independent confirmation. |

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
