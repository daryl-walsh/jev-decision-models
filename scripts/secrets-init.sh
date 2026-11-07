#!/usr/bin/env bash
# Create a personal age identity (once per machine) and register its public
# key as a recipient in fnox.toml so you can encrypt/decrypt project secrets.
set -euo pipefail

key="${FNOX_AGE_KEY_FILE:-$HOME/.config/fnox/age.txt}"

if [[ ! -f "$key" ]]; then
  mkdir -p "$(dirname "$key")"
  age-keygen -o "$key"
  chmod 600 "$key"
  echo "Created age identity at $key (back it up, e.g. in 1Password)."
fi

pub="$(age-keygen -y "$key")"

if grep -q "$pub" fnox.toml 2>/dev/null; then
  echo "Your key is already a recipient in fnox.toml."
  exit 0
fi

if grep -q '^age = { type = "age", recipients = \[\]' fnox.toml; then
  # First recipient: fill in the empty list.
  sed -i.bak -E "s|^age = \{ type = \"age\", recipients = \[\] \}|age = { type = \"age\", recipients = [\"$pub\"] }|" fnox.toml
  rm -f fnox.toml.bak
  echo "Added $pub as the first recipient."
else
  echo "fnox.toml already has recipients. Add this public key to the list:"
  echo "  $pub"
  echo "then re-encrypt existing secrets with: fnox reencrypt -p age"
fi

echo
echo "Add a secret:   fnox set OPENAI_API_KEY --provider age"
echo "Use secrets:    mise run run -- python -m <package>"
