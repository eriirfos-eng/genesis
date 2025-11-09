The Revelation Recurrence Model (RRM): Discovering Cross‑Cultural Recurrences of Sacred Meaning Without an Imposed Ontology
Short title: RRM: Recurrence of Sacred Concepts
 Authors: Simeon A. Kepp (RFI‑IRFOS), Albert (GPT‑5 Thinking)
 Date: 9 Nov 2025 (CET)
 Status: Registered‑report protocol + Manuscript (v1.3, submission‑ready, Unicode only)

Abstract
We introduce the Revelation Recurrence Model (RRM), a pattern‑agnostic, data‑driven framework to test whether religious and philosophical corpora contain recurrent and semantically stable concept clusters across languages, traditions, and epochs—without imposing an a priori ontology. RRM operationalizes emergent ontology via unsupervised clustering over a multilingual, diachronic corpus spanning Vedic/Upanishadic, Buddhist, Taoist, Zoroastrian, Abrahamic (Tanakh, New Testament, Qur’ān with specified hadith subsets), and selected parallel sources. We specify two hypotheses: H1 (Emergent Ontology)—unsupervised methods recover a finite set of recurrent conceptual clusters robust to translation, epoch slices, and sub‑corpus perturbations; H2 (Temporal Recurrence)—prevalence and/or semantic‑centroid trajectories of these clusters show non‑random structure over time.
We formalize two primary metrics—ITCA (Inter‑Tradition Conceptual Alignment) and CRS (Concept Recurrence Score)—alongside stability and validity criteria, and register falsification gates against multiple null models. Ethical design includes multilingual expert review, preregistration, open materials where licensing permits, and deferral of multimodal Indigenous Knowledge Systems (IKS) to a community‑co‑designed follow‑on governed by CARE principles. Technical foundations include multilingual sentence embeddings (LaBSE; Sentence‑BERT), diachronic calibration, density/manifold clustering (HDBSCAN, spectral), trajectory analysis (dynamic time warping, change‑point detection), and robust validation (ARI/NMI, κ). The result is a reproducible path to test whether “sacred concepts” recur across civilizations as diffusion, convergence, or deeper structural alignment.
Keywords: cultural evolutionary dynamics; diachronic semantics; emergent ontology; comparative religion; multilingual embeddings; ethics of data; Indigenous data governance; Bayesian meta‑analysis; reproducibility; registered reports

1. Introduction
Comparative religion has long oscillated between essentialist universalism and particularist hermeneutics. RRM reframes the field as pattern discovery within cultural evolutionary dynamics. Instead of hand‑crafting taxonomies (risk: importing modern/Western priors), we instantiate multilingual, diachronic embedding spaces that let ontology emerge from texts themselves. The central empirical question is not which tradition is correct? but do conceptual recurrences exist at scale—and with what shape?
1.1 Motivation and Scope
Scholar‑defined categories (e.g., “grace,” “law,” “emptiness”) often collapse culturally distinct notions into homogeneous bins. RRM replaces that imposition with latent structure learned directly from primary sources and carefully tracked translation genealogies. The approach is agnostic about whether observed recurrences reflect diffusion (historical contact), convergence (cognitive/social regularities), or deeper metaphysical invariance. Our task is to estimate the pattern; interpretation is deferred to a transparent triad (Section 9).
1.2 Contributions
Pattern‑agnostic theoretical core (Section 2).


Reproducible emergent‑ontology pipeline (Section 7).


Falsifiable, preregistered tests (Section 5).


Robust metrics (ITCA/CRS) with properties, sensitivity analyses, thresholds (Section 4).


Ethics and governance posture honoring CARE and Indigenous Data Sovereignty (Section 6).


Compute, power, and ablation planning (Section 8).


Compact replication kit and visual schematics for reviewers (Appendix C/D).



