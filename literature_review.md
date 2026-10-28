# Literature review: spatially validated ML prediction of LoRa SNR (28 Oct 2026)

**Scope.** Work needed to position the study: measured LoRa signal quality and path loss with ML; how ML radio
models are evaluated on unseen locations; and the spatial cross-validation literature that the evaluation design
relies on. This is a working review for the experiments, not the report's related-work section.

## How entries were verified

| Level | Meaning |
| --- | --- |
| **V1** | Full text read in this project |
| **V2** | Bibliographic record (title, authors, venue, year, DOI) read on a publisher, repository or index page fetched on 28 Oct 2026 |
| **V3** | DOI read from a publisher URL returned for an exact-title search; content summarised from the indexed abstract (Consensus) |

Method and finding summaries come only from the full text (V1) or from the abstract/record actually read. Where
a paper's evaluation design was not stated in the material read, the entry says "not stated in the material read"
rather than guessing. Crossref, doi.org and OpenAlex were not reachable from this workspace, which is why V2/V3 rely
on publisher and repository pages. All 25 entries are in `references_verified.bib`; two screened papers whose
metadata could not be verified are listed at the end and **not** included in the .bib.

## A. Same dataset and closest LoRa work

**[1] Azevedo & Mendonça (2026).** *A Large-Scale LoRa Measurement Campaign for Path-Loss Modeling in Urban and
Suburban Environments.* IEEE Access 14, 137151–137166. doi:10.1109/ACCESS.2026.3730186. **V1.**
- *Method:* the paper describing our dataset. 1,203 fixed positions in Funchal, 3 self-built gateways, SF12, 8 packets per position, calibrated RSSI, ESP-based path loss with linear-domain averaging, order-statistics correction near sensitivity.
- *Findings:*
    - Small-scale fading SD up to about 12 dB.
    - Uplink and downlink path loss similar (mean difference 0.9 dB).
    - Interference near cellular antennas degrades GA/GB.
    - Single-slope fits have RMSE 11–12 dB.
- *Evaluation:* no ML, no SNR prediction, no cross-validation. Machine learning on the dataset is named as future work.
- *Limitation for us:* path loss only, so it cannot answer how well SNR generalises to unseen locations. Its Table 3 is reproduced exactly by our `09_pathloss_reproduction.py`.

**[2] Azevedo & Mendonça (2024).** *A Critical Review of the Propagation Models Employed in LoRa Systems.* Sensors
24(12), 3877. doi:10.3390/s24123877. **V1.**
- *Method:* review of empirical, deterministic and measurement-based (incl. ML) LoRa propagation models, plus re-fitting of published measurements.
- *Findings:*
    - RSSI is unreliable below SNR 0 dB, so ESP should be used.
    - A "transitional region" near sensitivity biases log-distance fits.
    - Multi-slope models are needed.
    - For ML, generalisation to new locations "remains imperative" to verify.
- *Limitation:* review; no new evaluation of ML generalisation.

**[3] Cardoso et al. (2022).** *SNR Prediction with ANN for UAV Applications in IoT Networks Based on Measurements.*
Sensors 22(14), 5233. doi:10.3390/s22145233. **V1** (full text read earlier; record re-read on PMC, 28 Oct).
- *Method:* GRNN predicting measured LoRa SNR at 915 MHz from UAV height, SF, distance and path loss. 3,614 samples, UAV-mounted gateway.
- *Evaluation:* "k = 10" cross-validation repeated 100 times. Grouping by location is not described.
- *Findings:* RMSE 0.87–1.39 dB uplink, 1.23–1.66 dB downlink.
- *Limitation for us:*
    - Path loss is an input, which carries most of the received-power information.
    - No spatial separation is reported.
    - The data were not released.
    - The closest prior *measured-SNR* prediction study, but its question differs.

**[4] Bitterling, Nettersheim, Hees & Rademacher (2026).** *A Systematic Sample Size Analysis of ML-Based Path Loss
Prediction for LPWAN.* arXiv:2608.11083. **V1/V2** (abstract page re-read 28 Oct).
- *Method:* RF and k-NN path-loss prediction on 64,294 LoRa samples from 8 gateways in Bonn, with learning curves.
- *Evaluation:* 75/25 random pooled split plus a leave-one-gateway-out check.
- *Findings:*
    - RF is below 6.5 dB under the random split but 8.92 dB under leave-one-gateway-out.
    - Coordinate-only k-NN rises to about 13.3–13.7 dB.
- *Limitation for us:*
    - Path loss, not SNR.
    - No spatial blocking or buffering.
    - Shows that random-split accuracy does not transfer to new gateways.

