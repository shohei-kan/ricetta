# AGENTS.md

## Purpose

このファイルは、Ricettaで作業するCodex / AI agent向けの開発ルールと入口を定義する。

AGENTS.mdはプロダクト仕様全文の正本ではない。作業開始時にこのファイル、対象Issue、関連する正本docsを確認し、実装とドキュメントの不整合を増やさないこと。

## Project

Ricetta（リチェッタ）は、小規模飲食店向けのレシピ・原価・仕込み管理Webアプリ。

現在のv1.0.0は機能完成ではなく、GitHub + Bitwarden + S3 Backup + Documentationを正本として、一時EC2へ手動再構築できる公開デモを完成条件とする。

Terraform / Ansible / GitHub Actions CDや新規プロダクト機能は、明示的なIssueがない限りv1.0.0へ追加しない。

## Current Tech Stack

### Frontend

- React 19
- TypeScript 6
- Vite 8
- Tailwind CSS 4
- lucide-react
- Fetch API
- React標準のstate / effect

### Backend

- Python 3.11
- Django 5.2
- Django REST Framework 3.16
- PostgreSQL 15
- Gunicorn

### Runtime / Operations

- Docker Compose
- Caddy
- AWS EC2
- Amazon S3
- Amazon CloudWatch
- Bitwarden
- GitHub Actions CI

API prefix: `/api/v1/`

## Not Currently Adopted

以下は現時点のRicettaでは導入していない。将来候補であり、明示的なIssue・設計判断なしに追加しない。

- TanStack Query
- React Hook Form
- Zod
- shadcn/ui
- Redis
- Celery
- Terraform
- Ansible
- GitHub Actions CD
- RDS
- Google OAuth
- Google Sheets integration

新しいライブラリ、サービス、インフラ構成を追加する場合は、既存実装で解決できない理由と運用コストを確認すること。

## Source of Truth

詳細仕様をAGENTS.mdへ重複させない。以下を正本として参照する。

| 情報 | 正本 |
| --- | --- |
| プロジェクト概要 / Public Demo | `README.md` |
| Documentation index | `docs/README.md` |
| Product concept | `docs/product/concept.md` |
| MVP requirements | `docs/product/mvp-requirements.md` |
| 画面仕様 | `docs/product/screens.md` |
| 共通UI原則 | `docs/product/ui-guidelines.md` |
| API設計 | `docs/technical/api-design.md` |
| Data model | `docs/technical/data-model.md` |
| Deploy / Backup / Restore / Monitoring / Secrets | `docs/deploy/` |
| 長期的な設計・技術判断 | `docs/decisions/` |
| 今後の作業 / 課題 / Backlog | GitHub Issues |
| Release scope | GitHub Milestones |
| 変更内容 / 理由 / Verification | GitHub Pull Requests |
| 公開リリース | GitHub Releases |

ドキュメント間に矛盾を見つけた場合、推測で複数箇所を書き換えず、実装と正本を確認して責務を一つに寄せる。

## Required Development Flow

原則として以下の順序で作業する。

```text
AGENTS.md
  ↓
対象Issue
  ↓
関連docs / 現在の実装
  ↓
専用branch
  ↓
実装 / ドキュメント更新
  ↓
Verification
  ↓
Pull Request
  ↓
CI / Review
  ↓
merge
```

- Issueにない大きな機能追加・技術導入・設計変更を勝手に行わない。
- 1つのIssueでは、そのIssueの目的に必要な変更へスコープを絞る。
- `main`へ直接変更せず、原則としてIssue単位のbranchを使う。
- unrelated refactorを混ぜない。
- PR本文には変更内容、理由、実際に行ったVerificationを記録する。
- 実行していないテストを「実行済み」と記載しない。
- 長期的な判断が変わる場合は `docs/decisions/` の追加・Supersededを検討する。

## Critical Security Rules

### Secrets

- secret実値をrepositoryへcommitしない。
- `.env` / `.env.prod` をGit管理しない。
- secret実値をREADME、docs、Issue、PRへ記載しない。
- production secretの正本はBitwardenとする。
- GitHub docsにはsecret名、用途、配置場所、更新・復旧手順だけを記録する。
- AWSサービスへのEC2アクセスはIAM Roleを優先し、固定AWS access keyを新規追加しない。
- secretやcredentialをログ・エラーメッセージへ出力しない。

### Authentication / CSRF

- 現在の認証方式はDjango Session Authentication。
- state-changing requestではCSRF保護を維持する。
- 認証方式を明示的なIssueなしに変更しない。
- frontendだけで認証・認可を成立させない。
- production security設定を緩和する変更は、理由と影響を確認する。

### Authorization / Shop Scope

RicettaではShop Scopeを最重要のデータ境界として扱う。

- frontendから送信された `shop_id` を認可判断に使用しない。
- current ShopはログインユーザーとMembershipからbackend側で決定する。
- shop-scoped QuerySetはcurrent Shopでfilterする。
- shop-scoped modelの `shop_id` をwritable fieldとして公開しない。
- create時のShopはserver側で設定する。
- 他Shopのデータをread / update / deleteできないことを維持する。
- 新しいshop-scoped modelやendpointを追加する場合はcross-shop accessを防ぐテストを追加する。

