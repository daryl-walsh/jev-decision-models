"""The shape of the objective RLCD names.

At inference you score K answers and softmax them, so train that same K-way distribution rather
than the usual next-token loss. Both numbers fall out of one forward pass:

    lm_loss   = -score[gold]                  teacher forcing; never looks at the wrong answers
    rlcd_loss = -log_softmax(scores)[gold]    subtracts the wrong answers out

Only the second can push a wrong answer down. Runs on TINY, so it trains in seconds.
TypeSafe has not published their loss - this is the family it belongs to, not the recipe.

The one file still on PyTorch (common_hf.py): training needs gradients, and llama.cpp has none.
"""
import os
import pathlib
import sys

os.environ.setdefault("TINY", "1")
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import torch

from common_hf import build_trie, load, tree_scores

QUESTION = {"refund_requested": {"type": "boolean",
                                 "description": "Whether the customer is asking for money back"}}

TRAIN = [
    ("I want my money back for order 1182.", 0),
    ("How do I change my delivery address?", 1),
    ("Please refund the duplicate charge.", 0),
    ("Do you ship to Ireland?", 1),
    ("You billed me twice, send the extra back.", 0),
    ("The app crashes when I open the settings tab.", 1),
    ("Return my payment, I never received the package.", 0),
    ("What is the warranty on this laptop?", 1),
]

tok, model = load(attn_implementation="eager")
torch.set_grad_enabled(True)
model.train()
trie = build_trie(tok, QUESTION)
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)


def epoch(update):
    lm, rlcd, p_gold = 0.0, 0.0, 0.0
    for text, gold in TRAIN:
        scores = tree_scores(tok, model, text, QUESTION, trie).scores
        logprobs = scores.log_softmax(-1)
        loss = -logprobs[gold]
        lm += float(-scores[gold].detach())
        rlcd += float(loss.detach())
        p_gold += float(logprobs[gold].detach().exp())
        if update:
            loss.backward()
            optimizer.step()
            optimizer.zero_grad(set_to_none=True)
    n = len(TRAIN)
    return lm / n, rlcd / n, p_gold / n


for step in range(13):
    lm, rlcd, p_gold = epoch(update=step > 0)
    if step % 3 == 0 or step == 12:
        print(f"epoch {step:>2}  lm_loss={lm:6.3f}  rlcd_loss={rlcd:.4f}  mean p(gold)={p_gold:.4f}")

print("\nlm_loss stays a language-modelling number; rlcd_loss is the one bounded by log(K) that "
      "actually ranks the candidates. Missing versus real RL: on-policy sampling, a reward signal "
      "over outcomes, and a held-out reliability check after every update.")
print("Note p(gold) near 1.0 on eight examples is memorisation, not calibration - exactly the "
      "overconfidence extras/calibration_and_ece.py measures. Fit the temperature after training, never before.")
