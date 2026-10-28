#!/usr/bin/env bash
# Frozen-protocol pipeline (protocol-freeze doc, 28 Oct 2026). Requires: pandas, numpy, scikit-learn, xgboost, matplotlib.
# Order matters: 04a (B* calibration) must run before any 04b stage. Total runtime ~3-4 h on 2 cores.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p logs
for s in 01_validate 02_splits 03_eda 08_freeze_checks; do echo "== $s"; python3 "$s.py" 2>&1 | tee "logs/$s.log"; done
python3 04_evaluate.py --smoke 2>&1 | tee logs/04_smoke.log
python3 04_evaluate.py 2>&1 | tee logs/04_evaluate.log
python3 04_evaluate.py --r1-base 2>&1 | tee logs/04_r1_base.log   # D1: fixed-hp base-grid R1 member
python3 04a_calibrate.py 2>&1 | tee logs/04a_calibrate.log
for st in main r1 r2 r6; do python3 04b_buffered.py "$st" 2>&1 | tee "logs/04b_$st.log"; done
for s in 07_analysis 06_check 05_summarise 09_pathloss_reproduction; do echo "== $s"; python3 "$s.py" 2>&1 | tee "logs/$s.log"; done
