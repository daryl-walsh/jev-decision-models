"""A Score is only as stable as the tokens you make the model emit.

Same ticket, same three levels, same formula. The only thing changing is how the levels are written.

If the level text is what the model has to emit, the score picks up how likely that sentence is as
English, and an 11-token rubric is not comparable to a 3-token label. Put the rubric in the prompt
and emit a bare index instead: every option costs the same, so what is left is the judgement.

Then we flip the level order. A judgement that ignored wording would mirror exactly. Watch it not.
"""
import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from common import build_trie, decide, load

STATE = ("Ticket #8812: 'I was charged twice for the same order and nobody has replied in four days. "
         "Cancel it and give me my money back, or I am disputing with my bank.'")

RUBRIC = ["the customer is calm and polite",
          "the customer is clearly frustrated",
          "the customer is very angry and is threatening to escalate"]

VARIANTS = {
    "short labels": {"type": "enum", "description": "Customer frustration level",
                     "choices": ["calm", "frustrated", "very angry"]},
    "rubric as label": {"type": "enum", "description": "Customer frustration level",
                        "choices": RUBRIC},
    "index + rubric in prompt": {"type": "enum",
                                 "description": "Customer frustration level, where " +
                                                "; ".join(f"{i} means {r}" for i, r in enumerate(RUBRIC)),
                                 "choices": ["0", "1", "2"]},
}

tok, model = load(attn_implementation="eager")
for label, field in VARIANTS.items():
    lengths = [len(seq) for _, seq in build_trie(tok, {"frustration": field}).paths]
    probs = decide(tok, model, STATE, {"frustration": field}).answers["frustration"].probs
    score = sum(i * p for i, p in enumerate(probs))
    print(f"{label:<26} score={score:.2f} / 2  probs={[round(p, 3) for p in probs]}  "
          f"candidate_tokens={lengths}")

top = len(RUBRIC) - 1
reversed_field = {"type": "enum",
                  "description": "Customer frustration level, where " +
                                 "; ".join(f"{i} means {r}" for i, r in enumerate(reversed(RUBRIC))),
                  "choices": ["0", "1", "2"]}
forward = VARIANTS["index + rubric in prompt"]
a = sum(i * p for i, p in enumerate(decide(tok, model, STATE, {"frustration": forward}).answers["frustration"].probs))
b = sum(i * p for i, p in enumerate(decide(tok, model, STATE, {"frustration": reversed_field}).answers["frustration"].probs))
print(f"\nlevels reversed: {a:.2f} -> expected {top - a:.2f}, got {b:.2f}, asymmetry {abs(top - a - b):.2f}")
print("A perfectly order-free judgement mirrors exactly. Whatever is left is the prompt wording "
      "still speaking - measure it before you trust a Score in production.")

print("\nOne ticket, one rubric, three answers. The first two let candidate length and sentence "
      "likelihood into the distribution; only the third asks the model to choose between equals. "
      "Check candidate_tokens whenever a Score looks wrong.")
