# Main report (D3)

**Status:** final. All numbers come from `results/E1_tables.md`, `results/E1_summary.json`, `results/X3_summary.json`
and `replication/REPORT.md`. Single-seed results are labelled as such. Post-hoc results (A8, R1) are labelled as such.

## 1. Title
**Where a smaller model's state is usable inside a larger model.** Injection depth, size ratio and fitting
objective in cross-scale stitching of Pythia models.

## 2. Abstract
**Setup.** We map the final hidden state of a source language model S affinely into the residual stream of a
frozen target T = Pythia-410m at depth k, then run T's remaining blocks. The sources are Pythia-70m, Pythia-160m
and two independently trained 410m models. This tests a version of the hypothesis that a small model can
supply representations a larger model can use.

**Comparators.** We compare each stitch with two references:
* the same source read out linearly through T's head (k = L). The difference is D_k.
* the source model's own predictions. The difference is Δ_k, which corresponds to drafting.

**Findings:**
* **Interior depth beats the read-out for small sources.** For 70m and 160m, injecting at depth 18 of 24 beats
  the linear read-out. The fixed 200-step budget was used, with three seeds; the third-seed cells were added
  post hoc.
  * 70m: D_18 = +0.136 nats/token, seed-level 95% CI [0.074, 0.198].
  * 160m: D_18 = +0.072, CI [0.015, 0.129].
  * For 70m the effect survives maps trained 3× longer (D_18 = +0.121 [0.097, 0.144], seed 0). For 160m, the
    600-step value is +0.071 [0.051, 0.090] (WikiText +0.041 [0.024, 0.058]), robust.
  * An independent re-implementation reproduces the effect for 70m→160m, at 3/4 depth.
* **Equal-size models never benefit.** Two equal-size siblings show no interior depth with D_k > 0.
* **No stitch beats the source alone.** Every stitch is a worse approximation of T than the source model alone
  (Δ_k < 0 in all 16 tests). So these stitches are not useful drafters, and the preregistered prediction that an
  equal-size sibling would beat its own source is falsified.
* **Training on the downstream KL helps, but only modestly.** It improves on ridge regression by 1.30–1.35× at
  200 steps and by 1.49–1.62× at 600 steps.
* **Similarity does not track function.** Representational similarity (CKA, R²) peaks at the read-out depth for
  every pair. The functional optimum for small sources is interior.
* **The target's own early layers are better.** T's own first one or two layers beat the 70m stitch at early
  depths at comparable cost.
* **Speculative sampling (secondary study X3).** With 70m drafting for 410m, the textbook i.i.d. acceptance
  formula over-predicts realised throughput by only 0.6–6%.

**Verdict.** We report a **preliminary finding**. It is a robust, replicated depth effect for small sources, with
no practical speed-up.

## 3. Scientific background
* **Starting hypotheses.** The programme began from three hypotheses:
  * H1: a small model can predict representations of a larger model that the larger model can use.
  * H2: latent-space prediction can accelerate inference while keeping the target's output guarantees.
  * H3: adaptive computation improves the reliability/latency/cost trade-off.
* **Model stitching** operationalises "usable representation". An affine map feeds one network's activations
  into another network's later layers, and the composite is evaluated (Bansal et al. 2021, arXiv 2106.07682;
  Chen et al. 2025, arXiv 2506.06609).
* **Speculative decoding** with exact rejection sampling preserves the target distribution for any drafter
  (Leviathan et al. 2023; Chen et al. 2023). So the "guarantee" part of H2 holds by construction
  (`03_theory.md`, Prop. 3), and only efficiency is open.
* **Representational similarity.** CKA (Kornblith et al. 2019) and linear-probe R² are widely used as proxies for
  shared function. Whether similarity implies interchangeability is contested.

