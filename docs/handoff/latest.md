# Ricetta Handoff Latest

## Date

2026-08-19

## Project

Ricetta

## Status

GitHub Issue #78「Create Ricetta incident response runbook」のsource-first文書整備を実施。Ricetta全体の障害対応入口として、共通トリアージ、read-onlyコマンド、症状別判断、状態変更の安全境界、incident記録templateを追加した。

今回のCodex作業ではAWS、EC2、Docker container、systemd、DNS、SNS、CloudWatch、Slack等の実環境を確認・変更していない。文書とrepository内の構成だけを照合した。

## Current Goal

Issue #78のRunbook差分を検証し、掲載commandと既存正本への導線をcommit前に確認する。

## Current State

- Branch: `docs/issue-78-incident-response-runbook`
- Incident response source: `docs/deploy/operations/incident-response.md`
- Production services: `db` / `backend` / `frontend` / `caddy`
- Response policy: read-only確認と証拠保全を優先
- Restore / reset / rollback / rebuild: 判断後に既存正本またはIssue #69へ移動
- Infrastructure management: 手動。Terraform / Ansible化は別Issue

## What Was Done

- Issue #78本文とAcceptance Criteriaを確認した。
- 最初の5〜10分の共通トリアージを追加した。
- Docker、Caddy、Django、PostgreSQL、systemd、DNS、TLSのread-only確認commandを説明付きで追加した。
- application、container、DB、EC2、CloudWatch、backup、S3、通知、DNS、TLS、restore、rebuild、securityの症状別Runbookを追加した。
- container再作成、app再起動、rollback、restore、rebuild等の判断matrixを追加した。
- 状態変更commandをread-only調査から分離し、対象、前提、verification、禁止事項を明記した。
- docs indexとmonitoring / cost / backup / demo / secret正本から相互リンクを追加した。

## Key Decisions

- 横断的な運用入口のため `docs/deploy/operations/` に配置する。
- Runbookは一次切り分けと判断基準を正本とし、詳細なrestore、reset、monitoring、secret復旧を重複させない。
- DB / volumeの削除・初期化や`docker compose down -v`を通常手順に含めない。
- CloudWatchやAWS確認はread-onlyとし、private identifierをIssueやSlackへ転記しない。
- security侵害疑いは通常障害と分離し、証跡保全とcredential対応を優先する。

## Key Files

- `docs/deploy/operations/incident-response.md`
- `docs/README.md`
- `docs/deploy/monitoring/ec2-resource-monitoring.md`
- `docs/deploy/monitoring/aws-cost-monitoring.md`
- `docs/deploy/backup/backup-and-restore.md`
- `docs/deploy/demo/aws-demo-env.md`
- `docs/deploy/secret-management.md`
- `docs/handoff/latest.md`

## Verification

- Markdown相対リンク: pass
- `git diff --check`: pass
- secret-like / private identifier pattern: pass（systemd template unitの`@`はEmailではないことを確認）
- Markdown内bash構文: pass
- command / service / unit / path照合: pass
- `.env.prod`、backend、frontend、runtime config無変更: pass
- AWS / external serviceへの変更: 実施なし

## Open Items

- Issue #69のTemporary EC2 rebuild Runbook完成後、本Runbookのrebuild導線をfile linkへ更新する。
- 実障害または安全なdrillで、コマンドの期待結果と判断matrixを継続改善する。

## Suggested Commit Message

```text
docs(ops): add incident response runbook
```
