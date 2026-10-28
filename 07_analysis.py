"""Step 7 - frozen-protocol analysis from saved predictions only (no refitting).

Primary: P1 (error by scheme), P2 (error vs separation), P3 (paired gains, H1 verdict), P4 (floor).
Robustness: R1-R7. Appendix: rf_C, xgb_loc, resrf_loc on S250.
Uncertainty: paired spatial block bootstrap, 2,000 replicates, 500 m blocks (primary; U2) and 1,000 m
(sensitivity). The same block-count draws are used for every model compared within a direction, so all
differences are paired. delta = 0.5 dB (U4). Outputs: results/analysis/*.csv, analysis_summary.md, h1_verdict.json

Amendments applied before any buffered/analysis result existed (docs/PROTOCOL_AMENDMENTS_2026-10-28.md):
  A1 (D1) R1 = fixed-hyperparameter robustness only: 8 S250 grid/seed variants + LOBO o0/o1 at B*; the tuned
          S250 run is not part of R1.
  A3 (D3b) buffered schemes are paired against LOBO-B0; grouped schemes (R, L, S500) are paired against S250.
  A4 (D4) P2: B1000 primary on B1000-distance-supported packets, with B0/B300/B500 on the same packets (paired);
          B1000 on all packets is supplementary. H1 'supported' variant uses the same packet mask at B0 and B*.
          Grouped-scheme separation is measured to training locations that have packets in that direction.
  A5 (D5) residual correlation (rf_dist, L split) at the B* lag with its CI is copied into h1_verdict.json.
"""
import json
import numpy as np, pandas as pd
from common import *
from models import PRIMARY

OUT = RES / "analysis"; OUT.mkdir(parents=True, exist_ok=True)
DELTA = 0.5; NBOOT = 2000
BSTAR = json.loads((RES / "calibration" / "buffer_choice.json").read_text())["B_star_m"]
lf = pd.read_csv(SPLITS / "location_folds.csv", dtype={"location_id": str}).set_index("location_id")
GROUPED = {"R": None, "L": "fold_L", "S250": "fold_S250", "S500": "fold_S500"}
LOBO = [f"LOBO_B{b}" for b in (0, 300, 500, 1000)]
md = ["# Frozen-protocol analysis (received-packet SNR; all values computed from saved predictions)", "",
      f"B* = {BSTAR} m (from results/calibration/buffer_choice.json); delta = {DELTA} dB; bootstrap = {NBOOT} "
      "paired replicates over 500 m blocks (1,000 m as sensitivity).", ""]


def load(d, s):
    return pd.read_csv(PRED / f"oof_{d}_{s}.csv", dtype={"location_id": str}).set_index("packet_id")


def rmse(e):
    return float(np.sqrt(np.mean(e ** 2)))


# ---------- bootstrap machinery: per direction, one count matrix per block size
O = {d: {s: load(d, s) for s in list(GROUPED) + LOBO} for d in DIRECTIONS}
ORDER = {d: O[d]["S250"].index for d in DIRECTIONS}
for d in DIRECTIONS:
    for s in O[d]:
        O[d][s] = O[d][s].loc[ORDER[d]]                       # identical packet order everywhere
        assert len(O[d][s]) == len(ORDER[d])
rng = np.random.default_rng(SEED)
BOOT = {}
for d in DIRECTIONS:
    for bs in ["block500", "block1000"]:
        codes, uniq = pd.factorize(O[d]["S250"][bs])
        cnt = rng.multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=NBOOT)
        BOOT[(d, bs)] = (codes, len(uniq), cnt)


def boot_rmse_matrix(d, bs, e2, mask=None):
    codes, nb, cnt = BOOT[(d, bs)]
    w = np.ones_like(e2) if mask is None else mask.astype(float)
    S = np.bincount(codes, weights=e2 * w, minlength=nb); N = np.bincount(codes, weights=w, minlength=nb)
    return np.sqrt((cnt @ S) / (cnt @ N))


def paired(d, bs, ea, eb, mask=None):
    """RMSE(a) - RMSE(b) with paired block-bootstrap 95% CI."""
    m = np.ones(len(ea), bool) if mask is None else mask
    pt = rmse(ea[m]) - rmse(eb[m])
    bt = boot_rmse_matrix(d, bs, ea ** 2, m) - boot_rmse_matrix(d, bs, eb ** 2, m)
    lo, hi = np.percentile(bt, [2.5, 97.5])
    return pt, lo, hi, bt