## 4. Precise research question
* **The question.** For Pythia models sharing a tokenizer and training-data order: when does affinely mapping S's
  final-LayerNorm state into T's residual stream at depth k, then running T's frozen blocks k..L, give a
  distribution q_k closer to p_T than these two references?
  1. **The linear read-out q_L.** This is the H1 test, D_k = KL(p_T‖q_L) − KL(p_T‖q_k).
  2. **S's own distribution p_S.** This is the drafting test, Δ_k = KL(p_T‖p_S) − KL(p_T‖q_k).
* **Factors varied:**
  * size ratio (0.17, 0.39, 1.0)
  * depth (k = 6, 12, 18, 24)
  * fitting objective (ridge/MSE vs KL)
* **Also asked:** does representational similarity locate the functional optimum?

## 5. Related work
The full matrix is in `02_literature_matrix.md` (about 60 papers retrieved in-session). The closest works are:
* **Chen, Merullo, Stolfo, Pavlick 2025 (2506.06609).** Pythia-70m L3 → 160m L4 with MSE maps gives CE 3.99 vs
  3.14. They use a single depth and objective.
* **2608.09521.** Mid-depth cross-family injection into a frozen back model "works" (72–88% next-token agreement)
  with trained adapters.
* **2606.03280.** Pythia-160m L8 → 410m L16 replacement through a linear translator is destructive on multi-hop QA.
* **2603.18908.** Cross-family linear maps work only in the last 1–2 layers.
* **Speculative decoding with hidden-state drafters.** Tandem Transformers, EAGLE-1/2/3 (2503.01840) and HASS
  train drafters on target features. These are not frozen cross-scale stitches.
* **PolyPythias (2503.09543)** supplies the seed-varied 410m sibling.

## 6. Research gap
* **The contradiction.** The 2026 papers contradict each other on whether injected cross-model states are usable
  at mid-depth.
* **Why it is unresolved.** Each paper changes several factors at once. None separates "the source lacks
  information" from "an affine map cannot express it". None uses a comparator that isolates what the upper layers
  contribute.
* **Our design.** A controlled factorial in one family, using the read-out comparator D_k. Novelty audit: N2–N3,
  meaning a new design and an incremental finding.
* **What we do not claim.** We do not claim that stitching, KL-trained maps, or CKA/R² dissociation in general
  are new.

## 7. Hypotheses
These come from the frozen preregistration `05_preregistration_E1.md` plus amendments A1–A7 (made before any
result) and A8 (post hoc), and from `11_preregistration_R1.md`.
* **H-ratio (frozen primary).** max_k Δ_k increases with size ratio. Prediction: Δ < 0 at all k for 70m, and
  Δ > 0 at some k for the sibling.
* **D_k (A1, co-primary for H1).** For some k < L, D_k > 0 with a CI excluding 0.
* **H-objective (descriptive).** The kl/mse KL ratio is > 1.5 at k = 12.
* **H-dissociation (descriptive).** argmax CKA/R² ≠ argmin KL in ≥ 2 of 3 pairs.
* **H-self (H2 efficiency).** self:1 beats the 70m stitch at k ≤ 12.
* **R1 (post-review).** D_18 stays > 0 at 600 steps with n_fit = 1024.
* **Competing explanations, each with a planned control:**

| Label | Competing explanation | Control |
|---|---|---|
| C-info | the source lacks the information (excluded a priori by Prop. 1) | — |
| C-readout | the read-out cannot express p_S | A1 calibration |
| C-data | a training-data effect | A2: seed sibling vs data sibling |
| C-init | shared coordinates from a shared initialisation | A3: identity stitches |
| C-context | attention-context corruption | A7: single-position diagnostic |
| C-undertrain | maps are under-trained | convergence cells and R1 |

## 8. Methodology
* **Exact injection.** T's ModuleList is sliced, and states are passed as inputs_embeds. Re-injecting T's own
  states reproduces its logits with max |diff| = 0.0 (`xscale/test_injection.py`).
