#!/bin/bash
# LR pilot on a separate fit seed (99); training-set loss only, no eval data touched.
cd /home/user/cognitivemachina/replication
for kr in "6 1e-4" "6 3e-4" "12 1e-4" "12 3e-4"; do set -- $kr
  echo "== k=$1 lr=$2"; nice -n 19 python stitch_rep.py --k $1 --seed 99 --steps 40 --lr $2 --n_eval 128 --no_eval --out /dev/null 2>&1 | grep -e step -e pilot -e Error
done
