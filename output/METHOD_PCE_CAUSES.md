# fig11: causes of PCE inflation by quarter, 2020–2024

Chart: `output/fig11_pce_causes.png`. Table: `output/pce_causes_quarterly.csv` (with bands). Profits: `output/unit_profits_quarterly.csv`.

## What it can't show (read first)

- **Panel A labels price changes; it doesn't prove causes.** "Supply-driven" means a category's price rose more than expected while its quantity fell. The cause names attached to those buckets (war, COVID supply chains, staff shortages) are our reading of which categories and months they cover.
- **The demand line can't be split among the Trump-signed laws, the Biden-signed laws, the Fed and reopening from this data.** Panel B shows what outside studies estimate. Those estimates don't fit inside the measured demand line: in 2021 the fiscal study alone exceeds it, and the Fed study's counterfactual is rates held at zero. They're shown for size and timing, not added.
- **Greedflation (panel C) is an accounting split, not a cause.** It shows how much of corporate prices ended up as profit. Profit rises when shortages let firms charge more, so it overlaps the supply and demand lines and can't be added to them.
- **Not separated:** international pressures (inside the supply lines), quantitative easing, tariffs, other policies, and the student-loan pause.
- **This is PCE, not CPI.** PCE is the Fed's preferred index.

## Panel A: why it adds up

PCE inflation is the spending-weighted sum of its categories' price changes. Each category in each month carries the SF Fed supply/demand label (`output/METHOD_SUPPLY_DEMAND.md`; our recomputation matches the SF Fed's published series at correlation 0.99). Each category-month is then given to exactly one cause:

| Line | Category-months assigned |
|---|---|
| War in Ukraine | food & energy, supply-driven, Jan 2022 – Mar 2023 |
| Other food & energy supply shocks | food & energy, supply-driven, any other month |
| COVID supply chains: goods | goods other than food & energy, supply-driven |
| Supply limits in services | services other than housing & energy, supply-driven |
| Housing | rent and owners' equivalent rent (BEA lines 153–164), any label |
| Demand | demand-driven, everything except housing |
| Too small to label | ambiguous |
| Pre-existing inflation | the sum of every line's 2015–2019 average (1.24 points) |

Each line is shown minus its own 2015–2019 average. Those averages together form "pre-existing inflation", so the lines still add up to the total.
- **Check:** the sum of the lines matches BEA's official PCE inflation within 0.1 point in every quarter except 2020Q2–Q4, where the gap reaches 0.18. BEA chains its index with a Fisher formula, while the sum uses each category's previous-month spending share.
- **War window:** taken from fig9. Energy prices relative to wages (energy CPI / employment cost index) rose from 0 at 2021Q4 to +17.6% at 2022Q2 and were back to −1.5% at 2023Q1.
- **Food & energy months labeled demand-driven stay in the demand line.** That includes the 2020 energy crash, when people stopped driving, and some 2022 gasoline months. So the war line counts only the supply-labeled part.
- **Bands:** the range across four labeling variants: category detail at BEA level 4 or 5, times the paper's two descriptions of the "ambiguous" rule.

Key quarters (percentage points of year-over-year PCE inflation):

| | 2021Q2 | 2021Q4 | 2022Q2 | 2022Q4 | 2023Q2 | 2024Q4 |
|---|---|---|---|---|---|---|
| Pre-existing | 1.24 | 1.24 | 1.24 | 1.24 | 1.24 | 1.24 |
| Demand | 0.97 | 1.71 | 1.99 | 1.71 | 0.84 | 0.59 |
| COVID supply chains: goods | 0.34 | 0.74 | 0.83 | 0.64 | 0.36 | 0.02 |
| War in Ukraine | 0 | 0 | 0.48 | 0.67 | 0.20 | 0 |
| Other food & energy supply | 0.46 | 0.66 | 0.64 | 0.27 | 0.21 | 0.20 |
| Services supply limits | −0.26 | 0.01 | 0.65 | 0.65 | 0.42 | 0.04 |
| Housing | −0.15 | 0.02 | 0.27 | 0.58 | 0.69 | 0.24 |
| Too small to label | 1.25 | 1.20 | 0.55 | 0.06 | −0.13 | 0.12 |
| **Sum** | 3.85 | 5.59 | 6.66 | 5.83 | 3.84 | 2.46 |
| **Official PCE inflation** | 3.85 | 5.57 | 6.65 | 5.89 | 3.91 | 2.48 |

## Panel B: published policy estimates

Taken unchanged from fig9 (`output/separate_causes_yoy.csv`). Sources and quotes: `output/CAUSES_SOURCES.md` and `output/METHODS_quarterly.md`.
- **Relief laws:** the SF Fed Economic Letter 2022-07 model, re-run on the authors' data (`src/fiscal_sf_replication.py`). Each quarter's effect is split by when the excess federal transfer money was paid: March 2020 – February 2021 is Trump-signed (CARES Act, the December 2020 act), March 2021 on is Biden-signed (American Rescue Plan). Measured in core CPI.
- **Fed:** Chicago Fed Letter 483, Figure 2F, digitized. The counterfactual is rates held at zero through 2023Q3. Measured in CPI.

## Panel C: profit's share of prices

BEA NIPA Table 1.15, from the quarterly flat file `data/raw/bea/NipaDataQ.txt` (downloaded 2026-10-17). The identity price = unit labor cost + unit nonlabor cost + unit profit holds within 0.001 (`src/build_unit_profits.py`).
- **The level:** unit profits as a share of price averaged 13.4% in 2015–2019. They rose to about 17.5% in 2021 and stayed at 17–18.5% through 2024, the highest annual level since at least 1995 in this data.
- **What it supports:** margins rose during the shortage period and did not come back down after supply chains normalized.
- **What it doesn't say:** why. A share that stays high fits firms using the moment to raise margins, but this data alone can't rule out other explanations.

## Rerun

```
python src/replicate_sf_supply_demand.py 4 t      # and: 4 pct, 5 t, 5 pct (for the bands)
python src/build_pce_causes.py
python src/build_unit_profits.py
python src/make_pce_causes_figure.py
```
