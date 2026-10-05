"""What to do when two answers start with the same token.

3_pure_decoding.py reads one logit per option - the logit of the option's FIRST token. FRAUD and
FRAUD_REVIEW both begin with ' F', so that is the same number read twice and nothing can separate
them. pack() refuses such options rather than handing back a tie; this file is what the other
answer looks like.

The fix: score the whole answer, closing quote included, and add up the log-probabilities. It
always breaks the tie, for the price of one extra forward pass on that field. Whether the winner
also changes depends on the model and the options.

The machinery below is extras/score_dont_generate.py's - prompt, field suffix, candidate
continuations. Two other paths never meet this problem at all: extras/trie_ancestor_mask.py scores
every candidate in full by construction, and 2_pure_encoding.py plants its marker token in FRONT
of each option, so where it reads does not depend on how the option tokenises.
"""
import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import torch

from common import CONTEXT, SCHEMA, compile_field, load, parallel_prompt, repeat_cache

tok, model = load()
c = compile_field(tok, "decision", SCHEMA["decision"])
print("continuations:", c.conts)
print("token ids    :", c.cand_ids, " collision:", c.collision)

prompt_ids = tok(parallel_prompt(tok, CONTEXT, SCHEMA), add_special_tokens=False).input_ids
ids = prompt_ids + c.suffix_ids
out = model(torch.tensor([ids], device=model.device), use_cache=True)

first_logprobs = out.logits[0, -1].float().log_softmax(-1)
first_only = torch.stack([first_logprobs[s[0]] for s in c.cand_ids])
print("first-token scores :", [round(v, 3) for v in first_only.tolist()])

K = len(c.cand_ids)
W = max(len(s) for s in c.cand_ids) - 1
scores = first_only.clone()
if W:
    batch = torch.full((K, W), tok.pad_token_id, dtype=torch.long, device=model.device)
    mask = torch.zeros(K, W, dtype=torch.long, device=model.device)
    for r, s in enumerate(c.cand_ids):
        batch[r, :len(s) - 1] = torch.tensor(s[:-1], device=model.device)
        mask[r, :len(s) - 1] = 1
    attention = torch.cat([torch.ones(K, len(ids), dtype=torch.long, device=model.device), mask], 1)
    cont = model(input_ids=batch, attention_mask=attention,
                 past_key_values=repeat_cache(out.past_key_values, K), use_cache=True)
    logprobs = cont.logits.float().log_softmax(-1)
    for r, s in enumerate(c.cand_ids):
        if len(s) > 1:
            rows = torch.arange(len(s) - 1, device=model.device)
            scores[r] += logprobs[r, rows, torch.tensor(s[1:], device=model.device)].sum()

print("full-sequence      :", [round(v, 3) for v in scores.tolist()])
probs = torch.softmax(scores, -1)
print(dict(zip(c.choices, [round(p, 3) for p in probs.tolist()])))
print("first-token winner :", c.choices[int(first_only.argmax())])
print("full-score winner  :", c.choices[int(probs.argmax())])
