# Frozen-protocol analysis (received-packet SNR; all values computed from saved predictions)

B* = 500 m (from results/calibration/buffer_choice.json); delta = 0.5 dB; bootstrap = 2000 paired replicates over 500 m blocks (1,000 m as sensitivity).

## P1. RMSE (dB) by scheme

|                         |     R |     L |   S250 |   S500 |   LOBO_B0 |   LOBO_B300 |   LOBO_B500 |   LOBO_B1000 |
|:------------------------|------:|------:|-------:|-------:|----------:|------------:|------------:|-------------:|
| ('Downlink', 'logdist') | 6.099 | 6.103 |  6.165 |  6.315 |     6.157 |       6.41  |       6.896 |        9.686 |
| ('Downlink', 'lr_loc')  | 5.695 | 5.703 |  5.8   |  5.867 |     5.774 |       6.002 |       6.239 |        6.602 |
| ('Downlink', 'mean')    | 6.818 | 6.826 |  6.918 |  6.964 |     6.875 |       7.142 |       7.38  |        7.659 |
| ('Downlink', 'rf_dist') | 4.205 | 5.979 |  6.253 |  6.62  |     6.218 |       6.704 |       7     |        8.422 |
| ('Downlink', 'rf_loc')  | 3.259 | 4.479 |  4.934 |  5.657 |     4.88  |       5.787 |       6.13  |        7.509 |
| ('Uplink', 'logdist')   | 6.963 | 6.972 |  7.042 |  7.174 |     7.028 |       7.282 |       7.708 |       10.254 |
| ('Uplink', 'lr_loc')    | 6.576 | 6.589 |  6.708 |  6.757 |     6.66  |       6.857 |       7.042 |        7.699 |
| ('Uplink', 'mean')      | 7.952 | 7.964 |  8.069 |  8.093 |     8.02  |       8.306 |       8.561 |        8.905 |
| ('Uplink', 'rf_dist')   | 4.613 | 6.861 |  7.113 |  7.377 |     7.102 |       7.481 |       7.735 |        8.316 |
| ('Uplink', 'rf_loc')    | 3.611 | 5.03  |  5.719 |  6.396 |     5.585 |       6.654 |       6.918 |        8.036 |

## P3. Paired RMSE differences (dB; negative = first model better), 500 m blocks

|                            |      R |      L |   S250 |   S500 |   LOBO_B0 |   LOBO_B300 |   LOBO_B500 |   LOBO_B1000 |
|:---------------------------|-------:|-------:|-------:|-------:|----------:|------------:|------------:|-------------:|
| ('Downlink', 'delta_dist') | -1.893 | -0.123 |  0.088 |  0.305 |     0.061 |       0.293 |       0.104 |       -1.264 |
| ('Downlink', 'delta_loc')  | -0.946 | -1.501 | -1.319 | -0.963 |    -1.338 |      -0.917 |      -0.871 |       -0.913 |
| ('Downlink', 'total')      | -2.84  | -1.624 | -1.231 | -0.658 |    -1.277 |      -0.623 |      -0.766 |       -2.177 |
| ('Uplink', 'delta_dist')   | -2.35  | -0.111 |  0.07  |  0.203 |     0.073 |       0.199 |       0.027 |       -1.937 |
| ('Uplink', 'delta_loc')    | -1.001 | -1.831 | -1.393 | -0.981 |    -1.517 |      -0.827 |      -0.818 |       -0.28  |
| ('Uplink', 'total')        | -3.351 | -1.943 | -1.323 | -0.778 |    -1.443 |      -0.628 |      -0.791 |       -2.217 |

## H1 verdict (primary: 500 m blocks, all test packets)

```
{
 "Uplink": {
  "block500_all": {
   "delta_loc_Bstar": -0.818,
   "ci95": [
    -1.198,
    -0.456
   ],
   "classification": "inconclusive",
   "delta_loc_B0_same_packets": -1.517,
   "delta_loc_B0_ci95": [
    -1.808,
    -1.216
   ],
   "change_Bstar_minus_B0": 0.699,
   "change_ci95": [
    0.364,
    0.95
   ],
   "packets": 18519
  },
  "block500_supported": {
   "delta_loc_Bstar": -0.887,
   "ci95": [
    -1.258,
    -0.522
   ],
   "classification": "practically relevant location advantage persists",
   "delta_loc_B0_same_packets": -1.587,
   "delta_loc_B0_ci95": [
    -1.879,
    -1.261
   ],
   "change_Bstar_minus_B0": 0.7,
   "change_ci95": [
    0.353,
    0.97
   ],
   "packets": 17091
  },
  "block1000_all": {
   "delta_loc_Bstar": -0.818,
   "ci95": [
    -1.359,
    -0.493
   ],
   "classification": "inconclusive",
   "delta_loc_B0_same_packets": -1.517,
   "delta_loc_B0_ci95": [
    -1.779,
    -1.347
   ],
   "change_Bstar_minus_B0": 0.699,
   "change_ci95": [
    0.204,
    1.003
   ],
   "packets": 18519
  },
  "block1000_supported": {
   "delta_loc_Bstar": -0.887,
   "ci95": [
    -1.371,
    -0.577
   ],
   "classification": "practically relevant location advantage persists",
   "delta_loc_B0_same_packets": -1.587,
   "delta_loc_B0_ci95": [
    -1.811,
    -1.416
   ],
   "change_Bstar_minus_B0": 0.7,
   "change_ci95": [
    0.192,
    1.03
   ],
   "packets": 17091
  }
 },
 "Downlink": {
  "block500_all": {
   "delta_loc_Bstar": -0.871,
   "ci95": [
    -1.35,
    -0.416
   ],
   "classification": "inconclusive",
   "delta_loc_B0_same_packets": -1.338,
   "delta_loc_B0_ci95": [
    -1.63,
    -1.039
   ],
   "change_Bstar_minus_B0": 0.467,
   "change_ci95": [
    0.046,
    0.858
   ],
   "packets": 18510
  },
  "block500_supported": {
   "delta_loc_Bstar": -1.018,
   "ci95": [
    -1.458,
    -0.598
   ],
   "classification": "practically relevant location advantage persists",
   "delta_loc_B0_same_packets": -1.398,
   "delta_loc_B0_ci95": [
    -1.706,
    -1.08
   ],
   "change_Bstar_minus_B0": 0.38,
   "change_ci95": [
    0.008,
    0.725
   ],
   "packets": 17082
  },
  "block1000_all": {
   "delta_loc_Bstar": -0.871,
   "ci95": [
    -1.472,
    -0.49
   ],
   "classification": "inconclusive",
   "delta_loc_B0_same_packets": -1.338,
   "delta_loc_B0_ci95": [
    -1.587,
    -1.148
   ],
   "change_Bstar_minus_B0": 0.467,
   "change_ci95": [
    -0.023,
    0.749
   ],
   "packets": 18510
  },
  "block1000_supported": {
   "delta_loc_Bstar": -1.018,
   "ci95": [
    -1.546,
    -0.649
   ],
   "classification": "practically relevant location advantage persists",
   "delta_loc_B0_same_packets": -1.398,
   "delta_loc_B0_ci95": [
    -1.609,
    -1.211
   ],
   "change_Bstar_minus_B0": 0.38,
   "change_ci95": [
    -0.062,
    0.657
   ],
   "packets": 17082
  }
 },
 "primary": {
  "Uplink": "inconclusive",
  "Downlink": "inconclusive"
 },
 "general_claim_allowed": true,
 "residual_correlation_at_Bstar": {
  "B_star_m": 500,
  "lag_bin_m": "[500,1000)",
  "correlation_not_eliminated": true,
  "estimator": "location-mean rf_dist residuals, L split, 500 m block bootstrap (attenuated by within-location noise)",
  "series": [
   {
    "direction": "Uplink",
    "gateway": "GA",
    "pairs": 69111,
    "correlation": -0.039,
    "ci95": [
     -0.152,
     0.084
    ]
   },
   {
    "direction": "Uplink",
    "gateway": "GB",
    "pairs": 145294,
    "correlation": -0.021,
    "ci95": [
     -0.069,
     0.007
    ]
   },
   {
    "direction": "Uplink",
    "gateway": "GC",
    "pairs": 122058,
    "correlation": 0.08,
    "ci95": [
     -0.035,
     0.226
    ]
   },
   {
    "direction": "Downlink",
    "gateway": "GA",
    "pairs": 68951,
    "correlation": -0.009,
    "ci95": [
     -0.117,
     0.119
    ]
   },
   {
    "direction": "Downlink",
    "gateway": "GB",
    "pairs": 145294,
    "correlation": -0.002,
    "ci95": [
     -0.06,
     0.037
    ]
   },
   {
    "direction": "Downlink",
    "gateway": "GC",
    "pairs": 122058,
    "correlation": 0.085,
    "ci95": [
     -0.023,
     0.222
    ]
   }
  ]
 }
}
```

