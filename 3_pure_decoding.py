"""Pure decoding: read the state once, then answer questions against it.

    [ the state ]  ->  cache          read once, never read again
    [ question 1 + its options ]      sees the cached state, and itself
    [ question 2 + its options ]      sees the cached state, and itself, never question 1

Each question ends at a decision position - the point where the model is about to write its
answer. Take the vocabulary logits there, keep only the rows for the options you allowed, and
softmax over those. The model's own output head does the scoring, so nothing is trained and
nothing can be generated outside the option set.

Every step is a line in this file. Run them one at a time and look at what each makes:
cache, ids, segments, visible, mask, positions, logits.

Only the option's FIRST token is read, so two options that start alike - FRAUD and FRAUD_REVIEW -
cannot be told apart. pack() refuses them rather than returning a tie.
"""
import copy
import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parent))
import torch

from common import load, pack, prefill, question_mask

STATE = ("Ticket #8812: charged twice for the same order, no reply in four days. "
         "Cancel it and give me my money back, or I am disputing with my bank.")
QUESTIONS = [("Is the customer asking for money back?", ["no", "yes"]),
             ("Which team owns this?", ["billing", "technical"])]

tok, model = load(attn_implementation="eager")

cache, state_length = prefill(tok, model, STATE)


def answer(questions):
    ids, segments, decisions, options, candidates = pack(tok, "", questions)

    mask, visible = question_mask(model, segments, state_length)

    positions = torch.tensor([[state_length + i - segments.index(seg)
                               for i, seg in enumerate(segments)]]).to(model.device)

    logits = model(input_ids=torch.tensor([ids], device=model.device), attention_mask=mask,
                   position_ids=positions,
                   past_key_values=copy.deepcopy(cache)).logits[0].float().cpu()

    for (instructions, choices), decision, option_ids in zip(questions, decisions, candidates):
        probs = torch.softmax(logits[decision][torch.tensor(option_ids)], -1)
        print(f"  {instructions:<40} {dict(zip(choices, [round(p, 3) for p in probs.tolist()]))}")
    print(f"    {len(ids)} question tokens through the model, {state_length} state tokens reused")


answer(QUESTIONS)
answer([("How angry is the customer?", ["calm", "furious"])])
