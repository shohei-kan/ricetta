# Ricetta Handoff Latest

## Date

2026-05-05

## Project

Ricetta

## Status

Phase 5 PrepTask API implemented

## Summary

PrepTask APIまで実装済み。Recipeを今日の仕込みボードへ載せるためのbackend土台として、日付別一覧、status summary、status更新API、Recipe / Unit scope validationが入った。

## Current Goal

次はDashboard APIまたはfrontend layoutへ進み、今日の仕込みとレシピ台帳を画面から使える状態に近づける。

## What Was Done

- `PrepTask` モデルを追加
- PrepTask CRUD APIを追加
- `PATCH /api/v1/prep-tasks/{id}/status/` を追加
- PrepTask作成時に現在Shopをserver側で設定
- PrepTask一覧・詳細・更新・削除を現在Shopにスコープ
- PrepTaskで現在ShopのRecipe、標準Unit + 現在Shop Unitのみ指定可能にした
- `GET /api/v1/prep-tasks/?date=YYYY-MM-DD` で `summary` と `tasks` を返す形式にした
- date未指定時はサーバー側のtodayを使う
- `done` では `completed_at=now`、`done` 以外へ戻すと `completed_at=null`
- PrepTask関連テストを追加
- API docs / data model / READMEを更新

## Key Decisions

- `shop_id` はfrontendから信用しない。
- PrepTask作成時のShopは `get_current_shop(user)` から設定する。
- PrepTaskで選べるRecipeは現在Shopの `is_active=true` のRecipeのみ。
- PrepTaskで選べるUnitは標準Unit + 現在Shop Unitのみ。
- PrepTask一覧はMVPでは `sort_order, id` 順で返す。
- PrepTask deleteはMVPでは物理削除。
- Status更新は通常PATCHでも可能だが、タップ操作用に専用 `status/` APIを用意する。
- `docs/decisions/` に長期的な判断を集約する。

## Key Files

- `backend/api/models.py`
- `backend/api/serializers.py`
- `backend/api/views.py`
- `backend/api/urls.py`
- `backend/api/tests.py`
- `backend/api/migrations/0004_preptask.py`
- `docs/api/api-design.md`
- `docs/data/data-model.md`
- `docs/handoff/archive/backend-foundation.md`

## Verification

直近の確認結果:

```bash
docker compose run --rm backend python manage.py check
docker compose run --rm backend python manage.py makemigrations --check --dry-run
docker compose run --rm backend python manage.py test

cd frontend
npm run build
npm run lint
```

Result:

- Backend check: pass
- Migration check: pass
- Backend tests: pass
- Frontend build: pass
- Frontend lint: pass

## Current Product Scope

MVP対象:

- Login / logout
- Shop account scope
- Recipe list/detail/create/edit
- Ingredient create/edit
- Ingredient cost mode
- Basic food cost calculation
- Today's prep list
- Prep task status update
- Smartphone layout
- Tablet landscape layout

## Out of Scope for MVP

- Stripe payment / Checkout / Billing Portal
- POS integration
- Multi-shop management UI
- Automatic inventory deduction
- Advanced ordering
- AI auto-classification
- Nutrition calculation
- HACCP reports
- Advanced role management
- Shop device mode
- Full prep inventory / expiry alerts

## Next Recommended Tasks

1. Dashboard APIを実装する
2. 今日の仕込みsummaryと次にやるPrepTaskを返せるようにする
3. Frontend layoutの土台を作る
4. Login / Dashboard / Prep Today の画面導線を作る
5. docs / tests / handoff を更新する

## Open Questions

- Session Auth運用時のCSRF取得APIをfrontend実装時に追加するか
- Staffの原価情報閲覧制限をどのPhaseで入れるか
- 標準Unitの追加・変更をdata migrationで固定するか、seed command運用に寄せるか
- `unit_cost_label` / `cost_summary` の丸めを将来どこまで厳密にするか
- Ingredientの仕入価格履歴をどのPhaseで扱うか
- RecipeIngredientの個別編集APIを将来追加するか、nested replacementのまま進めるか
- PrepTask deleteを将来論理削除へ変えるか

## Notes for Next Agent

- `get_current_shop(user)` をDashboard queryset filteringでも使う。
- Dashboardで使うPrepTaskは現在Shop + 対象日で絞る。
- PrepTask APIの一覧は `summary` と `tasks` を返すため、通常のDRF list配列ではない。
- PrepTask status更新は `PATCH /api/v1/prep-tasks/{id}/status/` を使う。
- `done` から `todo` / `doing` に戻すと `completed_at` はnullになる。
- Recipe detailの材料欄には原価情報を混ぜない方針を維持する。

## Suggested Commit Message

```text
feat(api): add shop-scoped prep task management
```
