"""Unit test: run_upper(R_k, k) must reproduce the full-model logits for every k."""
import sys, torch
sys.path.insert(0, ".")
from xscale.common import load, residuals, run_upper, make_sequences, n_layers

def main(name="70m"):
    m = load(name)
    ids = make_sequences("pile", 2, 64, "fit", seed=1)
    R, logits = residuals(m, ids)
    assert len(R) == n_layers(m) + 1
    worst = 0.0
    for k in range(n_layers(m) + 1):
        out = run_upper(m, R[k], k)
        worst = max(worst, (out - logits).abs().max().item())
    print(name, "max |diff| over k:", worst)
    assert worst < 1e-3, worst

if __name__ == "__main__":
    for n in sys.argv[1:] or ["70m", "160m"]:
        main(n)
    print("OK")
