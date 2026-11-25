#!/bin/bash
# Decision 24: budget cut of the 1b arm (prereg budget rule). Wait for the running 160m->1b k4 cell, stop queue v2
# before it starts the next 1b cell, and reduce v2's 1b arm to 160m->1b k8,k16 (run later by the fill queue, after A8).
cd "$(dirname "$0")/.."
until [ -f results/E1/S160m_T1b_k4_kl_s0.json ]; do sleep 10; done
pkill -f queue_E1_v2.sh; sleep 1; pkill -f "run_cell.py --src S:[0-9a-z-]* --tgt 1b"
sed -i 's|^for pair in "160m" "410m"; do for k in 4 8 12 16; do run "S${pair}_T1b_k${k}_kl_s0".*$|# Decision 24 (budget cut): reduced to 160m->1b k4,8,16; 410m->1b and k12 dropped.\nfor k in 4 8 16; do run "S160m_T1b_k${k}_kl_s0" --src S:160m --tgt 1b --k $k --obj kl --seed 0; done|' xscale/queue_E1_v2.sh
rm -f logs/progress_S160m_T1b_k8_kl_s0.txt
echo "budget cut applied $(date -u)" >> logs/budget_cut.log
