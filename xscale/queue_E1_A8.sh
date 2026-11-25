#!/bin/bash
# Amendment A8 (POST-RESULT, disclosed): seeds 1-2 for the cells that carry the D_k signal (k=18 vs k=24, kl).
# Added after the seed-0 D_k table was seen; results are labelled post hoc / exploratory-confirmation.
cd "$(dirname "$0")/.."
while pgrep -f queue_E1_v2 >/dev/null; do sleep 60; done
run() { out=results/E1/$1.json; shift; [ -f "$out" ] && return; python3 xscale/run_cell.py "$@" --out "$out" 2>&1 | grep -E "^(S:|self:)|Error|Traceback" >> logs/E1_queue.log; }
for s in 1 2; do
  for pair in "70m" "160m" "410m-deduped"; do run "S${pair}_T410m_k18_kl_s$s" --src S:$pair --tgt 410m --k 18 --obj kl --seed $s; done
  run "S160m_T410m_k24_kl_s$s" --src S:160m --tgt 410m --k 24 --obj kl --seed $s
done
echo A8_DONE >> logs/E1_queue.log
