# 02 — Literature matrix and novelty audit (Agent 2)

Date of audit: 2026-11-24. Search window: up to and including November 2026.
Every paper below was retrieved during this session from the arXiv Atom API or OpenAlex. The identifier given (arXiv id, DOI or OpenAlex W-id) is the one returned by the API. Read depth is stated per paper. "Full (targeted)" means I downloaded the PDF, extracted the text with pypdf, and read the method, setup and results sections relevant to our questions. It does not mean I read every page.

**Novelty scale used here.**
- N0: established, already done.
- N1: minor variation of published work.
- N2: systematic extension or new measurement with a known technique. The publishable value lies in rigour and scope.
- N3: new question or comparison with partial precedent. The core result is not in the literature.
- N4: substantially new direction with only loose precedent.
- N5: no meaningful precedent.

---

## 1. Search log

**APIs used**
- arXiv Atom API (`export.arxiv.org/api/query`). Fielded queries (`ti:`, `abs:`, `all:`), sorted by relevance.
- OpenAlex `/works?search=` (relevance over title, abstract and full text, filtered by publication year). OpenAlex `filter=cites:` for forward citations.
- Semantic Scholar: every call returned HTTP 429 (rate limited) despite retries with 6 s backoff, so no S2 results are used. The research-desk reference-lookup MCP loaded, but its hosted backend failed to connect. OpenAlex was used directly in its place.

**Forward-citation crawls (OpenAlex `cites:`), run 2026-11-24**

| Seed | OpenAlex id | Cited-by count | Use |
|---|---|---|---|
| Chen et al. 2025, *Transferring Linear Features…* | W4415932906 | 33 | Main crawl for cross-scale stitching follow-ups |
| Bansal et al. 2021, *Revisiting Model Stitching* | W3166956420 | 102 | Stitching methodology follow-ups |
| Oozeer et al. 2025, *Activation Space Interventions…* | W4416113472 | 17 | Cross-model transfer follow-ups |
| Nair/P S et al. 2024, *Tandem Transformers* | W4391871631 | 14 | Cross-size hidden-state coupling for drafting |
| Pal et al. 2023, *Future Lens* | W4389521021 | 159 | A12 follow-ups |
| Wu et al. 2024, *Do LMs plan ahead* | W4393726172 | 51 | A12 follow-ups |

The forward-citation crawls of the stitching seeds surfaced the most dangerous 2026 papers: 2603.18908, 2608.09521, 2606.03280, 2608.03893 and 2604.06377. Keyword search alone did not find them.

**Query table** (2026-11-24; hit count = API `totalResults` or OpenAlex `meta.count`). The first four arXiv queries were run before logging to file. Their counts were: `all:"model stitching" AND all:language` = 10; `ti:"Transferring Features Across Language Models"` = 0 (the true title has "Linear"; found by the first query); `ti:"Tandem transformers"` = 1; `ti:"activation space interventions transfer"` = 0 (found with `ti:"Activation Space Interventions"`).

