# What caused America's 2021–24 inflation?

A cause-by-cause breakdown of US inflation, 2020–2024: pandemic relief (split by payment date into
payments made under Trump and under Biden), Federal Reserve policy, supply chains, the war in Ukraine,
pent-up demand, worker shortages, COVID restrictions, and what is left unexplained.

**Read the article:** `docs/index.html` (served by GitHub Pages at the link in the repository description).
**Every number, equation and source behind the main chart:** `docs/reproduce.html`, `docs/reproduce_long.csv`.
**Technical report:** `docs/report.html` / `output/REPORT.md`.

**How this was made.** The analysis, code and text were produced by Claude, an AI model from Anthropic,
working under the direction of the repository owner. The owner is not an economist. The core wage-price
model is Bernanke & Blanchard (NBER WP 31417), re-estimated from Lorenzoni's public replication data;
other parts reuse published estimates (CBO multipliers, Bauer–Swanson monetary-policy surprises, the
NY Fed supply-chain index, the Fed Board's FRB/US model as a cross-check). The results are model
estimates with wide ranges, not settled facts. Corrections are welcome: please open an issue.

**Data.** `data/raw/` holds copies of public data (BEA, BLS, FRED, CBO, NY Fed, Federal Reserve Board,
Oxford COVID-19 Government Response Tracker, published replication files). Each remains under its
source's terms; `SOURCE.txt` files record where each came from.

---

# U.S. pandemic inflation: causes by quarter, 2020Q1-2024Q4

Deliverables (in `output/`):
- `fig1_quarterly_decomposition.png` stacked causes vs actual CPI inflation
- `fig2_cause_panels_with_error_bars.png` per-cause estimates with 68%/90% bars + cumulative
- `inflation_causes_2020-2024.xlsx` the table (sources, formulas, coefficients, verification, robustness)
- `quarterly_table.csv`, `decomp_*.csv`, `draws.npy` raw numbers

Reproduce: `python src/run_all.py && python src/make_figures.py && python src/build_workbook.py`
(needs pandas, numpy, matplotlib, openpyxl). Inputs and their provenance: `data/raw/` (`SOURCE.txt` has the upstream commit; the NBER PDF is stored there).
Method: Blanchard & Bernanke, NBER WP 31417, estimated in Python from Lorenzoni's replication data (github.com/luigilor/bernanke-blanchard23).

## Quarterly causes chart (latest)
Run `python src/build_quarterly_causes.py && python src/make_quarterly_figure.py` (needs output/decomp_point.csv, draws.npy and output/fed_policy_effect_digitized.csv from `src/digitize_chicago_fed.py`). Outputs: output/fig6_quarterly_causes.png, fig7_fiscal_by_signer.png; method, assumptions and caveats: output/METHODS_quarterly.md.

## Chart with the causes as named (fig8)
Run `python src/make_user_causes.py` after the steps above. Outputs: output/fig8_causes_as_named.png, user_causes_yoy.csv, user_causes_cumulative.csv; how each line maps to a cause: output/USER_CAUSES_NOTES.md.

## Current version (v3, 2026-10-19): report on the causes, with error term, robustness and Fed test
**Start here: `output/REPORT.md`** (technical report). Rebuild everything: `sh run_report.sh` (~6 min; versions in `requirements.txt`).
Figures: `fig14_cumulative.png` (2021-24 totals, the headline), `fig13_stacked_causes.png` (every quarter), `fig12_unified_causes.png`
(lines), `fig15_fed_late.png` (earlier-hike test). Tables: `TABLE_UNIFIED.md` (every quarter, equations, sources), `COMPARISON.md`
(vs published studies), `robustness_unified.csv`. Code: `src/unified_model.py`, `src/pentup.py`, `src/robustness.py`,
`src/fed_late_report.py`, `src/compare_studies.py`, `src/make_report*.py`. `src/make_web_images.py` is from v2 and no longer used.

## v4 (2026-10-22): how sure, and every number by quarter
- `output/REPRODUCE_TABLE.md` / `output/reproduce_long.csv`: every cause x quarter with data series, numbered
  equations (E1-E15) and 68%/90% ranges (`src/make_reproduce_table.py`).
- `output/REPORT.md` Section 5: where each range's width comes from, grouped totals, pairwise shares, three failed
  attempts to narrow (`src/uncertainty/`, `run_uncertainty.sh`, logs `output/uncertainty_*.log`).
- `src/unified_model.py` now saves the redraws (`output/unified_draws.npy`).

## v5 (2026-10-22): outside evidence
- `src/cross_country_relief.py`: IMF fiscal measures (Oct 2021) vs OECD core / IMF headline inflation, 10 specs ->
  `output/cross_country_relief.csv`. Data in `data/raw/imf_fiscal/`, `data/raw/oecd/`, `data/raw/imf_weo/`.
- `src/combine_outside_evidence.py`: weights the redraws by the cross-country relief estimate (2021-22 core spec) and
  reconciles with the SF Fed supply/demand labels -> `output/combined_*.csv`, `output/shapiro_*.csv`. REPORT.md Section 6.

## v6 (2026-10-22): thirteen extensions
- `src/extensions/e01..e13`, `run_extensions.sh`, outputs in `output/ext/`; REPORT.md Sections 7 (extensions) and 8
  (best estimate: model updated with wage data, category panel and cross-country evidence).
- New data in `data/raw/ext/` (FRED, OxCGRT subnational, Opportunity Insights, Jarocinski-Karadi shocks, BEA
  input-output tables, DOL claims, Bernanke-Blanchard 11-economy paper). Downloaded 2026-10-22.
- `bb_model.WAGE` / `TAU` switch for the kinked wage curve (default "bb" = unchanged).

## v9 (2026-10-23): other countries' wage and price equations; value of better supply-chain data
- `src/extensions/e17_europe_panel.py`: (A) the B&B wage and price equations on 25 European countries, 2010-24
  (Eurostat, `data/raw/ext/eurostat/`), with specification and country-group variants; (B) how far a sharper estimate
  of the direct supply-chain effect could narrow the supply-chain line. Neither narrows the ranges; see REPORT.md E17.

## v8 (2026-10-23): wage catch-up, unemployment checks, why the ranges are wide, best-estimate chart
- `src/extensions/e15_wages_ui_ranges.py`: (A) labor share, real pay vs productivity, wage tracker by quartile, and a
  labor-share catch-up term in the wage equation; (B) where unemployment benefits are in the model, and a
  difference-in-differences on the 25 states that ended the $300 supplement early; (C) a state wage curve on job openings
  per unemployed (BLS JOLTS and LAUS by state, `data/raw/ext/bls_states/`); (D) relief size from the unemployment fit;
  (E) which equation sets each range's width.
- `src/extensions/e16_narrower.py`: the best estimate plus 2020-24 inflation (for the wage and expectations equations)
  and the state wage curve; saves every quarter's 90% range (`output/ext/e16_quarterly.csv`).
- `output/fig16_best_ranges.png` (`src/make_unified_figure.py best`): the quarterly chart with best-estimate ranges.
- Correction: Section 5 item 3 said the unemployment data can't choose a relief size, based on R^2 values computed on
  different left-hand sides. Corrected with the comparable statistic (E15 D).
- New downloads: `data/raw/ext/fred2b/` (FRED), `data/raw/ext/bls_states/` (BLS API v1).

## v7 (2026-10-23): the infrastructure law and the Inflation Reduction Act; each cause listed once
- `src/extensions/e14_iija_ira.py`: CBO's year-by-year scores of the IIJA and IRA through the relief chain (as scored,
  spending side only, and all ten years paid at signing), breakevens on the days each law's fate was decided, and
  inflation at signing -> `output/ext/e14_*.csv`. Sources in `data/raw/ext/laws/` (CBO PDFs via the Internet Archive,
  congress.gov bill status XML via govinfo, Fed press release of July 27, 2022, Wikipedia for the Manchin dates).
- Tables list each cause once; totals sit in their own rows marked as sums. `e12` adds the Fed's net line (`fed_net`).

## v10 (2026-10-29): cross-check with the Fed's FRB/US model
- `src/frbus/frbus_decomp.py`: the same inputs (relief payments, Fed rate path, energy & food window, direct
  supply-chain shock, pent-up spending) run through PyFRB/US instead of our chain. Results and reading:
  `output/frbus/FRBUS_NOTES.md`. Needs the PyFRB/US environment (pandas < 3, xlrd); package and data in `data/raw/frbus/`.
- Relief lines relabeled "paid under" (the split is by payment date); chart legend and footer corrected (the model line
  includes post-March-2023 energy & food, which "other & not explained" also counts).
