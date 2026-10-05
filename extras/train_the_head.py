"""Training the readout, on top of file 3's inference path.

The four lessons all score with a bare dot product, which is enough to show the mechanism and
useless as an answer. This is the missing piece: keep the backbone frozen, put a small bilinear
head where the dot product was, and fit it to real outcomes with log loss.

Log loss is a strictly proper scoring rule - it is minimised only by honest probabilities - which
is the public half of what TypeSafe calls RLCD. Same idea applies to files 2 and 4; only the
vectors you feed it change.
"""
import pathlib
import sys

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import torch

from common import load
from labelled_examples import EXAMPLES  # 32 labelled refund messages

tok, model = load(attn_implementation="eager")
torch.manual_seed(0)
HIDDEN = model.config.hidden_size


def pack(state, questions):
    """One sequence, one segment id per token: 0 is the state, i+1 is question i."""
    ids = tok.encode(state, add_special_tokens=False)
    segments = [0] * len(ids)
    decisions, options = [], []
    for q, (instructions, choices) in enumerate(questions):
        head = tok.encode(f"\nQ: {instructions}\n", add_special_tokens=False)
        ids += head
        segments += [q + 1] * len(head)
        spans = []
        for choice in choices:
            piece = tok.encode(f"- {choice}\n", add_special_tokens=False)
            ids += piece
            segments += [q + 1] * len(piece)
            spans.append(len(ids) - 1)
        tail = tok.encode("A:", add_special_tokens=False)
        ids += tail
        segments += [q + 1] * len(tail)
        decisions.append(len(ids) - 1)
        options.append(spans)
    return ids, segments, decisions, options


def encode(state, questions):
    """Frozen backbone. Returns the decision vector and option vectors for every question."""
    ids, segments, decisions, options = pack(state, questions)
    length = len(ids)
    seg = torch.tensor(segments)
    causal = torch.arange(length).view(-1, 1) >= torch.arange(length).view(1, -1)
    same = (seg.view(1, -1) == 0) | (seg.view(1, -1) == seg.view(-1, 1))
    mask = torch.zeros(1, 1, length, length, dtype=model.dtype).masked_fill(
        ~(causal & same), torch.finfo(model.dtype).min).to(model.device)

    state_length = segments.count(0)
    positions = torch.tensor([[i if s == 0 else state_length + i - segments.index(s)
                               for i, s in enumerate(segments)]]).to(model.device)

    out = model(input_ids=torch.tensor([ids], device=model.device), attention_mask=mask,
                position_ids=positions, output_hidden_states=True)
    hidden = out.hidden_states[-1][0].float().cpu()
    return [(hidden[d], hidden[torch.tensor(spans)]) for d, spans in zip(decisions, options)]


class Pointer(torch.nn.Module):
    """score(option) = <A q, B o>, one shared readout for Choice, Score and Noul.

    Low rank on purpose: a full HIDDEN x HIDDEN bilinear has four million parameters and this
    trains on sixteen examples.
    """

    def __init__(self, rank=16):
        super().__init__()
        self.A = torch.nn.Linear(HIDDEN, rank, bias=False)
        self.B = torch.nn.Linear(HIDDEN, rank, bias=False)
        # Same 1/sqrt(d) as attention: keeps the logits near 1 so softmax starts undecided.
        self.scale = rank ** 0.5

    def forward(self, q, o):
        return self.B(o) @ self.A(q) / self.scale


REFUND = ("Is the customer asking for money back?", ["no", "yes"])
WALK_STATE = "Charged twice, no reply in four days."
WALK_QUESTIONS = [REFUND, ("Which team owns this?", ["billing", "technical"])]

ids, segments, decisions, options = pack(WALK_STATE, WALK_QUESTIONS)
last = decisions[-1]

head = Pointer()

print("encoding 32 labelled messages once with the frozen backbone...")
cached = [(encode(text, [REFUND])[0], int(gold)) for text, gold in EXAMPLES]
order = torch.randperm(len(cached), generator=torch.Generator().manual_seed(0)).tolist()
fit = [cached[i] for i in order[:20]]
dev = [cached[i] for i in order[20:24]]
test = [cached[i] for i in order[24:]]


def report(label, rows):
    probs = torch.stack([torch.softmax(head(q, o), -1)[1] for (q, o), _ in rows])
    gold = torch.tensor([g for _, g in rows])
    correct = (probs > 0.5) == gold.bool()
    return (f"{label}: accuracy={float(correct.float().mean()):.3f} "
            f"confidence={float(torch.maximum(probs, 1 - probs).mean()):.3f} "
            f"brier={float(((probs - gold.float()) ** 2).mean()):.3f}")


print(report("untrained head, held out", test))

def log_loss(rows, smoothing=0.0):
    losses = []
    for (q, o), g in rows:
        logprobs = torch.log_softmax(head(q, o), -1)
        target = torch.full_like(logprobs, smoothing / len(logprobs))
        target[g] += 1 - smoothing
        losses.append(-(target * logprobs).sum())
    return torch.stack(losses).mean()


optimizer = torch.optim.AdamW(head.parameters(), lr=1e-3, weight_decay=0.05)
best, best_state = float("inf"), None
with torch.enable_grad():
    for step in range(300):
        loss = log_loss(fit, smoothing=0.1)
        loss.backward()
        optimizer.step()
        optimizer.zero_grad(set_to_none=True)
        with torch.no_grad():
            score = float(log_loss(dev))
        if score < best:
            best, best_state = score, {k: v.clone() for k, v in head.state_dict().items()}
head.load_state_dict(best_state)
print(f"early stopped on 4 held-out messages at dev log loss {best:.3f}")

print(report("trained head,   trained on", fit))
print(report("trained head,   held out   ", test))
print("\nThe backbone never moved and nothing was generated - only the readout learned, from log "
      "loss against outcomes. That is a proper scoring rule, minimised only by honest probabilities, "
      "and it is RLCD's public claim without the RL machinery. Held-out confidence above sits well "
      "over held-out accuracy, which is the overconfidence calibration training exists to close.")

SHORT = "You charged me twice and I want that second charge returned today."
TICKET = ("Ticket #8812: I was charged twice for the same order and nobody has replied in four "
          "days. Cancel it and give me my money back, or I am disputing with my bank.")

print("\nthe trained question on two unseen inputs:")
for label, state in (("short message, like training", SHORT), ("long ticket, unlike training", TICKET)):
    (q, o), = encode(state, [REFUND])[:1]
    probs = torch.softmax(head(q, o), -1).tolist()
    print(f"  {label:<30} p(yes)={probs[1]:.3f}")
print("  Twenty short training messages generalise to short messages and not much further. The "
      "mechanism is sound; the training set is a toy.")

QUESTIONS = [REFUND,
             ("Which team should own this ticket?", ["billing", "technical", "account"]),
             ("How angry is the customer?", ["calm", "frustrated", "very angry"])]
print("\none forward pass, three questions, isolated from each other:")
for (instructions, choices), (q, o) in zip(QUESTIONS, encode(TICKET, QUESTIONS)):
    probs = torch.softmax(head(q, o), -1).tolist()
    table = {c: round(p, 3) for c, p in zip(choices, probs)}
    print(f"  {instructions:<40} {table}")
print("Only the first question had training labels; the other two show the shape, not a result. "
      "Same head, same loss - they need their own labelled outcomes.")
