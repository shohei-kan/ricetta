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

echo "[ricetta-postgres-backup] starting at $(date -Is)"

cd "$APP_DIR"

mkdir -p "$BACKUP_DIR"

set -a
source .env.prod
set +a

echo "[ricetta-postgres-backup] creating dump: $BACKUP_FILE"

$COMPOSE exec -T db \
  pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" \
  > "$BACKUP_FILE"

if [ ! -s "$BACKUP_FILE" ]; then
  echo "[ricetta-postgres-backup] backup file is empty: $BACKUP_FILE" >&2
  exit 1
fi

echo "[ricetta-postgres-backup] compressing dump"

gzip "$BACKUP_FILE"

if [ ! -s "$COMPRESSED_FILE" ]; then
  echo "[ricetta-postgres-backup] compressed file is empty: $COMPRESSED_FILE" >&2
  exit 1
fi

echo "[ricetta-postgres-backup] uploading to S3: $S3_URI/"

aws s3 cp "$COMPRESSED_FILE" "$S3_URI/"

echo "[ricetta-postgres-backup] pruning local backups older than ${RETENTION_DAYS} days"

find "$BACKUP_DIR" -type f -name "ricetta_*.sql.gz" -mtime +"$RETENTION_DAYS" -print -delete

echo "[ricetta-postgres-backup] completed at $(date -Is)"
echo "[ricetta-postgres-backup] local file: $COMPRESSED_FILE"
