"""The trick: stop generating, start scoring.

A classification answer comes from a fixed list, so we write the JSON skeleton ourselves and ask
the model one thing per field - which allowed answer goes here?

Read the context once and keep its KV cache - in one sequence per field, which costs nothing
extra because a cached cell can belong to many sequences. Push all the field names through in a
single batch, each in its own sequence, and read one logit per field. Two forward passes, nothing
sampled, and the JSON cannot come out malformed because we wrote it.

Sharing the cache changes nothing - run any field on its own and the logits agree to float noise.
"""
import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import torch

from common import CONTEXT, SCHEMA, compile_field, load, parallel_prompt

tok, model = load()
fields = [compile_field(tok, n, f) for n, f in SCHEMA.items()]
prompt = tok.encode(parallel_prompt(tok, CONTEXT, SCHEMA), add_special_tokens=False)

for c in fields:
    print(f"  {c.name:<9} writes {c.suffix!r} then picks from "
          f"{[tok.decode(ids) for ids in c.cand_ids]}")

P, F = len(prompt), len(fields)
model.clear()
model.forward(prompt, range(P), [list(range(F))] * P)
print("prefix tokens:", P, " fields:", F)

tokens, positions, seqs, last = [], [], [], []
for i, c in enumerate(fields):
    tokens += c.suffix_ids
    positions += range(P, P + len(c.suffix_ids))
    seqs += [[i]] * len(c.suffix_ids)
    last.append(len(tokens) - 1)
print("suffix batch:", len(tokens), "tokens in", F, "sequences, no padding")

logits = model.forward(tokens, positions, seqs, outputs=last)
print("logits:", tuple(logits.shape))

for i, c in enumerate(fields):
    first = torch.tensor([ids[0] for ids in c.cand_ids])
    probs = torch.softmax(logits[i][first], -1)
    winner = int(probs.argmax())
    print(f"{c.name:<9} -> {c.choices[winner]:<12} p={probs[winner]:.3f} "
          f"all={dict(zip(c.choices, [round(p, 3) for p in probs.tolist()]))} collision={c.collision}")

print("forward_passes=2  tokens_generated=0")
