"""How Laya is actually trained: RLCD, ported from their fine-tuning notebook.

Their loop, in four moves:

  1. the model scores each option -> logits
  2. sample G noisy copies of those logits, z = logits + sigma * eps, softmax each into a
     distribution q  (the policy is a Gaussian over logits, not over answers)
  3. score every q with a strictly proper scoring rule against the TEACHER's distribution, take
     the group mean as the baseline, normalise -> advantage  (this is the GRPO part)
  4. loss = -(advantage * log p(z)) + cross entropy against the same teacher target

Then fit one temperature per question type on the finished logits.

The reward is log score + 0.75 * spherical score, minus ranked probability score for ordinal
`score` questions - RPS is what punishes probability mass sitting far from the true level, and it
is the only part of the reward that knows the levels are ordered.

Features here are synthetic so the loop runs in seconds. Swap in real marker embeddings and
nothing about the training changes.
"""
import os

import torch

GROUP_SIZE, SIGMA = 4, 0.5
W_RL = float(os.environ.get("W_RL", 1.0))
QTYPES = {"noul": 0, "choice": 1, "score": 2}
generator = torch.Generator().manual_seed(0)
DIM = 32


def make_items(n=240):
    """Each item: option features, a teacher distribution over options, and a question type."""
    direction = torch.randn(DIM, generator=generator)
    items = []
    for i in range(n):
        name = ["noul", "choice", "score"][i % 3]
        k = {"noul": 2, "choice": 4, "score": 5}[name]
        truth = torch.zeros(k)
        truth[torch.randint(k, (1,), generator=generator)] = 2.5
        if name == "score":
            truth = torch.stack([truth, truth.roll(1), truth.roll(-1)]).mean(0)
        target = torch.softmax(truth + 0.3 * torch.randn(k, generator=generator), -1)
        features = torch.randn(k, DIM, generator=generator) + target[:, None] * direction
        items.append((features, target, QTYPES[name]))
    return items


def batch(items):
    """Pad to the widest option set and carry a mask, the way marker_mask does."""
    width = max(f.shape[0] for f, _, _ in items)
    features = torch.zeros(len(items), width, DIM)
    target = torch.zeros(len(items), width)
    mask = torch.zeros(len(items), width, dtype=torch.bool)
    qtype = torch.tensor([q for _, _, q in items])
    for i, (f, t, _) in enumerate(items):
        features[i, :f.shape[0]], target[i, :len(t)], mask[i, :f.shape[0]] = f, t, True
    return features, target, mask, qtype


def proper_reward(q, target, qtype, mask, w_sph=0.75, w_rps=1.0):
    """Log score + spherical score, minus RPS on ordinal questions. Ported from laya.common."""
    q = q * mask
    logq = torch.log(q.clamp_min(1e-12)).clamp_min(-9.21)
    reward = (target * logq).sum(-1) + w_sph * (target * q).sum(-1) / q.norm(dim=-1).clamp_min(1e-9)
    is_score = (qtype == QTYPES["score"]).float()
    k = mask.sum(-1).clamp(min=2).float()
    rps = (((torch.cumsum(q, -1) - torch.cumsum(target, -1)) ** 2) * mask).sum(-1) / (k - 1)
    return reward - w_rps * rps * is_score


items = make_items()
features, target, mask, qtype = batch(items[:200])
held = batch(items[200:])
scorer = torch.nn.Linear(DIM, 1, bias=False)


@torch.no_grad()
def evaluate(pack, temperature=1.0):
    f, t, m, qt = pack
    logits = scorer(f).squeeze(-1).masked_fill(~m, -1e4) / temperature
    q = torch.softmax(logits, -1)
    return (float(((q.argmax(-1) == t.argmax(-1)).float()).mean()),
            float(proper_reward(q, t, qt, m).mean()),
            float((((q - t) ** 2) * m).sum(-1).mean()))


print("before: accuracy=%.3f reward=%+.3f brier=%.3f" % evaluate(held))

optimizer = torch.optim.AdamW(scorer.parameters(), lr=0.05)
for step in range(400):
    logits = scorer(features).squeeze(-1).masked_fill(~mask, -1e4)
    k = mask.sum(-1, keepdim=True).float()

    eps = torch.randn((GROUP_SIZE,) + logits.shape, generator=generator) * SIGMA * mask
    eps = (eps - eps.sum(-1, keepdim=True) / k) * mask
    z = logits.detach().unsqueeze(0) + eps
    q = torch.softmax(z.masked_fill(~mask, -1e4), -1)

    with torch.no_grad():
        reward = proper_reward(q, target.unsqueeze(0), qtype, mask)
        advantage = reward - reward.mean(0, keepdim=True)
        advantage = advantage / (advantage.std() + 1e-6)

    logp = -(((z - logits.unsqueeze(0)) ** 2) * mask).sum(-1) / (2 * SIGMA ** 2)
    loss_rl = -(advantage * logp).mean()
    loss_ce = -(target * torch.log_softmax(logits, -1)).sum(-1).mean()
    (W_RL * loss_rl + loss_ce).backward()
    torch.nn.utils.clip_grad_norm_(scorer.parameters(), 1.0)
    optimizer.step()
    optimizer.zero_grad(set_to_none=True)
    if step % 100 == 0:
        print(f"  step {step:>3}  rl={float(loss_rl):+.3f}  ce={float(loss_ce):.3f}")

print("after : accuracy=%.3f reward=%+.3f brier=%.3f" % evaluate(held))

log_t = torch.zeros(1, requires_grad=True)
fit = torch.optim.AdamW([log_t], lr=0.05)
with torch.no_grad():
    frozen = scorer(features).squeeze(-1).masked_fill(~mask, -1e4)
for _ in range(300):
    loss = -(target * torch.log_softmax(frozen / log_t.exp(), -1)).sum(-1).mean()
    loss.backward()
    fit.step()
    fit.zero_grad(set_to_none=True)
temperature = float(log_t.exp())
print("temperature fitted at %.3f -> accuracy=%.3f reward=%+.3f brier=%.3f"
      % ((temperature,) + evaluate(held, temperature)))
print("\nThe reward never touches an argmax - it scores the whole reported distribution, and a "
      "strictly proper rule is maximised only by reporting what you actually believe. That is the "
      "entire claim behind 'calibrated decisions'.")
print("Run again with W_RL=0 to drop the policy-gradient term. On this toy the cross entropy "
      "alone does as well or better, which is unsurprising: cross entropy against the teacher IS "
      "the log-score term, and the reward is differentiable, so the sampling only estimates a "
      "gradient you could have taken exactly. GLiNER2 trains comparable models with no RL at all.")
