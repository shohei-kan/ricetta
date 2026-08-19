# Ricetta Handoff Latest

## Date

2026-08-19

## Project

Ricetta

## Status

GitHub Issue #77「AWSコスト監視と課金ガードレール」の実環境設定確認とsource-first文書整備を実施。Budget、Cost Explorer、Free Tier、resource棚卸し、月次確認、想定外課金時の初動、再構築、rollbackを正本へ集約した。Budget→Slack実通知到着は次回評価待ち。

この文書整備より前に、管理者がSNS PolicyへのAWS Budgets用Statement追加、ACTUAL 30 / 50 / 80 / 100%へのSNS subscriber追加、FORECASTED 100%通知追加をAWS実環境で実施済み。今回のCodex作業ではAWSや外部サービスを変更していない。

## Current Goal

Issue #77のdocumentation差分を検証し、Budget→Slack実通知到着確認を保留事項として引き継ぐ。

## Current State

- Branch: `ops/issue-77-aws-cost-monitoring`
- AWS cost source of truth: `docs/deploy/monitoring/aws-cost-monitoring.md`
- Budget: monthly COST / USD 10 / account全体 / 5段階通知 / Action 0件
- Budget notifications: Email + existing SNS→Amazon Q→Slack
- Budget→Slack actual delivery: 次回評価待ち
- EC2 resource monitoring: Issue #56で構築・検証済み。責務は専用文書に分離
- Infrastructure management: 手動。Terraform / Ansible化は別Issue

## What Was Done

- Issue #77の本文とAcceptance Criteriaを確認した。
- AWSアカウント全体のコスト監視正本を追加した。
- 実環境で確認済みのBudget、通知、Cost Explorer、Free Tier、resource、S3状態を確認日付きで記録した。
- 文書整備前に実施済みのSNS Policy変更、ACTUAL 4通知へのSNS subscriber追加、FORECASTED通知追加を変更履歴として記録した。
- 24時間稼働時の税込月額約USD 18を、請求確定値ではない概算として分離した。
- 月次のBudget / Cost Explorer / Free Tier / Credits / Bills確認手順を追加した。
- Cost Explorerの調査順とresource棚卸しchecklistを追加した。
- 想定外課金時の初動、再構築、rollback手順を追加した。
- Issue #56文書との責務分離と相互リンク、docs indexからの導線を追加した。
- account固有値が必要な形骸的JSONは追加しなかった。

## Key Decisions

- Budget USD 10は厳格な警戒線として当面維持する。
- Budgetは約8〜12時間の更新遅延があるため、リアルタイム監視や自動停止として扱わない。
- 自動Budget Actionは使用せず、削除・停止前にbackupと依存関係を確認する。
- AWS Account ID、Instance ID、ARN、Email、Slack IDをrepositoryへ保存しない。
- EBS未暗号化はIssue #77で変更せず、Issue #69のTemporary EC2 rebuild drillへ引き継ぐ。
- S3は現状極小のためLifecycleを追加せず、長期保持と実コストを定期的に再評価する。
- Budget / SNS / Amazon Qのaccount固有設定は手動管理し、Terraform / Ansible化は別Issueで扱う。

## Key Files

- `docs/deploy/monitoring/aws-cost-monitoring.md`
- `docs/deploy/monitoring/ec2-resource-monitoring.md`
- `docs/README.md`
- `docs/handoff/latest.md`

## Verification

- Markdown相対リンク: pass
- `git diff --check`: pass
- secret-like pattern / account固有identifier検査: pass
- `.env.prod`、backend、frontendの無変更確認: pass
- 今回のCodexによるAWS / external serviceへの追加変更: 実施なし（文書整備前の実環境変更は上記Statusと正本文書に記録）

## Open Items

- 次回Budget評価でBudget→SNS→Amazon Q→Slackの実通知到着を確認する。
- 到着結果をAWS cost monitoring正本とhandoffへ記録する。
- Public demo公開後の実績を見てBudget上限を再評価する。現時点ではUSD 10を維持する。
- Issue #69で暗号化されたroot EBSとしての再構築を検討する。

## Suggested Commit Message

```text
docs(ops): document AWS cost monitoring guardrails
```