def err(o, m):
    return (o[m] - o.snr_db).values


# ---------- P1 (+R4 location weighting, R3 supported subset)
rows = []
for d in DIRECTIONS:
    for s, o in O[d].items():
        n_lg = o.groupby("loc_gw").snr_db.transform("size").values
        for m in PRIMARY:
            e = err(o, m); w = 1 / n_lg
            r = dict(direction=d, scheme=s, model=m, n=len(e), RMSE=rmse(e), MAE=float(np.mean(np.abs(e))),
                     bias=float(np.mean(e)), R2_pooled=float(1 - np.sum(e ** 2) / np.sum((o.snr_db - o.snr_db.mean()) ** 2)),
                     RMSE_location_weighted=float(np.sqrt(np.sum(w * e ** 2) / np.sum(w))))
            if "supported" in o:
                sm = o.supported.values.astype(bool)
                r.update(share_supported=float(sm.mean()), RMSE_supported=rmse(e[sm]))
            rows.append(r)
P1 = pd.DataFrame(rows); P1.round(4).to_csv(OUT / "P1_rmse_by_scheme.csv", index=False)
md += ["## P1. RMSE (dB) by scheme", "", P1.pivot_table(index=["direction", "model"], columns="scheme", values="RMSE")
       [list(GROUPED) + LOBO].round(3).to_markdown(), ""]

# ---------- P3 paired gains (+R3 supported, +block-size sensitivity)
COMP = [("rf_dist", "logdist", "delta_dist"), ("rf_loc", "rf_dist", "delta_loc"), ("rf_loc", "logdist", "total"),
        ("lr_loc", "logdist", "lr_vs_logdist")]
rows, BT = [], {}
for d in DIRECTIONS:
    for s, o in O[d].items():
        for bs in ["block500", "block1000"]:
            subsets = [("all", None)] + ([("supported", o.supported.values.astype(bool))] if "supported" in o else [])
            for sub, mask in subsets:
                for a, b, lab in COMP:
                    pt, lo, hi, bt = paired(d, bs, err(o, a), err(o, b), mask)
                    rows.append(dict(direction=d, scheme=s, comparison=lab, a=a, b=b, boot_blocks=bs, subset=sub,
                                     diff_RMSE=pt, ci95_low=lo, ci95_high=hi))
                    BT[(d, s, bs, sub, lab)] = bt
P3 = pd.DataFrame(rows); P3.round(4).to_csv(OUT / "P3_paired_gains.csv", index=False)
main = P3[(P3.boot_blocks == "block500") & (P3.subset == "all") & P3.comparison.isin(["delta_dist", "delta_loc", "total"])]
md += ["## P3. Paired RMSE differences (dB; negative = first model better), 500 m blocks", "",
       main.pivot_table(index=["direction", "comparison"], columns="scheme", values="diff_RMSE")[list(GROUPED) + LOBO]
       .round(3).to_markdown(), ""]


# ---------- H1 verdict
def classify(lo, hi):
    if lo > -DELTA and hi < DELTA:
        return "no practically relevant location advantage"
    if hi < -DELTA:
        return "practically relevant location advantage persists"
    return "inconclusive"


verdict = {}
for d in DIRECTIONS:
    r = {}
    ob, o0 = O[d][f"LOBO_B{BSTAR}"], O[d]["LOBO_B0"]
    for bs in ["block500", "block1000"]:
        for sub in ["all", "supported"]:
            x = P3[(P3.direction == d) & (P3.scheme == f"LOBO_B{BSTAR}") & (P3.comparison == "delta_loc")
                   & (P3.boot_blocks == bs) & (P3.subset == sub)].iloc[0]
            # A4: Delta_loc at B0 on the SAME packets as at B* (all packets, or the B*-supported packets)
            mask = None if sub == "all" else ob.supported.values.astype(bool)
            pt0, lo0, hi0, bt0 = paired(d, bs, err(o0, "rf_loc"), err(o0, "rf_dist"), mask)
            shrink = BT[(d, f"LOBO_B{BSTAR}", bs, sub, "delta_loc")] - bt0
            r[f"{bs}_{sub}"] = dict(delta_loc_Bstar=round(x.diff_RMSE, 3), ci95=[round(x.ci95_low, 3), round(x.ci95_high, 3)],
                                    classification=classify(x.ci95_low, x.ci95_high),
                                    delta_loc_B0_same_packets=round(pt0, 3), delta_loc_B0_ci95=[round(lo0, 3), round(hi0, 3)],
                                    change_Bstar_minus_B0=round(x.diff_RMSE - pt0, 3),
                                    change_ci95=[round(float(v), 3) for v in np.percentile(shrink, [2.5, 97.5])],
                                    packets=int(len(ob) if mask is None else mask.sum()))
    verdict[d] = r
