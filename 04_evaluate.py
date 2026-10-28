"""Step 4 - grouped evaluation schemes R, L, S250, S500 (frozen protocol, 28 Oct 2026).

Per direction, 5 outer folds. rf_dist and rf_loc are tuned SEPARATELY by inner grouped 3-fold CV on the
outer training set only (grid: min_samples_leaf {5,20,50} x max_features {0.5,1.0}).
Appendix models (S250 only): xgb_loc, resrf_loc, rf_C (same-packet RSSI diagnostic).
After S250: fixed hyperparameters for the buffered series = modal S250 choice per model and direction
(ties -> larger leaf) -> results/eval/hp_fixed.json. Then R1: S250 with 3 more grid offsets x 2 seeds,
fixed hyperparameters, models logdist / rf_dist / rf_loc.
No confidence intervals are computed here (all uncertainty is in 07_analysis.py).

Usage: python 04_evaluate.py            full run
       python 04_evaluate.py --r1-base  D1: only the fixed-hp base-grid R1 member (needs hp_fixed.json)
       python 04_evaluate.py --smoke    C7: provisional grid, rf_loc only, L and S250; must reproduce the
                                         archived rf_A predictions exactly
"""
import json, sys, time, platform
import numpy as np, pandas as pd, sklearn, xgboost
from collections import Counter
from xgboost import XGBRegressor
from models import *

OUT = RES / "eval"; OUT.mkdir(parents=True, exist_ok=True); PRED.mkdir(exist_ok=True)
SMOKE = "--smoke" in sys.argv
pk = load_packets()
lf = pd.read_csv(SPLITS / "location_folds.csv", dtype={"location_id": str})
pr = pd.read_csv(SPLITS / "packet_folds_R.csv")
pk = pk.merge(lf.drop(columns=["x_m", "y_m"]), on="location_id", validate="many_to_one").merge(
    pr, on="packet_id", validate="one_to_one")
SCHEMES = {"R": ("fold_R", None), "L": ("fold_L", "location_id"), "S250": ("fold_S250", "block250"),
           "S500": ("fold_S500", "block500")}
KEEP = ["packet_id", "location_id", "loc_gw", "gateway", "slot", "block250", "block500", "block1000",
        "distance_m", "log10_d", "rssi_dbm", "snr_db"]
t0 = time.time(); hp_rows = []

if SMOKE:
    import models
    models.RF_GRID = [dict(min_samples_leaf=m, max_features=0.5) for m in (5, 20, 50)]
    worst = 0.0
    for direction in DIRECTIONS:
        D = pk[pk.direction == direction].reset_index(drop=True)
        for sch in ["L", "S250"]:
            fcol, gcol = SCHEMES[sch]; p = np.full(len(D), np.nan)
            for k in range(5):
                tr_m, te_m = (D[fcol] != k).values, (D[fcol] == k).values
                tr = D[tr_m].reset_index(drop=True)
                hp, _ = tune_rf(tr, FEAT_LOC, gcol)
                p[te_m] = rf(**hp).fit(tr[FEAT_LOC], tr.snr_db.values).predict(D[te_m][FEAT_LOC])
            old = pd.read_csv(ROOT / "archive/provisional_2026-10/predictions" / f"oof_{direction}_{sch}.csv")
            old = old.set_index("packet_id").loc[D.packet_id, "rf_A"].values
            diff = float(np.max(np.abs(old - p))); worst = max(worst, diff)
            print(f"smoke {direction} {sch}: max |new - archived rf_A| = {diff:.2e}  "
                  f"RMSE new {np.sqrt(np.mean((p - D.snr_db) ** 2)):.4f}", flush=True)
    (OUT / "smoke_test.json").write_text(json.dumps(dict(max_abs_diff=worst, passed=worst < 1e-6,
                                                          runtime_s=round(time.time() - t0)), indent=1))
    assert worst < 1e-6, "smoke test failed: does not reproduce archived rf_A"
    print("SMOKE TEST PASSED"); sys.exit(0)


def xgb(**kw):
    return XGBRegressor(n_estimators=400, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8,
                        random_state=SEED, n_jobs=2, **kw)


