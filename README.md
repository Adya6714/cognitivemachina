# cognitivemachina — cross-scale state injection in Pythia

An autonomous research programme on AI inference and representation learning. Every claim in this repo is
labelled with an evidence category:
* established
* preliminary
* hypothesis
* reproduction
* negative/inconclusive

See `docs/` for the full trail.

## Main study (E1)
**Question.** When can a small model's internal state be injected into a larger model's frozen upper layers
and still be useful? The variables are:
* size ratio
* injection depth
* map objective
* representational vs functional correspondence

The models are Pythia 70m / 160m / 410m-deduped / 410m-seed1 feeding into 410m (plus 1b).

**Secondary study (X3).** How wrong is the i.i.d. speculative-decoding formula for a real 70m→410m drafter,
split into path-shift and dependence errors?

## Layout
| Path | Contents |
|---|---|
| `docs/00_decision_log.md` | Append-only decision log, including every deviation |
| `docs/01_candidate_questions.md` | 42 candidate questions (Stage 1) |
| `docs/02_literature_matrix.md` | Literature matrix and novelty audit (Stages 2–3) |
| `docs/03_theory.md` | Propositions and predictions |
| `docs/04_ranking.md` | Weighted ranking (Stage 4) |
| `docs/05_preregistration_E1.md` | Frozen E1 prereg plus amendments A1–A8 (A8 post-result, disclosed) |
| `docs/06_adversarial_review_design.md` | Design review (Agent 8) |
| `docs/07_preregistration_X3.md` | Frozen X3 prereg |
| `xscale/common.py` | Model loading, data windows, residual capture, exact upper-layer re-execution, metrics |
| `xscale/test_injection.py` | Unit test: re-injecting a model's own states reproduces its logits (max diff 0.0) |
| `xscale/run_cell.py` | One E1 cell: fit map (ridge / KL-trained affine), evaluate on Pile and WikiText |
| `xscale/queue_E1_v2.sh`, `queue_E1_A8.sh`, `queue_E1_fill.sh` | Resumable run queues (exact cell list) |
| `xscale/diag_single_pos.py` | A7 single-position diagnostic |
| `xscale/analyse_E1.py` | Preregistered statistics → `results/E1_summary.json`, `results/E1_tables.md` |
| `xscale/specdec_x3.py`, `xscale/analyse_X3.py` | X3 speculative sampling and analysis |
| `replication/` | Independent re-implementation (Agent 10): different code, target, data and seeds |
| `results/` | Raw per-cell JSON (per-sequence metrics, train logs, eval-set hashes) and summaries |
| `logs/` | Queue logs and pilot logs (pilots are exploratory; never reused as confirmatory data) |

## Reproduce
```bash
pip install -r requirements.txt
python3 xscale/test_injection.py
./xscale/queue_E1_v2.sh && ./xscale/queue_E1_A8.sh
python3 xscale/analyse_E1.py
python3 xscale/specdec_x3.py 48 96 && python3 xscale/analyse_X3.py
```
* **Compute:** everything ran on 4 CPU cores with 15 GB RAM and no GPU. A KL cell takes 6–25 minutes.
* **Downloads:** models and data come from the HuggingFace Hub:
  * EleutherAI/pythia-*
  * NeelNanda/pile-10k
  * Salesforce/wikitext
* **Fitted maps:** maps are saved to `runs/` (git-ignored, about 4–16 MB each) and are needed by `diag_single_pos.py`.
* **Seeds and data splits:**
  * Fit sequences: Pile docs 0–4999.
  * Eval sequences: Pile docs 5000–9999 and WikiText-103 test.
  * Seeds are fixed per cell, and every result JSON records the eval-set hash.
