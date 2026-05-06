# Ricetta Handoff Latest

## Date

2026-05-06

## Project

Ricetta

## Status

Phase 9 Frontend Recipe List / Detail implemented

## Summary

Recipe List / Detail画面まで実装済み。`/recipes` でRecipe APIの一覧を表示し、`/recipes/:id` でRecipe Detailを確認できる。Prep TodayのカードからRecipe Detailへ移動できる導線も入った。

## Current Goal

次はIngredient frontendまたはRecipe作成・編集frontendへ進み、台帳に登録・編集できる範囲を広げる。

## What Was Done

- `frontend/src/api/recipes.ts` を追加
- `GET /api/v1/recipes/` を呼ぶRecipe List API clientを追加
- `GET /api/v1/recipes/{id}/` を呼ぶRecipe Detail API clientを追加
- `/recipes` placeholderをRecipe List画面へ差し替え
- `/recipes/:id` の軽量History API routingを追加
- Recipe Listに検索欄、Recipeカード、loading / empty / errorを追加
- Recipeカードにレシピ名、カテゴリ、基準量、更新日を表示
- Recipe Detailに戻るボタンを追加
- Recipe Detailにレシピ名、カテゴリ、基準量、説明、材料、作り方、注意点、アレルゲン、原価情報を表示
- Recipe Detailでは材料欄と原価情報を分離
- 原価情報カードは `cost_summary` のみを使って表示
- Prep TodayのPrepTaskカードに「レシピを見る」ボタンを追加
- README / product screens / handoffを更新

## Key Decisions

- frontendから `shop_id` は送らない。
- Shop scopeと認可はbackendに任せ、Recipe画面はbackend responseを表示する。
- Recipe Detailの材料欄には材料名、使用量、単位、memoだけを表示する。
- 材料ごとの原価、単価、仕入情報、換算情報は表示しない。
- Recipe全体の原価情報は `cost_summary` だけを使って専用カードに集約する。
- Recipe作成・編集・削除UIはまだ実装しない。
- `/recipes/:id` ではSidebar / bottom nav上の現在地は `レシピ` として扱う。
- Detailの戻るボタンは `window.history.back()` を基本にし、履歴がなければ `/recipes` に戻す。

## Key Files

- `frontend/src/api/recipes.ts`
- `frontend/src/pages/RecipeListPage.tsx`
- `frontend/src/pages/RecipeDetailPage.tsx`
- `frontend/src/pages/PrepTodayPage.tsx`
- `frontend/src/App.tsx`
- `README.md`
- `docs/product/screens.md`
- `docs/handoff/archive/frontend-implementation.md`

## Verification

直近の確認結果:

```bash
cd frontend
npm run build
npm run lint
```

Result:

- Frontend build: pass
- Frontend lint: pass

Backend codeは今回変更していない。

## Current Product Scope

MVP対象:

- Login / logout
- Shop account scope
- Dashboard summary
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

1. Ingredient list / detail frontendを実装する
2. Recipe作成・編集frontendの入力設計を固める
3. Recipe作成時にIngredient / Unit / Categoryを選べるUIを作る
4. Recipe DetailからEditへ進む導線を追加する
5. docs / tests / handoff を更新する

## Open Questions

- Staffの原価情報閲覧制限をどのPhaseで入れるか
- 標準Unitの追加・変更をdata migrationで固定するか、seed command運用に寄せるか
- `unit_cost_label` / `cost_summary` の丸めを将来どこまで厳密にするか
- Ingredientの仕入価格履歴をどのPhaseで扱うか
- RecipeIngredientの個別編集APIを将来追加するか、nested replacementのまま進めるか
- PrepTask deleteを将来論理削除へ変えるか
- Dashboardの `frequent_recipes` を将来どの期間で集計するか
- 本番frontendでSession Auth / CSRF / CORSの境界をどの構成にするか
- Prep Todayの日付切り替えUIをどのタイミングで入れるか
- Prep Action Modalを入れるか、カード内ボタンのまま進めるか
- Recipe作成・編集フォームでnested replacement方針をどう見せるか

## Notes for Next Agent

- Login開発用アカウントは `owner@example.com` / `password`。
- frontendは `shop_id` を送らず、backend responseを表示する。
- API clientは `frontend/src/api/api.ts`。
- Recipe API clientは `frontend/src/api/recipes.ts`。
- Recipe Listは `frontend/src/pages/RecipeListPage.tsx`。
- Recipe Detailは `frontend/src/pages/RecipeDetailPage.tsx`。
- Prep TodayからRecipe Detailへは `navigate(/recipes/:id)` で移動する。
- Recipe Detailの材料欄には原価情報を混ぜない。
- 原価情報カードは `cost_summary` のみを使う。

## Suggested Commit Message

```text
feat(frontend): add recipe list and detail views
```