| API | Query | Hits |
|---|---|---|
| arXiv | `all:stitching AND all:"language models" AND all:layers` | 13 |
| arXiv | `abs:"small model" AND abs:"hidden states" AND abs:"large model" AND abs:"speculative"` | 0 |
| arXiv | `abs:"cross-model" AND abs:speculative AND abs:"hidden state"` | 0 |
| arXiv | `all:"Platonic representation hypothesis"` | 63 |
| arXiv | `ti:"Activation Space Interventions"` | 1 |
| arXiv | `abs:"layer correspondence" AND abs:"language models"` | 6 |
| arXiv | `ti:"secretly linear"` | 2 |
| arXiv | `ti:"unreasonable ineffectiveness of the deeper layers"` | 1 |
| arXiv | `ti:LayerSkip` | 1 |
| arXiv | `ti:"tuned lens"` | 2 |
| arXiv | `abs:Pythia AND abs:"representational similarity" AND abs:scale` | 1 |
| arXiv | `abs:"model stitching" AND abs:transformer AND abs:layer` | 3 |
| arXiv | `abs:"representation transfer" AND abs:"smaller model" AND abs:"larger model" AND abs:"residual stream"` | 0 |
| arXiv | `ti:"Revisiting model stitching"` | 2 |
| arXiv | `abs:"affine" AND abs:"stitching" AND abs:"Pythia"` | 0 |
| arXiv | `ti:"Jump to conclusions"` | 2 |
| arXiv | `ti:ReplaceMe` | 1 |
| arXiv | `abs:"layer pruning" AND abs:"linear transformation" AND abs:replace` | 0 |
| arXiv | `ti:"LLM-Streamline"` | 0 (found via OpenAlex as 2403.19135) |
| arXiv | `ti:"Big Little Decoder"` | 1 |
| arXiv | `ti:Kangaroo AND abs:speculative` | 2 |
| arXiv | `ti:"Draft & Verify"` | 3 |
| arXiv | `abs:"self-speculative" AND abs:"layer skipping"` | 9 |
| arXiv | `ti:EAGLE AND abs:speculative` | 7 |
| arXiv | `ti:"GLIDE with a CAPE"` | 1 |
| arXiv | `abs:"harmonized" AND abs:speculative AND abs:"representation"` | 3 |
| arXiv | `ti:Medusa AND abs:decoding` | 4 |
| arXiv | `ti:"Falcon" AND abs:"semi-autoregressive" AND abs:speculative` | 1 |
| arXiv | `ti:"Future Lens"` | 1 |
| arXiv | `ti:"Do language models plan ahead"` | 1 |
| arXiv | `ti:"relative representations enable zero-shot latent space communication"` | 1 |
| arXiv | `ti:"Similarity of neural network representations revisited"` | 1 |
| arXiv | `ti:"Understanding image representations by measuring their equivariance"` | 1 |
| arXiv | `ti:"Better & Faster Large Language Models via Multi-token Prediction"` | 1 |
| arXiv | `ti:"Fast Inference from Transformers via Speculative Decoding"` | 1 |
| arXiv | `ti:"Accelerating Large Language Model Decoding with Speculative Sampling"` | 1 |
| arXiv | `abs:"speculative decoding" AND abs:"acceptance" AND abs:"i.i.d."` | 2 |
| arXiv | `abs:"speculative decoding" AND abs:"acceptance rate" AND abs:"position" AND abs:"variance"` | 1 |
| arXiv | `abs:"speculative decoding" AND abs:"acceptance" AND abs:"correlat" AND abs:"token"` | 0 |
| arXiv | `abs:"speculative decoding" AND abs:"expected" AND abs:"accepted" AND abs:"model" AND abs:"analysis"` | 8 |
| arXiv | `abs:"draft" AND abs:"feature loss" AND abs:"speculative"` | 0 |
| arXiv | `abs:"future tokens" AND abs:"hidden state" AND abs:"linear" AND abs:"probe"` | 0 |
| arXiv | `abs:"stitching" AND abs:Mamba` | 3 (none relevant) |
| arXiv | `abs:Mamba AND abs:transformer AND abs:"representation" AND abs:"similarity" AND abs:"universality"` | 0 |
| arXiv | `abs:Pythia AND abs:checkpoints AND abs:"representational similarity"` | 2 |
| arXiv | `abs:Pythia AND abs:"across model sizes" AND abs:CKA` | 0 |
| arXiv | `abs:"convergence" AND abs:"representations" AND abs:"during training" AND abs:"Pythia"` | 2 |
| arXiv | `ti:stitching AND (abs:LLM OR abs:"language model")` | 24 |
| arXiv | `ti:stitch AND abs:"language model"` | 16 |
| arXiv | `abs:"stitched model" AND abs:"language model"` | 1 |
| arXiv | `(ti:grafting OR ti:transplant) AND abs:"language model" AND abs:layers` | 3 |
| arXiv | `abs:"smaller model" AND abs:"upper layers" AND abs:"larger model"` | 0 |
| arXiv | `abs:"cross-model" AND abs:"hidden states" AND abs:"speculative decoding"` | 0 |
| arXiv | `abs:"speculative decoding" AND abs:"draft model" AND abs:"hidden states" AND abs:"projection" AND abs:"target model" AND abs:"layers"` | 1 |
| arXiv | `abs:"layer" AND abs:"injection" AND abs:"different sizes" AND abs:"language models"` | 0 |
| arXiv | `abs:"cross-scale" AND abs:"language models" AND abs:"representations"` | 14 (none relevant) |
| arXiv | `abs:"same family" AND abs:"affine" AND abs:"hidden states"` | 0 |
| arXiv | `abs:"latent" AND abs:"communication" AND abs:"between language models" AND abs:"hidden states"` | 1 |
| arXiv | `ti:"LLM Augmented LLMs"` / `ti:"Relay Decoding"` / `ti:"hidden transfer" AND abs:decoding` | 1 / 1 / 1 |
| arXiv | `abs:"small model" AND abs:"bottom layers" AND abs:"large model"` | 0 |
| arXiv | `abs:"early layers" AND abs:"small model" AND abs:"large language model" AND abs:"replace"` | 0 |
| arXiv | `ti:"HeteroSpec"` / `ti:"Decoding Speculative Decoding"` / `ti:"SpecDec++"` | 1 / 2 / 2 |
| arXiv | `ti:"theoretical perspective" AND abs:"speculative decoding"` | 2 |
| arXiv | `abs:"speculative" AND abs:"acceptance" AND abs:"Markov"` | 8 |
| arXiv | `abs:"speculative decoding" AND abs:"acceptance" AND abs:"heterogeneous"` | 11 |
| arXiv | `abs:"speculative decoding" AND abs:"acceptance rate" AND abs:"varies"` | 10 |
| arXiv | `abs:"draft" AND abs:"hidden state" AND abs:"regression" AND abs:"token-level" AND abs:speculative` | 0 |
| arXiv | `ti:GRIFFIN AND abs:speculative` / `ti:"LK Losses"` | 1 / 1 |
| arXiv | `abs:"EAGLE" AND abs:"feature" AND abs:"loss" AND abs:"ablation"` | 0 |
| arXiv | `abs:"future tokens" AND abs:"residual stream"` | 1 (irrelevant) |
| arXiv | `abs:"speculative" AND abs:"acceptance" AND abs:"independent" AND abs:"assumption"` | 6 |
| arXiv | `abs:"speculative decoding" AND abs:"geometric"` | 12 |
| arXiv | `abs:"speculative decoding" AND abs:"empirical" AND abs:"acceptance" AND abs:"distribution"` | 14 |
| arXiv | `ti:"Transformers to SSMs"` / `ti:"Mamba in the Llama"` / `ti:"Mamba Drafters"` | 3 / 1 / 1 |
| arXiv | `abs:Mamba AND abs:Pythia AND abs:representations AND abs:layers` | 1 |
| arXiv | `abs:"universality" AND abs:"Pythia" AND abs:"checkpoints"` | 2 |
| arXiv | `abs:"model stitching" AND abs:"training dynamics"` | 0 |
| arXiv | `abs:stitching AND abs:CKA AND abs:functional` | 2 |
| OpenAlex | `stitching small language model into large language model layers` | 17,602 (top 12 inspected) |
| OpenAlex | `cross-scale model stitching language models` | 20,124 (top 12) |
| OpenAlex | `small model hidden states large model speculative decoding draft` | 1,952 (top 12) |
| OpenAlex | `layer correspondence across model sizes language models` | 78,152 (top 12) |
| OpenAlex | `hidden state transfer between language models of different sizes` | 211,649 (top 12) |
| OpenAlex | `affine map between residual streams of different language models` | 4,585 (top 12) |
| OpenAlex | `cross-model latent speculative decoding` | 6,918 (top 12) |
| OpenAlex | `speculative decoding acceptance rate heterogeneity per-token analysis expected accepted length` | 104 (top 10) |
| OpenAlex | `speculative decoding acceptance correlation bursty tokens analysis` | 10 |
| OpenAlex | `draft head feature regression loss versus token loss speculative decoding ablation` | 243 (top 10) |
| OpenAlex | `future token prediction from hidden states linear probe model scale` | 9,032 (top 10) |
| OpenAlex | `stitching Mamba transformer cross-architecture representations` | 444 (top 10; none relevant) |
| OpenAlex | `universality mechanistic similarity Mamba transformer sparse autoencoder` | 114 (top 10) |
| OpenAlex | `representational similarity across model sizes during training Pythia checkpoints` | 226 (top 10) |
| OpenAlex | `cross-model representation alignment emerges during training` | 210,393 (top 10) |
| OpenAlex | `layer-wise representational similarity language models different sizes CKA` | 665 (top 10) |
| OpenAlex | `small language model replaces lower layers of large language model linear adapter` | 13,473 (top 10; none relevant) |
| OpenAlex | `speculative decoding small model hidden states fed into target model upper layers` | 305 (top 10) |
| OpenAlex | `weak-to-strong hidden state transfer language models layers` | 52,450 (top 10) |
| OpenAlex | `composing language models by connecting intermediate layers across sizes` | 24,273 (top 10; found NinaXander) |
| OpenAlex | `replace lower layers of target model with small draft model hidden states speculative decoding` | 822 (top 10) |
| OpenAlex | `lightweight model approximates early layers of large language model for acceleration` | 12,578 (top 10) |
| OpenAlex | `layer substitution between language models of different sizes` | 118,758 (top 10) |
| OpenAlex | `small model predicts intermediate hidden states of large language model` | 46,732 (top 10) |
| OpenAlex | `stitched language model next token loss injection layer sweep` | 77 (top 10) |
| OpenAlex | `probing future token predictions in hidden states across model sizes` | 10,271 (top 10) |
| OpenAlex | `linear probe predicting tokens several steps ahead language model scaling` | 2,382 (top 10) |

