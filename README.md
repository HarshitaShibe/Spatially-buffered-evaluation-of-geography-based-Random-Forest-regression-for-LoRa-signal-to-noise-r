# Spatially buffered evaluation of geography-based Random Forest SNR prediction for LoRa links

Course research project for topic 5: *RF Prediction: regression models to predict Signal-to-Noise Ratio and channel
modelling for RF communication systems*. 

**Question.** Random Forest models that use position (x, y, bearing) predict LoRa SNR better than distance-only
models. Is that gain real generalisation to new places, or spatial leakage (test points sitting next to training
points)? We test it by holding out 250 m blocks and removing all training locations within a buffer *b* of the
test block, then measuring how much of the location advantage survives.

**Data.** Azevedo and Mendonça, *A Large-Scale LoRa Measurement Campaign in Urban and Suburban Environments*,
Mendeley Data, DOI [10.17632/79vh7wnwhg.1](https://doi.org/10.17632/79vh7wnwhg.1), CC BY 4.0.
- Funchal, Madeira: 3 gateways (GA, GB, GC), 1,203 fixed device locations, 8 packets per location.
- Radio settings: SF12, 125 kHz, 868 MHz.
- 37,029 received packets: 18,519 uplink and 18,510 downlink.
- Target: SNR (integer dB) of *received* packets, modelled per direction. Lost packets are never imputed.

---

## Main results

All results are verified. Source files are listed in `FINAL_STATUS.md`.

| | Result |
| --- | --- |
| **Buffer B\*** | 500 m, from the frozen correlogram rule. Residual correlation is **not** eliminated: the upper 95% CI reaches 0.226 at GC |
| **RF-loc RMSE, uplink** | 3.61 dB (random split) · 5.72 (250 m blocks) · 5.58 (LOBO 0 m) · 6.92 (LOBO 500 m) · 8.04 (LOBO 1,000 m). Within-location floor: 2.99 dB |
| **H1: location advantage at 500 m** | Δloc = RMSE(RF-loc) − RMSE(RF-dist) is −0.82 dB [−1.20, −0.46] uplink and −0.87 [−1.35, −0.42] downlink. It is about half the 0 m value but still present. Classification: **inconclusive** (δ = 0.5 dB). The result is **hyperparameter-sensitive**: leaf 5 gives −1.69 / −1.56 |
| **H2: distance non-linearity** | **Not supported.** RF-dist ≈ log-distance OLS under every grouped split, so the RF gain comes from location, not from a better distance curve |
| **H3: random-split optimism** | **Supported.** RMSE ordering R < L < S250 < S500, and every paired CI excludes 0 |
| **H4: error composition** | **Supported.** The floor's share of MSE falls from 0.35 (L) to 0.13–0.14 (LOBO 1,000 m) |
| **H5: weak links** | **Supported, descriptively.** At locations with only 1–2 received packets, SNR is over-predicted by +5.0 dB (uplink, S250) and +7.7 dB (uplink, LOBO 500 m) |
| **Per gateway** | The location advantage that remains at 500 m is concentrated at GC |
| **Channel model check** | The path-loss fit reproduces the dataset paper's Table 3 (α 42.7/54.8/44.0 dB, β 2.79/2.37/2.93) |

---

## Quick start

```bash
pip install -r requirements.txt
```

**A. Show the results without retraining (about 2 min).** This needs `predictions/`; see [Predictions and archive](#predictions-and-archive-not-in-git).

```bash
python 06_check.py               # integrity checks      -> "OK: 44 prediction files checked ..."
python tools/verify_results.py   # independent recompute -> "0 failure(s)"
python 07_analysis.py            # all statistics and the H1 verdict, from saved predictions
python 05_summarise.py           # Tables 1-6 and Figures 1-4
```

Or open `demo.ipynb` in Jupyter and choose **Kernel → Restart & Run All**. It runs the commands above and shows
the tables and figures. It then trains the models live on a 12-block subset (about 2–3 min).

**B. Full rerun from the raw CSVs (about 3–4 h on 2 cores).**

```bash
bash run_all.sh
```

On Windows without bash, run the commands in `run_all.sh` one by one, in the same order.

---

## Pipeline

```
data/raw (6 CSVs)
   │
01_validate ─► 02_splits ─► 03_eda ─► 08_freeze_checks
                                            │
                     04_evaluate --smoke ─► 04_evaluate ─► 04_evaluate --r1-base
                                                                  │
                                         04a_calibrate  (chooses buffer B*, BEFORE any buffered run)
                                                                  │
                                         04b_buffered main | r1 | r2 | r6
                                                                  │
                                    07_analysis ─► 06_check ─► 05_summarise ─► 09_pathloss_reproduction
                                                                  │
                                                     tools/verify_results.py
```

Each stage reads only earlier outputs and writes its own outputs to disk, so every number can be traced to a file.

---

## What each file does

### Pipeline scripts (in run order)

| File | What it does | Main outputs |
| --- | --- | --- |
| `common.py` | Shared helpers. Holds the folder paths and the global seed (`SEED = 20251028`). Holds the canonical column names, which fix two header quirks in the raw files. Holds the documented link parameters (SF, Tx power, frequencies, antenna heights). Also provides the raw-file reader, haversine distance, gateway-to-device bearing and a local x/y projection in metres | — (imported by every script) |
| `models.py` | **Model definitions.** Feature sets: `FEAT_DIST` is log10 d + gateway; `FEAT_LOC` adds sin/cos bearing and x, y. Models: M0 `mean`, M1 `logdist` (per-gateway OLS of SNR on log10 d), M2 `rf_dist`, M3 `lr_loc`, M4 `rf_loc`, plus the appendix models. `tune_rf` is the inner grouped 3-fold search over leaf {5, 20, 50} × max_features {0.5, 1.0}, with 200 trees. RSSI is never an input, except in the `rf_C` diagnostic | — (imported by 04, 04a, 04b) |
| `01_validate.py` | Loads the six raw files and runs hard schema and consistency asserts. Builds the tidy tables | `data/processed/packets.csv`, `locations.csv`, `sites.csv`, `gateways.csv`, `results/validation_report.*` |
| `02_splits.py` | Assigns folds **once**, per location. Schemes: R (random packets), L (by location), S250 and S500 (250 / 500 m grid blocks). Adds shifted grids and seeds for R1, and 1,000 m blocks for the bootstrap. Builds the leave-one-block-out buffer masks for b = 0 / 300 / 500 / 1,000 m, and asserts every kept training location is ≥ b from the test block | `splits/location_folds.csv`, `packet_folds_R.csv`, `lobo_excluded.csv`, `split_summary.json` |
| `03_eda.py` | Descriptive exploration on the whole dataset: SNR vs distance, packet loss, within-location variability, SNR saturation vs RSSI. **Not** evaluation results | `results/eda/*.csv`, `figures/eda_*.png` |
| `08_freeze_checks.py` | Feasibility checks before the protocol was frozen. Uses only geometry and packet counts: no SNR values, no model fitting. U1: training data and distance support left at each buffer. U2: number of bootstrap blocks | `results/freeze_checks/*` |
| `04_evaluate.py` | Grouped evaluation for R, L, S250 and S500, with 5 outer folds per direction. Tunes `rf_dist` and `rf_loc` **separately** inside each training fold. Then derives the fixed hyperparameters for the buffered runs (the modal S250 choice) and runs the R1 grid/seed variants. Flags: `--smoke` checks the code reproduces the archived predictions; `--r1-base` runs the fixed-hyperparameter base grid | `predictions/oof_<dir>_<scheme>.csv`, `results/eval/hp_fixed.json`, `chosen_hyperparameters*.csv`, `smoke_test.json` |
| `04a_calibrate.py` | **Chooses the buffer B\*** before any buffered result exists; it refuses to run if one does. Builds a correlogram of RF-dist residuals with a 500 m block bootstrap. Frozen rule: B\* is the smallest b in {300, 500} whose upper 95% CI is < 0.1 | `results/calibration/correlogram.csv`, `buffer_choice.json` |
| `04b_buffered.py` | **Buffered leave-one-250m-block-out.** Each block is tested once, and training locations within b m are removed. Each row records `sep_m` (distance to the nearest training location) and `supported` (distance support). Stages: `main` (b = 0/300/500/1,000), `r1` (shifted grid), `r2` (size-matched thinning), `r6` (leaf 5 / 50) | `predictions/oof_<dir>_LOBO_B<b>.csv`, `_R1_LOBO_o1_*`, `_R2_thin*`, `_R6_leaf*` |
| `07_analysis.py` | **All statistics**, from saved predictions only (no refitting). Uncertainty: paired spatial block bootstrap, 2,000 replicates, 500 m blocks (1,000 m as sensitivity). Covers P1 (RMSE by scheme), P2 (error vs separation), P3 (paired gains and the **H1 verdict**) and P4 (floor decomposition). Also robustness R1–R7 and the appendix models | `results/analysis/*.csv`, `h1_verdict.json`, `analysis_summary.md` |
| `06_check.py` | Integrity checks on every prediction file. Full packet coverage; no location in two folds; buffers hold (`sep_m ≥ b`). Same test packets across buffered runs; separate tuning. B\* written before the first buffered file; RMSE reproduces from the predictions | `logs/06_check.log` |
| `05_summarise.py` | Turns `results/analysis` into report tables and figures. Changes no number | `results/summary/table1…table6*.csv`, `summary.md`, `figures/fig1–fig4*.png` |
| `09_pathloss_reproduction.py` | **Channel-modelling check.** Effective signal power (ESP), then path loss, then a floating-intercept log-distance fit per gateway, following Azevedo & Mendonça (2026). The result is compared with their Table 3 and coverage figures, which validates our data handling | `results/pathloss/*` |
| `run_all.sh` | Runs every stage above in the correct order and writes one log per stage | `logs/*.log` |

### Verification and tools

| File | What it does |
| --- | --- |
| `tools/verify_results.py` | Recomputes the key numbers with code **separate from `07_analysis.py`**. Checks: RMSE; H1 Δloc with its own bootstrap; the B1000 subset; CI ordering; the floor; buffer distances; the R1 and pairing rules. Exits non-zero on any failure. Output: `results/verification/verification_report.md` |
| `tools/make_manifest.py` | Packaging helper. Writes `MANIFEST.csv` (path, size, SHA-256, provenance class) for a snapshot. Not a pipeline stage |
| `demo.ipynb` | Presentation notebook. Runs the checks and the recompute, shows the results tables, figures and path loss, then trains live on 12 uplink blocks at 0 m and 500 m buffers |
| `requirements.txt` | Pinned library versions (Python 3.13) |
| `.gitignore` | Keeps `predictions/`, `archive/`, caches and zips out of git |

### Documentation

| File | What it is |
| --- | --- |
| `FINAL_STATUS.md` | **Start here for results.** Every verified number with its source file, the stage execution table and 10 limitations |
| `CODE_WALKTHROUGH.md` | The six code places to show in a review (file:line), and how correctness is checked |
| `literature_review.md` | Literature review: 25 verified references grouped by theme, and the research gap |
| `references_verified.bib` | BibTeX for those 25 references, with the verification level of each |
| `docs/PROTOCOL_FREEZE_rev46.md` | The frozen protocol, written before results: models, splits, the B\* rule, hypotheses H1–H5, δ and the robustness checks |
| `docs/PROTOCOL_AMENDMENTS_2026-10-28.md` | Dated amendments A1–A6, all written before any buffered or analysis result existed |
| `docs/DECISION_LOG.md` | Open decisions D1–D5 and how each was resolved |
| `docs/ENVIRONMENT.md` | OS, Python and library versions, every random seed, and the full `pip freeze` |
| `STATUS.md` | Older execution snapshot (28 Oct, 00:46 UTC). Superseded by `FINAL_STATUS.md`, kept for the record |
| `PROVISIONAL_STATUS.md` | Status of the pre-freeze provisional outputs (`results/audit/`, `results/eda/`) |

### Data and output folders

| Folder | Contents |
| --- | --- |
| `data/raw/` | The six original CSVs (`GA/GB/GC_Uplink/Downlink.csv`), unmodified |
| `data/processed/` | Tidy tables from `01_validate`: packets, per-location counts, sites, gateways |
| `splits/` | Fold assignment per location, random packet folds and buffer exclusion lists |
| `predictions/` | *(not in git)* 44 files of out-of-fold predictions: every model for every packet, per scheme |
| `results/eval/` | Hyperparameters chosen per fold, the fixed hyperparameters, the smoke test and run info |
| `results/calibration/` | The correlogram and the B\* decision |
| `results/analysis/` | All primary, robustness and appendix tables, and the H1 verdict |
| `results/summary/` | Report Tables 1–6 (`table1`…`table6`) |
| `results/verification/` | Independent verification report |
| `results/pathloss/` | Path-loss reproduction vs the dataset paper |
| `results/freeze_checks/` | U1/U2 feasibility checks |
| `results/eda/`, `results/audit/` | Descriptive and provisional analyses from before the freeze (see `PROVISIONAL_STATUS.md`) |
| `figures/` | `fig1`–`fig4` (report figures) and `eda_*` (exploratory) |
| `logs/` | Console output of every stage run |
| `archive/` | *(not in git)* Untouched pre-freeze provisional outputs, with SHA-256 checksums |

Some files are **stale provisional files** from before the freeze:
- `results/eval/metrics*.csv`;
- `results/summary/table_main_S250.csv`, `table_by_gateway_S250.csv`, `table_location_level_S250.csv` and `table_split_inflation.csv`.

They are superseded by `results/analysis/` and `table1`–`table6`. Copies are in the archive.

---

## Design rules (pre-registered)

- **No target leakage.** Inputs are geometry and gateway only: no RSSI, ESP, timestamps or packet counts.
- **Tuning on training data only.** Inner CV is grouped by the same unit as the outer split.
- **Buffer chosen before results exist.** `04a` asserts that no buffered prediction exists; `06` checks the file timestamps.
- **Paired uncertainty.** The same bootstrap block draws are used for every model compared, so differences are paired.
- **H1 decision rule (95% CI of Δloc):**
  - inside (−0.5, 0.5) dB → no practical location advantage;
  - entirely below −0.5 dB → the advantage persists;
  - anything else → inconclusive.

  A general claim needs both directions to agree.
- **Wording.** Results are never called "spatially independent". We write "≥ b m from any training location" and give the residual correlation measured at that lag.

Full details: `docs/PROTOCOL_FREEZE_rev46.md` and `docs/PROTOCOL_AMENDMENTS_2026-10-28.md`.

## Limitations (short)

- One city, one spreading factor (SF12) and three gateways; frequency is confounded with gateway.
- Residual correlation is not eliminated at 500 m.
- H1 is hyperparameter-sensitive.
- Results apply to received packets only.
- Horizontal distance is used; the dataset paper corrects for antenna height.

The full list is in `FINAL_STATUS.md` §4.

## Predictions and archive (not in git)

`predictions/` (147 MB) and `archive/` are excluded by `.gitignore`. To run Quick start part **A** on a fresh clone:
1. Download `predictions.zip` from this repository's **Releases** page.
2. Unzip it into the project folder, so that `predictions/oof_*.csv` exists.

Or regenerate everything with `bash run_all.sh`.

## Citation and licence

- Dataset: Azevedo and Mendonça, Mendeley Data, DOI 10.17632/79vh7wnwhg.1, CC BY 4.0.
- Dataset paper: Azevedo and Mendonça, *IEEE Access*, 2026, doi:10.1109/ACCESS.2026.3730186.
- Code licence: to be added (e.g. MIT) after checking institution rules.