**[5] Callebaut & Van der Perre (2020).** *Characterization of LoRa Point-to-Point Path Loss: Measurement Campaigns
and Modeling Considering Censored Data.* IEEE Internet of Things Journal 7(3), 1910–1918.
doi:10.1109/JIOT.2019.2953804. **V2.**
- *Method:* P2P LoRa campaigns (urban, forest, coastal); path-loss parameters estimated with packets below sensitivity treated as censored.
- *Relevance:* the reference method for packet-loss (censoring) bias. Our target is SNR *given reception*, and censoring is an appendix option only.

**[6] Rademacher, Linka, Horstmann & Henze (2021).** *Path Loss in Urban LoRa Networks: A Large-Scale Measurement
Study.* IEEE 94th VTC2021-Fall. doi:10.1109/VTC2021-Fall52928.2021.9625531 (arXiv:2109.07768). **V2** (record as cited in [1]; abstract via Consensus).
- *Method:* 112k samples from garbage-truck sensors over 200 km²; 11 path-loss models compared.
- *Findings:* the log-distance model is reasonable in urban areas, and terrain-based models give no advantage. Data are public.
- *Limitation for us:* path loss; mobile, road-centred sampling.

**[7] González-Palacio, Tobón-Vallejo, Sepúlveda-Cano, Rúa & Le (2023).** *Machine-Learning-Based Combined Path Loss
and Shadowing Model in LoRaWAN for Energy Efficiency Enhancement.* IEEE Internet of Things Journal 10(12),
10725–10739. doi:10.1109/JIOT.2023.3239827. **V2.**
- *Method:* MLR, SVR, RF and ANN for path loss and shadowing, with distance, frequency, weather variables and **SNR as an input**.
- *Findings:* RMSE down to 1.566 dB, R² up to 0.94.
- *Evaluation:* not stated in the material read.
- *Limitation for us:* uses same-link SNR as a predictor of path loss. This is the leakage pattern our design excludes (RSSI/SNR never predict SNR).

**[8] Ojo et al. (2024).** *A Deep Learning Approach for Accurate Path Loss Prediction in LoRaWAN Livestock
Monitoring.* Sensors 24(10), 2991. doi:10.3390/s24102991. **V2.**
- *Method:* Bi-LSTM with remote-sensing land cover; 35,876 records from 8 mobile devices in the Alps.
- *Evaluation:* "we split the dataset into a training set and testing set by 9:1".
- *Findings:* error 4.97 dB. The authors note that scalability to diverse environments is limited.
- *Limitation for us:* the split is not spatially separated; path loss; mobile nodes.

**[9] Petäjäjärvi et al. (2015).** *On the coverage of LPWANs: range evaluation and channel attenuation model for
LoRa technology.* 14th ITST. doi:10.1109/ITST.2015.7377400. **V2** (record as cited in [1]).
- *Relevance:* an early LoRa range and attenuation study (vehicle-based). Background only; older than the review window.

## B. ML radio-signal prediction and evaluation on unseen locations

**[10] Eller, Svoboda & Rupp (2022).** *A Deep Learning Network Planner: Propagation Modeling Using Real-World
Measurements and a 3D City Model.* IEEE Access 10, 122182–122196. doi:10.1109/ACCESS.2022.3223097. **V2.**
- *Method:* RSRP from a 4G drive test with a 3D city model; RMSE 7.06 dB.
- *Evaluation:* the authors explicitly compare evaluation strategies and highlight "the importance of spatial separation of train and test areas".
- *Limitation for us:* cellular RSRP with rich environment inputs. The closest radio-domain statement of our evaluation concern.

**[11] Gupta, Du, Chizhik, Valenzuela & Sellathurai (2022).** *Machine Learning-based Urban Canyon Path Loss Prediction
using 28 GHz Manhattan Measurements.* IEEE Trans. Antennas and Propagation 70(6), 4096–4111.
doi:10.1109/TAP.2022.3152776. **V2.**
- *Method:* LiDAR clutter and building features.
- *Evaluation:* street-by-street training/testing, adopted to "improve generalizability".
- *Findings:* RMSE 4.8 ± 1.1 dB vs 6.5 ± 2.0 dB for a slope-intercept model.
- *Limitation for us:* mmWave path loss. A precedent for grouped (street-level) evaluation.

**[12] Thrane, Zibar & Christiansen (2020).** *Model-Aided Deep Learning Method for Path Loss Prediction in Mobile
Communication Systems at 2.6 GHz.* IEEE Access 8, 7925–7936. doi:10.1109/ACCESS.2020.2964103. **V2** (researchr BibTeX record).
- *Method:* CNN on satellite images plus a simple path-loss model.
- *Findings:* about 1 dB improvement at unseen locations for 811 MHz and 4.7 dB for 2630 MHz (per abstract).
- *Limitation for us:* "unseen locations" without a stated spatial-separation distance.

