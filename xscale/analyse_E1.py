"""Analysis of E1 cells (preregistered tests). Reads results/E1/*.json, writes results/E1_summary.json,
results/E1_tables.md and figures/E1_*.png.  Usage: python3 xscale/analyse_E1.py"""
import glob
import json
import os
import re
from collections import defaultdict

import numpy as np

RNG = np.random.default_rng(12345)
NB = 10000
cells = {}
for f in sorted(glob.glob("results/E1/*.json")):
    name = os.path.basename(f)[:-5]
    cells[name] = json.load(open(f))


def parse(name):
    m = re.match(r"(S(?P<src>[\w.\-]+?)|self(?P<self>\d))_T(?P<tgt>[\w.]+)_k(?P<k>\d+)_(?P<obj>mse|kl|klsrc|id)_s(?P<seed>\d)(?P<long>_long)?$", name)
    d = m.groupdict()
    return dict(src=d["src"] or f"self{d['self']}", tgt=d["tgt"], k=int(d["k"]), obj=d["obj"],
                seed=int(d["seed"]), long=bool(d["long"]))


def per_seq(cell, ev, tag, metric):
    return np.array(cell["eval"][ev]["per_seq"][tag][metric])


def boot_mean_ci(groups):
    """groups: list of 1-D arrays (one per seed). Stratified bootstrap over sequences within seed."""
    est = np.mean(np.concatenate(groups))
    bs = np.empty(NB)
    for b in range(NB):
        bs[b] = np.mean(np.concatenate([g[RNG.integers(0, len(g), len(g))] for g in groups]))
    lo, hi = np.percentile(bs, [2.5, 97.5])
    p_le0 = (np.sum(bs <= 0) + 1) / (NB + 1)  # one-sided bootstrap p for effect > 0
    return float(est), float(lo), float(hi), float(p_le0)


# group cells by (src, tgt, k, obj, long)
groups = defaultdict(list)
for n, c in cells.items():
    meta = parse(n)
    groups[(meta["src"], meta["tgt"], meta["k"], meta["obj"], meta["long"])].append((meta["seed"], c))

summary = {"cells": {}, "tests": {}}
rows = []
for key, lst in sorted(groups.items()):
    src, tgt, k, obj, long = key
    lst.sort()
    out = {"seeds": [s for s, _ in lst]}
    for ev in ["pile", "wiki"]:
        res = {}
        for metric in ["kl", "acc", "top1", "ce", "kl_to_source"]:
            if metric not in lst[0][1]["eval"][ev]["per_seq"]["stitched"]:
                continue
            g = [per_seq(c, ev, "stitched", metric) for _, c in lst]
            res[f"stitched_{metric}"] = boot_mean_ci(g)[:3]
            if metric in lst[0][1]["eval"][ev]["per_seq"].get("source", {}):
                gs = [per_seq(c, ev, "source", metric) for _, c in lst]
                res[f"source_{metric}"] = boot_mean_ci(gs)[:3]
            gt = [per_seq(c, ev, "target", "ce") for _, c in lst]
            res["target_ce"] = boot_mean_ci(gt)[:3]
        if "source" in lst[0][1]["eval"][ev]["per_seq"]:
            delta = [per_seq(c, ev, "source", "kl") - per_seq(c, ev, "stitched", "kl") for _, c in lst]
            res["delta_kl"] = boot_mean_ci(delta)
        res["r2"] = float(np.mean([c["eval"][ev]["r2_heldout"] for _, c in lst]))
        res["cka"] = float(np.mean([c["eval"][ev]["cka"] for _, c in lst]))
        res["seed_means_stitched_kl"] = [float(per_seq(c, ev, "stitched", "kl").mean()) for _, c in lst]
        out[ev] = res
    out["flops"] = lst[0][1]["flops"]
    out["train_log"] = [c["train_log"] for _, c in lst]
    summary["cells"]["|".join(map(str, key))] = out

# ---- H-ratio: Delta_k > 0 tests with Holm over pairs x depths (kl objective, 200-step cells)
pairs = ["70m", "160m", "410m-deduped", "410m-seed1"]
tests = []
for src in pairs:
    for k in [6, 12, 18, 24]:
        key = "|".join(map(str, (src, "410m", k, "kl", False)))
        if key in summary["cells"]:
            est, lo, hi, p = summary["cells"][key]["pile"]["delta_kl"]
            tests.append(dict(src=src, k=k, est=est, lo=lo, hi=hi, p=p, seeds=summary["cells"][key]["seeds"]))
