#!/bin/sh
# Extensions E1-E17 (src/extensions/, logs and CSVs in output/ext/). About 70 minutes. Run from the project root after
# run_report.sh's model step (src/unified_model.py), then rerun src/make_report.py.
set -e
PY=${PY:-python}
mkdir -p output/ext
for e in e01_kinked_phillips e02_category_panel e03_autos e04_supply_measures e05_states e06_relief_spending \
         e07_cross_country_quarterly e08_fed_alternatives e09_fed_credibility e10_industry_margins e11_out_of_sample \
         e13_wage_tracker e14_iija_ira e12_all_evidence e15_wages_ui_ranges e16_narrower e17_europe_panel; do
  $PY src/extensions/$e.py > output/ext/$e.log 2>&1
done
$PY src/make_unified_figure.py best                            # output/fig16_best_ranges.png (needs e16)
