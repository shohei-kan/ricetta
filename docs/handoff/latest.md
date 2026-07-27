# Ricetta Handoff Latest

## Date

2026-07-27

## Project

Ricetta

## Status

Demo seed uses prep tomato sauce in caponata.

## Summary

公開デモ用seedを整理し、追加サンプルRecipe「ベーコンとナスのトマトソースパスタ」を削除した。仕込み用Recipe「トマトソース」はIngredient「トマトソース」として維持し、主役レシピ「カポナータ」の材料に600g使用する構成へ変更した。これにより、トマトソースが仕込み用Recipeであり、販売商品Recipeの材料原価へ反映される流れを既存レシピ内で確認できる。

## Current Goal

次は実ブラウザで、Ingredient一覧 / Recipe Form / カポナータのRecipe Detailを確認する。特に、Ingredient「トマトソース」が仕込み由来材料として表示され、カポナータの材料と原価に600g分が反映されることを確認する。

## Current State

- Recipeには `recipe_type` がある。値は `prep` / `menu`。
- `base_yield_quantity` / `base_yield_unit` はUI上「出来上がり量」として扱う。
- `cost_summary.material_cost` は、出来上がり量1単位あたり原価。
- Ingredientには `ingredient_type` がある。値は `raw` / `prep_recipe`。
- `ingredient_type=raw` は従来通り `cost_mode=none / same_unit / conversion` で原価計算する。
- `ingredient_type=prep_recipe` は `source_recipe` を参照する。
- `source_recipe` に指定できるのは、同じShopの `recipe_type=prep` のRecipeのみ。
- `raw` で `source_recipe` を指定するとAPIは400を返す。
- `prep_recipe` で `source_recipe` または `usage_unit` がない場合、APIは400を返す。
- Recipe保存時、自分自身を `source_recipe` にしたIngredientを材料に入れる直接循環は400で止める。
- 原価計算側にも再帰ガードを入れ、深い循環で無限再帰しないようにしている。
- 深い循環参照を保存前に完全検証する仕組みはMVP後の課題。
- seed demo dataには、仕込み用Recipe「トマトソース」、Ingredient「トマトソース」、販売商品Recipe「カポナータ」が含まれる。
- ピクルスは `recipe_type=menu`、出来上がり量10食分の販売商品Recipeとして扱う。
- カポナータはIngredient「トマトソース」を600g使用する。
- パスタRecipeは公開デモseedから削除済み。

## What Was Done

- `Ingredient.IngredientType` を追加した。
- `Ingredient.ingredient_type` / `Ingredient.source_recipe` を追加し、migration `0007_ingredient_ingredient_type_ingredient_source_recipe.py` を作成・適用した。
- Ingredient serializerで `ingredient_type` / `source_recipe_id` を読み書き可能にした。
- Ingredient list/detail responseに `ingredient_type` と `source_recipe` 概要を含めた。
- Ingredient APIで、同一Shop・prep recipe限定、raw/source_recipe禁止、prep_recipe/source_recipe必須を検証するようにした。
- `calculate_recipe_cost_summary()` を更新し、prep_recipe Ingredientの原価をsource recipeから計算するようにした。
- `convert_quantity_between_units()` を追加し、`kg` ↔ `g`、`L` ↔ `ml`、同一単位に対応した。
- Recipe serializerで直接循環を検証し、計算側にもvisited setの再帰ガードを追加した。
- Ingredient Formに「材料種別」を追加した。
- 仕込みレシピ選択時は、source recipeと使用単位だけを入力し、通常の原価計算モード入力を隠すようにした。
- Ingredient List / Detailで仕込みレシピ由来材料が分かる表示にした。
- Recipe Formの材料selectで `トマトソース（仕込み）` のように表示するようにした。
- `seed_portfolio_data` からベーコン、スパゲッティ、パスタRecipeを削除した。
- トマトソース由来Ingredientは維持し、カポナータの材料に600g追加した。
- seed testsのピクルス期待値を `menu / 10食分` に揃えた。
- source_recipeの `PROTECT` に合わせて、`seed_portfolio_data --reset` の削除順を調整した。
- backend testsにIngredient API、prep_recipe原価計算、簡易単位変換、循環ガード、seed確認を追加した。
- docsに仕込み用RecipeをIngredientとして使う方針を追記した。

## Key Decisions

- Recipeを直接RecipeIngredientから参照するのではなく、Ingredientを介して仕込み用Recipeを材料化する。
- `ingredient_type=prep_recipe` のIngredientは、source recipeの1単位あたり原価から材料原価を計算する。
- Unitモデルに変換係数は追加しない。MVPでは `kg/g` と `L/ml` の小さなhelperで対応する。
- 変換できない単位の組み合わせは0円扱いにする。
- `prep_recipe` Ingredientの `cost_mode` は `none` に寄せ、仕入価格・換算情報は使わない。
- 深い循環参照の完全な保存前検証は今回やらない。計算側の再帰ガードで無限再帰を防ぐ。
- owner/staff権限は変更しない。

## Key Files

