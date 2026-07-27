# Ricetta Handoff Latest

## Date

2026-07-27

## Project

Ricetta

## Status

Recipe cost summary aligned with finished yield.

## Summary

Recipeの `base_yield_quantity` / `base_yield_unit` を「出来上がり量」として扱う方針に揃えた。原価サマリーの `material_cost` は、RecipeIngredientの材料原価合計を出来上がり量で割った1単位あたり材料原価として返す。Recipe Detail / Recipe List / Recipe Formの表示ラベルも「基準」から「出来上がり量」へ変更した。seedのトマトソースは2.5kg、ピクルスは1kg、カポナータは8食分、クレームブリュレは6個の出来上がり量にした。

## Current Goal

次はAWS公開デモ用の実運用準備へ進める。具体的には、公開環境の実env値、デモ環境で追加禁止する操作範囲、定期resetの実行方法、実ブラウザでのowner/staff導線確認を詰める。

## Current State

- Recipeモデルに `recipe_type` がある。
- `recipe_type` の値は `prep` / `menu`。
- defaultは `prep` なので既存データは仕込み用として扱われる。
- Recipe serializerは `recipe_type` をlist/detail responseに含め、create/update/patchで受け取る。
- Recipe Formでは「用途」として「仕込み用・中間材料」「販売商品」を選べる。
- Recipe Detailの原価情報カードは `recipe_type` に応じて表示内容を変える。
- `base_yield_quantity` / `base_yield_unit` は出来上がり量として扱う。
- `cost_summary.material_cost` は材料原価合計ではなく、出来上がり量で割った1単位あたり材料原価。
- `cost_summary.gross_profit` と `cost_summary.cost_rate` も1単位あたり材料原価で計算する。
- seed demo dataではトマトソース・ピクルスが `prep`、カポナータ・クレームブリュレが `menu`。
- seed demo dataの出来上がり量は、トマトソース2.5kg、ピクルス1kg、カポナータ8食分、クレームブリュレ6個。
- backend APIテストは `backend/api/tests/` に機能単位で分割済み。
- `VITE_DEMO_MODE=true` のときだけDemoBannerと公開デモ用ログイン情報を表示する。
- `backend/api/demo_policy.py` に `deny_in_demo()` を追加済み。ただし既存Viewにはまだ適用していない。

## What Was Done

- `Recipe.RecipeType` を追加した。
- `Recipe.recipe_type` フィールドを追加し、migration `0006_recipe_recipe_type.py` を作成した。
- Recipe list/detail serializer fieldsに `recipe_type` を追加した。
- Recipe API testsに `recipe_type` 指定、default、不正値、list/detail responseの確認を追加した。
- `seed_portfolio_data` のサンプルレシピへ `recipe_type` を明示した。
- seed command testsでサンプルレシピの `recipe_type` を確認するようにした。
- frontend Recipe型、Recipe Form payload、Recipe Form stateを更新した。
- Recipe Formに「用途」selectを追加した。
- CostSummaryCardを `prep` / `menu` で表示分岐した。
- `calculate_recipe_cost_summary()` で材料原価合計を `base_yield_quantity` で割るようにした。
- Recipe API testsに、menuの10食分原価、prepの1kg原価、prepの複数kg原価、出来上がり量0の安全確認を追加した。
- Recipe Detail / Recipe List / Recipe Formの「基準」表示を「出来上がり量」に変更した。
- seed demo dataの仕込み用レシピをkgベースの出来上がり量に調整した。
- docsに `recipe_type`、出来上がり量、1単位あたり原価の方針を追記した。

## Key Decisions

- `recipe_type` と `selling_price` は別概念として扱う。
- `prep` でも `selling_price` は禁止しない。ただしCostSummaryCardでは販売価格・原価率・粗利を表示しない。
- `menu` でも `selling_price` は必須にしない。未設定時は販売価格 `未設定`、原価率・粗利 `-` のままにする。
- 原価計算は、RecipeIngredient原価合計を出した後、`base_yield_quantity` が正の数なら割って1単位あたりにする。
- `base_yield_quantity` が不正・0の場合はゼロ除算せず、従来の合計原価を使う。
- DB/APIフィールド名は `base_yield_quantity` / `base_yield_unit` のままにし、今回リネームmigrationは作らない。
- recipe_typeによる権限制御変更はしない。

## Key Files

- `backend/api/models.py`
- `backend/api/costing.py`
- `backend/api/migrations/0006_recipe_recipe_type.py`
- `backend/api/serializers.py`
- `backend/api/management/commands/seed_portfolio_data.py`
- `backend/api/tests/test_recipes.py`
- `backend/api/tests/test_seed_portfolio_data.py`
- `frontend/src/api/recipes.ts`
- `frontend/src/pages/RecipeListPage.tsx`
- `frontend/src/pages/RecipeFormPage.tsx`
- `frontend/src/pages/RecipeDetailPage.tsx`
- `docs/product/mvp-requirements.md`
- `docs/technical/data-model.md`
- `docs/deploy/demo.md`
- `docs/handoff/latest.md`

