# X3 results: the i.i.d. speculative-decoding formula is accurate to within about 6% for 70m→410m (negative result)

Prereg: `07_preregistration_X3.md`. Raw data: `results/X3/specdec_70m_410m.json`. Tables: `results/X3_tables.md`.
Each γ was run with a single sampling seed. The 48 prompts × 96 tokens give 1 900–2 320 speculative steps per γ.

| γ | realised R | P1 (teacher-forced ᾱ) | e1 [95% CI] | e2 (dependence) [95% CI] |
|---|---|---|---|---|
| 2 | 2.000 | 2.013 | +0.6% [−1.9, +3.1] | −0.9% [−2.3, +0.6] |
| 4 | 2.301 | 2.407 | +4.6% [+0.1, +9.1] | −0.7% [−3.0, +1.8] |
| 8 | 2.470 | 2.620 | +6.1% [+1.4, +10.9] | −2.1% [−5.1, +0.7] |

## Preregistered verdicts
* **H-X3a (|e1| > 10% at γ = 8): not supported.** The point estimate is +6.1%, and the CI includes 10%.
* **H-X3b (dependence error ≠ 0): not supported** at any γ. All CIs include 0. The point estimates are
  negative, which is the predicted direction (positive burstiness), but they are at most about 2%.
  * A direct probe agrees. Given that the first draft was accepted, the realised acceptance rate of the
    second draft (0.649 / 0.601 / 0.611) is close to that position's mean α (0.628 / 0.617 / 0.615).
* **H0 (accurate within ±5%): holds at γ = 2 only.** At γ = 4 and 8 the plug-in formula *over*-predicts by
  5–6% (CI excludes 0).

## Interpretation
* **Size of the bias.** Plugging the teacher-forced acceptance rate into the i.i.d. formula over-predicts
  throughput by up to about 6%, and the bias grows with γ.
* **Source of the bias.** It comes mainly from the acceptance level *on the sampled path*
  (ᾱ_path = 0.59–0.61 vs ᾱ_TF = 0.624), not from within-block dependence.
* **Practical consequence.** For a CPU-scale Pythia drafter, the classical formula is adequate for
  planning γ to within about 6%. This is a small, cheap-to-correct effect, not a discovery.

## Validity checks and a correction to the prereg
* **Cache correctness:** max TV between cached and uncached distributions was 9e-5 (float32 noise).
* **Acceptance check:** the first-draft acceptance frequency matches ᾱ_path within CI at every γ. At
  γ = 8 the match is marginal: 0.565 [0.536, 0.594] vs 0.590.
* **Correction (found in the data, post hoc).** The prereg calls ᾱ_path "unbiased for on-path acceptance".
  That is not exactly true:
  * Step starts are selected positions. They follow either a residual-resampled token (one the draft
    under-weighted) or a bonus token.
  * The mix of these two cases changes with γ, which is consistent with ᾱ_path drifting from 0.610 to 0.590
    as γ grows.
  * So the e1 − e2 split into "path shift" vs "dependence" is approximate. It is reported as descriptive.
    The verdicts on e1 do not depend on it.

## Evidence category
**Negative / inconclusive (single seed per γ):** no evidence of a practically large i.i.d.-formula error at this scale.
