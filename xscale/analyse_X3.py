"""Analysis for X3 (prereg docs/07_preregistration_X3.md). Writes results/X3_summary.json and results/X3_tables.md."""
import json, sys
import numpy as np
sys.path.insert(0, ".")
from xscale.common import save_json

d = json.load(open("results/X3/specdec_70m_410m.json"))
rng = np.random.default_rng(777); NB = 10000
f = lambda a, g: (1 - a ** (g + 1)) / (1 - a)
a_tf = d["alpha_tf_mean"]
tf_seq = np.array(d["alpha_tf_seq"])
tf_ci = np.percentile([tf_seq[rng.integers(0, len(tf_seq), len(tf_seq))].mean() for _ in range(NB)], [2.5, 97.5])
out = dict(alpha_tf=a_tf, alpha_tf_ci_seqboot=tf_ci.tolist(), gamma={})
rows = []
for g, gd in d["gamma"].items():
    g = int(g); per = gd["per_prompt"]
    tok = [np.array(p["acc"]) + 1 for p in per]          # committed tokens per call, per prompt
    a1 = [np.array(p["a1"]) for p in per]                 # alpha at first drafted position
    acc1 = [(np.array(p["acc"]) >= 1).astype(float) for p in per]  # first draft accepted?
    # lag-1 dependence: P(accept 2nd | accept 1st) vs alpha at 2nd position (conditional expectation)
    n = len(per)

    def stats(idx):
        T = np.concatenate([tok[i] for i in idx]); A1 = np.concatenate([a1[i] for i in idx])
        C1 = np.concatenate([acc1[i] for i in idx])
        R = T.mean(); ap = A1.mean()
        return R, f(a_tf, g), f(ap, g), ap, C1.mean()

    R, P1, P2, ap, c1 = stats(range(n))
    bs = np.array([stats(rng.integers(0, n, n)) for _ in range(NB)])
    e1 = (bs[:, 1] - bs[:, 0]) / bs[:, 0]; e2 = (bs[:, 2] - bs[:, 0]) / bs[:, 0]
    ci = lambda x: np.percentile(x, [2.5, 97.5]).tolist()
    # direct dependence probe: among steps where pos1 accepted, compare realised acceptance at pos2 with mean alpha at pos2
    a2, c2 = [], []
    for p in per:
        for acc, al in zip(p["acc"], p["alphas"]):
            if acc >= 1 and len(al) >= 2:
                a2.append(al[1]); c2.append(float(acc >= 2))
    r = dict(R=R, R_ci=ci(bs[:, 0]), P1=P1, P2=P2, e1=(P1 - R) / R, e1_ci=ci(e1), e2=(P2 - R) / R, e2_ci=ci(e2),
             alpha_path=ap, alpha_path_ci=ci(bs[:, 3]), validity_first_accept_rate=c1, validity_ci=ci(bs[:, 4]),
             n_steps=int(sum(len(t) for t in tok)), cond_alpha2_mean=float(np.mean(a2)) if a2 else None,
             cond_accept2_rate=float(np.mean(c2)) if c2 else None, seconds=gd["seconds"])
    r["H_X3a_|e1|>0.10"] = bool(r["e1_ci"][0] > 0.10 or r["e1_ci"][1] < -0.10)
    r["H_X3b_e2!=0"] = bool(r["e2_ci"][0] > 0 or r["e2_ci"][1] < 0)
    r["H0_accurate_within_5pct"] = bool(r["e1_ci"][0] > -0.05 and r["e1_ci"][1] < 0.05)
    out["gamma"][g] = r
    rows.append(f"| {g} | {R:.3f} [{r['R_ci'][0]:.3f}, {r['R_ci'][1]:.3f}] | {P1:.3f} | {P2:.3f} | {r['e1']:+.3f} [{r['e1_ci'][0]:+.3f}, {r['e1_ci'][1]:+.3f}] "
                f"| {r['e2']:+.3f} [{r['e2_ci'][0]:+.3f}, {r['e2_ci'][1]:+.3f}] | {ap:.3f} | {c1:.3f} [{r['validity_ci'][0]:.3f}, {r['validity_ci'][1]:.3f}] | {r['n_steps']} |")
save_json(out, "results/X3_summary.json")
md = [f"# X3 results (single sampling seed per γ; {d['n_prompts']} prompts × {d['new_tokens']} tokens)", "",
      f"Teacher-forced ᾱ_TF = {a_tf:.4f} (95% CI over sequences {tf_ci[0]:.4f}–{tf_ci[1]:.4f})", "",
      "| γ | realised tokens/call R | P1 (ᾱ_TF) | P2 (ᾱ_path) | e1 total | e2 dependence | ᾱ_path | validity: first-draft accept rate (should ≈ ᾱ_path) | steps |",
      "|---|---|---|---|---|---|---|---|---|"] + rows
open("results/X3_tables.md", "w").write("\n".join(md) + "\n")
print("\n".join(md)); print(json.dumps({g: {k: v for k, v in r.items() if k.startswith("H")} for g, r in out["gamma"].items()}))
