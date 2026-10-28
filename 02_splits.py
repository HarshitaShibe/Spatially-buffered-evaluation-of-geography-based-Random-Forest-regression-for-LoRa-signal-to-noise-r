"""Step 2 - assign evaluation folds ONCE, at the location level, shared by all six files.

Schemes (5 outer folds each):
  R     random over packets                -> leaky on purpose (shows inflation)
  L     grouped by location_id             -> unseen locations, neighbours may be in training
  S250  grouped by 250 m grid blocks       -> MAIN: unseen areas
  S500  grouped by 500 m grid blocks       -> sensitivity
Grid origin = (min x, min y) of the 1,203 device locations in a local metric projection.
Outputs: splits/location_folds.csv, splits/packet_folds_R.csv, splits/split_summary.json
"""
import json
import numpy as np, pandas as pd
from sklearn.model_selection import GroupKFold, KFold
from common import *

K = 5
sites = pd.read_csv(PROC / "sites.csv", dtype={"location_id": str})
packets = pd.read_csv(PROC / "packets.csv", dtype={"location_id": str})

for size in (250, 500):
    bx = np.floor((sites.x_m - sites.x_m.min()) / size).astype(int)
    by = np.floor((sites.y_m - sites.y_m.min()) / size).astype(int)
    sites[f"block{size}"] = bx.astype(str) + "_" + by.astype(str)


def group_folds(groups, seed):
    gkf = GroupKFold(n_splits=K, shuffle=True, random_state=seed)
    fold = np.empty(len(groups), dtype=int)
    for f, (_, te) in enumerate(gkf.split(np.zeros(len(groups)), groups=groups)):
        fold[te] = f
    return fold


sites["fold_L"] = group_folds(sites.location_id.values, SEED)
sites["fold_S250"] = group_folds(sites.block250.values, SEED)
sites["fold_S500"] = group_folds(sites.block500.values, SEED)
SPLITS.mkdir(exist_ok=True)
sites[["location_id", "x_m", "y_m", "block250", "block500", "fold_L", "fold_S250", "fold_S500"]].to_csv(
    SPLITS / "location_folds.csv", index=False)

packets["packet_id"] = (packets.location_id + "_" + packets.gateway + "_" + packets.direction + "_s"
                        + packets.slot.astype(str))
fold_R = np.empty(len(packets), dtype=int)
for f, (_, te) in enumerate(KFold(K, shuffle=True, random_state=SEED).split(packets)):
    fold_R[te] = f
packets["fold_R"] = fold_R
packets[["packet_id", "fold_R"]].to_csv(SPLITS / "packet_folds_R.csv", index=False)

# leakage checks: no location / block appears in two folds of its own scheme
for scheme, key in [("fold_L", "location_id"), ("fold_S250", "block250"), ("fold_S500", "block500")]:
    assert sites.groupby(key)[scheme].nunique().max() == 1, scheme

summary = {}
pk = packets.merge(sites[["location_id", "fold_L", "fold_S250", "fold_S500"]], on="location_id")
for sch in ["fold_R", "fold_L", "fold_S250", "fold_S500"]:
    summary[sch] = {
        "locations_per_fold": sites[sch].value_counts().sort_index().tolist() if sch != "fold_R" else None,
        "packets_per_fold": pk[sch].value_counts().sort_index().tolist(),
    }
summary["n_blocks_250"] = int(sites.block250.nunique()); summary["n_blocks_500"] = int(sites.block500.nunique())
# how often does a test location have a training neighbour within 50 m? (shadowing-leak indicator)
P = sites[["x_m", "y_m"]].values
D = np.sqrt(((P[:, None] - P[None]) ** 2).sum(-1)); np.fill_diagonal(D, np.inf)
for sch in ["fold_L", "fold_S250", "fold_S500"]:
    f = sites[sch].values
    other = np.where(f[:, None] != f[None, :], D, np.inf).min(1)
    summary[sch]["median_dist_to_nearest_training_location_m"] = round(float(np.median(other)), 1)
    summary[sch]["share_with_training_neighbour_within_50m"] = round(float((other < 50).mean()), 3)

# ---------------- Frozen-protocol additions (protocol-freeze doc, 28 Oct 2026) ----------------
# Fold columns above are unchanged. Additions:
#   block1000            1,000 m blocks (bootstrap sensitivity, U2)
#   block250_o1          250 m blocks with the grid shifted by 125 m in x and y (R1 for LOBO)
#   fold_S250_o{i}_s{j}  S250 folds for 4 grid offsets x 2 GroupKFold seeds (R1); o0_s0 == fold_S250
#   lobo_excluded.csv    leave-one-250m-block-out buffers: for each test block and buffer b, the training
#                        locations removed because they lie < b m from any test location in that block
def grid_ids(size, ox=0.0, oy=0.0):
    bx = np.floor((sites.x_m - sites.x_m.min() + ox) / size).astype(int)
    by = np.floor((sites.y_m - sites.y_m.min() + oy) / size).astype(int)
    return bx.astype(str) + "_" + by.astype(str)


sites["block1000"] = grid_ids(1000)
sites["block250_o1"] = grid_ids(250, 125, 125)
OFFSETS = [(0, 0), (125, 0), (0, 125), (125, 125)]
for i, (ox, oy) in enumerate(OFFSETS):
    blk = grid_ids(250, ox, oy).values
    for j in range(2):
        sites[f"fold_S250_o{i}_s{j}"] = group_folds(blk, SEED + j)
        assert pd.Series(sites[f"fold_S250_o{i}_s{j}"].values).groupby(blk).nunique().max() == 1
assert (sites.fold_S250_o0_s0 == sites.fold_S250).all()
extra = ["block1000", "block250_o1"] + [c for c in sites.columns if c.startswith("fold_S250_o")]
sites[["location_id", "x_m", "y_m", "block250", "block500", "fold_L", "fold_S250", "fold_S500"] + extra].to_csv(
    SPLITS / "location_folds.csv", index=False)

BUFFERS = [0, 300, 500, 1000]
rows, lobo_summary = [], []
for grid, bcol, bufs in [("o0", "block250", BUFFERS), ("o1", "block250_o1", [0, 300, 500])]:
    blocks = sites[bcol].values
    for blk in np.unique(blocks):
        te = np.where(blocks == blk)[0]; tr = np.where(blocks != blk)[0]
        dmin = D[np.ix_(tr, te)].min(1)
        for b in bufs:
            ex = tr[dmin < b]
            rows += [(grid, b, blk, sites.location_id.values[e]) for e in ex]
            kept = tr[dmin >= b]
            assert b == 0 or D[np.ix_(kept, te)].min() >= b          # buffer holds by construction
            lobo_summary.append(dict(grid=grid, buffer_m=b, block=blk, retained_share=len(kept) / len(tr)))
pd.DataFrame(rows, columns=["grid", "buffer_m", "block", "location_id"]).to_csv(SPLITS / "lobo_excluded.csv", index=False)
ls = pd.DataFrame(lobo_summary)
summary["lobo"] = {f"{g}_b{b}": dict(blocks=int(len(x)), min_retained_share=round(float(x.retained_share.min()), 3),
                                     median_retained_share=round(float(x.retained_share.median()), 3))
                   for (g, b), x in ls.groupby(["grid", "buffer_m"])}
summary["n_blocks_1000"] = int(sites.block1000.nunique()); summary["n_blocks_250_o1"] = int(sites.block250_o1.nunique())
(SPLITS / "split_summary.json").write_text(json.dumps(summary, indent=1))
print(json.dumps(summary, indent=1))