* **Maps:**
  * mse: ridge onto R_k.
  * kl: ridge initialisation plus a scale-aware affine correction trained on KL(p_T‖q) through T's frozen upper
    blocks (Adam lr 3e-3, cosine, batch 8 × 128, n_fit = 512, 200 steps).
  * klsrc: as kl, but trained to reproduce p_S.
  * id: no map.
  * Position 0 (BOS) copies T's state.
* **Metrics** over positions 1..126: KL(p_T‖q), 1 − TV (one-token speculative acceptance), top-1 agreement, CE,
  and held-out R² and linear CKA (from mse cells).
* **Statistics:**
  * The unit is the evaluation sequence (64 per set). Sequences are paired across cells; eval-set hashes match.
  * Intervals use a seed-stratified bootstrap (10 000 resamples) with Holm correction. Following the review
    (R3), a **seed-level t interval** (n = 3 seeds) is also reported, because it includes map-fit variance.
* **Validity guards:**
  * divergence rule (step-0 loss logged)
  * disjoint Pile fit and eval document pools
  * WikiText-103 as a domain-shift check

## 9. Experimental setup
* **Models.** EleutherAI Pythia 70m, 160m, 410m (target), 410m-deduped, 410m-seed1 (PolyPythias), and 1b
  (second target, reduced arm).
