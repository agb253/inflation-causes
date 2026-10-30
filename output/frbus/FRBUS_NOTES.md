# Cross-check: the same causes through FRB/US (2026-10-29)

Code: `src/frbus/frbus_decomp.py` (method, mapping of each cause, settings in its docstring). Data and package:
`data/raw/frbus/` (PyFRB/US 1.1.1, LONGBASE Aug 2026; SOURCE.txt). Environment: PyFRB/US needs pandas < 3 and xlrd;
run with that environment from the project root. Logs: `output/frbus/frbus_run.log` (business aid as household income),
`frbus_run_none.log` (business aid left out). Tables: `frbus_causes_quarterly.csv`, `frbus_unemployment.csv`,
`frbus_vs_model.csv`.

## Result, 2021-24 totals (points of PCE inflation; four Q4 year-over-year values added)

| Cause | FRB/US | FRB/US, business aid left out | Our model | 2022Q2: FRB/US vs ours |
|---|---|---|---|---|
| Relief paid under Trump | +0.57 | +0.31 | +1.65 | 0.11 vs 0.47 |
| Relief paid under Biden | +0.35 | +0.25 | +2.06 | 0.06 vs 0.79 |
| Pent-up demand | +0.32 | | +1.21 | 0.05 vs 0.39 |
| Fed 2020-21 cuts + QE | +0.48 | | +0.84 | 0.12 vs 0.14 |
| Fed 2022-23 hikes | -0.30 | | -0.39 | 0.00 vs 0.00 |
| War in Ukraine | -0.03 | | +1.48 | 0.93 vs 1.13 |
| Supply chains (same direct shock) | +1.93 | | +4.21 | 1.78 vs 1.89 |
| FRB/US core-price residual (what its price equation can't explain) | +6.91 | | | 2.64 |
| FRB/US wage residual | +1.37 | | | 0.25 |

## Reading
- Peak supply effects agree (2022Q2 supply chains 1.8 vs 1.9, war 0.9 vs 1.1). Totals differ because FRB/US has
  little persistence: when energy and supply-chain pressure fell back, its inflation fell back too (war line negative
  2023Q2-2024Q4, supply chains negative 2023Q3-2024Q4).
- Demand: FRB/US gives relief 1/6 to 1/3 of our model's effect. Two parts of similar size: (1) a smaller unemployment
  effect (Biden-era relief peak -0.81 points of unemployment vs our -2.14; Trump-era -1.28 vs -2.71); (2) a flatter
  link from slack to inflation, measured by the unemployment gap (lur - lurnat) rather than job openings per unemployed.
- FRB/US explains little of the surge with its own equations: ~6.9 points of 2021-24 inflation sit in the core-price
  equation's tracking residual, 1.4 in the wage equation's (part of the core residual is the supply-chain effect, which
  FRB/US has no variable for; our direct shock 1.9 is the identified slice). So FRB/US does not show demand was small and
  something else large; it shows its unemployment-gap equations cannot account for 2021-22.
- Fed: FRB/US gives cuts+QE a larger unemployment effect (-0.88 vs our -0.38) but a smaller inflation effect.

## Limits
- Deterministic: no ranges.
- Mapping choices: business aid (PPP etc.) has no FRB/US channel (two variants shown); QE enters as an equivalent
  funds-rate cut via the SF Fed proxy rate; after each Fed window the funds rate returns to its actual path (our VAR
  lets it follow its usual response); pent-up demand pins nondurables+services consumption to actual minus the flow.
- No FRB/US counterpart for worker shortage, COVID shutdown drag, greedflation, pre-existing.
- FRB/US data vintage (Aug 2026) differs slightly from ours (2021Q4 PCE inflation 5.80 vs 5.73).
- PyFRB/US mcontrol did not converge for these targets; targets are hit by iterating each equation's add-factor
  (log-change equations, exact to 1e-9).
