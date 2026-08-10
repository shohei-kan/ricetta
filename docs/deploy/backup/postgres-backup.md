# PostgreSQL Backup

## Purpose

このドキュメントは、Ricetta公開デモ環境のPostgreSQLバックアップ取得・S3保存・自動実行の手順をまとめたものです。

バックアップ全体の方針やsecret管理、EC2再構築については [Backup and Restore](./backup-and-restore.md) を参照します。

このドキュメントはバックアップ取得と保存を扱います。失敗検知、S3上の最新backup確認、systemd `OnFailure`、Slack通知は [PostgreSQL Backup Monitoring](./postgres-monitoring.md) を参照します。

## Current Configuration

- App path: `/srv/ricetta`
- Local backup path: `/srv/backups/ricetta/postgres/`
- S3 bucket: `lintake-backups`
- S3 prefix: `ricetta/demo/postgres/`
- Backup script: `/usr/local/bin/ricetta-postgres-backup.sh`
- systemd service: `ricetta-postgres-backup.service`
- systemd timer: `ricetta-postgres-backup.timer`
- Schedule: daily 04:10 JST
- Local retention: 7 days
- Demo reset: daily around 04:30 JST

04:10にバックアップを取得し、04:30のdemo resetより前のDB状態を保存します。

## Manual PostgreSQL Backup

EC2上で `pg_dump` を実行して手動バックアップを取得できます。

### 1. Connect to EC2

```bash
ssh ricetta
cd /srv/ricetta
```

### 2. Prepare backup directory

```bash
sudo mkdir -p /srv/backups/ricetta/postgres
sudo chown -R ubuntu:ubuntu /srv/backups/ricetta
```

### 3. Load environment variables

```bash
set -a
source .env.prod
set +a
```

### 4. Create dump

```bash
BACKUP_FILE="/srv/backups/ricetta/postgres/ricetta_$(date +%Y%m%d_%H%M%S).sql"

docker compose --env-file .env.prod -f docker-compose.prod.yml exec -T db \
  pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" \
  > "$BACKUP_FILE"
```

### 5. Verify dump

```bash
echo "$BACKUP_FILE"
ls -lh "$BACKUP_FILE"
head -n 20 "$BACKUP_FILE"
tail -n 20 "$BACKUP_FILE"
```

確認項目:

- dumpファイルが `/srv/backups/ricetta/postgres/` に作成されている
- ファイル名に日時が含まれている
- ファイルサイズが0 byteではない
- `head` で `PostgreSQL database dump` が確認できる
- `tail` で `PostgreSQL database dump complete` が確認できる

検証時の例:

```text
/srv/backups/ricetta/postgres/ricetta_20260804_222845.sql
-rw-rw-r-- 1 ubuntu ubuntu 65K Aug  4 22:28 /srv/backups/ricetta/postgres/ricetta_20260804_222845.sql
-- PostgreSQL database dump
-- PostgreSQL database dump complete
```

## S3 Backup

PostgreSQL backupは、EC2外のオフサイト保存先としてAWS S3へ保存します。

### Bucket and prefix

```text
Bucket:
  lintake-backups

Prefix:
  ricetta/demo/postgres/
```

保存先の例:

```text
s3://lintake-backups/ricetta/demo/postgres/ricetta_20260809_232524.sql.gz
```

### IAM policy

EC2からS3へのアクセスにはIAM Roleを使用します。

AWS access keyをEC2上の `.env.prod` や設定ファイルへ直接保存しません。

IAM権限は最小権限とし、対象bucket / prefixに限定します。

許可する操作:

- `s3:ListBucket`
- `s3:PutObject`
- `s3:GetObject`

### Manual S3 upload

```bash
aws s3 cp \
  /srv/backups/ricetta/postgres/<backup-file> \
  s3://lintake-backups/ricetta/demo/postgres/
```

確認:

```bash
aws s3 ls s3://lintake-backups/ricetta/demo/postgres/
```

手動アップロード検証時の例:

```text
2026-08-04 23:21:53      66388 ricetta_20260804_222845.sql
```

## Automated PostgreSQL Backup

通常運用ではsystemd timerによってバックアップを毎日自動実行します。

バックアップ処理:

1. `.env.prod` を読み込む
2. `pg_dump` でPostgreSQL dumpを取得する
3. dumpファイルが0 byteではないことを確認する
4. gzipで圧縮する
5. 圧縮済みファイルが0 byteではないことを確認する
6. S3へアップロードする
7. EC2ローカルの古いバックアップを削除する
8. 実行結果をsystemd journalへ記録する

処理イメージ:

```text
pg_dump
↓
gzip
↓
S3 upload
↓
local retention cleanup
```

### Backup script

