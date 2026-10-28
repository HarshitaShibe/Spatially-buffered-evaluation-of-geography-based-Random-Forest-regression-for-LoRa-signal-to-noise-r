"""Step 3 - exploratory analysis and descriptive large-scale propagation fits (whole dataset).

Descriptive only: these fits use all data and are NOT evaluation results.
Outputs (results/eda/*.csv, figures/*.png):
  data_summary.csv, censoring_by_valid_count.csv, within_location_variability.csv,
  saturation_by_rssi_band.csv, rssi_pathloss_fit.csv, snr_logdistance_fit.csv
"""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import *

OUT = RES / "eda"; OUT.mkdir(parents=True, exist_ok=True); FIG.mkdir(exist_ok=True)
pk = pd.read_csv(PROC / "packets.csv", dtype={"location_id": str})
loc = pd.read_csv(PROC / "locations.csv", dtype={"location_id": str})
lf = pd.read_csv(SPLITS / "location_folds.csv", dtype={"location_id": str})
gws = pd.read_csv(PROC / "gateways.csv")
rng = np.random.default_rng(SEED)
EIRP_PLUS_GR = DOCUMENTED["tx_power_dbm"] + 2 * DOCUMENTED["antenna_gain_dbi"]  # 14 + 1 + 1 dB (documented)


def pooled_within_var(df):
    """Pooled within-location variance, ddof=1 per location, weighted by (n_i - 1)."""
    g = df.groupby("location_id").snr_db
    n = g.count(); v = g.var(ddof=1)
    m = n >= 2
    return float(((n[m] - 1) * v[m]).sum() / (n[m] - 1).sum()), int(m.sum())


def block_boot(df, fn, blocks, B=500):
    ub = blocks.unique(); vals = []
    idx = {b: np.where(blocks.values == b)[0] for b in ub}
    for _ in range(B):
        draw = rng.choice(ub, len(ub), replace=True)
        take = np.concatenate([idx[b] for b in draw])
        # a block drawn twice must count as two distinct copies, not merge into one location
        copy_tag = np.concatenate([np.full(len(idx[b]), k) for k, b in enumerate(draw)]).astype(str)
        boot = df.iloc[take].copy()
        boot["location_id"] = boot["location_id"].values + "#" + copy_tag
        vals.append(fn(boot))
    return np.percentile(vals, [2.5, 97.5])


pk = pk.merge(lf[["location_id", "block250"]], on="location_id")
rows, wl = [], []
for (gw, d), g in pk.groupby(["gateway", "direction"]):
    l = loc[(loc.gateway == gw) & (loc.direction == d)]
    var, nloc = pooled_within_var(g)
    lo, hi = block_boot(g, lambda x: np.sqrt(pooled_within_var(x)[0]), g.block250)
    rows.append(dict(gateway=gw, direction=d, locations_total=len(l), locations_with_packet=int((l.n_valid > 0).sum()),
                     locations_all_8=int((l.n_valid == 8).sum()), packets=len(g),
                     dist_min_m=round(g.distance_m.min(), 1), dist_median_m=round(g.distance_m.median(), 1),
                     dist_max_m=round(g.distance_m.max(), 1), snr_mean=round(g.snr_db.mean(), 2),
                     snr_sd=round(g.snr_db.std(), 2), snr_min=g.snr_db.min(), snr_max=g.snr_db.max(),
                     share_packets_rssi_above_m90=round(float((g.rssi_dbm > -90).mean()), 3)))
    wl.append(dict(gateway=gw, direction=d, locations_used=nloc, pooled_within_sd_db=round(np.sqrt(var), 3),
                   ci95_low=round(lo, 3), ci95_high=round(hi, 3)))
allv, alln = pooled_within_var(pk.assign(location_id=pk.location_id + pk.gateway + pk.direction))
pd.DataFrame(rows).to_csv(OUT / "data_summary.csv", index=False)
wlv = pd.DataFrame(wl); wlv.to_csv(OUT / "within_location_variability.csv", index=False)

# censoring: median location-mean SNR by number of valid packets
cen = loc[loc.n_valid > 0].groupby(["direction", "gateway", "n_valid"]).snr_median.median().unstack("n_valid").round(1)
cen.to_csv(OUT / "censoring_by_valid_count.csv")

# saturation
bands = [-125, -115, -110, -105, -100, -95, -90, -80, -70, -30]
sat = pk.dropna(subset=["rssi_dbm"]).assign(rssi_band=lambda x: pd.cut(x.rssi_dbm, bands)).groupby(
    ["direction", "gateway", "rssi_band"], observed=True).snr_db.agg(["count", "median", "max"])
sat.to_csv(OUT / "saturation_by_rssi_band.csv")

