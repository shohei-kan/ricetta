# Ricetta Handoff Latest

## Date

2026-08-15

## Project

Ricetta

## Status

GitHub Issue #56のCloudWatch Agent memory metric未送信に対するsource hotfixを実装中。AWS上のAgentはrunningのまま維持し、AWS / EC2 / IAM / CloudWatch / SNS / Slack変更、commit / pushは未実施。

## Summary

実環境では`disk_used_percent`がCloudWatchへ到着した一方、`mem_used_percent`は未到着。memory originalはすでに`InstanceId`だけを持つため同じdimensionへのrollupが生成されず、`drop_original_metrics`によって唯一のoriginalまで削除されたことが根本原因候補。memory measurementは`mem_used_percent`を維持し、memのdrop設定を削除した。source再適用後に2 metricの実到着を確認する。Alarm、SNS、Dashboardはまだ未作成。

## Current Goal

memory metric hotfixをsourceで確定し、実環境へ再適用して`mem_used_percent`の到着を確認する。

## Current State

- Branch: `fix/issue-56-cloudwatch-memory-metric`
- EC2 detailed monitoring: 使用しない
- Standard metrics: StatusCheckFailed / CPUUtilization / CPUCreditBalance
- Agent metrics: mem_used_percent / disk_used_percent (`/` only)
- Runtime observation: Agent running、disk到着済み、memory未到着
- AWS resources: Alarm / SNS / Dashboardは未作成
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
- memory measurementを`mem_used_percent`へ修正し、送信対象を0件にしていたmemの`drop_original_metrics`を削除した。
- diskのdrop対象を最終出力名`disk_used_percent`へ明示した。
- schema validation後にもCloudWatch上の実metric到着確認が必要であることを追記した。

## Key Decisions

- Agent欠測は監視停止としてbreaching、EC2標準欠測はmissingとして扱う。
- ALARM / OK / INSUFFICIENT_DATAの全状態遷移を同じSNS topicへ通知する。
- EC2 Roleには監視リソースの管理権限を付けず、Agentのmetric送信だけを許可する。
- AWS実値と変動する料金単価はsourceへ保存しない。
- source-first段階のコスト確認は未完了とし、Issue close前に確認日・Free Tier前提・見積額を記録する。
- Memoryはoriginalがすでに`InstanceId`だけなのでdropせず、diskだけを`InstanceId`へrollupしてoriginalをdropする。

## Key Files

- `ops/cloudwatch/amazon-cloudwatch-agent.json`
- `ops/cloudwatch/cloudwatch-agent-put-metrics-policy.json`
- `docs/deploy/monitoring/ec2-resource-monitoring.md`
- `docs/deploy/secret-management.md`
- `docs/README.md`

## Verification

- JSON syntax / Agent設定条件の静的検査: pass
- Markdown relative links: pass
- `git diff --check`: pass
- Secret-like and AWS identifier pattern check: pass
- `.env.prod`: unchanged / untracked
- Backend / frontend source changes: none
- IAM policy changes: none
- 実Agentへの再適用とCloudWatch上のmemory metric到着確認: not run

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

1. source-managed Agent JSONをEC2へ再配置し、`fetch-config -s`で再適用する。
2. runtime copyとAgent statusを確認する。
3. CloudWatchで`mem_used_percent` / `disk_used_percent`の2系列だけが到着することを確認する。
4. SNS、Amazon Q Developer Slack configuration、5 Alarms、Dashboardを管理者側で作成する。

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
