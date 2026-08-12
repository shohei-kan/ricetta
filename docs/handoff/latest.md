# Ricetta Handoff Latest

## Date

2026-08-12

## Project

Ricetta

## Status

GitHub Issue #59「Establish Bitwarden-based secret management」のドキュメント整備とenv example整合は完了済み。commit / pushは未実施。

## Summary

Ricetta運用secretの正本をBitwardenとし、production env、backup monitor Webhook、EC2 SSH鍵、AWS IAM Roleの用途・保管先・配置・更新・復旧方法を1つのデプロイ文書に整理した。`.env.prod.example` からCompose内で固定するDB host / portを削除し、実運用の10変数と整合させた。

## Current Goal

Issue #59の差分をレビューし、commitできる状態にする。

## Current State

- Branch: `docs/issue-59-secret-management`
- Production env item: `Ricetta Production Environment`
- Backup monitor item: `Ricetta Backup Monitor Secrets`
- EC2 SSH item: `Ricetta AWS EC2 SSH`
- AWS access: EC2 IAM Role `ricetta-demo-backup-role`
- `.env.prod`: Git管理外、`600 ubuntu:ubuntu`
- `/etc/ricetta/backup-monitor.env`: Git管理外、`600 root:root`

## What Was Done

- `docs/deploy/secret-management.md` をsecret運用の正本ドキュメントとして追加した。
- Docs indexからSecret Managementへの導線を追加した。
- backup docsの古いBitwarden項目名と重複説明を、Secret Managementへの参照に置き換えた。
- `.env.prod.example` とAWS demo env文書から `POSTGRES_HOST` / `POSTGRES_PORT` を削除した。
- EC2復旧手順、BitwardenとEC2の同時更新、IAM Role利用、secret記録禁止を明文化した。
- Issue #25で扱うsecurity hardening項目を分離した。

## Key Decisions

- secret実値の正本はBitwardenとし、GitHubには変数名・example値・手順だけを置く。
- 新EC2ではBitwardenからsecretを再構成し、旧EC2のsecretファイルをコピーしない。
- AWS接続はIAM Roleとし、固定access keyは作成しない。
- owner / staffの公開デモアカウントとCIの使い捨て値は運用secretと分ける。

## Key Files

- `.env.prod.example`
- `docs/README.md`
- `docs/deploy/secret-management.md`
- `docs/deploy/demo/aws-demo-env.md`
- `docs/deploy/backup/backup-and-restore.md`
- `docs/deploy/backup/postgres-monitoring.md`

## Verification

- `.env.prod.example` 10変数とproduction Composeの外部参照変数: match
- `docker compose --env-file .env.prod.example -f docker-compose.prod.yml config --quiet`: pass
- Markdown relative links: pass
- secret-like literals in diff: none
- `.env.prod` Git tracking / worktree change: none
- `git diff --check`: pass

EC2、AWS、Bitwarden、本番secretの変更は実施していない。

## Current Product Scope

- AWS EC2 public demo
- Bitwarden-based production secret management
- IAM Role-based S3 access
- Backup monitoring with Slack notification

## Out of Scope for MVP

- Production security fallback hardening tracked by Issue #25
- AWS fixed access keys
- Secret automation through Terraform / Ansible

## Next Recommended Tasks

1. Issue #59の差分をレビューしてcommitする。
2. Issue #25でproduction fallbackとdemo account passwordのhardeningを扱う。

## Open Questions

- Bitwarden項目更新の定期的な照合手順を追加するか。

## Notes for Next Agent

- `.env.prod` を作成・変更・Git追加しない。
- secret検査で実値を出力しない。
- Issue #59でDjango settings、Composeの `replace-me` fallback、seed既定パスワードは変更していない。

## Suggested Commit Message

```text
docs(ops): establish Bitwarden secret management
```
