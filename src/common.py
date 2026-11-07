"""Shared setup: model loading, the demo preset, prompts, schema -> token compilation.

llama.cpp edition: the same Qwen3, run locally from a GGUF file. Every function keeps its name and
its numbers; only the plumbing changed. Where the PyTorch version (common_hf.py) built a 4-D
attention mask, this one assigns sequence ids - llamacpp.py explains the translation.
"""
import json
import os
import pathlib
from types import SimpleNamespace

import torch

from llamacpp import Model, Tokenizer, open_gguf

HERE = pathlib.Path(__file__).resolve().parent
MODEL_GGUF = os.environ.get("MODEL_GGUF", str(HERE / "models" / "Qwen3-0.6B-Q8_0.gguf"))

CONTEXT = (
    "Card ending 4412 made 9 purchases in 3 minutes across 4 countries. "
    "The cardholder called to say the card is still in their pocket."
)

SCHEMA = {
    "priority": {"type": "enum", "description": "Incident priority", "choices": ["HIGH", "LOW"]},
    "decision": {"type": "enum", "description": "Case decision",
                 "choices": ["FRAUD", "FRAUD_REVIEW", "CLEAR"]},
    "escalate": {"type": "boolean", "description": "Whether escalation is required"},
}


def load():
    """Tokenizer and model from one GGUF. N_GPU_LAYERS=-1 offloads everything (CUDA/Metal
    builds); N_CTX bounds one pass; N_SEQ_MAX bounds candidates scored at once by tree_scores;
    FLASH_ATTN=1 trades a little precision for speed."""
    torch.set_grad_enabled(False)
    gguf = open_gguf(MODEL_GGUF, n_gpu_layers=int(os.environ.get("N_GPU_LAYERS", -1)))
    model = Model(gguf, n_ctx=int(os.environ.get("N_CTX", 4096)),
                  n_seq_max=int(os.environ.get("N_SEQ_MAX", 64)),
                  flash_attn=os.environ.get("FLASH_ATTN", "") not in ("", "0"))
    return Tokenizer(gguf), model


def load_tokenizer():
    """Vocabulary only, no weights - for files that never run the model."""
    return Tokenizer(open_gguf(MODEL_GGUF, vocab_only=True))


def chat(tok, system, user, prefill):
    """Model-agnostic prompt: the model's own template, then prefill the assistant turn."""
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
    # enable_thinking=False closes the reasoning block; without it Qwen3 opens one and never emits JSON.
    return tok.apply_chat_template(messages, add_generation_prompt=True,
                                   enable_thinking=False) + prefill


def naive_prompt(tok, context, schema):
    lines = ["{"]
    for name, f in schema.items():
        rhs = "boolean" if f["type"] == "boolean" else " | ".join(f'"{c}"' for c in f["choices"])
        lines.append(f'  "{name}": {rhs}, // {f["description"]}')
    lines.append("}")
    system = ("You are a precise data extraction system. Output ONLY a valid JSON object matching "
              "the schema below.\n\nJSON Schema:\n" + "\n".join(lines))
    return chat(tok, system, context, "{\n  ")


def parallel_prompt(tok, context, schema):
    catalog = "\n".join(f'  "{n}": {f["description"]}' for n, f in schema.items())
    return chat(tok, "Classify JSON attributes:\n" + catalog, context, "{\n")


def compile_field(tok, name, field):
    if field["type"] == "boolean":
        choices = ["true", "false"]
        suffix = f"  {json.dumps(name)}: "
        conts = [c + "," for c in choices]
    else:
        choices = field["choices"]
        escaped = [json.dumps(c, ensure_ascii=False)[1:-1] for c in choices]
        shared = os.path.commonprefix(escaped)
        suffix = f'  {json.dumps(name)}: "{shared}'
        conts = [c[len(shared):] + '"' for c in escaped]
    cand_ids = [tok.encode(c, add_special_tokens=False) for c in conts]
    return SimpleNamespace(
        name=name, choices=choices, suffix=suffix, conts=conts, cand_ids=cand_ids,
        suffix_ids=tok.encode(suffix, add_special_tokens=False),
        collision=len({ids[0] for ids in cand_ids}) < len(cand_ids))


def choices_of(field):
    if field["type"] == "boolean":
        return ["true", "false"]
    choices = field["choices"]
    if not 2 <= len(choices) <= 255:
        raise ValueError(f"enum takes 2-255 choices, got {len(choices)}")
    if any(not isinstance(c, str) or not c for c in choices) or len(set(choices)) != len(choices):
        raise ValueError("choices must be unique nonempty strings")
    return choices


