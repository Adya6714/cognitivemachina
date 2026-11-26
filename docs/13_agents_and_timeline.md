# Agents and timeline report

*Written 2026-11-26, 06:40 UTC. Times are UTC and come from the git history and `00_decision_log.md`.*

## Status right now
* **Nothing is running.** All compute finished on 2026-11-25 at 20:42 (79 E1 cells, X3, replication and R1).
* **All four subagents have finished.** None is still active.
* **All deliverables D1–D8 are complete and pushed** to `claude/research-programme`.
* **Pending, by choice or approval only:**
  * Any manuscript submission or public posting. It needs your explicit approval and has not been done.
  * The three recommended next experiments (D8). They are not started, because each extends the programme
    beyond the brief's budget.

---

## 1. The organisation: who existed and who did what

The brief defined a Research Director plus Agents 1–10. **Four separate subagent runs were spawned.** Each had
its own context, did not see the director's reasoning, and reported back once. The other roles were carried out
by the Research Director in the main session. They are listed here so they are not mistaken for independent work.

### 1a. Spawned subagents (independent)

| Agent | Role | Started → finished | Instructions / constraints | What it did | Output | Effect on the programme |
|---|---|---|---|---|---|---|
| **Agent 2** | Literature / prior-art investigator | 11-24 ~19:03 → ~19:20 | Cite only papers actually retrieved; assign novelty classes N0–N5 | Ran about 90 arXiv/OpenAlex queries plus forward-citation crawls; read about 60 papers, some only in targeted sections; built the literature matrix; graded each candidate's novelty | `docs/02_literature_matrix.md` | Found the 2026 contradiction (2608.09521 "works" vs 2606.03280 / 2603.18908 "fails"). This made X1 the top-ranked candidate. |
| **Agent 8 (1st instance)** | Adversarial reviewer, design stage | 11-24 ~20:24 → ~20:30 | Attack the frozen E1 design before any result exists | Found 18 issues (1 fatal, 10 major, 7 minor). The fatal one: the primary comparator Δ_k cannot test H1, because of a read-out bottleneck. | `docs/06_adversarial_review_design.md` | Amendments A1–A7, all adopted before any result: the D_k co-primary, the seed sibling, identity stitches, convergence cells, a FLOP fix, the single-position diagnostic, and statistics fixes. |
| **Agent 10** | Independent replication | 11-25 00:40 → 04:02 | New code from scratch; forbidden from reading `xscale/` or `results/`; different pair, data and seeds | Wrote `replication/stitch_rep.py`, unit-tested its injection (bit-exact), and ran 70m→160m with WikiText fit data and seeds 7–8 | `replication/REPORT.md` | C1 (interior D > 0) replicated at k = 9 of 12, D_9 = +0.254 [0.196, 0.320]. C2 (stitch worse than source) replicated at every k. |
| **Agent 8 (2nd, fresh instance)** | Adversarial reviewer, results stage | 11-25 17:39 → ~17:45 | Read-only; attack each of claims C1–C10 | Recomputed numbers from the raw JSON and raised 15 issues. Key: R1, that D_18 > 0 might be an under-training artefact. Others: R3 (CIs lacked seed variance), R4 (post-hoc seeds unlabelled), R9 (FLOP claim wrong), R10 (context decomposition invalid). | `docs/10_adversarial_review_results.md` | Led to the R1 convergence check (prereg `11`), seed-level CIs, narrower wording, and 3 claims withdrawn or downgraded. Verdict: PRELIMINARY FINDING. |

### 1b. Roles carried out by the Research Director, in the main session (not independent)

| Role (brief) | What was done | Output |
|---|---|---|
| Research Director | Overall strategy, decisions, approvals within the brief, final synthesis | `docs/00_decision_log.md` (27 entries) |
| Agent 1, Cartographer | 42 candidate questions across inference, representation, memory and reasoning | `docs/01_candidate_questions.md` |
| Agent 3, Theory | Props. 1–3: no information bottleneck; interior-minimum signature; acceptance = 1 − TV | `docs/03_theory.md` |
| Agent 4, Mech-interp | CKA/R² metrics; single-position diagnostic | `xscale/common.py`, `xscale/diag_single_pos.py` |
| Agent 5, Systems | FLOP accounting; KV-cached speculative sampler; infrastructure fixes | `xscale/specdec_x3.py`, deviation D4 |
| Agent 6, Memory | Candidate group C (memory / retrieval); none selected | `docs/01` |
| Agent 7, Experimental | Preregistrations, cell runner, queues, analysis | `docs/05`, `07`, `11`; `xscale/run_cell.py`, `analyse_E1.py` |
| Agent 9, Strategist | Weighted ranking with the brief's weights; top-10 landscape | `docs/04_ranking.md` |

---

## 2. Timeline

### Day 1: 2026-11-24 (Stages 1–6)

| Time | Who | Event |
|---|---|---|
| ~18:30 | Director | Compute audit: 4 CPU cores, 15 GB RAM, no GPU. Searched for the "research notebook" (not found). Audited the PI's prior repos to avoid duplicating their work. |
| ~18:45 | Director | Created a cloud environment allowing HuggingFace and arXiv. Chose the Pythia family. |
| 19:03 | **Agent 2 launched** | Prior-art audit runs in parallel. |
| 19:15 | Director | Candidate map (42), theory note, injection library. Exact-injection unit test passes (max diff 0.0). Pilots P1–P4 (exploratory). |
| 19:22 | **Agent 2 done** | Literature matrix and novelty classes. Ranking: X1 first (7.75), X3 second. |
| 20:19 | Director | E1 preregistration drafted. |
| 20:24 | Director | **E1 prereg FROZEN.** |
| 20:24 | **Agent 8 (design) launched** | — |
| 20:25 | Director | Deviation D1 (WikiText loader). |
| 20:32 | **Agent 8 done** → Director | Amendments A1–A7 adopted before any result. Queue v2 starts (core grid). |
| 20:56–23:59 | Queue | First confirmatory cells (70m, 160m grids). |