verdict["primary"] = {d: verdict[d]["block500_all"]["classification"] for d in DIRECTIONS}
verdict["general_claim_allowed"] = len(set(verdict["primary"].values())) == 1
# A5: residual correlation at the B* lag (frozen calibration output; reported, never used to change B*)
CHOICE = json.loads((RES / "calibration" / "buffer_choice.json").read_text())
CORR = pd.read_csv(RES / "calibration" / "correlogram.csv")
lag = {300: "[300,500)", 500: "[500,1000)"}[BSTAR]
cr = CORR[(CORR.model == "rf_dist") & (CORR.lag_m == lag)]
verdict["residual_correlation_at_Bstar"] = dict(
    B_star_m=BSTAR, lag_bin_m=lag, correlation_not_eliminated=CHOICE["correlation_not_eliminated"],
    estimator="location-mean rf_dist residuals, L split, 500 m block bootstrap (attenuated by within-location noise)",
    series=[dict(direction=q.direction, gateway=q.gateway, pairs=int(q.pairs), correlation=round(float(q.correlation), 3),
                 ci95=[round(float(q.ci95_low), 3), round(float(q.ci95_high), 3)]) for q in cr.itertuples()])
(OUT / "h1_verdict.json").write_text(json.dumps(verdict, indent=1))
md += ["## H1 verdict (primary: 500 m blocks, all test packets)", "", "```", json.dumps(verdict, indent=1), "```", ""]

# ---------- scheme vs LOBO-B0 (paired, per model)
rows = []
for d in DIRECTIONS:
    ref = O[d]["LOBO_B0"]
    for s in ["LOBO_B300", "LOBO_B500", "LOBO_B1000", "S250", "L"]:
        for m in ["logdist", "rf_dist", "rf_loc"]:
            pt, lo, hi, _ = paired(d, "block500", err(O[d][s], m), err(ref, m))
            rows.append(dict(direction=d, scheme=s, model=m, diff_vs_LOBO_B0=pt, ci95_low=lo, ci95_high=hi))
pd.DataFrame(rows).round(4).to_csv(OUT / "P1b_scheme_vs_LOBO_B0.csv", index=False)
md += ["## P1b. Buffered schemes paired against LOBO-B0 (S250, L rows: cross-family context only)", "",
       pd.DataFrame(rows).round(3).to_markdown(index=False), ""]

# ---------- A3: grouped schemes paired against S250 (H3 family)
rows = []
for d in DIRECTIONS:
    ref = O[d]["S250"]
    for s in ["R", "L", "S500"]:
        for m in PRIMARY:
            for bs in ["block500", "block1000"]:
                pt, lo, hi, _ = paired(d, bs, err(O[d][s], m), err(ref, m))
                rows.append(dict(direction=d, scheme=s, model=m, boot_blocks=bs, diff_vs_S250=pt, ci95_low=lo, ci95_high=hi))
P1c = pd.DataFrame(rows); P1c.round(4).to_csv(OUT / "P1c_grouped_vs_S250.csv", index=False)
md += ["## P1c. Grouped schemes paired against S250 (500 m blocks)", "",
       P1c[P1c.boot_blocks == "block500"].round(3).to_markdown(index=False), ""]

# ---------- P2 separation curve
XY = lf[["x_m", "y_m"]]; P = XY.values; Dm = np.sqrt(((P[:, None] - P[None]) ** 2).sum(-1)); np.fill_diagonal(Dm, np.inf)
pos = {i: k for k, i in enumerate(lf.index)}
BANDS = [0, 25, 50, 100, 200, 300, 500, 1000, np.inf]


