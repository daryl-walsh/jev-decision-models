#!/usr/bin/env bash
# Runs once when the dev container is created.
set -euo pipefail

# Docker creates named volumes owned by root.
sudo chown -R vscode:vscode \
  .venv ~/.local/share/mise ~/.cache/uv ~/.claude ~/.codex

# Agent CLIs are installed for this container only (they don't belong in the
# project's mise.toml, which every developer and CI run would install).
mise use -g node@lts npm:@anthropic-ai/claude-code npm:@openai/codex

# Project tools. The postinstall hook in mise.toml then runs `mise run setup`
# (uv sync + git hooks).
mise trust
mise install

# Claude Code's bubblewrap sandbox can't mount a fresh /proc in an
# unprivileged container. The container is the outer boundary, so let the
# inner sandbox reuse the container's /proc.
if [[ ! -f ~/.claude/settings.json ]]; then
  echo '{ "sandbox": { "enableWeakerNestedSandbox": true } }' > ~/.claude/settings.json
fi

echo
echo "Ready. Sign in once per container:  claude   then /login   |   codex login"
