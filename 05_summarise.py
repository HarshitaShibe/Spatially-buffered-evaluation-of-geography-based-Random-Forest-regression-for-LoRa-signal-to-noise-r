"""Step 5 - report tables and figures from results/analysis only (no refitting). Run after 07.

Outputs: results/summary/*.csv, results/summary/summary.md, figures/fig1-fig4 PNGs.
Primary vs supplementary labels come from 07 (A4); nothing here changes a number.
Colours: fixed categorical order logdist (blue), rf_dist (orange), rf_loc (aqua); validated with the dataviz
palette checker (all checks pass; aqua below 3:1 contrast, so every line is direct-labelled).
"""
import json
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common import *

A = RES / "analysis"; OUT = RES / "summary"; OUT.mkdir(parents=True, exist_ok=True); FIG.mkdir(exist_ok=True)
BSTAR = json.loads((RES / "calibration" / "buffer_choice.json").read_text())["B_star_m"]
P1 = pd.read_csv(A / "P1_rmse_by_scheme.csv"); P3 = pd.read_csv(A / "P3_paired_gains.csv")
P4 = pd.read_csv(A / "P4_floor_decomposition.csv"); H1 = json.loads((A / "h1_verdict.json").read_text())
P2 = pd.read_csv(A / "P2_error_by_separation.csv")
SCH = ["R", "L", "S250", "S500", "LOBO_B0", "LOBO_B300", "LOBO_B500", "LOBO_B1000"]
LAB = ["Random", "Location", "250 m\nblocks", "500 m\nblocks", "LOBO\n0 m", "LOBO\n300 m", "LOBO\n500 m", "LOBO\n1000 m"]
COL = {"logdist": "#2a78d6", "rf_dist": "#eb6834", "rf_loc": "#1baf7a"}
NAME = {"mean": "Mean", "logdist": "Log-distance fit", "rf_dist": "RF, distance only", "lr_loc": "Linear, location",
        "rf_loc": "RF, location-aware"}
INK, MUTED, GRID = "#1f1f1e", "#6b6a64", "#e4e3de"
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": MUTED,
                     "axes.labelcolor": INK, "xtick.color": MUTED, "ytick.color": MUTED, "axes.titlesize": 10})

def label_ends(ax, x, ends, min_gap_frac=0.07):
    """Direct labels at line ends, nudged apart vertically so they never overlap (ends: {name: y})."""
    lo, hi = ax.get_ylim(); gap = (hi - lo) * min_gap_frac
    items = sorted(ends.items(), key=lambda kv: kv[1]); placed = []
    for name, y in items:
        yy = max(y, placed[-1] + gap) if placed else y
        placed.append(yy)
        ax.annotate(name, (x, y), xytext=(x, yy), textcoords="data", va="center", fontsize=8, color=INK,
                    xycoords="data", annotation_clip=False)


# ---- Table 1: RMSE by scheme
t1 = P1.pivot_table(index=["direction", "model"], columns="scheme", values="RMSE")[SCH].reset_index()
t1["model"] = t1.model.map(NAME); t1.round(2).to_csv(OUT / "table1_rmse_by_scheme.csv", index=False)
# ---- Table 2: paired gains
t2 = P3[(P3.boot_blocks == "block500") & (P3.subset == "all") & P3.comparison.isin(["delta_dist", "delta_loc"])].copy()
t2["estimate"] = t2.apply(lambda r: f"{r.diff_RMSE:+.2f} [{r.ci95_low:+.2f}, {r.ci95_high:+.2f}]", axis=1)
t2 = t2.pivot_table(index=["direction", "comparison"], columns="scheme", values="estimate", aggfunc="first")[SCH].reset_index()
t2.to_csv(OUT / "table2_paired_gains.csv", index=False)
# ---- Table 3: H1
t3 = pd.DataFrame([dict(direction=d, bootstrap=k.split("_")[0].replace("block", "") + " m blocks", test_points=k.split("_")[1],
                        delta_loc_Bstar=v["delta_loc_Bstar"], ci95=f"[{v['ci95'][0]:+.2f}, {v['ci95'][1]:+.2f}]",
                        delta_loc_B0_same_packets=v["delta_loc_B0_same_packets"], packets=v["packets"],
                        change=v["change_Bstar_minus_B0"],
                        change_ci95=f"[{v['change_ci95'][0]:+.2f}, {v['change_ci95'][1]:+.2f}]",
                        classification=v["classification"])
                   for d in DIRECTIONS for k, v in H1[d].items()])
t3.to_csv(OUT / "table3_h1.csv", index=False)
# ---- Table 4: floor
t4 = P4[P4.model == "rf_loc"][["direction", "scheme", "RMSE", "floor_ddof0", "pooled_within_sd_ddof1",
                               "between_location_RMSE", "share_MSE_within"]]
