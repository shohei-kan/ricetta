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
