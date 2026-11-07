"""The thin layer between these lessons and llama.cpp (through llama-cpp-python's C bindings).

The PyTorch version shaped attention by handing the model a 4-D mask, explicit position ids and
deep-copied KV caches. llama.cpp takes none of those. What it does take, per token, is a position
and a list of SEQUENCE IDS, and its attention rule is:

    a token attends to every cached cell that holds the token's first sequence id
    and sits at a position <= its own

One cell can belong to many sequences at once (that is what kv_unified=True allows), so sequence
ids are a mask language of their own:

    shared prefix   - put the prefix tokens in every sequence; each branch sees all of it
    isolation       - give each question its own sequence; they never see each other
    tree / trie     - give each leaf a sequence and every node the leaves below it; a node then
                      sees exactly its ancestors
    copying a cache - seq_cp() adds a sequence id to existing cells, nothing is recomputed
    bidirectional   - causal=False drops the position test for one batch

That covers every mask the PyTorch files built by hand. The one thing llama.cpp cannot do is
backpropagate, so extras/rlcd_objective.py stays on PyTorch (common_hf.py).
"""
import ctypes
import json
import os

import llama_cpp
import numpy as np
import torch
from jinja2.ext import loopcontrols
from jinja2.sandbox import ImmutableSandboxedEnvironment

_VERBOSE = bool(os.environ.get("LLAMA_VERBOSE"))


@llama_cpp.llama_log_callback
def _log(level, text, user_data):
    if _VERBOSE:
        print(text.decode("utf-8", errors="replace"), end="", flush=True)


llama_cpp.llama_log_set(_log, ctypes.c_void_p(0))
llama_cpp.llama_backend_init()


def open_gguf(path, vocab_only=False, n_gpu_layers=-1):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"no GGUF at {path!r}. Download one, e.g.\n"
            "  hf download Qwen/Qwen3-0.6B-GGUF Qwen3-0.6B-Q8_0.gguf --local-dir models\n"
            "or point MODEL_GGUF at your own file (see README.md).")
    params = llama_cpp.llama_model_default_params()
    params.vocab_only = vocab_only
    params.n_gpu_layers = n_gpu_layers
    model = llama_cpp.llama_model_load_from_file(path.encode("utf-8"), params)
    if not model:
        raise RuntimeError(f"llama.cpp could not load {path!r} (LLAMA_VERBOSE=1 shows why)")
    return model


class Tokenizer:
    """The slice of a HuggingFace tokenizer these files use, backed by the GGUF's own vocab."""

    def __init__(self, model):
        self.vocab = llama_cpp.llama_model_get_vocab(model)
        self.eos_token_id = llama_cpp.llama_vocab_eos(self.vocab)
        pad = llama_cpp.llama_vocab_pad(self.vocab)
        self.pad_token_id = pad if pad >= 0 else self.eos_token_id
        template = llama_cpp.llama_model_chat_template(model, None)
        self.chat_template = template.decode("utf-8") if template else None

    def encode(self, text, add_special_tokens=False):
        """parse_special=True, as in HF: '<|im_start|>' written in text becomes the special token."""
        data = text.encode("utf-8")
        size = len(data) + 8
        for _ in range(2):
            buf = (llama_cpp.llama_token * size)()
            n = llama_cpp.llama_tokenize(self.vocab, data, len(data), buf, size,
                                         add_special_tokens, True)
            if n >= 0:
                return list(buf[:n])
            size = -n
        raise RuntimeError("tokenize failed")

    def decode(self, ids):
        arr = (llama_cpp.llama_token * len(ids))(*ids)
        size = 16 * len(ids) + 16
        for _ in range(2):
            buf = ctypes.create_string_buffer(size)
            n = llama_cpp.llama_detokenize(self.vocab, arr, len(ids), buf, size, False, True)
            if n >= 0:
                return buf.raw[:n].decode("utf-8", errors="replace")
            size = -n
        raise RuntimeError("detokenize failed")

    def is_eog(self, token):
        """End of generation - <|im_end|>, <|endoftext|> and the rest the GGUF marks as stop."""
        return bool(llama_cpp.llama_vocab_is_eog(self.vocab, token))

    def token_text(self, token):
        return self.decode([token])

    def apply_chat_template(self, messages, add_generation_prompt=True, **kwargs):
        """Render the template stored in the GGUF, the way transformers renders it."""
        if self.chat_template is None:
            raise ValueError("this GGUF carries no chat template")
        env = ImmutableSandboxedEnvironment(trim_blocks=True, lstrip_blocks=True,
                                            extensions=[loopcontrols])

        def tojson(x, ensure_ascii=False, indent=None, separators=None, sort_keys=False):
            return json.dumps(x, ensure_ascii=ensure_ascii, indent=indent,
                              separators=separators, sort_keys=sort_keys)

        def raise_exception(message):
            raise ValueError(message)

        env.filters["tojson"] = tojson
        env.globals["raise_exception"] = raise_exception
        return env.from_string(self.chat_template).render(
            messages=messages, add_generation_prompt=add_generation_prompt,
            eos_token=self.token_text(self.eos_token_id), **kwargs)


