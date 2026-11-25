"""Independent replication of cross-scale stitching (Agent 10).

Written from scratch; does not import or read anything under xscale/ or results/.

Setting
  source S (default EleutherAI/pythia-70m): final-LayerNorm output h_S (B,T,dS)
  target T (default EleutherAI/pythia-160m, L blocks)
  stitch at depth k: replace the input to T's block k (k<L) or T's final LayerNorm (k=L)
  at positions 1..T-1 by A h_S + b; position 0 (BOS) keeps T's own state.
  q_k = softmax(unembed(finalLN(blocks_k..L-1(injected)))).

Map fitting: ridge least-squares init (h_S -> R_k, T's own residual at the injection point),
then Adam on mean KL(p_T || q_k) over predicted positions 1..T-2 through T's frozen upper blocks.

Injection is done with a forward pre-hook (with_kwargs) on block k / the final LayerNorm that
replaces the hidden_states argument.
"""
import argparse, json, math, os, time
import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

torch.set_num_threads(int(os.environ.get("REP_THREADS", "1")))
HUB = os.path.expanduser("~/.cache/huggingface/hub")
SEQ = 128
P0, P1 = 1, 127  # metric positions 1..126 (python slice 1:127)


# ----------------------------------------------------------------- data
def _parquets(repo, sub, split):
    import glob
    pat = os.path.join(HUB, f"datasets--{repo.replace('/', '--')}", "snapshots", "*", sub, f"{split}-*.parquet")
    fs = sorted(glob.glob(pat))
    if not fs:
        from huggingface_hub import snapshot_download
        snapshot_download(repo, repo_type="dataset")
        fs = sorted(glob.glob(pat))
    return fs


def load_texts(name):
    import pyarrow.parquet as pq
    if name in ("wt_train", "wt_val"):
        split = "train" if name == "wt_train" else "validation"
        fs = _parquets("Salesforce/wikitext", "wikitext-103-raw-v1", split)
        if split == "train":
            fs = fs[:1]  # first train shard (~0.9M lines) is plenty and halves memory
        return [t for f in fs for t in pq.read_table(f).column("text").to_pylist()]
    if name == "pile_hi":
        fs = _parquets("NeelNanda/pile-10k", "data", "train")
        texts = [t for f in fs for t in pq.read_table(f).column("text").to_pylist()]
        return texts[5000:]  # documents with index >= 5000
    raise ValueError(name)


def make_seqs(name, n, seed, tok):
    """n sequences of length SEQ: [0] + 127 tokens."""
    rng = np.random.default_rng(seed)
    texts = load_texts(name)
    L = SEQ - 1
    if name.startswith("wt"):
        # WikiText: articles are split in lines; build contiguous stream from a random contiguous
        # window of lines, chunk into L-token windows, sample n of them.
        if name == "wt_train":
            # use a random 20k-line window to keep tokenisation cheap
            start = int(rng.integers(0, len(texts) - 20000))
            texts = texts[start:start + 20000]
        stream = tok("".join(texts))["input_ids"]
        del texts
        nchunk = len(stream) // L
        idx = rng.choice(nchunk, size=n, replace=False)
        seqs = [[0] + stream[i * L:(i + 1) * L] for i in sorted(idx)]
    else:
        order = rng.permutation(len(texts))
        seqs = []
        for i in order:
            ids = tok(texts[i])["input_ids"]
            if len(ids) >= L:
                seqs.append([0] + ids[:L])
            if len(seqs) == n:
                break
    return torch.tensor(seqs, dtype=torch.long)


# ----------------------------------------------------------------- models
def load(name):
    m = AutoModelForCausalLM.from_pretrained(name, torch_dtype=torch.float32)
    m.eval()
    for p in m.parameters():
        p.requires_grad_(False)
    return m


def inj_module(model, k):
    nx = model.gpt_neox
    L = len(nx.layers)
    return nx.layers[k] if k < L else nx.final_layer_norm


class _Stop(Exception):
    pass


class Injector:
    """Forward pre-hook replacing the hidden-states input of block k / final LN."""

    def __init__(self, model, k):
        self.mod = inj_module(model, k)
        self.is_ln = not hasattr(self.mod, "attention")
        self.replacement = None  # full (B,T,d) tensor or None
        self.captured = None
        self.capture = False
        self.stop = False
        self.h = self.mod.register_forward_pre_hook(self.hook, with_kwargs=True)

    def hook(self, mod, args, kwargs):
        if args:
            x = args[0]
        else:
            x = kwargs["hidden_states"]
        if self.capture:
            self.captured = x.detach().clone()
            if self.stop:
                raise _Stop()  # capture-only pass: skip the rest of the forward
        if self.replacement is None:
            return None
        r = self.replacement
        if args:
            return (r,) + tuple(args[1:]), kwargs
        kwargs = dict(kwargs)
        kwargs["hidden_states"] = r
        return args, kwargs

    def remove(self):
        self.h.remove()


