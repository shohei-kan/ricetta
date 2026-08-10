#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/srv/ricetta"
BACKUP_DIR="/srv/backups/ricetta/postgres"
S3_URI="s3://lintake-backups/ricetta/demo/postgres"
RETENTION_DAYS=7

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_FILE="${BACKUP_DIR}/ricetta_${TIMESTAMP}.sql"
COMPRESSED_FILE="${BACKUP_FILE}.gz"

COMPOSE="docker compose --env-file .env.prod -f docker-compose.prod.yml"

# Exit codes used by backup monitoring:
# 21: pg_dump failed
# 22: dump file is empty
# 23: compression failed or compressed file is empty
# 24: S3 upload failed
# 25: local retention cleanup failed
#
# Other unexpected failures use the default non-zero exit status.

echo "[ricetta-postgres-backup] starting at $(date -Is)"

cd "$APP_DIR"

mkdir -p "$BACKUP_DIR"

set -a
source .env.prod
set +a

echo "[ricetta-postgres-backup] creating dump: $BACKUP_FILE"

if ! $COMPOSE exec -T db \
  pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" \
  > "$BACKUP_FILE"; then

  echo "[ricetta-postgres-backup] pg_dump failed" >&2
  rm -f "$BACKUP_FILE"
  exit 21
fi

if [ ! -s "$BACKUP_FILE" ]; then
  echo "[ricetta-postgres-backup] backup file is empty: $BACKUP_FILE" >&2
  rm -f "$BACKUP_FILE"
  exit 22
fi

echo "[ricetta-postgres-backup] compressing dump"

if ! gzip "$BACKUP_FILE"; then
  echo "[ricetta-postgres-backup] gzip failed" >&2
  rm -f "$BACKUP_FILE" "$COMPRESSED_FILE"
  exit 23
fi

if [ ! -s "$COMPRESSED_FILE" ]; then
  echo "[ricetta-postgres-backup] compressed file is empty: $COMPRESSED_FILE" >&2
  rm -f "$COMPRESSED_FILE"
  exit 23
fi

echo "[ricetta-postgres-backup] uploading to S3: $S3_URI/"

if ! aws s3 cp \
  "$COMPRESSED_FILE" \
  "$S3_URI/" \
  --only-show-errors; then

  echo "[ricetta-postgres-backup] S3 upload failed" >&2
  exit 24
fi

echo "[ricetta-postgres-backup] S3 upload completed"

echo "[ricetta-postgres-backup] pruning local backups older than ${RETENTION_DAYS} days"

if ! find "$BACKUP_DIR" \
  -type f \
  -name "ricetta_*.sql.gz" \
  -mtime +"$RETENTION_DAYS" \
  -print \
  -delete; then

  echo "[ricetta-postgres-backup] local retention cleanup failed" >&2
  exit 25
fi

echo "[ricetta-postgres-backup] completed at $(date -Is)"
echo "[ricetta-postgres-backup] local file: $COMPRESSED_FILE"
