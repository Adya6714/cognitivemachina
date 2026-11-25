#!/bin/bash
# R1 convergence check (docs/11_preregistration_R1.md), deviation D5: runs before the last 1b cell.
cd "$(dirname "$0")/.."
until [ -f results/E1/S160m_T1b_k8_kl_s0.json ]; do sleep 10; done
pkill -f queue_E1_fill.sh; sleep 1; pkill -f "run_cell.py --src S:160m --tgt 1b --k 16"
run() { out=results/E1/$1.json; shift; [ -f "$out" ] && return; python3 xscale/run_cell.py "$@" --out "$out" 2>&1 | grep -E "^(S:|self:)|Error|Traceback" >> logs/E1_queue.log; }
for pair in 70m 160m; do for k in 24 18; do
  run "S${pair}_T410m_k${k}_kl_s0_long" --src S:$pair --tgt 410m --k $k --obj kl --seed 0 --steps 600 --n_fit 1024
done; done
run "S160m_T1b_k16_kl_s0" --src S:160m --tgt 1b --k 16 --obj kl --seed 0
echo R1_DONE >> logs/E1_queue.log
