"""EXPLORATORY PILOT (not confirmatory). Small source S -> large target T injection at several depths.
Usage: python3 xscale/pilot.py S T n_fit n_eval seq_len"""
import sys, time, torch
sys.path.insert(0, ".")
from xscale.common import load, residuals, run_upper, make_sequences, n_layers, token_metrics
from xscale.ridge import RidgeAcc, apply

S_name, T_name = sys.argv[1], sys.argv[2]
n_fit, n_eval, T_len = int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
torch.manual_seed(0)
S, T = load(S_name), load(T_name)
LS, LT = n_layers(S), n_layers(T)
ks = sorted(set([1, 2, LT // 4, LT // 2, 3 * LT // 4, LT - 2, LT]))
fit = make_sequences("pile", n_fit, T_len, "fit", seed=0)
ev = make_sequences("pile", n_eval, T_len, "eval", seed=0)
t0 = time.time()
accS = {k: RidgeAcc(S.config.hidden_size, T.config.hidden_size) for k in ks}
accT0 = {k: RidgeAcc(T.config.hidden_size, T.config.hidden_size) for k in ks}
for i in range(0, n_fit, 8):
    b = fit[i:i + 8]
    RS, _ = residuals(S, b); RT, _ = residuals(T, b)
    for k in ks:
        accS[k].add(RS[LS][:, 1:], RT[k][:, 1:])
        accT0[k].add(RT[0][:, 1:], RT[k][:, 1:])
print(f"fit stats {time.time()-t0:.0f}s", flush=True)
RS, lS = residuals(S, ev); RT, lT = residuals(T, ev)
base = token_metrics(lT, lS, ev)
print(f"S alone: KL {base['kl'].mean():.3f} acc {base['acc'].mean():.3f} top1 {base['top1'].mean():.3f} ce {base['ce'].mean():.3f}")
ceT = token_metrics(lT, lT, ev)['ce'].mean()
print(f"T alone ce {ceT:.3f}")
for lam in [1e-3, 1e-2, 1e-1]:
    for k in ks:
        for tag, acc, X in [("S->T", accS[k], RS[LS]), ("T0->T", accT0[k], RT[0])]:
            W, bb = acc.solve(lam)
            H = apply(X, W, bb)
            H[:, 0] = RT[k][:, 0]  # constant BOS state
            mt = token_metrics(lT, run_upper(T, H, k), ev)
            rec = (base['ce'].mean() - mt['ce'].mean()) / (base['ce'].mean() - ceT)
            print(f"lam {lam:g} k {k:2d} {tag:6s} R2 {acc.train_r2(W, bb):.3f} KL {mt['kl'].mean():.3f} acc {mt['acc'].mean():.3f} "
                  f"top1 {mt['top1'].mean():.3f} ce {mt['ce'].mean():.3f} recov {rec:.2f}", flush=True)
print(f"total {time.time()-t0:.0f}s")
