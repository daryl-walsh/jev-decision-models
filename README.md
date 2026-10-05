# Jev & RLCD, the short version

Four small scripts, about two hours. Four ways to get a typed decision out of a transformer, inference only.

```bash
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements.txt

.venv/bin/python 1_vanilla_decoding.py
.venv/bin/python 2_pure_encoding.py
.venv/bin/python 3_pure_decoding.py
```

`MODEL_ID` picks the decoder (default `Qwen/Qwen3-0.6B`, needs full softmax attention) and
`ENCODER_ID` the encoder (default `answerdotai/ModernBERT-base`).
`TINY=1` swaps in a 2-layer random model — instant, no download, meaningless numbers, right shapes.
F5 in VS Code runs the open file with the project interpreter. `./verify.sh` runs everything.

## 1 — Vanilla decoding

`1_vanilla_decoding.py`

The model writes JSON one token at a time: 23 tokens, 23 forward passes, structure valid only if it
happens to be. It also scores itself by multiplying the probability of each token that wrote a
value — a number that looks like confidence and is junk, for four reasons the script lists.

Everything after this deletes the decode loop.

## 2 — Pure encoding

`2_pure_encoding.py` — what Laya, the open Jev, does

One sequence **per question**, state at the end, a marker token in front of each option:

```
[CLS] instructions [SEP] [MASK] opt0 [MASK] opt1 [SEP] state [SEP]
                         ^^^^^^        ^^^^^^
```

Every token sees every other one, so the state is read with the question in view and the options
are compared against each other. No causal mask, no segment ids, no positions to fake — notice how
little plumbing this needs. The cost is in the first line: the whole state is re-encoded for every
question, and nothing can be cached, because changing the question changes every state vector.

`[MASK]` here is a placeholder **token**, not an attention mask. Files 3 and 4 use the other kind.

## 3 — Pure decoding

`3_pure_decoding.py` — what Jev does

```
[ the state ][ question 0 + its options ][ question 1 + its options ]
  seen by all     sees state + itself        sees state + itself
                  never question 1           never question 0
```

One sequence for everything, one pass, with an attention mask keeping the questions apart. Each
question ends at a decision position — the point where the model is about to write its answer.
Take the vocabulary logits there, keep only the rows for the options you allowed, and softmax over
those. The model's own output head does the scoring, so nothing is trained and nothing can be
generated outside the option set. The state is read once and its KV cache is reusable, because
nothing in it depends on anything after.

```
Is the customer asking for money back?   {'no': 0.052, 'yes': 0.948}
Which team owns this?                    {'billing': 0.975, 'technical': 0.025}
```

## Scoring, and the training that is missing

Files 3 and 4 score through the model's own output head, restricted to the allowed options — the
same readout the open decoder decision models ship. Nothing is trained and the numbers are real.
File 2 cannot borrow that trick: an MLM encoder has no next-token head pointed at the answer slot,
so it uses a parameter-free dot product and its numbers are shape-only.

Production systems replace the output head with a small trained readout and fit it to outcomes with
log loss — a strictly proper scoring rule, minimised only by honest probabilities, which is the
public half of RLCD. `extras/train_the_head.py` does exactly that.

### Encoder or decoder?

Not settled here, and these scripts cannot settle it. What is structural:

- The encoder re-reads the state per question; the decoder reads it once and caches it. The compute
  ranking flips on **how many questions you ask per document**, break-even roughly at the parameter
  ratio between the two models.
- The encoder reads the state *with the question visible*; the pure decoder must encode it
  question-blind, because that is the precondition for caching. A prefix-LM would have both, and
  nobody ships one — `extras/hybrid_encoding.py` shows why it is not free.
- Bidirectional attention should make an encoder a better classifier per parameter. Untested here;
  a fair test needs the same data, objective, parameter budget and readout on both.
- File 2 runs a **base** encoder and file 3 an **instruction-tuned** decoder, so any zero-shot
  quality gap between them is instruction tuning, not architecture. `ModernBERT-base` has never
  been trained to answer a question — asked through its own MLM head it answers `technical` at
  0.955 for a double-billing ticket. Laya starts from the same kind of backbone and gets its
  ability entirely from RLCD training; even then its shipped English checkpoint scores 0.362 on
  their own typed-decisions benchmark against 0.766 once fine-tuned on that domain, so domain fit
  matters as much as the pretraining underneath.
- Context ceilings differ: Laya caps at 8k, Qwen3 is native 32k.

## What Jev is, from TypeSafe

- Three question types: **Choice** (≤255 options), **Score** (2–10 ordered levels, answer is the
  probability-weighted mean of the level indices), **Noul** (one probability, no confidence)
- Questions run in parallel against one shared state; extra questions cost prefill, not latency
- Output tokens are free, because there is no decode loop
- **RLCD** = Reinforcement Learning for Calibrated Decisions: post-training with proper scoring
  rules so that 0.7 means 0.7

Not published: the architecture, the sampler and the loss. The confidence formula is undocumented
too, though an independent reproduction states it as `(n·p_max - 1)/(n - 1)` for Choice. Anything this
repo does in those four places is a labelled guess, and `extras/` measures the consequences.

One divergence is structural, not a guess: this repo scores each option independently, so the
log-odds between two options are exactly invariant to adding a third. Jev's options interact — a
measured reconstruction saw an irrelevant option move log-odds from +0.38 to +0.11.

## extras/

Depth, once the three files make sense. Each runs standalone.

| file | shows |
|---|---|
| `rlcd_training.py` | Laya's actual RLCD loop: proper-scoring-rule reward, GRPO advantage, temperature fit |
| `train_the_head.py` | the trained readout, on file 3's vectors |
| `score_dont_generate.py` | the frozen-model trick: score allowed answers, no training |
| `candidate_tokens.py` | schema → token sequences, no model |
| `first_token_collisions.py` | why one logit cannot separate `FRAUD` from `FRAUD_REVIEW` |
| `hybrid_encoding.py` | prefix-LM: bidirectional state, causal questions, cache still valid |
| `trie_ancestor_mask.py` | all fields and options in one pass via a DFS-interval mask |
| `choice_score_noul.py` | Jev's three primitives in its published answer shape |
| `score_depends_on_wording.py` | the same rubric scores 0.97, 1.46 or 1.98 depending on wording |
| `calibration_and_ece.py` | reliability bins, ECE, a fitted temperature |
| `rlcd_objective.py` | teacher forcing vs the contrastive loss, on a frozen-model scorer |
| `pointwise_vs_listwise.py` | our −0.0000 invariance against Jev's measured interaction |
| `vs_laya.py` | Laya on the same 32 messages, with every caveat attached |

## Credits

Method reverse-engineered from [`shreyansh26/Qwen-2.5-1B-RLCD`](https://huggingface.co/shreyansh26/Qwen-2.5-1B-RLCD)
(Apache-2.0), which serves stock Qwen weights and ships no checkpoint. Jev, System One and RLCD are
TypeSafe AI's; this is unaffiliated, and every claim about their system is sourced or marked as an
estimate.

## Sources

- [TypeSafe: Introducing System One Models & Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev)
- [TypeSafe API reference](https://docs.typesafe.ai/api)
- [Hume: Jev's Architecture Unmasked](https://archerhume.com/posts/jevs-architecture-unmasked)
- Open reproductions: [kev](https://github.com/jaredpalmer/kev), [NanoJev](https://github.com/TianyuCodings/NanoJev), [open-jev](https://huggingface.co/com-kotobalabs/open-jev-deberta-v3-large)
- Unrelated despite the name: [RLCD, Yang et al. 2023](https://arxiv.org/abs/2307.12950)
