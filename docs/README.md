# Ricetta Docs

Ricettaの詳細ドキュメントの入口です。

プロジェクト概要、Public Demo、主要機能、Quick Startはルートの [`README.md`](../README.md) を参照してください。

このディレクトリでは、同じ情報を複数ファイルへ重複させず、責務ごとに正本を分けて管理します。

## Product

「何を作るか」「どんな体験にするか」に関する正本です。

- [Concept](./product/concept.md) — プロダクトの背景、対象ユーザー、解決したい課題
- [MVP requirements](./product/mvp-requirements.md) — 現在のMVP要件
- [Screen specifications](./product/screens.md) — 画面ごとの仕様
- [UI guidelines](./product/ui-guidelines.md) — 共通UI原則

今後の作業順やBacklogはProduct docsではなくGitHub Issues / Milestonesで管理します。

## Technical

API・データモデルなど、現在実装に近い技術仕様の正本です。

- [API design](./technical/api-design.md)
- [Data model](./technical/data-model.md)

実装変更でAPIやデータモデルが変わる場合は、対応する正本も更新します。

## Deploy / Operations

公開デモ、secret、backup / restore、monitoringなど運用手順の正本です。

- [Public demo environment](./deploy/demo/demo.md)
- [AWS demo env checklist](./deploy/demo/aws-demo-env.md)
- [Secret management](./deploy/secret-management.md)
- [Backup and restore](./deploy/backup/backup-and-restore.md)
- [PostgreSQL backup](./deploy/backup/postgres-backup.md)
- [PostgreSQL restore](./deploy/backup/postgres-restore.md)
- [PostgreSQL backup monitoring](./deploy/backup/postgres-monitoring.md)
- [EC2 resource monitoring](./deploy/monitoring/ec2-resource-monitoring.md)

production secretの実値はGitHubへ保存せず、Bitwardenを正本とします。

## Decisions

長期的に残すべき設計・技術判断を記録します。

- [Architecture decisions](./decisions/)

過去の判断が変更された場合は、履歴を消すのではなく必要に応じてSupersededとして残します。

## Releases

公開リリース時の記録です。

- [Release note template](./releases/TEMPLATE.md)
- [v0.1.0](./releases/v0.1.0.md)

今後のrelease scopeはGitHub Milestones、公開リリースはGitHub Releasesを正本として扱います。

## Design References

画面検討・デザイン参照用の素材です。

- [Figma exports and notes](./figma/)

ここはProduct仕様の正本ではありません。現在の画面仕様は [`product/screens.md`](./product/screens.md) と [`product/ui-guidelines.md`](./product/ui-guidelines.md) を優先します。

## Project Management / Handoff

今後の作業、Backlog、Acceptance CriteriaはGitHub Issues、release scopeはGitHub Milestones、変更内容・理由・VerificationはPull Requestsで管理します。

`docs/handoff/` は過去のAI引き継ぎ記録として残っていますが、現在の作業フローでは `latest.md` を毎回更新しません。短期的な作業文脈はIssue / PRを正本とし、長期的な設計判断は `docs/decisions/` に残します。

## Documentation Maintenance

- READMEは初見向けの入口として簡潔に保つ。
- 詳細は責務ごとの正本docsへ置く。
- 同じ仕様を複数ファイルへコピーしない。
- 古いドキュメントを現在仕様として案内しない。
- secret / credential / private dataをGitHubへ記載しない。
- ドキュメント間に矛盾がある場合は、実装と正本を確認して責務を一つに寄せる。
