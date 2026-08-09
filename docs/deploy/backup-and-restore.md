# Backup and Restore

## Purpose

このドキュメントは、Ricetta公開デモ環境のバックアップ・復旧方針と運用手順を整理するためのものです。

目的は、EC2、Docker、PostgreSQL、設定ファイルなどに問題が起きた場合でも、GitHub、Bitwarden、S3、手順書をもとに復旧作業を進められる状態にすることです。

バックアップは「取ること」ではなく、「必要なときに戻せること」を目的とします。

## Scope

このドキュメントの対象は、RicettaのAWS公開デモ環境です。

対象:

- Ricetta AWS public demo
- AWS EC2
- Docker Compose
- PostgreSQL container
- Django REST Framework backend
- React / Vite frontend
- Caddy reverse proxy
- systemdによるデモデータリセット
- systemdによるPostgreSQL自動バックアップ
- AWS S3へのオフサイトバックアップ
- GitHub上のRicettaリポジトリ
- `.env.prod` などGit管理外の設定情報

この方針は、将来的にSplitMate、GreenLog、Wyse上で運用する個人利用アプリにも展開する予定です。

ただし、このドキュメントの直接対象はRicetta AWS公開デモ環境です。

## Current Environment

Ricetta公開デモの現在の構成は以下です。

- URL: `https://ricetta.lintake.net`
- Hosting: AWS EC2
- Region: `ap-northeast-1`
- App path: `/srv/ricetta`
- Runtime: Docker Compose
- Backend: Django REST Framework + Gunicorn
- Frontend: React / Vite + Caddy
- Database: PostgreSQL container
- Reverse proxy: Caddy
- AWS CLI: EC2へインストール済み
- S3 backup bucket: `lintake-backups`
- S3 backup prefix: `ricetta/demo/postgres/`
- EC2 local backup path: `/srv/backups/ricetta/postgres/`

### Demo reset

- Service: `ricetta-demo-reset.service`
- Timer: `ricetta-demo-reset.timer`
- Schedule: daily around 04:30 JST

### PostgreSQL backup

- Script: `/usr/local/bin/ricetta-postgres-backup.sh`
- Service: `ricetta-postgres-backup.service`
- Timer: `ricetta-postgres-backup.timer`
- Schedule: daily 04:10 JST
- Local retention: 7 days
- Remote backup: AWS S3

バックアップを04:10、demo resetを04:30に実行することで、reset前のDB状態をS3へ保存します。

## Recovery Policy

Ricetta公開デモでは、通常のデモ環境復旧は `seed_portfolio_data --reset` を優先します。

一方で、PostgreSQL dump / restore は、バックアップ運用の学習と将来の本番運用に備えて整備します。

seed resetとdatabase backupは目的が異なります。

- seed reset: 公開デモを決まった初期状態に戻すための仕組み
- database backup: ある時点のDB状態を保存し、必要に応じて復元するための仕組み

通常の公開デモ復旧では、まずseed resetを使います。

障害発生時の基本方針:

1. EC2 / Docker / Caddy / DB の状態を確認する
2. アプリが起動している場合は、まずdemo resetを試す
3. EC2自体に問題がある場合は、GitHubとBitwardenをもとに再構築する
4. DBの特定時点へ戻す必要がある場合のみ、S3 backupからのrestoreを検討する

## Backup Targets

| Target | Backup / Recovery Method | Priority | Notes |
| --- | --- | --- | --- |
| Source code | GitHub | High | アプリ再構築の正本 |
| `.env.prod` | Bitwarden | High | 実値はGit管理しない |
| PostgreSQL DB | `pg_dump` + gzip + S3 | High | 毎日04:10 JSTに自動取得 |
| Docker Compose config | GitHub | High | `docker-compose.prod.yml` |
| Caddy config | GitHub | High | root `Caddyfile` / frontend Caddyfile |
| systemd backup service/timer | docs | High | EC2再構築時に必要 |
| systemd reset service/timer | docs | Medium | EC2再構築時に必要 |
| Demo data | seed command | High | 通常の公開デモ復旧手段 |
| Uploaded files | Out of scope | Low | 現時点ではアップロード機能なし |

