"""No model in this one - just the tokenizer.

Before you can score an answer you have to know which tokens spell it. This turns each field into
a fixed prefix the program writes itself, plus one token sequence per allowed answer.

Sometimes two answers start with the same token: FRAUD and FRAUD_REVIEW both begin with 'F'. That
is a collision, and it decides whether the cheap one-logit read in extras/score_dont_generate.py works
for that field. It is a fact about the tokenizer, not about the model or the meaning.
"""
import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from common import SCHEMA, compile_field, load_tokenizer

tok = load_tokenizer()

for name, field in SCHEMA.items():
    c = compile_field(tok, name, field)
    print(f"--- {name} ({field['type']}) ---")
    print("suffix      :", repr(c.suffix), "->", c.suffix_ids)
    for choice, cont, ids in zip(c.choices, c.conts, c.cand_ids):
        print(f"  {choice:<12} {repr(cont):<14} {ids}  decoded={[tok.decode([i]) for i in ids]}")
    print("first tokens:", [ids[0] for ids in c.cand_ids], "collision:", c.collision)
    print("             ", "two choices start with the same token, so one logit cannot tell them "
          "apart: extras/first_token_collisions.py must score whole continuations, +1 forward pass" if c.collision else
          "every choice starts with a different token, so one logit decides the field for free")