def build_trie(tok, schema):
    nodes, parents, depths, children = [], [], [], {}

    def add(parent, token):
        key = (parent, token)
        if key not in children:
            children[key] = len(nodes)
            nodes.append(token)
            parents.append(parent)
            depths.append(0 if parent == -1 else depths[parent] + 1)
        return children[key]

    score_nodes, score_tokens, score_cand = [], [], []
    counts, lengths, labels, paths = [], [], [], []
    cand = 0
    for name, field in schema.items():
        suffix = f"  {json.dumps(name)}: "
        choices = choices_of(field)
        if field["type"] == "boolean":
            conts = [c + "," for c in choices]
        else:
            suffix += '"'
            conts = [json.dumps(c, ensure_ascii=False)[1:] for c in choices]
        suffix_ids = tok.encode(suffix, add_special_tokens=False)
        node = -1
        for token in suffix_ids:
            node = add(node, token)
        counts.append(len(conts))
        for choice, cont in zip(choices, conts):
            seq = tok.encode(cont, add_special_tokens=False)
            labels.append((name, choice))
            lengths.append(len(seq))
            paths.append((suffix_ids, seq))
            cur = node
            for j, token in enumerate(seq):
                score_nodes.append(cur)
                score_tokens.append(token)
                score_cand.append(cand)
                if j < len(seq) - 1:
                    cur = add(cur, token)
            cand += 1

    kids = [[] for _ in nodes]
    roots = []
    for n, p in enumerate(parents):
        (roots if p == -1 else kids[p]).append(n)
    starts, ends, clock = [0] * len(nodes), [0] * len(nodes), 0
    stack = [(n, False) for n in reversed(roots)]
    while stack:
        n, seen = stack.pop()
        if seen:
            ends[n] = clock
        else:
            starts[n] = clock
            clock += 1
            stack.append((n, True))
            stack.extend((c, False) for c in reversed(kids[n]))

    return SimpleNamespace(nodes=nodes, depths=depths, starts=starts, ends=ends,
                           score_nodes=score_nodes, score_tokens=score_tokens,
                           score_cand=score_cand, counts=counts, lengths=lengths,
                           labels=labels, paths=paths)


def tree_scores(tok, model, context, schema, trie=None):
    """Mean token log-prob of every candidate of every field, in two forward passes.

    One sequence per candidate. The prompt belongs to all of them; a trie node belongs to every
    candidate whose answer runs through it. A node reads through the first of those, so it sees
    the prompt and its own ancestors and nothing else - the DFS-interval mask, as sequence ids.
    """
    trie = trie if trie is not None else build_trie(tok, schema)
    prompt = tok.encode(parallel_prompt(tok, context, schema), add_special_tokens=False)
    P, N, C = len(prompt), len(trie.nodes), len(trie.lengths)

    s, e = torch.tensor(trie.starts), torch.tensor(trie.ends)
    visible = (s.view(1, -1) <= s.view(-1, 1)) & (s.view(-1, 1) < e.view(1, -1))
    deepest = {}
    for node, cand in zip(trie.score_nodes, trie.score_cand):
        deepest[cand] = node
    seqs = [[c for c in range(C) if visible[deepest[c], k]] for k in range(N)]
    visible = torch.cat([torch.ones(N, P, dtype=torch.bool), visible], 1)

    model.clear()
    model.forward(prompt, range(P), [list(range(C))] * P)
    rows = sorted(set(trie.score_nodes))
    logprobs = model.forward(trie.nodes, [P + d for d in trie.depths], seqs,
                             outputs=rows).log_softmax(-1)
    row_of = {node: r for r, node in enumerate(rows)}
    edges = logprobs[torch.tensor([row_of[n] for n in trie.score_nodes]),
                     torch.tensor(trie.score_tokens)]
    scores = torch.zeros(C).scatter_add_(0, torch.tensor(trie.score_cand), edges)
    scores = scores / torch.tensor(trie.lengths, dtype=torch.float)
    return SimpleNamespace(scores=scores, trie=trie, prefix_len=P, visible=visible)


def decide(tok, model, context, schema, temperature=1.0, trie=None):
    """Jev's surface: every question answered from one prefill, as typed choices with probabilities."""
    result = tree_scores(tok, model, context, schema, trie)
    answers, offset = {}, 0
    for (name, field), count in zip(schema.items(), result.trie.counts):
        probs = torch.softmax(result.scores[offset:offset + count] / max(temperature, 1e-4), -1)
        answers[name] = SimpleNamespace(choices=choices_of(field), probs=probs.tolist(),
                                        scores=result.scores[offset:offset + count].tolist())
        offset += count
    return SimpleNamespace(answers=answers, prefix_len=result.prefix_len,
                           nodes=len(result.trie.nodes))


