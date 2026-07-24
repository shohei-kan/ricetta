# Ricetta

小さな飲食店のための、レシピ台帳。

<p align="center">
  <img src="frontend/src/assets/brand/ricetta_logo_full.png" alt="Ricetta" width="520">
</p>

## Portfolio Summary

Ricetta（リチェッタ）は、飲食店運営経験をもとに企画・設計・実装した、小規模飲食店向けのレシピ管理Webアプリです。

React / TypeScriptによるフロントエンドと、Django REST Framework / PostgreSQLによるバックエンドを分離し、REST APIを通じてレシピ・材料・原価・仕込みタスクを管理します。

特にバックエンドでは、以下を重視して実装しました。

- Membershipを利用した店舗単位のデータ分離
- クライアントから送られる `shop_id` を信用しないShopスコープ
- Django Session認証とCSRF保護
- 材料ごとの単位換算を含む原価計算
- Recipe / RecipeIngredient / RecipeStepのnested write
- owner / staffの権限制御
- Django・frontend双方を検証するCI

将来的なSaaS化を想定していますが、現在はレシピ台帳と今日の仕込みボードを成立させるMVPとして開発しています。

## Background

飲食店の現場では、レシピ、仕込み量、材料原価、作業手順が紙・Excel・ホワイトボード・口頭説明に分散しやすく、情報が属人化しがちです。

特に小規模店舗では、大規模な業務システムを導入するほどではない一方、味の再現性や引き継ぎ、日々の仕込み、原価の把握には継続的な情報管理が必要です。

Ricettaでは飲食店運営で感じたこの課題に対して、まず以下の業務フローを一つのアプリにつなげることを目指しました。

```text
レシピを登録する
↓
今日の仕込みに入れる
↓
必要量に応じた材料量を見る
↓
作業が終わったら完了にする
```

## Product Concept

Ricettaが整理する情報は以下です。

- レシピ、分量、作り方
- 材料、仕入単位、使用単位
- 材料原価とレシピ原価
- 今日の仕込み量と進捗
- 店舗内のカテゴリと単位

対象は、カフェ、バー、小料理屋、ビストロ、惣菜店、弁当店、ベーカリー、キッチンカーなどの小規模飲食店です。

UIは「紙より探しやすく、Excelより読みやすく、大規模業務システムより軽い」ことを意識し、スマホ・タブレット横向き・PCに対応しています。

## Screenshots