2. Theory and Hypotheses
2.1 Objects and Notation (Unicode; no LaTeX)
We consider traditions (T), epochs (E), documents (D), languages (L), and segments (S: verse, sutra, ayah, aphorism). An embedding function maps segments to an n‑dimensional semantic space. To mitigate presentism, we apply time‑sliced calibration so vectors approximate meanings at composition rather than modern glosses. Two alternatives:
Independent encoders per time‑slice aligned via orthogonal Procrustes transforms; or


Continued pre‑training with epoch‑specific adapters, anchored by shared lexical pivots.


A concept cluster is a set of segments discovered by unsupervised methods with explicit stability and interpretability criteria (Section 7.2). For each cluster we define per tradition and epoch a centroid (mean or robust estimator over embedded members) and a prevalence (proportion of segments assigned in that slice).
2.2 Hypotheses
H1 (Emergent Ontology): Unsupervised clustering yields a finite, recurrent set of clusters robust across (a) translation variants, (b) epoch slices, and (c) sub‑corpus perturbations. Robustness is adjudicated via bootstrap stability (ARI/NMI), internal validity (silhouette/DBI), and blinded expert labeling (Cohen’s κ).


H2 (Temporal Recurrence): Cluster prevalence and/or centroid trajectories over epochs exhibit non‑random recurrence (no a priori shape assumed). Detection uses dynamic time warping (DTW) for misaligned timelines and change‑point methods (PELT, CUSUM) to distinguish discontinuities from drift.


2.3 Pattern‑Agnostic Predictions
P1: A non‑trivial subset of clusters persists across traditions and epochs (high CRS).
 P2: ITCA peaks near documented exchange/reform periods (diffusion or convergent response).
 P3: Trajectories deviate from nulls, supporting structured recurrence.
 P4: Cluster identities remain stable under translation‑family down‑weighting and liturgical masking.
2.4 Guardrails and Failure Modes
Universals‑collapse: If ≥ 80% of clusters map neatly to NSM semantic primes, we have rediscovered linguistic universals, not sacred recurrences; H1 is falsified.


Liturgical echo: Formulaic reuse inflates persistence; controlled via NM‑5 (masking) and explicit template down‑weights.


Translator imprint: Style dominates semantics; controlled via NM‑4 (family variance), lineage IDs, Levene checks.


Genre confound: Wisdom vs narrative vs legal; controlled via NM‑2 (genre‑matched secular sets).



3. Validation Hierarchy (Pre‑Registered Staircase)
Goal: distinguish true semantic convergence from superficial co‑occurrence via a transparent staircase of evidence.
VS‑0 — Semantic Validity of Embeddings (Diachronic Calibration)
Design: Expert‑curated Gold Pairs test cross‑language equivalence and scope (e.g., ḥesed ↔ agápē ↔ maitrī ↔ raḥma), evaluated with top‑k retrieval and expert‑similarity vs cosine. Benchmark LaBSE and multilingual SBERT; apply light domain‑tuning for ancient slices; report ablations with and without diachronic adapters.
 Pass: Top‑5 ≥ 0.70 across ≥ 70% of concept families; Spearman ρ ≥ 0.50 (p < 0.01).
 Stress tests: polysemy (“spirit,” “law,” “emptiness”), negation sensitivity, preservation of parallelism.
 Stopping rule: If VS‑0 fails twice with independent expert panels, halt H1/H2 claims and publish negative findings.
Level 1 — Cluster Meaningfulness (H1: stability + interpretability)
Metrics: bootstrap ARI/NMI across 500+ resamples; blinded recognition (Cohen’s κ) by area specialists; negative controls (genre‑matched secular corpora); internal validity (silhouette, DBI).
 Pass: median ARI ≥ 0.55; NMI ≥ 0.55; κ ≥ 0.60 for majority clusters; sacred CRS distribution stochastically dominates controls (Δ ≥ 0.15 Cohen’s d).
 Ablations: remove liturgical templates; vary cluster granularity; compare density vs manifold algorithms; Goldilocks Zone: 12–60 clusters total.
