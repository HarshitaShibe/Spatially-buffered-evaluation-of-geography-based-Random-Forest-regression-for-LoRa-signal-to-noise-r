<!-- Export of the Claude Docs document "Protocol Freeze: Spatially Validated LoRa SNR Prediction (Madeira)",
     revision 46, exported 28 Oct 2026 (markdown export; date/mention chips kept as text).
     Live doc: https://claude.ai/artifact/Gr7CVzZoKw1QACv1XEDSXh . This file is a frozen copy; do not edit. -->
# Protocol Freeze: Spatially Validated LoRa SNR Prediction (Madeira)

Oct 28, 2026 · @Harshita

## Status and how to read this

**Status: SNR protocol frozen 28 Oct 2026.** U1, U2 and U4 are closed, and supervisor sign-off (C3) was waived by Harshita. U3 was closed the same day after reading Azevedo & Mendonça (2026) in full. All four blocking decisions are closed. No numbers in this document are final results. The audit figures quoted are provisional, conditional on packet reception, and are cited only to justify design choices.

Every decision carries one tag:

- **AUDIT**: already supported by the project files, the cheap audit (`07_audit_cheap.py`), or my inspection of `02_splits.py` and `04_evaluate.py` on 28 Oct 2026.
- **PROPOSED**: my methodological recommendation, not yet tested.
- **UNRESOLVED**: needs a code, data or literature check, or a supervisor decision, before it can be fixed.

**Fixed scope:** Madeira/Funchal dataset only. Uplink and downlink analysed separately. Target = measured SNR of received packets. Geography-only predictors. No cross-frequency claim, because frequency is confounded with gateway. Path loss is supporting analysis only. Antwerp is excluded from this paper and deferred to future work.

**Current RQ (from the brief):** "How does the accuracy of geography-based regression models for received-packet LoRa SNR change with the distance between test locations and the nearest training location, and how much of the Random Forest advantage over distance-only baselines remains under spatially separated evaluation?"

## 1. Research question and contribution

**Final RQ (PROPOSED wording; the direction is unchanged):**

> In a fixed-location LoRa measurement campaign (Funchal; SF12; three gateways), how does the packet-level error of geography-based regression models for received-packet SNR change as the minimum distance between each test location and the training locations increases? And how much of the location-aware Random Forest's advantage over two distance-only baselines remains when every test location is at least a pre-specified buffer distance from all training locations? The two baselines are an empirical log-distance fit and a distance-only Random Forest. Uplink and downlink are analysed separately.

Why the wording changed from the brief:

- **"Minimum distance … increases"** names the controlled variable. A split label such as S250 only names a design. AUDIT: the median nearest-training distance is 42 m under L, 83 m under S250 and 133 m under S500, so the block size alone does not set separation.
- **"Two distance-only baselines"** separates two sources of gain. The step from log-distance to RF-distance measures the gain from non-linear distance dependence (e.g. saturation). The step from RF-distance to RF-location measures the gain from location information. AUDIT: `rf_A0` (distance + bearing) cannot do this, because distance plus bearing to a known gateway is a location.
- **"Pre-specified buffer"** fixes the threshold before results are seen (Section 8).

**Contribution statement (PROPOSED; cautious):**

> We give a leakage-controlled evaluation of geography-based SNR regression on public fixed-location LoRa measurements. It separates the error reduction due to non-linear distance dependence from the reduction due to spatial interpolation, and reports how each changes with spatial separation between training and test locations. Errors are interpreted against the packet-to-packet SNR variability observed within locations. We propose no new model and make no claim about prediction for all attempted transmissions.

UNRESOLVED (literature): whether this combination has been reported before. Section 9 (C1–C2) lists the checks. Until they are done, the paper uses no "first", "novel" or "to our knowledge" language.

