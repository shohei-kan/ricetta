#!/usr/bin/env bash
set -euo pipefail

SOURCE="${1:-}"

if [ -z "$SOURCE" ]; then
  echo "[ricetta-backup-alert] source service is required" >&2
  exit 1
fi

SOURCE_UNIT="${SOURCE}.service"

STATUS="$(
  systemctl show "$SOURCE_UNIT" \
    --property=ExecMainStatus \
    --value 2>/dev/null || true
)"

RESULT="$(
  systemctl show "$SOURCE_UNIT" \
    --property=Result \
    --value 2>/dev/null || true
)"

STATUS="${STATUS:-unknown}"
RESULT="${RESULT:-unknown}"

TITLE="🚨 [Ricetta / Backup]"
DETAIL="バックアップ処理で予期しない異常が発生しました。"

case "$STATUS" in
  21)
    DETAIL="PostgreSQL dumpの作成に失敗しました。"
    ;;
  22)
    DETAIL="作成されたPostgreSQLバックアップファイルが空です。"
    ;;
  23)
    DETAIL="PostgreSQLバックアップのgzip圧縮に失敗したか、圧縮後のファイルが空です。"
    ;;
  24)
    DETAIL="PostgreSQLバックアップのS3アップロードに失敗しました。"
    ;;
  25)
    DETAIL="EC2ローカルの古いバックアップ削除に失敗しました。"
    ;;
  31)
    TITLE="🚨 [Ricetta / Monitor]"
    DETAIL="S3にPostgreSQLバックアップが見つかりません。"
    ;;
  32)
    TITLE="🚨 [Ricetta / Monitor]"
    DETAIL="S3上の最新PostgreSQLバックアップが0 byteです。"
    ;;
  33)
    TITLE="⚠️ [Ricetta / Monitor]"
    DETAIL="最新のPostgreSQLバックアップが設定された許容時間を超えて更新されていません。"
    ;;
  34)
    TITLE="🚨 [Ricetta / Monitor]"
    DETAIL="S3のバックアップ状態を確認できませんでした。AWSまたはIAM設定を確認してください。"
    ;;
esac

MESSAGE="${TITLE}
${DETAIL}

Service: ${SOURCE_UNIT}
Result: ${RESULT}
Exit status: ${STATUS}

確認:
journalctl -u ${SOURCE_UNIT} -n 80 --no-pager"

/usr/local/bin/ricetta-backup-notify.sh "$MESSAGE"

echo "[ricetta-backup-alert] alert sent for ${SOURCE_UNIT} status=${STATUS} result=${RESULT}"
