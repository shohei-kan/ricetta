# Ricetta Handoff Latest

## Date

2026-05-04

## Project

Ricetta

## Status

Backend Foundation / Auth + Shop Scope implemented

## Summary

RicettaのSaaS化前提となる店舗スコープの土台を実装した。Django標準User、Shop、Membership、Category、Unit、初期データ投入、Auth API、Shop API、Category API、Unit API、スコープ用helper、テストを追加した。

## Current Goal

Recipe / Ingredient / PrepTask を作る前に、ログイン中ユーザーのMembershipから現在Shopを特定し、店舗ごとにデータを分離できるbackend foundationを固める。

## What Was Done

- Django標準Userを採用
- メールログインは `username=email` として扱う方針にした
- MVP認証方式を Django Session Auth + DRF Basic Auth にした
- `Shop` モデルを追加
- `Membership` モデルを追加
- `Category` モデルを追加
- `Unit` モデルを追加
- `get_current_membership(user)` / `get_current_shop(user)` を追加
- `seed_initial_data` management command を追加
- Auth APIを追加
- Shop APIを追加
- Category APIを追加
- Unit APIを追加
- Category作成時に現在Shopを自動設定
- Category削除は `is_active=false` の論理削除
- Unit一覧は標準Unit（`shop=null`）+ 現在ShopのUnitを返す
- 標準Unitは編集・削除不可にした
- Auth / Shop scope / Category / Unit のテストを追加
- Tailwind CSS v4に合わせて frontend PostCSS 設定を修正し、CI buildを通した
- README / API docs / data model docs を更新

## Key Decisions

- API prefix: `/api/v1/`
- User: Django標準User
- Login identifier: email
- Implementation detail: `User.username` and `User.email` both store the email address
- Auth: Django Session Auth + DRF Basic Auth
- JWTはMVPで必要になってから検討
- フロントから送られた `shop_id` は信用しない
- 現在Shopは有効なMembershipからサーバー側で特定する
- MVPでは複数Membershipがあっても最初のactive Membershipを使う
- Stripe / billing fields are not added yet

## Seed Command

```bash
cd backend
python manage.py migrate
python manage.py seed_initial_data
```

作成される開発用データ:

```text
email: owner@example.com
password: password
shop: 〇〇食堂
role: owner
```

このアカウントとShopはローカル開発用。本番データとして使わない。

## API Added

```text
POST /api/v1/auth/login/
POST /api/v1/auth/logout/
GET  /api/v1/auth/me/
GET  /api/v1/shop/me/
PATCH /api/v1/shop/me/
GET  /api/v1/categories/
POST /api/v1/categories/
PATCH /api/v1/categories/{id}/
DELETE /api/v1/categories/{id}/
GET  /api/v1/units/
POST /api/v1/units/
PATCH /api/v1/units/{id}/
DELETE /api/v1/units/{id}/
```

## Key Files

- `backend/api/models.py`
- `backend/api/serializers.py`
- `backend/api/views.py`
- `backend/api/urls.py`
- `backend/api/shop_scope.py`
- `backend/api/seed_data.py`
- `backend/api/management/commands/seed_initial_data.py`
- `backend/api/migrations/0001_initial.py`
- `backend/api/tests.py`
- `backend/ricetta/settings.py`
- `README.md`
- `docs/api/api-design.md`
- `docs/data/data-model.md`
- `frontend/postcss.config.js`
- `frontend/package.json`
- `frontend/package-lock.json`

## Verification

実行済み:

```bash
cd backend
python3 manage.py check
python3 manage.py makemigrations --check --dry-run
python3 manage.py test
python3 manage.py migrate
python3 manage.py seed_initial_data

cd frontend
npm run build
npm run lint
```

結果:

- Backend check: pass
- Migration check: pass
- Backend tests: 12 tests pass
- Seed command: pass
- Frontend build: pass
- Frontend lint: pass

## Current Product Scope

MVPでは以下を対象とする。

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

## Out of Scope for MVP

MVPでは以下は対象外。

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
- 本格的な仕込みログ
- 使用期限・残量アラート

## Next Recommended Tasks

1. Ingredient モデルとAPIを実装する
2. Ingredient cost mode のバリデーションを追加する
3. Unitを使った簡易換算の土台を作る
4. Recipe / RecipeIngredient / RecipeStep モデルとAPIを実装する
5. Frontend login screen と session状態取得を実装する

## Open Questions

- Session Auth運用時のCSRF取得APIをfrontend実装時に追加するか
- Staffの原価情報閲覧制限をどのPhaseで入れるか
- 標準Unitの追加・変更をdata migrationで固定するか、seed command運用に寄せるか
- `decisions/` と `docs/decisions/` の配置をどちらに統一するか

## Notes for Next Agent

- `get_current_shop(user)` を今後のRecipe / Ingredient / PrepTask queryset filteringで使う。
- Category / Unit 作成時は `shop_id` をserializerで受け取らず、server側で設定する方針を継続する。
- Unitの標準単位は `shop=None`。店舗独自Unitだけ編集・削除できる。
- frontend buildはTailwind v4対応として `@tailwindcss/postcss` を使う構成に変更済み。

## Suggested Commit Message

```text
feat(api): add auth and shop-scoped foundation
```
