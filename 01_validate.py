"""Step 1 - load the six Madeira files, run schema/consistency checks, build tidy tables.

Outputs
  data/processed/packets.csv    one row per (location, gateway, direction, slot) with a valid SNR
  data/processed/locations.csv  one row per (location, gateway, direction) incl. rows with 0 valid packets
  data/processed/sites.csv      one row per location (coordinates, local x/y)
  results/validation_report.json, results/validation_report.md
Any failed hard check raises AssertionError so a broken input never flows downstream.
"""
import hashlib, json
import numpy as np, pandas as pd
from common import *

report = {"files": {}, "checks": {}, "notes": []}

frames = []
for gw in GATEWAYS:
    for d in DIRECTIONS:
        f = RAW / f"{gw}_{d}.csv"
        raw_lines = f.read_text(encoding="utf-8-sig").splitlines()
        df = read_raw(gw, d)
        fpl = pd.Series([len(l.split(",")) for l in raw_lines[1:]]).value_counts().to_dict()
        S = df[[f"SNR{i}" for i in SLOTS]]; R = df[[f"RSSI{i}" for i in SLOTS]]
        info = {
            "sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
            "raw_header": raw_lines[0],
            "rows": len(df),
            "fields_per_data_line": {int(k): int(v) for k, v in fpl.items()},
            "duplicate_rows": int(df.duplicated().sum()),
            "duplicate_ids": int(df.ID.duplicated().sum()),
            "gateway_coords": df[["Lat_GW", "Lon_GW"]].drop_duplicates().values.tolist(),
            "missing_device_coords": int(df[["Lat_ED", "Lon_ED"]].isna().any(axis=1).sum()),
            "unparsed_timestamps": int(pd.to_datetime(df.Timestamp, format=TS_FORMAT, errors="coerce").isna().sum()),
            "valid_snr_cells": int(S.notna().sum().sum()),
            "valid_rssi_cells": int(R.notna().sum().sum()),
            "snr_without_rssi": int((S.notna().values & R.isna().values).sum()),
            "rssi_without_snr": int((R.notna().values & S.isna().values).sum()),
            "snr_non_integer": int((S.stack() % 1 != 0).sum()),
            "snr_range": [float(S.min().min()), float(S.max().max())],
            "rssi_range": [float(R.min().min()), float(R.max().max())],
        }
        report["files"][f"{gw}_{d}"] = info
        frames.append(df)

# ---- hard checks
for k, v in report["files"].items():
    assert v["rows"] == 1203, k
    assert v["fields_per_data_line"] == {22: 1203}, k
    assert v["duplicate_rows"] == 0 and v["duplicate_ids"] == 0, k
    assert len(v["gateway_coords"]) == 1, f"{k}: gateway coordinates not constant"
    assert v["missing_device_coords"] == 0 and v["unparsed_timestamps"] == 0, k
all_ = pd.concat(frames, ignore_index=True)
base = all_[(all_.gateway == "GA") & (all_.direction == "Uplink")].set_index("ID")[["Lat_ED", "Lon_ED"]]
for (gw, d), g in all_.groupby(["gateway", "direction"]):
    g = g.set_index("ID")[["Lat_ED", "Lon_ED"]]
    assert g.index.equals(base.index) and np.allclose(g.values, base.values), f"{gw}_{d}: device coords differ"
report["checks"]["same_1203_locations_in_all_files"] = True

ts = pd.to_datetime(all_.Timestamp, format=TS_FORMAT)
all_["ts"] = ts
piv = all_.pivot_table(index="ID", columns=["gateway", "direction"], values="ts", aggfunc="first")
report["checks"]["uplink_downlink_same_timestamp"] = bool(all(
    (piv[(g, "Uplink")] == piv[(g, "Downlink")]).all() for g in GATEWAYS))
off = {g: sorted((piv[(g, "Uplink")] - piv[("GA", "Uplink")]).dt.total_seconds().unique().tolist()) for g in GATEWAYS}
report["checks"]["gateway_poll_offsets_vs_GA_s"] = off
report["checks"]["campaign_days"] = int(ts.dt.date.nunique())
report["checks"]["campaign_range"] = [str(ts.min()), str(ts.max())]

# ---- tidy tables
sites = base.reset_index().rename(columns={"ID": "location_id"})
lat0, lon0 = sites.Lat_ED.mean(), sites.Lon_ED.mean()
sites["x_m"], sites["y_m"] = local_xy_m(sites.Lat_ED, sites.Lon_ED, lat0, lon0)
sites.attrs = {}
gw_xy = {}
for gw in GATEWAYS:
    la, lo = report["files"][f"{gw}_Uplink"]["gateway_coords"][0]
    gw_xy[gw] = dict(lat=la, lon=lo)

