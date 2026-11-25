"""X3: real speculative sampling (pythia-70m draft -> pythia-410m target) vs the i.i.d. acceptance formula.
Prereg: docs/07_preregistration_X3.md.  Usage: python3 xscale/specdec_x3.py [n_prompts] [new_tokens]"""
import sys, time
import numpy as np
import torch
sys.path.insert(0, ".")
from xscale.common import load, make_sequences, save_json

torch.set_num_threads(int(__import__("os").environ.get("X3_THREADS", "1")))
NP = int(sys.argv[1]) if len(sys.argv) > 1 else 48
NEW = int(sys.argv[2]) if len(sys.argv) > 2 else 96
q_m, p_m = load("70m"), load("410m")
V = min(q_m.config.vocab_size, p_m.config.vocab_size)


def probs(logits):
    return torch.softmax(logits[..., :V].double(), -1)


def crop(cache, n):
    extra = cache.get_seq_length() - n
    if extra > 0:
        cache.crop(-extra)


def fwd(m, ids, cache):
    out = m(input_ids=ids, past_key_values=cache, use_cache=True)
    return out.logits[0], out.past_key_values


# ---------------------------------------------------------------- teacher-forced alpha
tf = make_sequences("pile", 64, 128, "eval", seed=201)
a_tf = []
for i in range(len(tf)):
    p = probs(p_m(input_ids=tf[i:i + 1]).logits[0, 1:-1]); q = probs(q_m(input_ids=tf[i:i + 1]).logits[0, 1:-1])
    a_tf.append((1 - 0.5 * (p - q).abs().sum(-1)).numpy())
a_tf_seq = np.array([a.mean() for a in a_tf])

# ---------------------------------------------------------------- cache correctness unit test
ids = tf[:1, :40]
full = p_m(input_ids=ids).logits[0]
l1, c = fwd(p_m, ids[:, :30], None); l2, c = fwd(p_m, ids[:, 30:35], c); crop(c, 32); l3, c = fwd(p_m, ids[:, 32:40], c)
tvd = lambda a, b: float((0.5 * (probs(a) - probs(b)).abs().sum(-1)).max())
cache_err = max(tvd(l2, full[30:35]), tvd(l3, full[32:40]))
print("cache unit test max TV(cached, uncached) =", cache_err, "| max logit diff",
      float(max((l2 - full[30:35]).abs().max(), (l3 - full[32:40]).abs().max())), flush=True)
assert cache_err < 1e-4  # float32 reordering noise only

prompts = make_sequences("pile", NP, 32, "eval", seed=200)


def spec_generate(prompt, gamma, gen):
    seq = prompt[0].tolist()
    pc = qc = None; p_len = q_len = 0  # tokens covered by each cache
    steps = []
    while len(seq) - len(prompt[0]) < NEW:
        # draft
        if qc is not None: crop(qc, q_len)
        lq, qc = fwd(q_m, torch.tensor([seq[q_len:]]), qc); q_len = len(seq)
        drafts, qdist = [], []
        for j in range(gamma):
            qd = probs(lq[-1]); x = int(torch.multinomial(qd, 1, generator=gen))
            drafts.append(x); qdist.append(qd)
            if j < gamma - 1:
                lq, qc = fwd(q_m, torch.tensor([[x]]), qc); q_len += 1
        # verify
        if pc is not None: crop(pc, p_len)
        lp, pc = fwd(p_m, torch.tensor([seq[p_len:] + drafts]), pc)
        pd = probs(lp[-(gamma + 1):])
        alphas = [float(1 - 0.5 * (pd[j] - qdist[j]).abs().sum()) for j in range(gamma)]
        a = 0; new = None
        for j in range(gamma):
            x = drafts[j]
            if float(torch.rand(1, generator=gen)) < min(1.0, float(pd[j, x] / qdist[j][x])):
                a += 1
            else:
                r = (pd[j] - qdist[j]).clamp(min=0); new = int(torch.multinomial(r / r.sum(), 1, generator=gen)); break
        if new is None:
            new = int(torch.multinomial(pd[gamma], 1, generator=gen))
        old = len(seq)
        seq += drafts[:a] + [new]
        p_len = old + a  # cache valid through accepted drafts; the new token is not cached
        q_len = min(q_len, old + a)
        steps.append(dict(acc=a, alphas=alphas[:a + 1]))  # alphas observed up to and including first reject
    return steps


res = dict(n_prompts=NP, new_tokens=NEW, cache_unit_test=cache_err, alpha_tf_mean=float(np.concatenate(a_tf).mean()),
           alpha_tf_seq=a_tf_seq.tolist(), gamma={})
for gamma, seed in [(2, 11), (4, 12), (8, 13)]:
    gen = torch.Generator().manual_seed(seed); t0 = time.time()
    per = []
    for i in range(NP):
        st = spec_generate(prompts[i:i + 1], gamma, gen)
        per.append(dict(acc=[s["acc"] for s in st], a1=[s["alphas"][0] for s in st], alphas=[s["alphas"] for s in st]))
    res["gamma"][gamma] = dict(seed=seed, per_prompt=per, seconds=time.time() - t0)
    R = np.mean([np.mean(np.array(p["acc"]) + 1) for p in per])
    print(f"gamma {gamma}: realised tokens/call {R:.3f} | {time.time()-t0:.0f}s", flush=True)
    save_json(res, "results/X3/specdec_70m_410m.json")
print("X3_DONE")
