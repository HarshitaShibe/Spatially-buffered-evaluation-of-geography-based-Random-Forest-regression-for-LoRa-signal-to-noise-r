# Protocol amendments, 28 Oct 2026

Written and applied **before any buffered (04b) or analysis (07) result existed** (file written 00:58 UTC on 28 Oct 2026; at that time `results/calibration/` was empty and no `oof_*_LOBO_*` file existed). At the time of writing, the
only fitted outputs were stage 04 (grouped schemes) and its robustness variants. None of them had been
summarised into metrics.

The frozen protocol (`PROTOCOL_FREEZE_rev46.md`) is not edited. These amendments resolve the conflicts listed in
`DECISION_LOG.md` and are binding for the analysis. Harshita set the preferences for A1, A2, A4 and A5 on 28 Oct;
A3 is the smallest resolution proposed in the decision log, adopted the same day.

| ID | Protocol text affected | Amendment | Code |
| --- | --- | --- | --- |
| A1 (D1) | §7 R1 (line 239) | R1 is a **fixed-hyperparameter robustness check**. The S250 family has 8 members (4 grid offsets × 2 seeds, including the base grid o0_s0), all with `hp_fixed`. The LOBO family is o0 vs o1 at B\*, also fixed-hp. The tuned S250 run belongs to P1/P3 and is never compared within R1. | `04_evaluate.py --r1-base` (base member, added afterwards); R1 loop now includes o0_s0; `07_analysis.py` R1 section; output `R1_fixed_hp_*.csv` |
| A2 (D2) | §10 row "04_evaluate: Add the LOBO-… series" | The buffered series is implemented in `04b_buffered.py`. Behaviour is unchanged. | none |
| A3a (D3) | §5 table, row "Inner folds" (line 175), words "B300, B500" | Those words referred to the rejected scattered-fold design. The adopted leave-one-block-out series uses fixed hyperparameters, as in the next row (line 176) and line 186. | none (code already followed lines 176/186) |
| A3b (D3) | §6 metrics row "scheme vs S250" (line 197) vs §7 P1 (line 228) and §2 H1 (line 79) | **Buffered schemes are paired against LOBO-B0; grouped schemes (R, L, S500) are paired against S250.** S250 and L vs LOBO-B0 are kept as descriptive cross-family context only. | `07_analysis.py`: `P1b_scheme_vs_LOBO_B0.csv` (existing), `P1c_grouped_vs_S250.csv` (new) |
| A4 (D4) | §7 P2 (line 229) | Primary buffer series: B0/B300/B500 on all packets. The B1000 step uses the packets that are distance-supported at B1000, with B0/B300/B500 recomputed on the same packets so the series stays paired. B1000 on all packets is **supplementary**. The H1 "supported" variant uses the same packet mask at B0 and B\*. Separation for grouped schemes is measured to training locations that have packets in that direction, as for LOBO. | `07_analysis.py`: P2a/P2b and H1 sections; `05_summarise.py` table 5 and fig 4 |
| A5 (D5) | §8 rule 1 (line 264) | The frozen B\* rule and its threshold are unchanged. The residual correlation estimate and CI at the B\* lag, and the `correlation_not_eliminated` flag, are copied into `h1_verdict.json` and the summary. The estimator's attenuation by within-location noise is disclosed. | `07_analysis.py` H1 section; `05_summarise.py` table 6 |
| A6 | §10 06_check row | `06_check.py` additionally checks: R6 test locations ≥ B\* from training; R1 S250 fold labels match the splits; the R1 family is complete. | `06_check.py` |

No threshold, buffer candidate, metric, model, predictor, split or δ was changed.
