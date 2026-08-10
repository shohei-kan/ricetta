# Ricetta Handoff Latest

## Date

2026-08-11

## Project

Ricetta

## Status

GitHub Issue #12「Add backup monitoring」の実装・EC2検証は完了済み。ローカルrepoでdocsとopsの整合性を整理済み。

## Summary

PostgreSQL backup失敗とS3上のbackup異常をsystemd `OnFailure` で検知し、Slackへ原因別通知する構成をdocsに反映した。backup / restore / monitoringの責務を分離し、完了済みの監視・通知をOut of ScopeとFuture Improvementsから削除した。

## Current Goal

Issue #12の変更をレビューし、commit / pushできる状態にする。

## Current State

- Branch: `ops/issue-12-backup-monitoring`
- PostgreSQL backup: daily 04:10 JST
- Demo reset: daily 04:30 JST
- Backup monitor: daily 05:00 JST
- Monitor max age: 21600 seconds (6 hours)
- Slack: `LINTAKE Monitor` / `#infra-alerts`
- Webhook secret file: `/etc/ricetta/backup-monitor.env` (Git管理外)

## What Was Done

- backup exit code 21–25、monitor exit code 31–34を原因別通知と照合した。
- backup / monitor serviceの `OnFailure` とalert serviceの参照を確認した。
- `backup-and-restore.md`、`postgres-backup.md`、Docs indexからmonitoring docsへの導線を追加した。
- 完了済みのbackup monitoring / Slack通知 / 異常検知を将来項目から削除した。
- READMEの将来項目をS3 Lifecycleとrestore drillに具体化した。
- 旧deploy docs path、Markdownリンク、secret候補、`.env.prod` 非変更を確認した。

## Key Decisions

- backup取得は `postgres-backup.md`、restoreは `postgres-restore.md`、監視・通知は `postgres-monitoring.md` に分離する。
- 正常時は通知せず、対応が必要な異常時だけSlack通知する。
- Webhook URLはGitやdocsに記録せず、EC2のroot-only secret fileから読み込む。
- Slack通知の共通化、他アプリ展開、S3 Lifecycle、restore drill、host/container監視、IaCは将来課題とする。

## Key Files

- `ops/scripts/ricetta-postgres-backup.sh`
- `ops/scripts/ricetta-backup-monitor.sh`
- `ops/scripts/ricetta-backup-alert.sh`
- `ops/scripts/ricetta-backup-notify.sh`
- `ops/systemd/ricetta-postgres-backup.service`
- `ops/systemd/ricetta-postgres-backup.timer`
- `ops/systemd/ricetta-backup-monitor.service`
- `ops/systemd/ricetta-backup-monitor.timer`
- `ops/systemd/ricetta-backup-alert@.service`
- `docs/deploy/backup/backup-and-restore.md`
- `docs/deploy/backup/postgres-backup.md`
- `docs/deploy/backup/postgres-restore.md`
- `docs/deploy/backup/postgres-monitoring.md`

## Verification

ローカルで実行済み:

```bash
bash -n ops/scripts/ricetta-postgres-backup.sh
bash -n ops/scripts/ricetta-backup-monitor.sh
bash -n ops/scripts/ricetta-backup-alert.sh
bash -n ops/scripts/ricetta-backup-notify.sh
git diff --check
```

- shell syntax: pass
- old deploy path grep: pass
- Markdown relative link check: pass
- potential secret literal / Webhook assignment check: pass
- `.env.prod` unchanged: pass
- timer / service / exit codeの実装とdocsの照合: pass

EC2検証はユーザー実施済みの結果をdocsへ反映。このタスクでSSHやAWS変更は実行していない。

## Current Product Scope

- Ricetta public demo on AWS EC2
- PostgreSQL daily backup, gzip, S3 upload, local retention
- Backup health monitoring and failure-only Slack notification
- Temporary databaseを使ったsafe restore verification

## Out of Scope for MVP

- Public `ricetta` DBへの直接restore
- S3 Lifecycleによる長期世代管理
- RDS / multi-region / high availability
- EC2 / disk / containerの総合監視
- AWS環境の完全自動再構築

## Next Recommended Tasks

1. 差分レビュー後、Issue #12のcommitを作成する。
2. 後続IssueでS3 Lifecycleと定期restore drillを検討する。
3. 必要に応じてSlack通知処理を他アプリと共通化する。

## Open Questions

- systemd unitの自動静的検証をCIに追加するか。
- S3 Lifecycleとrestore drillをどの後続Issueで扱うか。

## Notes for Next Agent

- Webhook URLの実値をGit、docs、Issue、PR、ログへ記録しない。
- `MAX_AGE_SECONDS=21600` は通常運用値。failure test時の一時値を残さない。
- `systemd-analyze` はローカルmacOSにないため未実施。EC2上のunit動作は検証済み。

## Suggested Commit Message

```text
feat(ops): add backup monitoring
```
