# Secret Management

## Purpose

このドキュメントは、Ricetta公開デモの運用secretをBitwardenを正本として管理し、EC2再構築時にGitHubとBitwardenから安全に復旧するための方針をまとめます。

ここにはsecretの名称、用途、保管先、配置先、更新・復旧方法だけを記載し、実値は記載しません。

## Source of Truth

- secret実値の正本はBitwardenとする
- GitHubにはexample値、変数名、運用手順だけを保存する
- `.env.prod` を変更したら、Bitwardenの `Ricetta Production Environment` も同時に更新する
- 新しいEC2はBitwardenからsecretを再構成し、旧EC2からsecretファイルをコピーしない
- AWS接続にはEC2 IAM Roleを使い、固定AWS access keyを発行・配置しない
- secretをIssue、Pull Request、README、docs、ログ、チャット、スクリーンショットに記載しない

## Secret Inventory

| Secret | Purpose | Bitwarden item | EC2 / local location | Used by | Permissions |
| --- | --- | --- | --- | --- | --- |
| Production environment | Django、PostgreSQL、Caddy、demo modeのproduction設定 | `Ricetta Production Environment` | `/srv/ricetta/.env.prod` | `docker-compose.prod.yml`、backup / demo reset scripts | `600 ubuntu:ubuntu` |
| Backup monitor Slack Webhook | backup / monitor異常時のSlack通知 | `Ricetta Backup Monitor Secrets` | `/etc/ricetta/backup-monitor.env` | `ricetta-backup-alert@.service` | `600 root:root` |
| EC2 SSH private key | Ricetta EC2へのSSH認証 | `Ricetta AWS EC2 SSH` | Bitwarden SSH Agent経由で使用 | local SSH client / `ssh ricetta` | Bitwarden内で管理 |
| AWS access | S3 backup / restoreなどのAWS API操作 | 固定secretなし | EC2 IAM Role `ricetta-demo-backup-role` | AWS CLI、backup / monitor scripts | IAM policyで最小権限 |

`/home/ubuntu/.aws` と `/root/.aws` に固定credentialsは配置しません。

## Production Environment Variables

`/srv/ricetta/.env.prod` は以下の10項目で構成します。値はBitwardenから取得し、この文書には記載しません。

```env
DJANGO_SECRET_KEY=
DJANGO_DEBUG=
DEMO_MODE=
DJANGO_ALLOWED_HOSTS=
DJANGO_CSRF_TRUSTED_ORIGINS=
CADDY_SITE_ADDRESS=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
VITE_DEMO_MODE=
```

`POSTGRES_HOST` と `POSTGRES_PORT` は `docker-compose.prod.yml` が `db` と `5432` を固定指定するため、`.env.prod` には含めません。Caddyは `CADDY_SITE_ADDRESS` だけを参照します。

## Update Procedure

### Production environment

1. Bitwardenの `Ricetta Production Environment` を更新する
2. EC2の `/srv/ricetta/.env.prod` を同じ内容に更新する
3. ownerとpermissionを `ubuntu:ubuntu` / `600` に保つ
4. secret値を表示しない方法でCompose configを検証する

```bash
cd /srv/ricetta
chmod 600 .env.prod
docker compose --env-file .env.prod -f docker-compose.prod.yml config --quiet
```

BitwardenとEC2のどちらかだけを更新してはいけません。

### Backup monitor Slack Webhook

1. Bitwardenの `Ricetta Backup Monitor Secrets` を更新する
2. root権限で `/etc/ricetta/backup-monitor.env` を再構成する
3. ownerとpermissionを `root:root` / `600` に設定する
4. alert serviceが同ファイルを参照していることを確認する

secretをshell historyやjournalへ出力しない手順で作業します。

### EC2 SSH key

Bitwardenの `Ricetta AWS EC2 SSH` を正本とし、fingerprintを確認してBitwarden SSH Agent経由で使用します。秘密鍵をrepositoryやEC2のapp directoryにコピーしません。

## EC2 Recovery Procedure

1. GitHubからrepositoryを `/srv/ricetta` へcloneする
2. Bitwardenの `Ricetta Production Environment` から `/srv/ricetta/.env.prod` を新規に再構成する
3. `.env.prod` のownerとpermissionを設定する

```bash
sudo chown ubuntu:ubuntu /srv/ricetta/.env.prod
chmod 600 /srv/ricetta/.env.prod
```

4. production Composeの設定を検証する

```bash
cd /srv/ricetta
docker compose --env-file .env.prod -f docker-compose.prod.yml config --quiet
```

5. Docker Composeを起動する
6. Django migrationを実行する
7. 通常の公開デモ復旧ではdemo seed/resetを実行する

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
docker compose --env-file .env.prod -f docker-compose.prod.yml exec backend python manage.py migrate
docker compose --env-file .env.prod -f docker-compose.prod.yml exec backend python manage.py seed_portfolio_data --reset
```

8. 特定時点のDBが必要な場合だけ、[PostgreSQL Restore](./backup/postgres-restore.md) に従いS3 backupのrestoreを検討する
9. Bitwardenの `Ricetta Backup Monitor Secrets` から `/etc/ricetta/backup-monitor.env` をroot権限で再構成する

```bash
sudo chown root:root /etc/ricetta/backup-monitor.env
sudo chmod 600 /etc/ricetta/backup-monitor.env
```

10. Git管理の`ops/systemd/`と`ops/scripts/`を正本としてsystemd設定と運用scriptを再配置する
11. backup / reset / monitor timer、backend health check、owner / staff loginを確認する

## Non-secret Accounts and CI Values

- `owner@example.com` と `staff@example.com` は公開デモ用アカウントであり、運用secretとして扱わない
- Django superuserは運用しない。現在のsuperuser数は0人
- GitHub Actionsは使い捨てのテスト用値だけを使い、production secretを参照しない

## Issue #25 Handoff

以下はIssue #59で変更せず、Issue #25「Production security hardening」で扱います。

- Django settingsの開発用fallback
- `docker-compose.prod.yml` の `replace-me` fallback
- `seed_portfolio_data` の公開デモ用既定パスワード

## Verification Checklist

- [ ] `.env.prod.example` とproduction Composeの外部参照変数が一致している
- [ ] `.env.prod` とbackup monitor envのBitwarden項目名が現在の運用と一致している
- [ ] secret実値がGit差分に含まれていない
- [ ] `.env.prod` がGit管理対象になっていない
- [ ] Markdownの相対リンクが解決できる
- [ ] `git diff --check` が通る
