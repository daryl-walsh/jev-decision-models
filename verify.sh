#!/usr/bin/env bash
# Runs every lesson in order and reports pass/fail. MODEL_GGUF=path/to/model.gguf ./verify.sh to
# use a GGUF other than models/Qwen3-0.6B-Q8_0.gguf.
set -u
PY=${PY:-.venv/bin/python}
status=0
for f in 1_*.py 2_*.py 3_*.py extras/*.py; do
    if output=$("$PY" "$f" 2>&1); then
        printf 'PASS %s\n' "$f"
    else
        printf 'FAIL %s\n%s\n' "$f" "$output"
        status=1
    fi
done
exit "$status"
