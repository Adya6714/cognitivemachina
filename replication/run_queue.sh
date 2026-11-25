#!/bin/bash
# usage: run_queue.sh "k1 k2 ..." seed   -- strictly sequential
cd /home/user/cognitivemachina/replication
for k in $1; do
  out=results/S70m_T160m_k${k}_s$2.json
  [ -f $out ] && continue
  nice -n 19 python stitch_rep.py --k $k --seed $2 --steps 150 --lr 1e-4 --out $out > logs/S70m_T160m_k${k}_s$2.log 2>&1
done
