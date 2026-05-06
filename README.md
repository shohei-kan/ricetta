# Ricetta

小さな飲食店のための、レシピ台帳。

Ricetta（リチェッタ）は、個人経営のカフェ・バー・小料理屋・惣菜店など、小規模飲食店向けのレシピ管理SaaSです。

紙、Excel、ホワイトボード、口頭に散らばりがちなレシピ・原価・仕込み情報を、スマホ・タブレット・PCで確認できるようにします。

## Product Concept

Ricetta は、小さな飲食店のために以下を整理するアプリです。

- レシピ
- 材料
- 分量
- 作り方
- 原価
- 今日の仕込み

特に、厨房や仕込み場でホワイトボードに書いていた「今日の仕込み」を、レシピとつなげて管理できることを重視します。

基本の体験は以下です。

```text
レシピを登録する
↓
今日の仕込みに入れる
↓
必要量に応じた材料量を見る
↓
作業が終わったら完了にする
```

## Target Users

初期ターゲットは、個人経営・小規模飲食店です。

想定する店舗：

- カフェ
- バー
- 小料理屋
- ビストロ
- 惣菜店
- 弁当店
- ベーカリー
- キッチンカー
- 1〜3店舗程度の小規模飲食店

## MVP Scope

### In Scope

MVPでは、以下を実装対象にします。

- ログイン / ログアウト
- 店舗アカウント
- 店舗ごとのデータ分離
- レシピ一覧
- レシピ詳細
- レシピ作成 / 編集
- 材料作成 / 編集
- 材料ごとの原価計算モード
- レシピごとの材料原価計算
- 今日の仕込み一覧
- 仕込みタスクのステータス変更
- スマホ対応
- タブレット横向き対応

### Out of Scope

MVPでは以下を実装しません。

- Stripe決済
- Checkout
- Billing Portal
- POS連携
- 複数店舗管理
- 在庫自動減算
- 高度な発注管理
- AI自動分類
- 栄養計算
- HACCP帳票
- 高度な権限管理
- 店舗端末モード
- 本格的な仕込みログ / 使用期限 / 残量アラート

まずは、レシピ台帳と今日の仕込みボードを成立させることを優先します。

## Tech Stack

Frontend:

- React
- Vite
- TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Query
- React Hook Form
- Zod

Backend:

- Django 5.2 LTS
- Django REST Framework
- PostgreSQL

Development:

- Docker Compose

Future:

- Stripe Checkout / Billing

API prefix:

```text
/api/v1/
```

## Setup

### Prerequisites

- Docker
- Docker Compose

### Quick Start

1. Clone the repository
2. Copy `.env.example` to `.env`
3. Fill in `.env` values as needed
4. Run `docker compose up --build`
5. Open http://localhost:5173 for frontend
6. Backend API at http://localhost:8000

```bash
cp .env.example .env
docker compose up --build
```

Docker Compose reads the project root `.env`. The backend container also loads it with `env_file: .env`.

For backend-to-database connections inside Docker, use:

```text
POSTGRES_HOST=db
```

The Compose file also provides development defaults for PostgreSQL variables:

```text
POSTGRES_DB=ricetta
POSTGRES_USER=ricetta
POSTGRES_PASSWORD=ricetta
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

### Docker Verification

```bash
cp .env.example .env
docker compose down
docker compose up -d db
docker compose run --rm backend python -c "import os; print(os.getenv('POSTGRES_DB'), os.getenv('POSTGRES_HOST'))"
docker compose run --rm backend python -c "import django; print(django.get_version())"
docker compose run --rm backend python manage.py check
docker compose run --rm backend python manage.py makemigrations --check --dry-run
docker compose run --rm backend python manage.py test
```

Expected environment check output:

```text
ricetta db
```

### Health Check

```bash
curl http://localhost:8000/api/v1/health/
```

Response:

```json
{
  "status": "ok"
}
```

### Initial Development Data

Backend migration 後、開発用の標準単位・Shop・Ownerユーザー・Membership・初期カテゴリを作成できます。

```bash
cd backend
python manage.py migrate
python manage.py seed_initial_data
```

開発用ログイン:

```text
email: owner@example.com
password: password
shop: 〇〇食堂
```

このユーザーとShopはローカル開発用です。本番データとしては使いません。

### Auth / Shop Scope

MVPでは Django標準User を使います。メールログインは `username=email` として扱い、API認証は Django Session Auth + DRF Basic Auth で開始します。

主要データはサーバー側でログイン中ユーザーの有効な `Membership` から現在の `Shop` を特定します。フロントから送られた `shop_id` は信用しません。

主なAPI:

- `GET /api/v1/auth/csrf/`
- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/logout/`
- `GET /api/v1/auth/me/`
- `GET /api/v1/shop/me/`
- `PATCH /api/v1/shop/me/`
- `GET /api/v1/dashboard/`
- `GET /api/v1/categories/`
- `GET /api/v1/units/`
- `GET /api/v1/ingredients/`
- `POST /api/v1/ingredients/`
- `GET /api/v1/ingredients/{id}/`
- `PATCH /api/v1/ingredients/{id}/`
- `DELETE /api/v1/ingredients/{id}/`
- `GET /api/v1/recipes/`
- `POST /api/v1/recipes/`
- `GET /api/v1/recipes/{id}/`
- `PATCH /api/v1/recipes/{id}/`
- `DELETE /api/v1/recipes/{id}/`
- `GET /api/v1/prep-tasks/`
- `POST /api/v1/prep-tasks/`
- `GET /api/v1/prep-tasks/{id}/`
- `PATCH /api/v1/prep-tasks/{id}/`
- `DELETE /api/v1/prep-tasks/{id}/`
- `PATCH /api/v1/prep-tasks/{id}/status/`

