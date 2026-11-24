# Research decision log (append-only)

| # | Date (UTC) | Decision | Reason | Alternatives rejected |
|---|---|---|---|---|
| 1 | 2026-11-24 | Audit compute first: 4 CPU cores, 15 GB RAM, no GPU | Tractability must be judged against real resources | — |
| 2 | 2026-11-24 | Searched for the "research notebook" (repos, Google Drive). Not found; the Drive file titled "Research Notebook" concerns volatility-surface diffusion. Use H1–H3 as stated in the brief | Do not invent notebook content | Reconstructing notebook contents from memory |
| 3 | 2026-11-24 | Audited user's prior repos: `novel_discovery` (CoT read-vs-recompute in toy transformers — done), `computational_reasoning` (RC Paper 1: error propagation — in progress by PI), `retrieval-vs-computation`, `reasoning-reliability` (Q1 state loss — design), `JEPA` (CLIP I→T alignment). Exclude D1, D2 and closely overlapping questions from candidacy | Avoid duplicating the PI's own work | — |
| 4 | 2026-11-24 | New personal cloud environment `cognitivemachina` allowing HuggingFace + arXiv/OpenAlex/S2/Crossref | Open-weight models and primary literature are needed; previous programme was blocked from HF | API-only behavioural work |
| 5 | 2026-11-24 | Model family for any cross-scale work: Pythia (70m–1.4b) | Shared tokenizer, shared data order, public checkpoints; fits CPU | Qwen/SmolLM (different tokenizers across sizes would confound cross-scale maps) |
| 6 | 2026-11-24 | Build reversible infrastructure + exploratory pilots for A1 while the prior-art audit runs; label everything **PILOT/EXPLORATORY**; no confirmatory runs before novelty audit and preregistration | Pilots tell us if a measurement is viable and what it costs; preregistration after pilots is standard as long as pilot data are not reused as confirmatory | Waiting idle; selecting A1 before the audit |
| 7 | 2026-11-24 | Unit test: upper-block re-execution from captured residuals reproduces logits exactly (max diff 0.0 for 70m, 410m) | Injection mechanism must be exact before any claim | — |
| 8 | 2026-11-24 | Pilot P1 (70m→410m, ridge/MSE maps, 4k eval tokens): injection worse than small model alone at every depth; functional optimum interior (k≈18) while R² argmax at final layer | Motivates a functional (KL-trained) map control — the MSE objective is a confound | Concluding "H1 false" from MSE maps alone |