# descriptive log-distance fits: PL = 16 - RSSI (documented EIRP+Gr); PL = PL100 + 10 n log10(d/100)
fits, sfits = [], []
for (gw, d), g in pk.dropna(subset=["rssi_dbm"]).groupby(["gateway", "direction"]):
    x = 10 * np.log10(g.distance_m / 100.0)
    pl = EIRP_PLUS_GR - g.rssi_dbm
    A = np.c_[np.ones(len(x)), x]
    (pl100, n), *_ = np.linalg.lstsq(A, pl, rcond=None)
    res = pl - A @ [pl100, n]
    fits.append(dict(gateway=gw, direction=d, packets=len(g), PL_at_100m_dB=round(pl100, 2),
                     path_loss_exponent_n=round(n, 3), shadowing_sigma_dB=round(res.std(ddof=2), 2)))
    (a, b), *_ = np.linalg.lstsq(A, g.snr_db, rcond=None)
    r2 = g.snr_db - A @ [a, b]
    sfits.append(dict(gateway=gw, direction=d, SNR_at_100m_dB=round(a, 2), slope_per_decade_dB=round(10 * b, 2),
                      residual_sd_dB=round(r2.std(ddof=2), 2)))
pd.DataFrame(fits).to_csv(OUT / "rssi_pathloss_fit.csv", index=False)
pd.DataFrame(sfits).to_csv(OUT / "snr_logdistance_fit.csv", index=False)

# ---- figures
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
col = {"GA": "#1f5fbf", "GB": "#e08a1e", "GC": "#2e9e5b"}
fig, ax = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
for i, d in enumerate(DIRECTIONS):
    for gw in GATEWAYS:
        g = pk[(pk.gateway == gw) & (pk.direction == d)]
        ax[i].scatter(g.distance_m, g.snr_db + rng.uniform(-.3, .3, len(g)), s=2, alpha=.15, color=col[gw], label=gw)
    ax[i].set_xscale("log"); ax[i].set_title(f"{d} SNR vs distance"); ax[i].set_xlabel("Distance (m, log)")
ax[0].set_ylabel("SNR (dB, jittered)"); ax[1].legend(markerscale=5, frameon=False)
fig.tight_layout(); fig.savefig(FIG / "eda_snr_vs_distance.png", dpi=180); plt.close(fig)

fig, ax = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
for i, d in enumerate(DIRECTIONS):
    for gw in GATEWAYS:
        g = pk[(pk.gateway == gw) & (pk.direction == d)].dropna(subset=["rssi_dbm"])
        m = g.groupby(g.rssi_dbm.round()).snr_db.median()
        ax[i].plot(m.index, m.values, color=col[gw], label=gw)
    ax[i].set_title(f"{d}: median SNR vs RSSI"); ax[i].set_xlabel("RSSI (dBm)")
ax[0].set_ylabel("Median SNR (dB)"); ax[1].legend(frameon=False)
fig.tight_layout(); fig.savefig(FIG / "eda_snr_vs_rssi_saturation.png", dpi=180); plt.close(fig)

fig, ax = plt.subplots(figsize=(6, 3.6))
for (d, gw), r in cen.iterrows():
    ax.plot(r.index, r.values, marker="o", ms=3, color=col[gw], ls="-" if d == "Uplink" else "--", label=f"{gw} {d}")
ax.set_xlabel("Valid packets at location (of 8)"); ax.set_ylabel("Median location SNR (dB)")
ax.set_title("Lost packets are weak packets (informative missingness)"); ax.legend(fontsize=7, frameon=False, ncol=2)
fig.tight_layout(); fig.savefig(FIG / "eda_censoring.png", dpi=180); plt.close(fig)

sites = pd.read_csv(PROC / "sites.csv", dtype={"location_id": str}).merge(lf[["location_id", "fold_S250"]], on="location_id")
fig, ax = plt.subplots(figsize=(7, 4.4))
sc = ax.scatter(sites.Lon_ED, sites.Lat_ED, c=sites.fold_S250, cmap="tab10", s=6, vmin=0, vmax=9)
for _, g in gws.iterrows():
    ax.scatter(g.lon, g.lat, marker="^", s=90, color="k"); ax.annotate(g.gateway, (g.lon, g.lat), xytext=(4, 4), textcoords="offset points")
ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude"); ax.set_title("Measurement locations coloured by 250 m block fold; gateways ▲")
fig.tight_layout(); fig.savefig(FIG / "eda_map_folds_S250.png", dpi=180); plt.close(fig)

for f in ["data_summary", "within_location_variability", "rssi_pathloss_fit", "snr_logdistance_fit"]:
    print(f"\n== {f}\n", pd.read_csv(OUT / f"{f}.csv").to_string(index=False))
print("\n== censoring (median location SNR by valid count)\n", cen.to_string())
print(f"\nAll-file pooled within-location SD: {np.sqrt(allv):.3f} dB over {alln} location-gateway-direction groups")