order = np.argsort([t["p"] for t in tests])
m = len(tests)
running = 0
for rank, i in enumerate(order):
    adj = min(1.0, (m - rank) * tests[i]["p"])
    running = max(running, adj)
    tests[i]["p_holm"] = running
summary["tests"]["H_ratio"] = tests

# ---- A1 co-primary: D_k = KL(q_24) - KL(q_k), paired on the same eval sequences (kl objective)
dtests = []
for src in pairs:
    g24 = {s: c for s, c in groups.get((src, "410m", 24, "kl", False), [])}
    for k in [6, 12, 18]:
        gk = {s: c for s, c in groups.get((src, "410m", k, "kl", False), [])}
        seeds = sorted(set(g24) & set(gk))
        if not seeds:
            continue
        d = [per_seq(g24[s], "pile", "stitched", "kl") - per_seq(gk[s], "pile", "stitched", "kl") for s in seeds]
        est, lo, hi, pv = boot_mean_ci(d)
        t = dict(src=src, k=k, est=est, lo=lo, hi=hi, p=pv, seeds=seeds)
        # review R4: preregistered seed-0-only test, reported separately from post-hoc A8 seeds
        if 0 in seeds:
            t["seed0"] = boot_mean_ci([d[seeds.index(0)]])[:3]
        # review R3: seed-level t interval (includes map-fit variance); only with >= 2 seeds
        sm = np.array([x.mean() for x in d])
        t["seed_means"] = sm.tolist()
        if len(sm) >= 2:
            from scipy import stats
            h = stats.t.ppf(0.975, len(sm) - 1) * sm.std(ddof=1) / np.sqrt(len(sm))
            t["seed_t_ci"] = [float(sm.mean() - h), float(sm.mean() + h)]
        dw = [per_seq(g24[s], "wiki", "stitched", "kl") - per_seq(gk[s], "wiki", "stitched", "kl") for s in seeds]
        t["wiki"] = boot_mean_ci(dw)[:3]
        swm = np.array([x.mean() for x in dw])
        if len(swm) >= 2:
            from scipy import stats
            h = stats.t.ppf(0.975, len(swm) - 1) * swm.std(ddof=1) / np.sqrt(len(swm))
            t["wiki_seed_t_ci"] = [float(swm.mean() - h), float(swm.mean() + h)]
        dtests.append(t)
summary["tests"]["D_k"] = dtests

# ---- R1 convergence check (11_preregistration_R1.md) and second target (1b, L = 16): D_k for other cell sets
def dk_pair(key24, keyk):
    a = dict(groups.get(key24, [])); b = dict(groups.get(keyk, []))
    seeds = sorted(set(a) & set(b))
    if not seeds:
        return None
    d = [per_seq(a[s], "pile", "stitched", "kl") - per_seq(b[s], "pile", "stitched", "kl") for s in seeds]
    dw = [per_seq(a[s], "wiki", "stitched", "kl") - per_seq(b[s], "wiki", "stitched", "kl") for s in seeds]
    return dict(est_ci=boot_mean_ci(d), wiki=boot_mean_ci(dw)[:3], seeds=seeds)
extra = []
for src in ["70m", "160m", "410m-deduped"]:
    for k in [12, 18]:
        r = dk_pair((src, "410m", 24, "kl", True), (src, "410m", k, "kl", True))
        if r: extra.append(dict(label=f"{src}→410m, 600 steps", k=k, **r))
for k in [4, 8, 12]:
    r = dk_pair(("160m", "1b", 16, "kl", False), ("160m", "1b", k, "kl", False))
    if r: extra.append(dict(label="160m→1b (L=16)", k=k, **r))
summary["tests"]["D_k_extra"] = extra

# ---- A1 read-out calibration
cal = []
for src in pairs:
    c = summary["cells"].get("|".join(map(str, (src, "410m", 24, "klsrc", False))))
    if c:
        cal.append(dict(src=src, kl_to_source=c["pile"]["stitched_kl_to_source"][0], kl_to_target=c["pile"]["stitched_kl"][0],
                        source_kl_to_target=c["pile"]["source_kl"][0]))
summary["tests"]["readout_calibration"] = cal