Recipe API は現在Shopにスコープされます。作成時の `shop_id` は受け取らず、RecipeIngredientで指定できるIngredientは現在Shopの有効なIngredientのみ、Unitは標準Unitまたは現在ShopのUnitのみです。Recipe detailの材料欄には原価内訳を混ぜず、全体の原価情報は `cost_summary` に集約します。

PrepTask API も現在Shopにスコープされます。日付指定の一覧は `summary` と `tasks` を返し、`PATCH /api/v1/prep-tasks/{id}/status/` で `todo` / `doing` / `done` を更新できます。

Dashboard API は現在Shopの「今日の現場」情報として、仕込みsummary、次にやる仕込み、よく使うレシピ、ミニサマリー、空の `alerts` を返します。

FrontendはDjango Session Authを前提に、ログイン前に `GET /api/v1/auth/csrf/` でCSRF cookieを取得します。POST / PATCH / DELETEでは `credentials: "include"` と `X-CSRFToken` を送ります。`shop_id` はfrontendから送らず、backendがログイン中ユーザーのMembershipからShopを決定します。

## CI

GitHub Actions runs on PR and push to main.

- Backend: Django check, migration check, tests
- Frontend: Build and lint

## Main Features

## 1. Recipes

レシピを登録・管理します。

主な項目：

- レシピ名
- カテゴリ
- 説明
- 完成写真
- 基準量
- 基準単位
- 材料
- 作り方
- 注意点
- アレルゲン
- 販売価格
- 原価情報

レシピ詳細では、現場で見やすいことを優先します。

材料欄には原価情報を混ぜず、原価は専用の「原価情報」カードに集約します。

Frontendでは `/recipes` でレシピ一覧、`/recipes/{id}` でレシピ詳細、`/recipes/new` で新規作成、`/recipes/{id}/edit` で編集ができます。Recipe作成・編集ではCategory / Unit / IngredientをAPIから取得し、RecipeIngredient / RecipeStepをnested replacement方針で保存します。

## 2. Ingredients

材料を登録・管理します。

主な項目：

- 材料名
- 仕入先
- メモ
- 原価計算モード
- 仕入数量
- 仕入単位
- 仕入価格
- 使用単位
- 換算情報

Frontendでは `/ingredients` で材料一覧、`/ingredients/{id}` で材料詳細、`/ingredients/new` で新規作成、`/ingredients/{id}/edit` で編集ができます。Ingredient Detailは材料マスター管理画面なので、Recipe Detailとは違い、原価計算モード、仕入情報、換算情報、単価表示を表示します。

## 3. Ingredient Cost Mode

材料ごとに原価計算方法を選択できます。

```text
none
same_unit
conversion
```

### none

原価計算しない。

例：

- 水
- 塩少々
- 飾り

### same_unit

仕入単位のまま計算する。

例：

```text
卵 1個 = 30円
3個使用 → 90円
```

### conversion

使用単位に換算して計算する。

例：

```text
ホールトマト 1缶 = 180円
1缶 = 400g
200g使用 → 90円
```

MVPでは、1段階の簡易換算まで対応します。

対応例：

- kg ⇔ g
- L ⇔ ml
- 缶 → g
- 袋 → g
- 本 → ml

MVPでは、歩留まり・廃棄率・加熱後重量・複数段階換算は扱いません。

## 4. Today's Prep

ホワイトボードに書いていた「今日の仕込み」を置き換える機能です。

ステータス：

```text
todo
doing
done
```

画面表示：

```text
未着手
作業中
完了
```

操作はドラッグではなく、タップを基本にします。

仕込みカード例：

```text
トマトソース
3バッチ
```

