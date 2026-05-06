# Ricetta Handoff Latest

## Date

2026-05-06

## Project

Ricetta

## Status

Phase 12 Frontend Recipe Create / Edit implemented

## Summary

Recipe作成・編集画面まで実装済み。`/recipes/new` でレシピを新規作成し、`/recipes/:id/edit` で既存レシピを編集できる。Category / Unit / Ingredient選択、材料行・工程行のnested form、最低限のfrontend validation、backend validation error表示が入った。

## Current Goal

次はPrepTask作成導線またはSettings画面へ進み、レシピを今日の仕込みへ登録できる状態に近づける。

## What Was Done

- `frontend/src/api/recipes.ts` に `createRecipe` / `updateRecipe` を追加
- `frontend/src/api/categories.ts` を追加
- `GET /api/v1/categories/` でCategory選択肢を取得
- 既存のUnit / Ingredient API clientをRecipe formで利用
- `/recipes/new` routeを追加
- `/recipes/:id/edit` routeを追加
- `frontend/src/pages/RecipeFormPage.tsx` を追加
- Recipe Listに「レシピを追加」導線を追加
- Recipe Detailに「編集」導線を追加
- 作成成功後は作成されたRecipe Detailへ遷移
- 編集成功後はRecipe Detailへ遷移
- Recipe基本情報、材料行、工程行、管理情報のフォームを追加
- 材料行の追加・削除を追加
- 工程行の追加・削除を追加
- Ingredient選択時にIngredientの `usage_unit` を材料行Unitへ自動設定
- 編集保存時は `ingredients` / `steps` をpayloadに含め、backendのnested replacement方針に合わせた
- 工程番号は保存時にフォーム表示順で再採番する方針にした
- 空の材料行・工程行は送信前に除外する方針にした
- name、基準量、基準単位、材料行、工程行の最低限frontend validationを追加
- backend validation errorをフォーム上に表示
- 保存失敗時に入力内容が消えないようにした
- README / product screens / handoffを更新

## Key Decisions

- frontendから `shop_id` は送らない。
- Shop scopeと認可はbackendに任せ、Recipe作成・編集はbackend validationに従う。
- Recipeフォームは基本情報 / 材料 / 作り方 / 管理情報に分ける。
- 材料行には原価情報を表示しない。
- Ingredient選択時に `usage_unit` があれば材料行Unitに自動設定する。
- 工程番号は保存時に表示順で `1, 2, 3...` と再採番する。
- 編集保存時は現在フォームにある `ingredients` / `steps` をpayloadに含め、backend側で全置き換えする。
- 空の材料行・工程行は送信前に除外する。
- DRF validation errorはMVPでは汎用メッセージ + backend response文字列で表示する。
- Recipe削除UI、PrepTask作成フォーム、画像アップロード、材料ごとの原価内訳表示はまだ実装しない。

## Key Files

- `frontend/src/api/recipes.ts`
- `frontend/src/api/categories.ts`
- `frontend/src/api/units.ts`
- `frontend/src/api/ingredients.ts`
- `frontend/src/pages/RecipeFormPage.tsx`
- `frontend/src/pages/RecipeListPage.tsx`
- `frontend/src/pages/RecipeDetailPage.tsx`
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

1. PrepTask作成フォームまたは「レシピから仕込みに追加」導線を実装する
2. SettingsでCategory / Unitの管理画面を整える
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

## Notes for Next Agent

- Login開発用アカウントは `owner@example.com` / `password`。
- frontendは `shop_id` を送らず、backend responseを表示する。
- API clientは `frontend/src/api/api.ts`。
- Recipe API clientは `frontend/src/api/recipes.ts`。
- Category API clientは `frontend/src/api/categories.ts`。
- Ingredient API clientは `frontend/src/api/ingredients.ts`。
- Unit API clientは `frontend/src/api/units.ts`。
- Recipe Formは `frontend/src/pages/RecipeFormPage.tsx`。
- Recipe編集保存では `ingredients` / `steps` をpayloadに含め、backendのnested replacementに合わせる。
- Ingredient選択時、Ingredientの `usage_unit` を材料行Unitに自動設定している。
- 工程番号は保存時に表示順で再採番している。
- 空の材料行・工程行は送信前に除外している。

## Suggested Commit Message

```text
feat(frontend): add recipe create and edit forms
```
