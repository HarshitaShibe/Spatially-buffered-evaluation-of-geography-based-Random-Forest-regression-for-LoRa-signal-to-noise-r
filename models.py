"""Frozen model definitions (protocol-freeze doc, Sections 3 and 5). Shared by 04, 04a, 04b.

Primary models (M0-M4):
  mean     per-gateway training mean                                   (M0)
  logdist  per-gateway OLS  SNR = a_g + b_g log10 d  (empirical; NOT a path-loss model)   (M1)
  rf_dist  Random Forest on log10 d + gateway one-hot                  (M2, distance-only)
  lr_loc   linear regression on log10 d, sin b, cos b, x, y, gateway   (M3)
  rf_loc   Random Forest on log10 d, sin b, cos b, x, y, gateway       (M4, primary)
Appendix only: xgb_loc, resrf_loc, rf_C (rf_loc + same-packet RSSI; diagnostic).
Never inputs: RSSI (except rf_C), ESP, timestamps, slot, n_valid.
"""
import numpy as np, pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GroupKFold, KFold
from common import *

GW = [f"gw_{g}" for g in GATEWAYS]
FEAT_DIST = ["log10_d"] + GW
FEAT_LOC = ["log10_d", "sin_b", "cos_b"] + GW + ["x_m", "y_m"]   # same column order as provisional rf_A (smoke test)
FEAT_C = FEAT_LOC + ["rssi_dbm"]
RF_GRID = [dict(min_samples_leaf=m, max_features=f) for m in (5, 20, 50) for f in (0.5, 1.0)]
RF_TREES = 200
PRIMARY = ["mean", "logdist", "rf_dist", "lr_loc", "rf_loc"]


def load_packets():
    pk = pd.read_csv(PROC / "packets.csv", dtype={"location_id": str})
    pk["packet_id"] = pk.location_id + "_" + pk.gateway + "_" + pk.direction + "_s" + pk.slot.astype(str)
    pk["loc_gw"] = pk.location_id + "_" + pk.gateway
    pk["sin_b"], pk["cos_b"] = np.sin(np.radians(pk.bearing_deg)), np.cos(np.radians(pk.bearing_deg))
    for g in GATEWAYS:
        pk[f"gw_{g}"] = (pk.gateway == g).astype(float)
    return pk


def rf(**kw):
    return RandomForestRegressor(n_estimators=RF_TREES, n_jobs=-1, random_state=SEED, **kw)


def fit_logdist(tr):
    coef = {}
    for g, d in tr.groupby("gateway"):
        A = np.c_[np.ones(len(d)), d.log10_d]
        coef[g] = np.linalg.lstsq(A, d.snr_db.values, rcond=None)[0]
    return coef


def pred_logdist(coef, te):
    out = np.full(len(te), np.nan)
    for g, (a, b) in coef.items():
        m = (te.gateway == g).values
        out[m] = a + b * te.log10_d.values[m]
    return out


def inner_splits(tr, group_col):
    if group_col is None:
        return list(KFold(3, shuffle=True, random_state=SEED).split(tr))
    return list(GroupKFold(3, shuffle=True, random_state=SEED).split(tr, groups=tr[group_col]))


def tune_rf(tr, feats, group_col):
    """Inner grouped 3-fold CV on the outer training set only; criterion = mean inner packet MSE."""
    y = tr.snr_db.values; splits = inner_splits(tr, group_col); best, best_r = None, np.inf
    for p in RF_GRID:
        mse = [np.mean((rf(**p).fit(tr.iloc[a][feats], y[a]).predict(tr.iloc[b][feats]) - y[b]) ** 2) for a, b in splits]
        r = float(np.sqrt(np.mean(mse)))
        if r < best_r:
            best, best_r = p, r
    return best, best_r


def fit_predict_primary(tr, te, hp):
    """hp = {'rf_dist': params, 'rf_loc': params}. Returns dict model -> predictions for te."""
    y = tr.snr_db.values
    coef = fit_logdist(tr)
    gm = tr.groupby("gateway").snr_db.mean()
    return {"mean": te.gateway.map(gm).values,
            "logdist": pred_logdist(coef, te),
            "rf_dist": rf(**hp["rf_dist"]).fit(tr[FEAT_DIST], y).predict(te[FEAT_DIST]),
            "lr_loc": LinearRegression().fit(tr[FEAT_LOC], y).predict(te[FEAT_LOC]),
            "rf_loc": rf(**hp["rf_loc"]).fit(tr[FEAT_LOC], y).predict(te[FEAT_LOC])}, coef