* **Hardware.** 4 CPU cores and 15 GB RAM, float32, no GPU.
* **Data.** NeelNanda/pile-10k (fit docs 0–4999, eval docs 5000–9999) and the WikiText-103 test split.
* **Cells.** 79 E1 cells, plus the single-position diagnostic, X3, and the separate replication.
* **Deviations,** all in `00_decision_log.md`:
  * D1: WikiText windows.
  * D3: reordering.
  * D4: thread count (an oversubscription stall).
  * Container restart (#23).
  * D5: R1 before the last 1b cell.
* **Budget cut (#24, under the prereg rule).** The 1b arm was reduced to 160m→1b at k = 4, 8, 16. The 410m→1b
  arm and 160m→1b k = 12 were dropped. Cost was about 1 h per 1b cell.

## 10. Results
**Fig. 1** (`figures/fig1_kl_by_depth.png`) shows stitched KL by depth. **Fig. 2** (`figures/fig2_dk.png`) shows D_k.

**Stitched KL(p_T‖q_k), kl maps, Pile, 200 steps.** The seeds used are shown in brackets.

| source | k = 6 | k = 12 | k = 18 | k = 24 | source alone |
|---|---|---|---|---|---|
| 70m | 1.739 [0] | 1.587 [0–2] | 1.527 [0–2] | 1.663 [0–2] | 0.847 |
| 160m | 1.456 [0] | 1.199 [0–2] | 1.044 [0–2] | 1.116 [0–2] | 0.486 |
| 410m-deduped | 1.090 [0] | 0.877 [0–2] | 0.717 [0–2] | 0.689 [0–2] | 0.319 |
| 410m-seed1 | 1.184 [0] | 0.969 [0] | 0.810 [0] | 0.793 [0] | 0.275 |

* **Result 1, H1 co-primary (D_k).** The preregistered seed-0 test, the 3-seed estimate and the WikiText value
  are shown below. The 3-seed estimate includes post-hoc A8 seeds at k = 18.

| source | k | seed-0 D_k [bootstrap CI] | 3-seed D_k [seed-level t CI] | WikiText D_k [seed-level t CI] |
|---|---|---|---|---|
| 70m | 12 | +0.087 [0.029, 0.142] | +0.076 [0.010, 0.143] | +0.030 [−0.027, 0.088] |
| 70m | 18 | **+0.149** [0.120, 0.176] | **+0.136** [0.074, 0.198] | **+0.111** [0.062, 0.160] |
| 160m | 12 | −0.066 | −0.083 [−0.118, −0.048] | −0.170 |
| 160m | 18 | **+0.096** [0.072, 0.121] | **+0.072** [0.015, 0.129] | +0.038 [−0.016, 0.091] |
| 410m-deduped | 18 | −0.028 [−0.051, −0.007] | −0.028 [−0.034, −0.023] | −0.081 |
| 410m-seed1 | 18 | −0.018 [−0.045, 0.006] | single seed | −0.065 |

  At k = 6, D_k < 0 for every source.
* **Result 2, R1 convergence check (preregistered after the review).** These use 600 steps, n_fit = 1024 and
  seed 0.
  * 70m: KL at k = 18 is 1.349, and at k = 24 it is 1.469. So D_18 = **+0.121** [0.097, 0.144] (91% of sequences
    > 0), and on WikiText +0.086 [0.063, 0.109]. Seed 0 at 200 steps was +0.149, so the effect shrinks by about
    20% but remains. **Robust under the preregistered rule.**
  * 70m D_12 at 600 steps: +0.091 [0.034, 0.142], WikiText +0.026 [−0.013, 0.065].
  * 160m: KL at k = 24 is 0.972, and at k = 18 it is 0.901, giving D_18 = +0.071 [0.051, 0.090] (WikiText +0.041 [0.024, 0.058]), robust.
* **Result 3, H-ratio (frozen primary).** Δ_k < 0 for every source and every k; all 16 upper CI bounds are < 0.
  * The 70m prediction "Δ < 0 at all k" is **confirmed**.
  * The sibling prediction "Δ > 0" is **falsified**: the best sibling value is Δ = −0.370 at k = 24.
  * The ordering by size ratio does hold for max_k Δ_k (70m −0.680; 160m −0.558; deduped −0.370). But no pair
    reaches Δ > 0.
* **Result 4, second target (1b, L = 16, 160m source, seed 0, reduced arm).**
  * KL at k = 4 is 1.544 and at k = 8 it is 1.270; the source alone is 0.560.
  * D_k against k = 16: inconclusive. Single seed, 160m→1b (size ratio 0.16): D_4 = −0.266 [−0.351, −0.187], D_8 = +0.008 [−0.053, 0.066] (no benefit at 1/4 and 1/2 depth, as in the 410m target at those relative depths); the 3/4-depth cell (k = 12), where the effect appeared in 410m, was dropped in the budget cut, so the decisive depth is untested.
* **Result 5, independent replication** (`replication/REPORT.md`). Separate code, 70m→160m, WikiText fit, seeds 7–8:
  * D_9 = +0.254 [0.196, 0.320] on WikiText-val, positive on 99% of sequences; Pile median +0.15.
  * k = 3 and k = 6 are eval-set dependent.
  * Δ < 0 at every k.

## 11. Statistical analysis
* **Holm correction.** Over the 12 D_k tests (4 sources × 3 depths), the Holm-corrected one-sided p-values for
  D_18 (70m, 160m) and D_12 (70m) are ≤ 0.0012 under the sequence bootstrap (raw p = 0.0001, the bootstrap floor).
* **The seed-level t intervals (n = 3) are the honest intervals.** They are about 3× wider:
  * 160m D_18 keeps a CI above zero on Pile but not on WikiText.
  * 70m D_12 loses significance on WikiText.
  * Only 70m D_18 has a CI excluding zero on both eval sets.
* **No best-seed reporting.** Seed means are reported in `E1_tables.md`. 70m D_18 per seed: +0.149, +0.107, +0.152.
* **Labelling.** The A8 seeds (k = 18, all pairs; k = 24, 160m) are post hoc. The preregistered seed-0 test passes
  on its own.

## 12. Ablations
* **Objective (H-objective).**
  * kl/mse ratio at k = 12 at 200 steps: 1.30 (70m), 1.35 (160m), 1.34 (deduped), 1.30 (seed1). The 1.5 threshold
    is **not met**.
  * At 600 steps: 1.49 (70m) and 1.62 (deduped). So the 200-step ratio is a lower bound (review R7).
  * With ridge/MSE maps the optimum is k = 18 for **every** pair, siblings included (Fig. 1, right). Only KL
    training moves the siblings' optimum to the read-out (k = 24). So the sign of D_k for the siblings depends on
    the objective, while for 70m and 160m D_18 > 0 under both objectives.
* **Read-out calibration (A1).** A k = 24 map trained to reproduce p_S still has KL(p_S‖q) = 0.890 (70m), 0.711
  (160m) and 0.483 (deduped).
  * So T's head plus an affine map cannot express the source's own distribution. This is a read-out bottleneck,
    and it explains part of the gap behind Δ < 0.
  * It also shows that the k = 24 maps trained to p_T are not much better than the klsrc maps (1.683 vs 1.674 for
    70m, seed 0). That is one reason the review suspected under-training (R1).
* **Identity stitches (A3, no map; exploratory, one cell each).**
  * deduped→410m: KL 3.52 at k = 12 and 4.48 at k = 24.
  * seed1→410m: 9.50 and 10.90.
  * Neither sibling shares usable coordinates. The roughly 3× advantage of the deduped sibling is consistent with
    a shared initialisation, which we have not verified.
* **Self-prefix (H-self).** Paired seed-0 comparison against the 70m stitch:
  * self:1 at k = 6: 0.902 vs 1.739, an advantage of +0.84 [0.77, 0.92].
  * self:1 at k = 12: 1.557 vs 1.587, +0.04 [−0.02, 0.09], a **tie**.
  * self:2 at k = 6 and k = 12: 0.686 and 1.328.
  * self:0 (embeddings only, kl) at k = 6: 1.254.
  * At k ≥ 18 the 70m stitch beats both self baselines.
  * FLOPs: 70m's six blocks cost about 1.52 target blocks, between self:1 and self:2. A6's statement that "self:2
    is FLOP-matched" was wrong (review R9). The total per-token cost differs by < 2% because T's head and upper
    blocks dominate.
  * Prediction "self:1 < 70m at k ≤ 12": confirmed at k = 6, a tie at k = 12.
* **Single-position diagnostic (A7, 8 sequences, k = 12, seed 0, no CI).** Replacing one position at a time, with
  T's own states elsewhere, lowers KL to:
  * 1.00 (70m), from 1.70 with all positions replaced
  * 0.85 (160m), from 1.32
  * 0.59 (deduped), from 0.98
  * 0.68 (seed1), from 1.04

  A substantial per-token mismatch remains. We **withdraw** the earlier "≈40% context corruption" decomposition
  (review R10): the replaced position still reads correct context, so the two numbers do not decompose additively.
* **Convergence (C-undertrain).** 600 steps with n_fit = 1024 lowers KL by 13–17%:
  * 70m, k = 12: 1.587 → 1.379
  * deduped, k = 12: 0.877 → 0.728
  * 70m, k = 24: 1.663 → 1.469

  Steps and fit data changed together (review R8). All kl conclusions carry this caveat.

## 13. Competing explanations
* **C-info (the source lacks information).** Excluded by construction: Prop. 1 (injectivity). The failures are
  computational or representational, not informational.
* **C-readout.** Partly true: the A1 calibration shows a read-out bottleneck. This is why D_k, not Δ_k, is the H1
  test.
* **C-data vs size.** The seed sibling (same data) and the data sibling (deduped) behave the same: no interior
  benefit, read-out best. So the sign change of D_k tracks **size ratio**, not training data. Caveat: only two
  equal-size pairs exist.
* **C-init.** Possibly relevant to raw coordinates (A3). It is irrelevant once a map is fit: with trained maps
  the deduped and seed1 siblings differ by about 0.1 nats at every k (0.09–0.10).
* **C-undertrain / optimisation artefact (review R1).** This was the strongest alternative for D_18 > 0.
  * Tripling the budget shrinks 70m's D_18 by about 20% but leaves it clearly positive.
  * The k = 24 map also improves (1.663 → 1.469), so the comparison stayed balanced.
  * Not tested: 1 500-step maps, an lr sweep, and L-BFGS at k = 24.
* **Generic extra capacity (review R5).** D_18 > 0 could simply reflect that six more frozen nonlinear blocks
  form a richer read-out than T's head, rather than anything specific about the small model's state. T's own
  layer-1 state shows the same pattern, more strongly (self:1 D_18 ≈ +0.97). The siblings show it not at all.
  * We therefore state the finding as: **"for sources much smaller than the target, the target's last quarter is
    a better read-out than its head; for equal-size sources it is not."**
  * We do not claim that the upper blocks "understand" the small model.

## 14. Adversarial review
* **Design-stage review** (`06_adversarial_review_design.md`): 1 fatal and 10 major issues. These led to
  amendments A1–A7, adopted before any result. The fatal issue was the comparator, which led to D_k.
* **Results-stage review** (`10_adversarial_review_results.md`, an independent agent): 15 issues, verdict
  **PRELIMINARY FINDING**. Actions:
  * R1: convergence check run (Result 2).
  * R3: seed-level CIs added.
  * R4: A8 labelled.
  * R5: mechanism wording narrowed.
  * R6: "siblings D ≤ 0" changed to "no k with D > 0".
  * R7: H-objective reported as budget-dependent.
  * R8: confound disclosed.
  * R9: FLOP statement corrected.
  * R10: decomposition withdrawn.
  * R11: CKA fragility noted.
  * R13: X3 sub-claim downgraded.
* **Not addressed (budget):** 1 500-step and lr-sweep maps, and more 1b seeds.

## 15. Independent replication
* **Who and how.** Agent 10 wrote new code in `replication/` without reading `xscale/` or `results/`. It used a
  different pair (70m→160m), fit data (WikiText), eval sets and seeds (7, 8).
* **Outcome.** C1 replicates robustly at k = 9 of 12. C2 replicates at all k.
* **Limits (review R2):**
  * The replication's maps were trained at a 30× smaller learning rate and barely moved from ridge, so it does not
    independently rule out R1.
  * Its Pile mean is tail-driven; the median is +0.15.
  * The "optimum at 3/4 depth in both studies" coincidence has a 1-in-3 chance on quarter-depth grids.

## 16. Limitations
* **Scale and family.** Small models (≤ 1b), one family, CPU only. Nothing here licenses claims about frontier
  models or cross-family transfer.
* **Map class.** Affine, per-position maps. All failures are relative to this class (Prop. 1).
* **Seeds.** Three seeds for the key cells, one seed elsewhere. The 1b arm and the R1 cells are single-seed.
* **Training budget.** 200 steps, which under-trains by about 15%. R1 covers 70m and 160m at k = 18 and 24 only.
* **Eval size.** 64 sequences × 126 positions per eval set.
* **Interpretation.** "Usable" is measured as distributional closeness. Downstream task accuracy was not measured.
* **X3.** One drafter pair, one temperature, single seed per γ.

## 17. Scientific implications
1. **Read the contradictory literature through size ratio and depth.** Mid-depth injection is not usable in the
   drafting sense for any pair here. Relative to a linear read-out, the target's last quarter adds value only when
   the source is much smaller. This is consistent with 2603.18908's "only late layers work", and adds that
   "late" means the last quarter, not the head.
2. **Similarity metrics mislocate the functional optimum.** CKA and R² are highest at the read-out depth for every
   pair, while the functional optimum for small sources is interior. Using CKA to choose where to stitch would
   pick the wrong layer.
3. **For latent drafting (H2), the target's own early blocks dominate a separate small model at early depths.**
   A frozen small-model state, affinely mapped, is a worse drafter than the small model itself. That is a negative
   result for "latent-space drafting without retraining".
4. **Speculative-sampling throughput.** The i.i.d. formula is accurate to within about 6% for a 70m/410m pair, so
   path-dependence corrections are a second-order concern at this scale.

## 18. Future research
* The next three experiments are listed in `12_final_deliverables.md` (D8).
* Beyond those: cross-family pairs with a learned tokenizer bridge; non-affine (MLP or attention) maps; and
  downstream-task evaluation of stitched models.