Level 2 — Sacred Specificity (H1: sacred vs secular separation)
Test: Compare CRS distributions (sacred vs secular) via one‑sided Mann–Whitney U and Cliff’s delta; check translation‑family heteroskedasticity (Levene).
 Pass: U test p < 0.01, Cliff’s δ ≥ 0.33.
 Bayesian complement: posterior probability that ΔCRS > 0 under weakly informative priors.
Level 3 — Temporal Structure (H2)
Analyses: DTW (and derivative DTW) on prevalence and centroid‑change series; Ljung–Box for serial dependence; PELT/CUSUM for regime shifts; spectral tests for periodicity.
 Pass: separation from nulls on DTW distance distributions; significant autocorrelation or structural breaks in a pre‑specified fraction of clusters.

4. Metrics (Definitions and Properties)
4.1 Semantic Stability (S)
For each cluster, compute an epoch‑average centroid across traditions, then the mean cosine similarity between consecutive epoch‑averaged centroids. Rescale to [0,1] for reporting. High values indicate stable meanings through time, independent of mere re‑use (checked via NM‑5).
4.2 Membership Persistence (P)
Compute the Jaccard index of segment memberships across adjacent epochs using segment IDs and hashed signatures to absorb minor translation variance. High values indicate persistent membership over time. We explicitly check that S remains high when P is perturbed via NM‑5 masking (purifying S from formulaic persistence).
4.3 Cross‑Tradition Presence (T‑share)
Compute the fraction of traditions in which the cluster appears at least once. Optionally re‑weight by geographic or linguistic distance to encourage breadth across families.
4.4 Composite CRS
CRS = α·S + β·P + γ·T‑share, with α + β + γ = 1 (defaults: α = 0.4, β = 0.4, γ = 0.2). We report a simplex sweep and Kendall rank correlations to assess sensitivity of rankings under weight variation.
4.5 Inter‑Tradition Conceptual Alignment (ITCA)
For each epoch, compute pairwise cosine similarities between per‑tradition centroids for the cluster and take the median (robust to outliers). Average across epochs to obtain overall ITCA. We inspect ITCA peaks against historical contact windows; peaks must dissipate under NM‑4 if driven by translation genealogy rather than concept.
4.6 Temporal Trajectories and DTW
Track for each cluster: (a) prevalence series per epoch, (b) cosine‑based centroid change per epoch. Z‑score both; use DTW/derivative DTW to align mis‑phased timelines across traditions. Change‑point suite: PELT (sparse regime shifts), CUSUM (gradual drifts). Control FDR with Benjamini–Hochberg across clusters.
4.7 Aggregation and Meta‑Analysis
For multi‑tradition summaries, apply random‑effects meta‑analysis to CRS components (Fisher‑z transform for cosine‑based terms). Report pooled mean and between‑cluster variance with profile‑likelihood intervals.

5. Null Models and Falsification
5.1 Pre‑Registered Nulls
NM‑1 Random Shuffle: shuffle segment‑to‑epoch assignment within each tradition (chance co‑occurrence).


NM‑2 Genre Match: secular philosophy/legal corpora matched by era/language (humanistic baseline).


NM‑3 Within‑Tradition Scramble: permute epoch order per tradition (tests serial dependence; H2 falsification gate).


NM‑4 Translation Family Control: compute metrics by translation lineage; compare pooled vs family‑wise with Levene variance checks; down‑weight identical phrasing within families.


NM‑5 Lexical Masking: randomly mask high‑frequency function words and liturgical templates (removes formulaic echo; purifies S from P).


5.2 Dual Ablatio Stress (Reviewer Priority)
We pre‑register a dual ablatio test (NM‑4 + NM‑5 simultaneously) as the decisive H1 purification. For top‑ranked clusters by CRS/ITCA, we require that S and ITCA remain robust under concurrent controls for external (translation genealogy) and internal (formulaic reuse) biases. Failure downgrades or rejects H1 claims for those clusters.
5.3 Falsification Criteria
H1 fails if: median ARI < 0.40 or NMI < 0.40 (≥ 500 bootstraps); or κ < 0.50 on majority clusters; or universals‑collapse (≥ 80% clusters map to NSM primes).


