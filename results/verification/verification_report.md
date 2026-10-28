# Independent verification of results

B* = 500 m

## V1 P1 RMSE recomputed

- PASS  P1 RMSE reproduces (all rows; CSV rounded to 4 dp)  max abs diff 4.98e-05

## V2 H1 independent bootstrap

- PASS  Uplink: H1 point estimate  recomputed -0.818 vs reported -0.818
- PASS  Uplink: H1 CI agrees within Monte Carlo tolerance (0.05 dB)  independent [-1.202, -0.493] vs reported [-1.198, -0.456]
  - Uplink independent CI classification: inconclusive
- PASS  Downlink: H1 point estimate  recomputed -0.871 vs reported -0.871
- PASS  Downlink: H1 CI agrees within Monte Carlo tolerance (0.05 dB)  independent [-1.370, -0.428] vs reported [-1.350, -0.416]
  - Downlink independent CI classification: inconclusive

## V3 B1000 distance-supported subset (primary for B1000)

- PASS  Uplink: B1000 subset rows cover buffers 0/300/500/1000  
- PASS  Uplink: subset packet count = B1000 supported flags  14179 packets
- PASS  Uplink: B0 rf_loc RMSE on the B1000 mask  5.7334
- PASS  Uplink: B300 rf_loc RMSE on the B1000 mask  6.5861
- PASS  Uplink: B500 rf_loc RMSE on the B1000 mask  6.9871
- PASS  Uplink: B1000 rf_loc RMSE on the B1000 mask  7.7935
- PASS  Uplink: B1000 all-packet row labelled supplementary  
- PASS  Downlink: B1000 subset rows cover buffers 0/300/500/1000  
- PASS  Downlink: subset packet count = B1000 supported flags  14171 packets
- PASS  Downlink: B0 rf_loc RMSE on the B1000 mask  5.1407
- PASS  Downlink: B300 rf_loc RMSE on the B1000 mask  5.8917
- PASS  Downlink: B500 rf_loc RMSE on the B1000 mask  6.2460
- PASS  Downlink: B1000 rf_loc RMSE on the B1000 mask  7.0680
- PASS  Downlink: B1000 all-packet row labelled supplementary  

## V4 CI ordering and H1 classification logic

- PASS  P3_paired_gains.csv: all CIs ordered  1 CI column pair(s)
- PASS  P1b_scheme_vs_LOBO_B0.csv: all CIs ordered  1 CI column pair(s)
- PASS  P1c_grouped_vs_S250.csv: all CIs ordered  1 CI column pair(s)
- PASS  R2_size_matched.csv: all CIs ordered  1 CI column pair(s)
- PASS  R7_by_gateway_and_distance.csv: all CIs ordered  1 CI column pair(s)
- PASS  P2b_buffer_series_paired.csv: all CIs ordered  2 CI column pair(s)
- PASS  Uplink block500_all: classification consistent  inconclusive
- PASS  Uplink block500_supported: classification consistent  practically relevant location advantage persists
- PASS  Uplink block1000_all: classification consistent  inconclusive
- PASS  Uplink block1000_supported: classification consistent  practically relevant location advantage persists
- PASS  Downlink block500_all: classification consistent  inconclusive
- PASS  Downlink block500_supported: classification consistent  practically relevant location advantage persists
- PASS  Downlink block1000_all: classification consistent  inconclusive
- PASS  Downlink block1000_supported: classification consistent  practically relevant location advantage persists

## V5 floor

- PASS  Uplink: floor ddof0  2.9932 dB
- PASS  Downlink: floor ddof0  2.6734 dB

## V6 buffer distances

- PASS  Uplink LOBO_B300: min sep >= b  min 300.0 m
- PASS  Uplink LOBO_B500: min sep >= b  min 500.0 m
- PASS  Uplink LOBO_B1000: min sep >= b  min 1000.0 m
- PASS  Uplink R6 leaf5: min sep >= B*  min 500.0 m
- PASS  Uplink R6 leaf50: min sep >= B*  min 500.0 m
- PASS  Downlink LOBO_B300: min sep >= b  min 300.0 m
- PASS  Downlink LOBO_B500: min sep >= b  min 500.0 m
- PASS  Downlink LOBO_B1000: min sep >= b  min 1000.0 m
- PASS  Downlink R6 leaf5: min sep >= B*  min 500.0 m
- PASS  Downlink R6 leaf50: min sep >= B*  min 500.0 m

## V7/V8 amended families

- PASS  R1 excludes tuned S250  10 variants
- PASS  R1 has 8 S250 variants + 2 LOBO variants per direction  
- PASS  Grouped schemes paired vs S250  
- PASS  Buffered schemes paired vs LOBO-B0  

**0 failure(s).**