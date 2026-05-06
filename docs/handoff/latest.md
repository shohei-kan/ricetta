# Ricetta Handoff Latest

## Date

2026-05-06

## Project

Ricetta

## Status

Phase 11 Frontend Ingredient Create / Edit implemented

## Summary

Ingredient作成・編集画面まで実装済み。`/ingredients/new` で材料を新規作成し、`/ingredients/:id/edit` で既存材料を編集できる。`cost_mode` ごとの入力切り替え、Unit選択、最低限のfrontend validation、backend validation error表示が入った。

## Current Goal

次はRecipe作成・編集frontendへ進み、Ingredient / Unit / Categoryを選びながらレシピを登録・編集できる状態にする。

## What Was Done

- `frontend/src/api/ingredients.ts` に `createIngredient` / `updateIngredient` を追加
- `frontend/src/api/units.ts` を追加
- `GET /api/v1/units/` でUnit選択肢を取得
- `/ingredients/new` routeを追加
- `/ingredients/:id/edit` routeを追加
- `frontend/src/pages/IngredientFormPage.tsx` を追加
- Ingredient Listに「材料を追加」導線を追加
- Ingredient Detailに「編集」導線を追加
- 作成成功後は作成されたIngredient Detailへ遷移
- 編集成功後はIngredient Detailへ遷移
- `cost_mode=none` / `same_unit` / `conversion` ごとの入力切り替えを追加
- `same_unit` では仕入単位を選ぶと使用単位も同じ値に自動設定
- `conversion` では換算元単位を仕入単位、換算先単位を使用単位に自動設定
- name必須、数量・価格・Unit必須などの最低限frontend validationを追加
- backend validation errorをフォーム上に表示
- 保存失敗時に入力内容が消えないようにした
- README / product screens / handoffを更新

## Key Decisions

- frontendから `shop_id` は送らない。
- Shop scopeと認可はbackendに任せ、Ingredient作成・編集はbackend validationに従う。
- MVPではフォームを重くしすぎず、`cost_mode` ごとに必要な入力だけ表示する。
- `same_unit` は使用単位を手動変更させず、仕入単位と同じ値に固定する。
- `conversion` は換算元単位 / 換算先単位を手動入力させず、仕入単位 / 使用単位から自動設定する。
- 送信時、`none` では価格・単位・換算情報を `null` にして保存する。
- 送信時、`same_unit` では換算情報を `null` にして保存する。
- DRF validation errorはMVPでは汎用メッセージ + backend response文字列で表示する。
- Ingredient削除UI、Unit作成・編集UI、Recipe作成・編集UIはまだ実装しない。

## Key Files

- `frontend/src/api/ingredients.ts`
- `frontend/src/api/units.ts`
- `frontend/src/pages/IngredientFormPage.tsx`
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

1. Recipe作成・編集frontendを実装する
2. Recipe作成時にIngredient / Unit / Categoryを選べるUIを作る
3. RecipeIngredient / RecipeStepのnested replacement方針に合わせたフォーム保存を実装する
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
- Recipe作成・編集フォームでnested replacement方針をどう見せるか

## Notes for Next Agent

- Login開発用アカウントは `owner@example.com` / `password`。
- frontendは `shop_id` を送らず、backend responseを表示する。
- API clientは `frontend/src/api/api.ts`。
- Ingredient API clientは `frontend/src/api/ingredients.ts`。
- Unit API clientは `frontend/src/api/units.ts`。
- Ingredient Formは `frontend/src/pages/IngredientFormPage.tsx`。
- `same_unit` は `usage_unit_id = purchase_unit_id` で送信する。
- `conversion` は `conversion_from_unit_id = purchase_unit_id`、`conversion_to_unit_id = usage_unit_id` で送信する。
- `none` では価格・単位・換算情報を `null` にして送信する。

## Suggested Commit Message

```text
feat(frontend): add ingredient create and edit forms
```