@torch.no_grad()
def src_features(src, ids):
    out = src(ids, output_hidden_states=True)
    # HF GPT-NeoX: last hidden_states entry is post-final-LayerNorm. Verify against logits.
    h = out.hidden_states[-1]
    chk = src.get_output_embeddings()(h)
    assert torch.allclose(chk, out.logits, atol=1e-4), "source final-LN output mismatch"
    return h, out.logits


def unit_test(tgt, ids, ks):
    res = {}
    with torch.no_grad():
        ref = tgt(ids).logits
        for k in ks:
            inj = Injector(tgt, k)
            inj.capture = True
            tgt(ids)
            own = inj.captured
            inj.capture = False
            inj.replacement = own
            out = tgt(ids).logits
            # perturbation check: hook actually takes effect
            inj.replacement = own + torch.randn_like(own)  # (constant shift is LN-invariant at k=L)
            pert = tgt(ids).logits
            inj.remove()
            d = (out - ref).abs().max().item()
            dp = (pert - ref).abs().max().item()
            res[k] = {"max_abs_diff_own_state": d, "exact": bool(torch.equal(out, ref)),
                      "max_abs_diff_perturbed": dp}
            assert d == 0.0 or d < 1e-5, f"injection of own states not reproducing logits at k={k}: {d}"
            assert dp > 1e-3, f"hook has no effect at k={k}"
    return res


def kl_rows(logp_t, logq):
    """KL(p_T||q) per position: (..., V) -> (...)."""
    return (logp_t.exp() * (logp_t - logq)).sum(-1)