FrontendではRecipe Detailの「今日の仕込みに追加」から、レシピの基準量・基準単位を初期値にしてPrepTaskを作成できます。保存成功後は `/prep` へ移動し、今日の仕込み一覧でstatus更新できます。

## 5. Dashboard

Dashboard は、単なるホーム画面ではなく「今日の現場」を確認する画面です。

表示例：

- 今日の仕込みサマリー
- 次にやること
- 期限注意
- よく使うレシピ
- クイックアクション
- ミニサマリー

Frontend foundationでは `/login`、`/dashboard`、`/prep`、`/recipes`、`/ingredients`、`/settings` のルートを用意しています。`/dashboard` はDashboard APIを表示し、`/prep` はPrepTask APIを使って今日の仕込み一覧とstatus更新を行います。`/recipes` はRecipe APIを使って一覧・詳細・作成・編集を扱います。`/ingredients` はIngredient APIを使って一覧・詳細・作成・編集を扱います。`/settings` はCategory / Unit APIを使ってレシピカテゴリと単位を管理します。

## 6. Settings

MVPのSettingsでは、レシピ台帳の運用に必要な最小設定として以下だけを扱います。

- レシピカテゴリ
- 単位

Categoryは現在Shopのカテゴリのみ作成・編集・削除できます。Unitは標準Unitと現在Shopの店舗独自Unitを表示し、店舗独自Unitのみ作成・編集・削除できます。標準Unitは編集・削除できません。

## UI Policy

Ricetta のUIは、以下を重視します。

- 小規模飲食店向け
- 清潔感
- 柔らかい業務アプリ感
- 厨房タブレットで見やすい
- 文字は大きめ
- タップしやすい
- 複雑な操作を避ける
- アイコンより文字で分かりやすくする

### Navigation

スマホ：

- 下部ナビ

タブレット横・PC：

- 120px程度の固定サイドバー
- テキストのみ
- カード型
- 常時表示

サイドバー項目：

```text
ホーム
仕込み
レシピ
材料
設定
```

## Documentation

主要ドキュメント：

```text
docs/planning/concept.md
docs/planning/mvp-requirements.md
docs/product/screens.md
docs/data/data-model.md
docs/api/api-design.md
AGENTS.md
README.md
```

### Planning

企画・要件定義系のドキュメントです。

```text
docs/planning/concept.md
docs/planning/mvp-requirements.md
```

### Product

画面・UI仕様系のドキュメントです。

```text
docs/product/screens.md
```

### Data

データモデル設計です。

```text
docs/data/data-model.md
```

### API

API設計です。

```text
docs/api/api-design.md
```

### AGENTS.md

Codex / AI agent 向けの作業ルールです。

## Development Setup

> このセクションは実装開始後に更新します。

想定コマンド例：

```bash
docker compose up -d
```

Backend:

```bash
cd backend
python manage.py migrate
python manage.py runserver
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

> このセクションは `.env.example` 作成時に更新します。

想定する環境変数：

```env
DJANGO_SECRET_KEY=
DJANGO_DEBUG=
DATABASE_URL=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
FRONTEND_ORIGIN=
```

将来的なStripe関連：

```env
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PRICE_ID_STARTER=
STRIPE_PRICE_ID_SHOP=
STRIPE_PRICE_ID_PRO=
```

StripeはMVPでは使用しません。

## API

API prefix:

```text
/api/v1/
```

MVP API:

- Auth
- Shop
- Dashboard
- Recipes
- Ingredients
- PrepTasks
- Categories
- Units

詳細は以下を参照します。

```text
docs/api/api-design.md
```

## Implementation Order

推奨実装順：

```text
1. Project scaffold
2. Docker Compose
3. Backend models
4. Auth / Shop scope
5. Categories / Units seed data
6. Ingredients
7. Recipes
8. Cost calculation
9. PrepTasks
10. Dashboard API
11. Frontend layout
12. Frontend screens
13. Form integration
14. UI polish
```

MVPでは、Stripe、複数店舗管理、在庫自動減算から始めないこと。

## Git / Commit

Conventional Commits を使います。

例：

```text
docs(planning): add Ricetta MVP requirements
feat(api): add ingredient cost mode
feat(frontend): add tablet sidebar layout
fix(cost): handle missing selling price
refactor(recipe): split recipe detail components
```

## Current Status

Initial planning phase.

Prepared documents:

- Concept
- MVP requirements
- Screens
- Data model
- API design
- AGENTS.md

Next recommended documents:

- docs/planning/mvp-roadmap.md
- docs/product/ui-guidelines.md
- docs/decisions/0001-mvp-scope.md
- docs/decisions/0002-shop-scope.md
- docs/decisions/0003-cost-calculation-mode.md
- docs/decisions/0004-tablet-navigation.md
