# Stage 1 — Candidate research questions (42)

Date: 2026-11-24. Author: Research Director (Claude, autonomous). Status: candidate map, **not findings**.

Resource constraint that shapes tractability (audited 2026-11-24): 4 CPU cores, 15 GB RAM, no GPU; open-weight
models ≤ ~1.5B parameters can be run in fp32 on CPU for teacher-forced forward passes over a few hundred thousand
tokens; training from scratch only at toy scale. Literature APIs: arXiv, OpenAlex, Crossref, Semantic Scholar (rate-limited).
The "research notebook" referred to in the mission brief was not found in the repository, the user's other repositories or
Google Drive (searched); the three hypotheses H1–H3 stated in the brief are used as the starting material instead.

Columns: **Phenomenon** · **Known** · **Unknown** · **Why it matters** · **Resolving evidence** · **Tractable here?** (Y / P = partly / N) · **What a discovery looks like**.
Prior-art statements in this table are the director's working knowledge and are verified (or corrected) in `02_literature_matrix.md`.

## A. Inference and computational efficiency

| ID | Phenomenon | Known | Unknown | Why it matters | Resolving evidence | Tr. | Discovery |
|---|---|---|---|---|---|---|---|
| A1 | Cross-model state injection: replace the bottom *k* layers of a large LM with a small LM + learned affine map | Affine stitching between LMs of different size works for feature transfer (model-stitching literature); self layer-skipping/early exit (LayerSkip, CALM) | Whether a small model's state can stand in for a *deep* prefix of a large model, and whether it ever beats the large model's *own* cheaper prefix at equal FLOPs | Direct test of H1/H2 (cross-model latent speculation) | Next-token KL to the full large model vs *k*, vs self-skip baselines at matched FLOPs, across a model family | Y | A depth-correspondence law and a clear verdict on whether cross-model latents dominate self-prefixes |
| A2 | Which large-model depth does a small model's final layer correspond to? | CKA cross-depth correspondences in CNNs (Kornblith 2019); Platonic-representation alignment grows with scale | Whether the best-matching layer sits at a constant relative depth or scales with the size ratio, and whether *similarity* agrees with *functional* (injection) correspondence | Rule 5: similarity ≠ functional equivalence; tests it directly | CKA/linear-R² vs injection-loss argmax layer across ≥ 6 pairs | Y | Dissociation (or agreement) between representational and functional correspondence |
| A3 | Acceptance burstiness in speculative decoding | Leviathan et al. formula assumes i.i.d. acceptance; dynamic draft-length methods exist | Size of i.i.d.-formula error on real text; how heterogeneity in per-token α changes optimal γ | Planning γ and tree shapes | Per-token α_t = 1−TV(p,q) on real text; compare realised vs i.i.d. accepted length | Y | Quantified correction (convexity: heterogeneity raises E[L]) — likely small novelty |
| A4 | Latent (feature) vs token prediction for drafting | EAGLE (feature regression + CE); EAGLE-3 drops feature loss as it limits scaling | When feature-space targets help vs hurt, controlled for head capacity | Q8; H2 | Same draft head trained with MSE-on-features / KL-on-tokens / both; acceptance vs data size | Y | Controlled crossover curve |
| A5 | Verification cost lower bound for lossless speculation | Block verification optimality (Sun et al. 2024); SpecTr optimal transport | Bound on verifiable tokens/step given draft-target TV profile | Q7 | Theory + simulation | P | Tight bound — theory-heavy |
| A6 | Adaptive verification preserving guarantees | Lossless only with exact rejection sampling; "lenient"/typical acceptance is lossy | Quantified distribution shift of lenient schemes on downstream metrics | Q9 | Measure KL of realised output dist under lenient acceptance | Y | Pareto curve; likely incremental |
| A7 | Optimal parallel vs sequential speculation | Tree/block drafting literature (Sequoia, SpecInfer) | Closed-form optimum under memory-bandwidth model | Q12 | Analytic roofline model + measured α | P | Modest |
| A8 | Prefill/decode bottleneck attribution (architecture vs serving) | Roofline analyses (DistServe, Splitwise) | — mostly answered | Q10 | GPU profiling | N | — |
| A9 | Cross-request reuse of intermediate states (non-prefix KV reuse) | CacheBlend, EPIC, prompt cache | Error bound of positional re-use | Q11 | KV patch experiments | P | Mostly done |
| A10 | Uncertainty-routed compute (early exit) calibration under shift | CALM, LayerSkip, confidence-based exit | Whether exit criteria fail on distribution shift systematically | H3 | Exit-vs-true-change rates across domains | Y | Blind-spot map |
| A11 | KV eviction guided by a small model's attention | SnapKV, H2O; small-model guidance proposals | Whether attention importance transfers across scale | memory/latency | Overlap of top-k attended tokens across Pythia sizes | Y | Transfer law; crowded area |
| A12 | Multi-token prediction heads: what horizon is linearly decodable from the residual stream | "Future lens" (Pal et al. 2023); Medusa | How far-ahead decodability scales with model size | H1/MTP | Linear probes for t+k tokens across Pythia sizes | Y | Scaling law of look-ahead content; partly known |

