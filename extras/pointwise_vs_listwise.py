"""The one place this repo and Jev genuinely disagree.

Everything here scores each option alone and then softmaxes. The model never even sees the option
list. So the log-odds between two options cannot move when you add a third - exactly, by
construction, not approximately.

Jev's options do see each other: someone measured an irrelevant extra option moving the log-odds
between two others from +0.38 to +0.11.

Below, our shift (zero), then the cheap fix of listing the options in the prompt. Watch the price.
"""
import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from common import decide, load

STATE = ("Ticket #8812: 'I was charged twice for the same order and nobody has replied in four days. "
         "Cancel it and give me my money back, or I am disputing with my bank.'")
OPTIONS = ["BILLING", "TECHNICAL", "ACCOUNT"]
DISTRACTOR = "WAREHOUSE_ROBOTICS"

tok, model = load(attn_implementation="eager")


def ask(options, listed):
    description = "Team that should own this ticket"
    if listed:
        description += ", one of: " + ", ".join(options)
    question = {"team": {"type": "enum", "description": description, "choices": options}}
    answer = decide(tok, model, STATE, question).answers["team"]
    scores = dict(zip(answer.choices, answer.scores))
    return scores["TECHNICAL"] - scores["BILLING"], dict(zip(answer.choices, answer.probs))


for listed in (False, True):
    before, probs_before = ask(OPTIONS, listed)
    after, probs_after = ask(OPTIONS + [DISTRACTOR], listed)
    print(f"--- options {'written into the prompt' if listed else 'never shown to the model'} ---")
    print(f"log-odds(TECHNICAL vs BILLING)  {before:+.4f} -> {after:+.4f}   shift {after - before:+.4f}")
    print(f"  before {{{', '.join(f'{k}: {v:.3f}' for k, v in probs_before.items())}}}")
    print(f"  after  {{{', '.join(f'{k}: {v:.3f}' for k, v in probs_after.items())}}}")

print("\nThe first shift is exactly zero: softmax renormalises, but a ratio exp(s_i - s_j) of two "
      "unchanged scores cannot move. Independence of irrelevant alternatives is a property of this "
      "design, not a result. The second shift is real interaction - and on a 1.7B model the "
      "distractor also runs away with the distribution, so listwise is not free either.")
