# Madeira LoRa SNR pipeline: frozen protocol (28 Oct 2026)

The protocol is defined in the doc *Protocol Freeze: Spatially Validated LoRa SNR Prediction (Madeira)*.
The SNR protocol was frozen on 28 Oct 2026. Supervisor sign-off was waived by Harshita. Still open: U3 (the
Azevedo et al. full text), which affects only the contribution wording and the path-loss appendix.
Provisional outputs from before the freeze are kept unchanged in `archive/provisional_2026-10/`
(`SHA256SUMS.txt`, plus the scripts that produced them).

## Pre-registered rules (written before any frozen-protocol result existed)

- **Target:** SNR (integer dB) of *received* packets, per direction. Lost packets are never imputed, and no
  claim is made about all attempted transmissions.
- **Models:**
  - M0 `mean` (per gateway)
  - M1 `logdist` (per-gateway OLS of SNR on log10 d; empirical, *not* a path-loss model)
  - M2 `rf_dist` (log10 d + gateway)
  - M3 `lr_loc`
  - M4 `rf_loc` (log10 d, sin/cos bearing, x, y, gateway)
  - Appendix only: `xgb_loc`, `resrf_loc`, `rf_C` (same-packet RSSI).
- **Grouped schemes:** R, L, S250, S500, 5 folds each.
  - `rf_dist` and `rf_loc` are tuned separately by inner grouped 3-fold CV.
  - Grid: leaf {5, 20, 50} x max_features {0.5, 1.0}.
- **Buffered series:** leave-one-250m-block-out, with training locations closer than b to any test location removed.
  - Buffers: b in {0, 300, 500, 1000} m.
  - Fixed hyperparameters: the modal S250 choice per model and direction, ties going to the larger leaf.
  - The scattered-fold buffer was rejected by `08_freeze_checks.py`.
- **B\* rule:** the smallest b in {300, 500} m whose upper 95% CI of `rf_dist` L-split residual correlation is below 0.1.
  - The test uses the lag bin starting at b, and must hold for all 6 gateway x direction series.
  - If no b qualifies, B\* = 500 m and the correlation is reported as not eliminated.
  - 1,000 m is never primary, because it keeps < 50% of training data for some blocks.
  - B\* is recorded by `04a_calibrate.py` before `04b` runs (asserted in `06_check.py`).
- **Primary test (H1):** Δloc = RMSE(`rf_loc`) − RMSE(`rf_dist`) on LOBO-B\*, per direction.
  - Uses a paired block bootstrap: 2,000 replicates, 500 m blocks (U2), with 1,000 m as sensitivity.
  - δ = 0.5 dB. The 95% CI inside (−δ, δ) means "no practically relevant location advantage".
  - A CI entirely below −δ means "a practically relevant location advantage persists". Anything else is inconclusive.
  - A general claim requires both directions to agree.
- **Robustness:**
  - R1: grid offsets and seeds.
  - R2: size-matched thinning, 3 repeats.
  - R3: distance-supported points (|Δlog10 d| ≤ 0.1).
  - R4: location weighting.
  - R5: reception and valid-packet strata.
  - R6: leaf 5 and 50 at B\*; a change of more than 0.25 dB in Δloc is flagged as hyperparameter-sensitive.
  - R7: by gateway and distance band.
- **Wording:** never "spatially independent". Write "≥ b m from any training location", and give the
  residual correlation measured at that lag.

## Run order

For what has actually been executed and verified, and the commands for the remaining stages only, see `STATUS.md` (and `MANIFEST.csv` in a packaged snapshot).


See `run_all.sh`:

`01_validate` → `02_splits` → `03_eda` → `08_freeze_checks` → `04_evaluate --smoke` → `04_evaluate` → `04_evaluate --r1-base` →
`04a_calibrate` → `04b_buffered main|r1|r2|r6` → `07_analysis` → `06_check` → `05_summarise`.

## Data

`data/raw/` holds unmodified copies of the six files from *A Large-Scale LoRa Measurement Campaign in Urban and
Suburban Environments*, Azevedo and Mendonça, Mendeley Data, DOI 10.17632/79vh7wnwhg.1, CC BY 4.0.

Known header quirks, handled in `common.py`:

- `GB_Uplink` and `GC_Uplink` read `RSSI1;RSSI1`.
- `GC_Downlink` reads `Latitude_Gc`.

Link parameters (SF12, 125 kHz, 14 dBm, 868.1/868.3/868.5 MHz) come from the dataset page, not from the files.

## Outputs

| Path | Content |
| --- | --- |
| `results/freeze_checks/` | U1/U2 feasibility (no model fitting) |
| `results/eval/` | Hyperparameter record, fixed hyperparameters, smoke test, run info |
| `results/calibration/` | Correlogram with CIs; `buffer_choice.json` (B\*) |
| `predictions/oof_<dir>_<scheme>.csv` | Out-of-fold prediction of every model for every packet |
| `results/analysis/` | P1–P4, H1 verdict, R1–R7, appendix |
| `results/summary/`, `figures/fig*.png` | Report tables and figures |

## Predictions and archive (not in git)

`predictions/` (147 MB, 44 files) and `archive/` (provisional pre-freeze outputs) are excluded by `.gitignore`.
To run `demo.ipynb`, `06_check.py`, `07_analysis.py` or `tools/verify_results.py` on a fresh clone, either download
`predictions.zip` from this repository's Releases page and unzip it into the project folder, or regenerate everything
with `bash run_all.sh` (about 3-4 h on 2 cores).
