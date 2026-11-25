# Study guide: the whole programme, in and out

*Updated 2026-11-25 evening, after all E1 cells, the results-stage review and the R1 convergence check.
Sections 7 and 11 keep the interim snapshot (33 cells) for the record. **Section 13 has the final results and
supersedes them.** Every number was copied from a result file in this repo. Nothing is projected.*

---

## 0. Ten-line summary
1. **The brief.** Find (or rule out) a novel, rigorously established result about AI inference,
   representation learning or reasoning. It started from three hypotheses: H1 (small models predict large
   models' useful representations), H2 (latent prediction speeds up inference with guarantees) and H3
   (adaptive compute).
2. **Selection.** We mapped 42 candidate questions and audited about 60 papers for prior art. We ranked 11
   finalists with the brief's weights and picked **X1: cross-scale state injection ("stitching")** in the
   Pythia family. It ranked first because the 2026 literature contradicts itself on it.
3. **The experiment.** A small model's final state is affinely mapped into a big model's residual stream at
   depth k. The big model's frozen upper layers then finish the computation. We varied **size ratio, depth
   and map objective** and measured distance to the big model's own output distribution (KL).
4. **Practical result (interim, robust so far).** Every stitch, at every depth and for every source, is
   **worse than the small model on its own**. That includes an equal-size, same-data model. Stitching an
   affinely mapped state is not a useful drafter here.
5. **H1 result (interim, replicated).** For the *smaller* sources (70m, 160m → 410m), injecting at
   **depth 18 of 24** beats a plain linear read-out at the top (D_18 > 0, CI excludes 0).
   * The big model's upper layers therefore do add something beyond reading the small model out.
   * This effect **vanishes for an equal-size source** (410m-seed1: D_18 ≈ 0, best at the top).
   * An **independent re-implementation** (70m → 160m, different data and seeds) found the same interior
     optimum at 3/4 depth (k = 9 of 12).
6. **Read-out bottleneck.** An affine map plus the big model's head cannot even reproduce the small model's
   *own* distribution (KL 0.48 nats for the sibling). Much of the "stitch is worse than the source" gap is
   therefore a read-out limitation, not proof that the information is unusable.
7. **Similarity does not locate function.** CKA and R² peak at the top layer for every pair, while the
   functional optimum is at depth 18 for the smaller sources.
8. **Objective matters, but moderately.** KL-trained maps beat MSE maps by about 1.3×, below the
   preregistered 1.5× threshold.
9. **Secondary study X3 (negative).** The textbook i.i.d. speculative-decoding formula predicts real 70m → 410m
   speculative sampling within about 6%.
10. **Final decision: PRELIMINARY FINDING.** The 70m depth-18 effect held across 3 seeds, WikiText, and maps
    trained 3× longer (+0.121). An independent results-stage reviewer agreed with the label. See section 13 and
    `docs/12_final_deliverables.md`.

---

## 1. Who did what: agents and roles

The brief asked for a research organisation: a Research Director plus Agents 1–10.

**Spawned as separate subagents (3).** Each had its own context and instructions and did not see my
reasoning:

| # | Role | When | What it did | Output |
|---|---|---|---|---|
| Agent 2 | Literature / prior-art investigator | 2026-11-24 19:03 | Searched about 90 queries on the arXiv API and OpenAlex (Semantic Scholar was rate-limited), plus forward-citation crawls. It read about 60 papers, some only in targeted sections. It built the literature matrix and assigned a novelty class N0–N5 to each candidate. It was told never to cite a paper it had not retrieved. | `docs/02_literature_matrix.md` |
| Agent 8 | Adversarial reviewer (design stage) | 2026-11-24 20:24 | Tried to break the frozen E1 design. It found 18 issues: 1 fatal, 10 major, 7 minor. The fatal one: the primary comparator Δ_k (stitch vs source alone) cannot test H1, because the affine-plus-head read-out may not reproduce the source at all. | `docs/06_adversarial_review_design.md` |
| Agent 8 (fresh instance) | Adversarial reviewer (results stage) | 2026-11-25 17:45 | Read all results and code without running anything heavy. Raised 15 issues. The key one was R1: D_18 > 0 might be an artefact of under-trained k = 24 maps. Others: CIs omitted seed variance (R3); post-hoc seeds were unlabelled (R4); the FLOP statement was wrong (R9); the context-corruption decomposition was invalid (R10). Verdict: PRELIMINARY FINDING. | `docs/10_adversarial_review_results.md` |
| Agent 10 | Independent replication | 2026-11-25 00:40 → about 04:00 | Wrote new code from scratch and was forbidden from reading `xscale/` or `results/`. It used a different target (160m), different fit data (WikiText-103), different seeds (7, 8) and its own hyperparameters. It unit-tested its injection (bit-exact) and replicated both core claims. | `replication/REPORT.md` |

**Carried out by me, the Research Director, in the main session.** These roles were not separate processes,
and I say so plainly so they are not mistaken for independent work:
* Agent 1, Cartographer (42 candidates)
* Agent 3, Theory (`03_theory.md`)
* Agent 4, Mech-interp (CKA/R² and the A7 diagnostic)
* Agent 5, Systems (FLOP accounting, KV-cache speculative sampler)
* Agent 6, Memory (candidate group C)
* Agent 7, Experimental scientist (prereg, `run_cell.py`, queues)
* Agent 9, Strategist (ranking)

Their work is self-checked, not independently checked. Independence comes only from Agents 2, 8 (twice) and 10.

---

## 2. Research goal and strategy

**Goal.** One genuinely new, rigorously established finding, or an honest negative or inconclusive verdict.
The brief set non-negotiable rules:
* no fabrication
* no novelty claims without an audit
* no causal claims from correlation
* no best-seed-only reporting
* no hidden negatives
* no speed-up claims without end-to-end latency
* no treating output similarity as distribution preservation

**Strategy, as executed:**
1. **Audit resources first.** We have 4 CPU cores, 15 GB RAM and no GPU. That rules out training big
   models, so we chose questions answerable with forward passes and small maps on open-weight models
   (decision log #1).
2. **Map broadly.** 42 candidates across 5 groups (§3).
3. **Audit prior art before choosing.** Agent 2 checked each candidate against retrieved papers.
4. **Rank with the brief's weights.** Novelty 25%, significance 20%, feasibility 15%, falsifiability 10%,
   evidence 10%, reproducibility 10%, time 10%.
5. **Theory before data.** Three propositions defined what a positive H1 result would look like (§5).
6. **Preregister and freeze before any confirmatory run.** Pilots were labelled exploratory and never reused.
7. **Have the design attacked** (Agent 8). Amendments A1–A7 were adopted **before any KL result existed**.
8. **Run with exact infrastructure.** A unit test shows that re-injecting a model's own states reproduces its
   logits with zero error.
9. **Replicate independently** (Agent 10).
10. **Still to do:** results-stage adversarial review, then deliverables.

---

## 3. Research questions considered (Stage 1, `docs/01_candidate_questions.md`)

42 candidates in five groups:
* **A: inference.** Cross-model state injection (A1); depth correspondence (A2); acceptance burstiness in
  speculative decoding (A3); feature vs token drafting (A4); verification-cost bounds; adaptive
  verification; parallel speculation; prefill/decode attribution; non-prefix KV reuse; early-exit
  calibration; small-model-guided KV eviction; multi-token prediction horizons.
* **B: representations.** Similar outputs vs similar computation; similarity vs usefulness (B2); invariant
  states; copy-vs-recompute geometry; JEPA-style latent prediction; SAE feature transfer; transformer ↔ SSM
  transfer; anisotropy distorting similarity; emergence over training (B10).
* **C: memory.** Weights vs context vs retrieval; retrieval vs recomputation; consolidation; contradictory
  memories; forgetting; KV compression loss; CLS analogy.
* **D: reasoning.** Read vs recompute (D1) and error propagation (D2) were **excluded** because they
  duplicate the user's own repos. Also: pre-error signals, test-time compute, knowledge vs computation
  uncertainty, and others.
* **E: architectures.** Diffusion LMs, SSMs, MoE, predictive coding, engram storage, hippocampal indexing.

**Ranking (Stage 4, `docs/04_ranking.md`).** The top three were:
* X1 cross-scale injection: score 7.75
* X3 acceptance heterogeneity: 6.85
* X2 emergence over training: 6.80

H3 (adaptive compute) was **deliberately deprioritised**: its literature is dense, and a CPU-scale test
would be incremental. That is a scoping decision, not a refutation.

---

## 4. Why X1: the contradiction in the literature

| Paper | Setting | Verdict |
|---|---|---|
| arXiv 2608.09521 | Cross-family, similar sizes, depth 0.5, trained adapters | Mid-depth injection "works" (72–88% next-token agreement) |
| arXiv 2606.03280 | Pythia-160M L8 → 410M L16, linear translator | "Destructive" on multi-hop QA |
| arXiv 2603.18908 | Cross-family linear maps | Work only in the last 1–2 layers |
| Chen, Merullo, Stolfo, Pavlick 2025 (2506.06609) | Pythia-70m L3 → 160m L4, MSE maps | CE 3.99 vs 3.14 (closest prior work) |

Each paper changes several factors at once: depth, size ratio, map objective and metric. Our design crosses
them in one controlled family. Novelty class: **N2–N3**. The design and the comparator are new; stitching is
not.

---

## 5. Theory (`docs/03_theory.md`) in plain words

* **Prop 1 (no information bottleneck).** A transformer's states over a prefix determine the prefix, so in
  principle *some* function maps the small model's states to the big model's output exactly. Any failure we
  see is about what an **affine map** plus the big model's layers can compute, not about missing
  information. That is why the map class is fixed and stated.
* **Prop 2 (the H1 signature).** Let G(k) be the best achievable KL when injecting at depth k. If G has an
  **interior minimum below G(L)**, where G(L) is a plain linear read-out through the big model's head, then
  the big model's upper layers do real work on the small model's state. That is H1 in a falsifiable form.
  If the minimum is at L, the small model's state is no more useful to the upper layers than to a linear
  head.
* **Prop 3 (speculative decoding).** One-token acceptance equals 1 − TV(p, q). Exact verification guarantees
  the output distribution whatever the drafter is, so H2's "guarantees" part is automatic and **only
  efficiency is open**.

---

## 6. Experiment E1: design (`docs/05_preregistration_E1.md`)

**The mechanism**
1. Feed text to the small model S and take its final LayerNorm output at every position.
2. Map it through an affine map A into the 410m model's residual stream as the input to block k.
3. Run 410m's frozen blocks k..23, its final LayerNorm and its unembedding.
4. Compare the resulting distribution q_k with 410m's own p_T.

Position 0 (the BOS token) uses the target's own state. Injection is exact: slicing the layer list
reproduces normal logits with max diff 0.0.

**Factors**
* **Source** (size ratio relative to 410m):
  * 70m (≈ 0.17)
  * 160m (≈ 0.39)
  * 410m-deduped (1.0; different data)
  * 410m-seed1 (1.0; same data, different seed; added by amendment A2)
* **Depth:** k ∈ {6, 12, 18, 24}. k = 24 is the pure linear read-out through 410m's head.
* **Map objective:**
  * `mse`: ridge regression onto the target's residual.
  * `kl`: ridge initialisation, then a scale-aware affine correction trained for 200 Adam steps on
    KL(p_T‖q) through the frozen upper layers.

**Data**
* Fit on 512 Pile sequences (documents 0–4999 of pile-10k).
* Evaluate on 64 held-out Pile sequences (documents 5000–9999) and 64 WikiText-103 windows.
* All sequences are 128 tokens long. Metrics use positions 1..126.

**Outcomes**
* **Δ_k = KL(p_T‖p_S) − KL(p_T‖q_k).** Is the stitch closer to 410m than the small model alone? This is the
  practical drafting question. It was the frozen primary outcome.
* **D_k = KL(p_T‖q_24) − KL(p_T‖q_k).** Does injecting at k beat the linear read-out? This is the H1
  question. It was added as co-primary by amendment A1 **before any KL result existed**, because the
  reviewer showed that Δ_k cannot test H1.
* **Secondary:**
  * acceptance (1 − TV)
  * top-1 agreement
  * cross-entropy
  * WikiText versions of all metrics
  * held-out R² and CKA between the mapped state and the target residual
  * FLOPs

**Statistics**
* Bootstrap over evaluation sequences (10 000 resamples), stratified by seed.
* Holm correction across 12 tests, with unadjusted p-values also reported.
* Single-seed cells are labelled as such. Their CIs do **not** include map-fitting variance.

**Controls added by the design review (A1–A7) and later (A8)**

| Code | Control | Rival explanation it tests |
|---|---|---|
| A1 | D_k comparator, plus k = 24 maps trained to reproduce the *source's* distribution (`klsrc`) | Is the failure just the read-out? |
| A2 | 410m-seed1 → 410m (same data and size, different seed) | Is size ratio confounded with training data? |
| A3 | Identity stitch (no map) for equal-width pairs | Do sibling models share a coordinate system? |
| A4 | Step-0 loss logged; maps saved | Makes the divergence rule checkable |
| A5 | Convergence runs (600 steps, n_fit 1024) | Is the result an artefact of under-training? |
| A6 | Corrected FLOP accounting; self:2 FLOP-matched baseline | Is the H2 efficiency comparison fair? |
| A7 | Single-position replacement diagnostic | Per-token mismatch vs corrupted attention context |
| A8 (post-result, disclosed) | Seeds 1–2 at k = 18 and k = 24 | Seed robustness of the D_18 effect |

---

## 7. E1 results so far (seed 0; Pile eval; 95% CIs exclude map-fit variance)

### 7.1 Full KL table (lower is better: closer to 410m)

| Source → 410m | k = 6 | k = 12 | k = 18 | k = 24 | Source alone |
|---|---|---|---|---|---|
| 70m, kl map | 1.739 | 1.597 | **1.535** | 1.683 | **0.830** |
| 70m, mse map | 3.020 | 2.061 | 1.934 | 2.761 | 0.830 |
| 160m, kl | 1.456 | 1.196 | **1.033** | 1.130 | **0.474** |
| 160m, mse | 2.679 | 1.616 | 1.340 | 1.759 | 0.474 |
| 410m-deduped, kl | 1.090 | 0.873 | 0.710 | ⟨lost to OOM, re-queued⟩ | **0.311** |
| 410m-deduped, mse | 1.860 | 1.176 | 0.933 | 1.016 | 0.311 |
| 410m-seed1, kl | 1.184 | 0.969 | 0.810 | **0.793** | **0.275** |
| 410m-seed1, mse | 1.951 | 1.261 | 1.045 | 1.191 | 0.275 |

### 7.2 Finding 1: stitching never beats the small model alone (Δ_k < 0 everywhere)
* **Result.** All 15 Δ_k tests are negative, with every CI excluding 0 (p_Holm = 1.0 for "Δ > 0").
* **Size trend.** The gap shrinks as the source grows. Best KL by source: 1.535 (70m), 1.033 (160m),
  0.71–0.79 (410m siblings). Even so, an *equal-size* model is still about 2.5× further from 410m when
  stitched than when used on its own.
* **Preregistered verdicts:**
  * H-ratio prediction "70m: Δ < 0 at every k": **confirmed** (upper CI bound < 0 at every k).
  * H-ratio prediction "sibling: Δ > 0 at some k": **falsified**.
* **Meaning.** Under an affine map, a small model's state fed into a big model's upper layers makes a
  **worse drafter than the small model itself**. That is a negative result for the stitching route to H2.

### 7.3 Finding 2: the H1 signature appears for smaller sources only (D_k)

| Source | D_6 | D_12 | D_18 [95% CI] |
|---|---|---|---|
| 70m | −0.056 | +0.087 [0.028, 0.142] | **+0.149 [0.121, 0.175]** |
| 160m | −0.326 | −0.066 | **+0.096 [0.072, 0.120]** |
| 410m-seed1 | −0.392 | −0.176 | −0.018 [−0.044, 0.005] |

* **Result.** For 70m and 160m, injecting at depth 18 beats the linear read-out at 24. The big model's
  last 6 blocks add value to the small model's state beyond a linear read-out (Prop 2's signature).
* **Equal-size source.** For an equal-size, same-data model there is no such benefit: its best injection
  point is the read-out itself.
* **Tentative interpretation (exploratory).** A small model's final state looks like an
  *intermediate-depth* state of a bigger model, which the bigger model's last layers can still refine. A
  same-size model's final state is already "final-layer-like". This fits Prop 2's picture, but we have not
  tested a mechanism.
* **Independent replication (Agent 10).** It used different code, target 160m (12 layers), WikiText fit
  data and seeds 7 and 8.
  * D_9 = **+0.254 [0.196, 0.320]** on WikiText-val. Per-seed values were +0.240 and +0.268, and 99% of
    sequences had D_9 > 0.
  * On Pile, the median D_9 = +0.15. The mean is inflated by a few sequences where the k = 12 read-out is
    very bad.
  * k = 3 and 6 were **not** robust (their Pile medians are negative).
* **Pattern across both studies (exploratory, n = 2 targets).** The optimum sits at **3/4 depth** in both:
  18/24 here and 9/12 in the replication.
* **Caveats:**
  * Seed 0 only for the main study; the A8 seeds are pending.
  * The 410m-deduped k = 24 cell was lost and is re-queued.
  * With 3 equal-size points, "vanishes for equal size" rests on one pair so far.

### 7.4 Finding 3: there is a read-out bottleneck
* **Result.** A k = 24 map *trained to reproduce the source's own distribution* (410m-deduped) reaches only
  KL(p_S‖q) = 0.483. An affine map from the source's final features through 410m's head cannot express the
  source's own predictions.
* **Meaning.** A large part of "stitch worse than source" is a read-out limitation of the affine-plus-head
  pathway. That is the design reviewer's fatal objection, borne out in data.
* **Status.** The 70m and 160m calibration cells are re-queued; they were killed during the CPU stall.

### 7.5 Finding 4: representational similarity points to the wrong layer

| Source | argmax CKA | argmax R² | argmin KL (kl maps) |
|---|---|---|---|
| 70m | 24 | 24 | **18** |
| 160m | 24 | 24 | **18** |
| 410m-seed1 | 24 | 24 | 24 |

* **Result.** CKA and R² always peak at the top layer. Function peaks at 18 for the smaller sources.
* **Non-monotone CKA.** CKA dips at k = 18 (for example 70m: 0.245, 0.312, 0.202, 0.329), exactly where
  function is best.
* **Verdict.** H-dissociation is **supported descriptively** (2 of 3 pairs), as preregistered.
  Similarity metrics would have sent you to the wrong injection depth.

### 7.6 Finding 5: the map objective matters, by about 1.3×
* **Result.** At k = 12, KL maps improve on MSE maps by 1.29–1.35× for every pair.
* **Verdict.** This misses the preregistered 1.5× threshold, so H-objective is **not supported** as stated.
  It is still large and consistent.
* **Bearing on the contradiction.** The objective explains part of the works/fails split in the
  literature, but not all of it.

### 7.7 Finding 6: models do not share coordinates
* **Result.** The identity stitch, 410m-deduped → 410m at k = 12 with no map, gives KL 3.52. That is far
  worse than any trained map, with R² = −36.
* **Meaning.** A sibling's raw residual stream is not interchangeable with the target's, so a learned
  rotation is essential.
* **Status.** The seed1 identity cells are pending.

### 7.8 Robustness: WikiText
Every pattern above repeats on WikiText-103: stitch worse than source, the same ordering by depth and the
same objective effect. For example, 70m kl gives 2.01 / 1.89 / 1.83 / 1.94 across k = 6 / 12 / 18 / 24,
against 1.12 for the source.

---

## 8. Experiment X3: speculative decoding (`docs/07_preregistration_X3.md`, `docs/08_results_X3.md`)

**Question.** The textbook formula E[tokens per target call] = (1 − α^{γ+1}) / (1 − α) assumes acceptances
are independent. How wrong is it for a real 70m drafter verifying against 410m? Does any error come from
**path shift** (generated text is easier or harder than dataset text) or from **dependence** (bursty
acceptances)?

**Setup.** We ran real speculative sampling with KV caches and exact rejection sampling at temperature 1.
There were 48 prompts × 96 new tokens, at γ = 2, 4, 8.

**Result: negative.** The formula, using teacher-forced α = 0.624, over-predicts by +0.6%, +4.6% and +6.1%.
* The large-error hypothesis (> 10%) is **not supported**.
* The dependence error is ≤ 2% and not significant.
* The small over-prediction comes from acceptance on the sampled path (0.59–0.61) being lower than
  teacher-forced acceptance.

**Disclosed flaw in our own prereg.** It claimed our on-path α estimate was unbiased. It is not quite
unbiased, because step starts are selected positions. The path/dependence split is therefore approximate.

---

## 9. What went wrong, and how it was handled (honesty log)
* **Missing notebook.** The research notebook the brief mentions was not found. We proceeded from H1–H3 as
  written (decision #2).
* **Unreachable sources.** The network initially blocked HuggingFace and arXiv. We created a dedicated
  environment.
* **Pilot failures.** An MSE-only pilot motivated the KL objective. A naive parametrisation diverged and was
  fixed by a scale-aware one.
* **WikiText loader.** It crashed on 61 < 64 articles. Deviation D1 (2 windows per article) was decided
  before any confirmatory result.
* **Fatal design flaw caught by review** before results existed. Amendments A1–A7 followed.
* **Container restart** killed the queue. The queue is resumable, so it was relaunched.
* **Out-of-memory kill.** Running the replication concurrently lost one cell (deduped k24 kl). It is
  re-queued.
* **CPU-oversubscription stall** (deviation D4). One cell ran for 2 h. Stack sampling found the cause, and
  we switched to 3 threads while sharing the cores.
* **Post-result amendment A8** (extra seeds at k = 18). It is clearly labelled post hoc.

---

## 10. Novelty: what is new and what is not

| Claim | Status now | Closest prior work | Novelty |
|---|---|---|---|
| Stitching a small model into a larger one works partially (CE degrades) | Reproduction | 2506.06609 | N0–N1 |
| The interior-depth optimum beats the linear read-out for smaller sources, and the effect disappears for an equal-size source | Interim, single seed + independent replication on another target | None found that uses the D_k comparator or a size factor | **N2–N3 (candidate)** |
| The optimum sits at about 3/4 depth in two targets | Exploratory (n = 2) | — | Not claimable yet |
| An affine read-out cannot reproduce the source's own distribution | Interim, one pair | Implicit in logit-lens/tuned-lens work | N1–N2 |
| CKA/R² argmax ≠ functional argmax | Descriptive, 2 of 3 pairs | Bansal et al. 2021 (2106.07682): stitching reveals what CKA cannot; NinaXander 2609.38261 (same-size CKA/R² + switch-layer sweep) | N1–N2 (new in this setting) |
| KL-trained maps beat MSE by about 1.3× | Descriptive | Stitching literature uses task losses | N1 |
| The i.i.d. speculative-decoding formula is accurate within 6% for Pythia | Negative | SpecDec++ 2405.19715; 2608.30427 | N1 |

---

## 11. What remains (about 47 cells, about 11 h CPU at present speed)
1. **Same-size controls and baselines:**
   * seed1 identity stitches
   * self-prefix baselines: the 410m model's own layer-1 and layer-2 states as "source", for the FLOP-fair
     H2 comparison
   * self-0 baselines
2. **Diagnostics and re-runs:**
   * A7 single-position diagnostic
   * the 3 re-queued cells (70m/160m `klsrc`, deduped k24 kl)
3. **Extra seeds:**
   * seeds 1–2 for k = 12 and 24 (frozen)
   * A8: seeds 1–2 at k = 18. This is the key robustness test for Finding 2.
4. **Convergence runs:** 600 steps, n_fit 1024. Is the "worse than source" gap under-training?
5. **The 1b arm** (8 cells, about 4.5 h). The prereg allows dropping it first.
6. **After the queue:**
   * final statistics
   * results-stage adversarial review (a new independent agent)
   * deliverables: report, evidence table, manuscript and venue, a 4–6-page PDF, and the decision
     (DISCOVERY ESTABLISHED / PRELIMINARY / NO NOVEL / INCONCLUSIVE)

**Current honest reading.** If the A8 seeds hold, Finding 2 is the programme's candidate contribution. That
is: "a smaller model's final state is best consumed at an interior depth of a larger model's upper stack,
beyond a linear read-out, and this advantage disappears at equal size". Given its scale (≤ 410m, CPU, one
family) it would most likely be a **PRELIMINARY FINDING** suited to a workshop. Do not read it as an
established discovery yet.

## 12. Where to look

| You want | File |
|---|---|
| Every decision, in order | `docs/00_decision_log.md` |
| Candidates / literature / theory / ranking | `docs/01`–`04` |
| Frozen design + all amendments | `docs/05_preregistration_E1.md` |
| The design attack | `docs/06_adversarial_review_design.md` |
| X3 | `docs/07`, `docs/08` |
| Draft paper-style report | `docs/09_main_report.md` |
| Live E1 tables | `results/E1_tables.md` (regenerate: `python3 xscale/analyse_E1.py`) |
| Raw per-cell data | `results/E1/*.json` |
| Replication | `replication/REPORT.md` |

---

## 13. FINAL results (supersedes sections 7 and 11)

**What ran in the end:**
* 78 E1 cells, the single-position diagnostic, X3 and the separate replication.
* The 1b arm was cut under the prereg budget rule (decision #24). Each 1b cell took about 1 h, so only
  160m→1b at k = 4, 8, 16 ran.
* After the review, a preregistered convergence check R1 (`docs/11_preregistration_R1.md`): 600-step maps at
  k = 18 and 24 for 70m and 160m.

**13.1 Final KL table** (KL-trained maps, Pile, 200 steps, mean over seeds):

| source | k=6 | k=12 | k=18 | k=24 | source alone |
|---|---|---|---|---|---|
| 70m | 1.739 | 1.587 | **1.527** | 1.663 | 0.847 |
| 160m | 1.456 | 1.199 | **1.044** | 1.116 | 0.486 |
| 410m-deduped | 1.090 | 0.877 | 0.717 | **0.689** | 0.319 |
| 410m-seed1 | 1.184 | 0.969 | 0.810 | **0.793** | 0.275 |

**13.2 The main result, D_18** (depth 18 vs linear read-out). The seed-level CI includes map-fit variance.

| source | seed-0 (prereg) | 3 seeds, seed-level CI | WikiText | 600-step maps |
|---|---|---|---|---|
| 70m | +0.149 | **+0.136 [0.074, 0.198]** | +0.111 [0.062, 0.160] | **+0.121 [0.097, 0.144]** |
| 160m | +0.096 | +0.072 [0.015, 0.129] | +0.038 [−0.016, 0.091] | +0.071 [0.051, 0.090] (WikiText +0.041 [0.024, 0.058]), robust |
| 410m-deduped | −0.028 | −0.028 | −0.081 | — |
| 410m-seed1 | −0.018 | 1 seed | −0.065 | — |

**What changed from the interim reading:**
* **R1, the training budget.** Longer training shrinks 70m's D_18 by about 20% but does not remove it. Both depths
  improved, so the comparison stayed balanced.
* **160m is weaker than it looked.** It is significant on Pile only once seed variance is counted.
* **Mechanism wording narrowed.** We no longer say the upper blocks "use the small model's state". The honest
  statement is: *for much-smaller sources, the target's last quarter is a better read-out than its head; for
  equal-size sources it is not*. Why the narrowing: T's own layer-1 state shows the same pattern even more
  strongly, so generic extra capacity is a live explanation. The next experiment tests this (D8 #1).
* **Context-corruption claim withdrawn.** The "≈ 40% context corruption" decomposition was invalid (review R10).
* **FLOP statement corrected.** 70m costs about 1.5 target blocks, between self:1 and self:2.
  * self:1 beats the 70m stitch at k = 6 (+0.84).
  * They tie at k = 12.
  * 70m is better at k ≥ 18.
* **The objective ratio depends on the budget.** It is 1.30–1.35× at 200 steps but 1.49–1.62× at 600 steps.
* **Second target (1b, single seed).** {{1B}}

**13.3 Decision: PRELIMINARY FINDING.** It is robust and replicated within one family and an affine map class.
The mechanism is unresolved, and the practical drafting result is negative. Recommended venue: a workshop. No
submission has been made. Next three experiments:
1. a capacity-matched read-out control;
2. cross-family and absolute-size replication;
3. training-dynamics emergence.

Details are in `docs/12_final_deliverables.md` (D8).

**13.4 Final file map:**

| You want | File |
|---|---|
| Final report (18 sections) | `docs/09_main_report.md` |
| D1/D2/D4/D5/D6/D8 | `docs/12_final_deliverables.md` |
| 4-page executive PDF | `report/executive_summary.pdf` |
| Results-stage review | `docs/10_adversarial_review_results.md` |
| R1 preregistration | `docs/11_preregistration_R1.md` |
| Figures | `figures/fig1–4*.png` (`python3 xscale/figures_E1.py`) |
