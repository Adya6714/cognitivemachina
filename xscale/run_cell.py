"""Confirmatory cell runner (E1). One cell = (source, target, injection depth k, map objective, seed).

Source specs:
  S:<model>      small/other model, feature = its final-LayerNorm output (what its own head reads)
  self:<m>       the target model's own residual R_m (a cheaper prefix of the target itself)
Objectives:
  mse  ridge regression onto the target residual R_k (closed form, lambda_rel = 1e-3)
  kl   ridge initialisation + scale-aware affine correction trained on KL(p_T || p_stitched)
       through the frozen target blocks k..L (Adam, lr 3e-3, batch 8 x 128 tokens)
Outputs JSON with: per-sequence mean metrics for stitched / source-alone / target, held-out R^2 of the
*cell's own map* (ridge for mse cells, trained map for kl cells — representational analyses use mse cells),
linear CKA (map-free) and FLOP accounting. Maps are saved to runs/E1/<cell>.pt.
"""
from __future__ import annotations

import argparse
import os
import sys
import time

import torch

sys.path.insert(0, ".")
from xscale.common import (block_flops_per_token, head_flops_per_token, load, make_sequences, n_layers,
                           residuals, run_upper, save_json, seq_hash, token_metrics)
from xscale.ridge import RidgeAcc

p = argparse.ArgumentParser()
p.add_argument("--src", required=True)
p.add_argument("--tgt", required=True)
p.add_argument("--k", type=int, required=True)
p.add_argument("--obj", choices=["mse", "kl", "id"], required=True)  # id = identity map (equal widths only; amendment A3)
p.add_argument("--train_to", choices=["target", "source"], default="target")  # source = read-out calibration (amendment A1)
p.add_argument("--seed", type=int, default=0)
p.add_argument("--n_fit", type=int, default=512)
p.add_argument("--n_eval", type=int, default=64)
p.add_argument("--seq", type=int, default=128)
p.add_argument("--steps", type=int, default=200)
p.add_argument("--lr", type=float, default=3e-3)
p.add_argument("--out", required=True)
a = p.parse_args()

torch.manual_seed(a.seed)
torch.set_num_threads(int(os.environ.get("E1_THREADS", "4")))  # D4: 3 threads avoids oversubscription stalls when another job shares the 4 cores
torch.set_flush_denormal(True)  # deviation D4: guard against denormal slowdowns (affects only |x| < 1e-38)
t_start = time.time()
T = load(a.tgt)
LT = n_layers(T)
assert 0 <= a.k <= LT
for q in T.parameters():
    q.requires_grad_(False)

if a.src.startswith("S:"):
    S = load(a.src[2:])
    for q in S.parameters():
        q.requires_grad_(False)
    LS = n_layers(S)

    def source(ids, RT=None):
        R, logits = residuals(S, ids)
        return S.gpt_neox.final_layer_norm(R[LS]), logits
    src_flops = LS * block_flops_per_token(S, a.seq)  # source head is not used by the stitch (amendment A6)
else:
    m = int(a.src.split(":")[1])
    assert m < a.k

    def source(ids, RT):
        return RT[m], None
    src_flops = m * block_flops_per_token(T, a.seq)

stitch_flops = src_flops + (LT - a.k) * block_flops_per_token(T, a.seq) + head_flops_per_token(T)
target_flops = LT * block_flops_per_token(T, a.seq) + head_flops_per_token(T)

fit = make_sequences("pile", a.n_fit, a.seq, "fit", seed=a.seed)
evs = {"pile": make_sequences("pile", a.n_eval, a.seq, "eval", seed=100 + a.seed),
       "wiki": make_sequences("wiki", a.n_eval, a.seq, "eval", seed=100 + a.seed)}

# ---- fit statistics (+ cache for KL training)
acc = None
cache = []
B = 8
for i in range(0, a.n_fit, B):
    ids = fit[i:i + B]
    RT, _ = residuals(T, ids)
    X, _ = source(ids, RT)
    if acc is None:
        acc = RidgeAcc(X.shape[-1], RT[a.k].shape[-1])
    acc.add(X[:, 1:], RT[a.k][:, 1:])
    if a.obj == "kl":
        cache.append((X.clone(), RT[a.k].clone(), ids))
    del RT
W0, b0 = acc.solve(1e-3)
mx, my, Cxx, _, vy = acc.centered()
sx = Cxx.diagonal().clamp_min(1e-8).sqrt().float(); sy = vy.clamp_min(1e-8).sqrt().float(); mx = mx.float()
M = torch.nn.Parameter(torch.zeros_like(W0)); c = torch.nn.Parameter(torch.zeros_like(b0))


def mapf(X):
    return X @ W0 + b0 + (((X - mx) / sx) @ M / M.shape[0] ** 0.5 + c) * sy


