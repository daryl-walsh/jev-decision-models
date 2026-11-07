"""What "calibrated" actually means, measured.

Calibrated means that when the model says 0.7 it is right about 70% of the time. Expected
Calibration Error is that gap, measured bucket by bucket.

32 labelled messages, including awkward ones - refund words with no request, requests that never
say refund. Half of them fit a single temperature scalar, the other half report before and after.

Read the direction, not the decimals. 16 examples is far too few, and that is part of the lesson.
"""
import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import torch

from common import build_trie, decide, load
from labelled_examples import EXAMPLES

QUESTION = {"refund_requested": {"type": "boolean",
                                 "description": "Whether the customer is asking for money back"}}


tok, model = load()
trie = build_trie(tok, QUESTION)
scores, golds = [], []
for text, gold in EXAMPLES:
    answer = decide(tok, model, text, QUESTION, trie=trie).answers["refund_requested"]
    scores.append(answer.scores)
    golds.append(gold)
scores, golds = torch.tensor(scores), torch.tensor(golds)


def p_true(temperature):
    return torch.softmax(scores / temperature, -1)[:, 0]


def report(probs, gold, bins=5):
    predicted = probs > 0.5
    confidence = torch.maximum(probs, 1 - probs)
    correct = predicted == gold
    ece, rows = 0.0, []
    for b in range(bins):
        low, high = 0.5 + 0.5 * b / bins, 0.5 + 0.5 * (b + 1) / bins
        pick = (confidence >= low if b == 0 else confidence > low) & (confidence <= high)
        if pick.any():
            avg, acc = float(confidence[pick].mean()), float(correct[pick].float().mean())
            ece += float(pick.float().mean()) * abs(avg - acc)
            rows.append(f"    ({low:.2f},{high:.2f}]  n={int(pick.sum()):<3} confidence={avg:.3f} accuracy={acc:.3f}")
    return float(correct.float().mean()), float(confidence.mean()), ece, rows


index = torch.randperm(len(EXAMPLES), generator=torch.Generator().manual_seed(0))
fit, test = index[:len(EXAMPLES) // 2], index[len(EXAMPLES) // 2:]
grid = torch.logspace(-1, 1.3, 60)
nll = [-torch.log(torch.where(golds[fit], p_true(t)[fit], 1 - p_true(t)[fit]).clamp_min(1e-9)).mean()
       for t in grid]
best = float(grid[int(torch.tensor(nll).argmin())])

fit_accuracy, _, _, _ = report(p_true(1.0)[fit], golds[fit])
print(f"fit half accuracy={fit_accuracy:.3f} -> {int((1 - fit_accuracy) * len(fit))} mistakes to calibrate against\n")

for label, temperature in (("before (T=1.0)", 1.0), (f"after  (T={best:.2f})", best)):
    accuracy, confidence, ece, rows = report(p_true(temperature)[test], golds[test])
    print(f"{label}: accuracy={accuracy:.3f} mean_confidence={confidence:.3f} ECE={ece:.3f}")
    print("\n".join(rows))

print("\nECE is what RLCD claims to train against; one temperature scalar is the cheap post-hoc "
      "version of it, fitted on held-out data and applied at serve time.")
print("Read the direction, not the decimal: 16 examples per half is far too few, ECE is noisy at "
      "this size, and a half with no mistakes has nothing to calibrate against - NLL is then "
      "minimised by sharpening. Calibration needs thousands of outcomes, which is the whole reason "
      "RLCD is a training programme and not a scalar you fit on a rainy afternoon.")
