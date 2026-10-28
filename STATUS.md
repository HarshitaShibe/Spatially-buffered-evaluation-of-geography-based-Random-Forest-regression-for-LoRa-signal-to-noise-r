# Execution status: snapshot of 28 Oct 2026, 00:46 UTC (superseded by FINAL_STATUS.md)

This file separates what was **implemented** (code exists), **executed** (ran on the real data and finished), and
**verified** (outputs checked by an independent assertion or an external reference). No final results are
reported here, and none have been computed yet. Every file in this snapshot is listed with its SHA-256 and
provenance class in `MANIFEST.csv`.

## Stage-by-stage status

| Stage | Script | Implemented | Executed on real data | Verified | Notes |
| --- | --- | --- | --- | --- | --- |
| 01 Validate + tidy | `01_validate.py` | Yes (unchanged since 27 Oct) | Yes, 27 Oct 19:30 UTC | Yes: hard asserts in script; location coverage 62.0/95.8/83.5% matches Azevedo & Mendonça (2026) | Not rerun for the frozen protocol; its outputs are unchanged inputs |
| 02 Splits | `02_splits.py` | Yes (extended 28 Oct) | Yes, 28 Oct 00:11 UTC | Yes: original fold columns identical to the archived copy; buffer-distance asserts passed for every block and buffer | Adds LOBO masks, grid-offset/seed folds, 1,000 m blocks |
| 03 EDA | `03_eda.py` | Yes (unchanged) | Yes, 27 Oct (provisional run) | Descriptive only | `rssi_pathloss_fit.csv` withdrawn (see `PROVISIONAL_STATUS.md`) |
| 08 Freeze checks (U1/U2) | `08_freeze_checks.py` | Yes | Yes, 28 Oct 00:07 UTC | Used to close U1/U2; no model fitted, no SNR used | |
| 04 Smoke test (C7) | `04_evaluate.py --smoke` | Yes | Yes, 28 Oct 00:15 UTC | **Passed**: max abs. difference to the archived `rf_A` = 5.3e-15 (`results/eval/smoke_test.json`) | |
| 04 Grouped evaluation | `04_evaluate.py` | Yes | **Yes, finished 28 Oct 00:45 UTC** (1,772 s, exit 0) | Integrity only (see below); no metrics computed yet | R, L, S250, S500 + 7 R1 S250 offset/seed variants per direction; `hp_fixed.json` written |
| 04a Calibration (C8) | `04a_calibrate.py` | Yes | **No** | Dry run only (scratch copy, surrogate residuals from the archived `rf_A0`, 20 bootstraps): runs without error | The queued automatic run was cancelled on 28 Oct, so it can be verified first |
| 04b Buffered series | `04b_buffered.py main\|r1\|r2\|r6` | Yes | **No** | Dry run only (2 blocks, 10 trees, surrogate hyperparameters and B\*): all four stages ran; sep_m ≥ b held | Needs 04a first (asserted) |
| 07 Analysis | `07_analysis.py` | Yes | **No** | **Not tested at all** (needs 04a + 04b outputs) | Highest risk of a runtime bug |
| 06 Integrity checks | `06_check.py` (new) | Yes | **No** | Not tested | `logs/06_check.log` is from the old provisional 06 |
| 05 Summary tables/figures | `05_summarise.py` (new) | Yes | **No** | Not tested | `results/summary/*` and `logs/05_summarise.log` are provisional |
| 09 Path-loss reproduction | `09_pathloss_reproduction.py` | Yes | Yes, 28 Oct 00:26 UTC | **Yes**: reproduces Azevedo & Mendonça (2026) Table 3 (α within 0.4 dB, β within 0.01, RMSE identical to 0.1 dB) | Supporting analysis |
| Provisional cheap audit | `archive/provisional_2026-10/scripts/07_audit_cheap.py` | Archived | Yes, 27 Oct 23:51 UTC | Was verified at the time | Superseded; would fail on new prediction formats, so it is no longer run |

**Stage-04 integrity check, run on 28 Oct without refitting.** All 22 prediction files contain exactly the
direction's packets (18,519 uplink / 18,510 downlink), with no missing primary predictions. Fold labels match
`splits/location_folds.csv` for L, S250, S500 and all R1 variants, and no location appears in two folds.
`rf_loc` is constant within each location × gateway under grouped splits. `chosen_hyperparameters.csv` has 40
tuned grouped fold rows with separate `rf_dist`/`rf_loc` inner RMSE. Fixed hyperparameters (modal S250 choice)
are the same in both directions: `rf_dist` leaf 50 / max_features 1.0, `rf_loc` leaf 20 / max_features 0.5.

