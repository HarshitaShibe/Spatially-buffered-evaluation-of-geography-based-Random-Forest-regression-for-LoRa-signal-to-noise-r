"""Step 9 - supporting path-loss analysis: reproduction of Azevedo & Mendonca (2026), IEEE Access,
doi:10.1109/ACCESS.2026.3730186, following their stated method (Sec. II-A, III-B, III-F):
  ESP = RSSI + SNR - 10 log10(1 + 10^(0.1 SNR))                 (their eq. 1)
  per-location mean ESP averaged in the LINEAR domain           (their eq. 3)
  PL = PT + GT + GR - ESP, PT = 14 dBm, GT = GR = 1 dBi           (their eq. 2)
  distance corrected for antenna heights: sqrt(d_h^2 + (h_GW - 3 m)^2)  (our reading of Sec. III-B)
  floating-intercept fit PL = alpha + 10 beta log10 d per gateway  (their eq. 10, Table 3: uplink)
Also: uplink-minus-downlink PL per location (they report mean 0.9 dB, SD 1.5 dB) and received packets /
location coverage (they report 62.0 / 95.8 / 83.5 % of locations for GA / GB / GC).
This is a check of our data handling and a supporting comparison; it is not a new path-loss method.
Outputs: results/pathloss/*.csv, results/pathloss/reproduction.md
"""
import numpy as np, pandas as pd
from common import *

OUT = RES / "pathloss"; OUT.mkdir(parents=True, exist_ok=True)
PAPER_T3 = {"GA": (42.6, 2.79, 11.9), "GB": (54.9, 2.37, 11.1), "GC": (44.4, 2.92, 12.2)}
H = DOCUMENTED["gw_antenna_height_m"]; HT = 3.0
pk = pd.read_csv(PROC / "packets.csv", dtype={"location_id": str})
p = pk.dropna(subset=["rssi_dbm"]).copy()
p["esp"] = p.rssi_dbm + p.snr_db - 10 * np.log10(1 + 10 ** (0.1 * p.snr_db))
L = p.groupby(["direction", "gateway", "location_id"]).agg(
    esp=("esp", lambda x: 10 * np.log10(np.mean(10 ** (x / 10)))), d_h=("distance_m", "first"), n=("esp", "size")).reset_index()
L["pl"] = DOCUMENTED["tx_power_dbm"] + 2 * DOCUMENTED["antenna_gain_dbi"] - L.esp
L["d_3d"] = np.sqrt(L.d_h ** 2 + (L.gateway.map(H) - HT) ** 2)
rows = []
for dist in ["d_3d", "d_h"]:
    for (dr, g), x in L.groupby(["direction", "gateway"]):
        A = np.c_[np.ones(len(x)), 10 * np.log10(x[dist])]; c = np.linalg.lstsq(A, x.pl, rcond=None)[0]
        r = dict(distance=dist, direction=dr, gateway=g, locations=len(x), alpha_dB=c[0], beta=c[1],
                 RMSE_dB=float(np.sqrt(np.mean((A @ c - x.pl) ** 2))))
        if dr == "Uplink":
            r.update(paper_alpha=PAPER_T3[g][0], paper_beta=PAPER_T3[g][1], paper_RMSE=PAPER_T3[g][2])
        rows.append(r)
T = pd.DataFrame(rows); T.round(3).to_csv(OUT / "fi_fit_vs_paper_table3.csv", index=False)
W = L.pivot_table(index=["gateway", "location_id"], columns="direction", values="pl").dropna()
dd = W.Uplink - W.Downlink
cov = pk.groupby(["direction", "gateway"]).agg(packets=("snr_db", "size"), locations=("location_id", "nunique")).reset_index()
cov["share_locations_pct"] = cov.locations / 1203 * 100
cov.round(2).to_csv(OUT / "coverage_vs_paper.csv", index=False)
md = ["# Reproduction of Azevedo & Mendonca (2026)", "",
      "## Floating-intercept fit (paper Table 3 = uplink)", "", T.round(2).to_markdown(index=False), "",
      f"## Uplink minus downlink PL per location: mean {dd.mean():.2f} dB, SD {dd.std():.2f} dB, n = {len(dd)} "
      "(paper: 0.9 dB, SD 1.5 dB)", "",
      "## Received packets and location coverage (paper: 62.0 / 95.8 / 83.5 % of locations)", "",
      cov.round(1).to_markdown(index=False)]
(OUT / "reproduction.md").write_text("\n".join(md)); print("\n".join(md))
