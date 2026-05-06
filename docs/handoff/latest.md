# Ricetta Handoff Latest

## Date

2026-05-06

## Project

Ricetta

## Status

Phase 14 Frontend Settings Category / Unit Management implemented

## Summary

Settings画面でCategory / Unit管理を実装済み。`/settings` でレシピカテゴリと単位を一覧表示し、Categoryの作成・編集・削除、店舗独自Unitの作成・編集・削除ができる。標準Unitはreadonly表示にした。

## Current Goal

次は削除UIや日付切り替えなど、MVP運用で必要な仕上げ範囲を決める。

## What Was Done

- `frontend/src/api/categories.ts` に `createCategory` / `updateCategory` / `deleteCategory` を追加
- `frontend/src/api/units.ts` に `createUnit` / `updateUnit` / `deleteUnit` を追加
- Unit型に `is_standard` / `sort_order` / `is_active` を追加
- `/settings` placeholderをSettingsPageへ差し替え
- `frontend/src/pages/SettingsPage.tsx` を追加
- Category一覧を表示
- Category作成フォームを追加
- Category編集・削除を追加
- Unit一覧を表示
- Unit作成フォームを追加
- 店舗独自Unitの編集・削除を追加
- 標準Unitは編集・削除ボタンを出さないreadonly表示にした
- 保存成功 / 削除成功後は一覧を再取得する方針にした
- loading / empty / error / save error / delete errorを追加
- README / product screens / handoffを更新

## Key Decisions

- SettingsはMVPではCategory / Unit管理に限定する。
- frontendから `shop_id` は送らない。
- Categoryは現在Shopのものだけbackend responseとして扱う。
- Unitは標準Unit + 現在Shop Unitを表示する。
- 標準Unitはfrontendでも編集・削除不可にする。
- 編集UIはMVPでは作成フォームが編集フォームに切り替わる簡易方式にする。
- 削除は `window.confirm()` で確認する。
- 保存/削除成功後は楽観的更新ではなく一覧再取得する。

## Key Files

- `frontend/src/api/categories.ts`
- `frontend/src/api/units.ts`
- `frontend/src/pages/SettingsPage.tsx`
- `frontend/src/App.tsx`
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

1. Recipe / Ingredient削除UIの要否とタイミングを決める
2. Prep Todayの日付切り替えUIを実装するか検証する
3. Recipe formの入力補助や並び替えを必要に応じて整える
4. MVPリリース前の画面動作確認チェックリストを作る
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
- Settingsで店舗情報編集をMVPに含めるか

## Notes for Next Agent

- Login開発用アカウントは `owner@example.com` / `password`。
- frontendは `shop_id` を送らず、backend responseを表示する。
- API clientは `frontend/src/api/api.ts`。
- Recipe API clientは `frontend/src/api/recipes.ts`。
- Category API clientは `frontend/src/api/categories.ts`。
- Ingredient API clientは `frontend/src/api/ingredients.ts`。
- Unit API clientは `frontend/src/api/units.ts`。
- Settings Pageは `frontend/src/pages/SettingsPage.tsx`。
- 標準Unitは `is_standard` を見てreadonly表示している。
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
feat(frontend): add category and unit settings
```