## P1b. Buffered schemes paired against LOBO-B0 (S250, L rows: cross-family context only)

| direction   | scheme     | model   |   diff_vs_LOBO_B0 |   ci95_low |   ci95_high |
|:------------|:-----------|:--------|------------------:|-----------:|------------:|
| Uplink      | LOBO_B300  | logdist |             0.254 |      0.17  |       0.337 |
| Uplink      | LOBO_B300  | rf_dist |             0.379 |      0.218 |       0.538 |
| Uplink      | LOBO_B300  | rf_loc  |             1.069 |      0.763 |       1.331 |
| Uplink      | LOBO_B500  | logdist |             0.68  |      0.405 |       0.962 |
| Uplink      | LOBO_B500  | rf_dist |             0.634 |      0.401 |       0.941 |
| Uplink      | LOBO_B500  | rf_loc  |             1.333 |      1.095 |       1.542 |
| Uplink      | LOBO_B1000 | logdist |             3.225 |      1.292 |       5.14  |
| Uplink      | LOBO_B1000 | rf_dist |             1.214 |      0.77  |       1.711 |
| Uplink      | LOBO_B1000 | rf_loc  |             2.452 |      1.852 |       3.048 |
| Uplink      | S250       | logdist |             0.014 |     -0.014 |       0.039 |
| Uplink      | S250       | rf_dist |             0.011 |     -0.045 |       0.064 |
| Uplink      | S250       | rf_loc  |             0.135 |      0.041 |       0.246 |
| Uplink      | L          | logdist |            -0.056 |     -0.074 |      -0.038 |
| Uplink      | L          | rf_dist |            -0.241 |     -0.338 |      -0.152 |
| Uplink      | L          | rf_loc  |            -0.555 |     -0.768 |      -0.369 |
| Downlink    | LOBO_B300  | logdist |             0.253 |      0.154 |       0.355 |
| Downlink    | LOBO_B300  | rf_dist |             0.486 |      0.323 |       0.653 |
| Downlink    | LOBO_B300  | rf_loc  |             0.907 |      0.662 |       1.146 |
| Downlink    | LOBO_B500  | logdist |             0.739 |      0.392 |       1.112 |
| Downlink    | LOBO_B500  | rf_dist |             0.782 |      0.506 |       1.142 |
| Downlink    | LOBO_B500  | rf_loc  |             1.25  |      0.852 |       1.609 |
| Downlink    | LOBO_B1000 | logdist |             3.53  |      1.27  |       5.694 |
| Downlink    | LOBO_B1000 | rf_dist |             2.204 |      1.082 |       3.344 |
| Downlink    | LOBO_B1000 | rf_loc  |             2.629 |      1.618 |       3.565 |
| Downlink    | S250       | logdist |             0.008 |     -0.023 |       0.036 |
| Downlink    | S250       | rf_dist |             0.035 |     -0.026 |       0.1   |
| Downlink    | S250       | rf_loc  |             0.054 |     -0.033 |       0.132 |
| Downlink    | L          | logdist |            -0.054 |     -0.076 |      -0.034 |
| Downlink    | L          | rf_dist |            -0.239 |     -0.303 |      -0.172 |
| Downlink    | L          | rf_loc  |            -0.401 |     -0.527 |      -0.275 |

## P1c. Grouped schemes paired against S250 (500 m blocks)