def pack(tok, state, questions):
    """One sequence: the state, then each question with its options. Returns ids, segment ids
    (0 = state, i+1 = question i), the decision position per question, the option positions, and the
    first token of each option - the one the model would write if it answered."""
    ids = tok.encode(state, add_special_tokens=False)
    segments = [0] * len(ids)
    decisions, options, candidates = [], [], []
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
        first = [tok.encode(f" {c}", add_special_tokens=False)[0] for c in choices]
        if len(set(first)) < len(first):
            clash = [c for c, t in zip(choices, first) if first.count(t) > 1]
            raise ValueError(
                f"{clash} share a first token, and this readout only looks at the first token - "
                "it would return an exact tie. Rename them, or score whole continuations the way "
                "extras/first_token_collisions.py does.")
        candidates.append(first)
    return ids, segments, decisions, options, candidates


def visibility(segments, bidirectional_state=False):
    """Questions see the state and themselves, never each other. With bidirectional_state the
    state block also attends forwards within itself - that is the only difference between the
    pure decoder and the hybrid. llama.cpp never receives this matrix; sequence_ids() produces
    it. It is here so you can look at it."""
    length = len(segments)
    seg = torch.tensor(segments)
    causal = torch.arange(length).view(-1, 1) >= torch.arange(length).view(1, -1)
    key_is_state = seg.view(1, -1) == 0
    same_question = (seg.view(1, -1) == seg.view(-1, 1)) & ~key_is_state
    if bidirectional_state:
        return key_is_state | (same_question & causal)
    return (key_is_state | same_question) & causal


def sequence_ids(segments):
    """The segment id IS the sequence id. Question i lives in sequence i; the state lives in
    sequence 0 and in every question's sequence, so each question reads it and nothing else."""
    questions = list(range(1, max(segments, default=0) + 1))
    return [[0] + questions if s == 0 else [s] for s in segments]


def run_packed(model, ids, segments, outputs, bidirectional_state=False, hidden=False):
    """Push a pack()ed sequence through from an empty cache and read the `outputs` rows."""
    state_length = segments.count(0)
    positions = [i if s == 0 else state_length + i - segments.index(s)
                 for i, s in enumerate(segments)]
    seqs = sequence_ids(segments)
    model.clear()
    if bidirectional_state:
        # The state reads itself both ways in a pass of its own; the questions then read its
        # cache causally. Same keys and values as one pass under the hybrid mask.
        model.forward(ids[:state_length], positions[:state_length], seqs[:state_length],
                      causal=False)
        ids, positions, seqs = ids[state_length:], positions[state_length:], seqs[state_length:]
        outputs = [o - state_length for o in outputs]
    return model.forward(ids, positions, seqs, outputs, hidden=hidden)


def encode(tok, model, state, questions, bidirectional_state=False):
    """Frozen backbone, one forward. Per question: the vocabulary logits at the decision position,
    and the option token ids to read off them."""
    ids, segments, decisions, options, candidates = pack(tok, state, questions)
    logits = run_packed(model, ids, segments, decisions, bidirectional_state)
    return [(logits[r], torch.tensor(c)) for r, c in enumerate(candidates)]


def prefill(tok, model, state):
    """Push the state through once and keep its KV cache - in sequence 0 of the context."""
    ids = tok.encode(state, add_special_tokens=False)
    model.clear()
    model.forward(ids, range(len(ids)), [[0]] * len(ids))
    return SimpleNamespace(seq=0, length=len(ids)), len(ids)


def question_mask(segments, state_length):
    """Questions see the whole cached state, themselves causally, and never each other. For
    looking at only: answer_from_cache() gets the same pattern from sequence ids."""
    width = len(segments)
    seg = torch.tensor(segments)
    causal = torch.arange(width).view(-1, 1) >= torch.arange(width).view(1, -1)
    same_question = seg.view(1, -1) == seg.view(-1, 1)
    return torch.cat([torch.ones(width, state_length, dtype=torch.bool), same_question & causal], 1)


def answer_from_cache(model, cache, ids, segments, positions, outputs):
    """Questions on top of a prefill()ed state. Each question borrows the state with seq_cp (the
    cells gain its sequence id, nothing is recomputed) and gives it back afterwards, so the cache
    holds the state alone again - what copy.deepcopy(cache) bought in the PyTorch version."""
    branches = sorted(set(segments))
    for q in branches:
        model.seq_cp(cache.seq, q)
    try:
        return model.forward(ids, positions, [[s] for s in segments], outputs)
    finally:
        for q in branches:
            model.seq_rm(q)