**[13] Moraitis, Tsipi, Vouyioukas et al. (2021).** *Performance evaluation of machine learning methods for path
loss prediction in rural environment at 3.7 GHz.* Wireless Networks 27, 4169–4188. doi:10.1007/s11276-021-02682-3. **V2.**
- *Method:* ANN, SVR, RF and bagged k-NN vs empirical models.
- *Findings:* ML RMSE 4.0–6.5 dB, below the empirical models.
- *Evaluation:* split not stated in the material read.
- *Limitation:* site-specific; generalisation not tested.

**[14] Zhang, Wen, Yang, He & Wang (2019).** *Path Loss Prediction Based on Machine Learning: Principle, Method, and
Data Expansion.* Applied Sciences 9(9), 1908. doi:10.3390/app9091908. **V2.**
- *Method:* ANN, SVR and RF outperform the log-distance model.
- *Evaluation:* "We randomly selected 80% of samples as the training dataset and the remaining 20% as the test dataset".
- *Limitation:* a random packet-level split. This is exactly the design our R scheme shows to be optimistic.

**[15] Jo, Park, Lee, Choi & Park (2020).** *Path Loss Prediction Based on Machine Learning Techniques: Principal
Component Analysis, Artificial Neural Network, and Gaussian Process.* Sensors 20(7), 1927. doi:10.3390/s20071927. **V2.**
- *Method:* ANN for mean path loss and a Gaussian process for shadowing variance (suburban Korea).
- *Findings:* better than linear log-distance with log-normal shadowing.
- *Evaluation:* split not stated in the material read.

**[16] Jang et al. (2022).** *Path Loss Model Based on Machine Learning Using Multi-Dimensional Gaussian Process
Regression.* IEEE Access 10. doi:10.1109/ACCESS.2022.3217912. **V3** (full author list not verified).
- *Method:* GPR with a radial mean plus a local shadow-fading term for spatial consistency; indoor data.
- *Findings:* gains over log-distance grow "when spatial correlation gets more significant" (abstract).
- *Relevance:* supports interpreting a location-aware gain as exploitation of spatially correlated shadowing, which is what our separation curve tests.

## C. Spatial cross-validation and the meaning of "spatially separated" error

**[17] Roberts et al. (2017).** *Cross-validation strategies for data with temporal, spatial, hierarchical, or
phylogenetic structure.* Ecography 40(8), 913–929. doi:10.1111/ecog.02881. **V2/V3** (record from repository page; DOI from publisher-index URL).
- *Content:* blocked CV is recommended when data are structured; random CV underestimates error under dependence.
- *Use here:* the standard justification for grouped and blocked outer splits.

**[18] Schratz, Muenchow, Iturritxa, Richter & Brenning (2019).** *Hyperparameter tuning and performance assessment
of statistical and machine-learning algorithms using spatial data.* Ecological Modelling 406, 109–120.
doi:10.1016/j.ecolmodel.2019.06.002. **V2.**
- *Findings:* differences of up to 47% between spatial and non-spatial CV estimates. Spatial tuning is recommended for consistency (abstract of the arXiv version).
- *Use here:* motivates inner tuning grouped like the outer split, and our R6 check of fixed hyperparameters.

**[19] Wadoux, Heuvelink, de Bruin & Brus (2021).** *Spatial cross-validation is not the right way to evaluate map
accuracy.* Ecological Modelling 457, 109692. doi:10.1016/j.ecolmodel.2021.109692. **V2.**
- *Argument:* spatial CV has no design-based underpinning for *map accuracy*; probability sampling is the valid route.
- *Use here:* the main counter-argument. We therefore state which prediction scenario each scheme estimates (infill vs a new area ≥ b m away) and do not call buffered error "the true accuracy".

**[20] Meyer & Pebesma (2021).** *Predicting into unknown space? Estimating the area of applicability of spatial
prediction models.* Methods in Ecology and Evolution. doi:10.1111/2041-210X.13650 (arXiv:2005.07939). **V2** (DOI from the arXiv record).
- *Content:* the dissimilarity index and area of applicability. CV error holds only where prediction locations resemble the training data.
- *Use here:* the conceptual basis for our distance-support flag. A test packet counts as supported only if training has a similar gateway distance.

**[21] Milà, Mateu, Pebesma & Meyer (2022).** *Nearest neighbour distance matching Leave-One-Out Cross-Validation
for map validation.* Methods in Ecology and Evolution 13(6), 1304–1316. doi:10.1111/2041-210X.13851. **V2.**
- *Findings:* buffered LOO gives realistic errors for new prediction areas but overestimates interpolation error. NNDM matches the test-to-train nearest-neighbour distance distribution to the prediction task.
- *Use here:* directly supports reporting error as a function of nearest-training distance, and reading buffered results as the "new area" scenario.