t4.round(3).to_csv(OUT / "table4_floor_rf_loc.csv", index=False)
# ---- Table 5: paired buffer series (A4: B1000 primary on B1000-supported packets; all-packet B1000 supplementary)
P2b = pd.read_csv(A / "P2b_buffer_series_paired.csv")
t5 = P2b[["direction", "subset", "status", "buffer_m", "packets", "RMSE_logdist", "RMSE_rf_dist", "RMSE_rf_loc"]].copy()
for lab in ["delta_dist", "delta_loc"]:
    t5[lab] = P2b.apply(lambda r: f"{r[lab]:+.2f} [{r[lab + '_ci95_low']:+.2f}, {r[lab + '_ci95_high']:+.2f}]", axis=1)
t5.round(2).to_csv(OUT / "table5_buffer_series.csv", index=False)
# ---- Table 6: residual correlation at B* (A5)
RC = H1["residual_correlation_at_Bstar"]
t6 = pd.DataFrame(RC["series"]); t6["ci95"] = t6.ci95.map(lambda c: f"[{c[0]:+.2f}, {c[1]:+.2f}]")
t6.to_csv(OUT / "table6_residual_correlation_at_Bstar.csv", index=False)
(OUT / "summary.md").write_text("\n".join([
    f"# Summary tables (frozen protocol; B* = {BSTAR} m; received-packet SNR, dB)", "",
    "## Table 1. RMSE by scheme", "", t1.round(2).to_markdown(index=False), "",
    "## Table 2. Paired differences, 95% CI (500 m block bootstrap)", "", t2.to_markdown(index=False), "",
    "## Table 3. H1 (delta = 0.5 dB)", "", t3.to_markdown(index=False), "",
    "## Table 4. Floor decomposition, RF location-aware", "", t4.round(3).to_markdown(index=False), "",
    "## Table 5. Paired buffer series (95% CI, 500 m blocks)", "", t5.round(2).to_markdown(index=False), "",
    f"## Table 6. Residual correlation in lag bin {RC['lag_bin_m']} m (rf_dist, L split); "
    f"correlation_not_eliminated = {RC['correlation_not_eliminated']}", "", t6.to_markdown(index=False)]))

# ---- Figure 1: RMSE by scheme
fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True); pending = []
for ax, d in zip(axes, DIRECTIONS):
    x = np.arange(len(SCH))
    ends = {}
    for m in ["logdist", "rf_dist", "rf_loc"]:
        y = [P1[(P1.direction == d) & (P1.scheme == s) & (P1.model == m)].RMSE.iloc[0] for s in SCH]
        ax.plot(x, y, color=COL[m], lw=2, marker="o", ms=5, mec="white", mew=1, zorder=3)
        ends[NAME[m]] = y[-1]
    fl = P4[(P4.direction == d)].floor_ddof0.iloc[0]
    ax.axhline(fl, color=MUTED, ls="--", lw=1)
    ax.text(0, fl + 0.12, f"within-location floor {fl:.2f} dB", color=MUTED, fontsize=8)
    ax.axvspan(3.5, 7.5, color=GRID, alpha=0.5, lw=0, zorder=0)
    ax.set_xticks(x, LAB, fontsize=8); ax.set_title(d, loc="left", color=INK); ax.grid(axis="y", color=GRID, lw=0.6)
    ax.set_xlim(-0.3, 9.6); pending.append((ax, x[-1] + 0.25, ends))
for a in pending:
    label_ends(*a)
axes[0].set_ylabel("Packet-level RMSE (dB)")
fig.suptitle("Packet-level RMSE by evaluation scheme (shaded: buffered leave-one-block-out)",
             x=0.01, ha="left", fontsize=10, color=INK)
fig.tight_layout(); fig.savefig(FIG / "fig1_rmse_by_scheme.png", dpi=200); plt.close(fig)

# ---- Figure 2: gain decomposition with CIs
fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True)
for ax, d in zip(axes, DIRECTIONS):
    x = np.arange(len(SCH))
    ax.axhspan(-0.5, 0.5, color=GRID, alpha=0.6, lw=0, zorder=0)
    ax.axhline(0, color=MUTED, lw=0.8)
    for off, comp, col, lab in [(-0.12, "delta_dist", COL["rf_dist"], "Distance non-linearity (RF dist − log-distance)"),
                                (0.12, "delta_loc", COL["rf_loc"], "Location information (RF loc − RF dist)")]:
        r = [P3[(P3.direction == d) & (P3.scheme == s) & (P3.comparison == comp) & (P3.boot_blocks == "block500")
                & (P3.subset == "all")].iloc[0] for s in SCH]
        y = np.array([q.diff_RMSE for q in r]); lo = np.array([q.ci95_low for q in r]); hi = np.array([q.ci95_high for q in r])
        ax.errorbar(x + off, y, yerr=[y - lo, hi - y], fmt="o", color=col, ms=6, mec="white", mew=1, capsize=0, lw=2,
                    label=lab, zorder=3)
    ax.set_xticks(x, LAB, fontsize=8); ax.set_title(d, loc="left", color=INK); ax.grid(axis="y", color=GRID, lw=0.6)
    ax.annotate("shaded: ±0.5 dB (δ), not practically relevant", (0, 1), xycoords="axes fraction", xytext=(4, -4),
                textcoords="offset points", ha="left", va="top", color=MUTED, fontsize=8)
