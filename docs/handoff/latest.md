# Ricetta Handoff Latest

## Date

2026-05-05

## Project

Ricetta

## Status

Phase 4 Recipe API implemented

## Summary

Recipe / RecipeIngredient / RecipeStep APIまで実装済み。IngredientとUnitを使ったレシピ管理、shop scope validation、Recipe detailの `cost_summary` の土台が入った。

## Current Goal

次はPrepTask APIへ進み、Recipeを今日の仕込みボードに載せるためのbackend土台を作る。

## What Was Done

- `Recipe` / `RecipeIngredient` / `RecipeStep` モデルを追加
- Recipe CRUD APIを追加
- Recipe作成時に現在Shopをserver側で設定
- Recipe一覧・詳細・更新・削除を現在Shopにスコープ
- RecipeIngredientで現在ShopのIngredient、標準Unit + 現在Shop Unitのみ指定可能にした
- Recipe detail responseに `ingredients` / `steps` / `cost_summary` を追加
- `ingredients` には材料ごとの原価情報を含めず、原価情報を `cost_summary` に集約
- DELETEは `is_active=false` の論理削除
- PATCHで `ingredients` / `steps` が送られた場合は置き換え更新する方針にした
- Recipe関連テストを追加
- API docs / data model / READMEを更新

## Key Decisions

- `shop_id` はfrontendから信用しない。
- Recipe作成時のShopは `get_current_shop(user)` から設定する。
- RecipeIngredientで選べるIngredientは現在Shopの `is_active=true` のIngredientのみ。
- Recipe / RecipeIngredientで選べるUnitは標準Unit + 現在Shop Unitのみ。
- Recipeで選べるCategoryは現在ShopのCategoryのみ。
- 原価計算対象Ingredientでは、RecipeIngredientのUnitはIngredientの `usage_unit` と一致させる。
- Nested updateはMVPでは「送られた `ingredients` / `steps` を全置き換え」。
- Recipe detailでは材料欄と原価情報を分離し、原価情報は `cost_summary` に集約する。
- `docs/decisions/` に長期的な判断を集約する。

## Key Files

- `backend/api/models.py`
- `backend/api/serializers.py`
- `backend/api/views.py`
- `backend/api/urls.py`
- `backend/api/costing.py`
- `backend/api/tests.py`
- `backend/api/migrations/0003_recipe_recipeingredient_recipestep_and_more.py`
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

1. PrepTaskモデルとAPIを実装する
2. 今日の仕込み一覧を現在Shopでスコープする
3. PrepTaskでRecipeとUnitを現在Shopにスコープして選択できるようにする
4. Prep status (`todo` / `doing` / `done`) 更新APIを追加する
5. docs / tests / handoff を更新する

## Open Questions

- Session Auth運用時のCSRF取得APIをfrontend実装時に追加するか
- Staffの原価情報閲覧制限をどのPhaseで入れるか
- 標準Unitの追加・変更をdata migrationで固定するか、seed command運用に寄せるか
- `unit_cost_label` / `cost_summary` の丸めを将来どこまで厳密にするか
- Ingredientの仕入価格履歴をどのPhaseで扱うか
- RecipeIngredientの個別編集APIを将来追加するか、nested replacementのまま進めるか

## Notes for Next Agent

- `get_current_shop(user)` をPrepTask queryset filteringでも使う。
- PrepTask作成時も `shop_id` をserializerで受け取らず、server側で設定する。
- PrepTaskで選べるRecipeは現在Shopの `is_active=true` のRecipeのみ。
- PrepTaskで選べるUnitは標準Unit + 現在Shop Unitのみ。
- Recipe detailの材料欄には原価情報を混ぜない方針を維持する。
- Recipe全体の原価は `backend/api/costing.py` の `calculate_recipe_cost_summary()` で計算している。

## Suggested Commit Message

```text
feat(api): add shop-scoped recipe management
```
