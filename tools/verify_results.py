"""Independent verification of the frozen-protocol results (not a pipeline stage; run after 07, 06, 05).

Re-derives key numbers directly from predictions/ with code separate from 07_analysis.py:
  V1  P1 RMSE for every scheme x primary model
  V2  H1: Delta_loc at LOBO-B* (point) and an independent naive block bootstrap CI (2,000 reps, own RNG)
  V3  B1000 primary subset: packet count = B1000 'supported' flags; RMSE on that mask at every buffer
  V4  Every reported CI is ordered (low <= high); H1 classifications follow from CI and delta
  V5  Within-location floor (ddof 0) recomputed
  V6  Buffer distances: min sep_m >= b in every buffered file; R6 >= B*
  V7  R1 table contains only fixed-hyperparameter variants (no tuned S250 run)
  V8  Grouped-vs-S250 and buffered-vs-B0 pairings present as amended (A3)
Writes results/verification/verification_report.md and exits non-zero if any hard check fails.
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PRED, RES = ROOT / "predictions", ROOT / "results"
A = RES / "analysis"; OUT = RES / "verification"; OUT.mkdir(parents=True, exist_ok=True)
DIRS = ["Uplink", "Downlink"]; PRIMARY = ["mean", "logdist", "rf_dist", "lr_loc", "rf_loc"]
BSTAR = json.loads((RES / "calibration" / "buffer_choice.json").read_text())["B_star_m"]
lf = pd.read_csv(ROOT / "splits" / "location_folds.csv", dtype={"location_id": str}).set_index("location_id")
lines, fails = ["# Independent verification of results", "", f"B* = {BSTAR} m", ""], []


def ok(name, cond, detail=""):
    lines.append(f"- {'PASS' if cond else 'FAIL'}  {name}  {detail}")
    if not cond:
        fails.append(name)


def rmse(e):
    return float(np.sqrt(np.mean(np.square(e))))


P1 = pd.read_csv(A / "P1_rmse_by_scheme.csv")
lines += ["## V1 P1 RMSE recomputed", ""]
worst = 0.0
for (d, s), g in P1.groupby(["direction", "scheme"]):
    o = pd.read_csv(PRED / f"oof_{d}_{s}.csv")
    for r in g.itertuples():
        worst = max(worst, abs(rmse(o[r.model] - o.snr_db) - r.RMSE))
ok("P1 RMSE reproduces (all rows; CSV rounded to 4 dp)", worst < 1e-4, f"max abs diff {worst:.2e}")

lines += ["", "## V2 H1 independent bootstrap", ""]
H = json.loads((A / "h1_verdict.json").read_text())
rng = np.random.default_rng(12345)
for d in DIRS:
    o = pd.read_csv(PRED / f"oof_{d}_LOBO_B{BSTAR}.csv", dtype={"location_id": str})
    e1, e2 = (o.rf_loc - o.snr_db).values ** 2, (o.rf_dist - o.snr_db).values ** 2
    pt = np.sqrt(e1.mean()) - np.sqrt(e2.mean())
    b = o.location_id.map(lf.block500).values; ub = np.unique(b); idx = {k: np.where(b == k)[0] for k in ub}
    bt = []
    for _ in range(2000):
        t = np.concatenate([idx[k] for k in rng.choice(ub, len(ub))])
        bt.append(np.sqrt(e1[t].mean()) - np.sqrt(e2[t].mean()))
    lo, hi = np.percentile(bt, [2.5, 97.5]); rep = H[d]["block500_all"]
    ok(f"{d}: H1 point estimate", abs(pt - rep["delta_loc_Bstar"]) < 1e-3, f"recomputed {pt:+.3f} vs reported {rep['delta_loc_Bstar']:+.3f}")
    ok(f"{d}: H1 CI agrees within Monte Carlo tolerance (0.05 dB)",
       abs(lo - rep["ci95"][0]) < 0.05 and abs(hi - rep["ci95"][1]) < 0.05,
       f"independent [{lo:+.3f}, {hi:+.3f}] vs reported [{rep['ci95'][0]:+.3f}, {rep['ci95'][1]:+.3f}]")
    lines.append(f"  - {d} independent CI classification: "
                 f"{'no practically relevant' if lo > -0.5 and hi < 0.5 else ('persists' if hi < -0.5 else 'inconclusive')}")

lines += ["", "## V3 B1000 distance-supported subset (primary for B1000)", ""]
P2b = pd.read_csv(A / "P2b_buffer_series_paired.csv")
for d in DIRS:
    o1000 = pd.read_csv(PRED / f"oof_{d}_LOBO_B1000.csv").set_index("packet_id")
    mask_ids = o1000.index[o1000.supported.astype(bool)]
    q = P2b[(P2b.direction == d) & (P2b.subset == "B1000_supported")]
    ok(f"{d}: B1000 subset rows cover buffers 0/300/500/1000", sorted(q.buffer_m) == [0, 300, 500, 1000])
    ok(f"{d}: subset packet count = B1000 supported flags", set(q.packets) == {len(mask_ids)}, f"{len(mask_ids)} packets")
    for b in (0, 300, 500, 1000):
        ob = pd.read_csv(PRED / f"oof_{d}_LOBO_B{b}.csv").set_index("packet_id").loc[mask_ids]
        r = rmse(ob.rf_loc - ob.snr_db); rep = q[q.buffer_m == b].RMSE_rf_loc.iloc[0]
        ok(f"{d}: B{b} rf_loc RMSE on the B1000 mask", abs(r - rep) < 1e-4, f"{r:.4f}")
    s = P2b[(P2b.direction == d) & (P2b.status == "supplementary")]
    ok(f"{d}: B1000 all-packet row labelled supplementary", list(s.buffer_m) == [1000] and s.packets.iloc[0] == len(o1000))

lines += ["", "## V4 CI ordering and H1 classification logic", ""]
for f in ["P3_paired_gains.csv", "P1b_scheme_vs_LOBO_B0.csv", "P1c_grouped_vs_S250.csv", "R2_size_matched.csv",
          "R7_by_gateway_and_distance.csv", "P2b_buffer_series_paired.csv"]:
    t = pd.read_csv(A / f)
    pairs = [(c, c.replace("low", "high")) for c in t.columns if c.endswith("ci95_low")]
    bad = sum(int((t[a] > t[b]).sum()) for a, b in pairs)
    ok(f"{f}: all CIs ordered", bad == 0, f"{len(pairs)} CI column pair(s)")
for d in DIRS:
    for k, v in H[d].items():
        lo, hi = v["ci95"]
        exp = ("no practically relevant location advantage" if lo > -0.5 and hi < 0.5 else
               "practically relevant location advantage persists" if hi < -0.5 else "inconclusive")
        ok(f"{d} {k}: classification consistent", v["classification"] == exp, v["classification"])

lines += ["", "## V5 floor", ""]
P4 = pd.read_csv(A / "P4_floor_decomposition.csv")
for d in DIRS:
    o = pd.read_csv(PRED / f"oof_{d}_S250.csv")
    fl = np.sqrt(((o.snr_db - o.groupby("loc_gw").snr_db.transform("mean")) ** 2).mean())
    ok(f"{d}: floor ddof0", abs(fl - P4[P4.direction == d].floor_ddof0.iloc[0]) < 1e-4, f"{fl:.4f} dB")

lines += ["", "## V6 buffer distances", ""]
for d in DIRS:
    for b in (300, 500, 1000):
        m = pd.read_csv(PRED / f"oof_{d}_LOBO_B{b}.csv").sep_m.min()
        ok(f"{d} LOBO_B{b}: min sep >= b", m >= b, f"min {m:.1f} m")
    for leaf in (5, 50):
        m = pd.read_csv(PRED / f"oof_{d}_R6_leaf{leaf}.csv").sep_m.min()
        ok(f"{d} R6 leaf{leaf}: min sep >= B*", m >= BSTAR, f"min {m:.1f} m")

lines += ["", "## V7/V8 amended families", ""]
R1 = pd.read_csv(A / "R1_fixed_hp_grid_robustness.csv")
ok("R1 excludes tuned S250", "S250" not in set(R1.variant) and (R1.robustness_type == "fixed-hyperparameter").all(),
   f"{R1.variant.nunique()} variants")
ok("R1 has 8 S250 variants + 2 LOBO variants per direction", (R1.groupby("direction").size() == 10).all())
P1c = pd.read_csv(A / "P1c_grouped_vs_S250.csv"); P1b = pd.read_csv(A / "P1b_scheme_vs_LOBO_B0.csv")
ok("Grouped schemes paired vs S250", sorted(P1c.scheme.unique()) == ["L", "R", "S500"])
ok("Buffered schemes paired vs LOBO-B0", {"LOBO_B300", "LOBO_B500", "LOBO_B1000"} <= set(P1b.scheme))

lines += ["", f"**{len(fails)} failure(s).**" + ("" if not fails else " " + "; ".join(fails))]
(OUT / "verification_report.md").write_text("\n".join(lines)); print("\n".join(lines))
sys.exit(1 if fails else 0)
