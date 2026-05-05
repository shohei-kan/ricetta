# Ricetta Handoff Latest

## Date

2026-05-06

## Project

Ricetta

## Status

Phase 7 Frontend Foundation implemented

## Summary

Frontend Foundation / Auth / Layout / Dashboardまで実装済み。Django Session Auth向けのCSRF取得API、frontend API client、Auth state、Login画面、Protected route、Responsive App Layout、Dashboard画面、主要placeholder routesが入った。

## Current Goal

次はPrep Today画面へ進み、PrepTask APIを使って今日の仕込み一覧とstatus更新を画面から操作できるようにする。

## What Was Done

- `GET /api/v1/auth/csrf/` を追加
- frontend API clientを追加し、`credentials: "include"` とunsafe methodの `X-CSRFToken` 送信に対応
- `AuthProvider` / `useAuth` を追加し、`/api/v1/auth/me/` でログイン状態を確認
- `/login` 画面を追加し、CSRF取得後にSession Auth loginする流れを実装
- `/dashboard` `/prep` `/recipes` `/ingredients` `/settings` をProtected route化
- 共通App Layoutを追加
- スマホは下部ナビ、タブレット横 / PCは約120pxの固定テキストSidebar
- Dashboard APIを表示するDashboard画面を追加
- `/prep` `/recipes` `/ingredients` `/settings` にplaceholder画面を追加
- Figma Makeの雰囲気を参考に、柔らかい背景、カード、余白、2カラムDashboardをTailwindで実装
- API docs / README / handoffを更新

## Key Decisions

- frontendから `shop_id` は送らない。
- Shop scopeと最終的な認可判断はbackendに任せる。
- Session AuthのPOST前には `GET /api/v1/auth/csrf/` でCSRF cookieを取得する。
- API clientのbase URLは `/api/v1` とし、Vite dev proxyを前提にする。
- Auth stateはMVPではReact Context + hooksで管理する。
- RoutingはMVPでは追加dependencyなしの軽量History API実装にした。
- Figma Makeコードは丸ごと移植せず、レイアウト・余白・カード感・サイドバー方針の参考に留めた。
- Placeholderは導線確認用に留め、Recipe / Ingredient / PrepTaskの本格CRUD画面はまだ作り込まない。

## Key Files

- `backend/api/views.py`
- `backend/api/urls.py`
- `backend/api/tests.py`
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
- `docs/api/api-design.md`
- `docs/handoff/archive/frontend-implementation.md`

## Verification

直近の確認結果:

```bash
docker compose run --rm backend python manage.py check
docker compose run --rm backend python manage.py makemigrations --check --dry-run
docker compose run --rm backend python manage.py test

cd frontend
npm run build
npm run lint
```

Result:

- Backend check: pass
- Migration check: pass
- Backend tests: pass
- Frontend build: pass
- Frontend lint: pass

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

1. Prep Today画面を実装する
2. PrepTask APIの一覧を表示し、summaryとtasksを画面に出す
3. `PATCH /api/v1/prep-tasks/{id}/status/` でstatus更新UIを作る
4. 空・読み込み・保存失敗状態を整える
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

## Notes for Next Agent

- Login開発用アカウントは `owner@example.com` / `password`。
- frontendは `shop_id` を送らず、backend responseを表示する。
- API clientは `frontend/src/api/api.ts`。
- Auth stateは `frontend/src/auth/`。
- Dashboard画面は `GET /api/v1/dashboard/` を表示する。
- PrepTask status更新は `PATCH /api/v1/prep-tasks/{id}/status/` を使う。
- Figma Makeのデザインは雰囲気とレイアウト参考で、既存frontend構成に合わせて再実装している。

## Suggested Commit Message

```text
feat(frontend): add auth layout and dashboard foundation
```
