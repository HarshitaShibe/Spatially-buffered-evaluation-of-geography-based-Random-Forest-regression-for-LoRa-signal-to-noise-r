# Protocol-freeze data checks (no model fitting, no SNR values used)

## U1a. Training locations retained under the scattered-fold buffer (S250 folds)

|   fold |   0 |   300 |   500 |   1000 |
|-------:|----:|------:|------:|-------:|
|      0 |   1 | 0.157 | 0.031 |  0     |
|      1 |   1 | 0.306 | 0.054 |  0     |
|      2 |   1 | 0.265 | 0.044 |  0     |
|      3 |   1 | 0.268 | 0.076 |  0.002 |
|      4 |   1 | 0.177 | 0.006 |  0     |

|   buffer_m |   min_retained_share |   mean_retained_share |   min_train_retained |
|-----------:|---------------------:|----------------------:|---------------------:|
|          0 |                1     |                 1     |                  934 |
|        300 |                0.157 |                 0.234 |                  148 |
|        500 |                0.006 |                 0.042 |                    6 |
|       1000 |                0     |                 0     |                    0 |

## U1b. Distance support of test units (|dlog10 d| <= 0.1), pooled over folds

|   buffer_m | direction   | gateway   |   test_units |   min_train_units_in_any_fold |   supported_unit_share |   supported_packet_share |
|-----------:|:------------|:----------|-------------:|------------------------------:|-----------------------:|-------------------------:|
|          0 | Downlink    | GA        |          746 |                           580 |                  0.987 |                    0.981 |
|          0 | Downlink    | GB        |         1153 |                           888 |                  0.992 |                    0.991 |
|          0 | Downlink    | GC        |         1004 |                           773 |                  0.998 |                    0.998 |
|          0 | Uplink      | GA        |          747 |                           581 |                  0.987 |                    0.981 |
|          0 | Uplink      | GB        |         1153 |                           888 |                  0.992 |                    0.991 |
|          0 | Uplink      | GC        |         1004 |                           773 |                  0.998 |                    0.998 |
|        300 | Downlink    | GA        |          746 |                            88 |                  0.898 |                    0.86  |
|        300 | Downlink    | GB        |         1153 |                           141 |                  0.944 |                    0.934 |
|        300 | Downlink    | GC        |         1004 |                           108 |                  0.917 |                    0.901 |
|        300 | Uplink      | GA        |          747 |                            88 |                  0.898 |                    0.86  |
|        300 | Uplink      | GB        |         1153 |                           141 |                  0.944 |                    0.934 |
|        300 | Uplink      | GC        |         1004 |                           108 |                  0.917 |                    0.901 |
|        500 | Downlink    | GA        |          746 |                             4 |                  0.572 |                    0.543 |
|        500 | Downlink    | GB        |         1153 |                             6 |                  0.642 |                    0.599 |
|        500 | Downlink    | GC        |         1004 |                             4 |                  0.586 |                    0.547 |
|        500 | Uplink      | GA        |          747 |                             4 |                  0.577 |                    0.547 |
|        500 | Uplink      | GB        |         1153 |                             6 |                  0.642 |                    0.599 |
|        500 | Uplink      | GC        |         1004 |                             4 |                  0.586 |                    0.547 |
|       1000 | Downlink    | GA        |          746 |                             0 |                  0.031 |                    0.021 |
|       1000 | Downlink    | GB        |         1153 |                             0 |                  0.05  |                    0.051 |
|       1000 | Downlink    | GC        |         1004 |                             0 |                  0     |                    0     |
|       1000 | Uplink      | GA        |          747 |                             0 |                  0.031 |                    0.021 |
|       1000 | Uplink      | GB        |         1153 |                             0 |                  0.05  |                    0.051 |
|       1000 | Uplink      | GC        |         1004 |                             0 |                  0     |                    0     |

## U1c. Fallback: buffered leave-one-250m-block-out

|   buffer_m |   blocks |   min_retained_share |   median_retained_share |   min_train_retained |   test_packets |   supported_packets |   pooled_supported_packet_share |
|-----------:|---------:|---------------------:|------------------------:|---------------------:|---------------:|--------------------:|--------------------------------:|
|          0 |      126 |                1     |                   1     |                 1167 |          37029 |               36725 |                           0.992 |
|        300 |      126 |                0.864 |                   0.955 |                 1022 |          37029 |               35475 |                           0.958 |
|        500 |      126 |                0.751 |                   0.892 |                  889 |          37029 |               34173 |                           0.923 |
|       1000 |      126 |                0.431 |                   0.679 |                  512 |          37029 |               28350 |                           0.766 |

Distance-supported packet share by gateway x direction (fallback design)

|                    |     0 |   300 |   500 |   1000 |
|:-------------------|------:|------:|------:|-------:|
| ('Downlink', 'GA') | 0.981 | 0.969 | 0.905 |  0.683 |
| ('Downlink', 'GB') | 0.993 | 0.985 | 0.968 |  0.84  |
| ('Downlink', 'GC') | 0.998 | 0.919 | 0.882 |  0.731 |
| ('Uplink', 'GA')   | 0.981 | 0.969 | 0.905 |  0.683 |
| ('Uplink', 'GB')   | 0.993 | 0.985 | 0.968 |  0.84  |
| ('Uplink', 'GC')   | 0.998 | 0.919 | 0.882 |  0.731 |

## U2. Occupied bootstrap blocks (all directions/gateways pooled)

|   block_m |   offset_x_m |   offset_y_m |   occupied_blocks |   blocks_ge10_locations |   median_locations_per_block |   max_block_packet_share |
|----------:|-------------:|-------------:|------------------:|------------------------:|-----------------------------:|-------------------------:|
|       500 |            0 |            0 |                42 |                      32 |                         23.5 |                    0.087 |
|       500 |          250 |            0 |                43 |                      33 |                         26   |                    0.084 |
|       500 |            0 |          250 |                39 |                      32 |                         29   |                    0.077 |
|       500 |          250 |          250 |                39 |                      34 |                         28   |                    0.071 |
|      1000 |            0 |            0 |                13 |                      12 |                        103   |                    0.205 |
|      1000 |          500 |            0 |                14 |                      11 |                         62.5 |                    0.217 |
|      1000 |            0 |          500 |                15 |                      14 |                         51   |                    0.213 |
|      1000 |          500 |          500 |                17 |                      13 |                         37   |                    0.202 |