The large OpenAlex counts come from bag-of-words full-text matching. Only the top-ranked rows were inspected, so a count is not a measure of relevant hits.

**Coverage caveats**
- Semantic Scholar was unavailable (rate limited). Google Scholar, conference proceedings not indexed by OpenAlex, workshop papers, and blog posts (LessWrong, Alignment Forum, Transformer Circuits) were not searched. Cross-model stitching results often appear first in those venues, so a false "not found" remains possible for Q-A1(i) and Q-A1(iii).
- arXiv fielded search is literal. Paraphrased abstracts can be missed, which is why the OpenAlex and forward-citation passes were added.

---

## 2. Literature matrix

Abbreviations: CE = next-token cross-entropy; SD = speculative decoding.

| Paper (authors, year, venue / id) | Research question | Method | Main finding | Limitations | Relevance | Read depth |
|---|---|---|---|---|---|---|
| Chen, Merullo, Stolfo, Pavlick 2025, NeurIPS 2025 (DOI 10.52202/085713-1621), arXiv 2506.06609 | Can affine maps between residual streams of different-size same-family LMs transfer SAEs, probes and steering vectors? | Affine "stitches" in both directions (up T↑ and down T↓). Trained with MSE plus an inversion penalty, **not** with next-token loss. Activations from 180k OpenWebText samples (context 512; 128 for Gemma). For a fixed source layer, the target layer is chosen by **argmax SVCCA** (App. A.1; Fig. 6 shows SVCCA against every target layer). Pairs: pythia-70m-deduped.L3 → pythia-160m-deduped.L4; gpt2-small.L6 → gpt2-medium.L10; gemma-2-2b.L20 → gemma-2-9b.L33. | Stitched downstream CE is reported for **one layer pair per family** (Table 1). Pythia A→B is 3.99 vs native B 3.14 (+27%). GPT-2 is 3.08 vs 2.77 (+11%). Gemma is 3.28 vs 2.36 (+39%). SAE transfer used as initialisation saves about 50% of FLOPs. Probes and steering vectors transfer. | No sweep over injection depth. No sweep over size pairs (one pair per family). Stitch trained on MSE, not on downstream loss. Layer correspondence is chosen representationally (SVCCA) and never checked functionally. No self-model baseline. No drafting or efficiency use of the stitched model. | **A1/A2 (i), (ii)**: closest prior work | Full (targeted: §1–2, Table 1, App. A, A.1, A.2) |
| Gorbett & Jana 2026, arXiv 2603.18908 (*Ventriloquist LLMs*) | Can an affine map let one model's hidden states be read by another model's frozen output head? | Ridge/OLS affine maps between **final** hidden states of independent models (Qwen, Llama, Gemma, Mistral, OLMo; 270M–30B), evaluated on classification, OOD detection and greedy generation. §4 adds a depth sweep (L/4, L/2, 3L/4, h[−2], h[−1], last) for Qwen2.5-7B ↔ Llama-3-8B on MMLU. | Generation across models works sometimes. It depends on tokenizer overlap and source scale, and strong→weak works better than weak→strong. In the depth sweep, intermediate layers give 0% accuracy and accuracy appears only in the last 1–2 blocks: "a late-stage, output-space phenomenon". | Cross-family with different tokenizers. The text says intermediate maps are "evaluated by greedy mapped generation through the target LM head". It is ambiguous whether the target's remaining layers are run. Six depths, one pair, N=100 questions. Perplexity analysis has N=3–4. | **A1/A2 (i), (ii)**: shows the final layer of one model maps to the *final* layer of another. Partly pre-empts the "small final layer ↔ which large layer" question, but cross-family and not cross-scale within one family. | Full (targeted: abstract, §4 depth sweep, Table 3) |
| Kim, Mun, Han 2026, arXiv 2608.09521 (*One Adapter Pair per Model: Universal Activation Bus*) | Can a shared activation space with one linear encoder/decoder per model make probes, SAEs and NLAs portable, and can another model's upper layers "execute" translated states? | A shared dense space plus a linear adapter pair per model (Llama-3.2-3B, Qwen3-4B, SmolLM2-1.7B, Falcon3, OLMo-2-7B; Qwen2.5-7B as carrier). Cut at **normalized depth 0.5 only**. §6 "front–back composition": A's cut-layer state is translated and inserted into B's layer, and B's frozen upper layers produce the next token. | The composed model agrees with native B on 72–88% of next tokens. "Execution follows the back model". Next-token CE results are in App. D. | Single cut depth. Different-family models of similar size (1.7B–7B), not a controlled cross-scale family. No depth sweep, no FLOP accounting, no self-baseline. | **A1/A2 (i)**: demonstrates mid-depth cross-model injection into frozen upper layers works for next-token prediction | Full (targeted: abstract, §6, Table 8 setup) |
| Zhang & Xin 2026, arXiv 2606.03280 (*A Negative Result on Cross-Model Activation Transfer in a Pythia Multi-Hop Setting*) | Can a sender LM pass a useful intermediate reasoning state to a receiver through a linear bridge? | Pythia-160M → Pythia-410M. Linear translator from sender layer 8 to receiver layer 16 (fixed relative depth 0.67). Additive and replacement injection, scale-corrected variants, self-injection, random and shuffle controls. Multi-hop QA. | Normalised cosine about 0.97 offline, but **replacement injection is consistently destructive** and additive injection is null. Offline alignment does not give causal usability. | One pair, one depth, a task-accuracy metric (not LM loss), and the full prompt is also given to the receiver. | **A1/A2**: dangerous. Same family, same models and the same replacement-injection operation, with a negative result. Our study must explain the discrepancy (task vs LM loss, depth, MSE vs downstream-trained map). | Full (targeted: abstract, §1, §3 setup) |
| Kotama, Hayashi, Mukunoki, Hoshino 2026, arXiv 2609.38261 (*NinaXander*) | Can frozen LMs from different architecture families be composed by switching at a layer with one shared-latent adapter? | RWKV-4-Raven-7B ↔ Tulu-Pythia-6.9B (same tokenizer, depth 32, same width). One adapter shared across all switch layers. Composed models are evaluated at several switch layers (MCQ accuracy, WikiText LM). **Linear CKA and fitted R² over all 32×32 layer pairs**, plus an affine control and nonlinearity ablations. | Pythia first 5 layers + RWKV remaining 27 matches RWKV accuracy with an 84% KV-cache cut. No composed model matches Pythia. WikiText LM degrades sharply. The affine control is close to the nonlinear adapter. | Same size and depth (not cross-scale). One favourable pair. | **B8** (closest to transformer↔recurrent stitching), **A1 (ii)** (gives representational CKA/R² alongside a functional switch-layer sweep, but not cross-scale) | Full (targeted: abstract, §III-C, §IV grep of the CKA/R² and switch-layer analyses) |
| P S, Nair, Samaga, Boyd et al. 2024, arXiv 2402.08644 (*Tandem Transformers*) | Can a small AR model improve by attending to a large model's representations, for inference efficiency? | The small model (PaLM2-Gecko) attends, via a projection and a layer assignment π: [L_S]→[L_L], to large-model (PaLM2-Bison) representations of earlier blocks. The large model runs in block mode. Used inside SPEED speculative decoding. | +3.3% next-token accuracy over Gecko. 1.16× faster than Otter at comparable quality. About 1.14× faster than vanilla Gecko in SPEED. | The direction is **large→small** (the small model consumes large-model states). Trained jointly. Not open (PaLM2). | **A1 (iv)**: closest drafting design, but the opposite direction of information flow | Full (targeted: §1–3) |
| Bansal, Nakkiran, Barak 2021, arXiv 2106.07682 | Is stitching a better representational-comparison tool than CKA? | Bottom of A + 1×1 conv/linear stitch + top of B, trained on task loss (vision CNNs/ResNets). | Stitching reveals what CKA cannot. Representations from more data, more width or more training can be "plugged into" weaker models. | Vision only. Stitch trained on task loss. | **A1 (ii)** foundational | Abstract |
| Lenc & Vedaldi 2014/15, arXiv 1411.5908 | Equivariance and equivalence of CNN representations | Learned maps between CNN layers ("Franken-CNN" stitching) | Early layers of different CNNs are interchangeable | Vision only | A1 foundational | Abstract (title only verified) |
| Balogh & Jelasity 2024, arXiv 2412.11299 | Is task-loss stitching a valid similarity index? | Compare task-loss matching against direct (MSE) matching stitches | Task-loss matching can rate **distant layers as more similar than corresponding layers**, and even a layer as less similar to itself. | Vision. | **A1 (ii)**: methodological threat. A downstream-loss-trained affine map can hide correspondence. | Abstract |
| Almudévar & Ortega 2026, arXiv 2601.21568 | Link functional (stitching) and representational similarity | Usable-information framework | Stitching is asymmetric. Representational similarity is sufficient but not necessary for functional similarity. | Theory plus small experiments | **A1 (ii)** framing | Abstract |
| Mai et al. 2026, arXiv 2603.12433 (*Revisiting Model Stitching in the Foundation Model Era*) | Are heterogeneous vision foundation models stitchable? | Systematic sweep over stitch points, stitch families and losses | MSE at the stitch point fails at shallow points. Matching at the target's penultimate layer works. Deep stitches can beat both models. | Vision | A1: methodological precedent for sweeping stitch depth and for which loss the stitch should use | Abstract |
| Yom Din, Karidi, Choshen, Geva 2023, arXiv 2303.09435 (*Jump to Conclusions*) | Can linear maps from layer ℓ to the final layer short-cut transformers? | Linear maps h_ℓ → h_L (GPT-2, BERT; several scales) | Better than the logit lens. Useful for early exit (saves about 7.9% more layers for GPT-2). | Maps to the *final* layer, not into intermediate layers for continued computation | **A1 (iii)**: the "self linear shortcut" baseline exists | Abstract |
| Shopkhoev et al. 2025, arXiv 2505.02819 (*ReplaceMe*) | Training-free depth pruning by replacing a block range with a linear map | Least-squares linear map over a pruned contiguous block range, fused into weights | About 25% pruning with about 90% of performance retained, no healing | Prunes middle/deep blocks, not the prefix | **A1 (iii)**: self-skip-with-linear-map baseline | Abstract |
| Chen et al. 2024/25, arXiv 2403.19135 (*LLM-Streamline*, ICLR 2025) | Layer pruning with a learned lightweight replacement | Replaces pruned consecutive layers with a small trained network | Beats prior pruning | Self-model only | **A1 (iii)** | Abstract |
| Gromov et al. 2024, arXiv 2403.17887 | How many deep layers can be pruned? | Similarity-based block pruning plus QLoRA healing | Up to about half of the layers removable with small QA degradation | QA benchmarks, not LM loss | A1 (iii) background | Abstract |
| Razzhigaev et al. 2024, arXiv 2405.12250 (*Your Transformer is Secretly Linear*) | Linearity between consecutive layers | Procrustes similarity between sequential layers | About 0.99 linearity. Linear replacement of some blocks barely hurts | Adjacent layers only | A1 (iii) background | Abstract |
| Elhoushi et al. 2024, arXiv 2404.16710 (*LayerSkip*) | Early exit plus self-speculation | Layer dropout plus early-exit loss. The draft is the model's own prefix. | Self-speculative speedups | Needs training recipe changes | **A1 (iii)/(iv)**: the self-prefix drafting baseline | Abstract (title) |
| Liu et al. 2024, arXiv 2404.18911 (*Kangaroo*) | Self-speculation from a shallow sub-network | Fixed shallow prefix of the target plus a trained adapter → LM head | Lossless self-speculative speedup | Self-model prefix | **A1 (iii)/(iv)**: closest "own prefix + adapter" drafter | Abstract |
| Zhang et al. 2023, arXiv 2309.08168 (*Draft & Verify*) | Self-speculation by skipping layers | Bayesian-optimised layer-skip set | Lossless speedup | — | A1 (iv) | Title/abstract |
| Li et al. 2024, arXiv 2401.15077 (*EAGLE*) | Feature-level AR drafting | Draft head predicts the next second-to-top feature from (feature, shifted token). Loss = feature regression + token CE. | 2.7–3.5× on LLaMA2-Chat 70B | Feature-uncertainty argument | **A4**, A1 (iv) | Abstract |
| Li et al. 2025, arXiv 2503.01840 (*EAGLE-3*) | Why EAGLE does not scale with data | Removes the feature-prediction loss l_fea, adds "training-time test", fuses low/mid/high features | Stated reason: "feature prediction can be seen as an additional constraint, which limits the expressiveness of the draft model and makes it difficult to benefit from increased data". Ablation (LLaMA-Instruct-3.1-8B, MT-bench): EAGLE-2 3.16×/τ 4.05 → "+remove fea con" 3.82×/5.37 → "+fused features" 4.40×/6.13. | **The ablation confounds removing l_fea with adding training-time test**, which is needed once l_fea is gone. Single target model. No matched-capacity or matched-data comparison of feature vs token targets. | **A4**: key | Full (targeted: §3 motivation, §4.2 ablation, Table 2) |
| Zhang et al. 2024, arXiv 2408.15766 (*HASS*, ICLR 2025) | Harmonised training for EAGLE-style drafters | Harmonised objective distillation (top-K) plus context alignment. **Keeps** l_fea. | 2.81–4.05× (LLaMA). 8–20% over EAGLE-2. | — | A4 | Abstract (PDF downloaded, not read) |
| Du et al. 2024, arXiv 2402.02082 (*GliDe with a CaPE*) | Draft reuses the target's KV cache | Glimpse draft plus proposal expansion | Faster SD | — | A1 (iv) / A4 background | Title only |
| Cai et al. 2024, arXiv 2401.10774 (*Medusa*) | Multiple decoding heads | Token-level heads on the final hidden state | 2×+ | — | A4 (token-only target baseline) | Title only |
| Gao et al. 2024, arXiv 2412.12639 (*Falcon*) | Semi-AR drafting | Enhanced semi-AR draft plus custom tree | — | — | A4 | Title only |
| Chen et al. 2026, arXiv 2602.21224 (*Make Every Draft Count: Hidden-State based SD*) | Reuse discarded drafts | AR drafting at the hidden-state level with late token injection | Up to 3.3× over standard SD | Self-target features | A1 (iv), A4 | Abstract |
| Valliappan et al. 2026, arXiv 2611.23835 (*NarrowSpec*) | Must the draft width equal the target width? | DFlash/EAGLE-3 drafters at ½ or ¼ width; Qwen3-8B, GPT-OSS-20B | Narrow drafts keep acceptance, 1.06–1.44× | — | A1 (iv) (a small-width model can read the target's states) | Abstract |
| Heo et al. 2026, arXiv 2608.03893 (*Cross-Model KV Cache Transfer in LLM Families*) | Can a larger model reuse a smaller/other model's KV cache through linear maps? | Per-head ridge from top-k source layers to each target layer's K/V (RoPE stripped). Six pairs, three families, e.g. Qwen3 14B→32B. | One source layer explains 56% of key and 32% of value variance (79%/65% with several layers). Retains 73–98% of accuracy on 4 of 6 pairs. 2.7–25× faster than re-prefill. | KV, not residual stream. Prefill only. | **A1 (i)/(iv)**: cross-size linear state transfer for inference efficiency within a family | Abstract |
| Oozeer et al. 2025, arXiv 2503.04429 (ICML 2025) | Transfer steering interventions between LLMs | Learned (autoencoder/affine) maps between activation spaces of Llama, Qwen, Gemma | Steering and backdoor-removal vectors transfer small→large | Behavioural, not LM loss | A1 background | Abstract |
| Bello et al. 2025, arXiv 2506.00653 (*Linear Representation Transferability*) | Is there an affine map between hidden states of different-size models? | Affine maps small→large; steering-vector transfer | Steering survives transfer | Steering only | A1 background | Abstract |
| Balasubramanian et al. 2026, arXiv 2604.06377 (*Master Key Hypothesis*) | Cross-scale capability transfer via low-rank linear alignment | Contrastive capability direction aligned across scales (Qwen) | CoT and maths gains across scales | Steering, not stitching | A1 background | Abstract |
| Huh et al. 2024, arXiv 2405.07987 (*Platonic Representation Hypothesis*) | Do representations converge with scale? | Mutual k-NN alignment across models and modalities | Alignment increases with capability | Kernel-level, not functional | A1, B10 background | Abstract (title) |
| Herbst et al. 2026, arXiv 2611.12869 | Where does PRH alignment emerge across layers? | Layer and dimension analysis with baselines | Alignment metrics are confounded by depth and width. Baselines are needed. | Cross-modal focus | A1 (ii), B10 (metric caveat) | Abstract |
| Kornblith et al. 2019, arXiv 1905.00414 | CKA | — | CKA identifies corresponding layers | — | A1 (ii) foundational | Title |
| Moschella et al. 2022, arXiv 2209.15430 | Relative representations | Anchor-based cosine representations | Zero-shot stitching | — | A1 background | Title |
| Belrose et al. 2023, arXiv 2303.08112 (*Tuned Lens*) | Affine translators layer→final | Per-layer affine probe trained on KL | Better latent predictions than the logit lens | Self-model | A1 (iii), A12 | Title |
| Bansal et al. 2024, arXiv 2401.02412 (*CALM*) | Compose an anchor LLM with an augmenting model | Cross-attention between intermediate layers of PaLM2 models | Capability gains | Not stitching. Both models run fully. | A1 background | Abstract |
| Flamant et al. 2026, arXiv 2605.11167 (*Bicameral Model*) | Couple two frozen LMs via hidden states | Translation network plus gate, run in lockstep | Tool use through a hidden-state channel | Both models run fully | A1 background | Abstract |
| Fu et al. 2024, arXiv 2405.02933 (*Relay Decoding*) | Concatenate two LLMs for MT | Mapping layer between models | MT gains | Task-specific | A1 background | Abstract |
| Univ. of Bologna AMS thesis 2026 (OpenAlex W7154676592) | Inter-family stitching extending Chen et al. | Affine maps / SAEs across Llama 3, Gemma 2, Qwen 2.5 | Hybrid models function with degradation comparable to intra-family stitching | Master's thesis, not peer reviewed | A1 background | Abstract (OpenAlex) |
| Wang et al. 2024/25, arXiv 2410.06672 (*Towards Universality*, ICLR 2025) | Mechanistic similarity of Transformers vs Mambas | SAE feature matching, induction-circuit analysis | Most features are similar. Mamba shows an "off-by-one" motif. | No stitching | **B8** | Abstract |
| Nagaraj et al. 2026, arXiv 2609.24440 | SAE feature correspondence Mamba-130m vs Pythia-70m | SAE Jaccard alignment over 10M tokens | 99.98% of features align | No functional test | **B8** | Abstract |
| Bick et al. 2024, arXiv 2408.10189 (MOHAWK) / Wang et al. 2024, arXiv 2408.15237 (*Mamba in the Llama*) | Distil transformers into SSMs / hybrids | Matrix-mixer alignment, hidden-state alignment, weight reuse | Strong SSMs from transformer teachers | Distillation, not frozen stitching | B8 background | Title |
| Choi et al. 2025, arXiv 2506.01206 (*Mamba Drafters*) | Mamba as an SD drafter | External Mamba draft for transformer targets | Fast drafting | Token-level interface | B8 / A1 (iv) | Abstract |
| Kapoor, Srivastava, Khosla 2025, arXiv 2502.18710 (NeurIPS 2025) | How representational alignment evolves across layers and training | Linear, Procrustes and permutation alignment across dozens of **vision** models and training checkpoints | Nearly all eventual alignment crystallises **within the first epoch** | Vision only | **B10**: closest | Abstract |
| Kishino et al. 2025/26, arXiv 2505.15353 (Findings ACL 2026) | A KL-divergence scale across checkpoints, sizes and layers | Log-likelihood vectors; Pythia trajectories | Behaviour stabilises early. Trajectories are subdiffusive. | Output-space, not hidden states | B10 | Abstract |
| Kim & Lim 2026, arXiv 2611.27911 (*Functional Depth Is Learned*) | How cross-layer dependencies develop during pretraining | Inclusion–exclusion over layer ablations; Pythia, OLMo, Amber checkpoints | Connected coordination strengthens with training | Within-model | B10, A1 (iii) | Abstract |
| Gahtan et al. 2026, arXiv 2609.31098 (*Residual Stream's Effective Depth*) | Effective depth of the residual stream | Similarity-decay diagnostic, 16 LMs plus checkpoints | Pythia-1.4B has a distinct decreasing trajectory | Within-model | B10 | Abstract |
| Leviathan, Kalman, Matias 2022/23, arXiv 2211.17192 (ICML 2023) | Speculative decoding | Rejection-sampling verification | E[#tokens] = (1−α^{γ+1})/(1−α) "if we make the simplifying assumption that the βs are i.i.d." (§3.x). Wall-time analysis likewise assumes i.i.d. | i.i.d. assumption made explicitly | **A3** foundational | Full (targeted: the analysis section around the i.i.d. assumption) |
| Chen et al. 2023, arXiv 2302.01318 | Speculative sampling | Same idea, Chinchilla 70B | 2–2.5× | — | A3 | Title |
| Huang, Guo, Wang 2024, arXiv 2405.19715 (*SpecDec++*) | Adaptive candidate length | MDP formulation plus a trained acceptance-prediction head (llama-2-chat 7B/70B) | Explicitly contrasts with Leviathan's i.i.d. assumption and argues that acceptance correlates with context, shown by the success of the trained head. 2.04× on Alpaca. | Does not quantify the error of the i.i.d. formula itself | **A3**: closest | Full (targeted: related work, discussion) |
| Liu et al. 2025, arXiv 2505.13254 (*HeteroSpec*, ACL 2026) | Exploit verification heterogeneity | Entropy-based stratification of candidates | 4.24× over SOTA. "A small subset of high-confidence predictions accounts for most successful verifications." | Engineering focus | **A3** | Abstract plus grep |
| Yin et al. 2024, arXiv 2411.00841 | SD theory | Markov-chain abstraction, TV distances | Theoretical limits | Theory | A3 | Abstract |
| Wu 2026, arXiv 2608.30427 (*Ceiling-Clipped Acceptance Histograms*) | Do mean accepted lengths hide structure? | Per-cycle acceptance histograms (DFlash/DFlare) | Mean committed length hides a ceiling spike | Block-diffusion drafters | A3 | Abstract |
| Karimi et al. 2026, arXiv 2608.05448 (*DBLAST*) | Positional independence assumption in block drafters | Dependent block drafter | Accepted length degrades with entropy under independence | Block drafters | A3 | Abstract |
| Yan et al. 2024, arXiv 2402.01528 (*Decoding SD*) | What determines SD gains | 350+ experiments (LLaMA-65B, OPT-66B) | Draft latency matters more than draft LM quality | — | A3 | Abstract |
| Samarin et al. 2026, arXiv 2602.23881 (*LK Losses*, ICML 2026) | Direct acceptance-rate objective for drafts | Losses targeting acceptance vs KL | +8–10% acceptance length (8B–685B targets) | Token-level objectives only | **A4** | Abstract |
| Zou et al. 2026, arXiv 2602.05774 (*Variational SD*) | Sequence-acceptance objective | ELBO over draft paths | +9.6% over EAGLE-3 | — | A4 | Abstract |
| Pal et al. 2023, arXiv 2311.04897 (*Future Lens*, CoNLL 2023) | Can one hidden state predict tokens at t+2 and beyond? | Linear approximation plus causal intervention in **GPT-J-6B** only | More than 48% accuracy at some layers for subsequent tokens | Single model, no scale sweep | **A12** | Abstract |
| Wu, Morris, Levine 2024, arXiv 2404.00859 | Pre-caching vs breadcrumbs | Myopic training | Breadcrumbs dominate in LM. **Pre-caching increases with model scale.** | Small scales | **A12** | Abstract |
| Gloeckle et al. 2024, arXiv 2404.19737 (ICML 2024) | Multi-token prediction objective | n future-token heads | Better and faster, especially at scale | Training objective, not decodability | A12 | Title |
| Hanna & Ameisen 2026, arXiv 2604.12493 (*Latent Planning Emerges with Scale*) | Does latent planning grow with scale? | Qwen-3 0.6B–14B, mechanistic features | Planning ability increases with scale | Task-specific (a/an, rhyme) | **A12**: dangerous | Abstract |
| Pochinkov et al. 2025, arXiv 2511.00180 (*ParaScopes*) | What do activations encode about future text? | Residual-stream decoders | About 5+ tokens of future context decodable in small models | — | A12 | Abstract |
| Goel et al. 2026, arXiv 2603.17942 (*ESP*) | Latent multi-token prediction without training | Mask-token probing | Decoder layers align mask-token states with next-token states | — | A12 | Abstract |

---

## 3. Per-question novelty audit

### Q-A1/A2: cross-scale model stitching and state injection (TOP PRIORITY)

**What is demonstrated**
- **Mechanism.** Affine maps between residual streams of different-size same-family LMs exist and allow "start in A, finish in B" next-token prediction.
  - Chen et al. 2506.06609, Table 1: pythia-70m.L3 → pythia-160m.L4 gives CE 3.99 vs 3.14 native.
  - Mid-depth insertion into another model's frozen upper layers works, with 72–88% next-token agreement with the back model (2608.09521 §6; cross-family, half depth only).
- **Layer correspondence by representation.** Chen et al. already computed SVCCA between a fixed small-model layer and *every* large-model layer (App. A.1, Fig. 6, three families). They used the argmax to pick the stitch layer.
  - NinaXander (2609.38261) computed linear CKA and fitted R² over all 32×32 layer pairs, alongside a functional switch-layer sweep. That is same-size and cross-architecture.
- **Final-layer correspondence.** Ventriloquist (2603.18908) shows that the final hidden state of one model maps linearly to the final layer and head of another. Intermediate→head fails (0% at L/4, L/2 and 3L/4).
- **Negative evidence on the exact Pythia setting.** 2606.03280 maps Pythia-160M L8 → Pythia-410M L16 with a linear translator: cosine about 0.97, yet **replacement injection is destructive** on multi-hop QA.
- **Self-linear-shortcut baselines exist.**
  - Linear map layer ℓ → final: Jump to Conclusions 2303.09435; Tuned Lens 2303.08112.
  - Linear replacement of pruned block ranges: ReplaceMe 2505.02819; LLM-Streamline 2403.19135.
  - Own shallow prefix plus adapter as drafter: Kangaroo 2404.18911; LayerSkip 2404.16710.
- **Cross-size linear state transfer for inference efficiency.** Cross-model KV-cache transfer within families (2608.03893). Drafters reading the target's hidden states (EAGLE family; NarrowSpec 2611.23835). Small-reads-large in Tandem (2402.08644).

**What is NOT demonstrated** (not found after the searches logged above)
1. (i) Stitched next-token loss or KL **as a function of injection depth k**, swept over all k and over **many size pairs** in one controlled family (Pythia 70m/160m/410m/1b/1.4b, shared tokenizer and data order). Chen et al. report one (source, target) layer pair per family. 2608.09521 uses one depth. 2606.03280 uses one depth and a task metric. NinaXander sweeps the switch layer, but at equal size and across architectures.
2. (ii) A head-to-head of **functional correspondence** (argmin_k injection loss) against **representational correspondence** (argmax CKA/SVCCA/linear R²) for the small model's final layer and for each of its layers, across scales. Chen et al. used SVCCA only and never checked it functionally. Bansal 2021 and Balogh 2024 show the two can disagree, but in vision.
3. (iii) Cross-model injection vs the large model's **own truncated prefix plus linear shortcut** (layers 0..j of the large model, then an affine map to layer k), **at matched FLOPs**. Each ingredient exists separately. The comparison itself was not found.
4. (iv) "Cross-model latent speculation": a small model produces hidden states that the large model's upper layers consume as a drafter. Not found. Tandem has the opposite direction. EAGLE and Kangaroo use the target's own states or prefix.

**Novelty class**
- **(i): N2.** A systematic depth × size-pair sweep with a known technique. The value lies in being the first controlled map, not in the idea.
- **(ii): N2–N3.** The comparison is new for cross-scale LMs, but the inputs (SVCCA across all layers, stitching vs CKA) are published.
- **(iii): N3** as a framing ("is a small model a better prefix than the large model's own truncated prefix per FLOP?"). Expect reviewers to call it a natural control.
- **(iv): N3** on novelty but low expected value. The cost of running the large model's upper (L−k) layers for every draft token bounds the speedup, and the stitched model will not be distribution-matched. Self-speculation (LayerSkip/Kangaroo) and EAGLE-3 are strong incumbents. Overall question cluster: **N2–N3**.

**Could an existing paper invalidate it?**
- Partly. Chen et al. (2506.06609) already did the core stitch, with CE, on Pythia, and already published a cross-layer SVCCA landscape.
- Ventriloquist (2603.18908) already concluded that alignment is "a late-stage, output-space phenomenon", although for different families and decoding through the head.
- 2606.03280 published a *negative* result for replacement injection in Pythia-160M→410M. If our sweep finds injection works, we must reconcile it: they used a task metric with the full prompt given to the receiver, an MSE-style translator, and one depth. If it fails, we partly replicate them.
- None of these covers the full k × pair sweep or the functional-vs-representational comparison.

**What a domain expert would say is missing or required**
- How the stitch is trained matters a great deal. Compare MSE (Chen) with downstream KL-trained maps, and heed Balogh 2412.11299, which shows task-loss stitches can make distant layers look similar.
- Report KL to the large model and to the small model, not only CE. Include a "small model alone" baseline and the trivial baseline of injecting at k = L (the head only).
- Control for norm and outlier dimensions (massive activations) and for positional/BOS effects.
- Use matched-FLOP accounting.
- Test on held-out distributions (NinaXander and Ventriloquist both saw OOD collapse).
- Run seed variation (PolyPythias) to separate scale effects from seed effects.
- Without these, the work would read as an extension of Chen et al. Table 1.

### Q-A3: acceptance heterogeneity and the error of the i.i.d. formula
- **Demonstrated.**
  - Leviathan et al. (2211.17192) state the i.i.d. assumption explicitly as a simplification.
  - SpecDec++ (2405.19715) explicitly rejects it and shows that a trained head predicts per-token acceptance, which implies context dependence.
  - HeteroSpec (2505.13254) documents "verification heterogeneity".
  - DySpec (2410.11744) links draft confidence to acceptance.
  - Ceiling-clipped histograms (2608.30427) show that mean accepted length hides structure.
  - DBLAST (2608.05448) shows independence assumptions failing in block drafters.
- **Not demonstrated** (not found). A dedicated quantification, on real text across draft/target pairs, of (a) burstiness or autocorrelation of per-token acceptance and (b) the bias of the closed-form E[accepted] = (1−α^{γ+1})/(1−α) relative to the empirical value. It is likely that someone has plotted this in an appendix.
- **Novelty: N1–N2.** Practitioners know that acceptance is context-dependent, and adaptive-γ methods are built on that fact.
- **Expert view.** Useful as a short analysis or note only if it gives a corrected predictor (for example a mixture or Markov model of α) that predicts measured speedups better. Otherwise it is "known in practice".

### Q-A4: feature-level vs token-level targets for draft heads
- **Demonstrated.**
  - EAGLE (2401.15077) uses feature regression plus token CE.
  - EAGLE-3 (2503.01840) removes l_fea, arguing it "limits the expressiveness of the draft model and makes it difficult to benefit from increased data". Its ablation (LLaMA-3.1-8B-Instruct; MT-bench τ 4.05 → 5.37) adds training-time test at the same time, so the effect of the loss is confounded.
  - HASS (2408.15766) keeps l_fea and improves with harmonised distillation.
  - Token-objective refinements: LK losses (2602.23881), Variational SD (2602.05774).
- **Not demonstrated** (not found). A controlled comparison with matched architecture, data and compute, varying only the target (feature MSE, token KL, or a mix), across data scales and target models, with test-time-training held fixed.
- **Novelty: N2.** The gap is real, but the field is crowded, fast-moving and engineering-driven. A careful ablation would be valued but is low-novelty.
- **Invalidation risk.** Moderate. HASS and later EAGLE-3 follow-ups may contain partial ablations that I did not read in full.

### Q-A12: linear decodability of future tokens across scale
- **Demonstrated.**
  - Future Lens (2311.04897): GPT-J-6B only, more than 48% at some layers.
  - Wu et al. (2404.00859): pre-caching increases with scale.
  - Latent Planning Emerges with Scale (2604.12493): Qwen-3 0.6B–14B, mechanistic.
  - ParaScopes (2511.00180): multi-token future content decodable.
  - MTP: 2404.19737; ESP 2603.17942.
- **Not demonstrated.** A clean scaling curve of linear-probe accuracy for t+k (k = 2…8) by layer across a controlled family (Pythia 70m–12b), with a control for n-gram predictability, is not found as a standalone result. Its pieces exist.
- **Novelty: N1–N2.** Expect the expert comment: "Future Lens across Pythia sizes". It needs a baseline of what is predictable from the current token or n-gram statistics alone.

### Q-B8: SSM ↔ transformer stitching
- **Demonstrated.**
  - **NinaXander (2609.38261)** stitches RWKV-4-7B (recurrent) ↔ Pythia-6.9B with a single shared adapter at many switch layers, including a 32×32 CKA/R² map. This covers the core question for an RNN-family model.
  - SAE feature universality between Mamba and Pythia (2410.06672; 2609.24440).
  - Transformer→SSM distillation (2408.10189, 2408.15237).
  - Mamba as an SD drafter (2506.01206).
- **Not demonstrated.** Mamba (selective SSM) ↔ transformer frozen stitching with an affine map and an LM-loss-vs-depth curve was not found. Mamba-130m…2.8b and Pythia share the GPT-NeoX tokenizer and the Pile, so the pairing is natural.
- **Novelty: N2.** It is an architecture swap of NinaXander.

### Q-B10: emergence over training of cross-scale alignment (Pythia checkpoints)
- **Demonstrated.**
  - Vision: alignment crystallises within the first epoch (2502.18710, NeurIPS 2025).
  - Pythia output-space KL stabilises early (2505.15353).
  - Within-model functional-depth dynamics on Pythia checkpoints (2611.27911, 2609.31098).
  - The Platonic hypothesis and its metric caveats (2405.07987, 2611.12869).
- **Not demonstrated.** Cross-*scale* alignment (CKA or stitching loss between Pythia-70m and Pythia-1.4b) tracked over the shared checkpoint schedule was not found.
- **Novelty: N2–N3.** The prior from vision is strong (early crystallisation), so the expected result may be confirmatory. Value increases if it is measured *functionally* (stitch loss), not only with CKA.

### User's own prior work (inferred from repo names and docs/00_decision_log.md; repositories not accessed, since the GitHub API is not enabled for this session)
- `novel_discovery` (read vs recompute of CoT intermediates in toy transformers), `computational_reasoning`, `retrieval-vs-computation` and `reasoning-reliability` concern reasoning reliability. None overlaps with cross-scale stitching, SD acceptance or draft targets.
- `JEPA` (CLIP image↔text embedding alignment) is methodologically adjacent to A1 (a learned map between embedding spaces), but cross-modal, not cross-scale LM injection. **No duplication found** for A1–A4, A12, B8 or B10.

---

## 4. Three most dangerous prior-art papers for Q-A1/A2
1. **Chen, Merullo, Stolfo, Pavlick 2025, arXiv 2506.06609 (NeurIPS 2025).** Same mechanism and same model family (Pythia), with stitched CE and a cross-layer SVCCA landscape. Our work must be framed as the depth × scale × functional extension of it.
2. **Zhang & Xin 2026, arXiv 2606.03280.** Pythia-160M → 410M replacement injection through a linear bridge is destructive. It is a direct negative precedent that we must reproduce and explain.
3. **Gorbett & Jana 2026, arXiv 2603.18908 (Ventriloquist).** Its layer sweep localises linear cross-model compatibility to the final 1–2 layers. That pre-empts the "final-layer correspondence" claim and predicts that mid-depth injection fails. Close behind:
   - Kim et al. 2026, arXiv 2608.09521: mid-depth injection into frozen upper layers works across families.
   - NinaXander, arXiv 2609.38261: switch-layer sweep plus 32×32 CKA/R².
