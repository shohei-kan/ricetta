# Frontend Implementation Handoff Archive

Frontend画面実装に関するhandoffをここに追記する。

## 2026-05-06 Frontend foundation auth layout dashboard

Frontend Foundation / Auth / Layout / Dashboardを実装した。

### Summary

- `GET /api/v1/auth/csrf/` を追加し、Django Session Auth向けにCSRF cookie取得を用意
- frontend API clientを追加し、`credentials: "include"` とunsafe methodの `X-CSRFToken` 送信に対応
- React ContextベースのAuth stateを追加
- `/login` を追加し、ログイン成功後に `/dashboard` へ遷移
- `/dashboard` `/prep` `/recipes` `/ingredients` `/settings` をProtected route化
- 共通App Layoutを追加
- スマホは下部ナビ、タブレット横 / PCは約120pxの固定テキストSidebar
- Dashboard APIを表示するDashboard画面を追加
- `/prep` `/recipes` `/ingredients` `/settings` にplaceholderを追加

### Design Notes

Figma MakeのRicetta MVP Wireframesは、画面全体の雰囲気、柔らかい背景、カード設計、余白、Dashboardの2カラム構成、タブレット横の固定Sidebar方針を参考にした。コードは丸ごと移植せず、既存Vite frontendに合わせてAPI連携可能な土台として再実装した。

### Key Files

