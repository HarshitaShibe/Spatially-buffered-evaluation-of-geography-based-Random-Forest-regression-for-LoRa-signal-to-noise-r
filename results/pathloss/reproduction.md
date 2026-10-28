# Reproduction of Azevedo & Mendonca (2026)

## Floating-intercept fit (paper Table 3 = uplink)

| distance   | direction   | gateway   |   locations |   alpha_dB |   beta |   RMSE_dB |   paper_alpha |   paper_beta |   paper_RMSE |
|:-----------|:------------|:----------|------------:|-----------:|-------:|----------:|--------------:|-------------:|-------------:|
| d_3d       | Downlink    | GA        |         746 |      45.21 |   2.66 |     11.41 |         nan   |       nan    |        nan   |
| d_3d       | Downlink    | GB        |        1153 |      61.29 |   2.11 |     10.32 |         nan   |       nan    |        nan   |
| d_3d       | Downlink    | GC        |        1004 |      44.52 |   2.91 |     12.26 |         nan   |       nan    |        nan   |
| d_3d       | Uplink      | GA        |         746 |      42.69 |   2.79 |     11.89 |          42.6 |         2.79 |         11.9 |
| d_3d       | Uplink      | GB        |        1153 |      54.84 |   2.37 |     11.06 |          54.9 |         2.37 |         11.1 |
| d_3d       | Uplink      | GC        |        1004 |      44.02 |   2.93 |     12.23 |          44.4 |         2.92 |         12.2 |
| d_h        | Downlink    | GA        |         746 |      46.21 |   2.63 |     11.39 |         nan   |       nan    |        nan   |
| d_h        | Downlink    | GB        |        1153 |      61.3  |   2.11 |     10.32 |         nan   |       nan    |        nan   |
| d_h        | Downlink    | GC        |        1004 |      45.7  |   2.88 |     12.25 |         nan   |       nan    |        nan   |
| d_h        | Uplink      | GA        |         746 |      43.75 |   2.75 |     11.87 |          42.6 |         2.79 |         11.9 |
| d_h        | Uplink      | GB        |        1153 |      54.85 |   2.37 |     11.06 |          54.9 |         2.37 |         11.1 |
| d_h        | Uplink      | GC        |        1004 |      45.2  |   2.89 |     12.21 |          44.4 |         2.92 |         12.2 |

## Uplink minus downlink PL per location: mean 0.85 dB, SD 1.69 dB, n = 2903 (paper: 0.9 dB, SD 1.5 dB)

## Received packets and location coverage (paper: 62.0 / 95.8 / 83.5 % of locations)

| direction   | gateway   |   packets |   locations |   share_locations_pct |
|:------------|:----------|----------:|------------:|----------------------:|
| Downlink    | GA        |      4174 |         746 |                  62   |
| Downlink    | GB        |      7691 |        1153 |                  95.8 |
| Downlink    | GC        |      6645 |        1004 |                  83.5 |
| Uplink      | GA        |      4180 |         747 |                  62.1 |
| Uplink      | GB        |      7693 |        1153 |                  95.8 |
| Uplink      | GC        |      6646 |        1004 |                  83.5 |