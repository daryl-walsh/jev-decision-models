"""Pure encoding - what Laya, the open Jev, does.

One sequence per question, the state at the end, a marker token planted in front of each option:

    [CLS] instructions [SEP] [MASK] opt0 [MASK] opt1 [SEP] state [SEP]
                             ^^^^^^        ^^^^^^
                             read these two positions, score them, softmax

Every token sees every other one, so the state is read with the question in view and the options
are compared against each other. No causal mask, no segment ids, no positions to fake - compare
the amount of plumbing here with file 3.

The cost is in the first line: one sequence PER QUESTION means the whole state goes through the
encoder again for every question you ask of it. Nothing can be cached, because changing the
question changes every state vector.

Note the two senses of "mask": [MASK] here is a placeholder TOKEN, borrowed from BERT pretraining
and used as a place to read from. It has nothing to do with the attention masks in files 3 and 4.

Options are scored against the pooled question rather than [CLS], which an MLM-only encoder never
learned to use as a summary.
"""
import os
import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parent))
import torch
from transformers import AutoModel, AutoTokenizer

ENCODER_ID = os.environ.get("ENCODER_ID", "answerdotai/ModernBERT-base")

STATE = ("Ticket #8812: charged twice for the same order, no reply in four days. "
         "Cancel it and give me my money back, or I am disputing with my bank.")
QUESTIONS = [("Is the customer asking for money back?", ["no", "yes"]),
             ("Which team owns this?", ["billing", "technical"])]

torch.set_grad_enabled(False)
tok = AutoTokenizer.from_pretrained(ENCODER_ID)
encoder = AutoModel.from_pretrained(ENCODER_ID).float().eval()


def build(state, instructions, options):
    """[CLS] instructions [SEP] [MASK] opt0 [MASK] opt1 ... [SEP] state [SEP]

    Also returns where the instructions sit, so they can be pooled into a query below.
    """
    question = tok.encode(instructions, add_special_tokens=False)
    ids = [tok.cls_token_id] + question + [tok.sep_token_id]
    span = (1, 1 + len(question))
    markers = []
    for option in options:
        markers.append(len(ids))
        ids += [tok.mask_token_id] + tok.encode(option, add_special_tokens=False)
    ids += [tok.sep_token_id] + tok.encode(state, add_special_tokens=False) + [tok.sep_token_id]
    return ids, markers, span


# Breakpoint here and step into build(). One question at a time, by construction.
for instructions, options in QUESTIONS:
    ids, markers, span = build(STATE, instructions, options)
    hidden = encoder(input_ids=torch.tensor([ids])).last_hidden_state[0].float()
    query = hidden[span[0]:span[1]].mean(0)
    option_vectors = hidden[torch.tensor(markers)]
    probs = torch.softmax(option_vectors @ query / query.shape[0] ** 0.5, -1)
    print(f"{len(ids)} tokens, markers at {markers}, {tok.decode(ids[:markers[-1] + 3])!r}")
    print(f"  {instructions:<40} {dict(zip(options, [round(p, 3) for p in probs.tolist()]))}")

print(f"\nTwo questions cost two passes over the same {len(tok.encode(STATE))}-token state. "
      "Untrained dot product against the pooled question, so read the mechanism, not the numbers. "
      "Laya scores each marker with a trained MLP and needs no query at all.")
