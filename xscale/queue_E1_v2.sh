#!/bin/bash
# E1 queue v2 = frozen cells + amendments A1-A7 (post-freeze, pre-result; see prereg "Amendments").
# Order changed to put the review-critical controls before the extra seeds (deviation D3). Resumable.
cd "$(dirname "$0")/.."
run() { out=results/E1/$1.json; shift; [ -f "$out" ] && return; python3 xscale/run_cell.py "$@" --out "$out" 2>&1 | grep -E "^(S:|self:)|Error|Traceback" >> logs/E1_queue.log; }
diag() { [ -f results/E1_diag/$1_singlepos.json ] && return; python3 xscale/diag_single_pos.py $1 8 8 2>&1 | grep -E "KL all|Error|Traceback" >> logs/E1_queue.log; }
# 1. core grid seed 0 (frozen)
for pair in "70m" "160m" "410m-deduped"; do for k in 6 12 18 24; do for obj in mse kl; do
  run "S${pair}_T410m_k${k}_${obj}_s0" --src S:$pair --tgt 410m --k $k --obj $obj --seed 0; done; done; done
# 2. A1 read-out calibration: k=24 map trained to reproduce the SOURCE's own distribution
for pair in "70m" "160m" "410m-deduped"; do run "S${pair}_T410m_k24_klsrc_s0" --src S:$pair --tgt 410m --k 24 --obj kl --train_to source --seed 0; done
# 3. A2 same-data different-seed equal-size control (PolyPythias)
for k in 6 12 18 24; do for obj in mse kl; do run "S410m-seed1_T410m_k${k}_${obj}_s0" --src S:EleutherAI/pythia-410m-seed1 --tgt 410m --k $k --obj $obj --seed 0; done; done
# 4. A3 identity stitches (no training)
for pair in "410m-deduped" "410m-seed1"; do for k in 12 24; do
  src=$pair; [ "$pair" = "410m-seed1" ] && src=EleutherAI/pythia-410m-seed1
  run "S${pair}_T410m_k${k}_id_s0" --src S:$src --tgt 410m --k $k --obj id --seed 0; done; done
# 5. self baselines (frozen) + A6 self:2 (FLOP-matched to the 70m source, ~1.5 target blocks)
for k in 6 12 18 24; do run "self1_T410m_k${k}_kl_s0" --src self:1 --tgt 410m --k $k --obj kl --seed 0; done
for k in 6 12 18 24; do run "self2_T410m_k${k}_kl_s0" --src self:2 --tgt 410m --k $k --obj kl --seed 0; done
for k in 6 12 18 24; do run "self0_T410m_k${k}_mse_s0" --src self:0 --tgt 410m --k $k --obj mse --seed 0; done
run "self0_T410m_k6_kl_s0" --src self:0 --tgt 410m --k 6 --obj kl --seed 0
# 6. A7 single-position diagnostic (k=12, kl, seed 0)
for c in S70m_T410m_k12_kl_s0 S160m_T410m_k12_kl_s0 S410m-deduped_T410m_k12_kl_s0 S410m-seed1_T410m_k12_kl_s0; do diag $c; done
# 7. extra seeds (frozen)
for s in 1 2; do for pair in "70m" "160m" "410m-deduped"; do run "S${pair}_T410m_k12_kl_s$s" --src S:$pair --tgt 410m --k 12 --obj kl --seed $s; done
  for pair in "70m" "410m-deduped"; do run "S${pair}_T410m_k24_kl_s$s" --src S:$pair --tgt 410m --k 24 --obj kl --seed $s; done; done
# 8. convergence checks (frozen 70m + A5 sibling)
run "S70m_T410m_k12_kl_s0_long" --src S:70m --tgt 410m --k 12 --obj kl --seed 0 --steps 600 --n_fit 1024
run "S410m-deduped_T410m_k12_kl_s0_long" --src S:410m-deduped --tgt 410m --k 12 --obj kl --seed 0 --steps 600 --n_fit 1024
# 9. 1b replication arm (frozen, budget permitting)
for pair in "160m" "410m"; do for k in 4 8 12 16; do run "S${pair}_T1b_k${k}_kl_s0" --src S:$pair --tgt 1b --k $k --obj kl --seed 0; done; done
echo QUEUE_DONE >> logs/E1_queue.log
