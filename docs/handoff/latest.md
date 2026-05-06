# Ricetta Handoff Latest

## Date

2026-05-06

## Project

Ricetta

## Status

Phase 10 Frontend Ingredient List / Detail implemented

## Summary

Ingredient List / Detail画面まで実装済み。`/ingredients` でIngredient APIの一覧を表示し、`/ingredients/:id` で材料詳細、原価計算モード、仕入情報、換算情報、単価表示を確認できる。

## Current Goal

次はRecipe作成・編集frontendまたはIngredient作成・編集frontendへ進み、台帳に登録・編集できる範囲を広げる。

## What Was Done

- `frontend/src/api/ingredients.ts` を追加
- `GET /api/v1/ingredients/` を呼ぶIngredient List API clientを追加
- `GET /api/v1/ingredients/{id}/` を呼ぶIngredient Detail API clientを追加
- `/ingredients` placeholderをIngredient List画面へ差し替え
- `/ingredients/:id` の軽量History API routingを追加
- Ingredient Listに検索欄、Ingredientカード、loading / empty / errorを追加
- Ingredientカードに材料名、仕入先、原価計算モード、`unit_cost_label` を表示
- Ingredient Detailに戻るボタンを追加
- Ingredient Detailに材料名、仕入先、memo、原価計算モード、仕入情報、使用単位、換算情報、`unit_cost_label` を表示
- `none` / `same_unit` / `conversion` ごとに表示内容を整理
- README / product screens / handoffを更新

## Key Decisions

- frontendから `shop_id` は送らない。
- Shop scopeと認可はbackendに任せ、Ingredient画面はbackend responseを表示する。
- Ingredient Detailは材料マスター管理寄りの画面なので、原価・換算情報を表示する。
- Recipe Detailとは役割を分け、Recipe Detailの材料欄には原価・仕入・換算情報を混ぜない。
- `cost_mode` は日本語ラベルと短い説明で表示する。
- `unit_cost_label` が `null` の場合は「計算なし」と表示する。
- Ingredient作成・編集・削除UIはまだ実装しない。
- `/ingredients/:id` ではSidebar / bottom nav上の現在地は `材料` として扱う。
- Detailの戻るボタンは `window.history.back()` を基本にし、履歴がなければ `/ingredients` に戻す。

## Key Files

- `frontend/src/api/ingredients.ts`
- `frontend/src/pages/IngredientListPage.tsx`
- `frontend/src/pages/IngredientDetailPage.tsx`
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

1. Recipe作成・編集frontendの入力設計を固める
2. Recipe作成時にIngredient / Unit / Categoryを選べるUIを作る
3. Ingredient作成・編集frontendを実装する
4. SettingsでCategory / Unitの管理画面を整える
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
- Ingredient作成・編集フォームでcost_modeごとの入力切り替えをどう設計するか
- Recipe作成・編集フォームでnested replacement方針をどう見せるか

## Notes for Next Agent

- Login開発用アカウントは `owner@example.com` / `password`。
- frontendは `shop_id` を送らず、backend responseを表示する。
- API clientは `frontend/src/api/api.ts`。
- Ingredient API clientは `frontend/src/api/ingredients.ts`。
- Ingredient Listは `frontend/src/pages/IngredientListPage.tsx`。
- Ingredient Detailは `frontend/src/pages/IngredientDetailPage.tsx`。
- Recipe Detailの材料欄には原価情報を混ぜない。
- Ingredient Detailでは原価計算モード、仕入情報、換算情報、単価表示を表示してよい。
- `unit_cost_label` がない材料は「計算なし」と表示している。

## Suggested Commit Message

```text
feat(frontend): add ingredient list and detail views
```
