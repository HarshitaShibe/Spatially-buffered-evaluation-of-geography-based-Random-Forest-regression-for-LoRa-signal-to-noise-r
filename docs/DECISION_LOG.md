# Implementation decision log (28 Oct 2026)

**Status (updated 28 Oct, ~01:00 UTC): resolved.** D1, D3, D4 and D5 are applied as amendments A1-A6 in `docs/PROTOCOL_AMENDMENTS_2026-10-28.md`, before any buffered or analysis result existed. D2 needed no change. The text below is the original log, kept unchanged.

**Original status: open; nothing applied.** No stage was run and no code was changed while writing this log. The
archive (`archive/provisional_2026-10/`) is untouched.

Protocol references point to `docs/PROTOCOL_FREEZE_rev46.md` (section and line). Code references are file:line in
the current working tree.

Proposed resolutions are documentation-level amendments dated before any buffered or analysis result exists.
None depends on an outcome.

## Summary

| # | Decision | Harshita's preference (28 Oct) | Code today | Change needed |
| --- | --- | --- | --- | --- |
| 1 | Tuning in grid-offset/seed robustness (R1) | Fixed hyperparameters, labelled as such; no mixing with tuned runs | Fixed-hp variants are compared against the *tuned* S250 run | Yes: 07 + one small extra run |
| 2 | Buffered series in `04b_buffered.py` | Acceptable if behaviour matches | Matches §4, §5, §7 (checked below) | No |
| 3 | Conflicting tuning/comparison text | Resolve explicitly before final analysis | See D3 | Docs only, plus one small 07 addition |
| 4 | B1000 separation curve restricted to supported points | Supported = primary; all packets = supplementary | **Not implemented**: P2 uses all packets | Yes: 07 |
| 5 | Correlogram rule | Keep frozen rule; report remaining correlation | Rule implemented; correlation at B\* not surfaced in outputs | Yes: reporting only |

## D1. Fixed-hyperparameter robustness (R1)

**Protocol.**
- §7 R1 (line 239): "S250: 4 grid offsets (0/125 m in x and y) × 2 fold seeds. LOBO-B\*: a second grid offset … Report the spread of Δloc". Tuning is not specified.

**Code.**
- `04_evaluate.py:112-117` runs 7 S250 variants (o0_s1 … o3_s1) with `hp_fixed`. Line 115 skips `fold_S250_o0_s0`, because it equals `fold_S250`.
- `07_analysis.py:193` builds the R1 table from the tuned `S250` run plus those fixed-hp variants. **This mixes tuning variation with grid variation.**
- `04b_buffered.py:94-96` runs the LOBO o1 grid with fixed hp, so it is the same family as LOBO o0. That part is fine.

**Resolution.**
- Label R1 as "fixed-hyperparameter robustness".
- The base-grid reference must also be fixed-hp. No such run exists yet; it needs `fold_S250_o0_s0` with `hp_fixed` (about 1 min).
- 07 then compares 8 fixed-hp S250 variants among themselves, and LOBO o0 vs o1 at B\*.
- The tuned S250 run stays in P1/P3 only.

## D2. Buffered series in `04b_buffered.py`

The behaviour was checked against the protocol:

- **One 250 m block per run, point-based buffer** (§4, lines 120-140). Matches: `02_splits.py` builds the exclusion lists and asserts min distance ≥ b; `04b_buffered.py:81-85` applies them.
- **Fixed hp from modal S250** (§5, line 176). Matches: `04_evaluate.py:104-110` (ties → larger leaf), read at `04b:27,90`.
- **sep_m and distance support** (§4: same gateway, |Δlog10 d| ≤ 0.1, received packets). Matches: `04b:35-47`. sep_m uses training locations that have packets in that direction, which can only make it ≥ the buffer.
- **R1-LOBO, R2 (thin to the B\* retained count, 3 repeats), R6 (leaf 5/50 at B\*)**. Matches: `04b:94-110`.

No change needed. The only mismatch is the file name in §10, which says 04.

## D3. Conflicting tuning and comparison instructions

### Conflict 3a: inner tuning for buffered schemes

