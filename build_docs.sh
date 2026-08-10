#!/usr/bin/env bash
# Builds the course website with MkDocs.
#
# MkDocs 1.6+ refuses to let docs_dir be "." when mkdocs.yml lives at the
# repo root (docs_dir may not be an ancestor of the config file). Since the
# entire repo IS the course content, and moving ~300+ files into a docs/
# subfolder would break every relative link already verified throughout
# the course, this script instead makes an ephemeral, gitignored copy of
# the repo (minus tooling/build artifacts) into .docs_src/ and points
# MkDocs at that copy. .docs_src/ is disposable -- delete it any time.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

rm -rf .docs_src
mkdir -p .docs_src

tar \
  --exclude='./.git' \
  --exclude='./.github' \
  --exclude='./.venv-docs' \
  --exclude='./.venv' \
  --exclude='./.venv-*' \
  --exclude='**/node_modules' \
  --exclude='**/__pycache__' \
  --exclude='**/.pytest_cache' \
  --exclude='**/.ruff_cache' \
  --exclude='./site' \
  --exclude='./.docs_src' \
  --exclude='**/dist' \
  --exclude='**/build' \
  --exclude='**/.env' \
  --exclude='**/.env.*' \
  --exclude='./mkdocs.yml' \
  --exclude='./requirements-docs.txt' \
  --exclude='./build_docs.sh' \
  --exclude='./overrides' \
  -cf - . | tar -xf - -C .docs_src

mkdocs build --clean "$@"

echo ""
echo "Built into ./site -- open site/index.html or run:"
echo "  source .venv-docs/Scripts/activate && mkdocs serve"