| direction   | scheme   | model   | boot_blocks   |   diff_vs_S250 |   ci95_low |   ci95_high |
|:------------|:---------|:--------|:--------------|---------------:|-----------:|------------:|
| Uplink      | R        | mean    | block500      |         -0.116 |     -0.169 |      -0.061 |
| Uplink      | R        | logdist | block500      |         -0.08  |     -0.109 |      -0.045 |
| Uplink      | R        | rf_dist | block500      |         -2.5   |     -2.725 |      -2.252 |
| Uplink      | R        | lr_loc  | block500      |         -0.133 |     -0.213 |      -0.073 |
| Uplink      | R        | rf_loc  | block500      |         -2.108 |     -2.404 |      -1.876 |
| Uplink      | L        | mean    | block500      |         -0.104 |     -0.154 |      -0.052 |
| Uplink      | L        | logdist | block500      |         -0.07  |     -0.099 |      -0.035 |
| Uplink      | L        | rf_dist | block500      |         -0.252 |     -0.361 |      -0.155 |
| Uplink      | L        | lr_loc  | block500      |         -0.12  |     -0.195 |      -0.061 |
| Uplink      | L        | rf_loc  | block500      |         -0.69  |     -0.992 |      -0.438 |
| Uplink      | S500     | mean    | block500      |          0.024 |     -0.083 |       0.131 |
| Uplink      | S500     | logdist | block500      |          0.132 |      0.03  |       0.23  |
| Uplink      | S500     | rf_dist | block500      |          0.264 |      0.044 |       0.484 |
| Uplink      | S500     | lr_loc  | block500      |          0.048 |     -0.076 |       0.182 |
| Uplink      | S500     | rf_loc  | block500      |          0.677 |      0.341 |       1.042 |
| Downlink    | R        | mean    | block500      |         -0.1   |     -0.159 |      -0.037 |
| Downlink    | R        | logdist | block500      |         -0.066 |     -0.096 |      -0.034 |
| Downlink    | R        | rf_dist | block500      |         -2.047 |     -2.254 |      -1.847 |
| Downlink    | R        | lr_loc  | block500      |         -0.105 |     -0.145 |      -0.063 |
| Downlink    | R        | rf_loc  | block500      |         -1.675 |     -1.882 |      -1.508 |
| Downlink    | L        | mean    | block500      |         -0.092 |     -0.15  |      -0.03  |
| Downlink    | L        | logdist | block500      |         -0.062 |     -0.093 |      -0.029 |
| Downlink    | L        | rf_dist | block500      |         -0.273 |     -0.372 |      -0.184 |
| Downlink    | L        | lr_loc  | block500      |         -0.097 |     -0.138 |      -0.055 |
| Downlink    | L        | rf_loc  | block500      |         -0.455 |     -0.586 |      -0.309 |
| Downlink    | S500     | mean    | block500      |          0.046 |     -0.069 |       0.156 |
| Downlink    | S500     | logdist | block500      |          0.151 |      0.035 |       0.271 |
| Downlink    | S500     | rf_dist | block500      |          0.368 |      0.129 |       0.627 |
| Downlink    | S500     | lr_loc  | block500      |          0.067 |     -0.011 |       0.153 |
| Downlink    | S500     | rf_loc  | block500      |          0.724 |      0.38  |       1.055 |

## P2a. RMSE by distance to nearest training location

