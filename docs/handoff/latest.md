# Ricetta Handoff Latest

## Date

2026-05-06

## Project

Ricetta

## Status

Phase 13 Frontend Add Recipe to Prep implemented

## Summary

Recipe Detailから今日の仕込みへ追加する導線まで実装済み。`/recipes/:id` の「今日の仕込みに追加」からPrepTaskを作成し、保存成功後に `/prep` へ移動してPrep Todayに表示できる。

## Current Goal

次はSettings画面またはPrepTask作成の補助導線を整え、運用に必要な設定・導線を固める。

## What Was Done

- `frontend/src/api/prepTasks.ts` に `createPrepTask` を追加
- `POST /api/v1/prep-tasks/` でPrepTaskを作成できるようにした
- Recipe Detailに「今日の仕込みに追加」ボタンを追加
- Recipe Detail内にAdd to Prepパネルを追加
- Add to Prepで仕込み日、予定数量、予定単位、メモを入力できるようにした
- 仕込み日の初期値を今日にした
- 仕込み日は `<input type="date">` で変更可能にした
- 予定数量の初期値にRecipeの `base_yield_quantity` を使うようにした
- 予定単位の初期値にRecipeの `base_yield_unit.id` を使うようにした
- 予定単位の選択肢を `GET /api/v1/units/` から取得
- Unit取得失敗時もRecipeの基準単位を選択肢として表示できるfallbackを追加
- 保存成功後は `/prep` へ遷移する方針にした
- date / recipe_id / planned_quantity / planned_unit_id の最低限frontend validationを追加
- backend validation errorをパネル上に表示
- 保存失敗時に入力内容が消えないようにした
- README / product screens / handoffを更新

## Key Decisions

- frontendから `shop_id` は送らない。
- Shop scopeと認可はbackendに任せ、PrepTask作成時もfrontendから `shop_id` は送らない。
- Add to Prepは新routeを作らず、Recipe Detail内の小さなパネルとして表示する。
- 仕込み日はMVPでは今日を初期値にし、日付入力で変更可能にする。
- 予定数量 / 予定単位はRecipeの基準量 / 基準単位を初期値にする。
- 保存成功後は `/prep` へ移動し、追加結果をPrep Todayで確認する。
- Add to Prepフォームには原価情報を表示しない。
- DRF validation errorはMVPでは汎用メッセージ + backend response文字列で表示する。
- PrepTask編集・削除UI、PrepTask作成専用ページ、Prep Action Modal本格実装はまだ実装しない。

## Key Files

- `frontend/src/api/prepTasks.ts`
- `frontend/src/api/units.ts`
- `frontend/src/pages/RecipeDetailPage.tsx`
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

1. SettingsでCategory / Unitの管理画面を整える
2. PrepTask作成専用フォームが必要か、Recipe Detail導線だけで足りるか検証する
3. Recipe / Ingredient削除UIの要否とタイミングを決める
4. Recipe formの入力補助や並び替えを必要に応じて整える
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
- Recipe formで材料行・工程行の並び替えUIを入れるか
- Recipe formで原価プレビューを表示するか
- Recipe Detail以外からPrepTaskを作成する専用導線が必要か

## Notes for Next Agent

- Login開発用アカウントは `owner@example.com` / `password`。
- frontendは `shop_id` を送らず、backend responseを表示する。
- API clientは `frontend/src/api/api.ts`。
- Recipe API clientは `frontend/src/api/recipes.ts`。
- Category API clientは `frontend/src/api/categories.ts`。
- Ingredient API clientは `frontend/src/api/ingredients.ts`。
- Unit API clientは `frontend/src/api/units.ts`。
- Recipe Formは `frontend/src/pages/RecipeFormPage.tsx`。
- PrepTask API clientは `frontend/src/api/prepTasks.ts`。
- Recipe Detail内のAdd to Prepパネルから `createPrepTask` を呼ぶ。
- 保存成功後は `/prep` へ移動する。
- Recipe編集保存では `ingredients` / `steps` をpayloadに含め、backendのnested replacementに合わせる。
- Ingredient選択時、Ingredientの `usage_unit` を材料行Unitに自動設定している。
- 工程番号は保存時に表示順で再採番している。
- 空の材料行・工程行は送信前に除外している。

## Suggested Commit Message

```text
feat(frontend): add recipe to prep flow
```
