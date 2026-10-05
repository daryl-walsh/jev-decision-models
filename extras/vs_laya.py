"""Laya against ours, same 32 messages, same held-out split.

Laya is the open Jev: a ~400M bidirectional encoder, zero-shot, no training on this data.
Ours is a frozen Qwen3 decoder with a pointer head trained on 20 of these messages.
Not a fair fight in either direction, and not an architecture comparison: the accuracy gap measures
training investment and the latency gap measures implementation maturity. What it does show is two
working approaches and where each one spends its budget.
"""
import importlib.util
import pathlib
import sys
import time

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import torch

from labelled_examples import EXAMPLES

spec = importlib.util.spec_from_file_location("jev", pathlib.Path(__file__).resolve().parent / "train_the_head.py")
jev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(jev)

from laya import Router

QUESTION = {"refund": {"type": "noul", "instructions": "Is the customer asking for money back?"}}


def metrics(probs, golds):
    probs, golds = torch.tensor(probs), torch.tensor(golds)
    correct = (probs > 0.5) == golds.bool()
    return (f"accuracy={float(correct.float().mean()):.3f} "
            f"confidence={float(torch.maximum(probs, 1 - probs).mean()):.3f} "
            f"brier={float(((probs - golds.float()) ** 2).mean()):.3f}")


test_index = jev.order[24:]
test_texts = [EXAMPLES[i][0] for i in test_index]
test_golds = [int(EXAMPLES[i][1]) for i in test_index]

router = Router()
router.predict(test_texts[0], QUESTION)

laya_all = [router.predict(text, QUESTION)["answers"]["refund"]["noul"] for text, _ in EXAMPLES]
ours_test = [float(torch.softmax(jev.head(q, o), -1)[1]) for (q, o), _ in jev.test]


def per_question(fn):
    """Warm once, then time a second pass over the same eight messages."""
    for text in test_texts:
        fn(text)
    t0 = time.perf_counter()
    for text in test_texts:
        fn(text)
    return (time.perf_counter() - t0) * 1000 / len(test_texts)


laya_ms = per_question(lambda text: router.predict(text, QUESTION))
ours_ms = per_question(lambda text: jev.encode(text, [jev.REFUND]))

laya_test = [laya_all[i] for i in test_index]
print(f"\n{'':<34}{'8 held-out messages':<46}ms/question")
print(f"{'Laya, zero-shot':<34}{metrics(laya_test, test_golds):<46}{laya_ms:.0f}")
print(f"{'ours, head trained on 20':<34}{metrics(ours_test, [g for _, g in jev.test]):<46}{ours_ms:.0f}")
print(f"{'Laya, all 32 (never trained)':<34}{metrics(laya_all, [int(g) for _, g in EXAMPLES])}")
print("\nThese accuracies are not an architecture comparison: Laya is RLCD-trained on this class of "
      "task, our readout saw twenty examples. The latency is not one either - this side is naive "
      "eager PyTorch with a dense mask, theirs ships ONNX and TileLang. What is architectural is "
      "that the encoder re-reads the state for every question and we read it once, so the ranking "
      "flips with the number of questions per document. Pick by that, not by this table.")
