# Independent replication: cross-scale stitching, Pythia-70m → Pythia-160m (Agent 10)

**Bottom line.**
* **C1 (some interior k < L has D_k = KL_L − KL_k > 0): REPLICATES** in this new setting, most clearly at
  k = 9 of L = 12. At k = 9, D_k > 0 on both eval sets, with 2 fit seeds, by mean and by median, and on 96–99% of
  sequences. At k = 3 and k = 6 the result depends on the eval set and the summary statistic (details below).
* **C2 (every stitch is worse than the source alone): REPLICATES.** KL(p_T‖q_k) > KL(p_T‖p_S) at every k on
  both eval sets, and every 95% CI excludes 0.
* **Caveats:**
  * Only one pair was tested, and 2 of the 4 depths have a single fit seed.
  * The maps are under-trained: a 150-step budget, with training loss still falling.
  * The optional 1b arm was not run.

## Setup (separate implementation)
* **Code:** `replication/stitch_rep.py`, written from scratch with plain PyTorch 2.15 and transformers 5.24.
  * float32, CPU, `torch.set_num_threads(1)`, `nice -n 19`, cells run strictly sequentially.
  * Nothing under `xscale/` or `results/` was read or imported. Only `docs/05_preregistration_E1.md` was read,
    to understand the claim.
* **Models:** source S = EleutherAI/pythia-70m (d = 512); target T = EleutherAI/pythia-160m (L = 12, d = 768).
* **Source feature h_S:** S's final-LayerNorm output. The code asserts that `S.unembed(h_S)` equals S's logits.
* **Injection:** a forward pre-hook (with kwargs) on T's block k, or on T's final LayerNorm when k = L = 12.
  The hook replaces the `hidden_states` input with `[R_k^T(pos 0) ; A h_S(pos 1..127) + b]`.
  * Position 0 (BOS, token 0) keeps T's own state. That state is identical for every sequence, and the
    code asserts this.
  * T's blocks k..11, final LN and unembedding are frozen and run as usual.
* **Data:** sequences of length 128, each token id 0 followed by 127 tokens. Metrics use positions 1..126,
  i.e. the next-token distributions predicted at those positions.
  * **Fit set:** 512 windows from WikiText-103-raw-v1 train (first parquet shard). Each window is a random
    contiguous run of 20k lines, tokenised as a stream and cut into 127-token chunks. The fit set differs per
    fit seed (data seed = 1000 + fit seed).
  * **Eval sets** (the same for every cell, n = 128 sequences each):
    * (a) WikiText-103 *validation*, 128 random 127-token chunks of the token stream;
    * (b) NeelNanda/pile-10k documents with index ≥ 5000, in random order: the first 127 tokens of the first
      128 documents that have at least 127 tokens.
* **Metrics:**
  * For each sequence, KL(p_T‖·) is averaged over positions 1..126.
  * KL_k = KL(p_T‖q_k) and KL_source = KL(p_T‖p_S).
  * D_k = KL_12 − KL_k (k = 12 maps straight into the final LN and unembedding).

## Map and hyperparameters (same budget for every k)
* **Map:** affine, z = h W0 + b0 + σ ⊙ (h D + d).
  * (W0, b0) is ridge least squares from h_S to T's own residual R_k at the injection point. It is fitted on
    all fit positions 1..127, with ridge λ = 1e-3 · mean feature variance. It is then frozen.
  * σ is the per-dimension RMS of centred R_k.
  * (D, d) start at 0 and are trained with Adam on mean KL(p_T‖q_k) through T's frozen upper blocks.
  * The total map is still a single affine map. The σ-scaling makes the Adam step size comparable across
    output dimensions and depths, because T's residual stream has a few very large dimensions.
* **Training:** Adam (β = 0.9, 0.999), lr 1e-4, 10-step linear warm-up and then cosine decay to 0. 150 steps,
  batch 8 × 128, gradient-norm clip 1.0, no weight decay. Fit set n = 512. Fit seeds 7 and 8. Eval n = 128 per set.
* **lr selection:** a pilot on fit seed 99 (training data only, 40 steps, k ∈ {6, 12}); logs are in
  `logs/pilot_lr*.log`.
  * The first parametrisation, a plain Adam step on W scaled by RMS(W0), increased the training KL at
    rel-lr 0.01 and was abandoned.
  * With the σ-parametrisation, lr 1e-4 lowered a fixed-batch KL at k = 6 (1.307 → 1.096) and at k = 12
    (1.552 → 1.373). lr 3e-4 raised it at k = 6 (1.307 → 1.498).
* **Training-loss check:** no cell diverged. The mean of the last 25 steps is below both the step-0 value and
  the mean of the first 25 steps in every cell. Losses were still falling at step 150, so all maps are
  under-trained to the same degree.
* **Compute:** about 23–25 min per cell on a contended CPU.

## Unit test (run before every cell)
* **Self-injection test:** the hook captured T's own input to block k (or to the final LN) and re-injected it.
  * Logits were **bit-identical** to an unhooked forward pass: `torch.equal` is True and the max |Δ| is 0.0.
  * This held for k = 0, 3, 6, 9, 12 in a standalone test, and for each cell's k inside every run (stored in
    each JSON under `unit_test`).
* **Hook-effect test:** a random-noise injection changed the logits (max |Δ| ≈ 150–750), so the hook takes
  effect.
  * A constant +1 shift had no effect at k = 12, as expected, because LayerNorm is shift-invariant. This is
    why the noise test uses random noise.