long_rows, loc_rows = [], []
for df in frames:
    gw, d = df.gateway.iloc[0], df.direction.iloc[0]
    g = gw_xy[gw]
    dist = haversine_m(g["lat"], g["lon"], df.Lat_ED.values, df.Lon_ED.values)
    brg = bearing_deg(g["lat"], g["lon"], df.Lat_ED.values, df.Lon_ED.values)
    S = df[[f"SNR{i}" for i in SLOTS]].values; R = df[[f"RSSI{i}" for i in SLOTS]].values
    n_valid = (~np.isnan(S)).sum(1)
    with np.errstate(all="ignore"):
        mean = np.nanmean(S, 1); med = np.nanmedian(S, 1)
        sd = np.array([np.std(r[~np.isnan(r)], ddof=1) if (~np.isnan(r)).sum() >= 2 else np.nan for r in S])
        rmean = np.nanmean(R, 1)
    loc_rows.append(pd.DataFrame(dict(location_id=df.ID, gateway=gw, direction=d, timestamp=df.Timestamp,
                                      distance_m=dist, bearing_deg=brg, n_valid=n_valid, snr_mean=mean,
                                      snr_median=med, snr_sd=sd, rssi_mean=rmean)))
    for j, s in enumerate(SLOTS):
        keep = ~np.isnan(S[:, j])
        long_rows.append(pd.DataFrame(dict(location_id=df.ID.values[keep], gateway=gw, direction=d, slot=s,
                                           snr_db=S[keep, j], rssi_dbm=R[keep, j],
                                           distance_m=dist[keep], bearing_deg=brg[keep])))
packets = pd.concat(long_rows, ignore_index=True).merge(sites[["location_id", "Lat_ED", "Lon_ED", "x_m", "y_m"]], on="location_id")
locs = pd.concat(loc_rows, ignore_index=True).merge(sites[["location_id", "Lat_ED", "Lon_ED", "x_m", "y_m"]], on="location_id")
packets["log10_d"] = np.log10(packets.distance_m)
locs["log10_d"] = np.log10(locs.distance_m)
packets = packets.sort_values(["direction", "gateway", "location_id", "slot"]).reset_index(drop=True)

assert len(packets) == sum(v["valid_snr_cells"] for v in report["files"].values())
PROC.mkdir(parents=True, exist_ok=True)
packets.to_csv(PROC / "packets.csv", index=False)
locs.to_csv(PROC / "locations.csv", index=False)
sites.to_csv(PROC / "sites.csv", index=False)
pd.DataFrame([dict(gateway=k, **v, **{"documented_height_m": DOCUMENTED["gw_antenna_height_m"][k],
                                      "documented_freq_mhz": DOCUMENTED["freq_mhz"][k]}) for k, v in gw_xy.items()]
             ).to_csv(PROC / "gateways.csv", index=False)

report["checks"]["packet_rows"] = len(packets)
report["checks"]["packet_rows_rssi_missing"] = int(packets.rssi_dbm.isna().sum())
report["checks"]["locations_with_no_packet_at_any_gateway"] = int(
    (locs.groupby("location_id").n_valid.sum() == 0).sum())
report["checks"]["valid_packets_by_file"] = packets.groupby(["gateway", "direction"]).size().unstack().to_dict()
report["notes"] += [
    "GB_Uplink and GC_Uplink headers are malformed in the raw files (quoted, 'RSSI1;RSSI1'); read with fixed names.",
    "GC_Downlink header uses 'Latitude_Gc'; harmless with fixed names.",
    "Slots carry no individual timestamps; the row timestamp is one per (location, gateway).",
    "Units are not written in the files; values are consistent with dBm (RSSI) and dB (SNR).",
    "SF, bandwidth, Tx power, frequency, antenna heights and environment labels are NOT in the files.",
]
(RES / "validation_report.json").write_text(json.dumps(report, indent=1, default=str))

md = ["# Madeira data validation report", "", "All hard checks passed (script would have stopped otherwise).", "",
      "| File | Rows | Valid SNR | SNR range | RSSI range | SNR w/o RSSI | RSSI w/o SNR | sha256 (first 12) |",
      "|---|---|---|---|---|---|---|---|"]
for k, v in report["files"].items():
    md.append(f"| {k} | {v['rows']} | {v['valid_snr_cells']} | {v['snr_range']} | {v['rssi_range']} | "
              f"{v['snr_without_rssi']} | {v['rssi_without_snr']} | {v['sha256'][:12]} |")
md += ["", "## Cross-file checks", ""] + [f"- **{k}**: {v}" for k, v in report["checks"].items()]
md += ["", "## Notes", ""] + [f"- {n}" for n in report["notes"]]
(RES / "validation_report.md").write_text("\n".join(md))
print("\n".join(md))