| direction   | scheme     | subset          | status                | sep_band_m      |   packets |   locations |   median_distance_to_gw_m |   RMSE_logdist |   RMSE_rf_dist |   RMSE_rf_loc |
|:------------|:-----------|:----------------|:----------------------|:----------------|----------:|------------:|--------------------------:|---------------:|---------------:|--------------:|
| Uplink      | L          | all             | primary (descriptive) | [0.0, 25.0)     |      3197 |         202 |                    709.49 |           6.81 |           6.9  |          4.53 |
| Uplink      | L          | all             | primary (descriptive) | [25.0, 50.0)    |      8473 |         562 |                    897.38 |           6.82 |           6.7  |          4.96 |
| Uplink      | L          | all             | primary (descriptive) | [50.0, 100.0)   |      6432 |         410 |                   1161.7  |           7.26 |           7.06 |          5.3  |
| Uplink      | L          | all             | primary (descriptive) | [100.0, 200.0)  |       417 |          25 |                   1194.54 |           6.74 |           6.75 |          5.72 |
| Uplink      | S250       | all             | primary (descriptive) | [0.0, 25.0)     |       317 |          21 |                    683.3  |           7.1  |           7.5  |          5.09 |
| Uplink      | S250       | all             | primary (descriptive) | [25.0, 50.0)    |      2918 |         194 |                    855.18 |           7.19 |           7.2  |          5.14 |
| Uplink      | S250       | all             | primary (descriptive) | [50.0, 100.0)   |      8749 |         565 |                    960.77 |           7.03 |           7.05 |          5.75 |
| Uplink      | S250       | all             | primary (descriptive) | [100.0, 200.0)  |      6367 |         402 |                    973.06 |           7.02 |           7.18 |          5.93 |
| Uplink      | S250       | all             | primary (descriptive) | [200.0, 300.0)  |       141 |          14 |                   1406.32 |           5.43 |           4.95 |          6.79 |
| Uplink      | S250       | all             | primary (descriptive) | [300.0, 500.0)  |        27 |           3 |                   1194.54 |           5.31 |           4.7  |          5.75 |
| Uplink      | S500       | all             | primary (descriptive) | [0.0, 25.0)     |       210 |          12 |                    672.65 |           6.88 |           7.14 |          4.97 |
| Uplink      | S500       | all             | primary (descriptive) | [25.0, 50.0)    |      1241 |          86 |                    841.51 |           6.92 |           6.49 |          5.1  |
| Uplink      | S500       | all             | primary (descriptive) | [50.0, 100.0)   |      4736 |         310 |                    909.29 |           7.37 |           7.34 |          6.24 |
| Uplink      | S500       | all             | primary (descriptive) | [100.0, 200.0)  |      7758 |         480 |                    865.26 |           7.14 |           7.5  |          6.48 |
| Uplink      | S500       | all             | primary (descriptive) | [200.0, 300.0)  |      3574 |         237 |                   1006.82 |           7.2  |           7.45 |          6.79 |
| Uplink      | S500       | all             | primary (descriptive) | [300.0, 500.0)  |       979 |          72 |                   1541.99 |           6.75 |           7.45 |          6.8  |
| Uplink      | S500       | all             | primary (descriptive) | [500.0, 1000.0) |        21 |           2 |                   1657.89 |           4.93 |           3.81 |          4.13 |
| Uplink      | LOBO_B0    | all             | primary (descriptive) | [0.0, 25.0)     |       399 |          26 |                    680.91 |           7.15 |           7.08 |          4.66 |
| Uplink      | LOBO_B0    | all             | primary (descriptive) | [25.0, 50.0)    |      3303 |         221 |                    860.97 |           7.15 |           7.19 |          5.14 |
| Uplink      | LOBO_B0    | all             | primary (descriptive) | [50.0, 100.0)   |      9449 |         613 |                    954.48 |           7.02 |           7.01 |          5.68 |
| Uplink      | LOBO_B0    | all             | primary (descriptive) | [100.0, 200.0)  |      5271 |         330 |                    987.21 |           6.98 |           7.24 |          5.72 |
| Uplink      | LOBO_B0    | all             | primary (descriptive) | [200.0, 300.0)  |        97 |           9 |                   1280.01 |           5.71 |           5.43 |          7.18 |
| Uplink      | LOBO_B300  | all             | primary (descriptive) | [300.0, 500.0)  |     18497 |        1198 |                    936.15 |           7.28 |           7.48 |          6.66 |
| Uplink      | LOBO_B300  | all             | primary (descriptive) | [500.0, 1000.0) |        22 |           1 |                   1474.11 |          10.49 |           9.8  |          5.76 |
| Uplink      | LOBO_B500  | all             | primary (descriptive) | [500.0, 1000.0) |     18519 |        1199 |                    938.45 |           7.71 |           7.74 |          6.92 |
| Uplink      | LOBO_B1000 | B1000_supported | primary (descriptive) | [1000.0, inf)   |     14179 |        1176 |                   1072.43 |           8.11 |           8.38 |          7.79 |
| Uplink      | LOBO_B1000 | all             | supplementary         | [1000.0, inf)   |     18519 |        1199 |                    938.45 |          10.25 |           8.32 |          8.04 |
| Downlink    | L          | all             | primary (descriptive) | [0.0, 25.0)     |      3195 |         202 |                    709.49 |           5.5  |           5.56 |          3.75 |
| Downlink    | L          | all             | primary (descriptive) | [25.0, 50.0)    |      8468 |         562 |                    897.38 |           5.96 |           5.9  |          4.37 |
| Downlink    | L          | all             | primary (descriptive) | [50.0, 100.0)   |      6430 |         410 |                   1161.7  |           6.55 |           6.26 |          4.87 |
| Downlink    | L          | all             | primary (descriptive) | [100.0, 200.0)  |       417 |          25 |                   1194.54 |           6.19 |           6.29 |          5.34 |
| Downlink    | S250       | all             | primary (descriptive) | [0.0, 25.0)     |       315 |          21 |                    683.3  |           6.16 |           6.45 |          4.52 |
| Downlink    | S250       | all             | primary (descriptive) | [25.0, 50.0)    |      2913 |         194 |                    855.18 |           6.01 |           6.01 |          4.34 |
| Downlink    | S250       | all             | primary (descriptive) | [50.0, 100.0)   |      8748 |         565 |                    960.77 |           6.23 |           6.28 |          4.93 |
| Downlink    | S250       | all             | primary (descriptive) | [100.0, 200.0)  |      6366 |         402 |                    973.06 |           6.15 |           6.33 |          5.18 |
| Downlink    | S250       | all             | primary (descriptive) | [200.0, 300.0)  |       141 |          14 |                   1406.32 |           5.63 |           5.75 |          5.82 |
| Downlink    | S250       | all             | primary (descriptive) | [300.0, 500.0)  |        27 |           3 |                   1194.54 |           4.63 |           5.38 |          5.84 |
| Downlink    | S500       | all             | primary (descriptive) | [0.0, 25.0)     |       210 |          12 |                    672.65 |           5.47 |           5.85 |          4.57 |
| Downlink    | S500       | all             | primary (descriptive) | [25.0, 50.0)    |      1237 |          86 |                    772.86 |           6.05 |           5.79 |          4.62 |
| Downlink    | S500       | all             | primary (descriptive) | [50.0, 100.0)   |      4735 |         310 |                    909.29 |           6.41 |           6.49 |          5.39 |
| Downlink    | S500       | all             | primary (descriptive) | [100.0, 200.0)  |      7756 |         480 |                    865.26 |           6.29 |           6.61 |          5.61 |
| Downlink    | S500       | all             | primary (descriptive) | [200.0, 300.0)  |      3572 |         237 |                   1006.82 |           6.51 |           6.99 |          5.98 |
| Downlink    | S500       | all             | primary (descriptive) | [300.0, 500.0)  |       979 |          72 |                   1541.99 |           5.89 |           7.12 |          7.28 |
| Downlink    | S500       | all             | primary (descriptive) | [500.0, 1000.0) |        21 |           2 |                   1657.89 |           3.65 |           3.77 |          4.89 |
| Downlink    | LOBO_B0    | all             | primary (descriptive) | [0.0, 25.0)     |       397 |          26 |                    680.91 |           5.78 |           5.77 |          4.3  |
| Downlink    | LOBO_B0    | all             | primary (descriptive) | [25.0, 50.0)    |      3298 |         221 |                    859.53 |           5.96 |           5.95 |          4.31 |
| Downlink    | LOBO_B0    | all             | primary (descriptive) | [50.0, 100.0)   |      9448 |         613 |                    954.48 |           6.23 |           6.23 |          4.95 |
| Downlink    | LOBO_B0    | all             | primary (descriptive) | [100.0, 200.0)  |      5270 |         330 |                    987.21 |           6.17 |           6.39 |          5.1  |
| Downlink    | LOBO_B0    | all             | primary (descriptive) | [200.0, 300.0)  |        97 |           9 |                   1280.01 |           6.23 |           6.36 |          6.23 |
| Downlink    | LOBO_B300  | all             | primary (descriptive) | [300.0, 500.0)  |     18488 |        1198 |                    936    |           6.41 |           6.7  |          5.79 |
| Downlink    | LOBO_B300  | all             | primary (descriptive) | [500.0, 1000.0) |        22 |           1 |                   1474.11 |           6.3  |           7.37 |          6.04 |
| Downlink    | LOBO_B500  | all             | primary (descriptive) | [500.0, 1000.0) |     18510 |        1199 |                    937.33 |           6.9  |           7    |          6.13 |
| Downlink    | LOBO_B1000 | B1000_supported | primary (descriptive) | [1000.0, inf)   |     14171 |        1176 |                   1072.43 |           7.37 |           7.87 |          7.07 |
| Downlink    | LOBO_B1000 | all             | supplementary         | [1000.0, inf)   |     18510 |        1199 |                    937.33 |           9.69 |           8.42 |          7.51 |

## P2b. Paired buffer series (same packets within each subset; 500 m block CIs)

