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
