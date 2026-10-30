# fig8: causes as named in the request

Script: `src/make_user_causes.py` (calls `src/build_quarterly_causes.py`). Tables: `output/user_causes_yoy.csv`, `output/user_causes_cumulative.csv`.
Each line, the model behind it, and the assumption that maps the model's output to the cause's name. See `METHODS_quarterly.md` for model choice and data provenance.

| Line | Model / data | Assumption that names it |
|---|---|---|
| War in Ukraine | B&B energy + food terms, simulated with energy and food relative-price growth set to 0 **from 2022Q1 on** only | Every energy/food relative-price move from 2022Q1 on counts as war era. That includes the Jan–Feb 2022 rise before the invasion (2/24/22) and the later fall in prices, which is why the line goes negative in 2023–24 and the running total ends near 0 (peak +2.0 at 2022Q2). B&B is linear in these inputs, so war + COVID energy line = the B&B energy+food effect exactly (asserted). |
| COVID oil crash & reopening rebound | Same B&B energy+food effect minus the war line | Energy/food shocks 2020Q1–2021Q4 = COVID crash and reopening. |
| Trump-signed relief laws / Biden-signed relief law | SF Fed EL 2022-07 fiscal model, income gap split by which period's excess transfers paid it (Mar 2020–Feb 2021 vs Mar 2021 on) | Timing follows the money, not the signing date. Each part's 90% band uses the authors' standard errors on that part's income gap. These are the only Trump/Biden policies with a verifiable quarterly estimate. |
| Greedflation | BEA nonfinancial-corporate unit profits, excess over 2015–19 pace | Accounting identity, not a causal estimate. Profits rise when shortages and demand let firms raise prices, so this overlaps those lines. No band. |
| Supply-chain shortages | B&B shortage term | Shortage index from Google searches (in the Lorenzoni data). Not independently verified. |
| Pent-up demand & hot labor market | B&B labor-tightness term (job vacancies per unemployed person) | Demand shows up here in B&B: pent-up demand, stimulus and Fed easing all raise v/u. It cannot separate pent-up demand from them. |
| Fed interest-rate hikes | Chicago Fed Letter 483, Fig 2F, digitized; band = interquartile | Counterfactual is rates held near zero 2021Q4–2023Q3. Values after 2023Q3 are that paper's projections. Running total at 2023Q4 = −7.15, close to the paper's −7.1. |
| Pre-existing inflation trend | B&B with all 2020+ shocks removed | Expectations and inflation momentum as of end-2019. |
| Other / unexplained | B&B productivity + residual | Whatever the model does not attribute. |

**Sum line** (dotted purple, column `sum_of_causes`): the eight plotted causes added together. Profits and B&B "other/unexplained" are left out. Profits are an accounting split of every price rise, not a cause. "Other/unexplained" is a residual. The test: separate, correct estimates should add up to at or a little below actual CPI.
- **Red hatched (sum above CPI), 2020Q2-2022Q1**, up to +4.4 pp in the running total. The SF Fed relief-money estimate and the B&B supply lines both claim the same inflation, so they are not separate.
- **Gray (sum below CPI), 2022Q2 on**, ending 16.2 vs 20.5. The biggest driver is the Chicago Fed line (-7.7), which measures against rates held near zero through 2023Q3, a strong counterfactual. The gray gap also holds B&B's unexplained part (+2.1) and anything not estimated.

Solid lines (B&B) sum exactly to actual CPI in both panels (asserted). Dashed lines come from separate models, overlap the solid lines, and must not be added to them.

Not on the chart: international pressures (SF Fed EL 2024-27 gives only a total of about 2 pp for 2021Q1–2022Q4), tariffs, other Trump or Biden policies, housing and healthcare trends.
