# Supply-driven vs demand-driven inflation: method, data, and check

**Use this as the single measure of supply disruptions.** It's the San Francisco Fed's published series. We recomputed it from raw government data using their published equations, and our numbers track theirs closely (see "Check" below). Anyone can rerun it.

## What it can't show (read first)

- **"Supply-driven" is every supply shock, not only COVID supply chains.** It also includes the energy and food spike from the war in Ukraine, and any other month a category's price rose while its quantity fell. The food-and-energy share is split out in the table, but that split is ours, not the SF Fed's.
- **It measures PCE inflation, not CPI.** PCE is the Fed's preferred index and comes from BEA. CPI comes from BLS, covers different goods and weights them differently, and ran higher than PCE at the 2022 peak. Don't put these numbers next to CPI without saying so.
- **Demand shifts caused by expected shortages count as demand.** The paper says: "An increase in demand due to anticipated supply changes (e.g., consumer hoarding) would be labeled demand-driven."
- **It labels each category's price change. It doesn't say why** prices changed, so it can't tell a supply shock from a firm raising margins.

## Source

Adam Hale Shapiro, "A Simple Framework to Monitor Inflation," Federal Reserve Bank of San Francisco Working Paper 2020-29 (June 2022), section 6. Saved at `data/raw/sf_fed/paper/wp2020-29.pdf` from https://www.frbsf.org/wp-content/uploads/wp2020-29.pdf. Published series: https://www.frbsf.org/research-and-insights/data-and-indicators/supply-and-demand-driven-pce-inflation/ (file `data/raw/sf_fed/supply-demand-pce-inflation.xlsx`).

## Data (all public, BEA)

Paper, section 2: "The price and quantity data used in this study are publicly available and come from the Bureau of Economic Analysis (BEA). The data on the underlying detail of quantity, price, and expenditures of the PCE index are availble in Tables 2.4.3U, 2.4.4U and 2.4.5U."

We used `data/raw/bea/Section2All_xls.xlsx`, downloaded 2026-10-17 from https://apps.bea.gov/national/Release/XLS/Underlying/Section2All_xls.xlsx (published September 30, 2026, monthly data through 2026M08). Categories are BEA's fourth level of detail, as in the paper. That gives 98 categories in today's tables, 92 of them outside food and energy. The paper counted 124 core categories in the BEA tables available in 2022, and BEA has reorganized those tables since then.

## Equations (copied from the paper, pp. 18–19)

> I run rolling 120-month window rolling regressions (i.e., t ∈ [T − 119, T]):
>
> p_i,t = Z_t−1 γ + ε^p_i,t   (20)
> q_i,t = Z_t−1 γ + ε^q_i,t   (21)
>
> where p_i,t is the log of the price index of category i in month t, q_i,t is the log of the quantity index of category i in month t, Z_t−1 is vector of variables available in month t-1 [...]
>
> My preferred specification includes 12 lags of the log price level and the log quantity level of category i. [...] For each regression, I collect the final month (i.e., month T) residual. It follows that category i in month T is labeled as supply-driven if ε^p_i,T and ε^q_i,T are off opposite signs and demand-driven if ε^p_i,T and ε^q_i,T are off the same signs.

In plain terms: for each category, predict this month's price and quantity from the past year, then look at the surprises.
- **Price up and quantity down** (or both reversed): the supply curve shifted, so the month is supply-driven.
- **Price and quantity up together** (or both down): the demand curve shifted, so the month is demand-driven.

> The demand- and supply-driven monthly contributions to inflation are constructed as the weighted sum of price changes for categories within a given label. The year-over-year contributions are constructed as the 12-month rolling sums of monthly contributions.

Weights are each category's share of spending in the previous month (Economic Letter 2022-15: "its most recent respective weight in the PCE index").

**Ambiguous.** The paper describes this rule two ways: as "the middle 20% of the residuals," and as residuals with "a t-statistic < 0.125." We tested both. The t-statistic reading, |surprise| < 0.125 × the standard deviation of pre-2020 surprises, matches the published ambiguous series more closely, so we used it. Both readings give nearly the same supply-driven series.

## Check: our recomputation vs the SF Fed's published numbers

Headline PCE, year over year, monthly 2000–2026 (`src/compare_sf_replication.py`):

| Series | Correlation | Average gap | June 2022: SF Fed | June 2022: ours |
|---|---|---|---|---|
| Supply-driven | 0.99 | 0.11 pts | 3.43 | 3.33 |
| Demand-driven | 0.99 | 0.09 pts | 2.76 | 2.79 |

The biggest disagreement is 2021Q1 to Q2: our supply-driven line runs about 0.4 to 0.5 points below theirs. Likely causes are BEA's category regrouping and the unclear ambiguous rule. From late 2021 on, the two agree within about 0.3 points.

**Correction, 2026-10-17:** the first version of this file reported a correlation of 0.91 and a gap of 0.25. That run had a bug: BEA indents the total-PCE line like a category, so the script counted total PCE as one of its own categories. Fixed in `src/replicate_sf_supply_demand.py`. All numbers here are from the corrected run. Chart: `output/fig10_supply_vs_demand_driven.png`.

## Result

`output/supply_disruption_quarterly.csv`. "Above normal" means minus the 2015–2019 average. The SF Fed's supply-driven contribution averaged 0.44 points in 2015–2019.

| Quarter | Total PCE (ours, quarter-end) | Supply-driven (SF Fed) | Above normal (SF Fed) | Ours, excl. food & energy, above normal | Ours, food & energy, above normal |
|---|---|---|---|---|---|
| 2021Q2 | 4.1 | 1.58 | 1.14 | 0.25 | 0.39 |
| 2021Q4 | 5.9 | 2.44 | 2.00 | 0.96 | 0.72 |
| 2022Q2 | 7.0 | 3.43 | 2.99 | 1.50 | 1.38 |
| 2022Q4 | 5.4 | 2.69 | 2.25 | 1.34 | 0.88 |
| 2023Q2 | 3.2 | 1.47 | 1.03 | 0.79 | 0.11 |
| 2023Q4 | 2.8 | 1.31 | 0.87 | 0.46 | 0.28 |
| 2024Q4 | 2.6 | 0.80 | 0.36 | 0.13 | 0.22 |

At the June 2022 peak, supply-driven inflation was about 3 points above normal: about 1.5 points outside food and energy and about 1.4 in food and energy (our split). That is just under half of the 7.0% total. Demand-driven inflation was about the same size.

## Rerun

```
python src/replicate_sf_supply_demand.py 4 t     # about 35 s
python src/compare_sf_replication.py 4t 4pct 5t
python src/make_supply_disruption_table.py
python src/make_supply_disruption_figure.py
```
