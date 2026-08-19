# Ricetta Handoff Latest

## Date

2026-08-19

## Project

Ricetta

## Status

GitHub Issue #58「Perform cross-browser smoke test for public demo」のsource-first手動test計画を整備した。実際の手動cross-browser testはまだ実施しておらず、全結果は `Not run` である。

今回のCodex作業ではBrowser、AWS、EC2、公開デモ、DNS、CloudWatch、Slack等の実環境を確認・変更していない。repository内のroute、UI、role、Session / CSRF実装と既存docsだけを照合した。

## Current Goal

Issue #58の手動testをChrome desktopから順に実施し、確認した結果だけを記録する。

## Current State

- Branch: `test/issue-58-cross-browser-smoke`
- Manual QA source: `docs/testing/cross-browser-smoke-test.md`
- Browser order: Chrome desktop、iPhone Safari、Safari desktop、Firefox desktop、Edge desktop
- Browser results: 全5browser `Not run`
- Role results: owner / staffとも `Not run`
- Overall result: `Not run`

## What Was Done

- Issue #58本文とAcceptance Criteria、Issue #47との責務境界を確認した。
- source上のroute、navigation、owner / staff権限、主要画面、responsive UIを照合した。
- 5browserのmatrix、共通smoke test、role別checklist、iPhone Safari / desktop固有項目を追加した。
- Accountの表示名を使う、元へ戻せるSession / CSRF代表確認を定義した。
- 重大度、完了条件、問題記録template、Acceptance Criteria対応表を追加した。
- docs indexからmanual QA sourceへの導線を追加した。

## Key Decisions

- deploy構成ではなく再利用するmanual QA記録のため `docs/testing/` に配置する。
- Cost Summaryは独立routeではなくRecipe Detail内の `原価情報` として確認する。
- 存在しないrouteは専用404ではなく、login状態に応じたredirectとして確認する。
- Session / CSRF確認では店舗・recipe等を変更せず、自分の表示名を一時変更して直ちに戻す。
- 未実施項目、未集計件数、総合判定をPassまたは0件として扱わない。

## Key Files

- `docs/testing/cross-browser-smoke-test.md`
- `docs/README.md`
- `docs/handoff/latest.md`

## Verification

- Markdown相対リンク: pass
- `git diff --check` / Markdown末尾空白: pass
- route / navigation / role照合: pass
- secret-like / private identifier pattern: pass
- `.env.prod`、backend、frontend、package / lockfile無変更確認: pass
- 手動cross-browser test: 未実施（全件 `Not run`）
- Browser / AWS / external serviceへの変更: 実施なし

## Open Items

- Chrome desktopから手動testを開始する。
- iPhone実機、各desktop browser、Edgeを確認するOSを実施者が用意する。
- 発見事項はIssue #58で修正せず、重大度を付けてfollow-up Issue候補として記録する。

## Suggested Commit Message

```text
docs(test): add cross-browser smoke test plan
```
