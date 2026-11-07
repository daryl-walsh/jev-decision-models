"""Jev's three question types, all answered from one prefill.

Choice gives you the winner, the whole distribution, and a confidence.
Score gives you a number that can land between levels - the probability-weighted mean of the level
indices - plus a legend saying what each index meant.
Noul gives you a single probability and no confidence; that number is the uncertainty.

The rubric text sits in the prompt and the model only emits an index, so every option costs the
same tokens. extras/score_depends_on_wording.py shows what happens when they do not.

Last block: two very different distributions can share a score. That is why confidence ships too.
"""
import math
import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from common import decide, load

STATE = ("Ticket #8812: 'I was charged twice for the same order and nobody has replied in four days. "
         "Cancel it and give me my money back, or I am disputing with my bank.'")

QUESTIONS = {
    "team": {"kind": "choice", "type": "enum", "description": "Team that should own this ticket",
             "choices": ["BILLING", "TECHNICAL", "ACCOUNT"]},
    "frustration": {"kind": "score", "type": "enum",
                    "levels": ["the customer is calm and polite",
                               "the customer is clearly frustrated",
                               "the customer is very angry and is threatening to escalate"],
                    "description": "Customer frustration level, where 0 means the customer is calm "
                                   "and polite; 1 means the customer is clearly frustrated; 2 means "
                                   "the customer is very angry and is threatening to escalate",
                    "choices": ["0", "1", "2"]},
    "refund_requested": {"kind": "noul", "type": "boolean",
                         "description": "Whether the customer is asking for money back"},
}

for name, field in QUESTIONS.items():
    count = len(field.get("choices", ["true", "false"]))
    limit = (2, 10) if field["kind"] == "score" else (2, 255)
    if not limit[0] <= count <= limit[1]:
        raise ValueError(f"{name}: {field['kind']} takes {limit[0]}-{limit[1]} options, got {count}")


def confidence(probs):
    """Concentration of the distribution; 1.0 is all mass on one option. TypeSafe has not published theirs."""
    entropy = -sum(p * math.log(p) for p in probs if p > 0)
    return 1 - entropy / math.log(len(probs))


tok, model = load()
out = decide(tok, model, STATE, QUESTIONS)

for name, field in QUESTIONS.items():
    answer = out.answers[name]
    probs = answer.probs
    if field["kind"] == "score":
        score = sum(i * p for i, p in enumerate(probs))
        print(f"score  {name:<17} score={score:.2f}  legend={dict(enumerate(field['levels']))}")
        print(f"       {'':<17} probabilities={{{', '.join(f'{i}: {p:.3f}' for i, p in enumerate(probs))}}}"
              f"  confidence={confidence(probs):.3f}")
    elif field["kind"] == "noul":
        print(f"noul   {name:<17} noul={probs[0]:.3f}")
    else:
        top = max(range(len(probs)), key=probs.__getitem__)
        print(f"choice {name:<17} choice={answer.choices[top]}  "
              f"probabilities={{{', '.join(f'{c}: {p:.3f}' for c, p in zip(answer.choices, probs))}}}"
              f"  confidence={confidence(probs):.3f}")

print(f"\nprefill tokens={out.prefix_len}  trie nodes={out.nodes}  forward_passes=2  decode_steps=0")
one = decide(tok, model, STATE, {"team": QUESTIONS["team"]})
print(f"with 1 question: prefill={one.prefix_len} nodes={one.nodes}  "
      f"-> 3 questions cost +{out.prefix_len - one.prefix_len} prefill tokens, +{out.nodes - one.nodes} nodes")

for label, probs in (("certain middle", [0.0, 1.0, 0.0]), ("torn extremes", [0.5, 0.0, 0.5])):
    print(f"{label:<15} score={sum(i * p for i, p in enumerate(probs)):.2f}  confidence={confidence(probs):.3f}")
print("Same score, opposite meanings. Averaging indices of an independently judged categorical "
      "distribution cannot tell them apart - which is why a Score answer ships a confidence next to it.")
