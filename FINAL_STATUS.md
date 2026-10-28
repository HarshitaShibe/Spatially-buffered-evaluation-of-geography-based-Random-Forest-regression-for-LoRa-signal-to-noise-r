# Final status: experiments, analysis and verification complete (28 Oct 2026)

Every number below was copied from the listed output files. No paper sections (abstract, introduction,
discussion, conclusion) have been written. The target throughout is **received-packet SNR (dB)**, so nothing
here describes lost packets.

## 1. Stages

| Stage | Executed | Verified by |
| --- | --- | --- |
| 01 validate, 03 EDA | 27 Oct (unchanged inputs) | Hard asserts; location coverage matches Azevedo & Mendonça (2026) |
| 02 splits (LOBO masks, grid offsets, 1,000 m blocks) | 28 Oct | Original folds identical to the archive; buffer-distance asserts |
| 08 freeze checks (U1/U2) | 28 Oct | No model fitting |
| 04 smoke test | 28 Oct | Reproduces archived predictions (max diff 5.3e-15) |
| 04 grouped schemes + R1 S250 variants | 28 Oct, 1,772 s | Integrity check; 06 |
| 04 `--r1-base` (fixed-hp base grid, amendment A1) | 28 Oct, 22 s | 06 (R1 family complete, folds match) |
| 04a calibration | 28 Oct, written 01:02:49 UTC | 06: written before the first LOBO file |
| 04b main / r1 / r2 / r6 | 2,397 s / 629 s / 1,830 s / 1,397 s | 06; integrity check (supported share matches freeze checks) |
| 07 analysis | 18 s | `tools/verify_results.py`: **0 failures** |
| 06 integrity checks | 22 s | "OK: 44 prediction files checked …" (`logs/06_check.log`) |
| 06 portability fix (28 Oct, after GitHub push) | — | Check 7 originally compared live file times, and git does not keep file times, so it failed on any fresh clone. It now uses `results/calibration/run_order_record.json` (original times: B\* 01:02:55 UTC, first buffered file 01:08:39 UTC) after a SHA-256 match. Tested: passes in the original folder and on a fresh clone; fails if `buffer_choice.json` is altered. No result changed |
| 05 tables and figures | 2 s | Figures inspected |
| 09 path-loss reproduction | 28 Oct | Matches the dataset paper's Table 3 |
| Literature review | 28 Oct | 25 entries verified (`literature_review.md`, `references_verified.bib`) |

Pre-run validation: 07/06/05 were dry-run on surrogate data in a scratch copy, and two genuine defects were fixed
(figure-label collisions, and a verifier tolerance smaller than the CSV rounding). Protocol conflicts were resolved
by `docs/PROTOCOL_AMENDMENTS_2026-10-28.md`, written before any buffered or analysis result existed.

## 2. Verified results

**Calibration (frozen rule).** B\* = 500 m, `correlation_not_eliminated = true`.
- In the [500, 1000) m bin the residual-correlation estimates are −0.04 to 0.09.
- The upper 95% bounds reach 0.226 for GC uplink and 0.222 for GC downlink, against the 0.1 threshold.
- So buffered results are "≥ 500 m from any training location", **not** spatially independent.
- Source: `results/calibration/buffer_choice.json`, `results/summary/table6_residual_correlation_at_Bstar.csv`.

**RMSE (dB), RF location-aware** (`results/summary/table1_rmse_by_scheme.csv`):

| Direction | R | L | S250 | S500 | LOBO 0 | LOBO 300 | LOBO 500 | LOBO 1000 | Floor |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Uplink | 3.61 | 5.03 | 5.72 | 6.40 | 5.58 | 6.65 | 6.92 | 8.04 | 2.99 |
| Downlink | 3.26 | 4.48 | 4.93 | 5.66 | 4.88 | 5.79 | 6.13 | 7.51 | 2.67 |

**H1 (primary; Δloc = RMSE(RF-loc) − RMSE(RF-dist) at LOBO-B500; 500 m block bootstrap; δ = 0.5 dB)**
(`results/analysis/h1_verdict.json`):