# ---- H-objective: KL(mse)/KL(kl) at k=12
hobj = []
for src in pairs:
    a = summary["cells"].get("|".join(map(str, (src, "410m", 12, "mse", False))))
    b = summary["cells"].get("|".join(map(str, (src, "410m", 12, "kl", False))))
    if a and b:
        hobj.append(dict(src=src, kl_mse=a["pile"]["stitched_kl"][0], kl_kl=b["pile"]["stitched_kl"][0],
                         ratio=a["pile"]["stitched_kl"][0] / b["pile"]["stitched_kl"][0]))
summary["tests"]["H_objective"] = hobj

# ---- H-dissociation: representational argmax vs functional argmin over k (seed-0 cells)
hdis = []
for src in pairs:
    ks, cka, r2, klf = [], [], [], []
    for k in [6, 12, 18, 24]:
        c_kl = summary["cells"].get("|".join(map(str, (src, "410m", k, "kl", False))))
        c_ms = summary["cells"].get("|".join(map(str, (src, "410m", k, "mse", False))))
        if c_kl and c_ms:
            ks.append(k); cka.append(c_ms["pile"]["cka"]); r2.append(c_ms["pile"]["r2"]); klf.append(c_kl["pile"]["stitched_kl"][0])
    if len(ks) == 4:
        hdis.append(dict(src=src, ks=ks, cka=cka, r2=r2, kl=klf, argmax_cka=ks[int(np.argmax(cka))],
                         argmax_r2=ks[int(np.argmax(r2))], argmin_kl=ks[int(np.argmin(klf))]))
summary["tests"]["H_dissociation"] = hdis

# ---- H-self
hself = []
for k in [6, 12, 18, 24]:
    s1 = summary["cells"].get("|".join(map(str, ("self1", "410m", k, "kl", False))))
    x = summary["cells"].get("|".join(map(str, ("70m", "410m", k, "kl", False))))
    if s1 and x:
        hself.append(dict(k=k, self1_kl=s1["pile"]["stitched_kl"][0], s70m_kl=x["pile"]["stitched_kl"][0],
                          self1_flops=s1["flops"]["stitched"], s70m_flops=x["flops"]["stitched"]))
summary["tests"]["H_self"] = hself

os.makedirs("results", exist_ok=True)
json.dump(summary, open("results/E1_summary.json", "w"), indent=1)