## B. Representation and internal computational state

| ID | Phenomenon | Known | Unknown | Why it matters | Resolving evidence | Tr. | Discovery |
|---|---|---|---|---|---|---|---|
| B1 | Similar outputs ⇒ similar computation? | Platonic hypothesis; stitching; universality of neurons | Whether behaviourally matched pairs differ in *functional* layer correspondence | Q1 | Match outputs, compare injection maps | Y | Dissociation result |
| B2 | Representation similarity vs downstream usefulness | CKA criticisms (Davari et al. 2022) | Rank correlation between CKA/R² and stitched-model loss across many layer pairs | Q6 | Large grid of layer pairs | Y | Quantified mismatch between similarity and function |
| B3 | Invariant computational states across prompts | Universal neurons; attention sinks; massive activations | Whether "positional/sink" dims dominate cross-model alignment metrics | confounder for B1/B2 | Remove massive-activation dims, recompute | Y | Confound audit |
| B4 | Geometry predicts copy vs recompute | Induction heads, copying circuits | Linear signature that predicts copying before it happens | Q4 | Probe on induction vs non-induction tokens | Y | Probe; crowded |
| B5 | Layer-wise information transformation ("linear" layers) | "Your transformer is secretly linear"; layer pruning studies | Which layers are replaceable by affine maps, by depth and size | A1 baseline | Affine replacement of contiguous blocks | Y | Partly known |
| B6 | JEPA-style latent prediction in LMs | LLM-JEPA (2025) proposals | Whether latent-prediction objectives change cross-model alignment | H1 | Small training runs | P | Costly |
| B7 | SAE feature transfer across sizes | Model-stitching SAE transfer (2025) | Which features fail to transfer | interpretability | SAE training | P | Compute-heavy |
| B8 | Cross-architecture state transfer (transformer ↔ SSM) | Little | Whether affine maps suffice between Mamba and transformer residuals | Q2 | Mamba-130m ↔ Pythia-160m stitching | Y | New pair type |
| B9 | Rogue dimensions/anisotropy distort similarity metrics | Timkey & van Schijndel 2021 | Effect on cross-model metrics | confound | Standardise vs not | Y | Methodological |
| B10 | Training-time emergence of cross-model correspondence | Pythia checkpoints; Platonic convergence over training | When small→large correspondence stabilises | dynamics | Pythia checkpoint grid | Y | New dynamics observation |

## C. Memory and continual learning

