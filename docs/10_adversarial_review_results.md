# Adversarial review: E1/X3 results stage (Agent 8)

Read-only review. All numbers below were recomputed from `results/E1/*.json` and `results/E1_diag/*.json` with light Python; nothing was re-run.

## Issues

**R1. D_18 > 0 may be an optimisation-budget artefact (MAJOR, possibly fatal for C1; cheap to resolve).**
* **The trend runs against C1.** Seed 0, D_18 under ridge maps (mse) compared with 200-step kl maps:
  * 70m: +0.83 → +0.15
  * 160m: +0.42 → +0.10
  * deduped: +0.08 → −0.03
  * seed1: +0.15 → −0.02
* **Why.** Ridge is especially poor at k=24 (70m: mse KL 2.76 at k=24 vs 1.93 at k=18). The pre-final-LN residual has massive dimensions, so the k=24 map starts further from its optimum and gains most from training.
* **Pilot evidence.** `logs/pilot_kl_k24_ln.log` diverged to KL 11 at k=24. In `pilot_kl_k24_ln_scaled.log` the k=24 eval KL was still falling 0.024 per 25 steps at step 150, against 0.015 at k=12 (`pilot_kl_k12_ln_scaled.log`).
* **The A1 calibration cells raise the same concern.** At k=24, a map trained on p_S matches p_T as well as the map trained on p_T: 1.674 vs 1.683 (70m), 1.124 vs 1.130 (160m), 0.681 vs 0.682 (deduped). A well-optimised p_T-trained map should be strictly better on KL(p_T‖·).
* **No convergence data at k=18 or k=24.** The 600-step cells exist only at k=12, and C7 shows those maps are about 15% short of convergence.
* **Train logs cannot answer this.** They are single 8-sequence batches and too noisy.
* **Fix (cheap: k=24 cells are the fastest, about 8–10 min per 200 steps).**
  * For 70m and 160m, run k=24 and k=18 at 600 and 1500 steps with n_fit=1024.
  * Sweep lr at k=24 over {1e-3, 3e-3, 1e-2}, or fit the k=24 read-out to convergence with L-BFGS.
  * Select on a held-out fit split.
  * C1 stands only if D_18 > 0 survives with both arms converged.

**R2. The replication does not address R1 (MAJOR for "replicated independently").**
* **What is independent.** The code. It reuses the same parametrisation family: frozen ridge plus σ-scaled correction, from the prereg text.
* **How it was trained.** lr 1e-4 (30× smaller than E1) for 150 steps. Its losses barely move from step 0: k=12 s7 goes 1.14 → 1.05, with a spike to 1.96. So the replication is close to ridge maps, which is where D is known to be inflated.
* **Pile result is tail-driven.** The k=12 maximum KL is 30.9 (`REPORT.md`). The replication itself warns that "KL_L might benefit more".
* **What it does support.** An interior optimum at fixed, small budget, with a smaller source. That matches C1 in kind. It does not support C1 as a statement about the best affine maps.
* **The "3/4 depth in both" remark is weak** (`STUDY_GUIDE.md` §7). Both grids are quarters, so the coincidence has roughly 1-in-3 odds.

**R3. CIs exclude between-seed (map-fit) variance (MAJOR for the stated precision).**
* **How the CIs are built.** `boot_mean_ci` (`analyse_E1.py` l.30–38) resamples sequences within each seed and treats seeds as fixed. A seed changes the fit set, the eval set (seed 100+s) and the batch order. Init is deterministic ridge.
* **Pairing is correct.** D_k pairs seed-matched cells, and the eval hashes match.
* **Seed-level t intervals (df=2) are about 3× wider than the reported ones.** The effects still exclude 0 on Pile:

| Effect | Seed means | Seed-level 95% CI | Reported CI |
|---|---|---|---|
| 70m D_18 | 0.149 / 0.107 / 0.152 | [0.074, 0.198] | [0.117, 0.155] |
| 160m D_18 | 0.096 / 0.051 / 0.067 | [0.015, 0.129] | [0.055, 0.088] |
| 70m D_12 | 0.087 / 0.046 / 0.096 | [0.010, 0.143] | — |

* **On WikiText (domain-shift check), 160m D_18 and 70m D_12 lose significance:**
  * 160m D_18: [−0.016, 0.091]
  * 70m D_12: [−0.027, 0.088]
* **Fix.** Report seed-level intervals, or a hierarchical bootstrap that resamples seeds and then sequences, as the primary CI. Report the WikiText D_k.