## Out of Scope

現時点では以下を対象外とします。

- PostgreSQL restoreの本番デモDBへの直接実行
- restoreの定期自動テスト
- Slack等へのバックアップ失敗通知
- バックアップ監視の自動通知
- S3 Lifecycleによる長期世代管理
- RDS移行
- マルチリージョンバックアップ
- EC2の完全自動再構築
- Terraformによる既存AWS環境全体のIaC化
- 本番顧客データを前提とした高可用性設計

これらは後続Issueや将来の運用改善で段階的に対応します。

## Secrets and Configuration

`.env.prod` はGit管理しません。

Gitで管理するのは `.env.prod.example` のみとし、必要な変数名と役割だけを記載します。

実際のsecret値はBitwardenで管理します。

Secret management policy:

- 秘密の中身はBitwarden
- 金庫の場所と使い方はGitHub docs
- 最後の復旧キーは紙

Bitwardenで管理する想定アイテム:

- `Ricetta AWS Demo .env.prod`
- `Ricetta AWS EC2 SSH`
- `Ricetta Backup S3 IAM`

以下にはsecretの実値を書きません。

- GitHub Issues
- Pull Requests
- README
- docs
- Notion
- チャットログ
- スクリーンショット

`.env.prod` をEC2上で変更した場合は、Bitwardenの `Ricetta AWS Demo .env.prod` も同時に更新します。

Bitwardenのマスターパスワードと2FAリカバリーコードは、紙などのオフライン手段でも保管します。

### Required environment variables

`.env.prod` には以下の変数が必要です。

値はこのドキュメントには記載しません。

```env
DJANGO_DEBUG=
DEMO_MODE=
DJANGO_SECRET_KEY=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
DJANGO_ALLOWED_HOSTS=
DJANGO_CSRF_TRUSTED_ORIGINS=
CADDY_SITE_ADDRESS=
VITE_DEMO_MODE=
```

## Demo Data Reset

Ricetta公開デモの通常復旧では、まずdemo resetを使います。

EC2上で以下を実行します。

```bash
cd /srv/ricetta
sudo systemctl start ricetta-demo-reset.service
journalctl -u ricetta-demo-reset.service -n 50 --no-pager
```

timerの状態確認:

```bash
systemctl status ricetta-demo-reset.timer
```

期待する状態:

- reset serviceが失敗していない
- timerが `active (waiting)` になっている
- owner / staff のデモログインができる
- 主要画面が表示できる

アプリ側の確認:

- `https://ricetta.lintake.net`
- `/api/v1/health/`
- owner account login
- staff account login
- Dashboard
- Prep Today
- Recipe Detail
- Cost Summary

## Manual PostgreSQL Backup Policy

Ricetta公開デモ環境では、EC2上で `pg_dump` を実行してPostgreSQLの手動バックアップを取得できます。

この手順は、自動バックアップに問題がある場合の確認や、任意のタイミングでDB dumpを取得したい場合にも利用できます。

### Manual backup command

EC2へSSH接続し、Ricettaのproduction directoryへ移動します。

```bash
ssh ricetta
cd /srv/ricetta
```

バックアップ保存先ディレクトリを作成します。

```bash
sudo mkdir -p /srv/backups/ricetta/postgres
sudo chown -R ubuntu:ubuntu /srv/backups/ricetta
```

`.env.prod` の値を読み込みます。

```bash
set -a
source .env.prod
set +a
```

バックアップファイル名を作成し、`pg_dump` を実行します。

```bash
BACKUP_FILE="/srv/backups/ricetta/postgres/ricetta_$(date +%Y%m%d_%H%M%S).sql"

docker compose --env-file .env.prod -f docker-compose.prod.yml exec -T db \
  pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" \
  > "$BACKUP_FILE"
```

作成されたdumpファイルを確認します。