- `backend/api/models.py`
- `backend/api/migrations/0007_ingredient_ingredient_type_ingredient_source_recipe.py`
- `backend/api/serializers.py`
- `backend/api/costing.py`
- `backend/api/views.py`
- `backend/api/management/commands/seed_portfolio_data.py`
- `backend/api/tests/base.py`
- `backend/api/tests/test_ingredients.py`
- `backend/api/tests/test_recipes.py`
- `backend/api/tests/test_seed_portfolio_data.py`
- `frontend/src/api/ingredients.ts`
- `frontend/src/pages/IngredientFormPage.tsx`
- `frontend/src/pages/IngredientListPage.tsx`
- `frontend/src/pages/IngredientDetailPage.tsx`
- `frontend/src/pages/RecipeFormPage.tsx`
- `docs/technical/data-model.md`
- `docs/technical/api-design.md`
- `docs/product/mvp-requirements.md`
- `docs/deploy/demo.md`
- `docs/handoff/latest.md`

## Verification

実行済み:

```bash
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py test api.tests.test_seed_portfolio_data
docker compose exec backend python manage.py test
docker compose exec backend python manage.py check
docker compose exec backend python manage.py makemigrations --check --dry-run
cd frontend
npm run lint
npm run build
docker compose exec backend python manage.py seed_portfolio_data --reset
docker compose exec backend python manage.py shell -c "from api.models import Recipe, Ingredient, Shop; shop=Shop.objects.get(name='〇〇食堂'); cap=Recipe.objects.get(shop=shop, name='カポナータ'); print([(ri.ingredient.name, ri.quantity, ri.unit.name, ri.ingredient.ingredient_type) for ri in cap.ingredients.select_related('ingredient','unit').all()]); print(Recipe.objects.filter(shop=shop, name__icontains='パスタ').exists())"
git diff --check
```

Result:

- migration `0007_ingredient_ingredient_type_ingredient_source_recipe.py` created.
- migrate: pass
- seed command tests: 3 pass
- backend tests: 143 pass
- backend check: pass
- makemigrations dry-run: no changes detected
- frontend lint: pass
- frontend build: pass
- `seed_portfolio_data --reset`: pass
- seed DB確認: カポナータに `トマトソース / 600.00 g / prep_recipe` が含まれる
- seed DB確認: パスタRecipeなし
- whitespace check: pass

Manual browser verification:

- 未実施。次にUI確認する場合は、Ingredient一覧で「トマトソース」が仕込み由来材料として表示されること、Recipe Formで「トマトソース（仕込み）」を材料として選べること、カポナータのRecipe Detailで材料と原価にトマトソース600g分が反映されることを確認する。

## Current Product Scope

- Login / logout and Shop scope
- owner / staff role control for MVP operations
- Recipe / Ingredient / Prep Today / Dashboard / Settings / Account
- Recipe type distinction between prep recipes and menu recipes
- Prep recipes as reusable ingredients through `ingredient_type=prep_recipe`
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
- Complex unit conversion table
- Unit model conversion factors
- Automatic Ingredient creation button from prep Recipe
- Full deep cycle validation before save
- Demo reset API / reset button
- cron / systemd timer実設定
- AWSインスタンス作成
- Docker Compose production構成の大幅変更
- Demo-specific branch or duplicated app directories

## Next Recommended Tasks

1. 実ブラウザでIngredient Formの「通常材料 / 仕込みレシピ」切り替えを確認する。
2. 実ブラウザでRecipe Formの材料selectに `トマトソース（仕込み）` が出ることを確認する。
3. カポナータのRecipe Detailで、トマトソース由来Ingredientを含む原価が自然に表示されることを確認する。
4. owner / staff両方でログインし、staffがIngredient / Recipe編集できない既存挙動が壊れていないことを確認する。
5. AWS公開デモ用の実env値と定期reset方法を整理する。

## Open Questions

- 深い循環参照を保存時にどこまで厳密に検証するか。
- `prep_recipe` Ingredientの詳細画面で、source recipeへの導線を追加するか。
- 仕込み用RecipeからIngredientを自動作成する導線を将来追加するか。

## Notes for Next Agent

- `ingredient_type=prep_recipe` はIngredient経由でsource Recipeを使う設計。RecipeIngredientのDB構造は変更していない。
- `source_recipe` は `on_delete=PROTECT`。seed resetではRecipeより先にIngredientを削除する必要がある。
- `cost_summary.material_cost` は出来上がり量1単位あたり原価。prep_recipe Ingredientもこの値を使って計算される。
- 公開デモseedでは、仕込み用トマトソースをカポナータの材料として使う。パスタRecipeは作らない。
- ピクルスは公開デモseedでは販売商品Recipe（`menu / 10食分`）として扱う。
- `kg/g` と `L/ml` 以外の単位変換は0円扱い。Unitに変換係数はまだ持たせていない。
- `backend/api/tests.py` は削除済み。新規backend APIテストは `backend/api/tests/test_*.py` に追加する。
- 共通fixture / helperが必要な場合は `backend/api/tests/base.py` の `ApiTestCase` を使う。
- `owner@example.com` / `password` と `staff@example.com` / `password` は `seed_portfolio_data` で再作成・更新される。
- `backend/api/demo_policy.py` はまだ既存Viewから使っていない。DEMO_MODE固有制限は次タスクで明示的に行う。
- production envにはlocalhostを含めない。
- Docker frontendは `http://localhost:5174`。

## Suggested Commit Message

```text
chore(seed): use prep tomato sauce in caponata demo
```
