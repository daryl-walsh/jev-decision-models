"""The hybrid: bidirectional state, causal questions, cache still valid.

Nobody ships this. Every open decision model is fully causal or fully bidirectional; prefix-LM
exists in pretraining (UL2) and in converting decoders to embedders (LLM2Vec), but not here.

File 3 reads the state causally, so token 400 never sees token 900. File 2 reads everything both
ways but has to re-read the state for every question. A prefix-LM takes the middle:

    state          <-> state           both directions, like BERT
    question i      -> state           full view
    question i      -> question i      causal
    question i      -> question j      never

Nothing in the state depends on anything after it, so the KV cache still works - encoder-quality
state representations that stay reusable. One flag changes versus file 3.

Qwen3 was pretrained causally and has never seen its prefix attend forwards, so the numbers below
are not what this design is worth; they are what it costs before the backbone is adapted to it.
"""
import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import torch

from common import attention_mask, encode, load, pack

STATE = ("Ticket #8812: charged twice for the same order, no reply in four days. "
         "Cancel it and give me my money back, or I am disputing with my bank.")
QUESTIONS = [("Is the customer asking for money back?", ["no", "yes"]),
             ("Which team owns this?", ["billing", "technical"])]

tok, model = load(attn_implementation="eager")
ids, segments, decisions, options, candidates = pack(tok, STATE, QUESTIONS)
state_length = segments.count(0)

_, causal_view = attention_mask(model, segments, bidirectional_state=False)
_, hybrid_view = attention_mask(model, segments, bidirectional_state=True)
print(f"state is {state_length} tokens")
print(f"  first state token sees {int(causal_view[0].sum())} tokens causally, "
      f"{int(hybrid_view[0].sum())} in the hybrid - the whole state instead of just itself")
print(f"  questions are unchanged: {int(causal_view[-1].sum())} vs {int(hybrid_view[-1].sum())} "
      f"for the last decision token")

for flag, label in ((False, "causal state "), (True, "bidirectional")):
    readouts = encode(tok, model, STATE, QUESTIONS, bidirectional_state=flag)
    for (instructions, choices), (logits, option_ids) in zip(QUESTIONS, readouts):
        probs = torch.softmax(logits[option_ids], -1)
        print(f"  {label}  {instructions:<40} "
              f"{dict(zip(choices, [round(p, 3) for p in probs.tolist()]))}")
