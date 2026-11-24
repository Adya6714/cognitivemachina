"""Shared utilities for cross-scale state-injection experiments on GPT-NeoX (Pythia) models.

Conventions
-----------
* Residual stream R_k (k = 0..L) is the input to block k; R_0 = token embedding, R_L = output of the last
  block *before* the final LayerNorm. These are captured with forward hooks, so they are the exact tensors
  the next block consumes.
* Every sequence starts with the <|endoftext|> token (id 0) used as BOS. Position-0 states therefore do not
  depend on the input and are identical for every sequence; they are copied from the target model
  (a constant that can be cached at zero per-token cost). Metrics are computed on positions >= 1.
* Running the "upper" part of a model from layer k: the ModuleList is temporarily sliced to layers[k:] and
  the injected states are passed as inputs_embeds (GPT-NeoX applies only dropout, which is disabled in eval).
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import os

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

BOS_ID = 0
torch.set_grad_enabled(False)

PYTHIA = {
    "70m": "EleutherAI/pythia-70m",
    "160m": "EleutherAI/pythia-160m",
    "410m": "EleutherAI/pythia-410m",
    "1b": "EleutherAI/pythia-1b",
    "1.4b": "EleutherAI/pythia-1.4b",
    "410m-deduped": "EleutherAI/pythia-410m-deduped",
    "160m-deduped": "EleutherAI/pythia-160m-deduped",
    "410m-seed1": "EleutherAI/pythia-410m-seed1",
}


def load(name: str, revision: str | None = None):
    repo = PYTHIA.get(name, name)
    m = AutoModelForCausalLM.from_pretrained(repo, revision=revision, dtype=torch.float32)
    m.eval()
    return m


def tokenizer(name="70m"):
    return AutoTokenizer.from_pretrained(PYTHIA.get(name, name))


def n_layers(m):
    return m.config.num_hidden_layers


def d_model(m):
    return m.config.hidden_size


def block_flops_per_token(m, seq_len: int) -> float:
    """Approximate forward FLOPs per token of one transformer block (2 * matmul MACs).
    QKV 3d^2 + out d^2 + MLP 2*d*d_ff ; attention scores/values 2*n*d (average causal length n/2 -> n*d)."""
    d = d_model(m)
    dff = m.config.intermediate_size
    macs = 4 * d * d + 2 * d * dff + seq_len * d
    return 2.0 * macs


def head_flops_per_token(m) -> float:
    return 2.0 * d_model(m) * m.config.vocab_size


# ----------------------------------------------------------------------------------------- data

def make_sequences(source: str, n_seqs: int, seq_len: int, split: str, seed: int = 0) -> torch.Tensor:
    """One window per document (avoids within-document dependence between samples).
    source: 'pile' (NeelNanda/pile-10k; docs [0,5000) = 'fit', [5000,10000) = 'eval') or
            'wiki' (WikiText-103 test, article-level).  Returns LongTensor [n_seqs, seq_len] with BOS at 0."""
    from datasets import load_dataset

    tok = tokenizer()
    rng = np.random.default_rng(seed)
    if source == "pile":
        ds = load_dataset("NeelNanda/pile-10k", split="train")
        idx = np.arange(0, 5000) if split == "fit" else np.arange(5000, 10000)
        texts = (ds[int(i)]["text"] for i in rng.permutation(idx))
    elif source == "wiki":
        ds = load_dataset("Salesforce/wikitext", "wikitext-103-raw-v1", split="test")
        arts, cur = [], []
        for line in ds["text"]:
            if line.startswith(" = ") and not line.startswith(" = = ") and cur:
                arts.append("".join(cur)); cur = []
            cur.append(line)
        arts.append("".join(cur))
        texts = (arts[int(i)] for i in rng.permutation(len(arts)))
    else:
        raise ValueError(source)
    # One window per document for the Pile; WikiText-103 test has only ~60 long articles, so up to two
    # non-overlapping windows per article are taken there (deviation D1, logged before any confirmatory result).
    per_doc = 2 if source == "wiki" else 1
    out = []
    for t in texts:
        ids = tok(t)["input_ids"]
        for w in range(per_doc):
            chunk = ids[w * (seq_len - 1): (w + 1) * (seq_len - 1)]
            if len(chunk) < seq_len - 1 or len(out) == n_seqs:
                break
            out.append([BOS_ID] + chunk)
        if len(out) == n_seqs:
            break
    if len(out) < n_seqs:
        raise RuntimeError(f"only {len(out)} sequences available")
    return torch.tensor(out, dtype=torch.long)


def seq_hash(x: torch.Tensor) -> str:
    return hashlib.sha1(x.numpy().tobytes()).hexdigest()[:12]


# ----------------------------------------------------------------------------------------- model internals

def residuals(m, ids: torch.Tensor):
    """Return (list of L+1 residual tensors [B,T,d], logits [B,T,V])."""
    L = n_layers(m)
    store = [None] * (L + 1)
    hooks = []

    def pre0(mod, args, kwargs):
        store[0] = args[0] if args else kwargs["hidden_states"]

    hooks.append(m.gpt_neox.layers[0].register_forward_pre_hook(pre0, with_kwargs=True))
    for i, layer in enumerate(m.gpt_neox.layers):
        def post(mod, args, out, i=i):
            store[i + 1] = out[0] if isinstance(out, tuple) else out
        hooks.append(layer.register_forward_hook(post))
    try:
        logits = m(input_ids=ids).logits
    finally:
        for h in hooks:
            h.remove()
    return store, logits


@contextlib.contextmanager
def sliced(m, k: int):
    full = m.gpt_neox.layers
    m.gpt_neox.layers = torch.nn.ModuleList(list(full)[k:])
    try:
        yield m
    finally:
        m.gpt_neox.layers = full


def run_upper(m, H: torch.Tensor, k: int) -> torch.Tensor:
    """Run blocks k..L-1, final LN and unembedding on residual states H (input to block k)."""
    if k == n_layers(m):
        return m.lm_head(m.gpt_neox.final_layer_norm(H))
    with sliced(m, k):
        return m(inputs_embeds=H).logits


def run_skip(m, H: torch.Tensor, start: int, stop: int, k_out: int) -> torch.Tensor:
    """Utility: blocks [start, stop) applied to H (returns residual, no head)."""
    full = list(m.gpt_neox.layers)
    x = H
    pos = torch.arange(H.shape[1]).unsqueeze(0)
    pe = m.gpt_neox.rotary_emb(x, position_ids=pos)
    for layer in full[start:stop]:
        o = layer(x, position_ids=pos, position_embeddings=pe)
        x = o[0] if isinstance(o, tuple) else o
    return x


# ----------------------------------------------------------------------------------------- metrics

def token_metrics(logits_ref: torch.Tensor, logits: torch.Tensor, ids: torch.Tensor):
    """Per-token metrics on positions 1..T-2 predicting tokens 2..T-1 (excludes BOS position).
    Returns dict of 1-D float tensors: kl (ref||q), tv, acc (1-TV, = speculative acceptance prob),
    top1 (argmax agreement), ce (cross-entropy of q on true next token)."""
    lp = torch.log_softmax(logits_ref[:, 1:-1].float(), -1)
    lq = torch.log_softmax(logits[:, 1:-1].float(), -1)
    p = lp.exp(); q = lq.exp()
    kl = (p * (lp - lq)).sum(-1)
    tv = 0.5 * (p - q).abs().sum(-1)
    top1 = (lp.argmax(-1) == lq.argmax(-1)).float()
    tgt = ids[:, 2:]
    ce = -lq.gather(-1, tgt.unsqueeze(-1)).squeeze(-1)
    return {k: v.reshape(-1) for k, v in dict(kl=kl, tv=tv, acc=1 - tv, top1=top1, ce=ce).items()}


def save_json(obj, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, indent=1)
