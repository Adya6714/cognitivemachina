# Preregistration — E1: When can a language model's upper layers use another model's state?

Status: **FROZEN** (commit "FREEZE E1 prereg") before any confirmatory cell was run. Pilot data
(`logs/pilot_*`, 70m→410m, eval seed 0, ≤ 256 fit sequences) are exploratory and are **not** reused: confirmatory
cells use fit seeds 0–2 with n_fit = 1024 and eval sets drawn with seeds 100–102 from disjoint document pools.

## Background and the contradiction being tested
* **Works:** 2608.09521 reports that mid-depth cross-model injection into a frozen back model "works", with
  72–88% next-token agreement. That setting is cross-family, has similar sizes, uses depth 0.5 and trained
  adapters.
* **Fails:** 2606.03280 reports that Pythia-160M L8 → 410M L16 replacement injection through a linear
  translator is destructive on multi-hop QA. 2603.18908 reports that cross-family linear maps work only in
  the last 1–2 layers.
* **Chen et al. 2506.06609** stitch Pythia-70m L3 → 160m L4 using MSE maps and report CE 3.99 vs 3.14.
* **What differs:** the source/target size ratio, the depth, the map objective (MSE vs downstream) and
  the metric. No study crosses these factors.

## Factors
* **Pair (size ratio).** All pairs are Pythia, with a shared tokenizer.
  * 70m → 410m (ratio about 0.17)
  * 160m → 410m (about 0.39)
  * 410m-deduped → 410m (1.0; independently trained sibling on deduplicated data)
  * Second target family, replication arm: 160m → 1b; 410m → 1b
* **Injection depth k for T = 410m (L = 24):** {6, 12, 18, 24}. k = 24 means "linear read-out through the
  target's final LayerNorm and unembedding".
* **Map objective:**
  * mse: ridge onto R_k
  * kl: ridge init + scale-aware affine correction trained on KL to p_T through the frozen upper blocks
    (200 steps, Adam lr 3e-3 cosine, batch 8×128, n_fit = 512 sequences)