```bash
echo "$BACKUP_FILE"
ls -lh "$BACKUP_FILE"
head -n 20 "$BACKUP_FILE"
tail -n 20 "$BACKUP_FILE"
```

### Verification points

以下を確認します。

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

### Notes

`.env.prod` の実値はGit管理しません。

必要なsecretはBitwardenで管理します。

通常運用では後述する自動バックアップを利用します。

## S3 Backup Policy

PostgreSQL backupファイルは、EC2外のオフサイト保存先としてAWS S3へ保存します。

### S3 bucket

```text
lintake-backups
```

### Prefix

```text
ricetta/demo/postgres/
```

保存先の例:

```text
s3://lintake-backups/ricetta/demo/postgres/ricetta_20260809_232524.sql.gz
```

### IAM policy

EC2からS3へアクセスするために、EC2へIAM Roleを付与します。

AWS access keyをEC2上の `.env.prod` や設定ファイルへ直接保存しません。

IAM権限は最小権限とし、対象bucket / prefixに限定します。

対象:

```text
s3://lintake-backups/ricetta/demo/postgres/
```

許可する操作:

- `s3:ListBucket`
- `s3:PutObject`
- `s3:GetObject`

### Manual S3 upload

EC2上で、作成済みのPostgreSQL dumpファイルをS3へ手動アップロードできます。

```bash
aws s3 cp \
  /srv/backups/ricetta/postgres/<backup-file> \
  s3://lintake-backups/ricetta/demo/postgres/
```

アップロード後、S3上のファイルを確認します。

```bash
aws s3 ls s3://lintake-backups/ricetta/demo/postgres/
```

### Verification result

手動アップロード時には、以下のようにS3上でバックアップファイルを確認しました。

```text
2026-08-04 23:21:53      66388 ricetta_20260804_222845.sql
```

確認項目:

- S3上にbackupファイルが存在する
- prefixが `ricetta/demo/postgres/` になっている
- ファイル名に日時が含まれている
- ファイルサイズが0 byteではない
- EC2に直接AWS access keyを保存していない
- IAM Role経由でS3へアクセスしている

## Automated PostgreSQL Backup

Ricetta公開デモ環境では、PostgreSQLバックアップをsystemd timerで毎日自動実行します。

バックアップ処理では、以下を順番に実行します。

1. `.env.prod` を読み込む
2. `pg_dump` でPostgreSQL dumpを取得する
3. dumpファイルが0 byteではないことを確認する
4. gzipで圧縮する
5. 圧縮済みファイルが0 byteではないことを確認する
6. AWS S3へアップロードする
7. EC2ローカルの古いバックアップを削除する
8. 実行結果をsystemd journalへ記録する

### Backup script

バックアップ処理本体:

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

スクリプトは以下のような処理を行います。

```text
pg_dump
↓
gzip
↓
S3 upload
↓
local retention cleanup
```

### Manual script execution

スクリプト単体で動作確認する場合:

```bash
/usr/local/bin/ricetta-postgres-backup.sh
```

成功時は以下のようなログを確認できます。

```text
[ricetta-postgres-backup] starting
[ricetta-postgres-backup] creating dump
[ricetta-postgres-backup] compressing dump
[ricetta-postgres-backup] uploading to S3
[ricetta-postgres-backup] pruning local backups older than 7 days
[ricetta-postgres-backup] completed
```

### Local backup verification

```bash
ls -lh /srv/backups/ricetta/postgres/
```

`.sql.gz` ファイルが作成されていることを確認します。

例:

```text
ricetta_20260809_232524.sql.gz
```

### S3 verification

```bash
aws s3 ls s3://lintake-backups/ricetta/demo/postgres/
```

検証時には以下のように圧縮済みbackupが保存されました。

```text
2026-08-09 23:22:12      11441 ricetta_20260809_232209.sql.gz
```

### Local retention

EC2ローカルでは、7日より古いRicetta PostgreSQL backupを削除します。

対象:

```text
/srv/backups/ricetta/postgres/ricetta_*.sql.gz
```

S3上のバックアップは、このローカル保持処理では削除しません。

