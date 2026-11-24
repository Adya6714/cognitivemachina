# Adversarial review of the E1 design (Agent 8)

Status: written 2026-11-24 while the confirmatory queue was running (the first cell, `S70m_T410m_k6_mse_s0`,
was in progress and `results/E1/` was empty). I loaded no models and ran no heavy computation. The review
covers the frozen preregistration, the theory, the code, the pilot logs and the literature matrix. I treat the
designer's conclusions as claims, not facts. Severity levels: **fatal** means the stated inference cannot be
drawn as designed. **Major** means the inference is open to a strong alternative explanation, or a
preregistered rule cannot be carried out. **Minor** means it should be fixed or disclosed.

Line numbers refer to the files as they stood when I read them: `docs/05_preregistration_E1.md` (prereg),
`docs/03_theory.md` (theory), `xscale/run_cell.py`, `xscale/common.py`, `xscale/queue_E1.sh` and `logs/`.

## What I checked and found correct
I don't raise issues for the following, so the designer need not defend them.
* **Position handling.** BOS (id 0) is at position 0 (`common.py:101`). The target's own position-0 state is
  copied into the stitched input, both in KL training (`run_cell.py:346`) and in evaluation
  (`run_cell.py:372`). Position 0 is excluded from the ridge fit (`run_cell.py:321`). The position-0 state does
  not depend on the input, so copying it leaks no information.
* **Metric indexing.** Positions 1..T−2 predict tokens 2..T−1 (`common.py:173-179`), which gives 126 positions.
  This indexing is correct.
* **Injection runs exactly blocks k..L−1 plus the final LN and head.** `sliced` (`common.py:138-152`) does this,
  and k = L bypasses the blocks. Rotary embeddings are recomputed inside the sliced forward from the default
  `position_ids = arange(T)`, which is the same as in the full model. Decision 7 reports an exact
  reproduction.
* **Document-level fit/eval separation.** Fit sequences come from Pile-10k docs [0, 5000) and eval sequences
  from docs [5000, 10000), with one window per document (`common.py:83`).

---

## Fatal

### 1. The primary contrast Δ_k (vs. source alone) cannot isolate "the upper layers use the source state". In the pilot, the affine-plus-target-head read-out cannot even reproduce p_S. — FATAL for H-ratio as an H1 test
* **Evidence: the definitions.**
  * Prereg:35-37 defines Δ_k = KL(p_T‖p_S) − KL(p_T‖q_k).
  * The theory (theory:24-31) says the correct comparator is G(L), the distilled linear head (k = L). It calls
    "an interior minimum strictly below G(L)" the operational signature of H1.
  * The prereg replaced this comparator with p_S, which is a different quantity.
* **Evidence: the pilot.** In `logs/pilot_kl_k24_ln_scaled.log`, the 70m→410m map at k = 24 is trained by KL
  directly toward p_T. After 150 steps its eval KL is still 1.62, against KL(p_T‖p_S) = 0.78. This map runs no
  upper blocks. It is a pure read-out of the source's final features through T's final LN and unembedding.
  So the map class {A ↦ W_U^T · LN_T(A s)} fits on 256×127 tokens cannot represent the source's own
  next-token distribution.
* **Consequence for 70m.** "Δ_k < 0 at every k for 70m" is then predicted by a *read-out/representability
  bottleneck* (the affine-map + target-head family, finite fit data, few optimiser steps), whatever the upper
  layers can or cannot do.
* **Consequence for the sibling.** For 410m-deduped, d_S = d_T and the two unembeddings are near-aligned, so
  the k = 24 head can probably recover p_S. Training it toward p_T then gives Δ_24 > 0 through *distillation
  alone*.
* **Consequence for H-ratio.** H-ratio's two predictions (prereg:47-50) can therefore both "succeed" with zero
  contribution from blocks k..L. As designed, H-ratio measures how well the source can be read out through T's
  head as a function of source width, not cross-model use of upper layers.
