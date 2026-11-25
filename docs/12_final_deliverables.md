# Final deliverables: D1, D2, D4, D5, D6 and D8

The full report (D3) is `09_main_report.md`. The executive PDF (D7) is `report/executive_summary.pdf`. All numbers
are traceable to `results/E1_tables.md`, `results/X3_tables.md` and `replication/REPORT.md`.

---
## D1. Executive conclusion

**Bottom line.** When a much smaller Pythia model's final state is affinely injected into Pythia-410m, the
target's last quarter of blocks reads it out better than the target's head does. For equal-size models this never
happens. No such stitch is a better approximation of the target than the small model alone. So there is no
drafting speed-up from frozen cross-scale latent injection at this scale.

**Established** (replicated, multi-seed, robust to the checks run):
* **E1: interior depth beats the read-out for 70m.** For 70m→410m, injecting at depth 18 of 24 beats the linear
  read-out.
  * Pile: D_18 = +0.136, seed-level CI [0.074, 0.198], 3 seeds.
  * WikiText: +0.111 [0.062, 0.160].
  * Maps trained 3× longer: +0.121 [0.097, 0.144].
  * Replicated by independent code for 70m→160m at depth 9 of 12: D_9 = +0.254 [0.196, 0.320].
* **E2: no stitch beats the source alone.** Every stitch is worse than the source model alone: Δ_k < 0 in 16 of 16
  tests, and in the 600-step cells and the replication too.
* **E3: equal-size siblings never benefit.** For both, there is no k < 24 with D_k > 0.
  * The siblings are 410m-deduped (same seed, different data) and 410m-seed1 (same data, different seed).

**Preliminary** (single target family, 3 seeds or fewer, or depends on the budget or eval set):
* **P1.** 160m→410m D_18 = +0.072, CI [0.015, 0.129] on Pile, but not significant on WikiText. Its 600-step
  value is +0.071 [0.051, 0.090] (WikiText +0.041 [0.024, 0.058]), robust.
* **P2. KL training helps only modestly at 200 steps.** It improves over ridge by 1.30–1.35× at k = 12, short of
  the preregistered 1.5×. At 600 steps the ratio is 1.49–1.62×, so it depends on the budget.
* **P3. Similarity peaks at the read-out, function does not.** Representational similarity (CKA, R²) peaks at
  k = 24 for all pairs, while the functional optimum for small sources is k = 18. This is descriptive, and CKA
  margins are small.
* **P4. T's own early layers beat the 70m stitch early.** T's own first layer beats it at k = 6 (+0.84). They tie
  at k = 12. The 70m stitch is better at k ≥ 18.
* **P5. Read-out bottleneck.** A k = 24 affine map trained to reproduce p_S still has KL(p_S‖q) of 0.48–0.89.

**Unverified or exploratory:**
* **U1. Possible shared initialisation.** Identity stitches suggest the deduped sibling shares raw coordinates
  with 410m (KL 3.5 vs 9.5 for the seed sibling), consistent with a shared initialisation. One cell each, and the
  initialisation is not verified.
* **U2. A substantial per-token mismatch remains.** Shown by the single-position diagnostic (8 sequences, k = 12).
  The "≈ 40% context corruption" decomposition is **withdrawn**.
* **U3. Second target (1b).** inconclusive. Single seed, 160m→1b (size ratio 0.16): D_4 = −0.266 [−0.351, −0.187], D_8 = +0.008 [−0.053, 0.066] (no benefit at 1/4 and 1/2 depth, as in the 410m target at those relative depths); the 3/4-depth cell (k = 12), where the effect appeared in 410m, was dropped in the budget cut, so the decisive depth is untested

**Reproduction of prior work:**
* Chen et al. 2025 (2506.06609) report that MSE-stitched small Pythia models are much worse than the target. We
  reproduce this qualitatively (MSE stitches are 1.3–1.6× worse in KL than KL-trained ones).
* Leviathan/Chen speculative-sampling correctness: our implementation's cache test gives TV < 1e-4.

**Negative results:**
* **N1. The H-ratio sibling prediction is falsified.** The prediction was that a same-size sibling would draft
  better than its own source via stitching. Its best Δ is −0.370.
* **N2. X3: the i.i.d. formula is nearly right.** The i.i.d. speculative-sampling formula is accurate to 0.6–6%.
  The hypothesised large dependence error (> 10%) is not supported. The "5–6% over-prediction" sub-claim is not
  robust to uncertainty in ᾱ.
* **N3. Latent drafting without retraining.** Frozen small-model states are worse drafters than the small model
  itself.

---
## D2. Top-10 landscape (from `04_ranking.md`; weighted score out of 10)

