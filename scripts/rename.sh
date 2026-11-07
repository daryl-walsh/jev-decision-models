#!/usr/bin/env bash
# Rename the template package "python_starter" to a new name (Linux x86_64).
# Usage: mise run init <package_name>   (or: bash scripts/rename.sh <package_name>)
set -Eeuo pipefail

if [[ "${1:-}" == "--help" ]]; then
  echo "usage: mise run init <package_name>"
  exit 0
fi

new="${1:-}"
if [[ $# -ne 1 || -z "$new" ]]; then
  echo "usage: mise run init <package_name>" >&2
  exit 1
fi
if [[ ! "$new" =~ ^[a-z][a-z0-9_]*$ ]]; then
  echo "package name must be snake_case (letters, digits, underscores)" >&2
  exit 1
fi
if [[ "$new" == "python_starter" || -e "src/$new" ]]; then
  echo "choose a new package name with no existing src directory" >&2
  exit 1
fi
if [[ ! -d src/python_starter ]]; then
  echo "src/python_starter not found; this project was already renamed" >&2
  exit 1
fi
uv run --no-sync python -c 'import keyword, sys; sys.exit(keyword.iskeyword(sys.argv[1]))' "$new" || {
  echo "package name must not be a Python keyword" >&2
  exit 1
}

dist="${new//_/-}"   # distribution name uses hyphens

git mv src/python_starter "src/$new" 2>/dev/null || mv src/python_starter "src/$new"

# Package imports and references
# The rename regression test models a pristine template; keep its fixture names.
# An include must come first so unmatched files (especially .pyc) stay excluded.
grep -rlZ --include='*.py' --include='*.md' --include='*.toml' --exclude='test_rename.py' 'python_starter' \
  src tests AGENTS.md mise.toml README.md docs/tooling-reconciliation.md \
  | xargs -0 -r sed -i "s/python_starter/$new/g"
grep -rlZ --include='*.py' --exclude='test_rename.py' 'python-starter' src tests \
  | xargs -0 -r sed -i "s/python-starter/$dist/g"
# Distribution labels, preserving paths such as 0001-python-starter-baseline.
sed -i -E "s@(^|[^[:alnum:]_/-])python-starter([^[:alnum:]_/-]|$)@\1$dist\2@g" README.md
# Distribution name in pyproject.toml
sed -i "s/^name = \"python-starter\"/name = \"$dist\"/" pyproject.toml

rm -f -- CHANGELOG.md
uv lock -q
echo "Renamed package to '$new' (distribution '$dist')."