* **Required response.** This is a deviation from the frozen prereg, so it must be labelled as one. Do both of
  the following:
  * **(a) Representability-ceiling cell for each pair (no upper blocks).** Fit A at k = 24 to minimise
    KL(p_S‖q_{24,A}) and report how close it gets. If it cannot reach roughly 0.1 nats, then "source alone" is
    not attainable inside the map class, and Δ_k < 0 is uninterpretable for that pair.
  * **(b) Report D_k = G(L) − G(k) alongside Δ_k**, with G = KL(p_T‖q_kl) at each k. This is the theory's own
    H1 signature. Every k = 24 kl cell already exists in the grid, so (b) costs no extra compute. State
    explicitly that a positive max_k Δ_k attained at k = 24 is evidence of distillation, not of H1.

---

## Major

### 2. In H-ratio, "size ratio" is confounded with source capability, width, depth, FLOPs and probably shared initialisation. The sibling is not a clean equal-size control. — MAJOR
* **Evidence: only three pairs.** There are three pairs (prereg:20-22). Ratio moves together with:
  * source width d_S: 512 / 768 / 1024
  * source depth L_S: 6 / 12 / 24
  * source loss, and KL(p_T‖p_S), which is 0.78 for 70m in `logs/pilot_70m_410m.log`
  * source FLOPs: 1.5 / 6.8 / 24 target blocks, excluding the head (my arithmetic from `common.py:58-64`)
* **Evidence: the sibling's training differs.** Pythia-410m-deduped was trained on deduplicated Pile for
  about 1.5 epochs. It differs from the target in data and data order, not in size.
* **Evidence: likely shared initialisation.** In the released Pythia configs, the deduped and standard
  models of one size appear to share the same architecture *and seed*, though this needs verifying. If they
  start from the same initialisation, their residual bases may be partly aligned. The ratio-1.0 point would
  then carry "shared init" rather than "equal size".
* **Evidence: memorisation exposure.** The eval data are Pile-10k, which comes from the Pile *train* set.
  The non-deduped target saw duplicated documents several times; the sibling saw them once. Agreement with
  p_T on memorised spans differs between the pairs for reasons unrelated to size.
* **Evidence: a monotone trend cannot be tested.** With 3 points, one of them qualitatively special, a
  monotone trend is not testable. The falsification criteria (prereg:49-50) test only the two endpoints, so
  160m→410m plays no role in falsification.
