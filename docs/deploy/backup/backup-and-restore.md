# Backup and Restore

## Purpose

このドキュメントは、Ricetta公開デモ環境のバックアップ・復旧方針と運用全体を整理するためのものです。

目的は、EC2、Docker、PostgreSQL、設定ファイルなどに問題が起きた場合でも、GitHub、Bitwarden、S3、手順書をもとに復旧作業を進められる状態にすることです。

バックアップは「取ること」ではなく、「必要なときに戻せること」を目的とします。

詳細手順は責務ごとに分けています。

- [PostgreSQL Backup](./postgres-backup.md)
- [PostgreSQL Restore](./postgres-restore.md)

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

一方で、PostgreSQL backup / restore は、ある時点のDB状態へ戻す必要がある場合と、将来の実運用に備えた復旧手段として整備します。

seed resetとdatabase backupは目的が異なります。

- seed reset: 公開デモを決まった初期状態に戻すための仕組み
- database backup: ある時点のDB状態を保存し、必要に応じて復元するための仕組み

障害発生時の基本方針:

1. EC2 / Docker / Caddy / DB の状態を確認する
2. アプリが起動している場合は、まずdemo resetを試す
3. EC2自体に問題がある場合は、GitHubとBitwardenをもとに再構築する
4. DBの特定時点へ戻す必要がある場合のみ、S3 backupからのrestoreを検討する

PostgreSQL restoreの検証済み手順は [PostgreSQL Restore](./postgres-restore.md) を参照します。

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

バックアップの詳細は [PostgreSQL Backup](./postgres-backup.md)、復元確認は [PostgreSQL Restore](./postgres-restore.md) を参照します。

## Out of Scope

現時点では以下を対象外とします。

- 公開中の `ricetta` DBへの直接restore
- restoreの定期自動テスト
- Slack等へのバックアップ失敗通知
- バックアップ監視の自動通知
- S3 Lifecycleによる長期世代管理
- RDS移行
- マルチリージョンバックアップ
- EC2の完全自動再構築
- Terraformによる既存AWS環境全体のIaC化
- 本番顧客データを前提とした高可用性設計

## Verification Checklist

このドキュメントを作成・更新したら、以下を確認します。

- [ ] secretの実値が含まれていない
- [ ] seed resetとdatabase backupの役割が分かれている
- [ ] Bitwardenのアイテム名が記載されている
- [ ] `.env.prod` をGit管理しない方針が明記されている
- [ ] `.env.prod.example` をGit管理する方針が明記されている
- [ ] backup / restoreの詳細手順が責務別ファイルへ分離されている
- [ ] PostgreSQL backupの保存先が明記されている
- [ ] EC2再構築時の確認項目がある
- [ ] `git diff --check` が通る

## Future Improvements

後続Issueで以下を進めます。

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
