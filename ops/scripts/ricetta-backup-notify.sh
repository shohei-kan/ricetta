#!/usr/bin/env bash
set -euo pipefail

MESSAGE="${1:-}"

if [ -z "$MESSAGE" ]; then
  echo "[ricetta-backup-notify] message is required" >&2
  exit 1
fi

if [ -z "${SLACK_WEBHOOK_URL:-}" ]; then
  echo "[ricetta-backup-notify] SLACK_WEBHOOK_URL is not set" >&2
  exit 1
fi

PAYLOAD="$(
  python3 -c '
import json
import sys

print(json.dumps({"text": sys.argv[1]}))
' "$MESSAGE"
)"

curl -fsS \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  "$SLACK_WEBHOOK_URL"

echo
echo "[ricetta-backup-notify] notification sent"