| Rank | ID | Opportunity | Score | Novelty | Outcome |
|---|---|---|---|---|---|
| 1 | X1 | Cross-scale state injection: objective × depth × scale; function vs similarity; vs self-prefix | 7.75 | N2–N3 | **Executed (E1)**: preliminary finding |
| 2 | X3 | Per-token acceptance heterogeneity vs the i.i.d. speculative-decoding formula | 6.85 | N1–N2 | **Executed**: negative result |
| 3 | X2 | Emergence over training of cross-scale functional correspondence (checkpoints) | 6.80 | N2–N3 | Not run (budget); recommended next |
| 4 | X5 | Attention-importance transfer across scale for KV eviction | 6.70 | N2 | Rejected: crowded |
| 5 | X10 | Early-exit criteria blind spots under shift (H3) | 6.35 | N2 | Runner-up |
| 6 | X7 | Future-token linear decodability vs scale | 6.35 | N1–N2 | Rejected: largely answered |
| 7 | X6 | Mamba↔Pythia cross-architecture stitching | 6.30 | N2 | Rejected for now (2609.38261) |
| 8 | X4 | Feature vs token targets for draft heads | 6.00 | N2 | Rejected: CPU too slow |
| 9 | X8 | Retrieval vs recomputation with injected intermediate results | 6.00 | N2 | Rejected: overlaps the PI's programme |
| 10 | X11 | Lenient verification: realised distribution shift | 6.00 | N1–N2 | Rejected: incremental |

---
## D4. Evidence and novelty audit

Status codes: **DD** directly demonstrated · **SI** supported indirectly · **EX** exploratory · **NE** not yet
established.

| Claim | Supporting evidence | Closest prior work | Evidence strength | Remaining uncertainty | Status |
|---|---|---|---|---|---|
| For 70m→410m, depth-18 injection beats the linear read-out (D_18 > 0) | 3 seeds, Pile and WikiText, seed-level CI excluding 0; 600-step check +0.121; separate-code replication (70m→160m, k = 9) | 2603.18908 (late layers only); 2506.06609 (single depth, MSE) | Strong within the setting | Possible artefact of the map class; 1 500-step maps untested; one family | DD |
| Same for 160m→410m | 3 seeds on Pile (CI [0.015, 0.129]); WikiText CI includes 0; 600-step +0.071 [0.051, 0.090] (WikiText +0.041 [0.024, 0.058]), robust | same | Moderate | Eval-set dependence | SI |
| Equal-size siblings never benefit from interior injection | 2 siblings, 3 seeds (deduped), all k | PolyPythias 2503.09543 (sibling source) | Strong for these 2 pairs | Only 2 equal-size pairs; under MSE maps the siblings also have an interior optimum | DD |
| The sign change tracks size ratio, not data or seed | data sibling ≈ seed sibling; 70m and 160m positive | — | Moderate | 2 small sources only; ratio and absolute size confounded | SI |
| No affine stitch beats the source alone as an approximation of T | 16/16 CIs < 0; 600-step cells; replication | 2606.03280 (destructive injection) | Strong | Non-affine maps untested | DD |
| The KL objective improves over MSE by < 1.5× at k = 12 | 4 pairs, 200 steps | 2506.06609 (MSE only) | Moderate | Budget-dependent (1.49–1.62× at 600 steps) | SI |
| Similarity (CKA/R²) peaks at the read-out, function in the interior | 4 pairs, descriptive | Kornblith 2019; Bansal 2021 | Weak to moderate | Small CKA margins; pre-LayerNorm dimensions dominate | EX |
| Read-out bottleneck: the head cannot express p_S affinely | A1 calibration, 3 sources, single seed | — | Moderate | Upper bound (finite training) | SI |
| T's own early layers beat the 70m stitch at early k | self:1 at k = 6, +0.84 (paired CI) | LayerSkip / early exit | Strong at k = 6; tie at k = 12 | Single seed | DD (k = 6) |
| A shared initialisation yields partially shared raw coordinates | Identity stitches, 1 cell each | 2503.09543 | Weak | Initialisation not verified | EX |
| A per-token mismatch remains even with correct context | A7 diagnostic, 8 sequences | — | Weak | No CI; one k | EX |
| The i.i.d. speculative formula is accurate to within about 6% (70m/410m) | X3, 3 γ values, real sampling | 2211.17192; 2405.19715 | Moderate | One pair, one temperature, single seed per γ | DD (negative) |
| The effect transfers to a second target (1b) | inconclusive. Single seed, 160m→1b (size ratio 0.16): D_4 = −0.266 [−0.351, −0.187], D_8 = +0.008 [−0.053, 0.066] (no benefit at 1/4 and 1/2 depth, as in the 410m target at those relative depths); the 3/4-depth cell (k = 12), where the effect appeared in 410m, was dropped in the budget cut, so the decisive depth is untested | — | Single seed, reduced arm | — | NE / EX |

