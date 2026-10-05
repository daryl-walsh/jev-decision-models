"""Scoring every answer of every field in one forward pass.

Lay all the answers out as a tree of tokens - shared tokens become one node - and let each node see
the context plus its own ancestors and nothing else. One pass then scores everything, and each
answer comes out exactly as if you had decoded it on its own.

The trick for "is this node my ancestor?" is a DFS numbering: k is an ancestor of q when
start[k] <= start[q] < end[k]. The machinery is build_trie and tree_scores in common.py.

The last lines are the proof - every answer re-scored alone, compared against the tree.
"""
import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import torch

from common import CONTEXT, SCHEMA, build_trie, load, parallel_prompt, tree_scores

tok, model = load(attn_implementation="eager")
trie = build_trie(tok, SCHEMA)
flat = sum(len(s) + len(q) for s, q in trie.paths)
print(f"trie nodes={len(trie.nodes)}  candidates={len(trie.lengths)}  same tokens laid out flat={flat}")

result = tree_scores(tok, model, CONTEXT, SCHEMA, trie)
print("prefix tokens:", result.prefix_len,
      " keys visible per node (min/max):", int(result.visible.sum(1).min()), int(result.visible.sum(1).max()))

offset = 0
for count in trie.counts:
    probs = torch.softmax(result.scores[offset:offset + count], -1)
    table = {trie.labels[offset + j][1]: round(p, 3) for j, p in enumerate(probs.tolist())}
    print(f"{trie.labels[offset][0]:<9} -> {trie.labels[offset + int(probs.argmax())][1]:<12} {table}")
    offset += count

prompt_ids = tok(parallel_prompt(tok, CONTEXT, SCHEMA), add_special_tokens=False).input_ids
worst = 0.0
for i, (suffix_ids, seq) in enumerate(trie.paths):
    ids = prompt_ids + suffix_ids + seq
    logprobs = model(torch.tensor([ids], device=model.device)).logits[0].float().log_softmax(-1)
    start = len(ids) - len(seq) - 1
    independent = float(sum(logprobs[start + j, t] for j, t in enumerate(seq)) / len(seq))
    delta = abs(float(result.scores[i]) - independent)
    worst = max(worst, delta)
    print(f"  {str(trie.labels[i]):<28} trie={float(result.scores[i]):8.4f} independent={independent:8.4f} d={delta:.5f}")
print(f"worst deviation over every candidate: {worst:.6f}")
