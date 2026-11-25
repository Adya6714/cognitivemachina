# Preregistration — R1 convergence check of the D_18 result (written before any of these cells ran)

**Why.** The results-stage adversarial review (`10_adversarial_review_results.md`, issue R1) argues that D_18 > 0
could be an optimisation artefact. Its reasoning:
* The k = 24 map starts furthest from its optimum.
* The k = 24 map may be the most under-trained at 200 steps.
* Longer training (C7) already improved k = 12 by about 15%.

**Cells.** All use the kl objective, seed 0, 600 steps, n_fit = 1024. These settings are identical to the existing
`_long` cells.
* 70m → 410m at k = 18 and k = 24
* 160m → 410m at k = 18 and k = 24

**Outcome.** D_18^long = KL(p_T‖q_24^long) − KL(p_T‖q_18^long). It is computed on the same Pile eval set (seed 100)
and paired by sequence, with a 95% bootstrap CI over sequences. This is a single seed, so the CI excludes
map-fit variance.

**Decision rule, fixed now:**
* **Robust to budget:** if the CI of D_18^long excludes 0 and the estimate is positive for 70m, C1 is reported as
  robust to a 3× training budget for 70m. The same applies to 160m, separately.
* **Not robust to budget:** if the CI includes 0, or the estimate is ≤ 0, C1 is reported as **dependent on the
  training budget**. In that case the headline becomes "not established for well-fit maps".
* **Shrinkage:** whatever the outcome, the change in D_18 from 200 to 600 steps is reported.

**Not done (budget).** The review also asked for the following. They are listed as future work:
* 1 500-step cells
* an lr sweep and L-BFGS at k = 24

**Run order.** These cells run before the last 1b cell (160m→1b k = 16). This is deviation D5.