S3側の保持期間やLifecycle設定は別途管理します。

### systemd service

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

正常終了時には、journalに以下が記録されます。

```text
Deactivated successfully.
Finished ricetta-postgres-backup.service
```

### systemd timer

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

次回実行時刻も `Trigger` で確認できます。

### Timer list

Ricetta関連timerをまとめて確認します。

```bash
systemctl list-timers --all | grep ricetta
```

期待する順序:

```text
04:10 ricetta-postgres-backup.timer
04:30 ricetta-demo-reset.timer
```

### Log check

バックアップserviceのログを確認します。

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

### Verification result

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

## Restore Policy

restoreは危険操作です。

検証時は、公開中のRicetta demo DBへ直接restoreしません。

まずは一時DBまたは検証用環境で復元可能性を確認します。

restore検証は、後続Issue `Test PostgreSQL restore procedure` で実施します。

基本方針:

- 公開中のDBへ直接restoreしない
- restore前に、可能であれば現在DBのdumpを取得する
- 一時DBまたは検証環境でrestoreを確認する
- restore後に主要テーブルとレコードを確認する
- 必要に応じてRicettaアプリから復元データを参照できるか確認する

通常の公開デモ復旧では、まずseed resetを優先します。

database backupからのrestoreは、特定時点のDB状態へ戻す必要がある場合に検討します。

## EC2 Rebuild Checklist

EC2を再構築する場合は、以下を確認します。

- [ ] AWS EC2 instance
- [ ] Elastic IP
- [ ] Security Group
- [ ] IAM Role for S3 backup
- [ ] SSH key / SSH config
- [ ] DNS A record for `ricetta.lintake.net`
- [ ] Docker / Docker Compose
- [ ] Git
- [ ] AWS CLI
- [ ] Clone repository to `/srv/ricetta`
- [ ] Restore `.env.prod` from Bitwarden
- [ ] Confirm `.env.prod` file permission
- [ ] `docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build`
- [ ] Run database migrations
- [ ] Run seed reset
- [ ] Confirm Caddy HTTPS
- [ ] Recreate `ricetta-demo-reset.service`
- [ ] Recreate `ricetta-demo-reset.timer`
- [ ] Recreate `/usr/local/bin/ricetta-postgres-backup.sh`
- [ ] Recreate `ricetta-postgres-backup.service`
- [ ] Recreate `ricetta-postgres-backup.timer`
- [ ] Enable PostgreSQL backup timer
- [ ] Confirm PostgreSQL backup timer is `active (waiting)`
- [ ] Confirm backup can upload to S3
- [ ] Confirm `/api/v1/health/`
- [ ] Confirm owner login
- [ ] Confirm staff login
- [ ] Confirm main demo pages

## Verification Checklist

このドキュメントを作成・更新したら、以下を確認します。

- [ ] secretの実値が含まれていない
- [ ] seed resetとdatabase backupの役割が分かれている
- [ ] Bitwardenのアイテム名が記載されている
- [ ] `.env.prod` をGit管理しない方針が明記されている
- [ ] `.env.prod.example` をGit管理する方針が明記されている
- [ ] PostgreSQL backupの保存先が明記されている
- [ ] S3 bucket / prefixが明記されている
- [ ] backup script / service / timerの役割が分かる
- [ ] backup timerとdemo reset timerの実行順が分かる
- [ ] 未検証のrestore手順を最終手順として書いていない
- [ ] EC2再構築時の確認項目がある
- [ ] `git diff --check` が通る

## Future Improvements

後続Issueで以下を進めます。

- Test PostgreSQL restore procedure
- Add backup monitoring
- S3 Lifecycleによるバックアップ保持ルールの整備
- 定期的なrestore drillの検討
- Slack等への失敗通知
- バックアップ異常検知
- EC2再構築手順の自動化

将来的には、この方針を以下にも展開します。

- SplitMate
- GreenLog
- Wyse上の個人運用アプリ
- S3 backup for home server operations
- Terraform / Ansibleによる再構築手順の整備