| Direction | Δloc at B500 [95% CI] | Δloc at B0, same packets | Change B500 − B0 [95% CI] | Pre-registered classification |
| --- | --- | --- | --- | --- |
| Uplink | −0.82 [−1.20, −0.46] | −1.52 [−1.81, −1.22] | +0.70 [+0.36, +0.95] | **inconclusive** |
| Downlink | −0.87 [−1.35, −0.42] | −1.34 [−1.63, −1.04] | +0.47 [+0.05, +0.86] | **inconclusive** |

- In both directions the location advantage shrinks with the buffer (the change CI excludes 0).
- At 500 m it is still present (the CI excludes 0).
- But it is not entirely beyond δ (the upper bound is above −0.5 dB), so it is "inconclusive" under the frozen rule.
- Both directions agree.
- Secondary variants:
    - On B500 distance-supported packets the classification is "persists" (uplink −0.89 [−1.26, −0.52]; downlink −1.02 [−1.46, −0.60]).
    - With 1,000 m bootstrap blocks it is "inconclusive" for both directions.

**H2 (distance non-linearity) not supported.**
- Δdist = RMSE(RF-dist) − RMSE(log-distance) is between −0.12 and +0.31 dB under L, S250, S500 and LOBO 0/300/500. Every CI includes 0, except downlink LOBO 300, whose lower bound is +0.00 (`table2_paired_gains.csv`).
- On the B1000-supported packets, RF-dist is *worse* than log-distance at B500 (uplink +0.47 [+0.18, +0.72]).
- Only the random split shows a large Δdist (−2.35 / −1.89). That is leakage, not a gain.
- So the Random Forest gain is location information, not a better distance curve.

**H3 (random-split optimism) supported.** RF-loc RMSE orders R < L < S250 < S500. Paired against S250
(`P1c_grouped_vs_S250.csv`, 500 m blocks), every difference has a CI excluding 0:

| Direction | R − S250 | L − S250 | S500 − S250 |
| --- | --- | --- | --- |
| Uplink | −2.11 [−2.40, −1.88] | −0.69 [−0.99, −0.44] | +0.68 [+0.34, +1.04] |
| Downlink | −1.68 [−1.88, −1.51] | −0.46 [−0.59, −0.31] | +0.72 [+0.38, +1.06] |

**H4 (error composition) supported.** The within-location floor is fixed (2.99 / 2.67 dB; pooled ddof-1 SD 3.26 / 2.91 dB).
As separation grows, its share of RF-loc MSE falls:

| Direction | L | S250 | LOBO 500 | LOBO 1000 |
| --- | --- | --- | --- | --- |
| Uplink | 0.354 | 0.274 | 0.187 | 0.139 |
| Downlink | 0.356 | 0.294 | 0.190 | 0.127 |

Source: `P4_floor_decomposition.csv`.

**H5 (reception dependence) supported, descriptively.**
- RF-loc over-predicts SNR at locations with few received packets (`R5_error_by_valid_packets.csv`).
- Bias with 1–2 valid packets: +5.0 dB (uplink S250) and +7.7 dB (uplink B500).
- Bias with 6–8 packets: −1.0 and −1.9 dB.
- So results for weak links are optimistic.

**Paired buffer series on the B1000-supported packets (primary for B1000, amendment A4)** (`table5_buffer_series.csv`;
14,179 uplink and 14,171 downlink packets):

| Direction | Δloc at B0 | B300 | B500 | B1000 |
| --- | --- | --- | --- | --- |
| Uplink | −1.60 [−1.93, −1.25] | −1.09 [−1.49, −0.71] | −1.02 [−1.43, −0.66] | −0.59 [−1.01, −0.22] |
| Downlink | −1.42 [−1.75, −1.07] | −1.09 [−1.53, −0.68] | −1.11 [−1.64, −0.62] | −0.80 [−1.36, −0.29] |

- Supplementary, B1000 on all packets: log-distance RMSE rises to 10.25 / 9.69 dB.
- That reflects lost distance support: about 23% of packets are unsupported at 1,000 m. It is not a pure separation effect.

**Robustness** (all in `results/analysis/`):

