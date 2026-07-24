# Handoff Archive Index

## Operating Rules

- `docs/handoff/latest.md` は毎回更新し、次の作業者が現在地と次の一手をすぐ分かる状態に保つ。
- `latest.md` には最新の状況、重要な未完了事項、次に必要な作業だけを短く残す。
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