**R4. The post-hoc seeds are unlabelled in the tables (MINOR to MAJOR).**
* A8 adds k=18 seeds 1–2 for all pairs and 160m k=24 seeds 1–2. In `E1_tables.md` they are pooled into the D_k and Δ_k rows as "[0, 1, 2]", with no post-hoc mark.
* **The preregistered D_18 test is seed 0 only:** 70m +0.149 [0.121, 0.177]; 160m +0.096 [0.072, 0.120]. It passes, and the A8 seeds agree in sign.
* **Fix.** Mark the A8 rows, and report the seed-0 test as the confirmatory one.
* **No best-seed reporting was found.**

**R5. Mechanism wording overreaches (MAJOR for interpretation).**
* `STUDY_GUIDE.md` l.256 says the "last 6 blocks add value to the small model's state" and that a small model's state "looks like an intermediate-depth state".
* **What D_18 > 0 actually shows.** An affine map followed by 6 frozen nonlinear blocks beats an affine map followed by LN and the head. It does not separate T's learned computation from the generic benefit of extra frozen nonlinear capacity.
* **The self-prefix cells show how generic the effect is.** self:1 D_18 = +0.97 and self:2 D_18 = +1.06: any under-processed input benefits.
* **Fix.** Use operational wording, i.e. Prop. 2's G(k), at a fixed budget. Optionally add a control: k=24 with a trainable small-MLP read-out of matched size, or k=18 with T's blocks 18–23 replaced by another model's blocks.

**R6. The siblings' D_k is overstated as "≤ 0" (MINOR).**
* Deduped D_18 = −0.028 excludes 0.
* Seed1 D_18 = −0.018 [−0.044, 0.006], single seed.
* **Fix.** Say "no k < 24 with D_k > 0". Under R1, the siblings' sign flip from mse to kl suggests their D could fall further, which is consistent with C1's contrast.

**R7. H-objective (C3) depends on the training budget (MAJOR for C3).**
* **The comparison mixes seeds.** Pooled kl over seeds 0–2 is compared with mse at seed 0. Seed-0-only ratios are the same, 1.29–1.35.
* **The 600-step maps give larger ratios:** 70m 2.061/1.379 = **1.49**; deduped 1.176/0.728 = **1.62 (> 1.5)**.
* **Fix.** "Not met" holds only at 200 steps. State that 1.30–1.35× is a lower bound and that one pair passes the threshold with longer training.

**R8. C7 confounds steps with data (MINOR).**
* The long cells change both steps (600) and n_fit (1024).
* **There is a train/eval gap.** 70m klsrc: train-batch KL about 0.70 at step 200, eval 0.89. kl maps: train 1.2–1.5, eval 1.5–1.7. That points to over-fitting of the full-rank d_S×d_T correction on 65k tokens.
* **Fix.** Use the matched seed-0 base (1.597, not the pooled 1.587). Say "200-step/512-seq maps are 14–17% worse than 600-step/1024-seq maps", not "under-trained by 15%".

**R9. H-self FLOPs and statistics (MINOR to MAJOR for C8).**
* **Who is right.** `block_flops_per_token`: 410m block = 25.4 MFLOP; 70m block = 6.4 MFLOP. So 70m costs 6 × 0.2526 = **1.52 target blocks**.
  * A6 is right about 1.5 blocks. It is wrong that self:2 is "FLOP-matched".
  * 70m sits between self:1 (−0.5 block) and self:2 (+0.5 block).
  * The table's totals are within ±2% because the T head (103 MFLOP ≈ 4 blocks) and the upper blocks dominate. "Matched" is trivially true, and neither framing is wrong as such.
* **The prereg prediction at k=12 is not confirmed.**
  * The table compares single-seed self:1 with pooled 70m.
  * Paired at seed 0, self:1 vs 70m at k=12: 0.039 [−0.018, 0.092], so not confirmed.
  * At k=6: 0.84 [0.77, 0.92], confirmed.
  * self:2 vs 70m at k=12: 0.27 [0.22, 0.32], at +0.5 block.
* **At k ≥ 18 the 70m stitch beats both self baselines.**
* **Fix.** Use paired, seed-matched comparisons. Report "self:1 cheaper and better at k=6; tie at k=12; self:2 better at k=12 at +2% FLOPs".

