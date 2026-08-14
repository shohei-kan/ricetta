# Documentation Audit

## 目的

Issue #32 の成果物として、Ricetta の公開ドキュメントを棚卸しし、各情報の正本（Single Source of Truth）と今後の整理方針を明確にする。

この文書は #33 README、#34 AGENTS.md、#35 docs cleanup の作業前提を整理するための監査メモであり、個別仕様の正本そのものではない。

## 基本方針

- `README.md` は初見の閲覧者向けの入口に絞る。
- 詳細仕様は `docs/` 配下へ分離する。
- GitHub Issues を「これからやること・課題・Backlog」の正本とする。
- GitHub Milestones をリリーススコープの正本とする。
- Pull Request を「何を変更したか・なぜ変更したか・どう検証したか」の正本とする。
- Git history を実際の変更履歴の正本とする。
- `AGENTS.md` は AI / Codex が現在のリポジトリで作業するためのルールに絞る。
- 長期的な設計・技術判断は `docs/decisions/` に残す。
- secret の実値は GitHub に保存せず、Bitwarden を正本とする。

## 推奨する Single Source of Truth

```text
README.md
└─ プロジェクト概要 / 主要技術 / Public Demo / docs への入口

docs/
├─ README.md       Documentation index / 責務ルール
├─ product/        プロダクト仕様
├─ technical/      API / Data Model 等の技術仕様
├─ deploy/         Demo / Backup / Restore / Monitoring / Secrets / Recovery
├─ decisions/      長期的な設計・技術判断
└─ releases/       Release 関連情報

GitHub
├─ Issues          今後の作業 / 課題 / Backlog
├─ Milestones      Release scope
├─ Pull Requests   変更内容 / 理由 / Verification
└─ Releases        公開リリース

AGENTS.md
└─ AI / Codex 向けの現在の開発ルール
```

## 棚卸し結果

| 対象 | 判定 | 方針 |
| --- | --- | --- |
| `README.md` | 大幅整理 | 初見向けの概要へ短縮し、詳細は各 docs へリンクする |
| `docs/README.md` | 更新 | Documentation index と各ディレクトリの責務を明示する |
| `AGENTS.md` | 大幅更新 | 現在の技術構成・作業ルールへ合わせ、未導入技術や旧 handoff 運用を除く |
| `docs/product/concept.md` | 維持 | Product Concept の正本として扱う |
| `docs/product/mvp-requirements.md` | 更新 | 現在実装とのズレを確認して更新する |
| `docs/product/mvp-roadmap.md` | 廃止候補 | Roadmap の正本を GitHub Issues / Milestones へ移行する |
| `docs/product/screens.md` | 維持・更新 | 現在の画面仕様の正本として扱う |
| `docs/product/ui-guidelines.md` | 整理 | 共通 UI 原則へ絞り、個別画面仕様は `screens.md` へ寄せる |
| `docs/technical/api-design.md` | 維持・更新 | API 設計の正本。認証方式など現在実装とのズレを修正する |
| `docs/technical/data-model.md` | 維持・更新 | Data Model の正本。Implemented / Future を明確に分ける |
| `docs/deploy/` | 維持・更新 | 公開デモ運用・復旧の正本として扱う |
| `docs/decisions/` | 維持 | 長期的な設計判断の履歴として扱う |
| `docs/handoff/` | 廃止候補 | 日常の引き継ぎを Issue / PR / Git history へ移行する |
| `docs/releases/` | 維持 | Release 関連情報の置き場とする |
| `docs/figma/` | 要精査 | 現在も参照価値がある画像だけ残す |

## 確認できた主な不整合

### AGENTS.md

初期設定時の記述が残っており、現在未導入の技術を利用する前提の指示が含まれている。

例:

- TanStack Query
- React Hook Form
- Zod
- 旧 handoff 更新フロー

AI / Codex が不要な技術導入や古い運用を行わないよう、#34 で現在仕様に合わせる。

### Product docs

`screens.md` と `ui-guidelines.md` の間に、ナビゲーション項目、アイコン利用、Prep Today の操作方法などの差異がある。

