#!/usr/bin/env bash
# Scan tracked/staged files for accidental secret leaks before pushing.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

FAIL=0

echo "Checking for committed .env files..."
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  if git ls-files --error-unmatch .env >/dev/null 2>&1; then
    echo "ERROR: .env is tracked by git. Run: git rm --cached .env"
    FAIL=1
  fi
  SCAN_FILES=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null || true)
  if [ -z "$SCAN_FILES" ]; then
    SCAN_FILES=$(git ls-files 2>/dev/null || true)
  fi
else
  echo "Not a git repo yet — scanning project files (excluding .venv, data, .env)."
  SCAN_FILES=$(find . -type f \
    ! -path './.venv/*' \
    ! -path './data/*' \
    ! -path './.git/*' \
    ! -name '.env' \
    \( -name '*.py' -o -name '*.js' -o -name '*.html' -o -name '*.md' -o -name '*.json' -o -name '*.toml' -o -name '*.yml' -o -name '*.yaml' \))
fi

echo "Scanning for API key patterns..."
PATTERNS=(
  'gsk_[A-Za-z0-9]{20,}'
  'sk-[A-Za-z0-9]{20,}'
)

for pattern in "${PATTERNS[@]}"; do
  while IFS= read -r file; do
    [ -z "$file" ] && continue
    [ ! -f "$file" ] && continue
    case "$file" in
      .env.example|scripts/check-secrets.sh|README.md|SECURITY.md) continue ;;
    esac
    if grep -qE "$pattern" "$file" 2>/dev/null; then
      echo "ERROR: Possible secret in $file (pattern: $pattern)"
      FAIL=1
    fi
  done <<< "$SCAN_FILES"
done

if [ "$FAIL" -eq 0 ]; then
  echo "No obvious secrets found."
else
  echo ""
  echo "Fix the issues above before pushing to GitHub."
  exit 1
fi
