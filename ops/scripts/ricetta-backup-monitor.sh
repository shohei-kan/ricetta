#!/usr/bin/env bash
set -euo pipefail

S3_BUCKET="lintake-backups"
S3_PREFIX="ricetta/demo/postgres/"
MAX_AGE_SECONDS="${MAX_AGE_SECONDS:-21600}"

# Prevent AWS CLI from opening a pager.
export AWS_PAGER=""

# Exit codes used by backup monitoring:
# 31: no backup found
# 32: latest backup is empty
# 33: latest backup is too old
# 34: failed to inspect S3
#
# Other unexpected failures use the default non-zero exit status.

echo "[ricetta-backup-monitor] starting at $(date -Is)"

if ! LATEST="$(
  aws s3api list-objects-v2 \
    --bucket "$S3_BUCKET" \
    --prefix "$S3_PREFIX" \
    --query 'sort_by(Contents,&LastModified)[-1].[Key,Size,LastModified]' \
    --output text
)"; then
  echo "[ricetta-backup-monitor] failed to inspect S3" >&2
  exit 34
fi

if [ -z "$LATEST" ] || [ "$LATEST" = "None" ]; then
  echo "[ricetta-backup-monitor] no backup found in S3" >&2
  exit 31
fi

read -r KEY SIZE LAST_MODIFIED <<< "$LATEST"

echo "[ricetta-backup-monitor] latest key: $KEY"
echo "[ricetta-backup-monitor] latest size: $SIZE"
echo "[ricetta-backup-monitor] last modified: $LAST_MODIFIED"

if [ "$SIZE" -le 0 ]; then
  echo "[ricetta-backup-monitor] latest backup is empty" >&2
  exit 32
fi

LAST_EPOCH="$(date -d "$LAST_MODIFIED" +%s)"
NOW_EPOCH="$(date +%s)"
AGE_SECONDS="$((NOW_EPOCH - LAST_EPOCH))"

echo "[ricetta-backup-monitor] age seconds: $AGE_SECONDS"

if [ "$AGE_SECONDS" -gt "$MAX_AGE_SECONDS" ]; then
  echo "[ricetta-backup-monitor] latest backup is too old" >&2
  exit 33
fi

echo "[ricetta-backup-monitor] backup is healthy"
echo "[ricetta-backup-monitor] completed at $(date -Is)"
