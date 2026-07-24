# Ricetta Handoff Latest

## Date

2026-07-24

## Project

Ricetta

## Status

Owner / staff master data permissions aligned for the public demo.

## Summary

AWS公開デモ前の確認として、owner / staffの操作範囲をマスタデータまで整理した。Recipe / Ingredient / Category / Unit / Shopの管理操作はowner限定にし、staffは参照、Prep Todayの仕込みタスク操作、BoardMemo操作、自分の表示名編集を行える状態にした。frontendではstaffにRecipe / Ingredient / Settingsの管理導線を出さず、必要な参照一覧は維持している。

## Current Goal

次はAWS公開デモ用の実運用準備へ進める。具体的には、公開環境の実env値、デモ環境で追加禁止する操作範囲、定期resetの実行方法、実ブラウザでのowner/staff手動確認を詰める。

## Current State

- backendは `DEMO_MODE` を `settings.py` で扱える。
- frontendは `VITE_DEMO_MODE=true` のときだけDemoBannerを表示する。
- `backend/api/demo_policy.py` に `deny_in_demo()` を追加済み。ただし既存Viewにはまだ適用していない。
- `seed_portfolio_data --reset` を追加済み。固定Shop名 `〇〇食堂` のデモShopだけを削除し、サンプルデータを再投入する。
- ownerはRecipe / Ingredient / Category / Unit / Shop情報の作成・編集・削除ができる。
- staffはRecipe / Ingredient / Category / Unitを閲覧・参照できるが、作成・編集・削除はAPIで403になる。
- staffはPrepTask作成、PrepTask status変更、BoardMemo追加・チェック、自分の表示名編集ができる。
- Accountではstaffに店舗情報編集フォームを出さない既存UIを維持している。
- Recipe / Ingredientの一覧・詳細・フォームはstaff向け表示制御を追加済み。
- SettingsではstaffにCategory / Unitの管理フォーム、編集ボタン、削除ボタンを出さず、参照一覧と権限メッセージを表示する。
- docsは `product/`、`technical/`、`deploy/`、`decisions/`、`handoff/` に整理済み。

## What Was Done

- `get_current_owner_membership()` に権限エラーメッセージを渡せるようにした。
- `RecipeViewSet` の create / update / delete をowner限定にした。
- `IngredientViewSet` の create / update / delete をowner限定にした。
- `CategoryViewSet` の create / update / delete をowner限定にした。
- `UnitViewSet` の create / update / delete をowner限定にした。
- backendテストにowner/staff権限ケースを追加した。
- Recipe List / Detail / Formでstaff向けに作成・編集導線を非表示またはガードした。
- Ingredient List / Detail / Formでstaff向けに作成・編集導線を非表示またはガードした。
- Settingsでstaff向けにCategory / Unit管理導線を非表示にした。
- README、API design、data model、MVP requirements、roadmap、screensのrole説明を更新した。
- `docs/handoff/archive/release-prep.md` に今回のrelease prep履歴を追記した。

## Key Decisions

- DEMO_MODEとowner/staff権限は別物として扱う。
- 通常のrole制御として、Recipe / Ingredient / Category / Unit / Shopの管理操作はowner限定にする。
- staffには現場運用に必要なPrepTask / BoardMemo操作を許可する。
- frontendの表示制御だけに頼らず、API側でもstaffの管理操作を403で止める。
- メール変更、パスワード変更、アカウント削除、店舗削除、デモリセットAPI / ボタンは今回実装しない。

## Key Files

- `backend/api/shop_scope.py`
- `backend/api/views.py`
- `backend/api/tests.py`
- `frontend/src/pages/SettingsPage.tsx`
- `frontend/src/pages/RecipeListPage.tsx`
- `frontend/src/pages/RecipeDetailPage.tsx`
- `frontend/src/pages/RecipeFormPage.tsx`
- `frontend/src/pages/IngredientListPage.tsx`
- `frontend/src/pages/IngredientDetailPage.tsx`
- `frontend/src/pages/IngredientFormPage.tsx`
- `README.md`
- `docs/technical/api-design.md`
- `docs/technical/data-model.md`
- `docs/product/mvp-requirements.md`
- `docs/product/mvp-roadmap.md`
- `docs/product/screens.md`
- `docs/handoff/latest.md`
- `docs/handoff/archive/release-prep.md`

## Verification

実行済み:

```bash
cd frontend
npm run lint
npm run build
cd ..
docker compose exec backend python manage.py test
docker compose exec backend python manage.py check
docker compose exec backend python manage.py makemigrations --check --dry-run
git diff --check
```

Result:

- frontend lint: pass
- frontend build: pass
- backend tests: 125 pass
- backend check: pass
- makemigrations dry-run: no changes detected
- whitespace check: pass

Manual browser verification:

- 未実施。次にUI確認する場合は、owner / staff両方でログインし、Recipe / Ingredient / Settings管理導線、Account店舗編集、PrepTask / BoardMemo操作を確認する。

## Current Product Scope

- Login / logout and Shop scope
- owner / staff role control for MVP operations
- Recipe / Ingredient / Prep Today / Dashboard / Settings / Account
- Active Prep Today board and direct PrepTask creation
- BoardMemo as lightweight whiteboard memo under Prep Today columns
- Smartphone, tablet landscape, and PC layouts
- Demo mode foundation via environment variables
- Safe portfolio demo seed reset
- Public demo operation docs

## Out of Scope for MVP

- Stripe / Checkout / Billing portal
- POS integration
- Automatic inventory deduction
- Advanced ordering
- Multi-shop management UI
- Advanced role management beyond owner / staff
- Shop device mode
- Demo reset API / reset button
- cron / systemd timer実設定
- AWSインスタンス作成
- Docker Compose production構成の大幅変更
- Demo-specific branch or duplicated app directories

## Next Recommended Tasks

1. ブラウザでowner / staff両方の導線と403挙動を手動確認する。
2. `VITE_DEMO_MODE=true` でDemoBannerが自然に表示されるか確認する。
3. AWS公開デモ用の実env値を整理する。
4. デモ環境で追加禁止する操作（メール変更、パスワード変更、アカウント削除、店舗削除など）の範囲を決め、必要なViewに `deny_in_demo()` を適用する。
5. `seed_portfolio_data --reset` の定期実行方法（cron / systemd timer等）を別タスクで検討する。

## Open Questions

- デモ環境の自動リセット頻度をどうするか。
- デモ環境で通常role制御に加えて、どの操作を追加禁止するか。
- 公開デモの認証情報を固定表示するか、README/docsだけに記載するか。

## Notes for Next Agent

- `owner@example.com` / `password` と `staff@example.com` / `password` は `seed_portfolio_data` で再作成・更新される。
- staffはRecipe / Ingredientのフォーム直URLにアクセスしても、frontendでは権限メッセージを表示し、APIでも403になる。
- staffはSettingsを開いてCategory / Unit一覧を参照できるが、管理フォーム、編集、削除は表示されない。APIでもCategory / Unit変更操作は403になる。
- Shop情報更新は既存通りowner限定。表示名更新はowner / staff両方可能。
- `backend/api/demo_policy.py` はまだ既存Viewから使っていない。DEMO_MODE固有制限は次タスクで明示的に行う。
- production envにはlocalhostを含めない。
- docsの旧パス `docs/api/`、`docs/data/`、`docs/planning/` は廃止済み。新規参照は `docs/technical/` または `docs/product/` を使う。
- Docker frontendは `http://localhost:5174`。

## Suggested Commit Message

```text
feat(auth): enforce owner-only master data management
```
