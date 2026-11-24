#!/bin/bash
# Confirmatory E1 queue, in preregistered order. Resumable: skips cells whose JSON exists.
cd "$(dirname "$0")/.."
run() { out=results/E1/$1.json; shift; [ -f "$out" ] && return; python3 xscale/run_cell.py "$@" --out "$out" 2>&1 | grep -E "^(S:|self:)|Error|Traceback" >> logs/E1_queue.log; }
# 1. core grid seed 0
for pair in "70m" "160m" "410m-deduped"; do for k in 6 12 18 24; do for obj in mse kl; do
  run "S${pair}_T410m_k${k}_${obj}_s0" --src S:$pair --tgt 410m --k $k --obj $obj --seed 0; done; done; done
# 2. self baselines
for k in 6 12 18 24; do run "self1_T410m_k${k}_kl_s0" --src self:1 --tgt 410m --k $k --obj kl --seed 0; done
for k in 6 12 18 24; do run "self0_T410m_k${k}_mse_s0" --src self:0 --tgt 410m --k $k --obj mse --seed 0; done
run "self0_T410m_k6_kl_s0" --src self:0 --tgt 410m --k 6 --obj kl --seed 0
# 3. extra seeds
for s in 1 2; do for pair in "70m" "160m" "410m-deduped"; do run "S${pair}_T410m_k12_kl_s$s" --src S:$pair --tgt 410m --k 12 --obj kl --seed $s; done
  for pair in "70m" "410m-deduped"; do run "S${pair}_T410m_k24_kl_s$s" --src S:$pair --tgt 410m --k 24 --obj kl --seed $s; done; done
# 4. convergence check
run "S70m_T410m_k12_kl_s0_long" --src S:70m --tgt 410m --k 12 --obj kl --seed 0 --steps 600 --n_fit 1024
# 5. 1b replication arm
for pair in "160m" "410m"; do for k in 4 8 12 16; do run "S${pair}_T1b_k${k}_kl_s0" --src S:$pair --tgt 1b --k $k --obj kl --seed 0; done; done
echo QUEUE_DONE >> logs/E1_queue.log
