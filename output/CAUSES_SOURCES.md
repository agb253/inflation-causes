# Sources for fig5_causes_by_study.png
Quotes copied from pages/PDFs fetched 2026-10-16. Where a page could only be read through a summarizing fetch tool, that is stated.

1. **Fiscal 3.0 pp** — Jordà, Liu, Nechio, Rivera-Reyes, FRBSF Economic Letter 2022-07 (Mar 28, 2022),
   https://www.frbsf.org/research-and-insights/publications/economic-letter/2022/03/why-is-us-inflation-higher-than-in-other-countries/
   "The comparison between the actual path of inflation and our scenario in Figure 3 suggests that U.S. income transfers may have contributed to an increase in inflation of about 3 percentage points by the fourth quarter of 2021."
   "...this relatively sizable contribution is estimated with considerable uncertainty because the available sample is too short for any greater precision." Measure: core CPI, year over year. (Fetched via summarizing tool.)
2. **Demand 1.61 / 4.40 pp, supply 0.98 / 0.64 pp** — Beckworth & Horan, Mercatus Working Paper, July 2025 (not peer reviewed), Table 3, PDF p.15 (GDP deflator, year over year). Local text: scratchpad/mercatus.txt.
   2021: demand 1.61, temporary supply 0.51, permanent supply 0.47. 2022: demand 4.40, 0.08, 0.56. Abstract: "demand contributed to more than 60 percent of the excess inflation in 2021 and more than 85 percent of the excess inflation in 2022."
   Their "demand" is all aggregate demand, "which reflects both monetary and fiscal policy" (footnote 11).
3. **Supply chains 2.5 pp** — Liu & Nguyen, FRBSF Economic Letter 2023-14 (Jun 20, 2023),
   https://www.frbsf.org/research-and-insights/publications/economic-letter/2023/06/global-supply-chain-pressures-and-us-inflation
   "Since mid-2022, the contributions of GSCPI shocks have declined from 2.5 to 1.4 percentage points" (so 2.5 is the peak reading, not a 2021-22 average).
   "We estimate that these effects contributed about 60% of the above-trend run-up of headline inflation in 2021 and 2022." (Fetched via summarizing tool.)
4. **B&B shortages, energy, food** — this project: output/decomp_point.csv, annual mean of quarterly annualized CPI contributions (src/run_all.py). Model: Bernanke & Blanchard, NBER w31417; data/raw/paper/. Energy+food starts before the 2022 invasion and cannot be split into "Ukraine" with this model.
5. **International 2.0 pp** — Bell, Jordà, Nechio, Poduri, Stewart, FRBSF Economic Letter 2024-27 (Oct 15, 2024),
   https://www.frbsf.org/research-and-insights/publications/economic-letter/2024/10/international-influences-on-united-states-inflation
   "Between the first quarter of 2021 and the fourth quarter of 2022, the international inflation factor added about 2 percentage points to the rise in U.S. inflation." No uncertainty band is published. (Fetched via summarizing tool.)
6. **Markups** — Glover, Mustre-del-Río, von Ende-Becker, KC Fed Economic Review, Jan 12 2023 (abstract via https://ideas.repec.org/a/fip/fedker/95477.html; PDF p.1 read locally):
   "markups grew by 3.4 percent over the year, whereas inflation, as measured by the price index for Personal Consumption Expenditures, was 5.8 percent, suggesting that markups could account for more than half of 2021 inflation."
   Same abstract: timing "more consistent with firms raising prices in anticipation of future cost increases, rather than an increase in monopoly power or higher demand."
   Follow-up, Glover, Mustre-del-Río, Nichols, KC Fed Economic Bulletin, May 12 2023: "Although corporate profits indeed contributed to inflation in 2021, their contribution fell in 2022."
7. **Context, not charted** — Shapiro, FRBSF EL 2022-15 and data (data/raw/sf_fed/): supply-driven ~half of PCE inflation gap to 2019 in the April 2022 reading; see fig4.

Not found: ex-post estimates for Fed policy alone, pent-up demand alone, the Ukraine war alone, or Trump- vs Biden-era policy. An earlier search turned up ex-ante 2022 forecasts for Ukraine (Conference Board etc., via news sites) and a Barnichon counterfactual via news only; neither was verified, so neither is used.