**Novelty statement.** Novelty class N2–N3: a new controlled design and an incremental finding. What is new is:
* the factorial design (size ratio × depth × objective in one family);
* the read-out comparator D_k;
* the finding that the target's last quarter beats its head only for much-smaller sources.

Stitching, KL-trained maps and similarity–function dissociation are **not** new.

---
## D5. Reproducibility package
* **Environment** (`requirements.txt`): Python 3.13, torch 2.15.0 (CPU), transformers 5.24.1, datasets 5.2.0,
  numpy 2.5.3, scipy 1.18.1, matplotlib 3.11.2. Hugging Face access is needed for the EleutherAI checkpoints and
  datasets.
* **Unit test:** `python3 xscale/test_injection.py`. It checks exact injection (max |diff| = 0).
* **One cell:**

  ```bash
  python3 xscale/run_cell.py --src S:70m --tgt 410m --k 18 --obj kl --seed 0 --out results/E1/S70m_T410m_k18_kl_s0.json
  ```

  This takes about 15 min on 4 CPU cores. Add `--steps 600 --n_fit 1024` for the convergence cells.
* **All cells:** `xscale/queue_E1_v2.sh`, `xscale/queue_E1_A8.sh` and `xscale/queue_R1.sh`. They are resumable.
  The full set takes about 25 CPU-hours.
* **Analysis:**
  * `python3 xscale/analyse_E1.py` writes `results/E1_tables.md` and `E1_summary.json`.
  * `python3 xscale/figures_E1.py` writes `figures/`.
* **Diagnostics:** `xscale/diag_single_pos.py`.
* **X3:** `xscale/specdec_x3.py`, then `xscale/analyse_X3.py`.
* **Replication:** see `replication/README.md`. It is separate code; run `replication/run_queue.sh`.
* **Provenance:** every result JSON stores its config, the eval-set hash, the step-0 and train log, FLOPs and
  per-sequence metrics. Deviations are recorded in `docs/00_decision_log.md`.

---
## D6. Manuscript and venue recommendation
* **Manuscript basis:** `09_main_report.md`.
* **Honest framing:** "a controlled study of where a small model's state is usable in a larger one: a depth ×
  size-ratio effect, and a negative result for latent drafting".
* **Recommended venue: a workshop.** Suitable examples include workshops on representational alignment,
  mechanistic interpretability, or efficient inference at NeurIPS, ICML or ICLR.
* **Why not a main-track conference:**
  * models ≤ 1b, one family
  * an affine map class only
  * a moderate effect size (about 0.1 nats/token)
  * no downstream-task evaluation
* **Upgrade path to a main track:** first run the three experiments in D8, plus a second model family.
* **No submission or posting has been made.** Any submission needs the PI's explicit approval.

---
## D8. Decision

**PRELIMINARY FINDING**
* **Why not "no novel discovery":** the depth × size-ratio effect for small sources is robust to seeds, eval set
  and a 3× training budget, and it was independently replicated.
* **Why not "discovery established":**
  * one model family, small scale, an affine map class;
  * the mechanism is unresolved: is it the extra frozen capacity, or something specific to the small model's
    state?
  * the 160m and 1b evidence is weaker;
  * the practical (drafting) hypothesis is negative.

**Next three experiments:**
1. **Capacity-matched read-out control.** This separates "upper blocks use the small model's state" from "six
   frozen nonlinear blocks are simply a better read-out than an affine head".
   * Compare D_18 against a k = 24 read-out given equal extra capacity: a 2-layer MLP or a 6-block trainable
     adapter before T's head, with the parameter count matched to the frozen blocks.
   * Include a shuffled-block control: T's blocks 18–23 replaced with blocks from an unrelated model.
   * Use 70m and 160m, 3 seeds, 600-step maps. Cost: about 6 CPU-hours.
2. **Cross-family and absolute-size replication.** This tests generality and separates size ratio from absolute
   size.
   * Pairs: Pythia-160m → 1b (full k grid including k = 12 = 3/4 depth, 3 seeds); Pythia-410m → 1.4b; and one non-Pythia family with a shared
     tokenizer (e.g. SmolLM2 135m → 360m → 1.7b).
   * Cost: a GPU-day, or about 40 CPU-hours.
3. **Training-dynamics emergence (X2).** This asks whether the interior advantage emerges early or late in
   training, and whether it tracks the onset of the dissociation between similarity and function.
   * Repeat 70m→410m D_18 across Pythia checkpoints (steps 1k, 8k, 32k, 143k) for both models.
   * Cost: about 4 CPU-hours.
