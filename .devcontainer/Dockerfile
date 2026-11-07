# Optional dev container: runs the whole agent inside a container, so its
# file tools, MCP servers and hooks are isolated too, not just shell commands.
FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

# bubblewrap + socat: Claude Code's inner sandbox. ripgrep: agent search.
RUN apt-get update \
    && apt-get install -y --no-install-recommends bubblewrap socat ripgrep \
    && rm -rf /var/lib/apt/lists/*

USER vscode
RUN curl -fsSL https://mise.run | sh \
    && echo 'eval "$(~/.local/bin/mise activate bash)"' >> ~/.bashrc
ENV PATH="/home/vscode/.local/bin:/home/vscode/.local/share/mise/shims:${PATH}"
