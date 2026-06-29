# Ricetta Handoff Latest

## Date

2026-06-29

## Project

Ricetta

## Status

Frontend branding implemented and backend model diagnostics resolved

## Summary

Ricettaロゴ、空状態イラスト、小さな葉の装飾を主要画面へ追加した。あわせて `backend/api/models.py` のDjango動的属性とnullable値に関するPylance診断を、実行時挙動を変えずに解消した。

## Current Goal

実ブラウザでスマホ幅とタブレット横幅を目視確認し、必要なら画像サイズと余白を微調整する。

## Current State

- サイドバーとモバイルヘッダーにRicettaのシンプルロゴを表示する。
- ログイン画面にコピー入りフルロゴをレスポンシブ表示する。
- Dashboard、Prep Today、Recipe List、Ingredient Listの空状態に既存素材を表示する。
- Recipe / Ingredient検索0件時は、未登録状態と異なる画像・文言を表示する。
- DashboardとRecipe List、Settingsに控えめな葉・チェックリスト装飾を表示する。
- Dashboardの仕込み導線とサイドバーのログアウトは折り返さず1行表示する。
- Docker frontendは `http://localhost:5174`、ローカルViteは `http://localhost:5173`。

## What Was Done

- 実ファイル名に合わせた画像exportを `frontend/src/assets/index.ts` に追加した。
- レスポンシブな共通 `EmptyState` コンポーネントを追加した。
- サイドバーとモバイルヘッダーのテキストロゴを画像へ置き換えた。
- ログイン画面のブランドテキスト3行を `ricetta_logo_full.png` へ置き換えた。
- Prep Today、Recipe List、Ingredient Listの空状態イラストを追加した。
- Dashboardの仕込みカード、よく使うレシピ空状態、期限注意なし表示に装飾を追加した。
- Recipe ListとSettingsの見出し横に小さな葉の装飾を追加した。
- Dashboardボタンを「仕込みを見る」へ短縮し、ログアウトとともに折り返しを禁止した。
- サイドバーロゴを116pxへ拡大し、Dashboard空状態画像を80〜96pxへ縮小した。
- Settingsの葉装飾を28px・opacity 0.65へ調整した。
- `Unit.__str__` と `Ingredient` の原価表示・計算で、nullableな関連とDecimal値を明示的に型絞り込みした。
- `backend/api/tests.py` ではDjango ORMとDRFレスポンスの動的属性に対するPyright誤検知だけをファイル単位で無効化した。
- 装飾画像は `alt=""`、ロゴは `alt="Ricetta"` とした。

## Key Decisions

- 装飾は重要な数字・入力欄・操作ボタンへ重ねず、通常レイアウト内に置く。
- 空状態はスマホで縦並び、`sm` 以上で横並びにする。
- 元画像は加工せず、Tailwindの固定寸法とopacityで表示を調整する。
- ファイル名末尾に ` 1` がある素材は変更せず、assets indexで吸収する。

## Key Files

- `frontend/src/assets/index.ts`
- `frontend/src/components/EmptyState.tsx`
- `frontend/src/components/AppLayout.tsx`
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/pages/PrepTodayPage.tsx`
- `frontend/src/pages/RecipeListPage.tsx`
- `frontend/src/pages/IngredientListPage.tsx`
- `frontend/src/pages/SettingsPage.tsx`
- `backend/api/models.py`
- `backend/api/tests.py`

## Verification

実行済み:

```bash
cd frontend && npm run lint
cd frontend && npm run build
docker compose exec backend python manage.py check
docker compose exec backend python manage.py makemigrations --check --dry-run
docker compose exec backend python manage.py test
/tmp/ricetta-pyright/node_modules/.bin/pyright backend/api/tests.py --pythonversion 3.9
```

Result:

- Frontend lint: pass
- Frontend build: pass
- Vite buildで使用する全PNG assetの解決を確認した。
- Django system check: pass
- Migration check: pass（変更なし）
- Backend tests: pass
- `backend/api/tests.py` Pyright: 0 errors
- in-app browserが利用できず、ログイン画面を含むスマホ幅・タブレット横幅の自動目視確認は未実施。

## Current Product Scope

- Login / logout
- Shop account scope
- Dashboard summary
- Recipe list/detail/create/edit
- Ingredient create/edit and cost mode
- Today's prep list and status update
- Smartphone and tablet landscape layouts
- Settings for Category / Unit management

## Out of Scope for MVP

- Stripe / POS / multi-shop UI
- Automatic inventory deduction and advanced ordering
- Nutrition / HACCP reports
- Advanced role management
- Full prep inventory and expiry alerts
- Drag-and-drop prep operation
- Image upload implementation

## Next Recommended Tasks

1. `http://localhost:5174` でHome、Prep Today、Recipe List、Ingredient List、Settingsを確認する。
2. 390px前後のスマホ幅と1024px前後のタブレット横幅で画像と文章の収まりを確認する。
3. 実データあり・検索0件・完全な空状態をそれぞれ確認する。

## Open Questions

- 画像素材の末尾 ` 1` を将来リネームして統一するか。
- Dashboardの装飾密度を実店舗利用時にさらに下げる必要があるか。

## Notes for Next Agent

- 開発用ログインは `owner@example.com` / `password`。
- 画像importは `frontend/src/assets/index.ts` を経由する。
- 装飾画像は操作要素に重ねず、`pointer-events-none` と `select-none` を維持する。
- API proxyはDocker内 `http://backend:8000`、ローカルViteの既定は `http://localhost:8010`。

## Suggested Commit Message

```text
feat(frontend): add Ricetta branding and empty-state artwork
```
