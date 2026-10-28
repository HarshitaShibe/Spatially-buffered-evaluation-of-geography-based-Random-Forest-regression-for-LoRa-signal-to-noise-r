"""Step 8 - protocol-freeze data checks (C4/U1 buffer feasibility, C5/U2 bootstrap block count).

Uses only split assignments, coordinates, distances and packet counts. No model is fitted and no SNR
value is used, so these checks cannot influence model comparisons.

Buffer rule (protocol Section 4): for S250 test fold k, drop training location j if its distance to
any fold-k test location is < b. Distance support: a test (location, gateway, direction) with received
packets is supported if some retained training location with received packets for the same gateway and
direction has |log10 d difference| <= 0.1.
Outputs: results/freeze_checks/*.csv, results/freeze_checks/freeze_checks.md
"""
import numpy as np, pandas as pd
from common import *

OUT = RES / "freeze_checks"; OUT.mkdir(parents=True, exist_ok=True)
lf = pd.read_csv(SPLITS / "location_folds.csv", dtype={"location_id": str}).set_index("location_id")
loc = pd.read_csv(PROC / "locations.csv", dtype={"location_id": str})
loc = loc[loc.n_valid > 0]                       # (location, gateway, direction) with >=1 received packet
ids = lf.index.values
P = lf[["x_m", "y_m"]].values
D = np.sqrt(((P[:, None] - P[None]) ** 2).sum(-1))
pos = {i: n for n, i in enumerate(ids)}
BUFFERS = [0, 300, 500, 1000]
TOL = 0.1
md = ["# Protocol-freeze data checks (no model fitting, no SNR values used)", ""]


def retained_mask(test_idx, train_idx, b):
    if b == 0:
        return train_idx
    dmin = D[np.ix_(train_idx, test_idx)].min(1)
    return train_idx[dmin >= b]


def support(test_ids, train_ids):
    """Share of test (loc,gw,dir) units and of their packets with distance support in training."""
    rows = []
    for (g, d), grp in loc.groupby(["gateway", "direction"]):
        tr = grp[grp.location_id.isin(train_ids)].log10_d.values
        te = grp[grp.location_id.isin(test_ids)]
        if len(te) == 0:
            continue
        if len(tr) == 0:
            sup = np.zeros(len(te), bool)
        else:
            sup = np.abs(te.log10_d.values[:, None] - tr[None, :]).min(1) <= TOL
        rows.append(dict(gateway=g, direction=d, test_units=len(te), train_units=len(tr),
                         supported_units=int(sup.sum()), test_packets=int(te.n_valid.sum()),
                         supported_packets=int(te.n_valid.values[sup].sum())))
    return rows


# ---- U1: scattered-fold buffer on S250 folds
fold_rows, gwd_rows = [], []
for b in BUFFERS:
    for k in range(5):
        te = np.where(lf.fold_S250.values == k)[0]
        tr_all = np.where(lf.fold_S250.values != k)[0]
        tr = retained_mask(te, tr_all, b)
        fold_rows.append(dict(buffer_m=b, fold=k, test_locations=len(te), train_available=len(tr_all),
                              train_retained=len(tr), retained_share=len(tr) / len(tr_all)))
        for r in support(ids[te], ids[tr]):
            gwd_rows.append(dict(buffer_m=b, fold=k, **r))
F = pd.DataFrame(fold_rows)
G = pd.DataFrame(gwd_rows)
G["train_units_available"] = np.nan
F.round(3).to_csv(OUT / "U1_buffer_retained_by_fold.csv", index=False)
G.to_csv(OUT / "U1_buffer_support_by_fold_gw_dir.csv", index=False)

Gs = G.groupby(["buffer_m", "direction", "gateway"])[["test_units", "supported_units", "test_packets",
                                                      "supported_packets"]].sum()
Gs["min_train_units_in_any_fold"] = G.groupby(["buffer_m", "direction", "gateway"]).train_units.min()
Gs["supported_unit_share"] = Gs.supported_units / Gs.test_units
Gs["supported_packet_share"] = Gs.supported_packets / Gs.test_packets
Gs = Gs.reset_index()
Gs.round(3).to_csv(OUT / "U1_support_summary.csv", index=False)
Fs = F.groupby("buffer_m").agg(min_retained_share=("retained_share", "min"),
                               mean_retained_share=("retained_share", "mean"),
                               min_train_retained=("train_retained", "min")).reset_index()