### Day 2: 2026-11-25 (Stages 7–10 and deliverables)

| Time | Who | Event |
|---|---|---|
| 00:15 | Queue | Core grid done for 160m and the siblings (seed 0). |
| 00:40 | Director | Interim analysis on 23 cells: Δ < 0 everywhere; D_18 > 0 for small sources. |
| 00:40 | **Agent 10 launched** | Independent replication, run concurrently at low priority. |
| 00:43 | Director | **Amendment A8 (post hoc, disclosed):** extra seeds at k = 18. An OOM kill (replication ran 2 jobs) loses 1 cell, so a fill queue is added. |
| 01:13 | Director | **X3 prereg frozen**. Speculative-sampling study launched. |
| 01:52 | Director | **X3 done: negative result** (the i.i.d. formula is accurate within about 6%). |
| ~02:00 | Queue | Cell stalls for more than 2 h. |
| 03:12 | Director | **Deviation D4:** diagnosed CPU oversubscription. Switched to 3 threads and added progress logs. |
| 03:53 | Director | Main report sections 1–9 and 16 drafted. |
| 04:02 | **Agent 10 done** | Replication: C1 and C2 replicate. |
| 04:32 | Director | Back to 4 threads. |
| 05:15 | Director | Study guide (interim, 33 cells). |
| 05:49–09:57 | Queue | Identity stitches, self-prefix baselines, A7 diagnostic, frozen seeds 1–2. |
| ~11:58 | Infrastructure | **Container restarted.** Queues killed; one partial cell lost. |
| 12:00 | Director | Queues relaunched (decision 23). |
| 13:31 | Queue | Lost cells re-run. Convergence: 70m k12 at 600 steps gives 1.379 (vs 1.587). |
| 15:31 | Queue | Deduped convergence cell. 1b cells cost about 1 h each. |
| 15:31 | Director | **Decision 24: budget cut** of the 1b arm (prereg rule). |
| 16:25–17:36 | Queue | A8 seeds 1–2 at k = 18. 70m D_18 holds across 3 seeds. |
| 17:39 | Director | Full analysis on 73 cells. |
| 17:39 | **Agent 8 (results) launched** | — |
| ~17:45 | **Agent 8 done** → Director | 15 issues. R1 convergence check preregistered (`11`) and queued first (deviation D5). Analysis gets seed-level CIs and seed-0-only tests. |
| 18:06 | Director | Leftover queue shells killed to avoid CPU contention. |
| 19:45 | Queue | R1: 70m D_18 at 600 steps = +0.121 [0.097, 0.144]. **Robust.** |
| 19:49–20:14 | Director | Figures 1–4; full main report (D3); D1/D2/D4/D5/D6/D8; D7 PDF (4 pages); study guide final section. |
| 20:23 | Queue / Director | R1: 160m D_18 at 600 steps = +0.071 [0.051, 0.090]. **Robust** (decision 26). |
| 20:42 | Queue / Director | Last 1b cell. 1b arm **inconclusive** (the decisive 3/4-depth cell had been cut). **All deliverables final** (decision 27). |

### Day 3: 2026-11-26
| Time | Event |
|---|---|
| 06:40 | This report. Nothing running. |

---

## 3. What each stage of the brief produced

| Stage | Done by | Output | Status |
|---|---|---|---|
| 1. ≥ 40 candidates | Director (Agent 1 role) | 42 candidates | ✅ |
| 2. Literature matrix | **Agent 2** | about 60 papers | ✅ |
| 3. Novelty audit N0–N5 | **Agent 2** + Director | Classes per candidate | ✅ |
| 4. Weighted ranking | Director (Agent 9 role) | Top-10 landscape | ✅ |
| 5. Competing hypotheses | Director + **Agent 8 (design)** | 6 competing explanations, each with a control | ✅ |
| 6. Preregistration | Director (Agent 7 role) | E1 (frozen + A1–A8), X3, R1 | ✅ |
| 7. Execute | Queues | 79 E1 cells, A7 diagnostic, X3 | ✅ |
| 8. Statistics | Director | Bootstrap, Holm, seed-level t CIs | ✅ |
| 9. Adversarial review | **Agent 8**, twice | Design review and results review | ✅ |
| 10. Independent replication | **Agent 10** | 70m→160m, separate code | ✅ |
| D1–D8 | Director | `09`, `12`, `report/executive_summary.pdf`, figures | ✅ |

## 4. Compute used
* **About 26 CPU-hours** of model runs on 4 cores:
  * 79 E1 cells
  * the replication, about 3.5 h single-thread
  * X3, about 0.5 h
* **Paid compute purchased:** none. **External submissions:** none.

## 5. Final outcome (one paragraph)
**PRELIMINARY FINDING.** For sources much smaller than the target (70m and 160m → Pythia-410m), the target's last
quarter of blocks reads out an affinely injected source state better than the target's head does. Evidence:
* robust across 3 seeds and two eval sets;
* robust to 3× longer map training;
* replicated by independent code.

Equal-size siblings never benefit. No stitch drafts better than the small model alone, so there is no speed-up.
The mechanism (extra frozen capacity vs something specific to the small model's state) and the transfer to the 1b
target are unresolved. The next three experiments are in `docs/12_final_deliverables.md` (D8).
