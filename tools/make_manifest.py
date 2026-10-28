"""Packaging helper (not a pipeline stage). Writes MANIFEST.csv for a snapshot directory:
path, bytes, sha256, mtime_utc, provenance class. Classification is mechanical (path + file header +
run_info status), so stale provisional files left in the working tree are labelled, not hidden.
Usage: python3 tools/make_manifest.py <snapshot_dir>
"""
import csv, datetime, hashlib, json, sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
rows = []


def classify(rel, p):
    s = rel.as_posix()
    if s.startswith("archive/"):
        return "ARCHIVED provisional (frozen copy, 27 Oct 2026; never overwritten)"
    if s.startswith("data/raw/"):
        return "RAW input (Mendeley 10.17632/79vh7wnwhg.1, CC BY 4.0; unmodified)"
    if s.startswith("data/processed/") or s.startswith("results/validation_report"):
        return "CURRENT processed data (01_validate; unchanged since 27 Oct)"
    if s.startswith("splits/"):
        return "CURRENT splits (02_splits, frozen protocol, 28 Oct)"
    if s.startswith("predictions/"):
        head = p.open().readline().strip().split(",")
        if "rf_loc" in head or "rf_dist" in head:
            return "FROZEN-RUN output (04/04b)"
        return "STALE provisional file (pre-freeze format; will be overwritten by 04; copy in archive/)"
    if s.startswith("results/eval/"):
        if p.name == "smoke_test.json":
            return "FROZEN-RUN output (04 --smoke, passed)"
        if p.name in ("hp_fixed.json", "chosen_hyperparameters_R1_S250_o0_s0.csv"):
            return "FROZEN-RUN output (04)"
        try:
            info = json.loads((p.parent / "run_info.json").read_text())
            frozen = info.get("status", "").startswith("FROZEN")
        except Exception:
            frozen = False
        if p.name in ("chosen_hyperparameters.csv", "run_info.json"):
            return "FROZEN-RUN output (04)" if frozen else "STALE provisional file (rewritten when 04 finishes; copy in archive/)"
        return "STALE provisional file (not produced by frozen 04; superseded by results/analysis; copy in archive/)"
    if s.startswith("results/summary/"):
        import re
        if re.match(r"table\d", p.name) or p.name == "summary.md":
            return "FROZEN-RUN output (05)"
        return "STALE provisional file (old 05 table name; superseded by table1-6; copy in archive/)"
    if s.startswith(("results/audit/", "results/eda/")) or s == "logs/07_audit_cheap.log":
        return "PROVISIONAL analysis (kept for the record; see PROVISIONAL_STATUS.md)"
    if s.startswith(("results/freeze_checks/", "results/pathloss/", "results/calibration/", "results/analysis/")):
        return "FROZEN-RUN output"
    if s.startswith("figures/eda_"):
        return "PROVISIONAL figure (03_eda)"
    if s.startswith("figures/fig"):
        return "FROZEN-RUN output (05)"
    if s.startswith("logs/"):
        return "LOG"
    if s.startswith("docs/") or s.endswith((".md", ".bib")):
        return "DOCUMENTATION"
    if s.endswith((".py", ".sh", ".txt")):
        return "CODE / CONFIG"
    return "OTHER"


for p in sorted(root.rglob("*")):
    if p.is_file() and "__pycache__" not in p.parts and p.name != "MANIFEST.csv":
        rel = p.relative_to(root)
        rows.append(dict(path=rel.as_posix(), bytes=p.stat().st_size,
                         sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                         mtime_utc=datetime.datetime.fromtimestamp(p.stat().st_mtime, datetime.timezone.utc)
                         .strftime("%Y-%m-%d %H:%M"), provenance=classify(rel, p)))
with (root / "MANIFEST.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
from collections import Counter
for k, v in sorted(Counter(r["provenance"] for r in rows).items()):
    print(f"{v:4d}  {k}")
