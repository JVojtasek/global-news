#!/usr/bin/env bash
# Odešle nově napsané články zpět do repozitáře.
# Použití:  bash scripts/odesli.sh [pracovní-složka]
set -euo pipefail
DIR="${1:-/tmp/newsroom}"
cd "$DIR"

git config user.name  "claude-newsroom"
git config user.email "claude@users.noreply.github.com"
git add content/inbox
if git diff --staged --quiet; then
  echo "Nic nového k odeslání."
  exit 0
fi
N=$(git diff --staged --name-only | wc -l | tr -d ' ')
git commit -qm "[bot] redakce dodala $N článků $(date -u +%Y-%m-%d)"
git pull --rebase --autostash --quiet || true
git push --quiet
echo "Odesláno $N souborů. GitHub je teď zpracuje a vydá."
