# Ricetta Handoff Latest

## Date

2026-08-17

## Project

Ricetta

## Status

GitHub Issue #56「Add minimal EC2 resource monitoring with CloudWatch」の実装と実環境検証が完了。source、Agent、IAM、2 custom metrics、5 Alarm、SNS→Amazon Q→Slack通知、Dashboard、EC2再起動後の自動復旧、コスト見積を確認済み。Issue #56のPR / merge / close待ち。

## Summary

Ubuntu 24.04 x86_64 / `t3.micro`へCloudWatch Agent `1.300071.0b1720`を署名検証後に導入し、`CWAgent`へ`mem_used_percent`と`disk_used_percent`の2系列だけを60秒間隔・`InstanceId` dimensionで送信する構成を完成させた。5 Alarmは設計表どおり作成し、SNS→Amazon Q Developer in chat applications→SlackでALARM / OK通知を確認した。Dashboardと計画再起動後の自動復旧も検証済み。

## Current Goal

Issue #56のdocumentation差分をレビューしてPR / merge / closeし、その後に公開デモのsmoke testとrelease readinessへ進む。

## Current State

- Branch: `docs/issue-56-cloudwatch-verification`
- EC2 monitoring: 基本モニタリング、詳細モニタリングは使用しない
- Agent: enabled / active、running / configured、usage data無効
- Agent authentication: 固定access keyなし、EC2 IAM Role
- Agent permission: namespace `CWAgent`限定の`cloudwatch:PutMetricData`だけ
- Custom metrics: `mem_used_percent` / `disk_used_percent`、60秒、`InstanceId`のみ
- Alarms: 5件、ActionsEnabled、ALARM / OK / INSUFFICIENT_DATA通知あり、最終状態はすべてOK
- Notifications: CloudWatch Alarm → SNS → Amazon Q Developer → Slack
- Dashboard: 1件、7 widgets、validation messageなし
- Infrastructure management: 手動。Terraform / Ansible化は別Issue

## What Was Done

- 公式deb、署名、GPG keyを取得し、公式fingerprintとの一致とGPG署名成功後にAgentをinstallした。
- repository JSONとruntime copyの一致、JSON schema validation、config translationを確認した。
- source-managed最小IAM policyをEC2 Roleへ適用し、固定credentialを使用しない構成にした。
- memory未送信を調査し、mem originalをdropして送信対象が0件になる原因候補へ対応した。
- `mem_used_percent` originalを残し、diskだけを`InstanceId`へ集約してoriginalをdropする構成へ修正した。
- CloudWatch上に2 custom metricsだけが存在し、最新datapointが継続到着することを確認した。
- 設計表どおり5 Alarmを作成し、通知actionと最終OK状態を確認した。
- SNS、Amazon Q channel configuration、Slack通知経路を作成し、test message、ALARM、OK、スマートフォン通知を確認した。
- 一時Alarmを削除し、本番用Alarmが5件だけ残ることを確認した。
- 5 Alarm、5 metrics、説明textを表示するDashboardを作成した。
- 2026-08-17の計画再起動後にAgent、metrics、Docker Compose全4サービス、backend / db health、HTTPS health、Alarm状態を確認した。
- 料金前提を確認し、Free Tierが他用途で消費されていない前提で監視追加分を月額USD 0と見積もった。

## Key Decisions

- Agentから送るcustom metricは`mem_used_percent`と`disk_used_percent`の2系列だけにする。
- Memory originalはすでに`InstanceId`だけなのでdropせず、diskだけを`InstanceId`へrollupしてoriginalをdropする。
- EC2 Roleにはmetric送信権限だけを付与し、Alarm / SNS / Dashboard管理権限を付与しない。
- ALARM / OK / INSUFFICIENT_DATAを同じSNS経路でSlackへ通知する。
- 自動再起動、EC2停止、自動復旧actionは設定せず、Alarm actionは通知だけにする。
- Dashboard、SNS、Alarm、Amazon Qは手動管理とし、Terraform / Ansible化は別Issueで扱う。
- AWS resource ID、ARN、Slack ID、secret実値はrepositoryへ保存しない。

## Key Files

- `ops/cloudwatch/amazon-cloudwatch-agent.json`
- `ops/cloudwatch/cloudwatch-agent-put-metrics-policy.json`
- `docs/deploy/monitoring/ec2-resource-monitoring.md`
- `docs/deploy/secret-management.md`
- `docs/README.md`

## Verification

- Agent package fingerprint / GPG signature: pass
- Repository config / runtime copy一致: pass
- JSON schema validation / config translation: pass
- Agent enabled / active / running / configured: pass
- `CWAgent` custom metrics 2系列、60秒、`InstanceId`のみ: pass
- 5 Alarmの設定、actions、最終OK状態: pass
- SNS subscription / Amazon Q test message: pass
- Slack ALARM / OK / smartphone notification: pass
- Temporary Alarm削除、本番Alarm 5件のみ: pass
- Dashboard 7 widgets / validation message 0: pass
- EC2 reboot後のAgent / metric自動復旧: pass
- Docker Compose全4サービス、backend / db health、HTTPS health 200: pass
- Cost estimate reviewed: 2026-08-17
- Account全体のFree Tier使用量: 未確認

## Current Product Scope

- Single EC2 public demo resource monitoring
- Minimal CloudWatch metrics and Slack alarm notifications
- Source-managed Agent configuration and IAM policy
- Manual reconstruction and incident response procedures

## Out of Scope for MVP

- CloudWatch Logs、trace、X-Ray
- Auto Scaling、自動復旧、自動再起動
- Terraform / Ansible implementation
- External monitoring services

## Next Recommended Tasks

1. Issue #56の差分をレビューしてPRを作成する。
2. PRをmergeし、Issue #56をcloseする。
3. 公開デモのsmoke testとrelease readiness確認へ進む。

## Open Questions

- なし。

## Notes for Next Agent

- CPUCreditBalance 24 creditsは初期early-warning値のため、2～4週間後に実績から再評価する。
- Billing / Cost Explorerで監視導入後の実コストを継続確認する。
- Terraform / Ansible化は別Issueで扱う。
- account ID、Instance ID、ARN、Slack workspace/channel ID、secret実値をdocsへ追加しない。

## Suggested Commit Message

```text
docs(ops): record CloudWatch production verification
```
