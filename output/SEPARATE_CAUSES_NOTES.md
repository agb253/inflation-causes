# fig9: separate causes, summed and checked against CPI

Script: `src/make_separate_causes.py`. Tables: `output/separate_causes_yoy.csv`, `output/separate_causes_cumulative.csv`. Log of the last run: the script prints both tables.

## What changed from fig8

1. **Supply-chain shortages now use a measure with demand removed.** The Google-search shortage index in the Bernanke–Blanchard (B&B) price equation is replaced by the NY Fed Global Supply Chain Pressure Index (GSCPI). The data file is `data/raw/nyfed/gscpi_data.xlsx` (SHA-256 781bc95d377d235563c9be9a63042af02b803b6c5ffb6f3dd1148d0a23a5d301), downloaded 2026-10-16 from newyorkfed.org, with monthly data Jan 1998 to Sep 2026. The method is from Staff Report 1017 (Benigno, di Giovanni, Groen, Noble, May 2022), sec. 3.1, saved at `data/raw/nyfed/sr1017.pdf`:
   > "we collect data on the 'New Orders' PMI sub-component, which captures the extent of customer demand for firms' products and regress the three country-specific supply chain PMI measures (delivery time, backlogs, and purchase stocks) on the contemporaneous value and two lags of this new orders component in an attempt to purge demand factors from these three supply chain PMI subcomponents."

   The authors' own caveat, same section:
   > "While our empirical methodology attempts to purge demand factors before constructing the GSCPI, it is not a perfect measure and its dynamics during the GFC likely still capture some demand components."

   Assumptions:
   - Quarterly value = the mean of the three months.
   - Quarters before 1998 = the index's 1998–2019 mean (−0.304). This parallels the source data, which holds the Google index flat before 2004.
   - The price equation is re-estimated with the GSCPI. Nothing else in B&B changes.
2. **The war in Ukraine covers only the energy and food shocks of 2022Q1–2023Q1.** The energy price relative to wages (energy CPI / ECI) went from 0 at 2021Q4 to +17.6% at 2022Q2 and back to −1.5% at 2023Q1. So the window covers the spike and its fall back to the pre-war level. Later energy and food moves have their own line, "after the war spike". In fig8, the 2024 fall in energy prices relative to rising wages was wrongly charged to the war.
   - The war still pulls year-over-year inflation down in 2023Q1–Q2 (−0.4, −1.2). That is the gas-price spike reversing: when prices fall from a peak, the fall subtracts from the inflation rate.
   - Its effect on the price level stays positive: +2.0% at the 2022Q2 peak and +1.3% at 2024Q4. The +1.3% includes knock-on effects through wages and expectations.
3. The three energy/food windows (COVID 2020–21, war, after) add exactly to the B&B energy+food effect. The script asserts this.

## The check

The sum line adds nine causes: the war, shortages, Trump-signed relief, Biden-signed relief, the Fed, pent-up demand, the COVID energy swing, energy after the war, and pre-existing inflation. B&B's "unexplained" part is left out because it is a residual, not a cause.
- **2020Q3–2022Q2: the sum is above actual**, by up to 3.7 points in the running total. This is about the size of the relief-money lines: 5.0 at 2021Q4. Before this change it was 4.4 points with the Google index. Removing demand from the shortage measure did not remove the overshoot.
  - What remains is a disagreement between models about 2021. B&B fits 2021 inflation almost entirely with energy, shortages and pre-existing inflation; its unexplained part is +1.1 by 2021Q4. The SF Fed study says relief money added about 5% to prices by then.
  - Both cannot be right. Settling it requires one model that estimates relief money and supply shocks together.
- **2022Q3 on: the sum is below actual**, ending at 16.2 vs 20.5. Most of the gap is the Chicago Fed line (−7.7), which compares against holding rates near zero through 2023Q3. The rest is B&B's unexplained part (+2.2) and what is not estimated.

## Not estimated

- **Quantitative easing:** the Chicago Fed study covers the interest-rate path only.
- **Greedflation as a cause:** profit data only split prices into wages, other costs and profit.
- **Other gaps:** international pressures, tariffs, other Trump or Biden policies, housing and healthcare trends.

## Shipping cost (Census import charges), added 2026-10-17

Scripts: `src/fetch_census_freight.py` (Census API, key in `~/.config/census.env`), then `src/make_shipping_cost.py`.
Tables: `output/shipping_cost_quarterly.csv`, `output/shipping_cost_annual.csv`.

- Measure: Census "import charges" (GEN_CHA_MO), meaning freight, insurance and other costs to the first US port, summed over all 98 HS chapters. Sanity check: 2019 customs value is $2,491.7bn, matching the published Census total.
- Charges were 2.80% of import value in 2019. They peaked at 4.14% in 2022Q2 and were back to 2.7–2.9% from 2023Q2 on.
- Extra cost = charges above the 2019 rate × that period's import value: $5.6bn (2020), $24.9bn (2021), $38.6bn (2022), $1.8bn (2023), $0.4bn (2024). About $71bn over 2020–2024.
- As a share of consumer spending (PCE), that is an upper bound on the price effect if all of it was passed on: 0.22% of the price level in 2022, peaking at 0.26% in 2022Q2. Contribution to year-over-year inflation: +0.12 pts (2021), +0.06 (2022), −0.21 (2023).
- Not covered: shipping inside the US (trucking, rail), port-congestion and storage fees billed after arrival, retail markups applied on top of the landed cost, and price rises from goods simply being scarce or late. Contract freight rates also lag spot rates. These charges cover every way goods arrive (air, truck, pipeline, bulk, container), so they rise much less than the "over 500%" container-rate figure the IMF cites.
- Not added to fig9 yet: the shortages line (NY Fed GSCPI) already includes shipping-cost inputs, so adding both would count shipping twice.
