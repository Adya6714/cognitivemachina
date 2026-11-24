"""EXPLORATORY PILOT: affine map S_final -> T residual at layer k, trained by KL(p_T || p_stitched) through
frozen T blocks k..L. Initialised from the ridge solution. Usage: pilot_kl.py S T k steps"""
import sys, time, torch
sys.path.insert(0, ".")
from xscale.common import load, residuals, run_upper, make_sequences, n_layers, token_metrics
from xscale.ridge import RidgeAcc

S_name, T_name, k, steps = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
torch.manual_seed(0)
S, T = load(S_name), load(T_name)
for p in list(S.parameters()) + list(T.parameters()):
    p.requires_grad_(False)
LS = n_layers(S)
fit = make_sequences("pile", 256, 128, "fit", seed=0)
ev = make_sequences("pile", 32, 128, "eval", seed=0)
acc = RidgeAcc(S.config.hidden_size, T.config.hidden_size)
cache = []
for i in range(0, len(fit), 8):
    b = fit[i:i + 8]
    RS, _ = residuals(S, b); RT, lT = residuals(T, b)
    acc.add(RS[LS][:, 1:], RT[k][:, 1:])
    cache.append((RS[LS], RT[k][:, :1].clone(), torch.log_softmax(lT, -1)))
W0, b0 = acc.solve(1e-3)
W = torch.nn.Parameter(W0.clone()); bb = torch.nn.Parameter(b0.clone())
opt = torch.optim.Adam([W, bb], lr=1e-4)
RSe, lSe = residuals(S, ev); RTe, lTe = residuals(T, ev)

def evaluate():
    with torch.no_grad():
        H = RSe[LS] @ W + bb; H[:, 0] = RTe[k][:, 0]
        mt = token_metrics(lTe, run_upper(T, H, k), ev)
    return {m: round(float(v.mean()), 4) for m, v in mt.items()}

print("S alone", {m: round(float(v.mean()), 4) for m, v in token_metrics(lTe, lSe, ev).items()})
print("step 0", evaluate(), flush=True)
t0 = time.time()
with torch.enable_grad():
    for step in range(1, steps + 1):
        XS, h0, lpT = cache[step % len(cache)]
        H = XS @ W + bb
        H = torch.cat([h0, H[:, 1:]], 1)
        lq = torch.log_softmax(run_upper(T, H, k), -1)
        loss = (lpT.exp() * (lpT - lq)).sum(-1)[:, 1:].mean()
        opt.zero_grad(); loss.backward(); opt.step()
        if step % 25 == 0:
            print(f"step {step} train KL {loss.item():.3f} {time.time()-t0:.0f}s eval", evaluate(), flush=True)
