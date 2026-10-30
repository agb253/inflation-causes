#!/bin/sh
# Rebuild every number and figure in output/REPORT.md from data/raw/ (about 6 minutes). Run from the project root.
set -e
python src/unified_model.py > output/unified_model_run.log   # causes by quarter, 1,000 redraws
python src/robustness.py      > output/robustness_run.log     # alternative choices
python src/fed_late_report.py > output/fed_late_run.log       # 'did the Fed act too late?'
python src/compare_studies.py > /dev/null                     # output/COMPARISON.md
python src/make_unified_figure.py && python src/make_report_figures.py && python src/make_unified_table.py
[ -f output/uncertainty_sources.csv ] || PY=python ./run_uncertainty.sh    # ~30 min; delete that file to rerun after model changes
python src/cross_country_relief.py > /dev/null && python src/combine_outside_evidence.py > output/combine_outside_evidence.log
python src/make_reproduce_table.py                             # output/REPRODUCE_TABLE.md, reproduce_long.csv
python src/make_report.py                                     # output/REPORT.md
