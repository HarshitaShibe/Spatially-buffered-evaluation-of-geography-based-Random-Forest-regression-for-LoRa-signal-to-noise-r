"""Step 4b - buffered leave-one-250m-block-out series (frozen protocol; U1 outcome). Runs after 04a.

Each 250 m block is the test set once; training = all other locations minus those < b m from any test
location (splits/lobo_excluded.csv). Fixed hyperparameters from results/eval/hp_fixed.json (no inner tuning).
Every output row carries:
  sep_m      distance from the test location to the nearest retained training location
  supported  distance support: some retained training location with received packets for the same gateway
             and direction has |log10 d difference| <= 0.1
Stages (python 04b_buffered.py <stage>):
  main  grid o0, b in {0, 300, 500, 1000}, models M0-M4          -> oof_<dir>_LOBO_B<b>.csv
  r1    grid o1 (shifted 125 m), b = B*, logdist/rf_dist/rf_loc   -> oof_<dir>_R1_LOBO_o1_B<B*>.csv
  r2    size-matched control: B0 training randomly thinned to the B* retained count, 3 repeats
                                                                  -> oof_<dir>_R2_thin<rep>.csv
  r6    B* with min_samples_leaf 5 and 50 (rf_dist, rf_loc)        -> oof_<dir>_R6_leaf<l>.csv
"""
import json, sys, time
import numpy as np, pandas as pd
from models import *

STAGE = sys.argv[1]
t0 = time.time()
pk = load_packets()
lf = pd.read_csv(SPLITS / "location_folds.csv", dtype={"location_id": str})
pk = pk.merge(lf[["location_id", "block250", "block500", "block1000", "block250_o1"]], on="location_id",
              validate="many_to_one")
ex = pd.read_csv(SPLITS / "lobo_excluded.csv", dtype={"location_id": str, "block": str})
hp_fixed = json.loads((RES / "eval" / "hp_fixed.json").read_text())
bstar = json.loads((RES / "calibration" / "buffer_choice.json").read_text())["B_star_m"]
XY = lf.set_index("location_id")[["x_m", "y_m"]]
KEEP = ["packet_id", "location_id", "loc_gw", "gateway", "slot", "block250", "block500", "block1000",
        "distance_m", "log10_d", "rssi_dbm", "snr_db"]
EXCL = {k: set(v.location_id) for k, v in ex.groupby(["grid", "buffer_m", "block"])}


def annotate(te, tr):
    """sep_m and distance-support flag for test rows given the training packets actually used."""
    tl = tr.location_id.unique()
    P = XY.loc[tl].values; Q = XY.loc[te.location_id].values
    sep = np.sqrt(((Q[:, None] - P[None]) ** 2).sum(-1)).min(1)
    sup = np.zeros(len(te), bool)
    for g in GATEWAYS:
        m = (te.gateway == g).values
        if m.any():
            ref = tr.loc[tr.gateway == g, "log10_d"].unique()
            sup[m] = (np.abs(te.log10_d.values[m][:, None] - ref[None]).min(1) <= 0.1) if len(ref) else False
    return sep, sup


def run(name, grid, bcol, train_fn, models, hp_for):
    for direction in DIRECTIONS:
        D = pk[pk.direction == direction].reset_index(drop=True)
        parts = []
        for i, blk in enumerate(np.unique(D[bcol])):
            te = D[D[bcol] == blk]
            tr = train_fn(D, blk, direction).reset_index(drop=True)
            assert not set(te.location_id) & set(tr.location_id)
            preds, _ = fit_predict_primary_subset(tr, te, hp_for(direction), models)
            sep, sup = annotate(te, tr)
            out = te[KEEP].copy(); out["test_block"] = blk; out["n_train"] = len(tr)
            out["n_train_locations"] = tr.location_id.nunique(); out["sep_m"] = sep; out["supported"] = sup
            for m in models:
                out[m] = preds[m]
            parts.append(out)
            if i % 20 == 0:
                print(f"{name} {direction} block {i}  {time.time() - t0:6.0f}s", flush=True)
        o = pd.concat(parts); assert len(o) == len(D) and o.packet_id.is_unique
        o.to_csv(PRED / f"oof_{direction}_{name}.csv", index=False)


def fit_predict_primary_subset(tr, te, hp, models):
    if set(models) == set(PRIMARY):
        return fit_predict_primary(tr, te, hp)
    y = tr.snr_db.values; out = {}
    if "logdist" in models:
        out["logdist"] = pred_logdist(fit_logdist(tr), te)
    if "rf_dist" in models:
        out["rf_dist"] = rf(**hp["rf_dist"]).fit(tr[FEAT_DIST], y).predict(te[FEAT_DIST])
    if "rf_loc" in models:
        out["rf_loc"] = rf(**hp["rf_loc"]).fit(tr[FEAT_LOC], y).predict(te[FEAT_LOC])
    return out, None


def buffered(grid, b, bcol):
    def f(D, blk, direction):
        drop = EXCL.get((grid, b, blk), set())
        return D[(D[bcol] != blk) & ~D.location_id.isin(drop)]
    return f


fixed = lambda d: hp_fixed[d]
if STAGE == "main":
    for b in [0, 300, 500, 1000]:
        run(f"LOBO_B{b}", "o0", "block250", buffered("o0", b, "block250"), PRIMARY, fixed)
elif STAGE == "r1":
    run(f"R1_LOBO_o1_B{bstar}", "o1", "block250_o1", buffered("o1", bstar, "block250_o1"),
        ["logdist", "rf_dist", "rf_loc"], fixed)
elif STAGE == "r2":
    for rep in range(3):
        rng = np.random.default_rng(SEED + 100 + rep)

        def thin(D, blk, direction, rng=rng):
            others = np.array(sorted(set(lf.location_id[lf.block250 != blk])))
            n_keep = len(others) - len(EXCL.get(("o0", bstar, blk), set()))
            keep = set(rng.choice(others, n_keep, replace=False))
            return D[(D.block250 != blk) & D.location_id.isin(keep)]
        run(f"R2_thin{rep}", "o0", "block250", thin, ["logdist", "rf_dist", "rf_loc"], fixed)
elif STAGE == "r6":
    for leaf in [5, 50]:
        hp_leaf = lambda d, leaf=leaf: {m: dict(hp_fixed[d][m], min_samples_leaf=leaf) for m in ["rf_dist", "rf_loc"]}
        run(f"R6_leaf{leaf}", "o0", "block250", buffered("o0", bstar, "block250"), ["rf_dist", "rf_loc"], hp_leaf)
print("done", STAGE, round(time.time() - t0), "s")
