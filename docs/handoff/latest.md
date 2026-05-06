# Ricetta Handoff Latest

## Date

2026-05-06

## Project

Ricetta

## Status

Frontend tablet sidebar layout fixed

## Summary

AppLayoutのresponsive navigationを修正済み。Tailwind v4環境でresponsive variantが生成されていなかったため、CSS entryを修正し、タブレット横 / PC幅では約120pxの左Sidebarを常時表示、スマホでは下部ナビを表示する。

## Current Goal

次はSettings画面またはPrepTask作成の補助導線を整え、運用に必要な設定・導線を固める。

## What Was Done

- `frontend/src/components/AppLayout.tsx` のSidebar layoutを修正
- `frontend/src/index.css` をTailwind v4形式の `@import "tailwindcss";` に変更
- 親Layoutを `md:flex` に変更
- Sidebarを `hidden md:flex w-[120px] shrink-0` の左カラムとして表示する形に変更
- `fixed` + `md:ml-[120px]` 構成をやめ、mainを `flex-1 min-w-0` に変更
- タブレット横 / PC幅でSidebar、スマホで下部ナビになる構成を明確化
- Sidebarのラベルを `Dashboard` / `仕込み` / `レシピ` / `材料` / `設定` に変更
- `/recipes/:id` / `/recipes/new` / `/recipes/:id/edit` は親メニュー「レシピ」がactiveになることを確認
- `/ingredients/:id` / `/ingredients/new` / `/ingredients/:id/edit` は親メニュー「材料」がactiveになることを確認
- build後のCSSに `@media (width>=48rem)` と `md:flex` / `md:hidden` が生成されることを確認
- UI guidelines / handoffを更新

## Key Decisions

- AppLayoutは全Protected pagesの共通Layoutとして使う。
- AppLayout適用漏れではなく、Tailwind responsive CSS未生成がSidebar非表示の原因だった。
- `@tailwind base/components/utilities` のままでは現環境で `md:` 系が生成されていなかったため、Tailwind v4の `@import "tailwindcss";` に揃えた。
- タブレット横 / PCでは `md` breakpointからSidebarを表示する。
- Sidebarは開閉なし、テキストのみ、約120pxのカード型ナビにする。
- active stateはApp.tsxの `toRoutePath()` で親メニューへ正規化する。
- スマホではSidebarを出さず、下部ナビを表示する。

## Key Files

- `frontend/src/components/AppLayout.tsx`
- `frontend/src/index.css`
- `frontend/src/App.tsx`
- `docs/product/ui-guidelines.md`

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
fix(frontend): show tablet sidebar layout
```
