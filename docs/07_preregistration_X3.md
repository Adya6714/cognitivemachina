# Preregistration — X3: How wrong is the i.i.d. speculative-decoding formula for a real small→large Pythia drafter, and why?

Status: **FROZEN** in the commit that adds this file. No X3 data existed at that point.

## Question
Leviathan et al. (2211.17192) predict E[tokens per target call] = (1 − ᾱ^{γ+1}) / (1 − ᾱ), assuming i.i.d.
acceptance with rate ᾱ. Practitioners plug in a ᾱ measured by teacher forcing on held-out text. That
plug-in prediction can be wrong for two separable reasons:
1. **Path shift.** Speculative sampling walks along text sampled from p_T, not along dataset text, so the
   mean acceptance on the realised path can differ from the teacher-forced mean.
2. **Dependence.** Acceptances within a draft block are correlated (bursty), so E[Π α] ≠ ᾱ^j. Note that
   heterogeneity that is *independent* across positions leaves the formula unbiased (E[Π α_i] = Π E[α_i]),
   so only dependence and path shift can bias it.

Prior work does not quantify this decomposition (see `02_literature_matrix.md`, A3; SpecDec++ 2405.19715
argues context dependence; 2608.30427 shows histogram structure). Novelty is expected to be small (N1–N2).
This is a secondary, low-cost study.

## Design
* **Models.** Draft q = pythia-70m, target p = pythia-410m. Temperature 1, standard speculative sampling
  (accept with min(1, p/q), resample from norm(max(0, p − q)) on reject, bonus token if all accepted),
  with KV caches.
* **Prompts.** 48 prompts of 32 tokens (BOS + 31) from Pile eval documents (pile-10k index ≥ 5000, seed 200),
  disjoint from E1's eval seed. 96 new tokens per prompt.
* **Draft lengths.** γ ∈ {2, 4, 8}, with an independent sampling seed per γ.
* **Quantities.**
  * R = realised mean committed tokens per target call. This is the per-prompt ratio tokens/calls; the
    final partial step is excluded.
  * P1 = formula with ᾱ_TF, the teacher-forced mean of 1 − TV(p, q) on 64 held-out Pile sequences of
    length 128 (seed 201).
  * P2 = formula with ᾱ_path, the mean α at the *first* drafted position of each step on the realised path.
    The first position is never selected by earlier acceptance, so ᾱ_path is unbiased for on-path
    acceptance.
  * Built-in validity check: the realised acceptance frequency of the first drafted token must match
    ᾱ_path within its CI. A mismatch means an implementation bug.
* **Errors.**
  * e1 = (P1 − R) / R, the total error of the practitioner's formula.
  * e2 = (P2 − R) / R, the error due to dependence alone.
  * e1 − e2 is the error due to path shift.

## Hypotheses
* **H-X3a.** |e1| > 0.10 at γ = 8. Confirmed if the 95% CI of e1 excludes [−0.10, 0.10] on one side.
* **H-X3b.** e2 ≠ 0 (dependence matters). Confirmed if the 95% CI excludes 0 at γ = 8.
  * Prediction: e2 < 0 (positive burstiness makes the formula *under*-predict).
* **Competing hypothesis H0.** The formula is accurate: |e1| < 0.05 and the CIs are within ±0.05.

## Statistics
* **Unit:** the prompt.
* **Intervals:** bootstrap over prompts (10 000 resamples). P1 is treated as fixed, and its
  teacher-forced sampling CI is reported separately. P2 is recomputed within each resample.
* **Seeds:** one seed per γ, labelled single-seed.

**Pilot disclosure.** Before the freeze, a 2-prompt × 16-token smoke test was run to debug the KV-cache code. Its output was deleted, it used the same prompt seed (its 2 prompts are a subset of the 48), and it informed no design choice beyond the cache-test tolerance: TV < 1e-4, with float32 reordering noise of 9e-5 observed.
