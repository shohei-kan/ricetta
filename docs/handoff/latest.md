# Ricetta Handoff Latest

## Date

2026-05-05

## Project

Ricetta

## Status

Ready for Phase 4 Recipe API

## Summary

Ingredient APIまで完了し、次はRecipe / RecipeIngredient / RecipeStep APIを実装する状態。

## Current Goal

Recipe / RecipeIngredient / RecipeStep を実装し、IngredientとUnitを使ったレシピ管理と `cost_summary` の土台を作る。

## Current State

- Scaffold完了
- Docker / CI修正済み
- Auth / Shop Scope実装済み
- Category / Unit実装済み
- Ingredient API実装済み
- backend tests pass
- frontend build / lint pass
- handoff archive 方針をWebアプリ開発テンプレに合わせて整理済み

## What Was Done

- `docs/handoff/latest.md` を次フェーズ向けの現在地に整理
- `docs/handoff/archive/` を内容単位のarchive構成に整理
- `docs/handoff/archive/index.md` を追加
- `docs/handoff/archive/backend-foundation.md` にIngredient APIまでのbackend土台handoffを要約追記
- `AGENTS.md` にhandoff archive運用ルールを追記
- `docs/decisions/0005-documentation-structure.md` を追加

## Key Decisions

- Documentation decisions are stored in `docs/decisions/`.
- Handoff archive files are grouped by broad topic, not by every task.
- `shop_id` はfrontendから信用しない。
- Ingredientは現在Shopでスコープ済み。
- IngredientのUnit指定は標準Unit + 現在Shop Unitのみ。
- Recipe詳細では材料欄に原価情報を混ぜない。
- 原価情報は `cost_summary` に集約する。

## Key Files

- `backend/api/models.py`
- `backend/api/serializers.py`
- `backend/api/views.py`
- `backend/api/urls.py`
- `docs/api/api-design.md`
- `docs/data/data-model.md`
- `docs/handoff/archive/backend-foundation.md`
- `docs/handoff/archive/index.md`
- `docs/decisions/0005-documentation-structure.md`
- `AGENTS.md`

## Verification

直近のIngredient実装後に以下を確認済み。

```bash
docker compose run --rm -e POSTGRES_HOST= backend python manage.py check
docker compose run --rm -e POSTGRES_HOST= backend python manage.py makemigrations --check --dry-run
docker compose run --rm -e POSTGRES_HOST= backend python manage.py test

cd frontend
npm run build
npm run lint
```

Result:

- Backend check: pass
- Migration check: pass
- Backend tests: 29 tests pass
- Frontend build: pass
- Frontend lint: pass

今回の作業はドキュメント運用整理のみ。backend / frontend の検証は再実行していない。

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

1. Recipe / RecipeIngredient / RecipeStep モデルとAPIを実装する
2. RecipeIngredientでIngredientとUnitを現在Shopにスコープして選択できるようにする
3. Recipe単位の材料原価計算service/helperを実装する
4. Recipe detail response に `ingredients` / `steps` / `cost_summary` を含める
5. docs / tests / handoff を更新する

## Open Questions

- Session Auth運用時のCSRF取得APIをfrontend実装時に追加するか
- Staffの原価情報閲覧制限をどのPhaseで入れるか
- 標準Unitの追加・変更をdata migrationで固定するか、seed command運用に寄せるか
- `unit_cost_label` の丸めを将来どこまで厳密にするか
- Ingredientの仕入価格履歴をどのPhaseで扱うか

## Notes for Next Agent

- `get_current_shop(user)` をRecipe / Ingredient / PrepTask queryset filteringで使う。
- Recipe作成時も `shop_id` をserializerで受け取らず、server側で設定する。
- RecipeIngredientで選べるIngredientは現在ShopのIngredientのみ。
- RecipeIngredientで選べるUnitは標準Unit + 現在Shop Unitのみ。
- 材料欄と原価情報は分ける。
- Recipe全体の原価は `cost_summary` に集約する。

## Suggested Commit Message

```text
docs(handoff): align archive workflow with webapp template
```