md += ["## U1a. Training locations retained under the scattered-fold buffer (S250 folds)", "",
       F.pivot_table(index="fold", columns="buffer_m", values="retained_share").round(3).to_markdown(), "",
       Fs.round(3).to_markdown(index=False), "",
       "## U1b. Distance support of test units (|dlog10 d| <= 0.1), pooled over folds", "",
       Gs[["buffer_m", "direction", "gateway", "test_units", "min_train_units_in_any_fold", "supported_unit_share",
           "supported_packet_share"]].round(3).to_markdown(index=False), ""]

# ---- U1 fallback: buffered leave-one-block-out on 250 m blocks
lobo = []
blocks = lf.block250.values
lobo_gwd = []
for b in [0, 300, 500, 1000]:
    for blk in np.unique(blocks):
        te = np.where(blocks == blk)[0]
        tr_all = np.where(blocks != blk)[0]
        tr = retained_mask(te, tr_all, b)
        sup = pd.DataFrame(support(ids[te], ids[tr]))
        lobo.append(dict(buffer_m=b, block=blk, test_locations=len(te), train_retained=len(tr),
                         retained_share=len(tr) / len(tr_all),
                         test_packets=int(sup.test_packets.sum()) if len(sup) else 0,
                         supported_packets=int(sup.supported_packets.sum()) if len(sup) else 0))
        for r in (sup.to_dict("records") if len(sup) else []):
            lobo_gwd.append(dict(buffer_m=b, block=blk, **r))
Lb = pd.DataFrame(lobo)
Lb.round(3).to_csv(OUT / "U1_fallback_lobo_by_block.csv", index=False)
Lbs = Lb.groupby("buffer_m").agg(blocks=("block", "size"), min_retained_share=("retained_share", "min"),
                                 median_retained_share=("retained_share", "median"),
                                 min_train_retained=("train_retained", "min"),
                                 test_packets=("test_packets", "sum"),
                                 supported_packets=("supported_packets", "sum")).reset_index()
Lbs["pooled_supported_packet_share"] = Lbs.supported_packets / Lbs.test_packets
Lg = pd.DataFrame(lobo_gwd).groupby(["buffer_m", "direction", "gateway"])[["test_packets", "supported_packets"]].sum()
Lg["supported_packet_share"] = Lg.supported_packets / Lg.test_packets
Lg = Lg.reset_index()
Lg.round(3).to_csv(OUT / "U1_fallback_lobo_support_gw_dir.csv", index=False)
md += ["## U1c. Fallback: buffered leave-one-250m-block-out", "", Lbs.round(3).to_markdown(index=False), "",
       "Distance-supported packet share by gateway x direction (fallback design)", "",
       Lg.pivot_table(index=["direction", "gateway"], columns="buffer_m", values="supported_packet_share").round(3).to_markdown(), ""]

# ---- U2: occupied 1,000 m blocks (origin = min x/y, plus 500 m offsets)
pk_per_loc = loc.groupby("location_id").n_valid.sum()
rows_b = []
for size in [500, 1000]:
    for ox, oy in [(0, 0), (size / 2, 0), (0, size / 2), (size / 2, size / 2)]:
        bx = np.floor((lf.x_m - lf.x_m.min() + ox) / size).astype(int)
        by = np.floor((lf.y_m - lf.y_m.min() + oy) / size).astype(int)
        bid = bx.astype(str) + "_" + by.astype(str)
        locs_per = bid.value_counts()
        pk_per = pk_per_loc.reindex(lf.index).fillna(0).groupby(bid.values).sum()
        rows_b.append(dict(block_m=size, offset_x_m=ox, offset_y_m=oy, occupied_blocks=len(locs_per),
                           blocks_ge10_locations=int((locs_per >= 10).sum()),
                           median_locations_per_block=float(locs_per.median()),
                           max_block_packet_share=float(pk_per.max() / pk_per.sum())))
Bk = pd.DataFrame(rows_b)
Bk.round(3).to_csv(OUT / "U2_block_counts.csv", index=False)
md += ["## U2. Occupied bootstrap blocks (all directions/gateways pooled)", "", Bk.round(3).to_markdown(index=False), ""]
(OUT / "freeze_checks.md").write_text("\n".join(md))
print("\n".join(md))