axes[0].set_ylabel("Paired RMSE difference (dB)\nnegative = more complex model better")
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, frameon=False, fontsize=8, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.02))
fig.suptitle("Where the Random Forest gain comes from, by evaluation scheme (95% CI, 500 m block bootstrap)",
             x=0.01, ha="left", fontsize=10, color=INK)
fig.tight_layout(rect=(0, 0.07, 1, 1)); fig.savefig(FIG / "fig2_gain_decomposition.png", dpi=200); plt.close(fig)

# ---- Figure 3: buffered series, rf_loc vs rf_dist by buffer (paired test set)
fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True); pending = []
bufs = [0, 300, 500, 1000]
for ax, d in zip(axes, DIRECTIONS):
    ends3 = {}
    for m in ["logdist", "rf_dist", "rf_loc"]:
        y = [P1[(P1.direction == d) & (P1.scheme == f"LOBO_B{b}") & (P1.model == m)].RMSE.iloc[0] for b in bufs]
        ys = [P1[(P1.direction == d) & (P1.scheme == f"LOBO_B{b}") & (P1.model == m)].RMSE_supported.iloc[0] for b in bufs]
        ax.plot(bufs, y, color=COL[m], lw=2, marker="o", ms=5, mec="white", mew=1)
        ax.plot(bufs, ys, color=COL[m], lw=1, ls=":", marker="o", ms=3)
        ends3[NAME[m]] = y[-1]
    ax.axvline(BSTAR, color=MUTED, lw=0.8, ls="--")
    ax.annotate(f"B* = {BSTAR} m", (BSTAR, 1), xycoords=("data", "axes fraction"), xytext=(4, -4),
                textcoords="offset points", va="top", color=MUTED, fontsize=8)
    ax.set_xticks(bufs); ax.set_xlim(-50, 1500); ax.set_xlabel("Buffer around test block (m)")
    ax.set_title(d, loc="left", color=INK); ax.grid(axis="y", color=GRID, lw=0.6); pending.append((ax, 1060, ends3))
lo, hi = axes[0].get_ylim(); axes[0].set_ylim(lo, hi + (hi - lo) * 0.15)      # headroom for the B* label
for a in pending:
    label_ends(*a)
axes[0].set_ylabel("Packet-level RMSE (dB)")
fig.suptitle("Same test packets, training removed within the buffer (solid: all; dotted: each buffer's own supported subset, unpaired; see fig 4)",
             x=0.01, ha="left", fontsize=10, color=INK)
fig.tight_layout(); fig.savefig(FIG / "fig3_buffer_series.png", dpi=200); plt.close(fig)
# ---- Figure 4: paired buffer series on the B1000-supported packets (primary for B1000, A4)
fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), sharey=True); pending = []
for ax, d in zip(axes, DIRECTIONS):
    q = P2b[(P2b.direction == d) & (P2b.subset == "B1000_supported")].sort_values("buffer_m")
    for m in ["logdist", "rf_dist", "rf_loc"]:
        ax.plot(q.buffer_m, q[f"RMSE_{m}"], color=COL[m], lw=2, marker="o", ms=5, mec="white", mew=1)
    ax.set_xticks(q.buffer_m); ax.set_xlim(-50, 1500); ax.set_xlabel("Buffer around test block (m)")
    pending.append((ax, 1060, {NAME[m]: q[f"RMSE_{m}"].iloc[-1] for m in ["logdist", "rf_dist", "rf_loc"]}))
    ax.set_title(f"{d} ({int(q.packets.iloc[0]):,} packets)", loc="left", color=INK); ax.grid(axis="y", color=GRID, lw=0.6)
for a in pending:
    label_ends(*a)
axes[0].set_ylabel("Packet-level RMSE (dB)")
fig.suptitle("Same packets at every buffer: those with distance support at 1,000 m", x=0.01, ha="left", fontsize=10, color=INK)
fig.tight_layout(); fig.savefig(FIG / "fig4_buffer_series_B1000_supported.png", dpi=200); plt.close(fig)
print(open(OUT / "summary.md").read())
