# Preregistration — E1: When can a language model's upper layers use another model's state?

Status: **DRAFT** — to be frozen (commit message "FREEZE E1 prereg") before any confirmatory cell is run. Pilot data
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
  * kl: KL to p_T through the frozen upper blocks, 300 steps
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