| direction   | subset          | status        |   buffer_m |   packets |   locations |   RMSE_mean |   RMSE_logdist |   RMSE_rf_dist |   RMSE_lr_loc |   RMSE_rf_loc |   delta_loc |   delta_loc_ci95_low |   delta_loc_ci95_high |   delta_dist |   delta_dist_ci95_low |   delta_dist_ci95_high |
|:------------|:----------------|:--------------|-----------:|----------:|------------:|------------:|---------------:|---------------:|--------------:|--------------:|------------:|---------------------:|----------------------:|-------------:|----------------------:|-----------------------:|
| Uplink      | all             | primary       |          0 |     18519 |        1199 |       8.02  |          7.028 |          7.102 |         6.66  |         5.585 |      -1.517 |               -1.808 |                -1.216 |        0.073 |                -0.238 |                  0.323 |
| Uplink      | all             | primary       |        300 |     18519 |        1199 |       8.306 |          7.282 |          7.481 |         6.857 |         6.654 |      -0.827 |               -1.252 |                -0.418 |        0.199 |                -0.094 |                  0.443 |
| Uplink      | all             | primary       |        500 |     18519 |        1199 |       8.561 |          7.708 |          7.735 |         7.042 |         6.918 |      -0.818 |               -1.198 |                -0.456 |        0.027 |                -0.32  |                  0.349 |
| Uplink      | B1000_supported | primary       |          0 |     14179 |        1176 |       7.552 |          7.203 |          7.338 |         6.817 |         5.733 |      -1.604 |               -1.926 |                -1.255 |        0.135 |                -0.212 |                  0.423 |
| Uplink      | B1000_supported | primary       |        300 |     14179 |        1176 |       7.665 |          7.371 |          7.675 |         7.033 |         6.586 |      -1.089 |               -1.487 |                -0.712 |        0.304 |                -0.012 |                  0.556 |
| Uplink      | B1000_supported | primary       |        500 |     14179 |        1176 |       7.779 |          7.537 |          8.009 |         7.252 |         6.987 |      -1.021 |               -1.428 |                -0.66  |        0.472 |                 0.182 |                  0.72  |
| Uplink      | B1000_supported | primary       |       1000 |     14179 |        1176 |       7.954 |          8.114 |          8.385 |         7.813 |         7.793 |      -0.591 |               -1.012 |                -0.217 |        0.271 |                -0.064 |                  0.58  |
| Uplink      | all             | supplementary |       1000 |     18519 |        1199 |       8.905 |         10.254 |          8.316 |         7.699 |         8.036 |      -0.28  |               -0.757 |                 0.2   |       -1.937 |                -3.721 |                 -0.16  |
| Downlink    | all             | primary       |          0 |     18510 |        1199 |       6.875 |          6.157 |          6.218 |         5.774 |         4.88  |      -1.338 |               -1.63  |                -1.039 |        0.061 |                -0.233 |                  0.286 |
| Downlink    | all             | primary       |        300 |     18510 |        1199 |       7.142 |          6.41  |          6.704 |         6.002 |         5.787 |      -0.917 |               -1.309 |                -0.563 |        0.293 |                 0.002 |                  0.54  |
| Downlink    | all             | primary       |        500 |     18510 |        1199 |       7.38  |          6.896 |          7     |         6.239 |         6.13  |      -0.871 |               -1.35  |                -0.416 |        0.104 |                -0.307 |                  0.497 |
| Downlink    | B1000_supported | primary       |          0 |     14171 |        1176 |       6.677 |          6.443 |          6.56  |         6.01  |         5.141 |      -1.419 |               -1.748 |                -1.068 |        0.117 |                -0.196 |                  0.374 |
| Downlink    | B1000_supported | primary       |        300 |     14171 |        1176 |       6.785 |          6.622 |          6.984 |         6.205 |         5.892 |      -1.092 |               -1.53  |                -0.68  |        0.362 |                 0.054 |                  0.629 |
| Downlink    | B1000_supported | primary       |        500 |     14171 |        1176 |       6.889 |          6.801 |          7.356 |         6.407 |         6.246 |      -1.11  |               -1.638 |                -0.618 |        0.555 |                 0.252 |                  0.82  |
| Downlink    | B1000_supported | primary       |       1000 |     14171 |        1176 |       7.017 |          7.373 |          7.867 |         6.699 |         7.068 |      -0.799 |               -1.364 |                -0.286 |        0.494 |                 0.234 |                  0.758 |
| Downlink    | all             | supplementary |       1000 |     18510 |        1199 |       7.659 |          9.686 |          8.422 |         6.602 |         7.509 |      -0.913 |               -1.416 |                -0.338 |       -1.264 |                -2.479 |                  0.163 |

## R1. Fixed-hyperparameter robustness: grid offsets and fold seeds (tuned runs excluded)

| direction   | robustness_type      | family                  | variant         |   RMSE_logdist |   RMSE_rf_dist |   RMSE_rf_loc |   delta_loc |   delta_dist |
|:------------|:---------------------|:------------------------|:----------------|---------------:|---------------:|--------------:|------------:|-------------:|
| Uplink      | fixed-hyperparameter | S250 grid offset x seed | R1_S250_o0_s0   |          7.042 |          7.113 |         5.719 |      -1.393 |        0.07  |
| Uplink      | fixed-hyperparameter | S250 grid offset x seed | R1_S250_o0_s1   |          7.027 |          7.137 |         5.718 |      -1.419 |        0.11  |
| Uplink      | fixed-hyperparameter | S250 grid offset x seed | R1_S250_o1_s0   |          7.004 |          7.123 |         5.865 |      -1.258 |        0.119 |
| Uplink      | fixed-hyperparameter | S250 grid offset x seed | R1_S250_o1_s1   |          7.057 |          7.243 |         5.769 |      -1.474 |        0.187 |
| Uplink      | fixed-hyperparameter | S250 grid offset x seed | R1_S250_o2_s0   |          7.019 |          7.033 |         5.679 |      -1.354 |        0.014 |
| Uplink      | fixed-hyperparameter | S250 grid offset x seed | R1_S250_o2_s1   |          7.041 |          7.192 |         5.685 |      -1.506 |        0.151 |
| Uplink      | fixed-hyperparameter | S250 grid offset x seed | R1_S250_o3_s0   |          7.028 |          7.156 |         5.777 |      -1.379 |        0.128 |
| Uplink      | fixed-hyperparameter | S250 grid offset x seed | R1_S250_o3_s1   |          7.054 |          7.122 |         5.768 |      -1.354 |        0.068 |
| Uplink      | fixed-hyperparameter | LOBO at B* grid offset  | LOBO_B500       |          7.708 |          7.735 |         6.918 |      -0.818 |        0.027 |
| Uplink      | fixed-hyperparameter | LOBO at B* grid offset  | R1_LOBO_o1_B500 |          7.726 |          7.722 |         6.757 |      -0.965 |       -0.004 |
| Downlink    | fixed-hyperparameter | S250 grid offset x seed | R1_S250_o0_s0   |          6.165 |          6.251 |         4.911 |      -1.34  |        0.087 |
| Downlink    | fixed-hyperparameter | S250 grid offset x seed | R1_S250_o0_s1   |          6.17  |          6.268 |         5.013 |      -1.255 |        0.099 |
| Downlink    | fixed-hyperparameter | S250 grid offset x seed | R1_S250_o1_s0   |          6.11  |          6.233 |         5.044 |      -1.19  |        0.123 |
| Downlink    | fixed-hyperparameter | S250 grid offset x seed | R1_S250_o1_s1   |          6.169 |          6.315 |         5.087 |      -1.228 |        0.146 |
| Downlink    | fixed-hyperparameter | S250 grid offset x seed | R1_S250_o2_s0   |          6.141 |          6.181 |         4.921 |      -1.26  |        0.04  |
| Downlink    | fixed-hyperparameter | S250 grid offset x seed | R1_S250_o2_s1   |          6.164 |          6.296 |         4.996 |      -1.3   |        0.132 |
| Downlink    | fixed-hyperparameter | S250 grid offset x seed | R1_S250_o3_s0   |          6.142 |          6.3   |         4.941 |      -1.36  |        0.158 |
| Downlink    | fixed-hyperparameter | S250 grid offset x seed | R1_S250_o3_s1   |          6.173 |          6.221 |         4.932 |      -1.289 |        0.048 |
| Downlink    | fixed-hyperparameter | LOBO at B* grid offset  | LOBO_B500       |          6.896 |          7     |         6.13  |      -0.871 |        0.104 |
| Downlink    | fixed-hyperparameter | LOBO at B* grid offset  | R1_LOBO_o1_B500 |          6.898 |          7.012 |         6.016 |      -0.996 |        0.114 |

