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

from common import CONTEXT, SCHEMA, compile_field, load, parallel_prompt

tok, model = load()
c = compile_field(tok, "decision", SCHEMA["decision"])
print("continuations:", c.conts)
print("token ids    :", c.cand_ids, " collision:", c.collision)

prompt_ids = tok.encode(parallel_prompt(tok, CONTEXT, SCHEMA), add_special_tokens=False)
ids = prompt_ids + c.suffix_ids
K = len(c.cand_ids)

# One sequence per candidate. Prompt and field suffix go into all K of them, once.
model.clear()
first_logprobs = model.forward(ids, range(len(ids)), [list(range(K))] * len(ids),
                               outputs=[len(ids) - 1])[0].log_softmax(-1)
first_only = torch.stack([first_logprobs[s[0]] for s in c.cand_ids])
print("first-token scores :", [round(v, 3) for v in first_only.tolist()])

# Each candidate's remaining tokens go into its own sequence - no padding, no copied cache.
scores = first_only.clone()
tokens, positions, seqs, reads = [], [], [], []
for r, s in enumerate(c.cand_ids):
    for j in range(len(s) - 1):
        tokens.append(s[j])
        positions.append(len(ids) + j)
        seqs.append([r])
        reads.append((r, s[j + 1]))
if tokens:
    logprobs = model.forward(tokens, positions, seqs, outputs=range(len(tokens))).log_softmax(-1)
    for row, (r, nxt) in enumerate(reads):
        scores[r] += logprobs[row, nxt]

print("full-sequence      :", [round(v, 3) for v in scores.tolist()])
probs = torch.softmax(scores, -1)
print(dict(zip(c.choices, [round(p, 3) for p in probs.tolist()])))
print("first-token winner :", c.choices[int(first_only.argmax())])
print("full-score winner  :", c.choices[int(probs.argmax())])