| Check | Result | Reading |
| --- | --- | --- |
| R1, fixed-hp grid offsets/seeds | Δloc range 0.25 (uplink) / 0.17 dB (downlink) across 8 S250 variants; 0.15 / 0.13 dB for LOBO at B500 o0 vs o1 | Grid placement moves Δloc by less than δ/2 |
| R2, size-matched thinning | Δloc −1.42 to −1.44 (uplink), −1.26 to −1.31 (downlink) at B500 training size | The shrinkage at B500 is **not** explained by less training data |
| R6, leaf size at B500 | Leaf 50: change −0.04 / −0.07 dB (not sensitive). **Leaf 5: Δloc −1.69 / −1.56 vs −0.82 / −0.87 (change −0.88 / −0.69 dB): flagged `hyperparameter_sensitive = True`** | Per protocol §5, the H1 result is reported as **hyperparameter-sensitive**. Smaller leaves give a larger location advantage at B500 |
| R7, by gateway at B500 | GC: Δloc −1.86 [−2.83, −0.97] uplink, −2.00 [−3.14, −0.94] downlink. GA: CI includes 0 in both directions. GB: −0.29 [−0.46, −0.10] uplink; downlink CI includes 0 | The persisting location advantage is concentrated at GC. Per rule 15 this is not attributed to shadowing or interference |
| Appendix (S250) | XGBoost +0.15 / +0.12 dB worse than RF-loc (CI excludes 0); residual RF CI includes 0; RF + same-packet RSSI 3.57 / 3.65 dB (diagnostic only) | No change to the model set |

**Path-loss appendix.** The uplink floating-intercept fit reproduces Azevedo & Mendonça (2026) Table 3: α 42.7/54.8/44.0 dB,
β 2.79/2.37/2.93, RMSE 11.9/11.1/12.2 dB (`results/pathloss/`).

## 3. Output locations

| What | Where |
| --- | --- |
| Report tables (Tables 1–6) | `results/summary/*.csv`, `results/summary/summary.md` |
| Figures 1–4 | `figures/fig1_rmse_by_scheme.png`, `fig2_gain_decomposition.png`, `fig3_buffer_series.png`, `fig4_buffer_series_B1000_supported.png` |
| Machine-readable verdict | `results/analysis/h1_verdict.json` |
| All analysis tables | `results/analysis/*.csv`, `analysis_summary.md` |
| Independent verification | `results/verification/verification_report.md` |
| Predictions (every model, every packet) | `predictions/oof_<direction>_<scheme>.csv` (44 files) |
| Protocol, amendments, decisions | `docs/PROTOCOL_FREEZE_rev46.md`, `docs/PROTOCOL_AMENDMENTS_2026-10-28.md`, `docs/DECISION_LOG.md` |
| Literature | `literature_review.md`, `references_verified.bib` |
| Provisional archive (untouched, checksums verified) | `archive/provisional_2026-10/` |

## 4. Unresolved issues and limitations

1. **H1 is inconclusive in both directions and hyperparameter-sensitive (R6, leaf 5).** The fixed hyperparameters (modal S250 choice) are a pre-registered design choice. A sensitivity result this large must be reported next to H1, not resolved post hoc.
2. **Residual spatial correlation is not eliminated at 500 m** (upper CI up to 0.226 for GC). 500 m bootstrap blocks may be smaller than the correlation range (U2), so the CIs are not fully reliable spatial uncertainty estimates.
3. **The correlogram estimator** (location-mean residuals) is attenuated by within-location noise, which makes the rule lenient.
4. **Received-packet estimand.** Weak links are over-predicted (R5); nothing is claimed about lost packets or coverage.
5. **Distance support at 1,000 m** covers only about 77% of packets; all-packet B1000 results are supplementary.
6. **Horizontal distance is used as the predictor**; the dataset paper uses antenna-height-corrected distance (recorded deviation).
7. **One campaign, one city, SF12, three gateways**, with frequency confounded with gateway. The GC-specific effect cannot be separated from site.
8. **Literature:** the search was targeted, not systematic. Forward-citation tracing could not be completed (index sites blocked), so no "first" claim is made. 2 screened papers could not be verified and are excluded from the .bib.
9. **Stale provisional files** remain in `results/eval/metrics*.csv` (labelled in the manifest; copies in the archive).
10. **Data-packet note:** our uplink packet counts are 2–6 higher than the dataset paper's (coverage identical). Unexplained.