| direction   | family                  |   variants |   delta_loc_min |   delta_loc_max |   delta_dist_min |   delta_dist_max |   delta_loc_range |
|:------------|:------------------------|-----------:|----------------:|----------------:|-----------------:|-----------------:|------------------:|
| Downlink    | LOBO at B* grid offset  |          2 |          -0.996 |          -0.871 |            0.104 |            0.114 |             0.125 |
| Downlink    | S250 grid offset x seed |          8 |          -1.36  |          -1.19  |            0.04  |            0.158 |             0.17  |
| Uplink      | LOBO at B* grid offset  |          2 |          -0.965 |          -0.818 |           -0.004 |            0.027 |             0.147 |
| Uplink      | S250 grid offset x seed |          8 |          -1.506 |          -1.258 |            0.014 |            0.187 |             0.248 |

## R2. Size-matched control

| direction   | variant   |   mean_train_locations |   RMSE_rf_loc |   delta_loc |   ci95_low |   ci95_high |
|:------------|:----------|-----------------------:|--------------:|------------:|-----------:|------------:|
| Uplink      | LOBO_B0   |                1189.48 |         5.585 |      -1.517 |     -1.808 |      -1.216 |
| Uplink      | LOBO_B500 |                1053.78 |         6.918 |      -0.818 |     -1.198 |      -0.456 |
| Uplink      | R2_thin0  |                1053.86 |         5.645 |      -1.435 |     -1.723 |      -1.137 |
| Uplink      | R2_thin1  |                1053.83 |         5.638 |      -1.44  |     -1.711 |      -1.158 |
| Uplink      | R2_thin2  |                1053.84 |         5.664 |      -1.422 |     -1.684 |      -1.136 |
| Downlink    | LOBO_B0   |                1189.48 |         4.88  |      -1.338 |     -1.63  |      -1.039 |
| Downlink    | LOBO_B500 |                1053.78 |         6.13  |      -0.871 |     -1.35  |      -0.416 |
| Downlink    | R2_thin0  |                1053.9  |         4.912 |      -1.286 |     -1.573 |      -0.996 |
| Downlink    | R2_thin1  |                1053.79 |         4.952 |      -1.259 |     -1.553 |      -0.95  |
| Downlink    | R2_thin2  |                1053.88 |         4.916 |      -1.314 |     -1.62  |      -1     |

## R5. Reception by distance

| direction   | gateway   | dband            |   units |   share_no_packet |   mean_slot_reception |
|:------------|:----------|:-----------------|--------:|------------------:|----------------------:|
| Downlink    | GA        | [0.0, 250.0)     |      42 |             0     |                 1     |
| Downlink    | GA        | [250.0, 500.0)   |     142 |             0.042 |                 0.789 |
| Downlink    | GA        | [500.0, 1000.0)  |     290 |             0.117 |                 0.624 |
| Downlink    | GA        | [1000.0, 2000.0) |     541 |             0.54  |                 0.295 |
| Downlink    | GA        | [2000.0, 4000.0) |     188 |             0.665 |                 0.145 |
| Downlink    | GB        | [0.0, 250.0)     |      30 |             0     |                 1     |
| Downlink    | GB        | [250.0, 500.0)   |      84 |             0     |                 0.987 |
| Downlink    | GB        | [500.0, 1000.0)  |     347 |             0.003 |                 0.889 |
| Downlink    | GB        | [1000.0, 2000.0) |     580 |             0.083 |                 0.689 |
| Downlink    | GB        | [2000.0, 4000.0) |     162 |             0.006 |                 0.866 |
| Downlink    | GC        | [0.0, 250.0)     |      89 |             0     |                 0.985 |
| Downlink    | GC        | [250.0, 500.0)   |     142 |             0.007 |                 0.959 |
| Downlink    | GC        | [500.0, 1000.0)  |     350 |             0.08  |                 0.791 |
| Downlink    | GC        | [1000.0, 2000.0) |     526 |             0.253 |                 0.552 |
| Downlink    | GC        | [2000.0, 4000.0) |      96 |             0.385 |                 0.413 |
| Uplink      | GA        | [0.0, 250.0)     |      42 |             0     |                 1     |
| Uplink      | GA        | [250.0, 500.0)   |     142 |             0.042 |                 0.79  |
| Uplink      | GA        | [500.0, 1000.0)  |     290 |             0.117 |                 0.625 |
| Uplink      | GA        | [1000.0, 2000.0) |     541 |             0.538 |                 0.296 |
| Uplink      | GA        | [2000.0, 4000.0) |     188 |             0.665 |                 0.145 |
| Uplink      | GB        | [0.0, 250.0)     |      30 |             0     |                 1     |
| Uplink      | GB        | [250.0, 500.0)   |      84 |             0     |                 0.987 |
| Uplink      | GB        | [500.0, 1000.0)  |     347 |             0.003 |                 0.889 |
| Uplink      | GB        | [1000.0, 2000.0) |     580 |             0.083 |                 0.689 |
| Uplink      | GB        | [2000.0, 4000.0) |     162 |             0.006 |                 0.866 |
| Uplink      | GC        | [0.0, 250.0)     |      89 |             0     |                 0.985 |
| Uplink      | GC        | [250.0, 500.0)   |     142 |             0.007 |                 0.959 |
| Uplink      | GC        | [500.0, 1000.0)  |     350 |             0.08  |                 0.791 |
| Uplink      | GC        | [1000.0, 2000.0) |     526 |             0.253 |                 0.552 |
| Uplink      | GC        | [2000.0, 4000.0) |      96 |             0.385 |                 0.413 |