* **Required response.**
  * **(a) Different-seed equal-size controls.** Use PolyPythias (arXiv 2503.09543, verified; for example
    `EleutherAI/pythia-410m-seed1` → 410m). This gives an equal-size, same-data, different-seed control. The
    literature matrix itself recommended it (`02_literature_matrix.md:269`) and the prereg dropped it.
  * **(b) Measure the zero-training identity stitch** (inject 410m-deduped's own R_k unchanged) at each k. This
    quantifies how much of the sibling result is pre-existing alignment.
  * **(c) Rename H-ratio "source-model effect".** Alternatively, add a capability covariate such as KL(p_T‖p_S),
    and state that ratio is not separable from capability with these three pairs.

### 3. The confirmatory runs deviate from the frozen prereg on n_fit. — MAJOR (protocol integrity)
* **Evidence.**
  * Prereg:5 says confirmatory cells use "n_fit = 1024".
  * Prereg:29 says "n_fit = 512".
  * `run_cell.py:269` defaults to 512, and `queue_E1.sh:405-412` passes no `--n_fit`.
  * The convergence cell (`queue_E1.sh:414`) uses 1024.
* **Required response.** Log this as a deviation in the decision log now, before any results are seen. State
  which value is the preregistered one. If it is 1024, the running queue does not implement the prereg.

### 4. The preregistered divergence rule cannot be carried out, and the training log cannot show convergence. — MAJOR
* **Evidence.**
  * Prereg:87-88 says a cell is an "optimiser failure" if its final train loss exceeds its step-0 loss, and
    that such cells are rerun at lr/3.
  * `run_cell.py:350-351` logs only every 25 steps, starting at step 25. The step-0 loss is never recorded.
  * Each logged value is a single-minibatch loss, which is noisy: it moves 1.33 → 1.38 between steps 50 and 75
    in `pilot_kl_k12_ln_scaled.log`.
  * `queue_E1.sh` has no lr/3 rerun path.
  * The fitted maps (W0, b0, M, c) are not saved. No post-hoc diagnostic can reuse them, so every follow-up
    below must refit.
* **Required response.**
  * Record the step-0 loss and a held-out fit-set KL at the start and end of training.
  * Implement the rerun rule.
  * Save the maps (`torch.save`). Each is at most 4 MB.

### 5. "Fails" may be an artefact of under-training or over-fitting, and of differences in effective step size between pairs and depths. The convergence check is confounded. — MAJOR
* **Evidence: the pilots were neither converged nor generalising.**
  * At k = 12, eval KL went from 1.594 to 1.559 to 1.543 over steps 100, 125 and 150. It was still falling.
  * Train KL was about 0.95 against eval KL of 1.54, a gap of 0.6 nats at 256 fit sequences. The k = 24 run
    shows the same pattern (1.12 vs 1.62).
  * The confirmatory recipe (200 steps, cosine to zero, 512 sequences, about 3 epochs) anneals rather than
    converges. The map has 0.5–1 M parameters and is fit on 65 k tokens.
* **Evidence: the parametrisation is not scale-neutral across pairs** (`run_cell.py:332`). The correction is
  ((X−m)/s_x) M / √d_S · s_y.
  * With Adam's per-entry steps of about lr, the change in output scales like lr·√d_S·s_y.
  * The sibling (d_S = 1024) therefore gets about 1.4× the function-space step of 70m (d_S = 512).
  * s_y grows with depth, and is dominated by outlier dimensions.
  * The pilots show that this scaling choice determines success or failure: the unscaled k = 24 run went to
    KL 11 (`pilot_kl_k24_ln.log`).
  * A single untuned lr = 3e-3 then favours some pairs and depths over others, which is a confound for both
    H-ratio and H-objective.
* **Evidence: the convergence check is confounded and incomplete.** `queue_E1.sh:414` changes the step count
  (200→600) and n_fit (512→1024) together, and only for 70m at k = 12.
* **Required response.**
  * Run the convergence check for 70m *and* the sibling at k = 12.
  * Vary steps with n_fit fixed, and n_fit with steps fixed.
  * Run a 3-point lr sweep, {1e-3, 3e-3, 1e-2}, for one depth per pair.
  * Report held-out fit-set loss curves.
  * Call a cell's verdict "robust" only if its sign of Δ (or D_k) survives these changes.

### 6. H-objective is close to tautological and does not test the contradiction. — MAJOR
* **Evidence.** The kl map is initialised at the ridge solution and trained to minimise the evaluation metric
  itself (`run_cell.py:328-349`). The pilot already shows a factor of 2.0/1.54 ≈ 1.3 at k = 12 after 150
  steps. Whether the factor clears 1.5 is a question of training budget, not of the objective.
  * The prereg's own wording (prereg:52, "tests whether the objective explains the works/fails
    contradiction") needs a sign change, not a ratio. The question is whether the kl objective turns Δ_k (or
    D_k) from negative to positive.
  * The criterion has no CI or decision rule, and the mse cells are single-seed.
* **Required response.** Restate H-objective as "kl changes the sign of Δ_12 (or D_12) for some pair". Report
  the 1.5× ratio as descriptive only, with a seed-stratified CI on the paired per-sequence log-ratio.

### 7. H-dissociation is almost guaranteed by chance and by the choice of metric. — MAJOR
* **Evidence: the chance rate.** With 4 depths, an argmax and an argmin drawn independently and uniformly
  disagree with probability 3/4 per pair. P(≥ 2 of 3 pairs disagree) = 0.84 under the null. The prediction
  therefore carries little information.
* **Evidence: structural bias.** The source feature is S's final-LN output, so R² and CKA are pulled toward
  k = 24. The pilot's R² rises monotonically to 0.55 at k = 24. KL, meanwhile, rewards keeping upper
  computation.
* **Evidence: pooled R² is dominated by outlier dimensions.** R² is computed pooled over dimensions
  (`run_cell.py:384`; `ridge.py:228-233`), so it is driven by the few high-variance (outlier/"massive") residual
  dimensions. Linear CKA has the same weighting problem.
* **Evidence: R² is ambiguous for kl cells.** `run_cell.py:372-384` computes R² from P = mapf(X), which
  *includes* the trained KL correction. The docstring (`run_cell.py:11`) instead says "held-out R² of the ridge
  map". The prereg does not say whether H-dissociation uses mse-cell or kl-cell R².
