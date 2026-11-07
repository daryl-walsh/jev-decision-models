"""Asking a model for JSON the ordinary way.

You prompt it and it writes `{`, then `"`, then `priority`, one token at a time, and you hope the
whole thing parses. That is one forward pass per token - watch `passes` climb.

We also score it: keep each token's probability as it comes out, then multiply the ones that wrote
a value. It looks like a confidence. It isn't, and the last block says why.
"""
import json
import re
import pathlib
import sys
import time

sys.path.append(str(pathlib.Path(__file__).resolve().parent))
from common import CONTEXT, SCHEMA, load, naive_prompt

tok, model = load()
prompt = naive_prompt(tok, CONTEXT, SCHEMA)
ids = tok.encode(prompt, add_special_tokens=False)
print("prompt tokens:", len(ids))

model.clear()
step, position, generated, passes = ids, 0, [], 0
text = "{\n  "
spans = []
t0 = time.perf_counter()

for _ in range(200):
    # Append this step's tokens to the cache (sequence 0) and read the last row's logits.
    logits = model.forward(step, range(position, position + len(step)), [[0]] * len(step),
                           outputs=[len(step) - 1])[0]
    position, passes = position + len(step), passes + 1
    probs = logits.softmax(-1)
    token = int(probs.argmax())
    if tok.is_eog(token):
        break
    generated.append(token)
    grown = "{\n  " + tok.decode(generated)
    spans.append((len(text), len(grown), float(probs[token])))
    text = grown
    try:
        if isinstance(json.loads(text), dict):
            break
    except ValueError:
        pass
    step = [token]

print(text)
print(f"tokens={len(generated)}  forward_passes={passes}  ms={(time.perf_counter() - t0) * 1000:.0f}")
print("valid json:", isinstance(json.loads(text), dict) if text.strip().endswith("}") else False)

for name in SCHEMA:
    match = re.search(rf'"{re.escape(name)}"\s*:\s*', text)
    if not match:
        continue
    start = match.end()
    end, quoted = start, False
    while end < len(text) and (quoted or text[end] not in ',\n}'):
        quoted = not quoted if text[end] == '"' and text[end - 1] != "\\" else quoted
        end += 1
    inside = [p for a, b, p in spans if a < end and b > start]
    product = 1.0
    for p in inside:
        product *= p
    print(f"{name:<9} = {text[start:end].strip():<14} p(path)={product:.3f} over {len(inside)} token(s)"
          f"  weakest={min(inside, default=1.0):.3f}")

print("\nThat p(path) is not a decision probability. It normalises over the whole vocabulary, not "
      "over the allowed values; it multiplies without length normalisation, so long values look "
      "unlikely; it is conditioned on the fields already written, so field order changes it; and "
      "the alternatives were never scored at all. Part 2 fixes every one of those.")