```text
/usr/local/bin/ricetta-postgres-backup.sh
```

主な設定:

```text
Application:
  /srv/ricetta

Local backup:
  /srv/backups/ricetta/postgres/

S3:
  s3://lintake-backups/ricetta/demo/postgres/

Local retention:
  7 days
```

### Manual script execution

```bash
/usr/local/bin/ricetta-postgres-backup.sh
```

成功時のログ例:

```text
[ricetta-postgres-backup] starting
[ricetta-postgres-backup] creating dump
[ricetta-postgres-backup] compressing dump
[ricetta-postgres-backup] uploading to S3
[ricetta-postgres-backup] pruning local backups older than 7 days
[ricetta-postgres-backup] completed
```

### Verify local backup

```bash
ls -lh /srv/backups/ricetta/postgres/
```

`.sql.gz` ファイルが作成されていることを確認します。

例:

```text
ricetta_20260809_232524.sql.gz
```

### Verify S3 backup

```bash
aws s3 ls s3://lintake-backups/ricetta/demo/postgres/
```

検証時の例:

```text
2026-08-09 23:22:12      11441 ricetta_20260809_232209.sql.gz
```

## Local Retention

EC2ローカルでは、7日より古いRicetta PostgreSQL backupを削除します。

対象:

```text
/srv/backups/ricetta/postgres/ricetta_*.sql.gz
```

S3上のbackupはこのローカル保持処理では削除しません。

S3側の保持期間やLifecycle設定は別途管理します。

## systemd Service

バックアップスクリプトをsystemd経由で1回実行するservice:

```text
/etc/systemd/system/ricetta-postgres-backup.service
```

service名:

```text
ricetta-postgres-backup.service
```

手動実行:

```bash
sudo systemctl start ricetta-postgres-backup.service
```

状態確認:

```bash
systemctl status ricetta-postgres-backup.service
```

このserviceは `Type=oneshot` のため、正常終了後に以下のような状態になることがあります。

```text
Active: inactive (dead)
```

これは常駐serviceではなく、一度実行して終了する設計のため正常です。

正常終了時にはjournalに以下が記録されます。

```text
Deactivated successfully.
Finished ricetta-postgres-backup.service
```

## systemd Timer

バックアップserviceを定期実行するtimer:

```text
/etc/systemd/system/ricetta-postgres-backup.timer
```

timer名:

```text
ricetta-postgres-backup.timer
```

実行スケジュール:

```text
Daily 04:10 JST
```

demo resetとの順序:

```text
04:10 PostgreSQL backup
04:30 Demo reset
```

timer確認:

```bash
systemctl status ricetta-postgres-backup.timer
```

期待する状態:

```text
Active: active (waiting)
```

Ricetta関連timerをまとめて確認:

```bash
systemctl list-timers --all | grep ricetta
```

期待する順序:

```text
04:10 ricetta-postgres-backup.timer
04:30 ricetta-demo-reset.timer
05:00 ricetta-backup-monitor.timer
```

## Log Check

```bash
journalctl -u ricetta-postgres-backup.service -n 80 --no-pager
```

確認するポイント:

- `starting`
- `creating dump`
- `compressing dump`
- `uploading to S3`
- `pruning local backups`
- `completed`
- `Finished ricetta-postgres-backup.service`

## Verification Result

以下を確認済みです。

- バックアップスクリプトをubuntuユーザーで手動実行できる
- PostgreSQL dumpを取得できる
- dumpをgzip圧縮できる
- ローカルに `.sql.gz` が保持される
- S3へ `.sql.gz` をアップロードできる
- EC2 IAM Role経由でS3へアクセスできる
- systemd service経由でバックアップを実行できる
- `journalctl` で実行ログを確認できる
- systemd timerが `active (waiting)` になっている
- 次回実行時刻が04:10 JSTになっている
- demo reset timerより先にbackup timerが実行される

失敗時の通知と、05:00 JSTに実行する独立monitorの検証結果は [PostgreSQL Backup Monitoring](./postgres-monitoring.md) に分離しています。

## Troubleshooting

### Backup file is empty

`pg_dump` の失敗やDB接続情報を確認します。

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

`.env.prod` の実値は表示・共有せず、Bitwardenの保存内容と整合しているか確認します。

### S3 upload fails

IAM Role、AWS CLI、対象prefixへの権限を確認します。

```bash
aws sts get-caller-identity
aws s3 ls s3://lintake-backups/ricetta/demo/postgres/
```

### Timer does not run

```bash
systemctl status ricetta-postgres-backup.timer
systemctl list-timers --all | grep ricetta
```

service側のログも確認します。

```bash
journalctl -u ricetta-postgres-backup.service -n 80 --no-pager
```