* **Required response.**
  * State the null rate (0.84) in the report.
  * Use the mse-cell R² explicitly.
  * Add a per-dimension-standardised R² (mean of per-dimension R²) and CKA on standardised features, or SVCCA
    as in Chen et al.
  * Treat dissociation as supported only if it survives these alternatives *and* holds across all three seeds.
  * Better still, evaluate over all 25 depths for the cheap mse/R² part.

### 8. Statistics: the CIs ignore map-fitting variance, multiplicity correction protects the hypothesis, and the confirmation criteria are asymmetric. — MAJOR
* **Evidence: the unit of analysis.** The unit is the eval sequence, and the bootstrap is over sequences
  stratified by seed (prereg:76-79). Most cells are single-seed (prereg:63-67). A sequence bootstrap treats the
  fitted map as fixed, so the CI describes *this map*, not the method. With one seed per cell, a CI that
  excludes 0 can come from one lucky or unlucky fit.
* **Evidence: seeds confound fit data and eval data.** Seed s changes both the fit permutation and the eval
  set (seed 100+s) (`run_cell.py:307-309`). The eval sets of different seeds come from the *same* doc pool and
  can share documents. Expected overlap is small (about 1–2 sequences), but it is not checked, although
  `eval_hash` covers only whole sets.
* **Evidence: Holm is applied in the wrong direction.** Holm runs over the 12 Δ_k > 0 tests (prereg:80). For
  70m, the "falsified if some k has Δ_k > 0" criterion is a test the hypothesis *wants to fail*. Correcting it
  for multiplicity lowers the power to falsify, which protects the hypothesis.
* **Evidence: the 70m prediction is never positively confirmed.** The prediction is "max_k Δ_k < 0"
  (prereg:48), but no confirmation criterion is given: no test of Δ_k < 0. A result that cannot be
  distinguished from 0 is silently counted as "not falsified".
* **Evidence: the pairing is not stated.** The prereg does not say Δ_k is bootstrapped as a *paired*
  per-sequence difference.
* **Required response.**
  * Run at least 3 fit seeds (with the eval set fixed) for every cell that enters a hypothesis decision.
    Alternatively, report a two-level bootstrap (over seeds, then sequences) and label single-seed decisions
    as provisional.
  * Use an intersection–union test for "Δ_k < 0 at all k" (each one-sided at α, no correction).
  * Use Holm only for the existence claim "some Δ_k > 0".
  * Bootstrap the paired differences.
  * Fix the eval set across fit seeds.

### 9. Replacing every position conflates context (K/V) corruption with per-token representational mismatch, and attention-sink or outlier effects are not measured. — MAJOR (alternative explanation)
* **Evidence.**
  * Every position ≥ 1 is replaced (`run_cell.py:346, 372`). Block k therefore attends to keys and values
    built entirely from mapped states, so errors compound across positions.
  * A mid-depth failure can come from corrupted attention context rather than from the current token's
    state.
  * Only the position-0 sink is protected. If 410m has secondary high-norm or "massive-activation" tokens
    (delimiters, newlines), an MSE-fit map that regresses toward the mean will flatten them and disrupt
    attention patterns.
  * 2606.03280 (the "fails" paper) injects at selected positions while the receiver keeps the full prompt. So
    the study's all-position setting is not the setting it claims to reconcile.
* **Required response.**
  * Add a diagnostic using the saved kl and mse maps: replace *only the last position* (true target states at
    positions < t) at k ∈ {12, 24}, for 70m and the sibling.
  * Report the norm-ratio of mapped vs. true states per dimension (top-5 outlier dims) and KL by token class.
  * Keep all-position replacement as the H2-relevant setting, but do not attribute its failure to
    "representational mismatch" without this split.

### 10. The works/fails "contradiction" is probably a difference in metrics and baselines, which E1 does not reproduce. — MAJOR (framing)
* **Evidence.** Per the matrix (`02_literature_matrix.md:161-163`), the three papers each use a different
  metric and baseline:
  * **2608.09521:** "works" means 72–88% top-1 agreement with the back model, across families, at similar
    sizes, with no source-alone baseline. In our own pilot, 70m *alone* already agrees with 410m on top-1 for
    61.8% of tokens. For similarly sized models, front-model-alone agreement could well be ≥ 72%. So "works"
    there may be *below* the trivial baseline.
  * **2606.03280:** "destructive" is relative to the *receiver alone*, which has the full prompt, and is
    measured as multi-hop task accuracy. Any perturbation of a model that already has the answer looks
    destructive against that baseline.
  * **2603.18908:** this is an output-head read-out on MMLU, and it is ambiguous whether the upper layers run.
