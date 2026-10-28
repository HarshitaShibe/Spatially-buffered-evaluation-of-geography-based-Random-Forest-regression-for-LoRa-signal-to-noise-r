"""Shared constants and helpers for the Madeira LoRa SNR pipeline.

Scope is PROVISIONAL (pending supervisor approval). Nothing here encodes results.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
SPLITS = ROOT / "splits"
RES = ROOT / "results"
PRED = ROOT / "predictions"
FIG = ROOT / "figures"

SEED = 20251028
GATEWAYS = ["GA", "GB", "GC"]
DIRECTIONS = ["Uplink", "Downlink"]
SLOTS = list(range(1, 9))
# Canonical column names. Two raw files (GB_Uplink, GC_Uplink) have a malformed
# quoted header ("RSSI1;RSSI1", no RSSI2) and GC_Downlink spells "Latitude_Gc",
# so every file is read with header=None, skiprows=1 and these names.
COLS = (["ID", "Timestamp", "Lat_GW", "Lon_GW", "Lat_ED", "Lon_ED"]
        + [f"RSSI{i}" for i in SLOTS] + [f"SNR{i}" for i in SLOTS])
TS_FORMAT = "%d/%m/%Y-%H:%M:%S"

# From the Mendeley record page (not in the files): documented, not verified in data.
DOCUMENTED = {
    "sf": 12, "bw_khz": 125, "cr": "4/5", "tx_power_dbm": 14, "antenna_gain_dbi": 1,
    "freq_mhz": {"GA": 868.1, "GB": 868.3, "GC": 868.5},
    "gw_antenna_height_m": {"GA": 27, "GB": 7, "GC": 20},
}


def read_raw(gw: str, direction: str) -> pd.DataFrame:
    f = RAW / f"{gw}_{direction}.csv"
    df = pd.read_csv(f, header=None, skiprows=1, names=COLS, dtype={"ID": str})
    df["gateway"] = gw
    df["direction"] = direction
    return df


def haversine_m(lat1, lon1, lat2, lon2):
    R = 6371000.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp, dl = p2 - p1, np.radians(np.asarray(lon2) - np.asarray(lon1))
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


def bearing_deg(lat1, lon1, lat2, lon2):
    """Initial bearing from point 1 (gateway) to point 2 (device), degrees 0-360."""
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dl = np.radians(np.asarray(lon2) - np.asarray(lon1))
    x = np.sin(dl) * np.cos(p2)
    y = np.cos(p1) * np.sin(p2) - np.sin(p1) * np.cos(p2) * np.cos(dl)
    return (np.degrees(np.arctan2(x, y)) + 360) % 360


def local_xy_m(lat, lon, lat0, lon0):
    """Equirectangular projection to metres around (lat0, lon0); adequate over ~5 km."""
    R = 6371000.0
    x = R * np.radians(np.asarray(lon) - lon0) * np.cos(np.radians(lat0))
    y = R * np.radians(np.asarray(lat) - lat0)
    return x, y