H2 fails if: sacred vs nulls show no separation for CRS/ITCA (U p ≥ 0.01); or Ljung–Box fails to reject independence in ≥ 80% trajectories; or DTW distances match NM‑3 distributions.


Stopping rule: VS‑0 fails twice ⇒ publish negative findings; suspend H1/H2.



6. Corpus, Governance, and Scope
6.1 Text‑Based Corpora
Multilingual, diachronic sources include: Vedic/Upanishadic; Buddhist (Pali Canon; selected Mahayana); Taoist (Tao Te Ching, Zhuangzi); Zoroastrian (Avesta; Pahlavi); Abrahamic (Tanakh in Hebrew/Septuagint/major translations; New Testament in Koine Greek/major translations; Qur’ān in Arabic/major translations); Stoic/Greek fragments; Confucian Analects/Mencius; selected textual African and American sources with strong text anchors. We track edition/translator metadata and license status for each segment.
Hadith protocol: primary sets are Sahih al‑Bukhari and Sahih Muslim. We track isnad quality; include narrations with explicit topical anchors; deduplicate unless isnad variance is analytic; sensitivity analyses by school and mutawatir vs ahad classification. All inclusion criteria undergo pre‑review with two Islamic‑studies scholars.
6.2 Translation Genealogy and Confounds
Maintain translation‑family IDs (source, translator, era, school). Down‑weight identical‑phrase overlaps within families; prioritize original‑language slices when coverage permits. NM‑4 and Levene quantify family‑wise variance. For verse numbering differences (e.g., MT vs LXX), we establish crosswalk tables with fuzzy alignment tolerance and report robustness windows in sensitivity analyses.
6.3 Indigenous Knowledge Systems (IKS) — Ethical Boundary
Oral/performative/territorially embedded systems (e.g., Songlines, oral histories) require multimodal audio–text–geo models and community governance. We commit to a separate, co‑designed study under CARE (Collective Benefit, Authority to Control, Responsibility, Ethics) and Indigenous Data Sovereignty. RRM is evidence‑seeking, not doctrine‑asserting.
6.4 Data Management and Access
All derived embeddings, cluster assignments, and metrics are versioned with content hashes. Access to raw texts respects licensing and community constraints. We provide reproducible scripts for obtaining public‑domain sources and redaction wrappers for restricted materials.

7. Methods (RRM Pipeline)
7.1 Preprocessing and Embedding
Canonical segmentation (verse/aphorism/ayah); language‑specific normalization; preservation of negation and parallelism; punctuation‑aware sentence splitting for Greek/Hebrew/Arabic. Evaluate LaBSE and multilingual SBERT; apply epoch‑sliced adaptation using ancient corpora (continued pre‑training or retrofitting with anchor lexicons) to stabilize meanings across time.
 Quality gates: per‑language coverage ≥ 90%; OOV ≤ 2% after transliteration/normalization; back‑translation spot checks for difficult pairs.
7.2 Unsupervised Cluster Discovery (H1)
Trial HDBSCAN (density cores + noise), spectral clustering (global manifold), and transformer topic models (interpretability). Retain clusters passing stability filters (bootstrap ARI/NMI; silhouette/DBI). Goldilocks Zone: 12–60 clusters total; median silhouette ≥ 0.10; ARI ≥ 0.55; κ ≥ 0.60.
 Interpretability layer: for each cluster, surface top‑nearest segments per tradition, salient n‑grams, and token‑level attributions from a lightweight probing classifier to aid expert labeling.
7.3 Temporal Recurrence Analysis (H2)
Compare (i) prevalence series and (ii) centroid trajectories against nulls. Use DTW/derivative DTW, PELT/CUSUM for change points, and spectral tests for periodicity without prespecifying shape.
 Confound control:
