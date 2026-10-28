# Code walkthrough (for presenting the project)

The pipeline is about 1,800 lines of Python in 15 scripts. Each script is one stage, run in a fixed order, and
writes its outputs to disk, so every number can be traced back to a file. Line numbers refer to the files as shipped.

## Pipeline at a glance

```
raw CSVs ─► 01_validate ─► 02_splits ─► 04_evaluate ─► 04a_calibrate ─► 04b_buffered ─► 07_analysis ─► 05_summarise
 (6 files)   tidy packets   folds +      R/L/S250/S500   choose B*        leave-one-     metrics, CIs,   tables 1-6,
             + asserts      buffers      (tuned RF)      (correlogram)    block-out      H1 verdict      figs 1-4
                                                                          0-1000 m              │
                                                               06_check + tools/verify_results.py (integrity, independent recompute)
09_pathloss_reproduction: supporting channel model (reproduces Azevedo & Mendonça 2026, Table 3)
```

## Show these 6 places (about 10 minutes)

| # | What to show | File : lines | Point to make |
| --- | --- | --- | --- |
| 1 | **Models and predictors** | `models.py:19-24, 74-83` | Five regression models. `FEAT_DIST` = distance + gateway; `FEAT_LOC` adds bearing and x/y. No RSSI, ESP or SNR among the inputs, so there is no target leakage |
| 2 | **Tuning on training data only** | `models.py:57-72` (`inner_splits`, `tune_rf`) | Inner 3-fold CV is grouped by the same unit as the outer split and runs only on the outer training set |
| 3 | **Buffered leave-one-block-out** | `02_splits.py:98-107`; `04b_buffered.py:35-47, 56, 83-87` | Training locations within b m of any test location are removed. An `assert` proves the buffer holds, and a second `assert` checks no test location is in training. `annotate` adds the separation and distance-support flag |
| 4 | **Buffer chosen before results** | `04a_calibrate.py:17, 58-66` | The script refuses to run if buffered predictions exist. B\* comes from a frozen rule on the residual correlogram, and the result is written with a timestamp |
| 5 | **Paired spatial block bootstrap** | `07_analysis.py:42-72` (`boot_rmse_matrix`, `paired`) | The same block resample (500 m blocks, 2,000 replicates) is used for both models, so differences are paired. Vectorised as a count matrix |
| 6 | **Pre-registered H1 decision** | `07_analysis.py:117-158` (`classify`, verdict) | CI inside ±0.5 dB → "no practical advantage"; CI below −0.5 → "persists"; otherwise "inconclusive". The residual correlation at B\* is reported alongside |

## How correctness is checked

| Check | Where | What it proves |
| --- | --- | --- |
| Smoke test | `04_evaluate.py --smoke` (line 55) | New code reproduces the archived predictions (max diff 5.3e-15) |
| Integrity checks | `06_check.py` | 44 prediction files: full packet coverage, no fold crossing, buffers hold, B\* written before buffered runs, metrics reproduce |
| Independent recompute | `tools/verify_results.py` | Recomputes RMSE, H1 and the B1000 subset with separate code and its own bootstrap; **0 failures** |
| External reproduction | `09_pathloss_reproduction.py` | Matches the dataset paper's path-loss Table 3 (α, β, RMSE) |

## Live demo commands (fast, no training)

```
python 06_check.py                 # ~20 s, ends with "OK: 44 prediction files checked ..."
python tools/verify_results.py     # ~1 min, ends with "0 failure(s)"
python 07_analysis.py              # ~20 s, recomputes all tables and the H1 verdict from saved predictions
python 05_summarise.py             # ~2 s, regenerates Tables 1-6 and Figures 1-4
```

Full rerun from raw data: `bash run_all.sh` (about 3–4 h on 2 cores). On Windows, use the stage-by-stage commands in `README.md`.

## Where the results are

- `results/summary/table1_rmse_by_scheme.csv` … `table6_residual_correlation_at_Bstar.csv`
- `results/analysis/h1_verdict.json`
- `figures/fig1`–`fig4`
- `FINAL_STATUS.md` (summary of every result, with file references)
