# 0007 Documentation Source of Truth

## Date

2026-08-15

## Status

Accepted

## Context

Ricettaでは開発初期に `docs/handoff/latest.md` を中心としたAI引き継ぎ運用を採用していた。

その後、GitHub Issues、Milestones、Pull Requestsを使う開発フローへ移行し、READMEや各docsにも詳細情報が増えたことで、同じ情報が複数箇所に重複する状態が生まれた。

v1.0.0では、GitHub + Bitwarden + S3 Backup + Documentationを正本としてTemporary EC2へ手動再構築できる公開デモを完成条件とするため、「どこを見れば現在情報が分かるか」を明確にする必要がある。

## Decision

情報の責務を以下のように分ける。

```text
README.md
└─ 初見向けのプロジェクト概要 / Public Demo / 主要技術 / docsへの入口

docs/
├─ README.md       Documentation index
├─ product/        プロダクト仕様
├─ technical/      API / Data Modelなどの技術仕様
├─ deploy/         Demo / Backup / Restore / Monitoring / Secrets
├─ decisions/      長期的な設計・技術判断
└─ releases/       Release関連記録

GitHub
├─ Issues          今後の作業 / 課題 / Backlog
├─ Milestones      Release scope
├─ Pull Requests   変更内容 / 理由 / Verification
└─ Releases        公開リリース

AGENTS.md
└─ Codex / AI agent向けの現在の開発ルールと正本docsへの入口
```

production secretの実値はGitHubへ保存せず、Bitwardenを正本とする。

`docs/handoff/` は過去の引き継ぎ記録として参照できるが、現在の作業フローでは `latest.md` を毎回更新しない。

短期的な作業文脈はIssueとPull Requestで管理し、長期的に残す設計判断は `docs/decisions/` に記録する。

今後の実装順やBacklogは静的なMVP roadmapでは管理せず、GitHub Issues / Milestonesを正本とする。

## Reasons

- 同じ情報を複数箇所で更新する二重管理を避けるため。
- 初見の閲覧者と実装者で必要な情報を分離するため。
- AI agentが古いhandoffや旧ロードマップを現在仕様として扱わないようにするため。
- Pull Requestに変更理由とVerificationを集約し、実際の変更履歴と結びつけるため。
- v1.0.0の手動再構築で、必要な情報をGitHub docsから迷わず辿れるようにするため。

## Consequences

### Positive

- 情報の正本が明確になる。
- READMEを簡潔に保てる。
- Issue / PRとdocsの責務が分離される。
- AI / 人間ともに現在仕様を追いやすくなる。
- handoffの更新漏れによる古い「現在地」が残りにくくなる。

### Negative

- 古いhandoffや過去ADRには現在仕様と異なる内容が残る。
- Decisionを変更した場合はSuperseded関係を明示する必要がある。
- docsと実装の不整合を定期的に監査する必要がある。

## Supersedes

- `0005-documentation-structure.md`

## Related Docs

- `README.md`
- `AGENTS.md`
- `docs/README.md`
- `docs/documentation-audit.md`