def run_scheme(D, sch, fcol, gcol, hp_fixed=None, models=PRIMARY, appendix=False):
    oof = D[KEEP + [fcol]].rename(columns={fcol: "fold"}).copy()
    for m in models + (["xgb_loc", "resrf_loc", "rf_C"] if appendix else []):
        oof[m] = np.nan
    for k in range(5):
        tr_m, te_m = (D[fcol] != k).values, (D[fcol] == k).values
        tr, te = D[tr_m].reset_index(drop=True), D[te_m]
        if hp_fixed is None:
            (p_d, s_d), (p_l, s_l) = tune_rf(tr, FEAT_DIST, gcol), tune_rf(tr, FEAT_LOC, gcol)
        else:
            (p_d, s_d), (p_l, s_l) = (hp_fixed["rf_dist"], np.nan), (hp_fixed["rf_loc"], np.nan)
        preds, coef = fit_predict_primary(tr, te, {"rf_dist": p_d, "rf_loc": p_l})
        for m in models:
            oof.loc[te_m, m] = preds[m]
        row = dict(direction=D.direction.iloc[0], scheme=sch, fold=k, n_train=len(tr), n_test=int(te_m.sum()),
                   rf_dist=json.dumps(p_d), rf_dist_inner_rmse=s_d, rf_loc=json.dumps(p_l), rf_loc_inner_rmse=s_l,
                   logdist_coef=json.dumps({g: [round(float(a), 4), round(float(b), 4)] for g, (a, b) in coef.items()}))
        if appendix:
            y = tr.snr_db.values; best, best_r = None, np.inf
            for p in [dict(max_depth=d) for d in (3, 6)]:
                mse = [np.mean((xgb(**p).fit(tr.iloc[a][FEAT_LOC], y[a]).predict(tr.iloc[b][FEAT_LOC]) - y[b]) ** 2)
                       for a, b in inner_splits(tr, gcol)]
                if np.sqrt(np.mean(mse)) < best_r:
                    best, best_r = p, float(np.sqrt(np.mean(mse)))
            oof.loc[te_m, "xgb_loc"] = xgb(**best).fit(tr[FEAT_LOC], y).predict(te[FEAT_LOC])
            res = y - pred_logdist(coef, tr)
            oof.loc[te_m, "resrf_loc"] = pred_logdist(coef, te) + rf(**p_l).fit(tr[FEAT_LOC], res).predict(te[FEAT_LOC])
            trc, tec = tr.dropna(subset=["rssi_dbm"]), te.dropna(subset=["rssi_dbm"])
            oof.loc[tec.index, "rf_C"] = rf(**p_l).fit(trc[FEAT_C], trc.snr_db.values).predict(tec[FEAT_C])
            row["xgb"] = json.dumps(best)
        hp_rows.append(row)
        print(f"{D.direction.iloc[0]} {sch} fold {k}  {time.time() - t0:6.0f}s  rf_dist={p_d} rf_loc={p_l}", flush=True)
    oof.to_csv(PRED / f"oof_{D.direction.iloc[0]}_{sch}.csv", index=False)
    return oof


R1_MODELS = ["logdist", "rf_dist", "rf_loc"]
if "--r1-base" in sys.argv:
    # D1 (docs/DECISION_LOG.md; amendment A1, 28 Oct 2026): the fixed-hyperparameter R1 family needs its own
    # base-grid member (offset 0, seed 0). Runs only that scheme, using the hp_fixed.json written by the full run.
    # Does not touch any other output; its hyperparameter record goes to a separate file.
    hp_fixed = json.loads((OUT / "hp_fixed.json").read_text())
    for direction in DIRECTIONS:
        D = pk[pk.direction == direction].reset_index(drop=True)
        run_scheme(D, "R1_S250_o0_s0", "fold_S250_o0_s0", None, hp_fixed=hp_fixed[direction], models=R1_MODELS)
    pd.DataFrame(hp_rows).to_csv(OUT / "chosen_hyperparameters_R1_S250_o0_s0.csv", index=False)
    print("done --r1-base", round(time.time() - t0), "s"); sys.exit(0)

hp_fixed = {}
for direction in DIRECTIONS:
    D = pk[pk.direction == direction].reset_index(drop=True)
    for sch, (fcol, gcol) in SCHEMES.items():
        run_scheme(D, sch, fcol, gcol, appendix=(sch == "S250"))
    s = [r for r in hp_rows if r["direction"] == direction and r["scheme"] == "S250"]
    hp_fixed[direction] = {}
    for m in ["rf_dist", "rf_loc"]:
        c = Counter(r[m] for r in s); top = max(c.values())
        cands = [json.loads(k) for k, v in c.items() if v == top]
        hp_fixed[direction][m] = sorted(cands, key=lambda p: (-p["min_samples_leaf"], p["max_features"]))[0]
(OUT / "hp_fixed.json").write_text(json.dumps(hp_fixed, indent=1))

# R1: fixed-hyperparameter robustness family = S250 at 4 grid offsets x 2 seeds, ALL with hp_fixed, including the
# base grid o0_s0 (amendment A1). The tuned S250 run above belongs to P1/P3 only and is never compared within R1.
# (The 28 Oct execution of this script skipped o0_s0; it was added afterwards with --r1-base.)
for direction in DIRECTIONS:
    D = pk[pk.direction == direction].reset_index(drop=True)
    for c in [c for c in lf.columns if c.startswith("fold_S250_o")]:
        run_scheme(D, "R1_" + c.replace("fold_", ""), c, None, hp_fixed=hp_fixed[direction], models=R1_MODELS)

pd.DataFrame(hp_rows).to_csv(OUT / "chosen_hyperparameters.csv", index=False)
(OUT / "run_info.json").write_text(json.dumps(dict(
    status="FROZEN PROTOCOL run (protocol-freeze doc, 28 Oct 2026)", seed=SEED, runtime_s=round(time.time() - t0),
    python=platform.python_version(), sklearn=sklearn.__version__, xgboost=xgboost.__version__, pandas=pd.__version__,
    numpy=np.__version__, features=dict(dist=FEAT_DIST, loc=FEAT_LOC, C=FEAT_C), rf_grid=RF_GRID, rf_trees=RF_TREES,
    hp_fixed=hp_fixed), indent=1))
print("done", round(time.time() - t0), "s")