def sep_grouped(o, fold_col):
    """A4: distance to the nearest location in other folds that has packets in this direction."""
    has = np.zeros(len(lf), bool); has[[pos[i] for i in o.location_id.unique()]] = True
    f = lf[fold_col].values
    s = np.where((f[:, None] != f[None, :]) & has[None, :], Dm, np.inf).min(1)
    return o.location_id.map(pd.Series(s, index=lf.index)).values


def band_rows(d, s, o, sep, subset, status):
    out = []
    band = pd.cut(sep, BANDS, right=False)
    for bnd, idx in pd.Series(np.arange(len(o))).groupby(band, observed=True):
        g = o.iloc[idx.values]
        out.append(dict(direction=d, scheme=s, subset=subset, status=status, sep_band_m=str(bnd), packets=len(g),
                        locations=g.location_id.nunique(), median_distance_to_gw_m=float(g.distance_m.median()),
                        **{f"RMSE_{m}": rmse(err(g, m)) for m in ["logdist", "rf_dist", "rf_loc"]}))
    return out


rows = []
for d in DIRECTIONS:
    for s in ["L", "S250", "S500"]:
        o = O[d][s]; rows += band_rows(d, s, o, sep_grouped(o, GROUPED[s]), "all", "primary (descriptive)")
    for b in (0, 300, 500):
        o = O[d][f"LOBO_B{b}"]; rows += band_rows(d, f"LOBO_B{b}", o, o.sep_m.values, "all", "primary (descriptive)")
    o = O[d]["LOBO_B1000"]; sm = o.supported.values.astype(bool)
    rows += band_rows(d, "LOBO_B1000", o[sm], o.sep_m.values[sm], "B1000_supported", "primary (descriptive)")
    rows += band_rows(d, "LOBO_B1000", o, o.sep_m.values, "all", "supplementary")
P2 = pd.DataFrame(rows); P2.round(3).to_csv(OUT / "P2_error_by_separation.csv", index=False)
md += ["## P2a. RMSE by distance to nearest training location", "", P2.round(2).to_markdown(index=False), ""]

# P2b: paired buffer series on fixed packet sets (A4)
rows = []
for d in DIRECTIONS:
    sm = O[d]["LOBO_B1000"].supported.values.astype(bool)
    for subset, mask, bufs, status in [("all", None, (0, 300, 500), "primary"),
                                       ("B1000_supported", sm, (0, 300, 500, 1000), "primary"),
                                       ("all", None, (1000,), "supplementary")]:
        for b in bufs:
            o = O[d][f"LOBO_B{b}"]; m = np.ones(len(o), bool) if mask is None else mask
            r = dict(direction=d, subset=subset, status=status, buffer_m=b, packets=int(m.sum()),
                     locations=int(o.location_id[m].nunique()),
                     **{f"RMSE_{k}": rmse(err(o, k)[m]) for k in PRIMARY})
            for lab, a, bb in [("delta_loc", "rf_loc", "rf_dist"), ("delta_dist", "rf_dist", "logdist")]:
                pt, lo, hi, _ = paired(d, "block500", err(o, a), err(o, bb), mask)
                r.update({lab: pt, f"{lab}_ci95_low": lo, f"{lab}_ci95_high": hi})
            rows.append(r)
P2b = pd.DataFrame(rows); P2b.round(4).to_csv(OUT / "P2b_buffer_series_paired.csv", index=False)
md += ["## P2b. Paired buffer series (same packets within each subset; 500 m block CIs)", "",
       P2b.round(3).to_markdown(index=False), ""]

# ---------- P4 floor decomposition
rows = []
for d in DIRECTIONS:
    o = O[d]["S250"]; g = o.groupby("loc_gw").snr_db
    within = float(((o.snr_db - g.transform("mean")) ** 2).mean())
    n = g.size(); v1 = g.var(ddof=1)[n >= 2]
    pooled1 = float(np.sqrt((v1 * (n[n >= 2] - 1)).sum() / (n[n >= 2] - 1).sum()))
    for s, oo in O[d].items():
        if s == "R":
            continue
        for m in PRIMARY:
            assert oo.groupby("loc_gw")[m].std().fillna(0).max() < 1e-6     # location-constant predictions
            mse = float(np.mean(err(oo, m) ** 2))
            rows.append(dict(direction=d, scheme=s, model=m, RMSE=np.sqrt(mse), floor_ddof0=np.sqrt(within),
                             pooled_within_sd_ddof1=pooled1, between_location_RMSE=np.sqrt(max(mse - within, 0)),
                             share_MSE_within=within / mse, RMSE_over_floor=np.sqrt(mse / within)))