- §5 table, row "Inner folds" (line 175): "3, grouped by the outer scheme's unit: … 250 m blocks (S250, **B300, B500**) …"
- §5 table, row "Inner buffer" (line 176): "… The leave-one-block-out series uses **fixed hyperparameters** …"
- §5 last paragraph (line 186): "Fixing the parameters avoids 126 × 3 inner tunings … declared here, before any leave-one-block-out result exists."

Line 175 is a leftover from the pre-U1 design, when B300/B500 were buffered *S250 folds*. U1 replaced that design with leave-one-block-out, and lines 176 and 186 were written for the new design.

**Code** follows lines 176/186 (`04b:27,90`; no inner CV in 04b).

**Smallest resolution: amend line 175.** "B300, B500" applied to the rejected scattered-fold design; the adopted LOBO series uses fixed hyperparameters (next row). This is a clerical correction with no result-dependent choice. It matches what the code does and what R6 tests.

### Conflict 3b: reference scheme for paired comparisons

- §6 metrics table (line 197): "Paired ΔRMSE (Δloc, Δdist, **scheme vs S250**)".
- §7 P1 (line 228): "RMSE table; **buffered schemes paired vs LOBO-B0**".
- §2 H1 (line 79): "Δloc under the primary buffer B\* is closer to zero than Δloc under **LOBO-B0**".
- §2 H3 (line 87): "RMSE(R) < RMSE(L) < RMSE(S250) ≤ RMSE(B\*)". This orders grouped schemes around S250.

**What 07 implements now.**
- Δloc and Δdist within every scheme: `07:87-106`.
- Scheme-vs-reference pairs only against LOBO-B0, for LOBO-B300/B500/B1000, S250 and L: `07:138-146`.
- H1 change Δloc(B\*) − Δloc(B0): `07:124-126`.
- **No pairing against S250 exists.**

**Alternatives.**

| Option | Buffered schemes paired against | Grouped schemes (R, L, S500) paired against | Consequence |
| --- | --- | --- | --- |
| **A (recommended)** | LOBO-B0 | S250 | Each family uses its own zero-buffer reference: the difference isolates the buffer, or the grouping unit. Fully consistent with H1, H3 and P1. "Scheme vs S250" in §6 is read as the grouped-family reference. Adds one small 07 table (R−S250, L−S250, S500−S250 per model) |
| B | S250 | S250 | Buffered-vs-S250 mixes the buffer effect with design differences: 5-fold scattered vs one block held out, and 80% vs about 90–99% training data. Contradicts the H1 wording. Not recommended |
| C | LOBO-B0 | LOBO-B0 | Comparing R or L against a held-out-block design answers no hypothesis. H3 is not about LOBO. Not recommended |

**Smallest resolution: Option A.** Write it as one dated sentence in §6: "Scheme vs S250 applies to the grouped schemes (R, L, S500); buffered schemes are paired against LOBO-B0 (§2 H1, §7 P1)." All test sets contain the same packets, so every pairing is valid. Keep `07:138-146` (S250 and L vs LOBO-B0) as descriptive cross-family context, not inference.

**Related clerical lines.** §4 line 167 and §10 line 322 say "identical test packet sets across **S250**/B300/B500". In practice every scheme tests all packets of a direction, which `06_check.py` already asserts, so the statement is true as written. No change needed.

## D4. B1000 separation curve and distance support

**Protocol.**
- §7 P2 (line 229): "Same test locations across LOBO-B0 → B300 → B500, **plus B1000 on distance-supported points** (paired by location)".

**Code.**
- `07_analysis.py:158-167` bins **all** packets of every scheme, LOBO_B1000 included. **The supported restriction is not implemented in P2.**
- The `supported` flag is only used in P1 (`RMSE_supported`, `07:79-81`) and P3/H1 subsets.

A second issue in the same area: `07:126` (H1 change, supported variant) subtracts Δloc(B0) on **all** packets from Δloc(B\*) on **B\*-supported** packets. Those are different packet sets, so the pair is not matched.

**Resolution (needs a 07 change, not applied).**

- *Primary P2 buffer series:*
    - B0/B300/B500 on all packets (paired, as written).
    - The B1000 step on the B1000-supported mask, with B0/B300/B500 recomputed on the **same mask** so the series stays paired by location.