責務を以下のように分ける。

- `screens.md`: 個別画面の現在仕様
- `ui-guidelines.md`: 共通 UI / UX 原則

### Technical docs

`api-design.md` と `data-model.md` に、現在は利用していない Basic Authentication を前提とする記述が残っている。

現在の production security 方針・実装と照合して更新する。

`data-model.md` は現行モデルと Future entity が同じ流れで記載されているため、Implemented / Future を明確に分離する。

### Deploy docs

`docs/deploy/` は Backup / Restore / Monitoring / Secret Management を含み、v1.0.0 の手動再構築で利用する正本として十分な構成になっている。

一部に旧 SSH 手順（PEM ファイルを直接指定する接続）が残っているため、現在の Bitwarden SSH Agent を使う `ssh ricetta` 運用へ更新する。

Secret Management は Bitwarden を secret 実値の正本とし、GitHub には変数名・用途・配置先・復旧手順のみを残す現在方針を維持する。

## Handoff の扱い

従来は `docs/handoff/latest.md` と archive を AI / 開発作業の引き継ぎに利用していた。

現在は GitHub Issues / Pull Requests を使う開発フローへ移行しているため、handoff を毎回更新すると同じ情報を複数箇所で管理することになる。

今後の基本フローは以下とする。

```text
AGENTS.md
  ↓
対象 Issue
  ↓
関連 docs
  ↓
実装 / ドキュメント更新
  ↓
Pull Request
```

既存 handoff は即時削除せず、現在も有効な情報が product / technical / deploy / decisions 等の正本へ移っていることを確認してから廃止を判断する。

## ADR / Decision の扱い

既存 Decision は履歴として残す。

現在方針と異なる Decision は本文を履歴ごと削除するのではなく、`Superseded` として扱い、新しい Decision から置き換え関係を示す。

特に以下は見直し対象。

- `0004-tablet-navigation.md`: 現在の navigation 仕様と差異がある
- `0005-documentation-structure.md`: handoff を主要な引き継ぎ手段とする旧方針

Documentation 構造を変更する場合は、新しい ADR を追加して `0005` を Superseded とする。

## v1.0.0 との関係

v1.0.0 は「機能完成」ではなく、GitHub + Bitwarden + S3 Backup + Documentation を正本として Temporary EC2 へ手動再構築できる公開デモを完成条件とする。

そのため Documentation cleanup では、単に文章を見やすくするだけでなく、Temporary EC2 rebuild drill で必要な情報を GitHub docs から辿れる状態にする。

Terraform / Ansible / GitHub Actions CD は v1.0.0 の Documentation scope には含めない。

## 後続 Issue への引き継ぎ

### #33 README

- README を初見向けの入口へ短縮する
- Product / Technical / Deploy / Decisions へのリンクを整理する
- Public Demo、主要技術、プロジェクトの目的を簡潔に示す
- 詳細仕様や長い運用手順を README に重複させない

### #34 AGENTS.md

- 現在の実装・技術構成へ更新する
- 未導入技術を必須とする指示を削除する
- handoff 更新を必須とする旧ルールを廃止する
- Issue → related docs → work → PR の作業フローへ更新する
- secret を GitHub / AI 会話へ記載しないルールを明示する

### #35 Docs cleanup

- Product / Technical / Deploy docs の古い記述を更新する
- `mvp-roadmap.md` の廃止可否を確定する
- `docs/handoff/` の有効情報を移行し、廃止可否を確定する
- `docs/README.md` を新しい Single Source of Truth に合わせる
- 古い ADR は Superseded として履歴を維持する
- `docs/figma/` の公開価値を精査する
- Markdown link と相互参照を確認する

## 完了条件

Issue #32 は、以下を満たした時点で完了とする。

- 現在の主要ドキュメントを棚卸しできている
- 各情報の正本候補を定義できている
- 重複・古い記述・責務の曖昧さを特定できている
- handoff の今後の扱いを整理できている
- #33 / #34 / #35 へ具体的な作業を引き継げる状態になっている