P4 = pd.DataFrame(rows); P4.round(4).to_csv(OUT / "P4_floor_decomposition.csv", index=False)

# ---------- R1 fixed-hyperparameter robustness (A1): no tuned run is part of this family
rows = []
for d in DIRECTIONS:
    fam = [("S250 grid offset x seed", f"R1_S250_o{i}_s{j}") for i in range(4) for j in range(2)]
    fam += [("LOBO at B* grid offset", f"LOBO_B{BSTAR}"), ("LOBO at B* grid offset", f"R1_LOBO_o1_B{BSTAR}")]
    for family, s in fam:
        o = load(d, s)
        rows.append(dict(direction=d, robustness_type="fixed-hyperparameter", family=family, variant=s,
                         RMSE_logdist=rmse(err(o, "logdist")), RMSE_rf_dist=rmse(err(o, "rf_dist")),
                         RMSE_rf_loc=rmse(err(o, "rf_loc")), delta_loc=rmse(err(o, "rf_loc")) - rmse(err(o, "rf_dist")),
                         delta_dist=rmse(err(o, "rf_dist")) - rmse(err(o, "logdist"))))
R1 = pd.DataFrame(rows); R1.round(4).to_csv(OUT / "R1_fixed_hp_grid_robustness.csv", index=False)
R1s = R1.groupby(["direction", "family"]).agg(variants=("variant", "size"), delta_loc_min=("delta_loc", "min"),
                                              delta_loc_max=("delta_loc", "max"), delta_dist_min=("delta_dist", "min"),
                                              delta_dist_max=("delta_dist", "max")).reset_index()
R1s["delta_loc_range"] = R1s.delta_loc_max - R1s.delta_loc_min
R1s.round(4).to_csv(OUT / "R1_fixed_hp_spread.csv", index=False)
md += ["## R1. Fixed-hyperparameter robustness: grid offsets and fold seeds (tuned runs excluded)", "",
       R1.round(3).to_markdown(index=False), "", R1s.round(3).to_markdown(index=False), ""]

# ---------- R2 size-matched control
rows = []
for d in DIRECTIONS:
    for s in ["LOBO_B0", f"LOBO_B{BSTAR}"] + [f"R2_thin{r}" for r in range(3)]:
        o = load(d, s).loc[ORDER[d]]
        pt, lo, hi, _ = paired(d, "block500", err(o, "rf_loc"), err(o, "rf_dist"))
        rows.append(dict(direction=d, variant=s, mean_train_locations=float(o.groupby("test_block").n_train_locations.first().mean()),
                         RMSE_rf_loc=rmse(err(o, "rf_loc")), delta_loc=pt, ci95_low=lo, ci95_high=hi))
R2 = pd.DataFrame(rows); R2.round(4).to_csv(OUT / "R2_size_matched.csv", index=False)
md += ["## R2. Size-matched control", "", R2.round(3).to_markdown(index=False), ""]

# ---------- R5 reception and valid-packet strata
loc = pd.read_csv(PROC / "locations.csv", dtype={"location_id": str})
loc["dband"] = pd.cut(loc.distance_m, [0, 250, 500, 1000, 2000, 4000, np.inf], right=False)
R5a = loc.groupby(["direction", "gateway", "dband"], observed=True).agg(
    units=("n_valid", "size"), share_no_packet=("n_valid", lambda x: float((x == 0).mean())),
    mean_slot_reception=("n_valid", lambda x: float(x.mean() / 8))).reset_index()
