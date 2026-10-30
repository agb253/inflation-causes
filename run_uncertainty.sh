#!/bin/bash
# Uncertainty diagnostics (about 30 minutes). Run from project root after src/unified_model.py.
PY=${PY:-python}
set -e
$PY src/uncertainty/sources.py 150 output/uncertainty_sources.csv > output/uncertainty_sources.log 2>&1
$PY src/uncertainty/condition_on_2020_24.py 600 > output/uncertainty_condition.log 2>&1
$PY src/uncertainty/extend_sample.py > output/uncertainty_extend_sample.log 2>&1
$PY src/uncertainty/relief_scale_fit.py > output/uncertainty_relief_scale.log 2>&1
$PY src/uncertainty/gscpi_coef.py > output/uncertainty_coefs.log 2>&1
