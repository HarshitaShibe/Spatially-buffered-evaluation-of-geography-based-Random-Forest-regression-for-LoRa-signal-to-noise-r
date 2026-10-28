"""Step 4a - buffer calibration (C8). Must run after 04 and BEFORE 04b.

Correlogram of location-mean residuals of rf_dist (distance-only RF) from the L-split out-of-fold
predictions, per gateway x direction, with a 500 m block bootstrap (B = 500) for 95% CIs.
logdist residuals are shown for comparison only.
Pre-registered rule (protocol Section 4): B* = smallest b in {300, 500} m such that the upper 95% bound of
residual correlation in the lag bin starting at b ([300,500) for 300; [500,1000) for 500) is < 0.1 for all six
series. If none qualifies: B* = 500 and 'correlation_not_eliminated' = true.
No buffered model result exists when this runs.
Outputs: results/calibration/correlogram.csv, results/calibration/buffer_choice.json
"""
import json, datetime
import numpy as np, pandas as pd
from common import *

OUT = RES / "calibration"; OUT.mkdir(parents=True, exist_ok=True)
assert not (PRED / "oof_Uplink_LOBO_B0.csv").exists(), "buffered predictions already exist; calibration must come first"
rng = np.random.default_rng(SEED)
EDGES = np.array([0, 25, 50, 75, 100, 150, 200, 300, 500, 1000])
LABELS = [f"[{a},{b})" for a, b in zip(EDGES[:-1], EDGES[1:])]
NB = 500


def corr_by_bin(v, xy, orig):
    v = v - v.mean(); var = v.var()
    d = np.sqrt(((xy[:, None] - xy[None]) ** 2).sum(-1))
    iu = np.triu_indices(len(v), 1)
    keep = orig[iu[0]] != orig[iu[1]]                       # drop pairs of bootstrap copies of one location
    dd, pp = d[iu][keep], (v[:, None] * v[None, :])[iu][keep]
    b = np.digitize(dd, EDGES) - 1; ok = (b >= 0) & (b < len(LABELS))
    s = np.bincount(b[ok], weights=pp[ok], minlength=len(LABELS)); n = np.bincount(b[ok], minlength=len(LABELS))
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(n > 30, s / n / var, np.nan), n


lf = pd.read_csv(SPLITS / "location_folds.csv", dtype={"location_id": str}).set_index("location_id")
rows = []
for d in DIRECTIONS:
    o = pd.read_csv(PRED / f"oof_{d}_L.csv", dtype={"location_id": str})
    for model in ["rf_dist", "logdist"]:
        for gw, g in o.groupby("gateway"):
            L = g.assign(r=g.snr_db - g[model]).groupby("location_id").r.mean()
            xy = lf.loc[L.index, ["x_m", "y_m"]].values; blk = lf.loc[L.index, "block500"].values
            v = L.values; ids = np.arange(len(v))
            est, n = corr_by_bin(v, xy, ids)
            ub = np.unique(blk); idx = {b: np.where(blk == b)[0] for b in ub}; boots = []
            for _ in range(NB):
                t = np.concatenate([idx[b] for b in rng.choice(ub, len(ub), replace=True)])
                boots.append(corr_by_bin(v[t], xy[t], ids[t])[0])
            lo, hi = np.nanpercentile(np.array(boots), [2.5, 97.5], axis=0)
            for j, lab in enumerate(LABELS):
                rows.append(dict(direction=d, model=model, gateway=gw, lag_m=lab, pairs=int(n[j]),
                                 correlation=est[j], ci95_low=lo[j], ci95_high=hi[j]))
            print(d, model, gw, "done", flush=True)
C = pd.DataFrame(rows); C.round(3).to_csv(OUT / "correlogram.csv", index=False)

R = C[C.model == "rf_dist"]
check = {b: R[R.lag_m == lab].ci95_high.max() for b, lab in [(300, "[300,500)"), (500, "[500,1000)")]}
ok = [b for b in (300, 500) if check[b] < 0.1]
choice = dict(B_star_m=ok[0] if ok else 500, correlation_not_eliminated=not ok,
              max_upper_ci_at_candidate={str(k): round(float(v), 3) for k, v in check.items()},
              rule="smallest b in {300,500} with upper 95% CI of rf_dist residual correlation < 0.1 in the bin "
                   "starting at b, for all 6 gateway x direction series; else 500 with flag",
              written_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
              note="written before any LOBO (buffered) model was fitted")
(OUT / "buffer_choice.json").write_text(json.dumps(choice, indent=1))
print(json.dumps(choice, indent=1))
print(R.pivot_table(index=["direction", "gateway"], columns="lag_m", values="ci95_high")[LABELS].round(2).to_string())