## Results (`results/summary_S70m_T160m.json`; per-sequence values in `results/S70m_T160m_k*_s*.json`)
* **CIs:** paired bootstrap over the 128 eval sequences, 10 000 resamples, 95% percentile intervals.
* **Two-seed cells (k = 9, 12):** per-sequence KL is first averaged over seeds 7 and 8. The CI therefore
  reflects sequence sampling only.
* **D_k pairing:** D_k pairs each k with the seed-matched k = 12 cells.
* **Source baseline:** KL_source does not depend on k: 0.653 on WikiText-val and 0.563 on Pile.

**WikiText-103 validation (in-domain for the fit):**

| k | fit seeds | KL_k | KL_k − KL_src [95% CI] | D_k mean [95% CI] | D_k median [95% CI] | % seqs D_k>0 | top-1 agree (stitch / src) |
|---|---|---|---|---|---|---|---|
| 3 | 7 | 1.051 | +0.398 [+0.362, +0.439] | +0.132 [+0.069, +0.206] | +0.033 [+0.008, +0.056] | 63% | 0.455 / 0.567 |
| 6 | 7 | 1.028 | +0.375 [+0.339, +0.416] | +0.155 [+0.092, +0.230] | +0.066 [+0.044, +0.074] | 79% | 0.460 / 0.567 |
| 9 | 7, 8 | 0.942 | +0.289 [+0.256, +0.330] | **+0.254 [+0.196, +0.320]** | +0.143 [+0.130, +0.153] | 99% | 0.484 / 0.567 |
| 12 (=L) | 7, 8 | 1.197 | +0.544 [+0.461, +0.641] | — | — | — | 0.470 / 0.567 |

**Pile-10k, documents with index ≥ 5000 (domain shift relative to the WikiText fit):**

| k | fit seeds | KL_k | KL_k − KL_src [95% CI] | D_k mean [95% CI] | D_k median [95% CI] | % seqs D_k>0 | top-1 agree (stitch / src) |
|---|---|---|---|---|---|---|---|
| 3 | 7 | 2.389 | +1.826 [+1.606, +2.061] | +0.361 [−0.118, +0.967] | **−0.216 [−0.294, −0.151]** | 19% | 0.330 / 0.658 |
| 6 | 7 | 2.074 | +1.512 [+1.328, +1.708] | +0.675 [+0.183, +1.273] | **−0.055 [−0.087, −0.008]** | 41% | 0.360 / 0.658 |
| 9 | 7, 8 | 1.847 | +1.285 [+1.109, +1.482] | **+0.972 [+0.458, +1.627]** | +0.152 [+0.129, +0.178] | 96% | 0.400 / 0.658 |
| 12 (=L) | 7, 8 | 2.819 | +2.256 [+1.618, +3.059] | — | — | — | 0.402 / 0.658 |

**Seed-level means:**
* KL_9: 0.943 / 0.942 on WikiText and 1.825 / 1.870 on Pile.
* KL_12: 1.183 / 1.210 on WikiText and 2.749 / 2.889 on Pile.
* Seed-level D_9: +0.240 / +0.268 on WikiText and +0.925 / +1.019 on Pile.
* Seed-to-seed variation is small relative to D_9.

**Heavy tail at k = 12 on Pile:** the k = 12 stitch produces a few catastrophic sequences. On Pile the maximum
per-sequence KL_12 is 30.9, against a source maximum of 1.8. In WikiText it is 5.0. This inflates the mean
D_k at every k on Pile. It is why the mean D_3 and D_6 are positive on Pile while their medians are
negative.

## Verdicts
* **C1: replicates.**
  * At k = 9, D_9 > 0 with the CI excluding 0 on both eval sets, by mean and by median. This holds across
    both fit seeds and on 99% (WikiText) and 96% (Pile) of individual sequences.
  * It survives Holm correction over the three interior depths by a wide margin: the lower CI bound is far
    from 0 on WikiText.
  * At shallower depths the effect is weaker and not robust:
    * k = 3 and k = 6 have positive mean D_k on WikiText, and the medians are also positive but small.
    * On Pile, the median D_k is *negative* at k = 3 and k = 6: the read-out stitch beats them on a typical
      sequence. Their positive Pile means come from the k = 12 tail.
  * The robust statement is therefore "there is an interior depth (here 0.75·L) that beats direct read-out".
    The statement "every interior depth beats read-out" is not supported.
* **C2: replicates.**
  * KL_k − KL_source > 0 at every k on both eval sets, with every CI excluding 0. Even the best stitch is
    0.29 nats worse than the source on WikiText and 1.29 nats worse on Pile.
  * Top-1 agreement with T is also lower for every stitch than for the source alone.
  * The gap is much larger under domain shift. All maps were fitted on WikiText only, which likely makes
    C2 easier to satisfy on Pile than it would be with a Pile-fitted map.

## Limitations (stated honestly)
* **One pair only.** The pair is 70m→160m (ratio about 0.44 in parameters, 0.67 in width). The 1b arm was
  not run because of the compute budget.
* **Seeds:** k = 3 and 6 have a single fit seed. Their CIs include sequence sampling only and exclude map-fit
  variance.
* **Under-training:** 150 Adam steps with training loss still decreasing. A longer fit could shrink KL at all
  k, by different amounts. KL_L might in particular benefit more, but this was not tested.
* **Fit domain:** the fit used WikiText only. The Pile results mix the stitching effect with the domain
  shift of the map.
* **lr choice:** lr was chosen by a small pilot on training loss only, at k ∈ {6, 12}. It was not tuned per
  k; the same lr was used at every k.
* **Ridge-only baseline:** no ridge-only (untrained-correction) evaluation is reported. An early run with
  that evaluation was aborted (OOM/parallelism and an lr change), and its numbers are not used here.
