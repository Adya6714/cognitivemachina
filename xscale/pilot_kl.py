"""EXPLORATORY PILOT: affine map S_final -> T residual at layer k, trained by KL(p_T || p_stitched) through
frozen T blocks k..L. Initialised from the ridge solution. Usage: pilot_kl.py S T k steps"""
import sys, time, torch
sys.path.insert(0, ".")
from xscale.common import load, residuals, run_upper, make_sequences, n_layers, token_metrics
from xscale.ridge import RidgeAcc

S_name, T_name, k, steps = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
LR = float(sys.argv[5]) if len(sys.argv) > 5 else 1e-3
SRC = sys.argv[6] if len(sys.argv) > 6 else "ln"  # ln = S final-LayerNorm output; raw = pre-LN residual
torch.manual_seed(0)
torch.set_num_threads(4)
S, T = load(S_name), load(T_name)
for p in list(S.parameters()) + list(T.parameters()):
    p.requires_grad_(False)
LS = n_layers(S)
feat = (lambda R: S.gpt_neox.final_layer_norm(R[LS])) if SRC == "ln" else (lambda R: R[LS])
fit = make_sequences("pile", 256, 128, "fit", seed=0)
ev = make_sequences("pile", 32, 128, "eval", seed=0)
acc = RidgeAcc(S.config.hidden_size, T.config.hidden_size)
cache = []
for i in range(0, len(fit), 8):
    b = fit[i:i + 8]
    RS, _ = residuals(S, b); RT, lT = residuals(T, b)
    acc.add(feat(RS)[:, 1:], RT[k][:, 1:])
    cache.append((feat(RS), RT[k][:, :1].clone(), RT[k]))
    del RS, RT, lT
W0, b0 = acc.solve(1e-3)
mx, my, Cxx, _, vy = acc.centered()
sx = Cxx.diagonal().clamp_min(1e-8).sqrt().float(); sy = vy.clamp_min(1e-8).sqrt().float(); mx = mx.float()
M = torch.nn.Parameter(torch.zeros_like(W0)); c = torch.nn.Parameter(torch.zeros_like(b0))
opt = torch.optim.Adam([M, c], lr=LR)

def mapf(X):  # ridge solution + scale-aware correction
    return X @ W0 + b0 + (((X - mx) / sx) @ M / M.shape[0] ** 0.5 + c) * sy
RSe, lSe = residuals(S, ev); RTe, lTe = residuals(T, ev)

def evaluate():
    with torch.no_grad():
        H = mapf(feat(RSe)); H[:, 0] = RTe[k][:, 0]
        mt = token_metrics(lTe, run_upper(T, H, k), ev)
    return {m: round(float(v.mean()), 4) for m, v in mt.items()}

print("S alone", {m: round(float(v.mean()), 4) for m, v in token_metrics(lTe, lSe, ev).items()})
print("step 0", evaluate(), flush=True)
t0 = time.time()
with torch.enable_grad():
    for step in range(1, steps + 1):
        XS, h0, RTk = cache[step % len(cache)]
        with torch.no_grad():
            lpT = torch.log_softmax(run_upper(T, RTk, k), -1)
        H = mapf(XS)
        H = torch.cat([h0, H[:, 1:]], 1)
        lq = torch.log_softmax(run_upper(T, H, k), -1)
        loss = (lpT.exp() * (lpT - lq)).sum(-1)[:, 1:].mean()
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 25 == 0:
            print(f"step {step} train KL {loss.item():.3f} {time.time()-t0:.0f}s eval", evaluate(), flush=True)
