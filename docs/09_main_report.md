# Main report (D3) — DRAFT: sections marked ⟨PENDING⟩ wait for the remaining E1 cells, review and replication

## 1. Title
Where a smaller model's state is usable inside a larger model: depth, size ratio and objective in
cross-scale stitching of Pythia models.

## 2. Abstract
⟨PENDING — written last, from verified numbers only.⟩

## 3. Scientific background
* **Starting hypotheses.** The programme began from three hypotheses:
  * H1: a small model can predict representations of a larger model that the larger model can use.
  * H2: latent-space prediction can accelerate inference while keeping the target's output guarantees.
  * H3: adaptive computation improves the reliability/latency/cost trade-off.
* **Model stitching.** Bansal et al. 2021 and Chen et al. 2025 (arXiv 2506.06609) operationalise "usable
  representation": an affine map feeds one network's activations into another network's later layers, and
  the composite's behaviour is measured.
* **Speculative decoding.** Leviathan et al. 2023 and Chen et al. 2023 show that any drafter verified by
  exact rejection sampling preserves the target distribution. So the "guarantee" part of H2 holds
  automatically (`03_theory.md`, Prop. 3), and only efficiency is open.
* **Representational similarity.** CKA and R² are widely used as proxies for shared function. Whether high
  similarity implies functional interchangeability is contested.

## 4. Precise research question
* **The question.** For Pythia models sharing a tokenizer and training-data order, when does affinely mapping
  a source model S's final state into a target model T's residual stream at depth k, then running T's frozen
  blocks k..L, give a distribution closer to p_T than both of these?
  1. A purely linear read-out of S through T's head (k = L). This is the H1 test, D_k.
  2. S's own distribution. This is the practical drafting test, Δ_k.
* **Factors varied:**
  * size ratio
  * depth
  * map objective
* **Also asked:** does representational similarity locate the functional optimum?

## 5. Related work
Full matrix: `02_literature_matrix.md` (about 60 papers, retrieved and read in this session). The works
closest to ours are:
* **Chen, Merullo, Stolfo, Pavlick 2025 (2506.06609).** Stitching Pythia-70m L3 → 160m L4 with MSE maps
  gives CE 3.99 vs 3.14. They study a single depth and objective.
* **2608.09521.** Mid-depth cross-family injection into a frozen back model "works": 72–88% next-token
  agreement with trained adapters at depth 0.5.
* **2606.03280.** Pythia-160M L8 → 410M L16 replacement injection via a linear translator is destructive on
  multi-hop QA.
* **2603.18908.** Cross-family linear maps work only in the last 1–2 layers.
* **Speculative decoding:**
  * **Hidden-state drafters.** Tandem Transformers, EAGLE-1/2/3 (2503.01840) and HASS train drafters on
    target features. These are not frozen cross-scale stitches.

## 6. Research gap
* **The contradiction.** The 2026 literature directly contradicts itself on whether injected cross-model
  states are usable mid-depth.
* **Why it is unresolved.** Each paper changes several factors at once (depth, size ratio, map objective,
  metric). None separates "the source lacks information" from "an affine map cannot express it", and none
  uses a comparator that isolates the upper layers' contribution.
* **Our design.** A controlled factorial over these factors in one model family, using the D_k comparator,
  is new as a design (novelty audit: N2–N3).
* **What we do not claim.** We do not claim stitching itself, KL-trained maps, or CKA/R² dissociation in
  general as novel.

## 7. Hypotheses (frozen prereg `05_preregistration_E1.md` + amendments A1–A8)
* **H-ratio (frozen primary).** max_k Δ_k increases with size ratio.
  * Prediction: Δ < 0 for 70m → 410m at all k, and Δ > 0 for the equal-size sibling.
