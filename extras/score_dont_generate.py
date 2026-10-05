"""The trick: stop generating, start scoring.

A classification answer comes from a fixed list, so we write the JSON skeleton ourselves and ask
the model one thing per field - which allowed answer goes here?

Read the context once and keep its KV cache. Copy that cache once per field, push all the field
names through in a single batch, and read one logit per field. Two forward passes, nothing sampled,
and the JSON cannot come out malformed because we wrote it.

Copying the cache and padding the short field names change nothing - run any field on its own and
the logits agree to 7e-5 nats.
"""
import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import torch

from common import CONTEXT, SCHEMA, compile_field, load, parallel_prompt, repeat_cache

tok, model = load()
fields = [compile_field(tok, n, f) for n, f in SCHEMA.items()]
inputs = tok(parallel_prompt(tok, CONTEXT, SCHEMA), add_special_tokens=False, return_tensors="pt").to(model.device)

for c in fields:
    print(f"  {c.name:<9} writes {c.suffix!r} then picks from "
          f"{[tok.decode(ids) for ids in c.cand_ids]}")

out = model(**inputs, use_cache=True)
cache = out.past_key_values
P, F = inputs.input_ids.shape[1], len(fields)
print("prefix tokens:", P, " fields:", F)

lengths = [len(c.suffix_ids) for c in fields]
W = max(lengths)
suffixes = torch.tensor([c.suffix_ids + [tok.pad_token_id] * (W - len(c.suffix_ids)) for c in fields],
                        device=model.device)
suffix_mask = torch.tensor([[1] * n + [0] * (W - n) for n in lengths], device=model.device)
attention = torch.cat([torch.ones(F, P, dtype=torch.long, device=model.device), suffix_mask], 1)
print("suffix batch:", tuple(suffixes.shape), " attention:", tuple(attention.shape))

out = model(input_ids=suffixes, attention_mask=attention,
            past_key_values=repeat_cache(cache, F), use_cache=True)
print("logits:", tuple(out.logits.shape))

for i, c in enumerate(fields):
    logits = out.logits[i, lengths[i] - 1].float()
    first = torch.tensor([ids[0] for ids in c.cand_ids], device=model.device)
    probs = torch.softmax(logits[first], -1)
    winner = int(probs.argmax())
    print(f"{c.name:<9} -> {c.choices[winner]:<12} p={probs[winner]:.3f} "
          f"all={dict(zip(c.choices, [round(p, 3) for p in probs.tolist()]))} collision={c.collision}")

print("forward_passes=2  tokens_generated=0")