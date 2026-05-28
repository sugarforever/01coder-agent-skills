#!/usr/bin/env bash
# Rewrite plugins[0].skills in .claude-plugin/marketplace.json from the
# filesystem - scans skills/*/SKILL.md, respects .gitignore (so personal
# skills excluded via gitignore stay out), sorts alphabetically.
#
# Usage: ./scripts/sync-marketplace-skills.sh
#
# Run after adding or removing a skill, then commit. Version bumps stay
# manual - this script does not touch the version field.

set -euo pipefail

cd "$(dirname "$0")/.."

MARKETPLACE=".claude-plugin/marketplace.json"

if [[ ! -f "$MARKETPLACE" ]]; then
  echo "error: $MARKETPLACE not found" >&2
  exit 1
fi

# Collect tracked + untracked-but-not-gitignored SKILL.md, derive skill dirs,
# sort alphabetically, prefix with ./
skills_array=$(
  git ls-files --cached --others --exclude-standard 'skills/*/SKILL.md' \
    | xargs -n1 dirname \
    | sort -u \
    | sed 's|^|./|' \
    | jq -R . \
    | jq -s .
)

if [[ "$(echo "$skills_array" | jq 'length')" -eq 0 ]]; then
  echo "error: no SKILL.md files found under skills/" >&2
  exit 1
fi

tmp=$(mktemp)
jq --indent 4 --argjson skills "$skills_array" \
  '.plugins[0].skills = $skills' \
  "$MARKETPLACE" > "$tmp"
mv "$tmp" "$MARKETPLACE"

echo "Synced $(echo "$skills_array" | jq 'length') skills into $MARKETPLACE"
