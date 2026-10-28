# Status of results in this folder (updated 2026-10-28)

All results are PROVISIONAL. Research scope is pending supervisor approval (see Phase 2 doc, Revision 2).

| File(s) | Status | Known bias / caveat |
| --- | --- | --- |
| results/eda/rssi_pathloss_fit.csv | **Do not report.** Superseded pending Azevedo et al. (2026), IEEE Access | Ordinary least squares on received packets only. Lost (weak) packets are ignored, which biases the path-loss exponent and shadowing sigma; link budget (14 dBm, 1 dBi) is from the dataset page, RSSI calibration unknown. The apparent uplink/downlink difference conflicts with the authors' reported similarity. |
| results/eda/snr_logdistance_fit.csv | Descriptive only | Same packet-loss bias; fitted on all data (not an evaluation result). |
| results/eda/within_location_variability.csv | Provisional | Computed on received packets only; understates spread for weak links. |
| results/eval/*, results/summary/*, predictions/* | Provisional | SNR *given reception*. Packet loss sensitivity (>=4 valid packets, equal location weights) not yet run. Saturation near the gateway not yet analysed. |
| rf_C rows | Diagnostic only | Uses same-packet RSSI; not a planning model. |

Nothing has been deleted or overwritten; the path-loss method will be revised only after reading the original paper.

| results/eval/metrics.csv RMSE_ci95_* | **Too narrow; do not report** | Block bootstrap used 250 m blocks for every split (also S500); residual correlation extends to ~300-500 m (results/audit/F_residual_correlogram.csv). Use results/audit/E_paired_differences.csv until re-run with >=500 m bootstrap blocks. |
| rf_A0 ('no coordinates') | Mislabelled ablation | Distance + bearing + gateway already encode location (polar coordinates); it is not a location-free model. |

## Update 2026-10-28 (protocol frozen)
- Everything above refers to `archive/provisional_2026-10/` (scripts, predictions, results, with SHA256SUMS). The frozen-protocol run replaces `predictions/`, `results/eval/`, `results/analysis/`, `results/summary/`.
- `rssi_pathloss_fit.csv` stays withdrawn. It is superseded by `09_pathloss_reproduction.py`, which follows Azevedo & Mendonca (2026), IEEE Access, doi:10.1109/ACCESS.2026.3730186 (ESP, linear averaging, antenna-height distance). It reproduces their Table 3 to within 0.4 dB in alpha and 0.01 in beta.
- RSSI calibration is now known: the paper states that RSSI was calibrated before analysis.
- `results/audit/` (from the archived `07_audit_cheap.py`) is kept for the record and is superseded by `results/analysis/`.
