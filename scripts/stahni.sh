#!/usr/bin/env bash
# Stáhne repozitář do pracovní složky. Používá to naplánovaná Claude úloha.
# Použití:  bash scripts/stahni.sh <github-uzivatel>/<repozitar> <token>
set -euo pipefail
REPO="${1:?chybí jméno repozitáře}"
TOKEN="${2:?chybí token}"
DIR="${3:-/tmp/newsroom}"

if [ -d "$DIR/.git" ]; then
  git -C "$DIR" remote set-url origin "https://x-access-token:${TOKEN}@github.com/${REPO}.git"
  git -C "$DIR" fetch --quiet origin
  git -C "$DIR" reset --hard --quiet origin/main
else
  git clone --quiet --depth 20 "https://x-access-token:${TOKEN}@github.com/${REPO}.git" "$DIR"
fi
echo "Repozitář připraven v $DIR"
echo "--- zadání pro dnešek ---"
cat "$DIR/data/brief.md"
