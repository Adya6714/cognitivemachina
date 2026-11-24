# Stage 3–4 — Novelty audit summary and ranked opportunity portfolio

Weights: novelty 25%, significance 20%, feasibility 15%, falsifiability 10%, evidence accessibility 10%, reproducibility 10%, time/compute 10%. Scores 1–10. Novelty classes from `02_literature_matrix.md` (agent audit, papers retrieved via arXiv/OpenAlex in this session).

| Rank | ID | Opportunity | Nov | Sig | Feas | Fals | Evid | Repro | Time | **Weighted** | Closest prior work | Novelty class | Why it matters | Decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | X1 | Cross-scale state injection: objective × depth × scale; functional vs representational correspondence; vs self-prefix at matched cost (A1+A2+B2+H1/H2) | 7 | 7 | 8 | 9 | 9 | 9 | 7 | **7.75** | 2506.06609; 2606.03280; 2603.18908; 2608.09521 | N2–N3 | Resolves a 2026 contradiction; directly tests H1/H2 | SELECTED #1 |
| 2 | X3 | Heterogeneity of per-token acceptance and error of the i.i.d. speculative-decoding formula (A3) | 4 | 5 | 9 | 8 | 9 | 9 | 9 | **6.85** | 2211.17192; 2405.19715; 2608.30427 | N1–N2 | Planning γ; cheap with shared infra | SELECTED #2 (secondary, cheap) |
| 3 | X2 | Emergence over training of cross-scale functional correspondence (Pythia checkpoints) (B10) | 6 | 5 | 8 | 7 | 9 | 9 | 6 | **6.80** | 2502.18710 (vision); Huh 2024 | N2–N3 | Dynamics of when small/large models become interchangeable | SELECTED #3 (folded into #1 as an arm if budget allows) |
| 4 | X5 | Attention-importance transfer across scale for KV eviction (A11) | 4 | 6 | 8 | 8 | 8 | 9 | 8 | **6.70** | SnapKV; small-model-guided eviction | N2 | KV memory | Rejected: crowded, incremental |
| 5 | X10 | Early-exit criteria blind spots under shift (A10) | 4 | 6 | 7 | 8 | 8 | 8 | 7 | **6.35** | CALM; LayerSkip | N2 | H3 | Runner-up |
| 6 | X7 | Future-token linear decodability vs scale (A12) | 3 | 5 | 8 | 8 | 9 | 9 | 8 | **6.35** | Future Lens; Wu 2024; 2604.12493 | N1–N2 | MTP | Rejected: largely answered |
| 7 | X6 | Mamba↔Pythia cross-architecture stitching (B8) | 5 | 5 | 7 | 8 | 8 | 8 | 6 | **6.30** | 2609.38261 (RWKV↔Pythia) | N2 | Q2 | Rejected for now: NinaXander covers cross-architecture; runner-up |
| 8 | X4 | Controlled feature-vs-token targets for draft heads (A4) | 5 | 6 | 5 | 8 | 8 | 8 | 4 | **6.00** | EAGLE-3 2503.01840; HASS | N2 | Q8, H2 | Rejected: CPU training of drafters too slow for adequate data scaling |
| 9 | X8 | Retrieval vs recomputation crossover with injected intermediate results (C2) | 4 | 6 | 6 | 8 | 7 | 8 | 6 | **6.00** | Xie 2023; user's RvC | N2 | Q14 | Rejected: overlaps user's RvC/RR programmes |
| 10 | X11 | Lenient verification: realised distribution shift (A6) | 3 | 5 | 7 | 8 | 8 | 8 | 8 | **6.00** | typical acceptance (Medusa) | N1–N2 | Q9 | Rejected: incremental |
| 11 | X9 | Knowledge- vs computation-uncertainty separability (D5) | 5 | 7 | 5 | 6 | 6 | 7 | 5 | **5.80** | epistemic/aleatoric LLM probes | N2 | Q22 | Rejected: needs larger models to have the competence |

## Notes on the ranking (honesty)
* **Bias disclosure.** X1's feasibility and time scores benefit from injection infrastructure built during the audit (decision 6). Re-scoring X1 with feasibility 6 and time 5 gives 7.25, still rank 1, so the selection does not depend on that advantage.
* **Why X1 ranks first.** The 2026 literature holds a direct contradiction. Mid-depth injection into another model's frozen upper layers "works" in 2608.09521 (72–88% next-token agreement) but is "destructive" in 2606.03280 (Pythia-160M→410M) and gives 0% in 2603.18908. Each paper varies one factor and fixes the others:
  * depth
  * size ratio
  * map objective
  * evaluation metric

  A factorial sweep over these factors in a single controlled family is new as a design (N2–N3). It also bears directly on H1 and H2.
* **X3 and X2.** These are selected as the 2nd and 3rd candidates. X3 reuses the same forward passes (per-token p_S, p_T), so its marginal cost is near zero. X2 is run only if budget remains after X1's confirmatory runs.
* **H3 (adaptive computation).** H3 is represented only by X10 (runner-up). No H3 candidate ranked in the top three, because the adaptive-compute literature (CALM, LayerSkip, test-time scaling) is dense and a CPU-scale test would be incremental. We record this as a deliberate deprioritisation, not a refutation of H3.
