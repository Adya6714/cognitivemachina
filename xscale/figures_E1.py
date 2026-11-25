"""Figures for the main report. Reads results/E1_summary.json and results/X3_summary.json (run analyse_E1.py first).
Usage: python3 xscale/figures_E1.py   -> figures/fig1_kl_by_depth.png, fig2_dk.png, fig3_dissociation.png, fig4_x3.png"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

os.makedirs("figures", exist_ok=True)
S = json.load(open("results/E1_summary.json"))
C = S["cells"]
SRC = ["70m", "160m", "410m-deduped", "410m-seed1"]
COL = {"70m": "#1f77b4", "160m": "#ff7f0e", "410m-deduped": "#2ca02c", "410m-seed1": "#9467bd"}
KS = [6, 12, 18, 24]
plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False})


def cell(src, k, obj="kl", long=False, tgt="410m"):
    return C.get(f"{src}|{tgt}|{k}|{obj}|{long}")


# ---- Fig 1: KL(p_T||q_k) by depth, kl maps (all seeds pooled), source-alone dashed, 600-step points
fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0))
for src in SRC:
    ks, m, lo, hi = [], [], [], []
    for k in KS:
        c = cell(src, k)
        if c:
            e = c["pile"]["stitched_kl"]; ks.append(k); m.append(e[0]); lo.append(e[0] - e[1]); hi.append(e[2] - e[0])
    ax[0].errorbar(ks, m, yerr=[lo, hi], marker="o", ms=4, capsize=2, color=COL[src], label=f"{src} stitch (kl map)")
    srcv = cell(src, 12)["pile"]["source_kl"][0]
    ax[0].axhline(srcv, ls=":", color=COL[src], lw=1)
    lk, lm = [], []
    for k in KS:
        c = cell(src, k, long=True)
        if c:
            lk.append(k); lm.append(c["pile"]["stitched_kl"][0])
    if lk:
        ax[0].plot(lk, lm, marker="*", ms=9, ls="--", lw=0.8, color=COL[src])
ax[0].set_xticks(KS); ax[0].set_xlabel("injection depth k in Pythia-410m (24 = linear read-out)")
ax[0].set_ylabel("KL(p_T ‖ q_k), Pile eval (nats/token)")
ax[0].set_title("Stitched KL by depth (dotted: source alone;\n★ dashed: 600-step maps)", fontsize=9)
# mse vs kl objective
for src in SRC:
    mk = [cell(src, k, "mse")["pile"]["stitched_kl"][0] for k in KS]
    ax[1].plot(KS, mk, marker="s", ms=3, color=COL[src], ls="-", label=src)
    kk = [cell(src, k)["pile"]["stitched_kl"][0] for k in KS if cell(src, k)]
    ax[1].plot([k for k in KS if cell(src, k)], kk, marker="o", ms=3, color=COL[src], ls=":", lw=1)
ax[1].set_xticks(KS); ax[1].set_xlabel("injection depth k"); ax[1].set_title("Objective: ridge/MSE map (solid)\nvs KL-trained map (dotted)", fontsize=9)
h, l = ax[1].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=4, fontsize=7, frameon=False, bbox_to_anchor=(0.5, -0.02))
fig.tight_layout(rect=(0, 0.06, 1, 1)); fig.savefig("figures/fig1_kl_by_depth.png", dpi=200); plt.close(fig)

# ---- Fig 2: D_k with seed-level t CI (or sequence CI for single seed), Pile and WikiText
fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.9), sharey=True)
w = 0.2
for j, ev in enumerate(["pile", "wiki"]):
    for i, src in enumerate(SRC):
        xs, ys, el, eh = [], [], [], []
        for t in S["tests"]["D_k"]:
            if t["src"] != src:
                continue
            if ev == "pile":
                est = t["est"]; ci = t.get("seed_t_ci", [t["lo"], t["hi"]])
            else:
                est = t["wiki"][0]; ci = t.get("wiki_seed_t_ci", t["wiki"][1:])
            xs.append(KS.index(t["k"]) + (i - 1.5) * w); ys.append(est); el.append(est - ci[0]); eh.append(ci[1] - est)
        ax[j].bar(xs, ys, w, yerr=[el, eh], capsize=2, color=COL[src], label=src)
    for t in S["tests"].get("D_k_extra", []):
        if "600" in t["label"] and t["k"] == 18:
            e = t["est_ci"] if ev == "pile" else t["wiki"]
            src = t["label"].split("→")[0]
            ax[j].plot(KS.index(18) + (SRC.index(src) - 1.5) * w, e[0], marker="*", ms=10, color="k")
    ax[j].axhline(0, color="k", lw=0.8)
    ax[j].set_xticks(range(3)); ax[j].set_xticklabels(["k=6", "k=12", "k=18"])
    ax[j].set_title(("Pile" if ev == "pile" else "WikiText-103") + ": D_k = KL(q_24) − KL(q_k)", fontsize=9)
ax[0].set_ylabel("D_k (> 0: injection beats linear read-out)")
ax[0].legend(fontsize=7, frameon=False, loc="lower right")
fig.text(0.5, -0.02, "Bars: 200-step kl maps; error bars = seed-level 95% t CI (3 seeds) or sequence bootstrap (1 seed). ★ = 600-step maps, seed 0.",
         ha="center", fontsize=7)
fig.tight_layout(); fig.savefig("figures/fig2_dk.png", dpi=200, bbox_inches="tight"); plt.close(fig)

# ---- Fig 3: dissociation (normalised CKA, R2, -KL by depth)
fig, axs = plt.subplots(1, 4, figsize=(7.2, 2.2), sharey=True)
for a, src in zip(axs, SRC):
    cka = np.array([cell(src, k, "mse")["pile"]["cka"] for k in KS])
    r2 = np.array([cell(src, k, "mse")["pile"]["r2"] for k in KS])
    kl = np.array([cell(src, k)["pile"]["stitched_kl"][0] for k in KS])
    nz = lambda v: (v - v.min()) / (v.max() - v.min())
    a.plot(KS, nz(cka), marker="o", ms=3, label="CKA"); a.plot(KS, nz(r2), marker="s", ms=3, label="R²")
    a.plot(KS, nz(-kl), marker="^", ms=3, color="k", label="−KL (function)")
    a.set_title(src, fontsize=8); a.set_xticks(KS)
axs[0].set_ylabel("min–max normalised"); axs[0].legend(fontsize=6, frameon=False)
fig.tight_layout(); fig.savefig("figures/fig3_dissociation.png", dpi=200); plt.close(fig)

# ---- Fig 4: X3 realised vs predicted tokens per target call
X = json.load(open("results/X3_summary.json"))
g = sorted(X["gamma"], key=int)
R = [X["gamma"][k]["R"] for k in g]; Rlo = [X["gamma"][k]["R_ci"][0] for k in g]; Rhi = [X["gamma"][k]["R_ci"][1] for k in g]
P1 = [X["gamma"][k]["P1"] for k in g]; P2 = [X["gamma"][k]["P2"] for k in g]
fig, ax = plt.subplots(figsize=(3.4, 2.5))
xg = [int(k) for k in g]
ax.errorbar(xg, R, yerr=[np.subtract(R, Rlo), np.subtract(Rhi, R)], marker="o", capsize=3, label="realised (speculative sampling)")
ax.plot(xg, P1, marker="x", ls="--", label="i.i.d. formula, teacher-forced ᾱ")
ax.plot(xg, P2, marker="+", ls=":", label="i.i.d. formula, on-path ᾱ")
ax.set_xticks(xg); ax.set_xlabel("draft length γ"); ax.set_ylabel("tokens per target call")
ax.set_title("X3: 70m drafting for 410m", fontsize=9); ax.legend(fontsize=6, frameon=False)
fig.tight_layout(); fig.savefig("figures/fig4_x3.png", dpi=200); plt.close(fig)
print("figures written")
