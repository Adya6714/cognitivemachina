# Theoretical analysis for cross-scale state injection (Agent 3)

Status: analysis written before confirmatory experiments. Propositions 1–2 are elementary and stated for
precision, not claimed as novel results.

## Setup
Target model T with blocks B_1..B_L, embedding E, final LayerNorm + unembedding H_T. Write
T = H_T ∘ U_k ∘ D_k with D_k = B_k∘…∘B_1∘E (bottom), U_k = B_L∘…∘B_{k+1} (top). A source model S
produces residual states s_t = S_{≤j}(x_{≤t}) at layer j. A *stitched model* is
  q_{k,A}(· | x_{≤t}) = softmax( H_T( U_k( A s_{1..t} ) )_t ),
where A is a per-position affine map applied to every position, and U_k uses causal attention over the
injected sequence.

Quantity of interest: the gap G(k) = min_A E_t KL( p_T(·|x_{≤t}) || q_{k,A}(·|x_{≤t}) ), compared with the
small model's own distribution p_S and with a *distilled linear head* on s (the k = L case, where U_L = id and
the map + T's head is a linear read-out of s).

## Proposition 1 (no information bottleneck — the gap is computational)
If the map x_{≤t} ↦ (s_1, …, s_t) is injective (true whenever the token embedding is injective and the
residual stream carries it forward with nonzero weight, which holds generically for real-valued weights), then
there exists a (generally non-affine) function F with p_T(·|x_{≤t}) = F(s_1..s_t). Hence the
information-theoretic lower bound on G(k) is 0 for every k, and any measured gap reflects the *computational
accessibility* of the information to an affine map followed by U_k — not missing information.
*Consequence:* claims of the form "small-model latents contain the large model's information" are vacuous
unless the reading function's capacity is fixed. We fix it to affine.

## Proposition 2 (monotonic capacity in the read-out, not in k)
For fixed A the function class {U_k ∘ A} is neither nested nor monotone in k: deeper injection (larger k)
removes computation that could exploit s, while shallower injection forces s to be expressed in an earlier
coordinate system. Therefore G(k) can have an interior minimum. An interior minimum strictly below
G(L) is the operational signature of H1 ("the small model computes something the large model's upper layers
can use beyond a linear read-out"). If argmin_k G(k) = L, the small model's state is no more useful to T's
upper layers than to a linear head — H1 in its useful form is false for that pair.

## Proposition 3 (acceptance and speculative decoding)
For one-token-ahead speculative sampling with draft q and target p, the acceptance probability at a context is
1 − TV(p, q) (Leviathan et al. 2023; Chen et al. 2023), and Pinsker gives TV ≤ sqrt(KL/2). Output
guarantees are provided by the verification rule, independently of how q was produced; so H2's
"preserving guarantees" is automatic for any drafter verified by exact rejection sampling. The open part of
H2 is only *efficiency*: expected tokens per target call versus draft cost. A stitched drafter costs
C(S) + C(U_k) per drafted token; a self-drafter that runs T's bottom m blocks + head (early exit) costs
C(D_m) + C(head). The relevant comparison is therefore acceptance at matched draft cost, which we report.

## Prediction register (made before confirmatory runs)
* If small models behave like shallow versions of large models (the "S ≈ D_k" picture), G(k) should be
  minimised at an intermediate k* whose relative depth k*/L grows with the size of S.
* If representational similarity tracked function, argmax_k R²(A s, R_k) ≈ argmin_k G(k).
* Null: argmin_k G(k) = L for all pairs (no usable prefix), and similarity argmax unrelated to function.