* **D_k (A1, co-primary for H1, adopted pre-result).** D_k = KL(p_T‖q_24) − KL(p_T‖q_k) > 0 for some k < L.
* **H-objective (descriptive).** The kl objective reduces KL relative to mse by more than 1.5× at k = 12.
* **H-dissociation (descriptive).** argmax_k CKA/R² ≠ argmin_k KL in at least 2 of 3 pairs.
* **H-self (H2 efficiency).** self-prefix stitches beat 70m at matched FLOPs.
* **Competing hypotheses:**
  * **C-info.** The small model lacks the information. This is ruled out a priori by Prop. 1 (injectivity),
    so any gap is computational accessibility.
  * **C-readout.** Stitches fail only because the affine map plus T's head cannot express p_S at all. This
    is tested by A1 calibration cells.
  * **C-data.** The size-ratio effect is a training-data effect. This is tested by A2 (410m-seed1: same data,
    different seed) vs the 410m-deduped sibling.
  * **C-init.** Equal-size pairs share coordinates through a shared initialisation. This is tested by A3
    identity stitches.
  * **C-context.** The failure comes from corrupting attention context, not per-token mismatch. This is
    tested by the A7 single-position diagnostic.
  * **C-undertrain.** KL maps are under-trained. This is tested by 600-step / n_fit = 1024 convergence cells.

## 8. Methodology
* **Exact injection.** The model's own ModuleList is sliced and the injected states are passed as
  inputs_embeds.
  * Unit test: re-injecting a model's own states reproduces its logits with max |diff| = 0.0
    (`xscale/test_injection.py`).
* **Maps:**
  * mse: ridge onto R_k.
  * kl: ridge initialisation plus a scale-aware affine correction trained on KL(p_T‖q) through T's frozen
    upper blocks (200 Adam steps, lr 3e-3, cosine, batch 8 × 128, n_fit = 512).
  * Position 0 (BOS) copies T's state.
* **Metrics.** The following are computed over positions 1..126:
  * KL(p_T‖q)
  * 1 − TV (= one-token speculative acceptance)
  * top-1 agreement
  * CE
  * held-out R² and linear CKA (taken from mse cells)
* **Statistics.**
  * The unit is the evaluation sequence (64 per set).
  * Intervals use a seed-stratified bootstrap over sequences (10 000 resamples), with Holm correction plus
    unadjusted p-values.
  * Single-seed cells are labelled as such. Their CIs omit map-fit variance.
* **Validity guards:**
  * divergence rule (step-0 loss logged)
  * eval-set hashes
  * Pile fit and eval drawn from disjoint document pools
  * WikiText-103 as a domain-shift check

## 9. Experimental setup
* **Models.** EleutherAI Pythia:
  * 70m, 160m, 410m-deduped and 410m-seed1 (PolyPythias) as sources
  * 410m as the target
  * 1b as a second target (budget permitting)
* **Hardware and precision.** 4 CPU cores and 15 GB RAM, float32.
* **Data.** NeelNanda/pile-10k (fit docs 0–4 999, eval docs 5 000–9 999) and WikiText-103 test.
* **Decisions and deviations.** All are listed in `00_decision_log.md`:
  * D1: WikiText windows.
  * D3: reordering.
  * D4: CPU-oversubscription stall. The fix used 3 threads plus progress logs.
  * A8: post-result extra seeds, labelled post hoc.

## 10. Results ⟨PENDING⟩
## 11. Statistical analysis ⟨PENDING⟩
## 12. Ablations ⟨PENDING: objective, identity, self-prefix, single-position, convergence⟩
## 13. Competing explanations ⟨PENDING⟩
## 14. Adversarial review ⟨PENDING: Agent 8 results-stage review⟩
## 15. Independent replication ⟨PENDING: Agent 10, `replication/REPORT.md`⟩

## 16. Limitations (known now; to be extended)
* **Scale.** Small models only (≤ 1b), on CPU. Conclusions about frontier-scale drafting are not licensed.
* **Map class.** The map is affine and per-position, so failures are relative to this map class (Prop. 1).
* **Seeds.** Most cells are single-seed. The extra seeds cover only the key contrasts.
* **Training budget.** 200 steps, mitigated but not eliminated by the convergence cells.
* **Model family.** One family (Pythia) with a shared tokenizer and data order. Cross-family generality is
  untested.
* **Secondary study X3 (`08_results_X3.md`).** It found no large i.i.d.-formula error. That is a
  negative result, single-seed per γ.

## 17. Scientific implications ⟨PENDING⟩
## 18. Future research ⟨PENDING⟩
