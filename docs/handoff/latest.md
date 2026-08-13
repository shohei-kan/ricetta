# Ricetta Handoff Latest

## Date

2026-08-13

## Project

Ricetta

## Status

GitHub Issue #56「Add minimal EC2 resource monitoring with CloudWatch」のsource-first実装を完了。AWS / EC2 / IAM / Slack変更、Agent install、commit / pushは未実施。

## Summary

EC2基本モニタリング3種とCloudWatch Agentカスタムメトリクス2種の最小監視設計を追加した。Agent設定とnamespace制限付きIAM policyをGit管理し、Alarm、missing data、SNS→Amazon Q Developer→Slack、Dashboard、一次対応、rollback、再構築、コスト確認を文書化した。

## Current Goal

source差分をレビューし、AWS管理者権限で段階的に実環境へ反映・検証する。

## Current State

- Branch: `ops/issue-56-cloudwatch-monitoring`
- EC2 detailed monitoring: 使用しない
- Standard metrics: StatusCheckFailed / CPUUtilization / CPUCreditBalance
- Agent metrics: mem_used_percent / disk_used_percent (`/` only)
- Collection: 60 seconds、namespace `CWAgent`、dimension `InstanceId` only
- EC2 Role permission: namespace制限付きcloudwatch:PutMetricDataだけ
- Logs / trace / X-Ray / high-resolution metrics: なし
- StatusCheckFailed: Maximum、60秒、1/1、1以上、missing

## What Was Done

- CloudWatch Agent設定JSONを追加した。
- 最小IAM policy JSONを追加した。
- Ubuntu x86_64での署名検証、install、設定validation、起動、自動起動確認を文書化した。
- 5 Alarmのthreshold、period、M-of-N、missing data、state通知方針を決定した。
- commit前レビューでStatusCheckFailedを基本モニタリング対応の60秒評価へ修正した。
- Agent公開鍵fingerprint照合、usage data無効化、IAM反映前の停止確認を追加した。
- CPUCreditBalance 24 creditsの判断理由を記録した。
- SNS→Amazon Q Developer in chat applications→Slackの構築・テスト手順を記録した。
- Dashboard、一次対応、rollback、再構築、コスト確認を文書化した。
- docs indexとsecret managementを更新した。

## Key Decisions

- Agent欠測は監視停止としてbreaching、EC2標準欠測はmissingとして扱う。
- ALARM / OK / INSUFFICIENT_DATAの全状態遷移を同じSNS topicへ通知する。
- EC2 Roleには監視リソースの管理権限を付けず、Agentのmetric送信だけを許可する。
- AWS実値と変動する料金単価はsourceへ保存しない。
- source-first段階のコスト確認は未完了とし、Issue close前に確認日・Free Tier前提・見積額を記録する。

## Key Files

- `ops/cloudwatch/amazon-cloudwatch-agent.json`
- `ops/cloudwatch/cloudwatch-agent-put-metrics-policy.json`
- `docs/deploy/monitoring/ec2-resource-monitoring.md`
- `docs/deploy/secret-management.md`
- `docs/README.md`

## Verification

- JSON syntax: pass
- Markdown relative links: pass
- `git diff --check`: pass
- Secret-like and AWS identifier pattern check: pass
- Backend / frontend source changes: none

## Current Product Scope

- Single EC2 public demo resource monitoring
- Minimal CloudWatch metrics and Slack alarm delivery design
- Manual source-first reconstruction

## Out of Scope for MVP

- CloudWatch Logs、trace、X-Ray
- Auto Scaling、自動復旧、自動再起動
- Terraform / Ansible implementation
- External monitoring services

## Next Recommended Tasks

1. Agent policyをAWS管理者sessionからEC2 Roleへ追加する。
2. EC2で公式deb署名を検証してAgentをinstallし、2 metricsの到着を確認する。
3. SNS、Amazon Q Developer Slack configuration、5 Alarms、Dashboardを管理者側で作成する。
4. 安全な一時thresholdでALARM / OK通知を確認し、EC2再起動後のAgent復旧を確認する。

## Open Questions

- 実環境の通常負荷を2～4週間観測後、CPUCreditBalance 24 creditsが適切か再評価する。
- 実装時点のap-northeast-1料金見積をAWS Pricing Calculatorで記録する。

## Notes for Next Agent

- account ID、Instance ID、SNS ARN、Slack IDsをGitへ追加しない。
- EC2 RoleへCloudWatchAgentServerPolicyやAlarm/SNS/Dashboard管理権限を付けない。
- Agent停止計画時はcustom metric alarmがALARMになるため事前共有する。

## Suggested Commit Message

```text
docs(ops): add minimal EC2 CloudWatch monitoring
```