Liturgical reuse (blessings, responsorial psalms) inflates recurrence ⇒ mark and down‑weight templates so the model privileges conceptual over formulaic recurrence (NM‑5).


Diffusion fingerprint: ITCA peaks coincident with known translation waves (e.g., Septuagint uptake) must dissipate under NM‑4 if driven chiefly by phrasing rather than concept.


7.4 Power and Simulation Plan
Simulate synthetic corpora with known latent clusters and mixing schedules; inject translation‑family artifacts and liturgical templates; estimate expected power for detecting CRS/ITCA separation at target sample sizes. Report Type I/II error curves; preregister minimal viable corpus sizes per tradition.
7.5 Implementation Details
Containerized pipeline; orchestration via Prefect/Argo; artifact logging with MLflow or Weights & Biases; seeds fixed per grid; deterministic export of intermediate artifacts (embeddings, cluster labels, metrics, null draws). Measure and report CO₂ footprint (Section 8.4).

8. Risks, Compute, and Reproducibility
8.1 Practical Compute Plan
Pilot (Abrahamic; ~70–120k segments): Embedding 6–12 GPU‑hours on 8×A100; clustering + bootstraps 200–400 CPU‑hours.


Full corpus (0.5–1.0M segments): Embedding 24–48 GPU‑hours; clustering bootstraps 2–4k CPU‑hours (parallel).


Orchestration with Prefect/Argo; deterministic seeds; artifact logging.


8.2 Risk Register and Mitigations
Ancient‑language weakness → VS‑0; ancient‑slice adaptation; expert Gold Pairs.


Universals‑collapse (reject H1) → enforce Goldilocks Zone; alternate algorithms; accept falsification if persistent.


Translation‑family bias → NM‑4; lineage metadata; Levene checks.


Hadith selection controversy → transparent inclusion/exclusion; isnad metadata; pre‑review; mutawatir/ahad sensitivity.


Compute overrun → pilot pruning; early stopping; containerized parallel runs.


Ethical drift → annual governance review with community advisors.


8.3 Reproducibility Checklist
Public preregistration (OSF/registered‑report) with frozen thresholds and nulls.


Hashes for corpora and segmenters; versioned translation‑family tables.


Seeds/config dumps for all clustering runs; bootstrap logs.


Open notebooks for metrics (CRS/ITCA) and null generators.


Expert‑review protocol and inter‑rater scripts (κ).


Data access notes for restricted texts; redaction wrappers.


8.4 Sustainability
Estimate and report energy use and carbon cost (GPU/CPU hours). Adopt mixed precision, caching, and pruning of ablations. Consider offsets and publish efficiency metrics alongside results.

9. Program Phasing, Interpretation, and Future Work
9.1 Phasing
Phase 1 (Paper 1): VS‑0 + Abrahamic pilot (initial H1/H2).


Phase 2 (Paper 2): Full‑corpus execution (1M+ segments) with expanded nulls and Bayesian synthesis.


Phase 3 (Paper 3): IKS multimodal extension (audio–text–geo) co‑designed under CARE/Indigenous Data Sovereignty.


9.2 Interpretive Triad
Use ITCA and CRS plus geography/chronology to triage among:
A) Universal moral grammar: high alignment without spatiotemporal proximity.


B) Diffusion: gradients tracking historical contact.


C) Transcendent revelation: patterns resilient to diffusion and stress (NM‑4/NM‑5), maintaining high CRS/ITCA.


9.3 Deferred: Socio‑Stress Linkage Index (SSLI)
Correlate CRS dips/peaks with exogenous proxies (conflict indices, paleoclimate, population) via Granger, cross‑correlation, and lag grids.

