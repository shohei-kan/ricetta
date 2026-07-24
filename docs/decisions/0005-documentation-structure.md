# 0005 Documentation Structure

## Date

2026-05-05

## Status

採用

## Context

Ricettaでは、次の作業者やエージェントがプロジェクト全体の履歴を読み直さなくても開発を継続できるように、handoffドキュメントを使う。

以前の `docs/handoff/latest.md` は複数フェーズの作業内容が蓄積し始めており、「現在地を把握するためのhandoff」として使いづらくなっていた。

## Decision

Ricettaでは、以下のドキュメント構成を使う。

```text
docs/README.md
docs/product/
docs/technical/
docs/handoff/latest.md
docs/handoff/archive/
docs/handoff/archive/index.md
docs/decisions/
```

`docs/README.md` は、プロジェクトドキュメント全体の入口とする。

`docs/product/` には、プロダクトコンセプト、MVP要件、ロードマップ、画面仕様、UIガイドラインを置く。

`docs/technical/` には、API設計やデータモデルなど、実装に近い設計ドキュメントを置く。

`docs/handoff/latest.md` には、最新の現在地と次に推奨される作業だけを残す。

`docs/handoff/archive/` には、過去のhandoffを細かい作業単位ではなく、大まかなトピックごとに保存する。

archiveファイル名は、以下のような大分類の名前にする。

```text
planning-and-docs.md
backend-foundation.md
frontend-implementation.md
release-prep.md
```

各archiveファイルの中では、日付とタイトルの見出しでエントリを区切る。

`docs/handoff/archive/index.md` は、archiveファイルの目次とする。個別エントリをすべて列挙するのではなく、各archiveファイルの大まかな用途を示す。

長期的に残すべき意思決定は `docs/decisions/` に置く。Ricettaではroot直下の `decisions/` ディレクトリは使わない。

## Reasons

- `latest.md` を短く保ち、次の作業者にとって使いやすくするため。
- 過去の文脈を検索可能なまま残しつつ、現在のhandoffを重くしすぎないため。
- 長期的な意思決定と、短期的な作業文脈を分けるため。
- product系とtechnical系のドキュメントを、読む目的ごとに分けるため。
- archiveファイルが細かく増えすぎるのを避けるため。

## Consequences

- エージェントは `latest.md` を置き換える前に、古いhandoff内容をarchiveへ移すか、要約する必要がある。
- 類似するhandoffエントリは、既存の大分類archiveファイルへ追記する。
- 新しいarchiveファイルは、新しい大きな作業領域が出てきた場合だけ作成する。

## Related Docs

- `AGENTS.md`
- `docs/handoff/latest.md`
- `docs/handoff/archive/index.md`