**Literature read in full, 28 Oct 2026: [Azevedo & Mendonça (2024), *A Critical Review of the Propagation Models Employed in LoRa Systems*, Sensors 24, 3877](https://doi.org/10.3390/s24123877).** This is the same authors' review, not the 2026 Madeira-campaign paper. Published June 2024, it predates the campaign (Feb–Oct 2025), so it does not analyse this dataset. What it establishes, and how this project uses it:

| What the review states | Where | Consequence here |
| --- | --- | --- |
| Below SNR 0 dB, RSSI is dominated by noise and interference. The authors use ESP (RSSI + SNR − 10 log10(1 + 10^(SNR/10))) for received power; LoRa RSSI errors can reach \~20 dB without calibration | Sec. 5.1–5.2, 6 | Supports keeping RSSI and ESP out of the predictors. Any path-loss appendix must state which received-power measure is used, and that RSSI is uncalibrated |
| A wide "transitional region" near receiver sensitivity skews log-distance parameters. The authors refit using data only up to where packet loss begins | Sec. 5.3, Table 12 | A sourced, simple handling of packet-loss bias for the path-loss appendix. It is truncation, not censoring; Callebaut & Van der Perre (2020) is the censored alternative they cite |
| Single-slope log-distance models are often inadequate; multi-slope models reduce error | Sec. 5.5, 6 | Path-loss evidence consistent with H2 (non-linear distance dependence). Our H2 concerns SNR, so it is cited as consistent evidence, not as confirmation |
| ML models for path loss can beat empirical models at the measured site, but generalisation to new locations "remains imperative" to verify | Sec. 3 | Motivation for this study, cited as the authors' call. It is not evidence that no one has done spatially separated evaluation |
| Cites Cardoso et al. (2022) for ANN SNR prediction; typical Semtech LoRa demodulation down to SNR ≈ −20 dB; SF12 sensitivity −136 dBm in their RFM95 test | Sec. 1, 5.1–5.2 | Secondary-sourced values for an optional censoring sensitivity (appendix only) |

No change to the frozen SNR protocol follows from this paper. U3 still needs the 2026 IEEE Access paper itself.

**U3 closed, 28 Oct 2026: [Azevedo & Mendonça (2026), *A Large-Scale LoRa Measurement Campaign for Path-Loss Modeling in Urban and Suburban Environments*, IEEE Access 14, 137151–137166](https://doi.org/10.1109/ACCESS.2026.3730186), read in full.** It is the paper describing this dataset. Its scope is path-loss characterisation. It contains no machine learning, no SNR prediction and no cross-validation, and its conclusion names machine learning on this dataset as future work.

| What the paper reports | Consequence here |
| --- | --- |
| Path loss from ESP, averaged per location in the linear domain; calibrated RSSI; distance corrected for antenna heights | Followed exactly in the path-loss appendix (`09_pathloss_reproduction.py`). Our uplink fit reproduces their Table 3 (α 42.7/54.8/44.0 vs 42.6/54.9/44.4 dB; β 2.79/2.37/2.93 vs 2.79/2.37/2.92; RMSE 11.9/11.1/12.2 vs 11.9/11.1/12.2 dB). This independently validates our parsing |
| Location coverage 62.0 / 95.8 / 83.5% (GA/GB/GC) | Matches ours exactly. Their received-packet counts equal our downlink counts within 1 packet; our uplink counts are 2–6 higher. Minor and unexplained; recorded, not blocking |
| Uplink − downlink PL: mean 0.9 dB, SD 1.5 dB | Ours: 0.85 dB, SD 1.69 dB. Cited as theirs; our earlier RSSI-only fits stay withdrawn |
| Single-slope fits: RMSE 11–12 dB; mean C-I exponents 3.16–3.28; argue for multi-slope or environment-based models | The path-loss claim is theirs. Our H2 concerns SNR and is only consistent with it |
| The SX1276 detector saturates for SNR above about 7 dB (their ref. \[38\]) | Explains our SNR plateau near the gateways: the target has a measurement ceiling. Added as interpretation rule 14 |
| Interference near cellular antennas (800/900 MHz bands) lowers uplink SNR at GA and GB and raises the effective noise floor; GA loses packets above the theoretical sensitivity limit | Explains the lower uplink SNR at the same RSSI and GA's 62% coverage. Spatially clustered interference is something a location-aware model can learn. Added as interpretation rule 15 |
| Order-statistics correction for truncation near sensitivity, applied to ESP | Not applied to SNR. It targets per-location ESP means with few samples, not SNR regression; the received-packet estimand stays as frozen |
| Slots 1–4 come from 4 different end devices 1.5 λ apart; one timestamp per location | Confirms the repeat structure. Slot is never a predictor |

**Novelty position after U3:** there is no overlap with the dataset paper on the SNR-prediction question. C2 is partly done: a targeted web search on 28 Oct 2026 found no later study using this dataset for ML. Most hits were behind paywalls and could not be checked, so no "first" claim is made.

**One deviation recorded:** our predictors use horizontal distance, while the paper uses distance corrected for antenna heights. Per gateway the correction is a monotone transform, so the Random Forests are nearly unaffected. The log-distance baseline differs slightly. The protocol stays frozen as is.

## 2. Hypotheses

All hypotheses use packet-level RMSE (dB) of received-packet SNR on the same test packets. They are tested separately for uplink and downlink. A conclusion is called general only if both directions agree.

Notation (paired, same test packets):

- Δloc = RMSE(RF-loc) − RMSE(RF-dist)
- Δdist = RMSE(RF-dist) − RMSE(LogD)
- δ = smallest effect of practical interest. PROPOSED 0.5 dB; UNRESOLVED until the supervisor agrees (Section 11, U4).

**Primary hypothesis H1 (PROPOSED).** The location-aware RF advantage shrinks as the buffer grows: Δloc under the primary buffer B\* is closer to zero than Δloc under LOBO-B0. At B\* the advantage falls below practical relevance: the 95% CI of Δloc lies within (−δ, +δ).

- AUDIT support for the direction: RF-loc minus log-distance was −1.32 dB under S250 and −0.78 dB under S500 (uplink). That comparison mixes both sources of gain, so it does not test H1.
- Pre-registered outcomes: CI inside ±δ → *no practically relevant location advantage at ≥B\**. CI entirely below −δ → *a location advantage persists at ≥B\**. Anything else → *inconclusive*.

**Secondary hypotheses (PROPOSED):**

1. **H2: distance non-linearity.** Δdist < 0 under every grouped and buffered split, and its size changes little with the buffer. Reason: saturation is a function of distance, not of local shadowing. AUDIT support: SNR saturates at a median of about +8 to +11 dB once RSSI exceeds about −90 dBm.
2. **H3: random-split optimism.** For RF-loc, RMSE(R) < RMSE(L) < RMSE(S250) ≤ RMSE(B\*). AUDIT already shows R < L < S250 < S500 provisionally, so this is confirmatory only.
3. **H4: error composition.** For location-constant predictors under grouped splits, the between-location share of MSE rises with separation, while the within-location part (the floor) stays fixed. AUDIT: the decomposition is exact for these models and splits.
4. **H5: reception dependence.** Error and bias are larger for locations with fewer valid packets and at longer distances. This is descriptive and tests no causal claim about lost packets.

## 3. Models and predictors

The primary set has five models; only one is new (RF-dist). Every model is fitted per direction on training folds only.

**Target (AUDIT):** `snr_db`, the integer-dB SNR of one received packet. Uplink is measured at the gateway and downlink at the end device. Lost packets are absent and never imputed. The processed table holds 37,029 received packets from 1,203 locations, 3 gateways and 2 directions.

| ID | Model | Predictors | Role | Tag |
| --- | --- | --- | --- | --- |
| M0 | Mean | gateway | Floor-free reference | AUDIT (exists as `mean`) |
| M1 | LogD: per-gateway OLS of SNR on log10 d | log10 d, gateway | Empirical baseline; not a path-loss model | AUDIT (exists as `logdist`) |
| M2 | RF-dist: Random Forest | log10 d, gateway one-hot | Flexible distance-only baseline | PROPOSED (new) |
| M3 | LR-loc: linear regression | log10 d, sin b, cos b, x, y, gateway one-hot | Linear location-aware context | AUDIT (exists as `lr_A`) |
| M4 | RF-loc: Random Forest | log10 d, sin b, cos b, x, y, gateway one-hot | Primary location-aware model | AUDIT (exists as `rf_A`) |

b is the bearing from gateway to device. x and y are local metric coordinates of the device.

Decisions on the remaining models:

- **`rf_A0` (distance + bearing): dropped.** AUDIT: it is not location-free, and `rf_A` minus `rf_A0` ranged from −0.03 to +0.14 dB. M2 replaces it.
- **XGBoost and residual RF: appendix, one line.** AUDIT: XGBoost was 0.07–0.21 dB worse than RF, and residual RF gave no gain. They answer no hypothesis.
- **`rf_C` (M4 + same-packet RSSI): appendix diagnostic only.** It is never a planning model and never enters a primary comparison.
- **Never inputs (AUDIT, enforced in code):** RSSI (except in `rf_C`), ESP, timestamps, slot, sub-position, n\_valid.

Interpretation note (PROPOSED): log10 d is a legitimate physical predictor, not leakage. Under buffering it still pools locations at similar distance in other directions; that pooling is exactly what M2 is meant to measure.

UNRESOLVED (minor, non-blocking): whether M2 should be one RF with a gateway one-hot (as proposed, matching M4) or three per-gateway fits. I propose one model for symmetry with M4.

## 4. Outer evaluation splits and leakage control

R, L, S250 and S500 use 5 outer folds. The buffered series uses leave-one-250m-block-out with a buffer of b ∈ {0, 300, 500} m; this replaced the scattered-fold buffer after the U1 check (below). Every location is tested exactly once per scheme, and the test packets are identical across the series LOBO-B0, B300 and B500, so the comparisons are paired. Only the training set changes.

| Scheme | Test unit | Training set | Prediction scenario | Tag |
| --- | --- | --- | --- | --- |
| R | Random packets | All other packets | Leaky reference (same location seen in training) | AUDIT |
| L | Locations, GroupKFold | All other locations | Infill at unseen points | AUDIT |
| S250 | 250 m grid blocks, GroupKFold | All other blocks | Infill at unseen blocks | AUDIT |
| S500 | 500 m grid blocks | All other blocks | Sensitivity | AUDIT |
| LOBO-B0 | One 250 m block (126 runs) | All other blocks | Reference for the buffer series | PROPOSED; feasibility checked |
| LOBO-B300 | One 250 m block | Other blocks minus every location within 300 m of any test location | New area ≥300 m from data | PROPOSED; feasibility checked |
| LOBO-B500 | One 250 m block | Same rule with 500 m | New area ≥500 m from data | PROPOSED; feasibility checked |
| LOBO-B1000 | One 250 m block | Same rule with 1,000 m | Sensitivity only (fails the 50% rule) | PROPOSED; feasibility checked |

**Buffer rule (PROPOSED).** The buffer is point-based: exclude training location j if min\_i dist(i, j) < b over test locations i in fold k. Every test location then has nearest-training distance ≥ b by construction. This is a statement about distance, not about independence (Section 8).

**How the primary buffer B\* is chosen (PROPOSED; rule fixed before any model comparison).**

1. Fit RF-dist under split L only and compute the correlogram of location-mean residuals per gateway × direction, with block-bootstrap CIs.
2. B\* = the smaller of {300, 500} m at which the upper 95% bound of residual correlation is below 0.1 for all six gateway × direction series. 1,000 m is not eligible as primary, because it keeps only 43% of training locations for the worst block, below the 50% rule. It is reported as a sensitivity on distance-supported points.
3. If none qualifies, report B500 as the largest feasible buffer and state that residual correlation was not eliminated.

Why re-estimate (PROPOSED): AUDIT's correlogram used log-distance residuals. Those include the saturation misfit, which varies with distance from the gateway and is therefore spatially structured. They may overstate the shadowing range.

**Known side-effects of buffering (PROPOSED controls):**

- **Less training data.** Handled by a size-matched control (R2).
- **Lost distance support.** Near a gateway, a 500 m buffer removes all short-distance training points. A test point is distance-supported if training data for that gateway contains locations whose log10 d lies within ±0.1 of it (about ±26%). Results are reported on all test points and on supported points only (R3).
- **Sensitivity to grid placement.** Handled by grid-offset repeats (R1).

**U1 resolved (AUDIT, 28 Oct 2026; `08_freeze_checks.py`, `results/freeze_checks/`).** No model was fitted and no SNR values were used.

| Design | Buffer | Training kept, worst fold or block | Training kept, mean or median | Distance-supported test packets | Verdict |
| --- | --- | --- | --- | --- | --- |
| Scattered folds (S250) | 300 m | 16% | 23% (mean) | 86–93% by gateway | Rejected |
| Scattered folds (S250) | 500 m | 0.6% | 4% (mean) | 54–60% | Rejected |
| Leave-one-block-out | 300 m | 86% | 96% (median) | 96% (92–99% by gateway) | Adopted |
| Leave-one-block-out | 500 m | 75% | 89% (median) | 92% (88–97%) | Adopted |
| Leave-one-block-out | 1,000 m | 43% | 68% (median) | 77% (68–84%) | Sensitivity only |

The scattered-fold design fails the 50% rule at both buffers, so the pre-declared fallback applies. The training-size confound is small under leave-one-block-out (B0 → B500 keeps ≥75%), but R2 still controls for it.

**Leakage controls:**

- AUDIT, enforced: folds are assigned once per location and shared across all gateways and both directions.
- AUDIT, enforced: no location or block crosses folds (asserted in 02 and 06).
- AUDIT, enforced: no target-derived features.
- AUDIT, enforced: the only data-wide preprocessing is the projection origin and grid origin (minimum x/y over all locations). These are coordinate translations with no target information.
- PROPOSED new asserts: buffered minimum distance ≥ b; identical test packet sets across S250/B300/B500; each model tuned only on its own training set.

## 5. Inner cross-validation and tuning

Only M2 and M4 are tuned; M0, M1 and M3 have no hyperparameters. Tuning uses only the outer training set of each fold.

| Item | Decision | Tag |
| --- | --- | --- |
| Inner folds | 3, grouped by the outer scheme's unit: packets (R), locations (L), 250 m blocks (S250, B300, B500), 500 m blocks (S500) | AUDIT (current code for R/L/S250/S500); PROPOSED for buffered |
| Inner buffer | Not applicable. The leave-one-block-out series uses fixed hyperparameters: for each model and direction, the most frequently chosen setting across the 5 S250 outer folds (ties go to the larger leaf) | PROPOSED; checked by R6 |
| Tuning criterion | Mean inner packet-level MSE, same as the primary metric | AUDIT |
| Grid, RF | min\_samples\_leaf {5, 20, 50} × max\_features {0.5, 1.0}; 200 trees; fixed seed | PROPOSED (adds max\_features) |
| Tuned separately | M2 and M4 each get their own tuning | PROPOSED; fixes an AUDIT finding |
| Logged | Chosen parameters and inner RMSE per fold, model and scheme | AUDIT (exists) |

The AUDIT finding behind separate tuning: in `04_evaluate.py`, `rf_A0` and `resrf_A` reuse the parameters tuned for `rf_A`. That is acceptable for an ablation but unfair for a baseline.

Risk of fixed parameters taken from unbuffered tuning (PROPOSED reasoning): S250 inner folds keep close neighbours, so tuning may favour small leaves that interpolate well. Under buffered testing that could handicap M4 and push Δloc toward zero, so this bias would favour H1. R6 therefore repeats the B\* run with leaf sizes 5 and 50. If Δloc moves by more than δ/2 (0.25 dB), the H1 result is reported as hyperparameter-sensitive.

Fixing the parameters avoids 126 × 3 inner tunings per model and direction. It is declared here, before any leave-one-block-out result exists.

## 6. Metrics and paired uncertainty

The primary metric is packet-level RMSE (dB), pooled over gateways, per direction and scheme. Primary inference is the paired difference Δloc under B\*, with a spatial block-bootstrap CI.

**Metrics:**

| Metric | Use | Tag |
| --- | --- | --- |
| Packet-level RMSE | Primary | AUDIT |
| Paired ΔRMSE (Δloc, Δdist, scheme vs S250) | Primary inference | AUDIT method; PROPOSED block size |
| MAE, mean error (bias) | Secondary | AUDIT |
| Location-weighted RMSE (each location × gateway weighted equally) | Secondary (R4) | AUDIT |
| Per-gateway RMSE | Secondary; location sets differ by gateway | AUDIT |
| Within-location floor (ddof 0) and between-location RMSE | Grouped and buffered schemes only, M0–M4 | AUDIT (exact for location-constant predictors) |
| Pooled within-location SD (ddof 1) | Population reference, reported beside the floor | AUDIT |
| R² | Pooled only, as context; never per gateway | PROPOSED |

**Paired block bootstrap (PROPOSED):**

1. Resample spatial blocks with replacement, 2,000 replicates.
2. Apply the same resample to both models, so the difference is paired.
3. Compute RMSE(A) − RMSE(B) per replicate and take the 2.5% and 97.5% percentiles.
4. Block size: at least the residual correlation range from the B\* calibration. Fixed at 500 m by U2, with 1,000 m as a sensitivity.

**U2 resolved (AUDIT, 28 Oct 2026).** Only 13–17 occupied 1,000 m blocks exist across 4 grid offsets, below the 20 required, and the largest holds about 21% of packets. 500 m blocks give 39–43 occupied blocks, the largest holding 7–9% of packets. By the pre-set rule, **primary CIs use 500 m blocks, and 1,000 m is a sensitivity analysis.** The audit correlogram still showed correlation of about 0.31 at 300–500 m for GC, so 500 m blocks may be smaller than the correlation range. The paper must say so, and must not call these CIs fully reliable spatial uncertainty estimates.

Also fixed in advance:

- The bootstrap does not capture variation from fold assignment. Spread across the grid-offset repeats (R1) is reported separately, not combined.
- The `boot_rmse` CIs in `metrics.csv` (250 m blocks for every split) are withdrawn. AUDIT: they are already flagged in `PROVISIONAL_STATUS.md`.
- Multiplicity: one primary test per direction. Everything else is reported as estimates with CIs, without claims of significance.

## 7. Primary, mandatory robustness and appendix analyses

Four primary analyses answer the RQ. Seven mandatory robustness checks each guard one specific threat. Everything else goes in the appendix or is dropped.

**Primary analyses (all PROPOSED; all run on M0–M4):**

| # | Question | Train/test | Output |
| --- | --- | --- | --- |
| P1 | Error by evaluation design | R, L, S250, S500, LOBO-B0/B300/B500 | RMSE table; buffered schemes paired vs LOBO-B0 |
| P2 | Error vs separation | Same test locations across LOBO-B0 → B300 → B500, plus B1000 on distance-supported points (paired by location); L and S500 binned by nearest-training distance | RMSE per band, with locations per band and median distance to gateway |
| P3 | Source of gain | LogD → RF-dist → RF-loc on every scheme | Δdist, Δloc with paired CIs (the H1 test is Δloc at B\*) |
| P4 | Distance from the floor | Grouped and buffered schemes | Within vs between MSE; RMSE ÷ floor |

P2 must report band composition, because separation is confounded with location type: sparse, edge and far-from-gateway areas have larger separation. The LOBO-B0 → B500 series removes that confound for the test set, since the test locations are fixed and only training changes.

**Mandatory robustness:**

| # | Threat addressed | Check | Tag |
| --- | --- | --- | --- |
| R1 | Grid placement and fold luck | S250: 4 grid offsets (0/125 m in x and y) × 2 fold seeds. LOBO-B\*: a second grid offset (125 m in both x and y). Report the spread of Δloc | PROPOSED |
| R2 | Buffer = less data | Size-matched control: for each block, randomly thin the LOBO-B0 training set to the LOBO-B\* training size, 3 repeats; compare Δloc | PROPOSED |
| R3 | Buffer = lost distance support | Repeat P1/P3 on distance-supported test points only (Section 4) | PROPOSED |
| R4 | Strong links dominate | Location-weighted RMSE; check whether the model ranking changes | AUDIT (computed provisionally) |
| R5 | Non-random reception | Reception rate by distance band per gateway × direction (from zero-packet rows); RMSE and bias by valid-packet stratum (1–2, 3–5, 6–8); ≥4-packet subset | AUDIT (partial) + PROPOSED strata |
| R6 | Tuning without a buffer | Repeat LOBO-B\* with leaf size 5 and leaf size 50 | PROPOSED |
| R7 | Pooling hides gateways | Per-gateway P1/P3; RMSE by distance band | AUDIT (partial) |

**Optional appendix:**

- `rf_C` (same-packet RSSI) diagnostic.
- XGBoost and residual RF, one line each.
- RMSE by observed-RSSI band, with RSSI used only for stratifying.
- Single-gateway case studies (train on two gateways, test on the third), context only.
- Supporting path-loss characterisation (RSSI log-distance), compared with Azevedo et al. using their method. Not before the full text is read.
- Censored-regression sensitivity, only if a defensible SF12 threshold is sourced. Interference losses make a pure-threshold model questionable.

**Dropped:** `rf_A0`. Antwerp (deferred to future work). Cross-frequency analysis.

## 8. Interpretation rules

These rules are PROPOSED for adoption at the freeze. Once adopted, the paper's wording must follow them.

**Spatial separation**

1. Never write "spatially independent" or "independent test set". Write "test locations at least b m from any training location", and give the residual correlation estimated at that lag, with its CI.
2. A buffer is adequate only if the calibration correlogram supports it (Section 4). A buffer chosen by rule but not supported is reported as such.
3. Do not attribute buffered degradation to spatial dependence unless R2 (data size) and R3 (distance support) leave the effect in place.
4. L and S250 estimate infill error in a surveyed area; buffered splits estimate error in a new area at least b m away. Neither is "the true accuracy". The paper states which scenario each number answers.

**Effects and uncertainty**

5. A CI that includes 0 but extends beyond ±δ is *inconclusive*, never "no difference".
6. Do not change δ, B\*, the block size or the primary scheme after seeing Δloc. Any post-hoc change is labelled post hoc.
7. Report both directions, even if only one supports H1.

**Target and floor**

8. Every result is about SNR given that a packet was received. No claims about coverage, outage, or SNR of lost packets. Weak-link results are flagged as likely optimistic (R5).
9. The floor is a lower bound only for location-constant predictors under grouped or buffered splits. Being near the floor means little error is left between locations, not that the model is optimal.
10. The LogD slope is not 10n and is never reported as a path-loss exponent.

**Scope and novelty**

11. One campaign, one city, SF12, three gateways, and frequency confounded with gateway. No generalisation to other deployments, spreading factors or frequencies.
12. Novelty is stated only as specific differences from named papers whose full text we read. "To our knowledge" is allowed only after the C2 search log exists. "First" is not used.
13. No provisional number from the current pipeline is quoted. Final tables come only from the frozen rerun.

**Measurement physics (added after reading Azevedo & Mendonça 2026)**

14. SNR above about 7 dB is limited by detector saturation. Errors near the gateways are partly a ceiling effect, not model failure, and gains there are not read as propagation learning.
15. A location advantage (Δloc < 0) may reflect spatially clustered interference near cellular antennas as well as shadowing. The paper attributes neither, without per-location interference data.

## 9. Freeze criteria before final experiments

The final run starts only when C1–C9 are all met. C4 and C5 can be checked today from existing split files, with no model fitting.

| # | Criterion | Evidence required | Current state |
| --- | --- | --- | --- |
| C1 | Azevedo et al. (2026) full text read | Notes on their path-loss method, any ML or spatial evaluation, and uplink/downlink findings; revise Section 1 if they overlap | Done: the 2026 paper and the 2024 review were read in full; Table 3 reproduced |
| C2 | Targeted literature check | Logged forward citations of Azevedo, Cardoso, Bitterling; Scholar search for LoRa/LPWAN SNR with spatial or blocked CV | Not done |
| C3 | Supervisor approval | Approval of the RQ, scope (Antwerp out, path loss supporting) and δ | Waived by Harshita on 28 Oct 2026; δ = 0.5 dB adopted |
| C4 | Buffer feasibility (U1) | Retained training per fold and per gateway × direction for B300/B500; distance-supported share; buffered design chosen | Done: scattered folds rejected, leave-one-block-out adopted |
| C5 | Bootstrap block size (U2) | Occupied 1,000 m block count; rule applied | Done: 500 m primary, 1,000 m sensitivity |
| C6 | Pre-registered rules written | B\* selection rule, δ, primary scheme and outcome categories copied into the README before the run | Drafted here |
| C7 | Code changes done and tested | All Section 10 changes; new asserts pass; an R/L/S250 smoke run reproduces the archived provisional `rf_A` RMSE | Not done |
| C8 | Calibration done | RF-dist L-split correlogram with CIs; B\* chosen by rule and recorded *before* the B schemes run | Not done |
| C9 | Provisional outputs archived | Current `results/` and `predictions/` copied to `archive/provisional_2026-10/`, with checksums, never overwritten | Not done |

## 10. Change list by pipeline stage

The five audit issues map to changes in stages 02, 04, 05, 06 and 07. Stage 01 and the raw data are unchanged. One new stage, `04a_calibrate`, runs the buffer calibration.

| Fix (audit issue) | Stage | Change | Tag |
| --- | --- | --- | --- |
| A1 Insufficient separation | 02\_splits | Leave-one-250m-block-out training masks for B0/B300/B500/B1000 (point-based; store excluded IDs per block); grid-offset and seed variants; feasibility summary (retained counts, distance support); 1,000 m block IDs | PROPOSED |
| A1 | 04a\_calibrate (new) | RF-dist on L only, then correlogram of location-mean residuals with block-bootstrap CIs; apply the B\* rule and write `buffer_choice.json` | PROPOSED |
| A1 | 04\_evaluate | Add the LOBO-B0/B300/B500/B1000 series with fixed hyperparameters, the size-matched control and the leaf-size sensitivity (R6); log training sizes per fold | PROPOSED |
| A2 rf\_A0 not location-free | 04\_evaluate | Add RF-dist (log10 d + gateway); tune M2 and M4 separately; add max\_features {0.5, 1.0}; remove `rf_A0`; move XGBoost and residual RF behind an appendix flag | PROPOSED |
| A3 LogD is not physical | 05\_summarise, README | Rename to "empirical log-distance SNR fit"; never print the slope as an exponent; keep the RSSI path-loss fit marked "do not report" until C1 | PROPOSED |
| A4 CIs too narrow | 04\_evaluate, 07 | Remove `boot_rmse` from 04; all CIs come from 07's paired bootstrap at the U2 block size | PROPOSED |
| A5 Received-packet target | 03\_eda, 07 | Reception rate by distance band per gateway × direction; RMSE and bias by valid-packet stratum; target named "received-packet SNR" in every table | AUDIT (partial) + PROPOSED |
| All | 05\_summarise | New tables for P1–P4 and R1–R7; separation-curve figure; floor shown only for grouped and buffered schemes | PROPOSED |
| All | 06\_check | New asserts: buffer minimum distance ≥ b; identical test packets across S250/B schemes; no fold crossing; per-model tuning record; metrics reproduced from predictions | PROPOSED |
| All | README, PROVISIONAL\_STATUS | Pre-registered rules (C6); archive note (C9) | PROPOSED |

## 11. Blocking decisions and readiness

**Verdict (28 Oct 2026): ready for implementation. The SNR protocol is frozen.** U1, U2 and U4 are closed on evidence or by decision. U3 was closed after reading the 2026 paper in full.

| # | Decision | Outcome | Basis |
| --- | --- | --- | --- |
| U1 | Buffered design | Leave-one-250m-block-out with b ∈ {0, 300, 500}; 1,000 m sensitivity only | AUDIT: the scattered-fold buffer kept 16–31% of training at 300 m and 0.6–8% at 500 m |
| U2 | Bootstrap block size | 500 m primary, 1,000 m sensitivity, with a disclosed limitation | AUDIT: 13–17 occupied 1,000 m blocks, below 20 |
| U3 | Contribution and path-loss role | **Closed. The paper has no ML, SNR prediction or cross-validation; the path-loss appendix reproduces its Table 3** | Needs the Azevedo PDF |
| U4 | δ | 0.5 dB, fixed before any result | Decision by Harshita, 28 Oct 2026 |

**Not blocking, decided by pre-set rules:**

- B\* itself (the calibration rule).
- Whether the fixed leaf size matters for H1 (R6 decides).
- M2 as one pooled model or per gateway (pooled proposed).

**Suggested order:**

1. Copy the pre-registered rules into the README (C6) and archive the provisional outputs (C9).
2. Implement Section 10.
3. Smoke test (C7): L and S250 must reproduce the archived `rf_A` RMSE.
4. Calibration (C8): record B\* in `buffer_choice.json` before the buffered models run.
5. Full run, then R1–R7.
6. Path-loss appendix: done (Table 3 reproduced by `09_pathloss_reproduction.py`).
7. Write-up.
