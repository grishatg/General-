#!/usr/bin/env bash
# Warns before destructive shell commands that are hard to reverse.
# Reads tool_input from stdin (JSON from Claude Code hook system).

set -euo pipefail

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_input', {}).get('command', ''))" 2>/dev/null || echo "")

if [ -z "$COMMAND" ]; then
  exit 0
fi

# Patterns that are destructive or hard to reverse
DESTRUCTIVE_PATTERNS=(
  "rm -rf"
  "git push --force"
  "git push -f"
  "git reset --hard"
  "DROP TABLE"
  "DROP DATABASE"
  "DELETE FROM"
  "truncate"
  "git checkout -- ."
  "git restore ."
  "git clean -f"
)

for pattern in "${DESTRUCTIVE_PATTERNS[@]}"; do
  if echo "$COMMAND" | grep -qi "$pattern"; then
    echo "{\"systemMessage\": \"[precision-delivery] Destructive command detected: '${pattern}'. Confirm this is intentional before proceeding.\"}"
    exit 0
  fi
done

exit 0
