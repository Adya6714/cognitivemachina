"""Aggregate replication cells: KL_k, KL_source, D_k = KL_L - KL_k, KL_k - KL_source with paired
bootstrap CIs over eval sequences (10 000 resamples). Where >1 fit seed exists for a cell, per-sequence
values are averaged over seeds first (eval sequences are identical across seeds), so the CI reflects
sequence sampling only; seed-level means are reported separately."""
import glob, json, sys
from collections import defaultdict
import numpy as np

RES = "/home/user/cognitivemachina/replication/results"
prefix = sys.argv[1] if len(sys.argv) > 1 else "S70m_T160m"
B = 10000


def ci(x, rng):
    x = np.asarray(x)
    bs = x[rng.integers(0, len(x), (B, len(x)))].mean(1)
    return float(x.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


cells = defaultdict(dict)
for f in sorted(glob.glob(f"{RES}/{prefix}_k*_s*.json")):
    r = json.load(open(f))
    cells[r["k"]][r["seed"]] = r
L = max(cells)
out = {"prefix": prefix, "L": L, "rows": {}}
rng = np.random.default_rng(12345)
for ev in ["wt_val", "pile_hi"]:
    print(f"\n== eval set {ev} ==")
    print(f"{'k':>3} {'seeds':>6} {'KL_k':>8} {'KL_src':>7}  {'D_k=KL_L-KL_k [95% CI]':>28}  {'KL_k-KL_src [95% CI]':>28}  seed means KL_k")
    def per_seq(k, key="eval", seeds=None):
        seeds = sorted(cells[k]) if seeds is None else seeds
        arr = [np.array(cells[k][s][key][ev]["kl_stitch"]) for s in seeds if key in cells[k][s]]
        return np.mean(arr, 0) if arr else np.array([np.nan])
    src = np.array(next(iter(cells[L].values()))["eval"][ev]["kl_source"])
    KLL = per_seq(L)
    for k in sorted(cells):
        x = per_seq(k)
        init = per_seq(k, "eval_init")
        common = sorted(set(cells[k]) & set(cells[L]))  # D_k uses seed-matched cells only
        KLLm = per_seq(L, seeds=common)
        d = ci(KLLm - per_seq(k, seeds=common), rng) if k != L else None
        g = ci(x - src, rng)
        sm = {s: float(np.mean(cells[k][s]["eval"][ev]["kl_stitch"])) for s in sorted(cells[k])}
        ds = f"{d[0]:+.3f} [{d[1]:+.3f},{d[2]:+.3f}]" if d else "—"
        print(f"{k:>3} {len(cells[k]):>6} {x.mean():8.3f} {src.mean():7.3f}  {ds:>28}  {g[0]:+.3f} [{g[1]:+.3f},{g[2]:+.3f}]  {sm}")
        extra = {}
        if k != L:
            dd = KLLm - per_seq(k, seeds=common)
            mb = np.median(dd[rng.integers(0, len(dd), (B, len(dd)))], 1)
            extra = {"D_k_seeds": common, "D_k_median_seq": float(np.median(dd)),
                     "D_k_median_ci": [float(np.percentile(mb, 2.5)), float(np.percentile(mb, 97.5))], "frac_seq_D_pos": float((dd > 0).mean()),
                     "D_k_seed_level": {s: float(np.mean(cells[L][s]["eval"][ev]["kl_stitch"]) - sm[s])
                                        for s in sm if s in cells[L]}}
            print(f"      median per-seq D_k {extra['D_k_median_seq']:+.3f} [{extra['D_k_median_ci'][0]:+.3f},{extra['D_k_median_ci'][1]:+.3f}], frac seqs D_k>0 {extra['frac_seq_D_pos']:.2f}, seed-level D_k {extra['D_k_seed_level']}")
        out["rows"][f"{ev}_k{k}"] = {**extra, "k": k, "eval": ev, "seeds": sorted(cells[k]), "KL_k": float(x.mean()),
                                     "KL_source": float(src.mean()),
                                     "D_k": d, "KLk_minus_KLsrc": g, "seed_means": sm,
                                     "top1_stitch": float(np.mean([np.mean(cells[k][s]["eval"][ev]["top1_stitch"]) for s in cells[k]])),
                                     "top1_source": float(np.mean(next(iter(cells[k].values()))["eval"][ev]["top1_source"]))}
json.dump(out, open(f"{RES}/summary_{prefix}.json", "w"), indent=1)