- `frontend/src/App.tsx`
- `frontend/src/auth/AuthContext.tsx`
- `frontend/src/auth/auth-context.ts`
- `frontend/src/auth/useAuth.ts`
- `frontend/src/api/api.ts`
- `frontend/src/api/auth.ts`
- `frontend/src/api/dashboard.ts`
- `frontend/src/components/AppLayout.tsx`
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/pages/PlaceholderPage.tsx`
- `frontend/src/index.css`
- `backend/api/views.py`
- `backend/api/urls.py`
- `backend/api/tests.py`

### Verification

- Backend check: pass
- Migration check: pass
- Backend tests: pass
- Frontend build: pass
- Frontend lint: pass

## 2026-05-06 Ingredient create and edit forms

Ingredient作成・編集フォームを実装した。

### Summary

- `frontend/src/api/ingredients.ts` に `createIngredient` / `updateIngredient` を追加
- `frontend/src/api/units.ts` を追加
- `/ingredients/new` routeを追加
- `/ingredients/:id/edit` routeを追加
- `frontend/src/pages/IngredientFormPage.tsx` を追加
- Ingredient Listから作成画面へ移動できる導線を追加
- Ingredient Detailから編集画面へ移動できる導線を追加
- `cost_mode` ごとの入力切り替えを追加
- 最低限のfrontend validationを追加
- backend validation errorを表示

### Decisions

- `same_unit` は仕入単位を選ぶと使用単位も同じ値に自動設定する。
- `conversion` は換算元単位を仕入単位、換算先単位を使用単位に自動設定する。
- 保存失敗時も入力内容は消さない。
- Ingredient削除UI、Unit作成・編集UIはまだ実装しない。

### Key Files

- `frontend/src/api/ingredients.ts`
- `frontend/src/api/units.ts`
- `frontend/src/pages/IngredientFormPage.tsx`
- `frontend/src/pages/IngredientListPage.tsx`
- `frontend/src/pages/IngredientDetailPage.tsx`
- `frontend/src/App.tsx`
- `docs/handoff/latest.md`

### Verification

- Frontend build: pass
- Frontend lint: pass

## 2026-05-06 Category and unit settings

Settings画面でCategory / Unit管理を実装した。

### Summary

- `frontend/src/api/categories.ts` に作成・更新・削除clientを追加
- `frontend/src/api/units.ts` に作成・更新・削除clientを追加
- `/settings` placeholderをSettingsPageに差し替え
- Category一覧 / 作成 / 編集 / 削除を追加
- Unit一覧 / 作成 / 編集 / 削除を追加
- 標準Unitをreadonly表示にした
- loading / empty / error / save error / delete errorを追加

### Decisions

- frontendから `shop_id` は送らない。
- SettingsはMVPではCategory / Unit管理に限定する。
- 編集UIは作成フォームが編集フォームに切り替わる簡易方式にする。
- 標準Unitは編集・削除ボタンを出さず、店舗独自Unitのみ編集・削除可能にする。
- 保存/削除成功後は一覧を再取得する。
- 削除時は `window.confirm()` を使う。
- ユーザー管理、店舗情報編集、請求設定は実装しない。

### Key Files

- `frontend/src/api/categories.ts`
- `frontend/src/api/units.ts`
- `frontend/src/pages/SettingsPage.tsx`
- `frontend/src/App.tsx`
- `docs/handoff/latest.md`

### Verification

- Frontend build: pass
- Frontend lint: pass

## 2026-05-06 Add recipe to prep flow

Recipe Detailから今日の仕込みへ追加する導線を実装した。

### Summary

- `frontend/src/api/prepTasks.ts` に `createPrepTask` を追加
- `POST /api/v1/prep-tasks/` でPrepTaskを作成
- Recipe Detailに「今日の仕込みに追加」ボタンを追加
- Recipe Detail内にAdd to Prepパネルを追加
- 仕込み日、予定数量、予定単位、メモを入力できるようにした
- 予定単位選択肢を `GET /api/v1/units/` から取得
- 最低限のfrontend validationを追加
- backend validation errorを表示

### Decisions

- frontendから `shop_id` は送らない。
- Add to Prepは新routeを作らず、Recipe Detail内のパネルとして表示する。
- 仕込み日は今日を初期値にし、日付入力で変更可能にする。
- 予定数量 / 予定単位はRecipeの基準量 / 基準単位を初期値にする。
- Unit取得失敗時もRecipeの基準単位をfallbackとして表示する。
- 保存成功後は `/prep` へ移動する。
- Add to Prepフォームには原価情報を表示しない。
- PrepTask編集・削除UI、PrepAction Modal本格実装はまだ実装しない。

### Key Files

- `frontend/src/api/prepTasks.ts`
- `frontend/src/pages/RecipeDetailPage.tsx`
- `docs/handoff/latest.md`

### Verification

- Frontend build: pass
- Frontend lint: pass

## 2026-05-06 Recipe create and edit forms

Recipe作成・編集画面を実装した。

### Summary

- `frontend/src/api/recipes.ts` に `createRecipe` / `updateRecipe` を追加
- `frontend/src/api/categories.ts` を追加
- `/recipes/new` routeを追加
- `/recipes/:id/edit` routeを追加
- `frontend/src/pages/RecipeFormPage.tsx` を追加
- Recipe Listから作成画面へ移動できる導線を追加
- Recipe Detailから編集画面へ移動できる導線を追加
- Category / Unit / Ingredient選択肢をAPIから取得
- Recipe基本情報、材料行、工程行、管理情報のフォームを追加
- 材料行と工程行の追加・削除を追加
- 最低限のfrontend validationを追加
- backend validation errorを表示

### Decisions

- frontendから `shop_id` は送らない。
- 編集保存時は現在フォームにある `ingredients` / `steps` をpayloadに含め、backendのnested replacement方針に合わせる。
- Ingredient選択時に、Ingredientの `usage_unit` を材料行Unitへ自動設定する。
- 工程番号は保存時に表示順で再採番する。
- 空の材料行・工程行は送信前に除外する。
- 材料行には原価情報を表示しない。
- Recipe削除UI、PrepTask作成フォーム、画像アップロードはまだ実装しない。

### Key Files

- `frontend/src/api/recipes.ts`
- `frontend/src/api/categories.ts`
- `frontend/src/pages/RecipeFormPage.tsx`
- `frontend/src/pages/RecipeListPage.tsx`
- `frontend/src/pages/RecipeDetailPage.tsx`
- `frontend/src/App.tsx`
- `docs/handoff/latest.md`

### Verification

- Frontend build: pass
- Frontend lint: pass

## 2026-05-06 Ingredient list and detail views

Ingredient List / Detail画面を実装した。

### Summary

- `frontend/src/api/ingredients.ts` を追加
- `GET /api/v1/ingredients/` で材料一覧を取得
- `GET /api/v1/ingredients/{id}/` で材料詳細を取得
- `/ingredients` placeholderをIngredient List画面に差し替え
- `/ingredients/:id` routingを追加
- Ingredient Listに検索欄、Ingredientカード、loading / empty / errorを追加
- Ingredient Detailに戻るボタン、基本情報、原価計算モード、仕入情報、換算情報、単価表示を追加
- `cost_mode` を日本語ラベルと説明で表示
- `unit_cost_label` がない場合は「計算なし」と表示

### Decisions

- Ingredient Detailは材料マスター管理画面なので、原価・換算情報を表示する。
- Recipe Detailとは役割を分け、Recipe Detailの材料欄には原価・仕入・換算情報を混ぜない。
- Ingredient作成・編集フォームはまだ実装しない。

### Key Files

- `frontend/src/api/ingredients.ts`
- `frontend/src/pages/IngredientListPage.tsx`
- `frontend/src/pages/IngredientDetailPage.tsx`
- `frontend/src/App.tsx`
- `docs/handoff/latest.md`

### Verification

- Frontend build: pass
- Frontend lint: pass

## 2026-05-06 Recipe list and detail views

Recipe List / Detail画面を実装した。

### Summary

- `frontend/src/api/recipes.ts` を追加
- `GET /api/v1/recipes/` でレシピ一覧を取得
- `GET /api/v1/recipes/{id}/` でレシピ詳細を取得
- `/recipes` placeholderをRecipe List画面に差し替え
- `/recipes/:id` routingを追加
- Recipe Listに検索欄、Recipeカード、loading / empty / errorを追加
- Recipe Detailに戻るボタン、材料、作り方、注意点、アレルゲン、原価情報カードを追加
- Prep TodayのカードからRecipe Detailへ移動できる「レシピを見る」導線を追加

### Decisions

- Recipe Detailでは材料欄と原価情報を分離する。
- 材料欄には材料ごとの原価、単価、仕入情報、換算情報を表示しない。
- 原価情報は `cost_summary` のみを使い、専用カードに集約する。
- Recipe作成・編集フォームはまだ実装しない。

### Key Files

- `frontend/src/api/recipes.ts`
- `frontend/src/pages/RecipeListPage.tsx`
- `frontend/src/pages/RecipeDetailPage.tsx`
- `frontend/src/pages/PrepTodayPage.tsx`
- `frontend/src/App.tsx`
- `docs/handoff/latest.md`

### Verification

- Frontend build: pass
- Frontend lint: pass

## 2026-05-06 Prep today status board

Prep Today画面を実装した。

### Summary

- `frontend/src/api/prepTasks.ts` を追加
- `GET /api/v1/prep-tasks/?date=YYYY-MM-DD` で今日の仕込み一覧を取得
- `PATCH /api/v1/prep-tasks/{id}/status/` でstatus更新
- `/prep` placeholderをPrep Today画面に差し替え
- 未着手 / 作業中 / 完了のsummaryを表示
- status別にPrepTaskカードを表示
- タブレット横 / PCでは3カラム、スマホでは縦1カラム
- カード内にstatus更新ボタンを配置
- loading / empty / error / status更新errorを追加

### Decisions

- status更新後はMVPでは一覧を再取得する。
- 日付は今日固定で取得し、日付切り替えUIは後続フェーズに残す。
- ドラッグ&ドロップ、Prep Action Modal、PrepTask作成フォームは実装しない。
- PrepTaskカードに原価情報は表示しない。

### Key Files

- `frontend/src/api/prepTasks.ts`
- `frontend/src/pages/PrepTodayPage.tsx`
- `frontend/src/App.tsx`
- `docs/handoff/latest.md`

### Verification

- Frontend build: pass
- Frontend lint: pass