**[22] Linnenbrink, Milà, Ludwig & Meyer (2024).** *kNNDM CV: k-fold nearest-neighbour distance matching
cross-validation for map accuracy estimation.* Geoscientific Model Development 17, 5897–5912.
doi:10.5194/gmd-17-5897-2024. **V2.**
- *Content:* a k-fold version of NNDM. The match quality of the distance distributions is associated with the reliability of the error estimate.
- *Use here:* an alternative we did not adopt. It is noted as future work because our question is the error-vs-distance curve itself, not one map-accuracy number.

**[23] Milà, Ludwig, Pebesma, Tonne & Meyer (2024).** *Random forests with spatial proxies for environmental
modelling: opportunities and pitfalls.* Geoscientific Model Development 17, 6007–6033.
doi:10.5194/gmd-17-6007-2024. **V2.**
- *Findings:*
    - Coordinates as RF predictors help interpolation only with strong residual autocorrelation and well-spread samples.
    - They are poorly suited to extrapolation to new areas.
    - Random k-fold CV favours proxy models even when inappropriate.
- *Use here:* the closest methodological analogue of our RF-loc (x, y as predictors) vs RF-dist comparison, from environmental modelling. It predicts the pattern our H1 tests, but no LoRa or radio data are involved.

**[24] Kattenborn et al. (2022).** *Spatially autocorrelated training and validation samples inflate performance
assessment of convolutional neural networks.* ISPRS Open Journal of Photogrammetry and Remote Sensing.
doi:10.1016/j.ophoto.2022.100018. **V2.**
- *Findings:* random hold-outs overestimated performance by up to 28% compared with spatial blocks.
- *Use here:* the size of the random-split optimism in another domain (context for H3).

**[25] Kumar, Walton, Santi & Luza (2025).** *Random Cross-Validation Produces Biased Assessment of Machine Learning
Performance in Regional Landslide Susceptibility Prediction.* Remote Sensing 17(2), 213. doi:10.3390/rs17020213. **V2.**
- *Findings:* random CV is 6–18% more optimistic than spatial CV. The effect is stronger for complex models such as RF. Random CV also distorts hyperparameter importance.
- *Use here:* supports reporting R/L/S/buffered side by side, and expecting the RF gain to shrink most.

## Screened but not verified (not in the .bib)

- Chen et al. (2024), *AI-Enhanced Generalizable Scheme for Path Loss Prediction in LoRaWAN*, IEEE IoT J. Transfer learning to new scenarios with limited data. DOI not confirmed (publisher pages blocked).
- Liu et al. (2021), *DeepLoRa: Learning Accurate Path Loss Model for Long Distance Links in LPWAN*, IEEE INFOCOM. Land-cover-aware Bi-LSTM; DOI not confirmed.

## Synthesis: what is established, and the defensible gap

**Established by others (do not claim):**
- Random or packet-level splits overestimate the accuracy of spatial ML, RF included [17, 18, 24, 25]. In radio prediction, spatial or grouped separation of train and test is recognised as necessary [10, 11, 4].
- ML beats single-slope log-distance models *at the measured site* [13, 14, 15]. Single-slope models are inadequate for LoRa [1, 2].
- Coordinates as RF predictors mainly help interpolation and fail to transfer to new areas [23]. Buffered CV estimates new-area error, not interpolation error [21]. Spatial CV is not a design-based map-accuracy estimate [19].
- Path loss on this exact dataset is characterised in [1], including packet-loss truncation, interference and uplink/downlink similarity.

**Not found in the papers read (a "not found", not a "first"):**
- A study of *measured LoRa SNR*, on a public fixed-location dataset, that reports error as a function of distance to the nearest training location (buffered leave-one-block-out).
- That also separates the gain from non-linear distance dependence (log-distance → RF-distance) from the gain from location (RF-distance → RF-location).
- And interprets errors against the within-location packet-to-packet floor.
- [3] predicts SNR, but with path loss as input and without spatial separation. [4], [10] and [11] use spatial or grouped evaluation, but for path loss or RSRP. [23] makes the distance-only vs coordinate comparison for environmental variables, not radio data.

**Defensible framing:** *an application and test of established spatial-validation methodology [21, 23] to measured
LoRa SNR, on the public dataset of [1], with a decomposition of where the ML gain comes from.* The search was
targeted, not systematic. Forward-citation tracing of [1], [3] and [4] could not be completed (index sites blocked
or paywalled). So the paper may say "among the studies reviewed", but not "first" or "to our knowledge, no study".

Paper metadata via Consensus: Upgrade to Consensus Pro to return 20 results per search instead of 10, and include more data like study design and key takeaways for every result.: https://consensus.app/pricing/?utm_source=claude_desktop