## Verification

実行済み:

```bash
docker compose exec backend python manage.py test
docker compose exec backend python manage.py check
docker compose exec backend python manage.py makemigrations --check --dry-run
cd frontend
npm run lint
npm run build
git diff --check
docker compose exec backend python manage.py seed_portfolio_data --reset
docker compose exec backend python manage.py shell -c "from api.models import Recipe, Shop; shop=Shop.objects.get(name='〇〇食堂'); print([(r.name, r.recipe_type, str(r.base_yield_quantity), r.base_yield_unit.name) for r in Recipe.objects.filter(shop=shop).order_by('name')])"
```

Result:

- backend recipe / seed tests: 33 pass
- backend tests: 131 pass
- backend check: pass
- makemigrations dry-run: no changes detected
- frontend lint: pass
- frontend build: pass
- whitespace check: pass
- `seed_portfolio_data --reset`: pass
- seed DB確認: トマトソース `prep / 2.50 kg`、ピクルス `prep / 1.00 kg`、カポナータ `menu / 8.00 食分`、クレームブリュレ `menu / 6.00 個`

Manual browser verification:

- 未実施。次にUI確認する場合は、トマトソースで「出来上がり量: 2.5 kg」と「1kgあたりの材料原価です。」、カポナータで「出来上がり量: 8 食分」と「1食分あたりの原価サマリーです。」を確認する。

## Current Product Scope

- Login / logout and Shop scope
- owner / staff role control for MVP operations
- Recipe / Ingredient / Prep Today / Dashboard / Settings / Account
- Recipe type distinction between prep recipes and menu recipes
- Active Prep Today board and direct PrepTask creation
- BoardMemo as lightweight whiteboard memo under Prep Today columns
- Smartphone, tablet landscape, and PC layouts
- Demo mode foundation via environment variables
- Safe portfolio demo seed reset
- Public demo operation docs
- Demo login account information on LoginPage

## Out of Scope for MVP

- Stripe / Checkout / Billing portal
- POS integration
- Automatic inventory deduction
- Advanced ordering
- Multi-shop management UI
- Advanced role management beyond owner / staff
- Shop device mode
- Yield loss / waste rate / cooked weight
- Demo reset API / reset button
- cron / systemd timer実設定
- AWSインスタンス作成
- Docker Compose production構成の大幅変更
- Demo-specific branch or duplicated app directories

## Next Recommended Tasks

1. 実ブラウザでRecipe Formの用途selectとRecipe Detailの原価カード表示を確認する。
2. owner / staff両方でログインし、導線と403挙動を実ブラウザで手動確認する。
3. AWS公開デモ用の実env値を整理する。
4. デモ環境で追加禁止する操作（メール変更、パスワード変更、アカウント削除、店舗削除など）の範囲を決め、必要なViewに `deny_in_demo()` を適用する。
5. `seed_portfolio_data --reset` の定期実行方法（cron / systemd timer等）を別タスクで検討する。

## Open Questions

- デモ環境の自動リセット頻度をどうするか。
- デモ環境で通常role制御に加えて、どの操作を追加禁止するか。

## Notes for Next Agent

- `recipe_type` は `prep` / `menu` のみ。
- `base_yield_quantity` / `base_yield_unit` はUI上「出来上がり量」として扱う。DB/API名はまだ変更しない。
- `cost_summary.material_cost` は出来上がり量1単位あたり原価。合計原価が必要な場合は別フィールド/APIを検討する。
- 既存データはmigration defaultにより `prep` になる。
- `seed_portfolio_data --reset` 実行後、demo recipeの用途は明示状態へ戻る。
- `backend/api/tests.py` は削除済み。新規backend APIテストは `backend/api/tests/test_*.py` に追加する。
- 共通fixture / helperが必要な場合は `backend/api/tests/base.py` の `ApiTestCase` を使う。
- `owner@example.com` / `password` と `staff@example.com` / `password` は `seed_portfolio_data` で再作成・更新される。
- `VITE_DEMO_MODE` はViteのbuild時環境変数。公開環境ではfrontend build/deploy時に設定する必要がある。
- `backend/api/demo_policy.py` はまだ既存Viewから使っていない。DEMO_MODE固有制限は次タスクで明示的に行う。
- production envにはlocalhostを含めない。
- docsの旧パス `docs/api/`、`docs/data/`、`docs/planning/` は廃止済み。新規参照は `docs/technical/` または `docs/product/` を使う。
- Docker frontendは `http://localhost:5174`。

## Suggested Commit Message

```text
fix(cost): align recipe cost summary with finished yield
```