**R10. Single-position diagnostic (C6) is over-interpreted (MAJOR for C6).**
* **Scope.** n = 8 sequences × 15 positions, seed 0, k=12 only, no CI.
* **Results:** all-vs-single KL 1.70/1.00 (70m), 1.32/0.85 (160m), 0.98/0.59 (deduped), 1.04/0.68 (seed1). That is 34–41%.
* **Why it is not purely "context corruption".** With a single replacement, position t also reads T's *own correct* states at the other positions through attention, so T's computation partly supplies p_T. The maps were also trained in the all-positions regime.
* **Fix.** Call it "replacing all positions instead of one increases KL by 1.5–1.7× (exploratory, n=8)". Add CIs and more sequences, or drop the "~40% is corruption" wording.

**R11. C4 (dissociation) is fragile for CKA (MINOR to MAJOR).**
* **The 70m CKA argmax is within seed noise.** CKA by k is 0.245 / 0.312 / 0.202 / 0.329, so k=24 beats k=12 by 0.017. Pooled CKA at k=12 (kl cells) is 0.336, which would exceed 0.329.
* **R² is monotone and robust.** But R² and CKA at k=24 are dominated by T's massive pre-LN dimensions, which LN discards. "Similarity peaks at k=24" may reflect residual anisotropy rather than function.
* **The prereg criterion is met (2 of 3 pairs), but only descriptively.**
* **Fix.** Use multi-seed CKA, and similarity metrics computed after LN or whitening.

**R12. C5 calibration (MINOR).**
* Single seed, 200 steps, with an evident over-fit gap (train ≈ 0.70 vs eval 0.89 for 70m).
* KL(p_S‖q) 0.48–0.89 is an *upper bound* on the bottleneck.
* The near-identity of KL(p_T‖q) between the klsrc and kl maps (see R1) is unexplained and should be reported.

**R13. X3 CI ignores uncertainty in ᾱ_TF (MAJOR for one X3 sub-claim).**
* P1 is treated as fixed, but ᾱ_TF has CI [0.601, 0.650].
* At ᾱ = 0.601, the formula gives R = 2.478 (γ=8) and 2.308 (γ=4). That is e1 ≈ +0.3%.
* "Over-predicts 5–6% (CI excludes 0)" and "H0 holds at γ=2 only" are therefore not robust.
* The headline (the error is small) is, if anything, strengthened.
* **Fix.** Propagate ᾱ_TF uncertainty into e1.

**R14. Infrastructure (no threat).**
* **Thread counts 3/4 and flush_denormal.** These change float summation order at about 1e-6, against effects of ≥ 0.02.
* **Restart, OOM and stall.** The lost cells were re-run whole, and the eval hashes are consistent (`3f34b72b713e` / `36bef642cd3f` / `02ee1a65219a` for seeds 0/1/2).
* **Eval sets across seeds** are drawn from the same pool, so they may overlap by about 1 document. This is negligible.
* **Disclosed.** The budget cut (#24) and the loss of the 410m→1b arm are disclosed. No second-target D_k exists yet: only 160m→1b k=4 is done.

**R15. Generality (MINOR).**
* "Smaller sources" rests on one model instance each of 70m and 160m, and a single target. Seeds do not sample model instances.
* No "novel" claim should exceed N2 until R1 is resolved.

## Verdicts

| Claim | Verdict | Basis |
|---|---|---|
| C1 | **SUPPORTED WITH CAVEATS** as a fixed-budget (200-step) operational result; **UNCLEAR** as a claim about best affine maps / G(k) | R1–R6. The replication matches in kind but shares the R1 confound. |
| C2 | **SUPPORTED** | All Δ_k CIs < 0, including the 600-step cells (−0.55, −0.42). Sibling Δ>0 is falsified per the frozen rule. |
| C3 | **SUPPORTED WITH CAVEATS** | True at 200 steps only. At 600 steps the ratio is 1.49–1.62 (R7). |
| C4 | **SUPPORTED WITH CAVEATS** (descriptive) | R² robust; CKA argmax fragile; anisotropy confound (R11). |
| C5 | **SUPPORTED WITH CAVEATS** | An upper bound; single seed (R12). |
| C6 | **NOT SUPPORTED** as worded | R10 |
| C7 | **SUPPORTED WITH CAVEATS** | Steps and data are confounded (R8). |
| C8 | **SUPPORTED WITH CAVEATS** | Holds at k=6 only for self:1; tie at k=12 (R9). |
| C9 | **SUPPORTED WITH CAVEATS** (exploratory, n=1 per arm) | — |
| C10 | **SUPPORTED** (small error) | The "5–6% significant over-prediction" sub-claim is not robust (R13). |

**Overall decision: PRELIMINARY FINDING.** The interior-depth advantage for smaller sources is consistent across seeds and two implementations. But it has not been shown to survive converged maps, and the direction of the mse→kl trend makes that the decisive, inexpensive next experiment (R1).