## R5. Error by valid packets per location x gateway

| direction   | scheme    | valid_packets   |   packets | model   |   RMSE |   bias |
|:------------|:----------|:----------------|----------:|:--------|-------:|-------:|
| Uplink      | S250      | 1-2             |       443 | logdist |  9.711 |  9.011 |
| Uplink      | S250      | 1-2             |       443 | rf_dist |  9.214 |  8.382 |
| Uplink      | S250      | 1-2             |       443 | rf_loc  |  5.882 |  4.995 |
| Uplink      | S250      | 3-5             |      1946 | logdist |  8.1   |  6.9   |
| Uplink      | S250      | 3-5             |      1946 | rf_dist |  7.984 |  6.306 |
| Uplink      | S250      | 3-5             |      1946 | rf_loc  |  5.39  |  3.473 |
| Uplink      | S250      | 6-8             |     16130 | logdist |  6.814 | -1.136 |
| Uplink      | S250      | 6-8             |     16130 | rf_dist |  6.933 | -1.077 |
| Uplink      | S250      | 6-8             |     16130 | rf_loc  |  5.753 | -1.035 |
| Uplink      | S250      | >=4             |     17686 | logdist |  6.927 | -0.437 |
| Uplink      | S250      | >=4             |     17686 | rf_dist |  7.025 | -0.436 |
| Uplink      | S250      | >=4             |     17686 | rf_loc  |  5.719 | -0.648 |
| Uplink      | LOBO_B500 | 1-2             |       443 | logdist |  9.975 |  9.258 |
| Uplink      | LOBO_B500 | 1-2             |       443 | rf_dist | 10.044 |  9.212 |
| Uplink      | LOBO_B500 | 1-2             |       443 | rf_loc  |  8.591 |  7.666 |
| Uplink      | LOBO_B500 | 3-5             |      1946 | logdist |  8.297 |  7.069 |
| Uplink      | LOBO_B500 | 3-5             |      1946 | rf_dist |  8.47  |  6.789 |
| Uplink      | LOBO_B500 | 3-5             |      1946 | rf_loc  |  7.15  |  5.397 |
| Uplink      | LOBO_B500 | 6-8             |     16130 | logdist |  7.562 | -1.947 |
| Uplink      | LOBO_B500 | 6-8             |     16130 | rf_dist |  7.568 | -1.466 |
| Uplink      | LOBO_B500 | 6-8             |     16130 | rf_loc  |  6.837 | -1.872 |
| Uplink      | LOBO_B500 | >=4             |     17686 | logdist |  7.62  | -1.163 |
| Uplink      | LOBO_B500 | >=4             |     17686 | rf_dist |  7.646 | -0.746 |
| Uplink      | LOBO_B500 | >=4             |     17686 | rf_loc  |  6.865 | -1.242 |
| Downlink    | S250      | 1-2             |       445 | logdist |  8.892 |  7.712 |
| Downlink    | S250      | 1-2             |       445 | rf_dist |  8.392 |  7.052 |
| Downlink    | S250      | 1-2             |       445 | rf_loc  |  5.797 |  4.247 |
| Downlink    | S250      | 3-5             |      1938 | logdist |  7.479 |  5.77  |
| Downlink    | S250      | 3-5             |      1938 | rf_dist |  7.437 |  5.23  |
| Downlink    | S250      | 3-5             |      1938 | rf_loc  |  5.263 |  2.75  |
| Downlink    | S250      | 6-8             |     16127 | logdist |  5.892 | -0.937 |
| Downlink    | S250      | 6-8             |     16127 | rf_dist |  6.023 | -0.945 |
| Downlink    | S250      | 6-8             |     16127 | rf_loc  |  4.866 | -0.886 |
| Downlink    | S250      | >=4             |     17678 | logdist |  6.039 | -0.358 |
| Downlink    | S250      | >=4             |     17678 | rf_dist |  6.154 | -0.41  |
| Downlink    | S250      | >=4             |     17678 | rf_loc  |  4.899 | -0.577 |
| Downlink    | LOBO_B500 | 1-2             |       445 | logdist |  9.132 |  7.941 |
| Downlink    | LOBO_B500 | 1-2             |       445 | rf_dist |  9.327 |  7.928 |
| Downlink    | LOBO_B500 | 1-2             |       445 | rf_loc  |  6.962 |  5.455 |
| Downlink    | LOBO_B500 | 3-5             |      1938 | logdist |  7.727 |  5.959 |
| Downlink    | LOBO_B500 | 3-5             |      1938 | rf_dist |  8.056 |  5.92  |
| Downlink    | LOBO_B500 | 3-5             |      1938 | rf_loc  |  6.026 |  3.528 |
| Downlink    | LOBO_B500 | 6-8             |     16127 | logdist |  6.716 | -1.688 |
| Downlink    | LOBO_B500 | 6-8             |     16127 | rf_dist |  6.786 | -1.34  |
| Downlink    | LOBO_B500 | 6-8             |     16127 | rf_loc  |  6.117 | -2.038 |
| Downlink    | LOBO_B500 | >=4             |     17678 | logdist |  6.803 | -1.027 |
| Downlink    | LOBO_B500 | >=4             |     17678 | rf_dist |  6.901 | -0.71  |
| Downlink    | LOBO_B500 | >=4             |     17678 | rf_loc  |  6.109 | -1.551 |

## R6. Leaf-size sensitivity at B*

| direction   |   leaf |   delta_loc |   delta_loc_fixed |   change | hyperparameter_sensitive   |
|:------------|-------:|------------:|------------------:|---------:|:---------------------------|
| Uplink      |      5 |      -1.693 |            -0.818 |   -0.875 | True                       |
| Uplink      |     50 |      -0.861 |            -0.818 |   -0.043 | False                      |
| Downlink    |      5 |      -1.556 |            -0.871 |   -0.685 | True                       |
| Downlink    |     50 |      -0.943 |            -0.871 |   -0.072 | False                      |

## R7. By gateway and distance band