* **Consequence.** E1's Δ_k uses a third baseline (source alone) and a third metric (KL). E1 can therefore
  neither confirm nor dissolve the contradiction as framed (prereg:7-16; `04_ranking.md:159`).
* **Required response.**
  * Reframe the motivation as "the literature uses incompatible metrics and baselines".
  * Report all three baselines for every cell: source-alone, target-alone (KL to native), and the G(L)
    read-out.
  * Report top-1 agreement next to KL, so that 2608.09521's 72–88% can be placed on our scale.

### 11. FLOP accounting and H-self are mis-specified. — MAJOR for H2 claims; minor for H1
* **Evidence: the source head is overcounted.** `run_cell.py:295` adds S's head (2·d_S·V) to the stitched
  cost, but the stitched model reads only S's final-LN output and never S's logits. For 70m, the head
  (51 MFLOP) is larger than its 6 blocks (38.5 MFLOP).
* **Evidence: the prereg's cost estimate is wrong.** Prereg:57 says "70m costs about 0.25 of a 410m block".
  Using `common.py:58-64` at T = 128, 70m's blocks cost **1.52** 410m blocks, and 3.5 with its head. 160m costs
  6.8 blocks. 410m-deduped costs 24 blocks, so the sibling stitch costs *more than running the target*. H2
  efficiency is therefore undefined for the sibling, and its inclusion in an "efficiency" narrative is
  vacuous.
* **Evidence: other omissions.** The cost of the map (d_S·d_T) is omitted. The self:1 baseline is not
  cost-matched to 70m; that would need self:2.
  * self:1→k is an affine layer-skip within one model, sharing coordinates with the target. Beating 70m is
    the expected result and says little about cross-model use.
* **Required response.**
  * Drop the source head from `stitch_flops`.
  * Correct prereg:57 in a deviation note.
  * Add a self:2 kl cell at k ∈ {6, 12}, cost-matched to 70m.
  * Exclude the sibling from H2.

---

## Minor

### 12. Possible near-duplicate leakage between fit and eval halves. — MINOR
* **Evidence.** Pile-10k is drawn from the non-deduplicated Pile, so document-index disjointness
  (`common.py:83`) does not guarantee content disjointness.
* **Required response.** Check n-gram (for example 32-token) overlap between the fit and eval sequences once,
  and report it.

### 13. WikiText-103 is not a domain shift for Pythia. — MINOR
* **Evidence.** Wikipedia is a Pile component.
* **Required response.** Relabel it "second corpus", or use a non-Pile corpus.

### 14. Window selection. — MINOR
* **Evidence.** Keeping only documents of ≥ 127 tokens and only their first 127 tokens (`common.py:99-101`)
  biases the sample toward document openings and longer documents.
* **Required response.** Disclose this. Positions are fine.

### 15. Ridge λ. — MINOR
* **Evidence.** λ_rel = 1e-3 is set relative to the *mean* eigenvalue (`ridge.py:222`), so outlier dimensions
  set the regularisation scale differently for each d_S. The pilot shows Δ is insensitive between 1e-3 and
  1e-2, but less so at 1e-1 (KL at k = 24 goes from 2.35 to 2.75).
* **Required response.** Report a two-value λ check for one cell per pair.

### 16. KL direction. — MINOR
* **Evidence.** Training and evaluation both use forward KL(p_T‖q), which is consistent. Forward KL penalises
  missing mass heavily, and is reported in nats whose scale differs across pairs.
* **Required response.** Report the 1−TV and top-1 deltas next to Δ, as the prereg already plans. Also
  report Δ normalised by KL(p_T‖p_S).

