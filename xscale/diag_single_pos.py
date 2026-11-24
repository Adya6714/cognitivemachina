"""Amendment A7 (review issue 9): separate per-token representational mismatch from attention-context
corruption. For a saved map, compare at the same positions:
  all-positions stitch : every position's R_k replaced by the mapped source state (the E1 setting)
  single-position stitch: only position t replaced; all other positions keep the target's own R_k
Metric: KL(p_T || q) at position t. Usage: diag_single_pos.py <cell-name> [n_seq] [stride]"""
import json
import os
import re
import sys

import torch

sys.path.insert(0, ".")
from xscale.common import load, make_sequences, n_layers, residuals, run_upper, save_json

name = sys.argv[1]
n_seq = int(sys.argv[2]) if len(sys.argv) > 2 else 8
stride = int(sys.argv[3]) if len(sys.argv) > 3 else 8
torch.set_num_threads(4)
m = re.match(r"S(?P<src>[\w.\-]+?)_T(?P<tgt>[\w.]+)_k(?P<k>\d+)_(?P<obj>\w+?)_s(?P<seed>\d)", name)
src, tgt, k, seed = m["src"], m["tgt"], int(m["k"]), int(m["seed"])
mp = torch.load(f"runs/E1/{name}.pt")
S, T = load(src), load(tgt)
LS = n_layers(S)


def mapf(X):
    if mp["obj"] == "id":
        return X
    return X @ mp["W0"] + mp["b0"] + (((X - mp["mx"]) / mp["sx"]) @ mp["M"] / mp["M"].shape[0] ** 0.5 + mp["c"]) * mp["sy"]


ev = make_sequences("pile", n_seq, 128, "eval", seed=100 + seed)
positions = list(range(stride, 127, stride))
kl_all, kl_single = [], []
for i in range(n_seq):
    ids = ev[i:i + 1]
    RT, lT = residuals(T, ids)
    RS, _ = residuals(S, ids)
    X = S.gpt_neox.final_layer_norm(RS[LS])
    H = mapf(X); H[:, 0] = RT[k][:, 0]
    lp = torch.log_softmax(lT[0], -1)
    lq_all = torch.log_softmax(run_upper(T, H, k)[0], -1)
    Hs = RT[k].repeat(len(positions), 1, 1)
    for j, t in enumerate(positions):
        Hs[j, t] = H[0, t]
    lq_s = torch.log_softmax(run_upper(T, Hs, k), -1)
    for j, t in enumerate(positions):
        kl_all.append(float((lp[t].exp() * (lp[t] - lq_all[t])).sum()))
        kl_single.append(float((lp[t].exp() * (lp[t] - lq_s[j, t])).sum()))
res = dict(cell=name, n_seq=n_seq, positions=positions, kl_all=kl_all, kl_single=kl_single,
           mean_all=sum(kl_all) / len(kl_all), mean_single=sum(kl_single) / len(kl_single))
save_json(res, f"results/E1_diag/{name}_singlepos.json")
print(name, "KL all-positions %.3f | single-position %.3f | n=%d" % (res["mean_all"], res["mean_single"], len(kl_all)))