# ---- tables
L = ["# E1 results tables (auto-generated by xscale/analyse_E1.py)", "",
     "Means over evaluation sequences (Pile held-out; 64 seq × 126 positions per seed); 95% CI = stratified bootstrap over sequences.", "",
     "| source | target | k | objective | seeds | KL(p_T‖q) stitched [CI] | KL(p_T‖p_S) source | Δ_k [CI] | acc stitched | acc source | top1 stitched | CE stitched | CE source | CE target | R² | CKA | Wiki KL stitched | Wiki KL source |",
     "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
f3 = lambda t: f"{t[0]:.3f} [{t[1]:.3f}, {t[2]:.3f}]"
for key, c in summary["cells"].items():
    src, tgt, k, obj, long = key.split("|")
    p, w = c["pile"], c["wiki"]
    g = lambda d, n: f"{d[n][0]:.3f}" if n in d else "—"
    L.append(f"| {src}{' (600 steps)' if long == 'True' else ''} | {tgt} | {k} | {obj} | {c['seeds']} | {f3(p['stitched_kl'])} | {g(p,'source_kl')} | "
             f"{f3(p['delta_kl']) if 'delta_kl' in p else '—'} | {g(p,'stitched_acc')} | {g(p,'source_acc')} | {g(p,'stitched_top1')} | "
             f"{g(p,'stitched_ce')} | {g(p,'source_ce')} | {g(p,'target_ce')} | {p['r2']:.3f} | {p['cka']:.3f} | {g(w,'stitched_kl')} | {g(w,'source_kl')} |")
L += ["", "## H-ratio (Δ_k > 0, Holm-corrected one-sided bootstrap p)", "", "| source | k | Δ_k | 95% CI | p | p_Holm | seeds |", "|---|---|---|---|---|---|---|"]
for t in tests:
    L.append(f"| {t['src']} | {t['k']} | {t['est']:.3f} | [{t['lo']:.3f}, {t['hi']:.3f}] | {t['p']:.4f} | {t['p_holm']:.4f} | {t['seeds']} |")
L += ["", "## H-objective (k = 12)", "", "| source | KL mse | KL kl | ratio |", "|---|---|---|---|"]
for t in hobj:
    L.append(f"| {t['src']} | {t['kl_mse']:.3f} | {t['kl_kl']:.3f} | {t['ratio']:.2f} |")
L += ["", "## H-dissociation", "", "| source | CKA by k | R² by k | KL(kl) by k | argmax CKA | argmax R² | argmin KL |", "|---|---|---|---|---|---|---|"]
for t in hdis:
    L.append(f"| {t['src']} | {[round(x,3) for x in t['cka']]} | {[round(x,3) for x in t['r2']]} | {[round(x,3) for x in t['kl']]} | {t['argmax_cka']} | {t['argmax_r2']} | {t['argmin_kl']} |")
L += ["", "## H-self", "", "| k | self:1 KL | 70m KL | self:1 GFLOP/token | 70m-stitch GFLOP/token |", "|---|---|---|---|---|"]
for t in hself:
    L.append(f"| {t['k']} | {t['self1_kl']:.3f} | {t['s70m_kl']:.3f} | {t['self1_flops']/1e9:.3f} | {t['s70m_flops']/1e9:.3f} |")
L += ["", "## A1 co-primary: D_k = KL(p_T‖q_24) − KL(p_T‖q_k) (kl objective; > 0 means the upper blocks add value beyond a linear read-out)", "", "| source | k | D_k | 95% CI | one-sided p | seeds |", "|---|---|---|---|---|---|"]
for t in dtests:
    L.append(f"| {t['src']} | {t['k']} | {t['est']:.3f} | [{t['lo']:.3f}, {t['hi']:.3f}] | {t['p']:.4f} | {t['seeds']} |")
L += ["", "### D_k robustness (review R3/R4): preregistered seed-0 test; seed-level t CI (incl. map-fit variance); WikiText",
      "", "| source | k | seed-0 D_k [CI] (prereg) | seed means | seed-level 95% t CI | WikiText D_k [CI] | WikiText seed-level t CI |", "|---|---|---|---|---|---|---|"]
for t in summary["tests"]["D_k"]:
    s0 = f"{t['seed0'][0]:.3f} [{t['seed0'][1]:.3f}, {t['seed0'][2]:.3f}]" if "seed0" in t else "–"
    st = f"[{t['seed_t_ci'][0]:.3f}, {t['seed_t_ci'][1]:.3f}]" if "seed_t_ci" in t else "single seed"
    wt = f"[{t['wiki_seed_t_ci'][0]:.3f}, {t['wiki_seed_t_ci'][1]:.3f}]" if "wiki_seed_t_ci" in t else "single seed"
    w = t["wiki"]
    L.append(f"| {t['src']} | {t['k']} | {s0} | {[round(x, 3) for x in t['seed_means']]} | {st} | {w[0]:.3f} [{w[1]:.3f}, {w[2]:.3f}] | {wt} |")
L += ["", "Seeds 1–2 at k = 18 (all pairs) and k = 24 (160m) are **post hoc** (amendment A8).", "",
      "## D_k for the R1 convergence cells (600 steps, n_fit 1024, seed 0) and the 1b target", "",
      "| cells | k | D_k [CI] Pile | one-sided p | D_k [CI] WikiText | seeds |", "|---|---|---|---|---|---|"]
for t in summary["tests"]["D_k_extra"]:
    e = t["est_ci"]; w = t["wiki"]
    L.append(f"| {t['label']} | {t['k']} | {e[0]:.3f} [{e[1]:.3f}, {e[2]:.3f}] | {e[3]:.4f} | {w[0]:.3f} [{w[1]:.3f}, {w[2]:.3f}] | {t['seeds']} |")
L += ["", "## A1 read-out calibration (k = 24 map trained to reproduce p_S)", "", "| source | KL(p_S‖q) | KL(p_T‖q) | KL(p_T‖p_S) |", "|---|---|---|---|"]
for t in cal:
    L.append(f"| {t['src']} | {t['kl_to_source']:.3f} | {t['kl_to_target']:.3f} | {t['source_kl_to_target']:.3f} |")
open("results/E1_tables.md", "w").write("\n".join(L) + "\n")
print("\n".join(L))