| ID | Phenomenon | Known | Unknown | Why it matters | Resolving evidence | Tr. | Discovery |
|---|---|---|---|---|---|---|---|
| C1 | Weights vs context vs retrieval allocation | RAG vs FT comparisons (Ovadia 2024) | Principled decision rule from frequency/volatility | Q13 | Controlled fact-injection | P | Rule; needs fine-tuning at scale |
| C2 | Retrieval less reliable than recomputation | Context-memory conflicts (Xie et al. 2023) | Crossover point by computation length | Q14 | Synthetic arithmetic with injected retrieved results | Y | Crossover curve |
| C3 | Consolidation without interference | Replay, EWC, sleep-like replay | Sparse-update consolidation in small LMs | Q15 | Toy continual learning | Y | Crowded |
| C4 | Contradictory memories over time | Knowledge-editing ripple effects | Recency vs frequency arbitration law | Q16 | Edited facts with repeated contradictions | P | |
| C5 | Separating retrieval from update | Memory-layer architectures | Independent optimisation | Q17 | Architecture study | P | |
| C6 | When forgetting helps | Active forgetting (Zhou et al. 2022), plasticity loss | Measurable conditions | Q18 | Toy resets | Y | Crowded |
| C7 | KV-cache as memory: what is lost under compression | Quantised/evicted KV studies | Which computation types fail first | memory | Task-type ablation | Y | Benchmarking |
| C8 | Biological consolidation analogy (CLS theory) | McClelland 1995 CLS; replay | Formal correspondence test | Q27 | Theory | P | Mostly analogy |

## D. Reasoning and computational reliability

| ID | Phenomenon | Known | Unknown | Why it matters | Resolving evidence | Tr. | Discovery |
|---|---|---|---|---|---|---|---|
| D1 | Read vs recompute written intermediates | **Done by user's own prior programme** (novel_discovery/cot_reliance) | — | — | — | — | Excluded (duplicate) |
| D2 | Error propagation vs correction | Nguyen et al. EMNLP 2026; user's RC programme Direction 1 | Mechanism of use of wrong value | Q19 | Open-weight interventions | P | Overlaps user's RC Paper 1 — excluded to avoid duplication |
| D3 | Pre-error internal signal | Correctness probes (many) | Causal use | Q20 | Probes + patching | P | Crowded |
| D4 | Non-uniform gains from test-time compute | Snell et al. 2024; task-dependent TTC | Which task features predict gain | Q21 | Many API calls | P | |
| D5 | Knowledge vs computation uncertainty | Epistemic/aleatoric LLM work | Internal separability | Q22 | Toy tasks | Y | |
| D6 | Stability of reasoning strategies | — | — | Q23 | | P | |
| D7 | Interventions that improve reliability | Steering vectors, ITI | Improvement without behaviour damage | Q24 | | P | |
| D8 | Algorithm execution vs approximation | Grokking, length generalisation | | | | Y | Crowded |
| D9 | Depth hazard in toy chains | Firke & Kannan 2026 | Mechanism | | | Y | |

## E. Alternative architectures and biology

| ID | Phenomenon | Known | Unknown | Why it matters | Resolving evidence | Tr. | Discovery |
|---|---|---|---|---|---|---|---|
| E1 | Diffusion LMs' error-correction | Remasking (LLaDA, MDLM) | Whether diffusion LMs correct injected errors more | Q25 | Needs ≥1B diffusion LMs on CPU | N/P | |
| E2 | SSM state efficiency | Mamba recall limits (Arora et al.) | — partly answered | Q26 | | P | |
| E3 | MoE routing blind spots | Expert collapse studies | Systematic blind spots | Q28 | OLMoE too big for CPU | N | |
| E4 | Predictive coding as LM objective | PC networks | Equivalence to backprop limits | | | P | |
| E5 | Engram-like sparse fact storage | ROME/MEMIT localisation debates | | | | P | |
| E6 | Hippocampal indexing ↔ retrieval augmentation | Theory analogy | | | | P | |

## Cross-cutting intersections flagged as potentially neglected
1. **A1 + A2 + B2**: functional (injection) vs representational (CKA) correspondence across model *scale* — tests H1 and rule 5 simultaneously.
2. **A3 + A4**: what fraction of a large model's next-token information is linearly available in a small model's state (an upper bound on any "latent drafter").
3. **B8**: cross-architecture stitching (SSM ↔ transformer) as a test of Q2.
4. **B10**: when during training do cross-scale correspondences appear (Pythia checkpoints share data order).
