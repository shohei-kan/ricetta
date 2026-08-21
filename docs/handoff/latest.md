# Ricetta Handoff Latest

## Date

2026-08-21

## Project

Ricetta

## Status

GitHub Issue #58「Perform cross-browser smoke test for public demo」のChrome desktop、iPhone Safari、Safari desktop実機test結果を正本へ記録した。Chromeは `Pass with issues`、iPhone Safariは `Pass`、Safari desktopは `Fail`、残り2browserと全browser総合判定は `Not run` である。

SafariとChromeで共通のIssue #85 / #86を確認した。Issue #86は未対応Majorかつpublic release blockerである。

今回のCodex作業ではBrowser、AWS、EC2、公開デモ、DNS、CloudWatch、Slack等の実環境を確認・変更していない。repository内のroute、UI、role、Session / CSRF実装と既存docsだけを照合した。

## Current Goal

Issue #58の手動testをFirefox desktopから継続し、確認した結果だけを記録する。

## Current State

- Branch: `test/issue-58-cross-browser-smoke`
- Manual QA source: `docs/testing/cross-browser-smoke-test.md`
- Browser order: Chrome desktop、iPhone Safari、Safari desktop、Firefox desktop、Edge desktop
- Browser results: Chrome desktop `Pass with issues`、iPhone Safari `Pass`、Safari desktop `Fail`、残り2browser `Not run`
- Overall findings: Blocker 0 / Major 1 / Minor 3 / Cosmetic 1
- Chrome findings: Blocker 0 / Major 1 / Minor 3 / Cosmetic 1
- iPhone Safari findings: Blocker 0 / Major 0 / Minor 0 / Cosmetic 0
- Safari desktop findings: Blocker 0 / Major 1 / Minor 1 / Cosmetic 0
- Chrome / iPhone / Safari role results: owner / staffとも確認済み
- Public release blocker: Issue #86
- Overall result: `Not run`（必須browser未完了）

## What Was Done

- Issue #58本文とAcceptance Criteria、Issue #47との責務境界を確認した。
- source上のroute、navigation、owner / staff権限、主要画面、responsive UIを照合した。
- 5browserのmatrix、共通smoke test、role別checklist、iPhone Safari / desktop固有項目を追加した。
- Accountの表示名を使う、元へ戻せるSession / CSRF代表確認を定義した。
- 重大度、完了条件、問題記録template、Acceptance Criteria対応表を追加した。
- docs indexからmanual QA sourceへの導線を追加した。
- Chrome desktopのpreflight、owner / staff、Session / CSRF、logout結果を記録した。
- Chrome findingsをIssue #82、#83、#84へ紐付けた。
- iPhone Safari実機のresponsive、safe area、navigation、owner / staff、Session / CSRF相当、logout結果を記録した。
- iPhone Safariで一時変更した表示名とPrep statusが元へ復元済みであることを記録した。
- Safari desktopのpreflight、owner / staff、native form、Session / CSRF、browser navigation、logout結果を記録した。
- Issue #85をMinor、Issue #86をMajorかつpublic release blockerとしてChrome / Safariの共通findingへ追加した。

## Key Decisions

- deploy構成ではなく再利用するmanual QA記録のため `docs/testing/` に配置する。
- Cost Summaryは独立routeではなくRecipe Detail内の `原価情報` として確認する。
- 存在しないrouteは専用404ではなく、login状態に応じたredirectとして確認する。
- Session / CSRF確認では店舗・recipe等を変更せず、自分の表示名を一時変更して直ちに戻す。
- 未実施項目、未集計件数、総合判定をPassまたは0件として扱わない。
- Browser個別判定と全browser総合判定を分け、未実施2browserを `Not run` のまま維持する。
- iPhone SafariのSession / CSRFはtoken値や通信headerを記録せず、更新、reload、復元成功による機能確認として扱う。
- Safari desktopは基本表示・認証・Sessionが成功していても、未対応MajorのIssue #86がpublic release blockerであるため `Fail` とする。
- iPhone SafariではIssue #85 / #86を再確認していないため、iPhone結果へ加算しない。

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
- 手動cross-browser test: Chrome desktop、iPhone Safari、Safari desktop実施済み。残り2browserは `Not run`
- Browser / AWS / external serviceへの変更: 実施なし

## Open Items

- Firefox desktop、Edge desktopの手動testを実施する。
- Edgeを確認するOSを実施者が用意する。
- 発見事項はIssue #58で修正せず、重大度を付けてfollow-up Issue候補として記録する。
- Issue #82〜#86の修正結果は各Issueで追跡する。
- Issue #86を解消し、未対応Major 0を確認するまでpublic release blockerは解消しない。

## Suggested Commit Message

```text
docs(test): record Safari desktop smoke results
```