## Architecture Responsibility

### Frontend

Frontendの責務:

- UI rendering
- Form interaction
- UXのためのclient-side validation
- API calling
- loading / empty / error states
- 一時的な画面state

Frontendは最終的なauthorization、Shop Scope、永続的なbusiness ruleを決定しない。

現在はFetch APIとReact標準機能を中心に実装している。TanStack Queryやform libraryを前提に既存コードを書き換えない。

### Backend

Backendの責務:

- Authentication
- Authorization
- Shop Scope enforcement
- Data validation
- Persistent business rules
- Cost calculation
- API response shape
- Database writes

frontend inputは常にuntrustedとして扱い、frontendでvalidation済みでもserver側で再検証する。

nested writeなど複数の関連データを一括更新する処理では、部分更新による不整合を避けるためtransaction boundaryを維持する。

### Database

Databaseの責務:

- Persistence
- Relational integrity
- Migrationで管理されるschema

重要な整合性を守れる場合はdatabase constraintを使う。ただしcurrent Shopのようなrequest-aware ruleはbackendで保証する。

## API Rules

- Business APIは `/api/v1/` 配下とする。
- 認証が必要なAPIでは既存のSession Authentication / permission方針を維持する。
- validation errorはfrontendが表示できる形で返す。
- raw stack traceや内部実装情報をresponseへ出さない。
- cross-shop resourceは存在を隠す必要がある場合404を優先する。
- API response shapeを変更した場合は `docs/technical/api-design.md` を更新する。
- Data modelを変更した場合はmigrationと `docs/technical/data-model.md` の更新要否を確認する。

## Product / UI Rules

AGENTS.mdでは個別画面仕様を固定しない。最新仕様は `docs/product/screens.md` と `docs/product/ui-guidelines.md` を参照する。

共通原則:

- 厨房で読みやすく、操作しやすいUIを優先する。
- smartphone / tablet landscape / PCを考慮する。
- user-facing labelは原則日本語。
- 過剰なinteractionや装飾を避ける。
- cost calculationの最終結果はbackendで計算する。
- Recipeの材料情報と管理用の原価情報を不用意に混在させない。

## Documentation Rules

実装変更時は、その情報の正本だけを必要に応じて更新する。

| Change | Update candidate |
| --- | --- |
| Product scope | `docs/product/mvp-requirements.md` |
| Screen behavior | `docs/product/screens.md` |
| Shared UI principle | `docs/product/ui-guidelines.md` |
| API | `docs/technical/api-design.md` |
| Data model | `docs/technical/data-model.md` |
| Deploy / Recovery / Operations | `docs/deploy/` |
| Durable design decision | `docs/decisions/` |
| Project overview / entry point | `README.md` |

`docs/handoff/latest.md` を作業ごとに更新する旧運用は採用しない。

短期的な作業文脈はIssueとPRで管理し、長期的な判断はDecision docsへ残す。既存 `docs/handoff/` の整理・廃止判断はDocumentation cleanup Issueで扱う。

## Coding Guidelines

### General

- 現在のIssue scopeを優先する。
- clear implementationをclever implementationより優先する。
- premature abstractionを避ける。
- 大規模なunrelated refactorを行わない。
- directory構成を理由なく変更しない。
- 既存の命名・設計パターンを確認してから新しいpatternを追加する。
- dependencyを追加する前に標準機能・既存dependencyで解決できないか確認する。

### Frontend

- TypeScriptを使用する。
- 現在のReact / Fetch APIベースの実装と整合させる。
- componentは読みやすい責務に保つ。
- client-side validationはUX補助であり、backend validationを正本とする。
- API-backed screenではloading / empty / error stateを考慮する。
- save失敗時に可能な限り入力内容を失わない。
- 未導入libraryをIssueなしに追加しない。

### Backend

- Django + DRF + PostgreSQLの現在構成を維持する。
- serializer等でserver-side validationを行う。
- QuerySetのShop Scopeを維持する。
- cost calculationはbackend側を正本とする。
- frontend inputを信用しない。
- shop-scoped modelの `shop_id` をwritableにしない。
- authentication strategyを明示的なIssueなしに変更しない。
- 複数modelを更新する処理ではatomicityの必要性を確認する。

## Verification

変更内容に応じて必要なVerificationを実施する。

Backendの基本確認:

```bash
docker compose exec backend python manage.py check
docker compose exec backend python manage.py makemigrations --check --dry-run
docker compose exec backend python manage.py test
```

Frontendの基本確認:

```bash
cd frontend
npm run lint
npm run build
```

Documentation-only変更では、少なくとも以下を確認する。

- Markdownの内容とリンク先
- 現在実装との矛盾
- secret実値を含んでいないこと
- `git diff --check`

実行環境がなくVerificationを実施できない場合は、PRに未実施理由を明記する。

## Before Finishing a Task

- 対象IssueのAcceptance Criteriaを確認する。
- unrelated changeが混ざっていないか確認する。
- 必要な正本docsが更新されているか確認する。
- secret / credential / private dataが差分に含まれていないか確認する。
- 実際に行ったVerificationをPRへ記載する。
- 新しいIssueやDecisionが必要な未解決事項を、作業中に勝手に実装して解消しない。
