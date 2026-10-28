"""Step 6 - integrity checks of the frozen-protocol outputs (run after 07; no refitting).

1. Every prediction file covers exactly the packets of its direction, without missing primary predictions.
2. Grouped schemes: fold column matches splits/location_folds.csv; no location in two folds.
3. Buffered files: every test location is >= b m from every training location used (sep_m >= b).
4. LOBO, R1-LOBO, R2 and R6 files contain identical test packets.
5. R2: training locations per block do not exceed the B* retained count; R6 test locations are >= B* from training.
5b. The fixed-hp R1 family is complete (8 S250 variants + LOBO o1 at B*) and R1 S250 fold labels match the splits.
6. Hyperparameters were tuned separately for rf_dist and rf_loc in every grouped fold.
7. The B* choice was written before the first buffered prediction file (live file times in the original working copy;
   on a clone, results/calibration/run_order_record.json after a SHA-256 match, because git does not keep file times).
8. P1 RMSE values reproduce from the saved predictions.
"""
import datetime, hashlib, json, re
import numpy as np, pandas as pd
from common import *
from models import PRIMARY, load_packets

pk = load_packets()
lf = pd.read_csv(SPLITS / "location_folds.csv", dtype={"location_id": str})
ex = pd.read_csv(SPLITS / "lobo_excluded.csv", dtype={"location_id": str, "block": str})
bstar = json.loads((RES / "calibration" / "buffer_choice.json").read_text())["B_star_m"]
n_checked = 0
for d in DIRECTIONS:
    ids = set(pk.packet_id[pk.direction == d])
    ref_set = None
    for f in sorted(PRED.glob(f"oof_{d}_*.csv")):
        s = f.stem.replace(f"oof_{d}_", "")
        o = pd.read_csv(f, dtype={"location_id": str, "test_block": str})
        assert set(o.packet_id) == ids and o.packet_id.is_unique, f
        cols = [m for m in PRIMARY if m in o]
        assert cols and o[cols].notna().all().all(), f
        if s in ("L", "S250", "S500"):
            c = {"L": "fold_L", "S250": "fold_S250", "S500": "fold_S500"}[s]
            chk = o.merge(lf[["location_id", c]], on="location_id")
            assert (chk.fold == chk[c]).all() and o.groupby("location_id").fold.nunique().max() == 1, f
        if s.startswith("R1_S250_"):                             # R1 fold labels match splits (decision log D1)
            c = "fold_" + s[3:]
            chk = o.merge(lf[["location_id", c]], on="location_id")
            assert (chk.fold == chk[c]).all(), f
        mb = re.search(r"_B(\d+)$", s)
        if mb and int(mb.group(1)) > 0:
            assert o.sep_m.min() >= int(mb.group(1)) - 1e-6, (f, o.sep_m.min())
        if s.startswith("R6_"):                                   # R6 runs at B* (decision log, 06 risk 2)
            assert o.sep_m.min() >= bstar - 1e-6, (f, o.sep_m.min())
        if s.startswith(("LOBO", "R2", "R6")):
            assert ref_set is None or set(o.packet_id) == ref_set
            ref_set = set(o.packet_id)
        if s.startswith("R2"):
            for blk, g in o.groupby("test_block"):
                others = lf.location_id[lf.block250 != blk].nunique()
                need = others - len(ex[(ex.grid == "o0") & (ex.buffer_m == bstar) & (ex.block == blk)])
                assert g.n_train_locations.iloc[0] <= need, (f, blk)
        n_checked += 1
for d in DIRECTIONS:                                              # complete fixed-hp R1 family (A1)
    for i in range(4):
        for j in range(2):
            assert (PRED / f"oof_{d}_R1_S250_o{i}_s{j}.csv").exists(), (d, i, j)
    assert (PRED / f"oof_{d}_R1_LOBO_o1_B{bstar}.csv").exists()
hp = pd.read_csv(RES / "eval" / "chosen_hyperparameters.csv")
g = hp[hp.scheme.isin(["R", "L", "S250", "S500"])]
assert g.rf_dist_inner_rmse.notna().all() and g.rf_loc_inner_rmse.notna().all() and len(g) == 40
bc = RES / "calibration" / "buffer_choice.json"
t_choice = bc.stat().st_mtime
t_first = min(p.stat().st_mtime for p in PRED.glob("oof_*_LOBO_B*.csv"))
t_written = datetime.datetime.fromisoformat(json.loads(bc.read_text())["written_utc"]).timestamp()
if abs(t_choice - t_written) <= 120:      # original working copy: file times are the real run times
    assert t_choice < t_first, "B* choice was not recorded before the buffered runs"
    order_src = "file times"
else:                                     # fresh clone / unzip: git does not keep file times, use the run record
    rec = json.loads((RES / "calibration" / "run_order_record.json").read_text())
    for k in ("buffer_choice", "first_buffered_prediction"):
        assert hashlib.sha256((ROOT / rec[k]["path"]).read_bytes()).hexdigest() == rec[k]["sha256"], \
            f"{rec[k]['path']} differs from the file in run_order_record.json"
    assert rec["buffer_choice"]["mtime_utc"] < rec["first_buffered_prediction"]["mtime_utc"], \
        "B* choice was not recorded before the buffered runs"
    order_src = "run_order_record.json (hash-checked)"
P1 = pd.read_csv(RES / "analysis" / "P1_rmse_by_scheme.csv"); bad = 0
for _, r in P1.iterrows():
    o = pd.read_csv(PRED / f"oof_{r.direction}_{r.scheme}.csv")
    bad += abs(np.sqrt(((o[r.model] - o.snr_db) ** 2).mean()) - r.RMSE) > 1e-3
assert bad == 0
print(f"OK: {n_checked} prediction files checked; buffers hold; packet sets identical; separate tuning; "
      f"B* recorded before buffered runs [{order_src}]; P1 metrics reproduce.")