R5a.round(3).to_csv(OUT / "R5_reception_by_distance.csv", index=False)
rows = []
for d in DIRECTIONS:
    for s in ["S250", f"LOBO_B{BSTAR}"]:
        o = O[d][s]; nv = o.groupby("loc_gw").snr_db.transform("size")
        strata = pd.cut(nv, [0, 2, 5, 8], labels=["1-2", "3-5", "6-8"])
        for st in ["1-2", "3-5", "6-8", ">=4"]:
            g = o[nv >= 4] if st == ">=4" else o[strata == st]
            for m in ["logdist", "rf_dist", "rf_loc"]:
                e = err(g, m)
                rows.append(dict(direction=d, scheme=s, valid_packets=st, packets=len(g), model=m,
                                 RMSE=rmse(e), bias=float(np.mean(e))))
R5b = pd.DataFrame(rows); R5b.round(4).to_csv(OUT / "R5_error_by_valid_packets.csv", index=False)
md += ["## R5. Reception by distance", "", R5a.round(3).to_markdown(index=False), "",
       "## R5. Error by valid packets per location x gateway", "", R5b.round(3).to_markdown(index=False), ""]

# ---------- R6 leaf-size sensitivity
rows = []
for d in DIRECTIONS:
    base = O[d][f"LOBO_B{BSTAR}"]
    d0 = rmse(err(base, "rf_loc")) - rmse(err(base, "rf_dist"))
    for leaf in [5, 50]:
        o = load(d, f"R6_leaf{leaf}").loc[ORDER[d]]
        dl = rmse(err(o, "rf_loc")) - rmse(err(o, "rf_dist"))
        rows.append(dict(direction=d, leaf=leaf, delta_loc=dl, delta_loc_fixed=d0, change=dl - d0,
                         hyperparameter_sensitive=abs(dl - d0) > DELTA / 2))
R6 = pd.DataFrame(rows); R6.round(4).to_csv(OUT / "R6_leaf_sensitivity.csv", index=False)
md += ["## R6. Leaf-size sensitivity at B*", "", R6.round(3).to_markdown(index=False), ""]

# ---------- R7 per gateway and distance band
rows = []
for d in DIRECTIONS:
    for s in ["S250", f"LOBO_B{BSTAR}"]:
        o = O[d][s]
        for gw in GATEWAYS:
            m = (o.gateway == gw).values
            pt, lo, hi, _ = paired(d, "block500", err(o, "rf_loc"), err(o, "rf_dist"), m)
            rows.append(dict(direction=d, scheme=s, group=f"gateway {gw}", packets=int(m.sum()),
                             **{f"RMSE_{k}": rmse(err(o, k)[m]) for k in ["logdist", "rf_dist", "rf_loc"]},
                             delta_loc=pt, ci95_low=lo, ci95_high=hi))
        band = pd.cut(o.distance_m, [0, 250, 500, 1000, 2000, 4000, np.inf], right=False)
        for bnd in band.cat.categories:
            m = (band == bnd).values
            if m.sum() == 0:
                continue
            rows.append(dict(direction=d, scheme=s, group=f"distance {bnd}", packets=int(m.sum()),
                             **{f"RMSE_{k}": rmse(err(o, k)[m]) for k in ["logdist", "rf_dist", "rf_loc"]}))
R7 = pd.DataFrame(rows); R7.round(4).to_csv(OUT / "R7_by_gateway_and_distance.csv", index=False)
md += ["## R7. By gateway and distance band", "", R7.round(3).to_markdown(index=False), ""]

# ---------- Appendix (S250)
rows = []
for d in DIRECTIONS:
    o = O[d]["S250"]
    for m in ["xgb_loc", "resrf_loc", "rf_C"]:
        sub = o[o[m].notna()]; mask = o[m].notna().values
        pt, lo, hi, _ = paired(d, "block500", np.where(mask, err(o, m) if m != "rf_C" else (o[m].fillna(0) - o.snr_db).values, 0),
                               err(o, "rf_loc"), mask)
        rows.append(dict(direction=d, model=m, n=len(sub), RMSE=rmse(err(sub, m)), diff_vs_rf_loc=pt, ci95_low=lo, ci95_high=hi))
A = pd.DataFrame(rows); A.round(4).to_csv(OUT / "Appendix_S250_models.csv", index=False)
md += ["## Appendix (S250): XGBoost, residual RF, RSSI diagnostic", "", A.round(3).to_markdown(index=False), ""]
(OUT / "analysis_summary.md").write_text("\n".join(md))
print("\n".join(md))
