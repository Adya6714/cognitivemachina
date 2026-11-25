# Independent replication of cross-scale stitching (Agent 10)

Separate implementation; nothing under `xscale/` or `results/` was read or imported.

* `stitch_rep.py` — one cell (source, target, depth k, fit seed). Builds data, runs the injection unit
  test, fits the affine map (ridge init + Adam on KL through T's frozen upper blocks), evaluates on
  WikiText-103 validation and Pile-10k docs with index >= 5000, writes per-sequence metrics as JSON.
* `run_queue.sh "k1 k2 ..." SEED` — runs cells strictly sequentially (`nice -n 19`, 1 thread).
* `pilot.sh` — learning-rate pilot (fit seed 99, training loss only; `logs/pilot_lr.log` = abandoned RMS(W)-scaled parametrisation, `logs/pilot_lr2.log` = final sigma-parametrisation; pilot.sh as committed is the second one).
* `analyze.py [PREFIX]` — tables + paired bootstrap CIs; writes `results/summary_<PREFIX>.json`.
* `results/*.json` — raw per-sequence results; `logs/` — per-cell logs; `REPORT.md` — the report.

Reproduce: `./run_queue.sh "12 6 3 9" 7; ./run_queue.sh "12 9" 8; python analyze.py`.
