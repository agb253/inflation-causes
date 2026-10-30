# Quarterly causes of US inflation 2020Q1-2024Q4: models, assumptions, how each constant was set

Figure: `output/fig6_quarterly_causes.png` (panels A, B, C) and `output/fig7_fiscal_by_signer.png`.
Numbers: `output/quarterly_causes_yoy.csv`, `quarterly_causes_cumulative.csv`, `fiscal_by_signer_yoy.csv`. Code: `src/build_quarterly_causes.py`, `src/make_quarterly_figure.py`.
Units: year-over-year CPI inflation in percentage points (panel A, C); cumulative percent change in the CPI level since 2019Q4 (panel B).

## Why there are two kinds of lines
- **Panel A/B (additive).** One model, Bernanke & Blanchard (B&B), decomposes *what actually happened* into pieces that sum exactly to CPI (checked in code with an assert).
- **Panel C (overlay).** Fiscal, Fed and profit estimates come from *different* models and answer a different question: "how different would inflation have been without this?" Those counterfactual effects cannot be added to Panel A. When I tried, the sum overshot actual CPI by up to 9 points in 2021 and undershot it by up to 4 points in 2023. That gap is real disagreement between the published models, so I kept them separate instead of hiding it.

## Model chosen per cause, and why
| Cause | Model used | Alternatives considered | Why this one |
|---|---|---|---|
| Normal inflation trend / pre-existing | B&B baseline (all shocks set to pre-2020 values) | none comparable | Same model as the shocks, so it adds up. Includes housing, healthcare and other slow structural pressure; cannot be split further. |
| Supply chain | B&B "shortages" term (Google "shortage" searches, paper PDF p.24; NOT independently verified) | SF Fed GSCPI VAR (Liu & Nguyen 2023): ~60% of the above-trend rise | Only quarterly series with data I could re-run and uncertainty bands. SF Fed gives a share, no quarterly path. |
| Ukraine / energy / food | B&B energy + food terms (BLS CPI energy, food; verified against BLS API) | Early-2022 forecasts (Conference Board etc.) | Estimated on realized prices. The invasion (2/24/22) cannot be separated from the earlier 2021 energy rise, and 2020 shows the COVID oil crash. |
| Labor-market tightness | B&B v/u term | none | Where fiscal, Fed and pent-up demand all show up in this model. |
| Other / unexplained | B&B productivity + residual | none | The paper says markups arise inside the shortage effect; no separate markup term. |
| Fiscal stimulus | SF Fed Economic Letter 2022-07 panel local projection, re-run in Python (`src/fiscal_sf_replication.py`) on the authors' replication data | Mercatus SVAR (annual only, not peer reviewed); B&B ("fiscal not needed", p.25) | Quarterly, public data and code, uses a cross-country comparison, and times the effect by actual income flows. Replication gives 3.11 pp at 2021Q4; the paper says "about 3". |
| Fed policy | Chicago Fed Letter 483 (D'Amico & King 2023) survey-augmented VAR, read off its Figure 2F | PIIE WP 24-13 (FRB/US; an earlier-hike counterfactual, different question, not read in full) | Only quarterly CPI estimate I could verify, with a published band. Counterfactual = policy rate held at zero from 2021Q4 to 2023Q3. |
| Corporate profits | BEA nonfinancial-corporate unit profit contribution to price growth (identity: price = unit labor + unit nonlabor + unit profit), excess over its 2015-19 average (-0.24 pp annualized) | KC Fed markup estimate (annual; 3.4% markup growth vs 5.8% PCE inflation in 2021) | Quarterly, public, adds up by identity. NOT causal: profits respond to shortages and costs too. |

## Timing assumptions (your point that a law's date is not the date of its effect)
- **Fiscal**: effect_t = sum over h=0..3 of c_h x (4-quarter average income gap)_{t-h}. The c_h are estimated by the authors' regression (0.071, 0.169, 0.222, 0.092 on core-CPI yoy). Income gap = real disposable income per capita minus its 2015-19 linear trend. So money affects inflation when it reaches household income, spread over a year, not when signed.
- **Fiscal after 2021**: I assume support ended with 2021 and set the income gap to zero from 2022Q1. Only the model's lags carry effects into 2022. Reason: later income-above-trend gaps are real wage growth and inflation erosion, not stimulus. Data: BEA real disposable income per capita chain-linked to the authors' OECD series at 2021Q3 (the two correlate 0.996 in 2007-21; levels differ by up to ~1.5% in 2021).
- **Fiscal applied to headline CPI**: the paper's estimate is for core CPI. I use it as a headline effect.
- **Trump vs Biden split (fig7)**: each quarter's income gap is apportioned by the share of excess federal transfers (BEA PCTR above its Jan-2019 to Feb-2020 trend) paid Mar 2020-Feb 2021 ("Trump-signed laws": CARES, signed 3/27/20; the Dec 2020 relief act) vs Mar 2021 onward ("Biden-signed": American Rescue Plan, signed 3/11/21). Both signing dates are from CRS/Treasury pages; the exact Dec 2020 day and Trump as signer are from public record I did not fetch. This is timing of money. It cannot assign the Fed's actions, tariffs, regulations, the student-loan pause or later laws.
- **Fed**: the model lets expectations move before rates do, so effects begin 2021Q4 although the first hike was 3/16/22. The letter's counterfactual is a zero-rate hold, not "no policy". Values after 2023Q3 are the model's projections.
- **yoy**: B&B quarterly annualized contributions are averaged over four quarters; before 2020Q1, "baseline" = actual inflation and shocks = 0.

## Error bands (they mean different things; do not compare widths across lines)
- B&B lines: 5th-95th percentile of 2,000 draws of the coefficients from each equation's restricted-least-squares covariance; coefficient uncertainty only, not model or data error. The widest band, on "other / unexplained", runs from -2.7 to 6.7 on the cumulative scale.
- Fiscal: authors' definition, +/-1.645 standard errors per coefficient times the income gap (their `do3_fig_3_final.do`). Standard errors computed with statsmodels cluster-robust, not Stata's small-sample adjustment.
- Fed: interquartile range read off the published chart; digitized values reproduce the letter's own cumulative figure to within 0.5 (-6.7 vs -7.1 in the text).
- Profits: none (accounting identity; BEA revisions only).

## What the result says (all with the caveats above)
- By end-2024 CPI was 20.5% above its 2019Q4 level. About 12.6 points (8.6 to 16.9) is the normal pre-pandemic trend. The remaining ~8 points split into supply chain 3.6 (1.1 to 6.6), energy and food 1.8 (0.9 to 2.9), labor tightness 0.4 (0.0 to 0.9), other 2.1 (-2.7 to 6.7).
- Fiscal (overlay): peak ~3.6 pp on yoy inflation in 2021Q3, ~0 by 2023Q2. By who signed, Trump-signed laws dominate through 2021Q2 and Biden's ARP dominates from 2021Q4.
- Fed (overlay): lowered inflation by ~3.9 pp at its 2023Q1 trough, with a wide band.
- B&B and the SF Fed fiscal model disagree about 2021: B&B leaves only ~1 pp of 2021 inflation for anything beyond baseline and supply shocks; SF Fed assigns ~3.5 pp to fiscal. Mercatus (2025) goes further, finding demand 60%+ of 2021 and 85%+ of 2022 excess inflation. The reader should treat the true fiscal contribution as uncertain across these models, not as one number.

## Not estimated (no verifiable quarterly estimate found)
Pent-up demand/excess savings alone; international pressures (SF Fed EL 2024-27 gives only endpoints: ~2 pp added Q1 2021 to Q4 2022); Ukraine separately from the 2021 energy rise; Trump-era vs Biden-era policy other than fiscal transfers; COVID direct effects as their own line (they sit inside energy/food in 2020 and shortages).

## Provenance
- B&B data/paper: `data/raw/` (Lorenzoni replication; NBER w31417). SF Fed fiscal replication zip: `data/raw/sf_fed_fiscal/` (SHA-256 6e0e2bc4a362fdb6a326bee048026cdc2eca551cc16500c0cd2022894702fc49). Chicago Fed letter and Fig 2F: `data/raw/chicago_fed/`.
- FRED/BEA series (unit costs, profit, price, real DPI per capita, PCTR) were read through a fetch subagent because direct curl to FRED hangs here; CSVs in `data/raw/fred_via_fetch/` were transcribed from its report. Checks: unit labor + nonlabor + profit equals price to within 0.001 in all 24 quarters; BEA vs OECD income correlation 0.996.
- Quotes and URLs for SF Fed 2022-07, 2023-14, 2024-27, Mercatus, KC Fed and Chicago Fed: `output/CAUSES_SOURCES.md`.