* **Self baselines (target's own prefix):**
  * self:1 → k with the kl objective, for each k
  * self:0 (embeddings only) → k

## Outcomes
* **Primary outcome:** Δ_k = KL(p_T‖p_S) − KL(p_T‖q_k), the per-sequence mean over predicted positions on
  the held-out Pile eval set. Positive values mean the stitched model is closer to the target than the
  source model alone is. Here q_k is the stitched distribution with the kl objective.
* **Secondary outcomes:**
  * acceptance 1−TV, which is the one-token speculative acceptance probability
  * top-1 agreement with T
  * CE on true next tokens
  * the same metrics on WikiText-103 (domain-shift check)
  * held-out R² and linear CKA between the source feature and R_k
  * FLOPs per token

## Hypotheses and predictions
* **H-ratio (primary).** max_k Δ_k increases with size ratio.
  * Prediction: max_k Δ_k < 0 for 70m→410m, and max_k Δ_k > 0 for 410m-deduped→410m.
  * Falsified if 70m→410m has some k with Δ_k > 0 (CI excluding 0), or if the sibling pair has Δ_k ≤ 0 at
    all k.
* **H-objective.** At mid depth (k = 12), the kl objective reduces KL(p_T‖q_k) relative to mse by a
  factor > 1.5 for every pair. This tests whether the objective explains the works/fails contradiction.
* **H-dissociation.** The representational optimum argmax_k CKA (and argmax_k R²) differs from the
  functional optimum argmin_k KL(p_T‖q_k, kl) in ≥ 2 of 3 pairs.
* **H-self (H2 efficiency).** At each k, compare the cross-model stitch with the self:1 stitch.
  * The self:1 stitch costs one target block. Every source here costs ≥ 1 target block at 410m scale
    (70m costs about 0.25 of a 410m block plus its head), so FLOP-matching is reported, not imposed.
  * Prediction: self:1 achieves lower KL than 70m→410m at k ≤ 12.

## Compute budget (fixed after pilots, before freeze)
* **Pilot cost:** 4.8 s/step at k = 12 for 410m, so a 200-step kl cell costs about 6–25 min depending on k.
* **Confirmatory cells, in run order:**
  1. **Core grid, seed 0:** 3 pairs × k ∈ {6, 12, 18, 24} × {mse, kl}.
  2. **Self baselines, seed 0:**
     * self:1 → k, kl
     * self:0 → k, mse and kl at k = 6
  3. **Seeds 1 and 2:** kl at k = 12 for all 3 pairs, plus kl at k = 24 for 70m→410m and the sibling.
  4. **Convergence check:** 70m→410m, k = 12, kl, 600 steps, n_fit = 1024, seed 0. This addresses
     whether "fails" reflects under-training. It is reported separately and does not replace the
     200-step cell in the primary test.
  5. **If budget remains:** the 1b replication arm (160m→1b, 410m→1b at k ∈ {4, 8, 12, 16}, kl, seed 0).
* **Primary-test scope and seed caveat:** the primary test Δ_k uses all available seeds for each cell.
  Seed-0-only cells are labelled single-seed, and their CIs reflect sequence-level sampling only.

## Statistics
* **Unit:** the evaluation sequence (64 sequences × 126 positions per eval set), with 3 fit/eval seeds.
* **Effects and intervals:** each effect is the mean over sequences pooled across seeds, with a 95% CI
  from a bootstrap over sequences (10 000 resamples) that is stratified by seed. Seed-level means are
  also reported.
* **Multiple comparisons:** Holm correction across the 3 pairs × 4 depths for the Δ_k > 0 tests.
* **Not a significance test:** H-dissociation is a descriptive comparison of argmax/argmin with
  seed-level agreement, not a significance test.
* **Primary metric:** fixed as Δ_k (KL). Any other metric is labelled secondary or exploratory.

## Exclusions and stopping
* **No exclusions:** no sequences are excluded post hoc.
* **Divergence:** a kl cell whose final train loss exceeds its step-0 loss is reported as "optimiser
  failure" and rerun once at lr/3. Both runs are reported.
* **Budget stop:** if the compute budget runs out, the 1b replication arm is dropped first, then seeds 1–2
  of the mse cells. Dropped cells are listed in the report.

---
## Amendments (post-freeze, **pre-result**), 2026-11-24, in response to the adversarial design review
These amendments were written after the freeze. When they were written, exactly one confirmatory cell
(`S70m_T410m_k6_mse_s0`) existed. It was not inspected beyond its one-line log, and no KL cell had finished.
All frozen tests are still reported exactly as frozen. The amendments add tests and controls; they do not
replace any frozen test.

* **A1 (review issue 1, fatal: comparator).**
  * **The problem:** Δ_k compares against the source's own distribution, but an affine map into the
    target's head may be unable to reproduce p_S at all. That is a read-out bottleneck, not a statement
    about upper-layer usefulness.
  * **New co-primary outcome for H1:** D_k = KL(p_T‖q_L) − KL(p_T‖q_k) for k < L, with both stitches
    trained with the kl objective. This is the theory's own comparator, G(L) − G(k), from
    `03_theory.md` Prop. 2. H1 is supported for a pair if some k < L has D_k > 0 with a 95% CI excluding 0.
  * **Δ_k is retained**, but relabelled as the *practical drafting* outcome: is the stitched model a
    better drafter than the source alone?
  * **Read-out calibration cells:** k = 24, with the map trained to reproduce p_S (`--train_to source`).
    They report KL(p_S‖q), which measures how much of the source's own distribution an affine map plus
    the target head can express.
* **A2 (issue 2: size ratio confounded with data).** Add PolyPythias `pythia-410m-seed1` → 410m. This
  pair has the same data and architecture and a different seed (arXiv 2503.09543). It is the
  equal-size control. The deduped sibling becomes a "same size, different data" condition.
* **A3 (issue 2).** Identity stitches (no training) for equal-width pairs at k ∈ {12, 24}. They test for
  shared coordinate systems, for example from a shared initialisation.
* **A4 (issue 4).** The pre-update (step-0) training loss is logged and maps are saved. This makes the
  divergence rule applicable.
* **A5 (issue 5).** A convergence check is added for the sibling as well (600 steps, n_fit = 1024). The
  under-training caveat is stated for every kl conclusion.
* **A6 (issue 11, FLOPs).** FLOP accounting is corrected:
  * The source head is excluded, because the stitch does not use it.
  * The prereg statement that "70m costs ≈ 0.25 target blocks" was wrong. 70m's six blocks cost ≈ 1.5
    blocks of 410m.
  * self:2 (two target blocks) is added as the FLOP-matched self baseline.
  * The FLOP field of the already-run mse cell is recomputed in analysis.
  * Pairs whose stitch costs more than the target (the siblings) are excluded from H2 claims.
* **A7 (issue 9).** A single-position diagnostic (`xscale/diag_single_pos.py`) replaces one position at a
  time, keeping the target's own states elsewhere. This separates per-token mismatch from
  attention-context corruption.
* **Statistics (issues 7, 8):**
  * H-dissociation is downgraded to *descriptive*. Representational metrics are taken from mse cells.
    CKA is map-free.
  * Unadjusted p-values are reported alongside Holm-adjusted ones.
  * Confirmation criterion for "70m: Δ_k < 0 at all k": the upper 95% CI bound is < 0 at every k.
  * Single-seed cells are labelled as such, and their CIs exclude map-fit variance.
* **H-objective (issue 6).** It is relabelled as a descriptive effect size: how much of the gap is
  attributable to the fitting objective. It is not a mechanistic test.
* **Prereg inconsistency (issue 3).** The background section says n_fit = 1024. The budget section and
  the queue use 512, and 512 is binding.
* **Deviation D3.** The run order is changed so that A1–A7 precede the extra seeds and the 1b arm.

* **A8 (POST-RESULT, 2026-11-25).** Added after seeing the seed-0 D_k table: seeds 1–2 for kl at k = 18 (all three pairs) and k = 24 (160m). These cells are labelled post hoc. The seed-0 D_k results remain the preregistered single-seed test.