class Model:
    """One llama.cpp context. forward() is the only way tokens go through it."""

    def __init__(self, model, n_ctx=4096, n_seq_max=64, n_ubatch=512, n_threads=None,
                 flash_attn=False):
        self.model = model
        self.n_vocab = llama_cpp.llama_vocab_n_tokens(llama_cpp.llama_model_get_vocab(model))
        self.hidden_size = llama_cpp.llama_model_n_embd(model)
        params = llama_cpp.llama_context_default_params()
        params.n_ctx = n_ctx
        params.n_batch = n_ctx
        params.n_ubatch = min(n_ubatch, n_ctx)
        params.n_seq_max = n_seq_max
        params.kv_unified = True              # one cell may belong to several sequences
        params.pooling_type = llama_cpp.LLAMA_POOLING_TYPE_NONE   # per-token hidden states
        params.type_k = params.type_v = llama_cpp.GGML_TYPE_F32   # the PyTorch files ran fp32
        # Flash attention computes in half precision inside: ~1e-2 nats of drift against fp32,
        # enough to move the third decimal these files print. FLASH_ATTN=1 for speed instead.
        params.flash_attn_type = (llama_cpp.LLAMA_FLASH_ATTN_TYPE_ENABLED if flash_attn
                                  else llama_cpp.LLAMA_FLASH_ATTN_TYPE_DISABLED)
        params.n_threads = params.n_threads_batch = n_threads or os.cpu_count() or 4
        self.ctx = llama_cpp.llama_init_from_model(model, params)
        if not self.ctx:
            raise RuntimeError("llama.cpp could not create a context (LLAMA_VERBOSE=1 shows why)")
        self.memory = llama_cpp.llama_get_memory(self.ctx)
        self.n_batch, self.n_ubatch, self.n_seq_max = params.n_batch, params.n_ubatch, n_seq_max

    # -- the KV cache, addressed by sequence --------------------------------------------------

    def clear(self):
        llama_cpp.llama_memory_clear(self.memory, True)

    def seq_cp(self, src, dst, p0=-1, p1=-1):
        """dst now sees src's cells too. No copy: the cells just gain a sequence id."""
        llama_cpp.llama_memory_seq_cp(self.memory, src, dst, p0, p1)

    def seq_rm(self, seq, p0=-1, p1=-1):
        llama_cpp.llama_memory_seq_rm(self.memory, seq, p0, p1)

    # -- the forward pass ---------------------------------------------------------------------

    def forward(self, tokens, positions, seqs, outputs=(), causal=True, hidden=False):
        """Append tokens to the cache and return one row per index in `outputs`.

        tokens[i] goes in at positions[i] as a member of every sequence in seqs[i]; seqs[i][0] is
        the one it reads through. Rows are vocabulary logits, or with hidden=True the final
        hidden state (after the last norm, i.e. HF's hidden_states[-1]).
        """
        n = len(tokens)
        if not n == len(positions) == len(seqs):
            raise ValueError("tokens, positions and seqs must be the same length")
        if n > self.n_batch:
            raise ValueError(f"{n} tokens in one pass, context allows {self.n_batch}; raise N_CTX")
        if not causal and n > self.n_ubatch:
            raise ValueError(f"bidirectional pass of {n} tokens needs one micro-batch "
                             f"(n_ubatch={self.n_ubatch})")
        top = max((s for row in seqs for s in row), default=0)
        if top >= self.n_seq_max:
            raise ValueError(f"needs {top + 1} sequences, context has {self.n_seq_max}; "
                             "raise N_SEQ_MAX")
        outputs = list(outputs)
        want = set(outputs)
        batch = llama_cpp.llama_batch_init(n, 0, self.n_seq_max)
        try:
            for i, (token, pos, row) in enumerate(zip(tokens, positions, seqs)):
                batch.token[i], batch.pos[i], batch.n_seq_id[i] = token, pos, len(row)
                for k, seq in enumerate(row):
                    batch.seq_id[i][k] = seq
                batch.logits[i] = i in want
            batch.n_tokens = n
            llama_cpp.llama_set_causal_attn(self.ctx, causal)
            llama_cpp.llama_set_embeddings(self.ctx, hidden)
            status = llama_cpp.llama_decode(self.ctx, batch)
            if status != 0:
                raise RuntimeError(f"llama_decode returned {status} (LLAMA_VERBOSE=1 shows why)")
            width = self.hidden_size if hidden else self.n_vocab
            read = llama_cpp.llama_get_embeddings_ith if hidden else llama_cpp.llama_get_logits_ith
            rows = np.empty((len(outputs), width), dtype=np.float32)
            for r, i in enumerate(outputs):
                rows[r] = np.ctypeslib.as_array(read(self.ctx, i), shape=(width,))
        finally:
            llama_cpp.llama_batch_free(batch)
            llama_cpp.llama_set_causal_attn(self.ctx, True)
            llama_cpp.llama_set_embeddings(self.ctx, False)
        return torch.from_numpy(rows)