10. Case Vignette (Illustrative)
Mercy/Compassion cluster: pilot retrieval aligns Hebrew ḥesed, Greek agápē, Arabic raḥma, Pali karuṇā, and Sanskrit maitrī within a single manifold region after diachronic calibration. Under NM‑2 (secular match), analogous virtue language appears but shows lower ITCA and fragmented centroids, suggesting sacred‑specific cohesion. Experts label sub‑senses (covenant‑loyalty vs universal benevolence), increasing κ and enabling sensitivity to theological nuance. Under the dual ablatio (NM‑4 + NM‑5), top‑ranked clusters maintain S and ITCA beyond confidence thresholds, supporting H1 purity.

11. Limitations
Embedding spaces are proxies—not proofs—of meaning; we temper claims and prefer negative conclusions when metrics fail. Diachronic calibration reduces but cannot eliminate presentism; ancient genre conventions require ongoing expert input. Sacred specificity may be confounded by educational/liturgical pipelines; our masking and down‑weights remain partial. Multi‑author translations encode ideology; we mitigate but cannot remove this entirely. Power limitations for rarer traditions or epochs may bias CRS downward.

12. Ethics Statement
This project involves sacred texts and cross‑cultural materials. We commit to: (a) multilingual expert review; (b) transparent inclusion/exclusion criteria; (c) no extraction of Indigenous Knowledge Systems without community governance; (d) fully reproducible methods; (e) humility in interpretation—RRM is evidence‑seeking, not doctrine‑asserting.

13. Author Contributions
S.A.K.: conception, ethics scaffolding, corpus protocol, theory.
 Albert: formalization, metric design (ITCA/CRS), validation staircase, drafting.

14. Data and Code Availability (Pre‑Registered)
Upon acceptance of Paper 1, we will release: (i) preprocessing scripts and configuration (epoch dictionaries, translation genealogy tables); (ii) VS‑0 Gold Pairs (non‑copyright‑restricted snippets), embedding configs, and clustering seeds; (iii) null‑model generators and analysis notebooks.

15. Reviewer Guide (for Double‑Blind)
Claims ↔ Evidence: Are H1/H2 claims strictly tied to preregistered tests?


Metrics: Are CRS/ITCA computed as defined; are weight sensitivities reported?


Confounds: Are liturgical and translation‑family effects addressed with NM‑5/NM‑4 and the dual ablatio?


Ethics: Is the IKS boundary respected; are licenses documented?


Reproducibility: Do artifacts, seeds, and hashes line up?



16. References (selection; URLs are illustrative)
Feng et al., LaBSE — https://arxiv.org/abs/2007.01852
 Reimers & Gurevych, Sentence‑BERT — https://arxiv.org/abs/1908.10084
 CARE Principles (Data Science Journal) — https://datascience.codata.org/articles/dsj-2020-043
 Hamilton et al., Diachronic semantics — https://aclanthology.org/P16-1141/
 ARI/NMI overview — https://faculty.washington.edu/kayee/pca/supp.pdf
 Dynamic Time Warping (classic) — https://cdn.aaai.org/Workshops/1994/WS-94-03/WS94-03-031.pdf
 Derivative DTW — https://ics.uci.edu/~pazzani/Publications/sdm01.pdf
 Stanford diachronic reference — https://nlp.stanford.edu/pubs/hamilton2016diachronic.pdf
 Sunnah (Bukhari) — https://sunnah.com/bukhari
 HDBSCAN (JOSS) — https://joss.theoj.org/papers/10.21105/joss.00205.pdf
 Mann–Whitney U (Project Euclid) — https://projecteuclid.org/journals/annals-of-mathematical-statistics/volume-18/issue-1/On-the-Distribution-of-the-Two-Sample-Rank-Sum-Statistic/10.1214/aoms/1177730491.full
 Levene’s test note — https://arxiv.org/pdf/1010.0308

Appendix A — Open Items for Co‑Author Decision
Base models for VS‑0: choose LaBSE vs multilingual SBERT variants.


Gold Pair Catalog: finalize concept families; recruit expert panel (Hebrew Bible, NT Greek, Qur’ān Arabic, Sanskrit, Pali, Classical Chinese).


Hadith protocol: lock draft; identify two Islamic‑studies pre‑reviewers.


