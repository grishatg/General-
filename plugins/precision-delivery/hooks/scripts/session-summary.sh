#!/usr/bin/env bash
# Logs a brief session summary when Claude stops.
# Reads from git to summarize changes made in this session.

set -euo pipefail

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
LOG_DIR="${CLAUDE_PLUGIN_DATA:-/tmp}/session-logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/session-$(date -u +%Y%m%d-%H%M%S).log"

{
  echo "Session ended: $TIMESTAMP"
  echo "Working directory: ${PWD}"
  echo ""

  if git rev-parse --git-dir > /dev/null 2>&1; then
    echo "=== Git Status ==="
    git status --short 2>/dev/null || echo "(git status unavailable)"
    echo ""
    echo "=== Recent Commits ==="
    git log --oneline -5 2>/dev/null || echo "(no commits)"
    echo ""
    echo "=== Unstaged Changes ==="
    git diff --stat 2>/dev/null || echo "(none)"
  else
    echo "(not a git repository)"
  fi
} > "$LOG_FILE" 2>&1

echo "{\"systemMessage\": \"[precision-delivery] Session summary saved to ${LOG_FILE}\"}"
exit 0