train_log = []
if a.obj == "kl":
    opt = torch.optim.Adam([M, c], lr=a.lr)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, a.steps)
    g = torch.Generator().manual_seed(a.seed)
    with torch.enable_grad():
        for step in range(1, a.steps + 1):
            X, RTk, ids_b = cache[int(torch.randint(len(cache), (1,), generator=g))]
            with torch.no_grad():
                lp = torch.log_softmax(run_upper(T, RTk, a.k) if a.train_to == "target" else source(ids_b)[1], -1)
            H = mapf(X)
            H = torch.cat([RTk[:, :1], H[:, 1:]], 1)
            lq = torch.log_softmax(run_upper(T, H, a.k), -1)
            loss = (lp.exp() * (lp - lq)).sum(-1)[:, 1:].mean()
            if step == 1:
                train_log.append((0, round(loss.item(), 4)))  # pre-update loss (amendment A4)
            opt.zero_grad(); loss.backward(); opt.step(); sched.step()
            if step % 25 == 0:
                train_log.append((step, round(loss.item(), 4)))
                with open("logs/progress_" + os.path.basename(a.out).replace(".json", ".txt"), "a") as pf:
                    pf.write(f"step {step} loss {loss.item():.4f} t {time.time() - t_start:.0f}s\n")
    del cache
if a.obj == "id":
    assert W0.shape[0] == W0.shape[1]
    mapf = lambda X: X  # noqa: E731


# ---- evaluation
def linear_cka(X, Y):
    X = X - X.mean(0); Y = Y - Y.mean(0)
    xy = (X.T @ Y).norm() ** 2
    return float(xy / ((X.T @ X).norm() * (Y.T @ Y).norm()))


result = dict(args=vars(a), flops=dict(source=src_flops, stitched=stitch_flops, target=target_flops),
              train_log=train_log, fit_hash=seq_hash(fit), eval={})
for name, ev in evs.items():
    per = {"stitched": {}, "source": {}, "target": {}}
    Xs, Ys, Ps = [], [], []
    for i in range(0, a.n_eval, B):
        ids = ev[i:i + B]
        RT, lT = residuals(T, ids)
        X, lS = source(ids, RT)
        with torch.no_grad():
            H = mapf(X); H[:, 0] = RT[a.k][:, 0]
            lq = run_upper(T, H, a.k)
        Xs.append(X[:, 1:].reshape(-1, X.shape[-1])); Ys.append(RT[a.k][:, 1:].reshape(-1, RT[a.k].shape[-1]))
        Ps.append(H[:, 1:].reshape(-1, H.shape[-1]))
        n_pos = ids.shape[1] - 2
        if lS is not None:
            per["stitched"].setdefault("kl_to_source", []).extend(token_metrics(lS, lq, ids)["kl"].view(-1, n_pos).mean(1).tolist())
        for tag, lg in [("stitched", lq), ("source", lS), ("target", lT)]:
            if lg is None:
                continue
            mt = token_metrics(lT, lg, ids)
            for key, v in mt.items():
                per[tag].setdefault(key, []).extend(v.view(-1, n_pos).mean(1).tolist())
    X = torch.cat(Xs); Y = torch.cat(Ys); P = torch.cat(Ps)
    resid = ((Y - P) ** 2).sum() ; tot = ((Y - Y.mean(0)) ** 2).sum()
    sub = torch.randperm(X.shape[0], generator=torch.Generator().manual_seed(0))[:4000]
    result["eval"][name] = dict(per_seq={k2: v for k2, v in per.items() if v},
                                r2_heldout=float(1 - resid / tot),
                                cka=linear_cka(X[sub].double(), Y[sub].double()),
                                eval_hash=seq_hash(ev))
result["seconds"] = round(time.time() - t_start, 1)
save_json(result, a.out)
os.makedirs("runs/E1", exist_ok=True)  # maps saved for post-hoc diagnostics (amendment A4)
torch.save(dict(W0=W0, b0=b0, M=M.detach(), c=c.detach(), mx=mx, sx=sx, sy=sy, obj=a.obj),
           os.path.join("runs/E1", os.path.basename(a.out).replace(".json", ".pt")))
pe = result["eval"]["pile"]["per_seq"]
mean = lambda v: sum(v) / len(v)
print(a.src, "->", a.tgt, "k", a.k, a.obj, "seed", a.seed,
      "| KL stitched %.3f" % mean(pe["stitched"]["kl"]),
      ("| KL source %.3f" % mean(pe["source"]["kl"])) if pe.get("source") else "",
      "| R2 %.3f CKA %.3f" % (result["eval"]["pile"]["r2_heldout"], result["eval"]["pile"]["cka"]),
      "| %ss" % result["seconds"], flush=True)
