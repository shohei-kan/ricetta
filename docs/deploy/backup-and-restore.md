# Backup and Restore

## Purpose

このドキュメントは、Ricetta公開デモ環境のバックアップ・復旧方針を整理するためのものです。

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
- Demo reset: systemd service / timer
- Demo reset service: `ricetta-demo-reset.service`
- Demo reset timer: `ricetta-demo-reset.timer`
- Demo reset schedule: daily around 04:30 JST

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
4. DBの特定時点へ戻す必要がある場合のみ、backupからのrestoreを検討する

## Backup Targets

| Target | Backup / Recovery Method | Priority | Notes |
| --- | --- | --- | --- |
| Source code | GitHub | High | アプリ再構築の正本 |
| `.env.prod` | Bitwarden | High | 実値はGit管理しない |
| PostgreSQL DB | `pg_dump` / future S3 backup | Medium | デモDBだが運用学習用に保存する |
| Docker Compose config | GitHub | High | `docker-compose.prod.yml` |
| Caddy config | GitHub | High | root `Caddyfile` / frontend Caddyfile |
| systemd reset service/timer | docs | Medium | EC2再構築時に必要 |
| Demo data | seed command | High | 通常の公開デモ復旧手段 |
| Uploaded files | Out of scope | Low | 現時点ではアップロード機能なし |

## Out of Scope

このドキュメント作成Issueでは、以下は実装しません。

- PostgreSQL dumpの実行検証
- S3バケット作成
- S3アップロード
- backup script作成
- systemd timerによるDB backup自動化
- restore完全検証
- Slack通知
- 監視実装
- RDS移行
- Terraformによる既存環境の完全IaC化

これらは後続Issueで段階的に対応します。

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
````

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

* reset serviceが失敗していない
* timerがactiveになっている
* owner / staff のデモログインができる
* 主要画面が表示できる

アプリ側の確認:

* `https://ricetta.lintake.net`
* `/api/v1/health/`
* owner account login
* staff account login
* Dashboard
* Prep Today
* Recipe Detail
* Cost Summary

## Manual PostgreSQL Backup Policy

手動PostgreSQLバックアップは、後続Issue `Add manual PostgreSQL backup command` で検証します。

このドキュメント作成時点では、実行済みの最終手順としては扱いません。

基本方針:

* EC2上で `pg_dump` を使ってPostgreSQL dumpを取得する
* backup保存先は `/srv/backups/ricetta/postgres/` とする
* ファイル名に日時を含める
* dumpファイルが0 byteでないことを確認する
* 手順は検証後にこのドキュメントへ追記する

想定保存先:

```text
/srv/backups/ricetta/postgres/
```

後続Issueで確認すること:

* `pg_dump` の実行コマンド
* `.env.prod` の安全な読み込み方法
* dumpファイル名
* dumpファイルサイズ確認
* 失敗時の確認ポイント

## S3 Backup Policy

S3へのバックアップ保存は、後続Issue `Set up PostgreSQL backup to S3` で対応します。

基本方針:

* EC2とは別の保存先としてS3を使う
* まずは手動アップロードを確認する
* その後、自動化Issueでスクリプト化する
* IAM権限は最小権限にする
* 対象bucket / prefix以外へのアクセスを許可しない

予定prefix:

```text
ricetta/demo/postgres/
```

prefix設計の考え方:

```text
<app>/<environment>/<resource>/
```

例:

```text
ricetta/demo/postgres/
splitmate/home/postgres/
greenlog/demo/postgres/
```

## Restore Policy

restoreは危険操作です。

検証時は、公開中のRicetta demo DBへ直接restoreしません。

まずは一時DBまたは検証用環境で復元可能性を確認します。

restore検証は、後続Issue `Test PostgreSQL restore procedure` で実施します。

基本方針:

* 公開中のDBへ直接restoreしない
* restore前に、可能であれば現在DBのdumpを取得する
* 一時DBまたは検証環境でrestoreを確認する
* restore後に主要テーブルとレコードを確認する
* 必要に応じてRicettaアプリから復元データを参照できるか確認する

通常の公開デモ復旧では、まずseed resetを優先します。

database backupからのrestoreは、特定時点のDB状態へ戻す必要がある場合に検討します。

## EC2 Rebuild Checklist

EC2を再構築する場合は、以下を確認します。

* [ ] AWS EC2 instance
* [ ] Elastic IP
* [ ] Security Group
* [ ] SSH key / SSH config
* [ ] DNS A record for `ricetta.lintake.net`
* [ ] Docker / Docker Compose
* [ ] Git
* [ ] Clone repository to `/srv/ricetta`
* [ ] Restore `.env.prod` from Bitwarden
* [ ] Confirm `.env.prod` file permission
* [ ] `docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build`
* [ ] Run database migrations
* [ ] Run seed reset
* [ ] Confirm Caddy HTTPS
* [ ] Recreate systemd demo reset service
* [ ] Recreate systemd demo reset timer
* [ ] Confirm `/api/v1/health/`
* [ ] Confirm owner login
* [ ] Confirm staff login
* [ ] Confirm main demo pages

## Verification Checklist

このドキュメントを作成・更新したら、以下を確認します。

* [ ] secretの実値が含まれていない
* [ ] seed resetとdatabase backupの役割が分かれている
* [ ] Bitwardenのアイテム名が記載されている
* [ ] `.env.prod` をGit管理しない方針が明記されている
* [ ] `.env.prod.example` をGit管理する方針が明記されている
* [ ] 未検証のbackup / restoreコマンドを最終手順として書いていない
* [ ] 後続Issueとの役割分担が分かる
* [ ] EC2再構築時の確認項目がある
* [ ] `git diff --check` が通る

## Future Improvements

後続Issueで以下を進めます。

* Add manual PostgreSQL backup command
* Set up PostgreSQL backup to S3
* Automate PostgreSQL backup
* Test PostgreSQL restore procedure
* Add backup monitoring

将来的には、この方針を以下にも展開します。

* SplitMate
* GreenLog
* Wyse上の個人運用アプリ
* S3 backup for home server operations
* Terraform / Ansibleによる再構築手順の整備