### 17. Inconsistencies inside the prereg. — MINOR
* **Evidence.**
  * The budget-stop rule drops "seeds 1–2 of the mse cells" (prereg:89-90), but no such cells exist.
  * The "64 × 126 × 3 seeds" unit (prereg:76) holds only for 10 cells.
  * Chen et al. used the *deduped* 70m/160m (`02_literature_matrix.md:160`), whereas E1 uses the non-deduped
    models. A direct comparison with their CE 3.99 is therefore approximate.
* **Required response.** Correct these in the deviation note.

### 18. The unit-test evidence for 410m is not on disk. — MINOR
* **Evidence.** `test_injection.py:19` defaults to 70m/160m. Decision 7 claims exactness for 410m, but no log
  is saved.
* **Required response.** Save a 410m (and 1b) run log before the 1b arm runs.

---

## Prior art: does any paper already answer the hypotheses?
* **H-objective.** Largely pre-empted in direction:
  * In vision stitching (Bansal 2021; Mai 2603.12433), task-loss stitches beat MSE stitches.
  * Balogh 2412.11299 shows task-loss stitches can make distant layers look similar.
  * Only the effect size in Pythia LMs is new.
* **H-dissociation.** Partly pre-empted:
  * Chen 2506.06609 picks layers by SVCCA and never checks them functionally.
  * NinaXander 2609.38261 already reports CKA/R² next to a functional switch-layer sweep (same size).
  * Almudévar 2601.21568 argues that representational similarity is sufficient but not necessary for
    functional similarity.
  * The new contribution is the cross-scale version. It is only informative if issue 7 is fixed.
* **H-ratio.**
  * 2603.18908 reports that transfer depends on source scale, and that strong→weak beats weak→strong (across
    families).
  * Bansal 2021 shows that "better" representations plug into weaker models.
  * A within-family ratio curve is new, but issue 2 means E1 cannot separate ratio from capability.
* **H-self.** The self linear shortcut is well established (Jump to Conclusions 2303.09435; Tuned Lens
  2303.08112; layer-skipping work). That self:1 beats 70m is expected.
* **The contradiction.** See issue 10: it is probably not real; the papers differ in metric and baseline.
* **Caveat.** I could not independently read the 2026 papers. These judgements rely on the matrix's
  summaries. I verified only PolyPythias (arXiv 2503.09543).

## Minimum additional experiments, ranked by how much they would change my confidence
CPU estimates come from the pilots: 4.8 s/step at k = 12, about 1.6 s/step at k = 24, and about 2–5 min of fit
statistics per 512 sequences. They assume the queue is idle.

| Rank | Experiment | Addresses | Approx. CPU cost |
|---|---|---|---|
| 1 | Representability ceiling: at k = 24, fit A to minimise KL(p_S‖q) for each of the 3 pairs. Recompute D_k = G(24) − G(k) from existing cells | Issue 1 (fatal) | 3 cells × about 10 min ≈ **0.5 h**; D_k is free |
| 2 | PolyPythias 410m-seed1 → 410m, kl at k ∈ {12, 24}, plus the zero-training identity stitch 410m-deduped → 410m at all 4 k | Issue 2 | 2 × about 35 min + 4 × about 5 min ≈ **1.5 h** |
| 3 | Training-robustness grid: 70m and sibling at k = 12. Steps 600 at n_fit 512; n_fit 1024 at 200 steps; lr {1e-3, 1e-2} at 200 steps. Save maps | Issues 3–5 | about 6 cells, 16–50 min each ≈ **3.5 h** (cut to the 600-step pair, about 1.7 h, if pressed) |
| 4 | Last-position-only injection and outlier-norm diagnostics, reusing saved maps (k ∈ {12, 24}; 70m and sibling) | Issue 9 | eval only once maps are saved, about 5 min each ≈ **0.3 h** (plus refits if maps were not saved) |
| 5 | Fit seeds 1–2 for every cell that decides a hypothesis (kl at the argmax-Δ depth per pair, and mse at k = 12), with the eval set fixed | Issue 8 | about 8 cells ≈ **2.5–3 h** |
| 6 | Cost-matched self:2 kl at k ∈ {6, 12}; standardised R²/CKA computed from mse refits (no training) | Issues 7 and 11 | **≈ 1 h** |

If only one item can be added, do rank 1. It costs about 30 minutes and decides whether the primary outcome
means anything for the 70m pair.