- *Supplementary:* B1000 on all packets, labelled supplementary.
- *H1 supported variant (`07:126`):* compute Δloc(B0) on the B\*-supported mask before differencing.

**Feasibility.** Supported share at B1000 was 77% of packets (68–84% by gateway; `results/freeze_checks/U1_fallback_lobo_support_gw_dir.csv`).

**A minor inconsistency to fix at the same time.** For grouped schemes, `07:150-154` measures separation to *any* training location, even ones with no packets in that direction. LOBO files measure it to training locations with packets (`04b:37-39`). Proposed: use locations with packets in that direction for both.

## D5. Correlogram buffer rule

**Protocol.**
- §4 (lines 137-139): B\* = smaller of {300, 500} m with upper 95% bound < 0.1 for all six series; otherwise B500 with "not eliminated".
- §8 rule 1 (line 264): report "the residual correlation estimated at that lag, with its CI".
- §8 rule 6 (line 272): no change after seeing Δloc.

**Code.**
- `04a_calibrate.py:58-66` implements the rule exactly: candidate bins [300,500) and [500,1000), the `correlation_not_eliminated` flag, and a timestamp.
- `04a:17` refuses to run if buffered predictions exist.
- `06_check.py` asserts the B\* file is older than the first LOBO prediction.

**Gap.** 07/05 never copy the correlation and CI at B\* into the H1 verdict or summary, so rule 1 cannot be met from the outputs.

**Resolution.** Reporting only: 07 adds, per gateway × direction, the estimate and CI at the B\* bin and the not-eliminated flag to `h1_verdict.json` and the summary. Threshold and rule unchanged.

Known limitation to disclose: location-mean residuals include packet noise, which attenuates correlation. That makes "< 0.1" lenient. The rule stays frozen; the limitation is reported.

## Runtime and dependency review of the new 05 and 06 (static; neither has been run)

**`06_check.py`.**
- **Dependencies:** needs `results/calibration/buffer_choice.json` (04a), `splits/lobo_excluded.csv`, `results/eval/chosen_hyperparameters.csv` and `results/analysis/P1_rmse_by_scheme.csv` (07). Order: after 07. Running it now would fail at line 20 (no calibration file).
- **Risks:**
    1. `assert len(g) == 40` is correct for the current file (verified: 40 tuned rows).
    2. The `sep_m ≥ b` regex (`_B(\d+)$`) covers LOBO_B\* and R1_LOBO_o1_B\*, but **not R6** (run at B\*). Proposed: add R6.
    3. R1_S250 fold labels are not checked by 06. I checked them manually on 28 Oct; proposed: add the check.
    4. The P1 reproduction reads one CSV per P1 row (~80 reads of ~4 MB), which takes seconds.
- No other runtime risk found.

**`05_summarise.py`.**
- **Dependencies:** needs 07 outputs `P1_rmse_by_scheme.csv` (with `RMSE_supported` for LOBO rows), `P3_paired_gains.csv`, `P4_floor_decomposition.csv`, `P2_error_by_separation.csv`, `h1_verdict.json`, plus `buffer_choice.json` and `tabulate`. Order: after 07.
- **Risks:**
    1. `t1 … [SCH]` requires all 8 schemes to be present; it raises KeyError if any 04b stage is missing.
    2. If D4 changes the P2/H1 key names, 05 must be updated to match (t3 parses keys such as `block500_all`).
    3. 05 has no R1 output, so no mixing risk there.
    4. Figure 3 places the B\* label using the y-limits before all lines are drawn; that is cosmetic.
- No other runtime risk found.

**`07_analysis.py`** (the main risk; never executed).
- The logic was re-read for this log. Besides D1/D4/D5, no definite bug was found, but it has never been run.
- Proposed: before the real run, dry-run 07 → 06 → 05 on a scratch copy with surrogate LOBO files, as was done for 04a and 04b.

## Proposed order once approved

1. Apply the documentation amendments for D3a and D3b, dated 28 Oct, before any result.
2. Make the code changes for D1, D4, D5 and the 06 additions.
3. Dry-run 07/06/05 on scratch.
4. Run the one fixed-hp S250 o0_s0 job.
5. Run 04a → 04b → 07 → 06 → 05.