## Stale files still in the working tree (kept, labelled, not deleted)

Identical copies are in `archive/provisional_2026-10/` (SHA256SUMS.txt):

- `results/eval/metrics.csv`, `metrics_by_gateway.csv`, `metrics_location_level.csv`: provisional. The frozen 04 no longer writes metrics; 07 replaces them.
- `results/summary/*`, `logs/05_summarise.log`, `logs/06_check.log`: provisional; replaced when the new 05/06 run.
- `results/audit/*`, `results/eda/*`, `figures/eda_*`: provisional analyses kept for the record.

## Implementation vs frozen protocol: points to verify

These are places where the code makes a choice the protocol text does not fix, or where the protocol text is
internally inconsistent. Nothing has been changed silently; each needs your accept/reject.

1. **R1 S250 offset/seed variants use fixed hyperparameters** (modal S250 choice), not inner tuning. The protocol says only "4 grid offsets × 2 seeds". In 07, the R1 spread compares the tuned S250 run with fixed-hyperparameter variants, so it mixes grid effects with tuning effects.
2. **The buffered series lives in `04b_buffered.py`**, not in `04_evaluate.py` as protocol §10 lists. Same content, different file.
3. **Protocol §5, first table row** still says buffered inner folds are grouped by 250 m blocks. The row below it (fixed hyperparameters, no inner CV) is what is implemented.
4. **Protocol §6** lists "scheme vs S250" pairing; **§7 P1** says buffered schemes are paired against LOBO-B0. The code follows §7 and also reports S250 and L against LOBO-B0 (`P1b_scheme_vs_LOBO_B0.csv`).
5. **P2 for LOBO-B1000:** the protocol says "on distance-supported points". 07 bins B1000 on all points in P2 and reports supported-only RMSE separately in P1 (`RMSE_supported`).
6. **Correlogram estimator (04a):** location-mean residuals include within-location packet noise, which attenuates correlations. It is the same estimator as the provisional audit, but it makes the "< 0.1" rule somewhat lenient. Not stated in the protocol.
7. **Distance:** predictors use horizontal distance; the dataset paper uses antenna-height-corrected distance (recorded deviation, protocol §1).
8. **Protocol doc status cells are out of date** and were not edited, at your instruction:
    - C2 is partly done (one web search).
    - C6 is done (README).
    - C7 is partly done (smoke test passed; new 06 asserts not yet run).
    - C9 is done (archive + checksums).
    - U3's "Basis" cell still reads "Needs the Azevedo PDF".

## How `run_all.sh` relates to the pipeline

The `run_all.sh` in the earlier zip (`madeira_snr_pipeline_provisional.zip`) ran only the provisional stages
01 → 07 (validate, splits, EDA, evaluate, summarise, check, cheap audit). The current `run_all.sh` was rewritten
on 28 Oct and lists the **full frozen pipeline in protocol order**: 01, 02, 03, 08, 04 --smoke, 04, 04a, 04b
main/r1/r2/r6, 07, 06, 05, 09.

It has **never been executed as a whole**. Every stage so far was run individually. Running it now would redo
the completed stages 01–04 (about 35 min, deterministic, overwriting current non-archived outputs with
identical content) before reaching the missing ones. **To execute only the missing stages, do not use `run_all.sh`; run:**

```
python3 04a_calibrate.py            # ~5 min; writes results/calibration/buffer_choice.json (B*) - must precede 04b
python3 04b_buffered.py main        # ~70 min; LOBO B0/B300/B500/B1000, models M0-M4
python3 04b_buffered.py r1          # ~18 min; LOBO at B* on the 125 m-shifted grid
python3 04b_buffered.py r2          # ~50 min; size-matched thinning, 3 repeats
python3 04b_buffered.py r6          # ~35 min; leaf 5 and 50 at B*
python3 07_analysis.py              # minutes; P1-P4, H1 verdict, R1-R7, appendix
python3 06_check.py                 # integrity checks of everything above
python3 05_summarise.py             # report tables and figures
```

Runtimes are estimates for 2 cores. Each long command should run under `nohup` or in the background, with
output tee'd to `logs/<stage>.log`.

## Archive

`archive/provisional_2026-10/` holds the provisional `results/`, `predictions/`, `splits/`, figures and the
scripts that produced them, with `SHA256SUMS.txt` (43 data files; its own line is a self-reference that cannot match) and `SHA256SUMS_scripts_figures.txt` (scripts and figures archived shortly after). All checksums verified on 28 Oct about 00:45 UTC; nothing in it has been modified.