# ----------------------------------------------------------------- one cell
def run_cell(args):
    t0 = time.time()
    torch.manual_seed(args.seed)
    tok = AutoTokenizer.from_pretrained(args.tgt)
    src, tgt = load(args.src), load(args.tgt)
    Lt = len(tgt.gpt_neox.layers)
    k = args.k

    cache = os.path.join(args.cache_dir, f"data_fit{args.seed}_n{args.n_fit}_e{args.n_eval}.pt")
    if os.path.exists(cache):
        D = torch.load(cache)
        fit, evals, HS = D["fit"], D["evals"], D["HS"]
    else:
        fit = make_seqs("wt_train", args.n_fit, 1000 + args.seed, tok)
        evals = {"wt_val": make_seqs("wt_val", args.n_eval, 2000, tok),
                 "pile_hi": make_seqs("pile_hi", args.n_eval, 3000, tok)}
        HS = None

    import gc; gc.collect()
    ut = unit_test(tgt, evals["pile_hi"][:4], [k])
    print("unit test", ut, flush=True)

    inj = Injector(tgt, k)

    def target_states(ids, bs=16):
        RK = []
        inj.capture, inj.stop, inj.replacement = True, True, None
        for i in range(0, len(ids), bs):
            try:
                with torch.no_grad():
                    tgt(ids[i:i + bs])
            except _Stop:
                pass
            RK.append(inj.captured)
        inj.capture, inj.stop = False, False
        return torch.cat(RK)

    if HS is None:
        HS = torch.cat([src_features(src, fit[i:i + 16])[0] for i in range(0, len(fit), 16)])
        os.makedirs(args.cache_dir, exist_ok=True)
        torch.save({"fit": fit, "evals": evals, "HS": HS}, cache)
    RK = target_states(fit)
    bos_state = RK[0, 0].clone()  # identical for all sequences (token 0 at position 0)
    assert torch.allclose(RK[:, 0], bos_state.expand_as(RK[:, 0]), atol=1e-4)

    # ridge init on positions 1..T-1
    X = HS[:, 1:].reshape(-1, HS.shape[-1]).double()
    Y = RK[:, 1:].reshape(-1, RK.shape[-1]).double()
    mx, my = X.mean(0), Y.mean(0)
    Xc, Yc = X - mx, Y - my
    lam = args.ridge * Xc.pow(2).sum(0).mean()
    G = Xc.T @ Xc + lam * torch.eye(X.shape[1], dtype=X.dtype)
    W = torch.linalg.solve(G, Xc.T @ Yc)  # dS x dT
    b = my - mx @ W
    r2 = 1 - ((Yc - Xc @ W) ** 2).sum() / (Yc ** 2).sum()
    sigma = Yc.pow(2).mean(0).sqrt().float()  # per-output-dim scale of T's residual at the injection point
    del X, Y, Xc, Yc, G, RK

    # Affine map z = h W0 + b0 + sigma * (h D + d); (W0,b0) = ridge init (frozen), (D,d) trained from 0.
    # The sigma-scaled correction makes the Adam step size comparable across output dims and depths
    # (T's residual stream has a few very-large-scale dims). Overall map is still a single affine map.
    lr0 = args.lr
    W0, b0 = W.float(), b.float()
    Wp = torch.nn.Parameter(torch.zeros_like(W0))
    bp = torch.nn.Parameter(torch.zeros_like(b0))

    def stitched_logits(hS):
        h = hS[:, 1:]
        z = h @ W0 + b0 + sigma * (h @ Wp + bp)
        B = hS.shape[0]
        inj.replacement = torch.cat([bos_state.expand(B, 1, -1), z], 1)
        out = tgt(cur_ids).logits  # token ids only matter below k (overwritten) and for BOS
        inj.replacement = None
        return out

    # target log-probs for fit set computed on the fly (cheap relative to backward)
    def target_logp(ids):
        inj.replacement = None
        with torch.no_grad():
            return F.log_softmax(tgt(ids).logits[:, P0:P1], -1)

    def eval_set(ids, bs=8):
        per_seq = {"kl_stitch": [], "kl_source": [], "top1_stitch": [], "top1_source": []}
        nonlocal cur_ids
        for i in range(0, len(ids), bs):
            bi = ids[i:i + bs]
            cur_ids = bi
            lpT = target_logp(bi)
            hS, lS = src_features(src, bi)
            with torch.no_grad():
                lq = F.log_softmax(stitched_logits(hS)[:, P0:P1], -1)
            lS = F.log_softmax(lS[:, P0:P1], -1)
            per_seq["kl_stitch"] += kl_rows(lpT, lq).mean(1).tolist()
            per_seq["kl_source"] += kl_rows(lpT, lS).mean(1).tolist()
            at = lpT.argmax(-1)
            per_seq["top1_stitch"] += (lq.argmax(-1) == at).float().mean(1).tolist()
            per_seq["top1_source"] += (lS.argmax(-1) == at).float().mean(1).tolist()
        return per_seq

    cur_ids = None
    result = {"src": args.src, "tgt": args.tgt, "k": k, "L": Lt, "seed": args.seed,
              "hparams": {"n_fit": args.n_fit, "n_eval": args.n_eval, "steps": args.steps, "bs": args.bs,
                          "lr": lr0, "param": "z = h W0 + b0 + sigma*(h D + d), W0,b0 ridge; D,d Adam from 0", "sched": "linear warmup 10 + cosine", "ridge": args.ridge,
                          "wd": 0.0, "grad_clip": 1.0},
              "unit_test": ut, "ridge_r2_fit": r2.item()}

    if args.eval_init:
        result["eval_init"] = {n: eval_set(ids) for n, ids in evals.items()}
        print("init eval", {n: float(np.mean(v["kl_stitch"])) for n, v in result["eval_init"].items()}, flush=True)

    def fixed_loss():  # pilot diagnostic: KL on 16 fixed fit sequences
        nonlocal cur_ids
        cur_ids = fit[:16]
        with torch.no_grad():
            return kl_rows(target_logp(cur_ids), F.log_softmax(stitched_logits(HS[:16])[:, P0:P1], -1)).mean().item()
    if args.no_eval:
        fl0 = fixed_loss()
    opt = torch.optim.Adam([Wp, bp], lr=lr0)
    g = torch.Generator().manual_seed(args.seed)
    losses = []
    for step in range(args.steps):
        lr = lr0 * min(1.0, (step + 1) / 10) * 0.5 * (1 + math.cos(math.pi * step / args.steps))
        for pg in opt.param_groups:
            pg["lr"] = lr
        idx = torch.randint(0, len(fit), (args.bs,), generator=g)
        cur_ids = fit[idx]
        lpT = target_logp(cur_ids)
        lq = F.log_softmax(stitched_logits(HS[idx])[:, P0:P1], -1)
        loss = kl_rows(lpT, lq).mean()
        opt.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_([Wp, bp], 1.0)
        opt.step()
        losses.append(loss.item())
        if step % 25 == 0 or step == args.steps - 1:
            print(f"step {step} loss {loss.item():.4f} lr {lr:.2e} t {time.time()-t0:.0f}s", flush=True)
    result["train_loss"] = losses
    if args.no_eval:
        print("pilot: fixed-batch KL before %.4f after %.4f | mean loss first5 %.4f last10 %.4f" % (fl0, fixed_loss(), np.mean(losses[:5]), np.mean(losses[-10:])), flush=True)
        return
    result["eval"] = {n: eval_set(ids) for n, ids in evals.items()}
    result["seconds"] = time.time() - t0
    for n, v in result["eval"].items():
        print(n, "KL_stitch", np.mean(v["kl_stitch"]), "KL_source", np.mean(v["kl_source"]), flush=True)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(result, f)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="EleutherAI/pythia-70m")
    ap.add_argument("--tgt", default="EleutherAI/pythia-160m")
    ap.add_argument("--k", type=int, required=True)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--n_fit", type=int, default=512)
    ap.add_argument("--n_eval", type=int, default=128)
    ap.add_argument("--steps", type=int, default=300)
    ap.add_argument("--bs", type=int, default=8)
    ap.add_argument("--lr", type=float, default=1e-4, help="Adam lr on the sigma-scaled correction (D,d)")
    ap.add_argument("--cache_dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache"))
    ap.add_argument("--ridge", type=float, default=1e-3)
    ap.add_argument("--eval_init", action="store_true")
    ap.add_argument("--no_eval", action="store_true", help="pilot mode (lr selection): no eval, no output")
    ap.add_argument("--out", required=True)
    run_cell(ap.parse_args())