| direction   | scheme    | group                     |   packets |   RMSE_logdist |   RMSE_rf_dist |   RMSE_rf_loc |   delta_loc |   ci95_low |   ci95_high |
|:------------|:----------|:--------------------------|----------:|---------------:|---------------:|--------------:|------------:|-----------:|------------:|
| Uplink      | S250      | gateway GA                |      4180 |          6.827 |          6.909 |         5.759 |      -1.15  |     -1.495 |      -0.774 |
| Uplink      | S250      | gateway GB                |      7693 |          6.9   |          6.844 |         6.055 |      -0.789 |     -1.141 |      -0.392 |
| Uplink      | S250      | gateway GC                |      6646 |          7.333 |          7.532 |         5.277 |      -2.255 |     -2.949 |      -1.602 |
| Uplink      | S250      | distance [0.0, 250.0)     |      1277 |          4.559 |          3.794 |         3.997 |     nan     |    nan     |     nan     |
| Uplink      | S250      | distance [250.0, 500.0)   |      2649 |          7.197 |          7.397 |         5.626 |     nan     |    nan     |     nan     |
| Uplink      | S250      | distance [500.0, 1000.0)  |      6133 |          7.305 |          7.647 |         6.222 |     nan     |    nan     |     nan     |
| Uplink      | S250      | distance [1000.0, 2000.0) |      6803 |          7.04  |          7.117 |         5.505 |     nan     |    nan     |     nan     |
| Uplink      | S250      | distance [2000.0, 4000.0) |      1657 |          7.382 |          6.518 |         5.913 |     nan     |    nan     |     nan     |
| Uplink      | LOBO_B500 | gateway GA                |      4180 |          7.102 |          7.258 |         7.261 |       0.003 |     -0.736 |       0.636 |
| Uplink      | LOBO_B500 | gateway GB                |      7693 |          7.423 |          7.091 |         6.803 |      -0.288 |     -0.458 |      -0.104 |
| Uplink      | LOBO_B500 | gateway GC                |      6646 |          8.371 |          8.683 |         6.827 |      -1.856 |     -2.825 |      -0.969 |
| Uplink      | LOBO_B500 | distance [0.0, 250.0)     |      1277 |          8.164 |          3.913 |         4.699 |     nan     |    nan     |     nan     |
| Uplink      | LOBO_B500 | distance [250.0, 500.0)   |      2649 |          8.315 |          8.188 |         7.741 |     nan     |    nan     |     nan     |
| Uplink      | LOBO_B500 | distance [500.0, 1000.0)  |      6133 |          7.49  |          7.992 |         7.436 |     nan     |    nan     |     nan     |
| Uplink      | LOBO_B500 | distance [1000.0, 2000.0) |      6803 |          7.412 |          7.838 |         6.565 |     nan     |    nan     |     nan     |
| Uplink      | LOBO_B500 | distance [2000.0, 4000.0) |      1657 |          8.306 |          7.817 |         6.358 |     nan     |    nan     |     nan     |
| Downlink    | S250      | gateway GA                |      4174 |          4.753 |          5.022 |         4.217 |      -0.804 |     -1.269 |      -0.37  |
| Downlink    | S250      | gateway GB                |      7691 |          5.824 |          5.783 |         5.028 |      -0.755 |     -1.018 |      -0.478 |
| Downlink    | S250      | gateway GC                |      6645 |          7.239 |          7.372 |         5.232 |      -2.14  |     -2.844 |      -1.497 |
| Downlink    | S250      | distance [0.0, 250.0)     |      1277 |          3.648 |          2.843 |         2.87  |     nan     |    nan     |     nan     |
| Downlink    | S250      | distance [250.0, 500.0)   |      2648 |          5.569 |          5.687 |         4.303 |     nan     |    nan     |     nan     |
| Downlink    | S250      | distance [500.0, 1000.0)  |      6132 |          6.17  |          6.478 |         5.176 |     nan     |    nan     |     nan     |
| Downlink    | S250      | distance [1000.0, 2000.0) |      6796 |          6.606 |          6.796 |         5.302 |     nan     |    nan     |     nan     |
| Downlink    | S250      | distance [2000.0, 4000.0) |      1657 |          6.695 |          5.837 |         4.641 |     nan     |    nan     |     nan     |
| Downlink    | LOBO_B500 | gateway GA                |      4174 |          4.943 |          5.258 |         5.526 |       0.268 |     -0.374 |       0.891 |
| Downlink    | LOBO_B500 | gateway GB                |      7691 |          6.363 |          6.095 |         5.897 |      -0.198 |     -0.514 |       0.109 |
| Downlink    | LOBO_B500 | gateway GC                |      6645 |          8.383 |          8.726 |         6.725 |      -2.001 |     -3.138 |      -0.94  |
| Downlink    | LOBO_B500 | distance [0.0, 250.0)     |      1277 |          7.741 |          3.646 |         5.345 |     nan     |    nan     |     nan     |
| Downlink    | LOBO_B500 | distance [250.0, 500.0)   |      2648 |          6.948 |          6.717 |         6.029 |     nan     |    nan     |     nan     |
| Downlink    | LOBO_B500 | distance [500.0, 1000.0)  |      6132 |          6.436 |          6.913 |         6.232 |     nan     |    nan     |     nan     |
| Downlink    | LOBO_B500 | distance [1000.0, 2000.0) |      6796 |          6.961 |          7.494 |         6.277 |     nan     |    nan     |     nan     |
| Downlink    | LOBO_B500 | distance [2000.0, 4000.0) |      1657 |          7.476 |          7.608 |         5.854 |     nan     |    nan     |     nan     |

## Appendix (S250): XGBoost, residual RF, RSSI diagnostic

| direction   | model     |     n |   RMSE |   diff_vs_rf_loc |   ci95_low |   ci95_high |
|:------------|:----------|------:|-------:|-----------------:|-----------:|------------:|
| Uplink      | xgb_loc   | 18519 |  5.864 |            0.145 |      0.047 |       0.244 |
| Uplink      | resrf_loc | 18519 |  5.82  |            0.101 |     -0.044 |       0.26  |
| Uplink      | rf_C      | 18508 |  3.566 |           -2.148 |     -2.453 |      -1.848 |
| Downlink    | xgb_loc   | 18510 |  5.054 |            0.12  |      0.036 |       0.213 |
| Downlink    | resrf_loc | 18510 |  4.985 |            0.052 |     -0.025 |       0.141 |
| Downlink    | rf_C      | 18508 |  3.648 |           -1.286 |     -1.546 |      -1.007 |