Thresholds and Nulls: approve ARI/NMI/κ, ΔCRS, and null suite (U, Cliff’s δ, Levene).


Appendix B — Implementation Sketch (Reproducible Pseudocode; plain text)
VS‑0
 Load model/configs → embed time‑sliced corpus → evaluate Top‑k + ρ on Gold Pairs → stress tests (polysemy/negation/parallelism).
 Clustering grid (HDBSCAN, spectral) with fixed seeds → retain clusters meeting stability thresholds.
 Metrics (S, P, T‑share, CRS, ITCA) → Nulls (NM‑1..5) → Dual ablatio (NM‑4 + NM‑5).
 H1/H2 adjudication vs preregistered gates → export artifacts (hashes, seeds, labels, metrics, null draws).
Appendix C — Reporting Table Templates (plain text)
Table 1: Gold Pair retrieval (Top‑k, Spearman), per language.
 Table 2: Cluster stability (ARI/NMI) and human agreement (κ).
 Table 3: CRS/ITCA by tradition and epoch; null comparisons (U, Cliff’s δ).
 Figures:
 • Fig. 1: UMAP of retained clusters with translation‑family overlays.
 • Fig. 2: DTW‑aligned prevalence trajectories (per cluster).
 • Fig. 3: Change‑point diagnostics (PELT/CUSUM).
Appendix D — Sample Gold Pair Families
Mercy/Compassion: ḥesed ↔ agápē ↔ raḥma ↔ karuṇā ↔ maitrī.
 Justice/Righteousness: tsedeq/mishpat ↔ dikaiosynē ↔ ʿadl.
 Breath/Spirit: rûaḥ ↔ pneuma ↔ rūḥ.
 Wisdom: ḥokhmah ↔ sophia ↔ ḥikma.
 Way/Path: derekh ↔ hodos ↔ ṣirāṭ.
Appendix E — Configuration Snapshot (plain text)
Tokenization/segmentation rules per language; adapter learning rates; slice boundaries; Procrustes alignment flags; HDBSCAN min_cluster_size grid; spectral affinity variants; liturgical template lists and down‑weight multipliers.
Appendix F — Null Model Sketches (plain text)
NM‑3 scramble epoch order within each tradition; recompute metrics and compare DTW distance distributions to observed.
 NM‑5 mask high‑frequency function words and liturgical templates; re‑run clustering and recompute CRS/ITCA to test over‑reliance on formulae.

Figure 0 — Schematic (ASCII)
[Corpus] → [Preprocessing + Segmentation] → [Embeddings (diachronic adapters)] →
 → [Clustering (HDBSCAN / Spectral)] → [Stability Filters] → [Retained Clusters] →
 → [Metrics: S, P, T‑share, CRS, ITCA] → [Null Models] → [H1/H2 Tests] → [Interpretive Triad]

Cover Letter (Registered‑Report style; draft)
Dear Editors,
 We submit “The Revelation Recurrence Model (RRM): Discovering Cross‑Cultural Recurrences of Sacred Meaning Without an Imposed Ontology” as a registered report. RRM offers a falsifiable, preregistered framework to test whether sacred corpora exhibit recurrent conceptual clusters across languages, traditions, and epochs. The design is pattern‑agnostic: ontology emerges from the data rather than hand‑crafted categories. We introduce two core metrics—ITCA and CRS—and a validation staircase that integrates expert judgment with statistical stability, multiple nulls, temporal analyses, and a dual ablatio stress (NM‑4 + NM‑5) to purify conceptual signals from translation genealogy and liturgical echo. The protocol emphasizes ethical handling of sacred materials, multilingual expert review, and defers multimodal Indigenous systems to a co‑designed follow‑on under CARE principles.
 We believe this work will interest readers in cultural evolution, digital humanities, religious studies, and computational linguistics, providing a reproducible bridge between interpretive scholarship and quantitative evidence.
 Sincerely,
 Simeon A. Kepp and Albert



