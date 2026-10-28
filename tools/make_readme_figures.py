"""README illustration figures (not a pipeline stage; changes no result).

Reads only existing split files and results/analysis/P2b_buffer_series_paired.csv, and writes two PNGs:
  figures/readme_split_concept.png    real locations: location split vs 250 m block vs block + 500 m buffer
  figures/readme_delta_loc.png        location advantage (Delta_loc, 95% CI) vs buffer, from P2b
Usage: python tools/make_readme_figures.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from common import *

INK, MUTED, GRID = "#1f1f1e", "#6b6a64", "#e4e3de"
TEST, TRAIN, DROP = "#eb6834", "#2a78d6", "#8f8d86"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED})

lf = pd.read_csv(SPLITS / "location_folds.csv", dtype={"location_id": str})
ex = pd.read_csv(SPLITS / "lobo_excluded.csv", dtype={"location_id": str})
gw = pd.read_csv(PROC / "gateways.csv")
sites = pd.read_csv(PROC / "sites.csv", dtype={"location_id": str})
lat0, lon0 = sites.Lat_ED.mean(), sites.Lon_ED.mean()          # same origin as 01_validate
gw["x_m"], gw["y_m"] = local_xy_m(gw.lat, gw.lon, lat0, lon0)

# Illustrative block: the 250 m block with the most locations, among blocks near the data centre.
cx, cy = lf.x_m.median(), lf.y_m.median()
cnt = lf.groupby("block250").agg(n=("location_id", "size"), x=("x_m", "mean"), y=("y_m", "mean"))
cnt = cnt[np.hypot(cnt.x - cx, cnt.y - cy) < 1500]
blk = cnt.n.idxmax()
test = lf.block250 == blk
excl = set(ex[(ex.grid == "o0") & (ex.buffer_m == 500) & (ex.block == blk)].location_id)
drop = lf.location_id.isin(excl) & ~test
bx, by = lf.loc[test, "x_m"].mean(), lf.loc[test, "y_m"].mean()
W = 1400
xmin = lf.x_m.min()  # grid origin for 250 m block outline
ymin = lf.y_m.min()
i, j = [int(v) for v in blk.split("_")]
# block id convention check: recompute and pick the outline that contains the test points
cand = [(i, j), (j, i)]
for a, b in cand:
    x0, y0 = xmin + a * 250, ymin + b * 250
    if ((lf.loc[test, "x_m"] >= x0 - 1e-6) & (lf.loc[test, "x_m"] <= x0 + 250 + 1e-6)
            & (lf.loc[test, "y_m"] >= y0 - 1e-6) & (lf.loc[test, "y_m"] <= y0 + 250 + 1e-6)).all():
        break
else:
    x0 = y0 = None

fig, axs = plt.subplots(1, 3, figsize=(12, 4.6), sharex=True, sharey=True)
fL = lf.loc[test, "fold_L"].mode()[0]
panels = [
    ("A  Location split (L)", "Test locations are scattered;\ntheir neighbours stay in training"),
    ("B  250 m block split (S250)", "Whole block held out;\ntraining still touches its edge"),
    ("C  Block + 500 m buffer (LOBO-B500)", "Training within 500 m of any\ntest location is removed"),
]
for k, (ax, (title, sub)) in enumerate(zip(axs, panels)):
    if k == 0:
        t = lf.fold_L == fL; tr = ~t; dr = np.zeros(len(lf), bool)
    elif k == 1:
        t = test; tr = ~test; dr = np.zeros(len(lf), bool)
    else:
        t = test; dr = drop.values; tr = ~test & ~drop
        for _, r in lf[test].iterrows():
            ax.add_patch(Circle((r.x_m, r.y_m), 500, color="#f6e3da", lw=0, zorder=0))
    ax.scatter(lf.x_m[tr], lf.y_m[tr], s=7, color=TRAIN, lw=0, label="training")
    ax.scatter(lf.x_m[dr], lf.y_m[dr], s=7, color=DROP, lw=0, label="removed (buffer)")
    ax.scatter(lf.x_m[t], lf.y_m[t], s=16, color=TEST, lw=0.4, edgecolor="white", label="test", zorder=4)
    if k > 0 and x0 is not None:
        ax.add_patch(Rectangle((x0, y0), 250, 250, fill=False, ec=INK, lw=1))
    ax.scatter(gw.x_m, gw.y_m, marker="^", s=70, color=INK, zorder=5)
    for _, g in gw.iterrows():
        if abs(g.x_m - bx) < W and abs(g.y_m - by) < W:
            ax.annotate(g.gateway, (g.x_m, g.y_m), xytext=(5, 4), textcoords="offset points", fontsize=8, color=INK)
    ax.set_xlim(bx - W, bx + W); ax.set_ylim(by - W, by + W); ax.set_aspect("equal")
    ax.set_title(title, loc="left", color=INK, fontsize=10)
    ax.text(0.02, 0.02, sub, transform=ax.transAxes, fontsize=8, color=MUTED, va="bottom",
            bbox=dict(fc="white", ec="none", alpha=0.85, pad=2))
    ax.set_xlabel("x (m)", color=MUTED)
axs[0].set_ylabel("y (m)", color=MUTED)
h = [plt.Line2D([], [], marker="o", ls="", color=c, ms=5) for c in (TEST, TRAIN, DROP)] + \
    [plt.Line2D([], [], marker="^", ls="", color=INK, ms=7)]
fig.legend(h, ["test locations", "training locations", "removed by buffer", "gateway"], frameon=False,
           loc="upper left", ncol=4, fontsize=9, bbox_to_anchor=(0.005, 0.965))
fig.suptitle("How the evaluation gets stricter (real Funchal locations; one example fold / block)",
             x=0.01, y=1.0, ha="left", fontsize=11, color=INK)
fig.tight_layout(rect=(0, 0, 1, 0.91))
fig.savefig(FIG / "readme_split_concept.png", dpi=160, bbox_inches="tight"); plt.close(fig)
print("block", blk, "test", int(test.sum()), "removed", int(drop.sum()), "outline", x0 is not None)

# ---- Figure 2: Delta_loc vs buffer
p = pd.read_csv(RES / "analysis" / "P2b_buffer_series_paired.csv")
fig, axs = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
for ax, d in zip(axs, ["Uplink", "Downlink"]):
    ax.axhspan(-0.5, 0.5, color="#efeee9", lw=0)
    ax.axhline(0, color=MUTED, lw=0.8)
    ax.text(1040, 0.42, "±0.5 dB: not practically relevant", fontsize=8, color=MUTED, ha="right", va="top")
    for sub, col, off, lab in [("all", "#1baf7a", -12, "all packets (B0–B500)"),
                               ("B1000_supported", "#6b4fbf", 12, "packets supported at 1,000 m (B0–B1000)")]:
        q = p[(p.direction == d) & (p.subset == sub) & (p.status == "primary")].sort_values("buffer_m")
        x = q.buffer_m + off
        ax.plot(x, q.delta_loc, color=col, lw=2, marker="o", ms=6, mec="white", label=lab)
        ax.vlines(x, q.delta_loc_ci95_low, q.delta_loc_ci95_high, color=col, lw=2)
    ax.axvline(500, color=MUTED, ls="--", lw=0.8)
    ax.text(510, -2.05, "B* = 500 m", fontsize=8, color=MUTED)
    ax.set_xticks([0, 300, 500, 1000]); ax.set_xlabel("Buffer around test block (m)", color=MUTED)
    ax.set_title(d, loc="left", color=INK); ax.grid(axis="y", color=GRID, lw=0.6); ax.set_ylim(-2.15, 0.6)
axs[0].set_ylabel("Δloc = RMSE(RF-loc) − RMSE(RF-dist) (dB)\nnegative = location helps", color=MUTED)
hh, ll = axs[0].get_legend_handles_labels()
fig.legend(hh, ll, frameon=False, loc="lower center", ncol=2, fontsize=9, bbox_to_anchor=(0.5, -0.04))
fig.suptitle("The location advantage shrinks as training is pushed away, but does not vanish (95% CI, 500 m block bootstrap)",
             x=0.01, ha="left", fontsize=10, color=INK)
fig.tight_layout(rect=(0, 0.07, 1, 1))
fig.savefig(FIG / "readme_delta_loc.png", dpi=160, bbox_inches="tight"); plt.close(fig)
print("wrote", FIG / "readme_split_concept.png", FIG / "readme_delta_loc.png")