| Dashboard | Today's Prep |
|---|---|
| ![Dashboard screen](frontend/src/assets/images/screenshots/dashboard.png) | ![Today's Prep screen](frontend/src/assets/images/screenshots/prep-today.png) |

| Recipe Detail | Cost Summary |
|---|---|
| ![Recipe Detail screen](frontend/src/assets/images/screenshots/recipe-detail.png) | ![Cost Summary screen](frontend/src/assets/images/screenshots/cost-summary.png) |

| Account |
|---|
| ![Account screen](frontend/src/assets/images/screenshots/account.png) |

## Main Features

### Recipe management

- レシピ一覧、検索、詳細、作成、編集
- 基準量、材料行、作り方、注意点、アレルゲンの管理
- 材料情報と管理用の原価情報を分けた詳細表示
- RecipeIngredient / RecipeStepを含むnested write

### Ingredient and cost management

- 材料一覧、検索、詳細、作成、編集
- 仕入先、仕入数量、仕入価格、使用単位の管理
- `none` / `same_unit` / `conversion` の原価計算モード
- kgとg、Lとml、缶からgなどの1段階換算
- レシピ全体の材料原価、原価率、粗利の計算

### Today's Prep

- レシピ詳細から仕込みタスクを作成
- `todo` / `doing` / `done` の3状態をタップで更新
- 日付、予定数量、予定単位、メモの管理
- 当日の状態別件数とタスク一覧の表示

### Dashboard

- 今日の仕込みサマリー
- 次に行う仕込み
- よく使うレシピ
- レシピ・材料・仕込み件数

### Account and settings

- 店舗情報とログイン中ユーザー情報の表示
- ownerによる店舗名・業態・メモの編集
- owner / staffによる自分の店舗内表示名の編集
- カテゴリと店舗独自単位の管理
- Accountページからのログアウト

### Responsive UI

- スマホでは下部ナビゲーション
- タブレット横向き・PCでは固定サイドバー
- 厨房でも読みやすい文字サイズとタップ領域
- 空状態、通信中、エラー状態の表示

## MVP Scope

### Implemented

- Login / logout
- Shop-scoped account and data access
- Recipe / Ingredient / PrepTask CRUD
- Ingredient cost modes and recipe cost summary
- Dashboard
- Category / Unit settings
- Account表示、表示名更新、owner限定の店舗情報更新
- Smartphone / tablet landscape / PC layouts

### Not implemented

- Accountでのメールアドレス変更、パスワード変更
- 複数店舗切り替えUI
- Stripe、Checkout、Billing Portal
- POS連携、在庫自動減算、高度な発注管理
- 栄養計算、HACCP帳票
- 画像アップロード
- 詳細なstaff権限管理
- 本格的な仕込みログ、使用期限、残量アラート

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, TypeScript 6, Vite 8, Tailwind CSS 4 |
| Backend | Python 3.11, Django 5.2, Django REST Framework 3.16 |
| Database | PostgreSQL 15 |
| Authentication | Django Session Authentication, CSRF protection |
| Development | Docker Compose, Node.js 22 |
| CI | GitHub Actions |

現時点のfrontendはReact標準のstate / effectとFetch APIを中心に実装しています。TanStack Query、React Hook Form、Zod、shadcn/uiは未導入です。

## Why This Stack?

### React / TypeScript

一覧、詳細、入力フォーム、ステータス更新など、状態を持つ画面をコンポーネントとして分け、APIレスポンスとフォーム値を型で確認しながら実装するために採用しました。

### Tailwind CSS

スマホ・タブレット・PCのレイアウトを同じコンポーネント内で調整し、厨房向けの余白、文字サイズ、タップ領域を素早く検証するために採用しました。

### Django REST Framework

認証、Serializer validation、権限、QuerySetの店舗スコープをバックエンドへ集約し、Recipe、Ingredient、PrepTaskなどの業務データをREST APIとして扱うために採用しました。

### PostgreSQL

User、Membership、Shop、Recipe、Ingredient、Unit、PrepTaskなど、関係性と整合性が重要なデータを扱うために採用しました。

### Docker Compose

frontend、backend、databaseを同じ手順で起動し、ローカル環境とCIで利用するバージョン差を小さくするために採用しました。

## Architecture

```text
[Browser]
   |
   | React / TypeScript / Vite
   | /api proxy, Session Cookie, CSRF Token
   v
[Frontend Container :5173]
   |
   | REST API
   v
[Backend Container :8000]
   | Django REST Framework
   | Django ORM
   v
[PostgreSQL Container :5432]
```

Docker Composeでのホスト公開ポートは以下です。

| Service | Host | Container |
|---|---:|---:|
| Frontend | 5174 | 5173 |
| Backend | 8010 | 8000 |
| PostgreSQL | 5433 | 5432 |

frontendとbackendは分離し、画面表示・一時的なUI状態はfrontend、認証・権限・validation・原価計算・永続化はbackendが担当します。

## Backend Design Highlights

### Shop-scoped data access

Ricettaでは、店舗ごとにデータを分離するため、ログイン中ユーザーの有効なMembershipから現在のShopをサーバー側で決定します。

```text
request.user
→ active Membership
→ current Shop
→ QuerySetをshopでfilter
```

クライアントから送信された `shop_id` は信用せず、QuerySetの絞り込みと作成時のShop設定をAPI側で行います。別店舗のIDを指定されても、一覧・詳細・更新・削除からアクセスできないことをテストしています。

現在のMVPは1ユーザー1店舗運用を前提とし、有効なMembershipのID順先頭を現在店舗として使用します。複数店舗切り替えは未実装です。

### Session authentication and CSRF protection

frontendはDjango Session Authenticationを利用します。ログイン前に `GET /api/v1/auth/csrf/` でCSRF Cookieを取得し、POST / PATCH / PUT / DELETEでは `credentials: "include"` と `X-CSRFToken` を送信します。

ローカル開発ではViteの `http://localhost:5173` とDocker frontendの `http://localhost:5174` をtrusted originに設定しています。本番では環境変数から本番Originだけを指定する想定です。

### Role-based shop editing

Membershipには `owner` / `staff` のroleがあります。店舗情報の更新では、現在MembershipがownerであることをAPI側で確認し、staffからの更新には403を返します。表示名はowner / staffとも自分のMembershipだけを更新できます。

### Ingredient cost calculation modes

材料ごとに原価計算方法が異なるため、以下の3種類を用意しています。

| Mode | Behavior | Example |
|---|---|---|
| `none` | 原価計算に含めない | 水、飾り |
| `same_unit` | 仕入単位のまま単価を計算 | 卵1個30円 |
| `conversion` | 仕入単位から使用単位へ1段階換算 | 1缶400g、200g使用 |

最終的なレシピ原価はbackendで計算し、frontendは `cost_summary` を表示します。販売価格がない場合、原価率と粗利は `null` として扱います。

### Nested recipe update

Recipe作成・編集では、RecipeIngredient / RecipeStepをレシピ本体とまとめて受け取ります。

更新時は、リクエストに含まれた材料行・手順を置き換えるnested replacement方針です。Serializerで、現在ShopのCategory / Ingredientと、標準Unitまたは現在ShopのUnitだけを参照できるよう制御しています。

### Validation and logical deletion

- Serializerで数量、価格、単位、Shopスコープを再検証
- Recipe / Ingredient / Categoryは `is_active=false` による論理削除
- 標準Unitは編集・削除不可
- frontendからの入力を認可判断に使用しない

## Data Model Overview

```text
User
  | 1:N
  v
Membership ---- N:1 ----> Shop
                           | 1:N
                           +----> Category
                           +----> Ingredient ----> Unit
                           +----> Recipe
                           |        | 1:N
                           |        +----> RecipeIngredient ----> Ingredient
                           |        +----> RecipeStep
                           |
                           +----> PrepTask ----> Recipe / Unit
```

`Unit.shop` はnullableです。`shop=null` は全店舗で利用できる標準Unit、Shopが設定されたUnitは店舗独自Unitとして扱います。

詳細は [docs/technical/data-model.md](docs/technical/data-model.md) を参照してください。

## API Overview

API prefix:

```text
/api/v1/
```

Main resources:

- Auth / Account
- Shop
- Dashboard
- Recipes
- Ingredients
- PrepTasks
- Categories
- Units

Representative endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/auth/csrf/` | CSRF Cookie取得 |
| POST | `/api/v1/auth/login/` | ログイン |
| GET / PATCH | `/api/v1/auth/me/` | 現在ユーザー取得、表示名更新 |
| GET / PATCH | `/api/v1/shop/me/` | 現在店舗取得、ownerによる更新 |
| GET | `/api/v1/dashboard/` | 今日の現場サマリー |
| GET / POST | `/api/v1/recipes/` | レシピ一覧・作成 |
| GET / PATCH / DELETE | `/api/v1/recipes/{id}/` | レシピ詳細・更新・論理削除 |
| GET / POST | `/api/v1/ingredients/` | 材料一覧・作成 |
| GET / POST | `/api/v1/prep-tasks/` | 仕込み一覧・作成 |
| PATCH | `/api/v1/prep-tasks/{id}/status/` | 仕込みstatus更新 |

リクエスト・レスポンスとvalidation errorの詳細は [docs/technical/api-design.md](docs/technical/api-design.md) を参照してください。

## Setup

### Prerequisites

- Docker
- Docker Compose

### Quick Start

```bash
git clone <repository-url>
cd ricetta
cp .env.example .env
docker compose up --build -d
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_initial_data
```

起動後に以下へアクセスします。

- Frontend: http://localhost:5174
- Backend API: http://localhost:8010/api/v1/
- PostgreSQL（ホストツール用）: `localhost:5433`

開発用ログイン:

```text
email: owner@example.com
password: password
shop: 〇〇食堂
```

このアカウントはローカル開発専用です。

### Portfolio Demo Data

ポートフォリオ掲載用スクリーンショットやAWS公開デモ環境では、同じサンプルデータを再現できます。

```bash
docker compose exec backend python manage.py seed_portfolio_data
```

作成されるデモログイン:

```text
owner: owner@example.com / password
staff: staff@example.com / password
shop: 〇〇食堂
```

`seed_portfolio_data` は撮影・公開デモ用の開発データです。本番運用データとしては使いません。既存データが重複しにくいように冪等に作成し、カポナータをRecipe DetailとCost Summary確認用の主役レシピとして用意します。

### Local frontend development

backendとdatabaseをDockerで起動したまま、frontendだけホストで起動できます。

```bash
cd frontend
npm install
npm run dev
```

ローカルViteは http://localhost:5173 で起動し、APIを http://localhost:8010 へproxyします。

### Common commands

```bash
# Start
docker compose up -d

# Stop
docker compose down

# Backend checks
docker compose exec backend python manage.py check
docker compose exec backend python manage.py makemigrations --check --dry-run
docker compose exec backend python manage.py test

# Frontend checks
cd frontend
npm run lint
npm run build
```

## Environment Variables

主要な環境変数は `.env.example` に定義しています。

| Variable | Purpose | Development value |
|---|---|---|
| `DJANGO_SECRET_KEY` | Django secret key | 開発用ダミー値 |
| `DJANGO_DEBUG` | Debug mode | `True` |
| `DJANGO_ALLOWED_HOSTS` | 許可Host | `localhost,127.0.0.1,backend` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | unsafe methodを許可するOrigin | `http://localhost:5173,http://localhost:5174` |
| `POSTGRES_DB` | Database name | `ricetta` |
| `POSTGRES_USER` | Database user | `ricetta` |
| `POSTGRES_PASSWORD` | Database password | `ricetta` |
| `POSTGRES_HOST` | Docker内Database host | `db` |
| `POSTGRES_PORT` | Docker内Database port | `5432` |
| `POSTGRES_HOST_PORT` | Host公開Database port | `5433` |
| `FRONTEND_ORIGIN` | 開発frontend URL | `http://localhost:5174` |
| `BACKEND_ORIGIN` | 開発backend URL | `http://localhost:8010` |

localhostのtrusted originsは開発専用です。本番環境では `DJANGO_SECRET_KEY` を安全な値へ変更し、`DJANGO_ALLOWED_HOSTS` と `DJANGO_CSRF_TRUSTED_ORIGINS` に本番環境の値だけを設定します。

`.env` はコミットしません。

## Test / CI

GitHub Actionsはpull requestと `main` へのpushで実行されます。

### Backend

- Python 3.11
- PostgreSQL 15 service container
- `python manage.py check`
- `python manage.py makemigrations --check --dry-run`
- `python manage.py test`

テストでは、認証必須、他店舗データへのアクセス拒否、Recipe / Ingredient / PrepTask CRUD、原価計算モード、nested recipe write、Accountのowner / staff権限などを確認しています。

### Frontend

- Node.js 22
- `npm ci`
- `npm run build`
- `npm run lint`

frontendの自動UIテストは未導入です。

## Challenges and Learnings

### 業務フローをデータモデルへ落とし込むこと

飲食店では、レシピ・材料・仕込み内容が紙の上では一続きでも、システムでは責務と更新単位を分ける必要があります。

Recipe / Ingredient / PrepTask / Unit / Categoryを分け、RecipeIngredientを通じてレシピと材料を接続することで、現場での見やすさとデータ整合性の両立を考えました。

### 店舗スコープを認可として扱うこと

単に `shop_id` をAPIで受け取る実装では、別店舗のIDを指定される危険があります。

現在ユーザーのMembershipからShopを解決し、QuerySet・Serializer・作成処理の各層でスコープを守ることで、マルチテナントを想定したデータアクセスを学びました。

### 原価計算の単位変換

飲食店の材料は、仕入単位と使用単位が一致しないことがあります。たとえば缶で仕入れ、レシピではg単位で使用します。

MVPでは複雑な歩留まり計算まで広げず、1段階換算に限定することで、実用性と実装範囲のバランスを取りました。

### Session認証とCSRF

Session認証では、ログイン可否だけでなくunsafe methodのCSRF Cookie、header、trusted originまで揃える必要があります。

Vite proxyを使うローカル環境でもOrigin checkingを通せるよう、開発Originと本番Originを環境変数で分離しました。

## Documentation

- [Docs index](docs/README.md)
- [MVP requirements](docs/product/mvp-requirements.md)
- [MVP roadmap](docs/product/mvp-roadmap.md)
- [Screen specifications](docs/product/screens.md)
- [UI guidelines](docs/product/ui-guidelines.md)
- [Data model](docs/technical/data-model.md)
- [API design](docs/technical/api-design.md)
- [Architecture decisions](docs/decisions/)
- [Latest handoff](docs/handoff/latest.md)
- [Handoff archive](docs/handoff/archive/index.md)
- [Agent instructions](AGENTS.md)

## Current Status

MVPの主要なbackend APIとfrontend画面は実装済みです。

- Login / logout / Account Phase 1 + 2
- Shop scopeとowner限定店舗編集
- Recipe / Ingredient / PrepTask / Dashboard / Category / Unit
- 原価計算とnested recipe write
- スマホ・タブレット横向き・PCレイアウト
- Docker Compose開発環境とGitHub Actions CI

未デプロイのローカル開発段階です。最新の作業状況と確認事項は [docs/handoff/latest.md](docs/handoff/latest.md) を参照してください。

## Future Improvements

- AWS公開デモURLの追加
- スマホ幅スクリーンショットの追加
- Accountでのメールアドレス変更、パスワード変更
- 複数店舗切り替え
- staffの詳細な権限設計
- 画像アップロード
- frontendの自動テスト
- サーバー状態・フォーム管理ライブラリ導入の検討
- 本番デプロイとproduction settings
- Stripe Billing、POS、在庫連携の段階的な検討
