# Handoff Archive Index

## Archived Operating Rules

以下はhandoff archiveを運用していた当時の履歴です。現在はIssue / Pull Requestを作業文脈の正本とし、`docs/handoff/latest.md`を毎回更新する必須運用は採用しません。現在方針は[Documentation Source of Truth](../../decisions/0007-documentation-source-of-truth.md)を参照してください。

- `latest.md` には当時の最新状況、重要な未完了事項、次に必要な作業だけを短く残していた。
- 過去のhandoffは削除せず、`docs/handoff/archive/` に積み重ねる。
- archiveは作業単位ごとに新規ファイルを増やさず、大まかな内容でファイルを分ける。
- 既存の大分類に収まる場合は、そのarchiveファイルへ追記する。
- archive内の各エントリは `## YYYY-MM-DD タイトル` 形式で区切る。
- 新しいarchiveファイルを作る場合は、このindexに用途を追加する。

## Files

- [planning-and-docs.md](./planning-and-docs.md)
  - 企画、MVP要件、画面設計、データ/API設計などの初期ドキュメント整理。

- [backend-foundation.md](./backend-foundation.md)
  - scaffold、Docker、CI、Auth / Shop scope、Ingredient API などbackend土台作業。

- [frontend-implementation.md](./frontend-implementation.md)
  - frontend画面実装ログ。

- [release-prep.md](./release-prep.md)
  - MVP公開前の確認、デプロイ、リリース準備。
