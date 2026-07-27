# Ricetta Handoff Latest

## Date

2026-07-24

## Project

Ricetta

## Status

Backend API tests split by feature.

## Summary

`backend/api/tests.py` に集まっていたAPIテストを、機能単位の `backend/api/tests/` パッケージへ分割した。テスト内容・期待値・API挙動は変更せず、共通ヘルパー `ApiTestCase` を `tests/base.py` に移動し、Auth / Shop / Category / Unit / Ingredient / Recipe / PrepTask / BoardMemo / Dashboard / seed commandごとにファイルを分けた。

## Current Goal

次はAWS公開デモ用の実運用準備へ進める。具体的には、公開環境の実env値、デモ環境で追加禁止する操作範囲、定期resetの実行方法、実ブラウザでのowner/staff導線確認を詰める。

## Current State

- backendは `DEMO_MODE` を `settings.py` で扱える。
- frontendは `VITE_DEMO_MODE=true` のときだけDemoBannerと公開デモ用ログイン情報を表示する。
- `VITE_DEMO_MODE=true` のとき、LoginPageのフォーム初期値は `owner@example.com / password`。
- demoアカウントカードクリックはフォーム値の切り替えのみ。自動ログインや自動submitはしない。
- 通常モードではLoginPageにデモ用ログイン情報を表示せず、フォーム初期値も空にする。
- `backend/api/demo_policy.py` に `deny_in_demo()` を追加済み。ただし既存Viewにはまだ適用していない。
- `seed_portfolio_data --reset` を追加済み。固定Shop名 `〇〇食堂` のデモShopだけを削除し、サンプルデータを再投入する。
- ownerはRecipe / Ingredient / Category / Unit / Shop情報の作成・編集・削除ができる。
- staffはRecipe / Ingredient / Category / Unitを閲覧・参照できるが、作成・編集・削除はAPIで403になる。
- staffはPrepTask作成、PrepTask status変更、BoardMemo追加・チェック、自分の表示名編集ができる。
- backend APIテストは `backend/api/tests/` に機能単位で分割済み。

## What Was Done

- `backend/api/tests.py` を削除し、`backend/api/tests/` パッケージへ移行した。
- `ApiTestCase` と共通fixture / helperを `backend/api/tests/base.py` に移動した。
- 各テストクラスを機能別ファイルへ移動した。
- 各ファイルで必要なimportを整理した。
- テスト内容・期待値・API実装は変更していない。
- `docs/handoff/archive/backend-foundation.md` に今回の履歴を追記した。

## Key Decisions

- テスト分割は構成整理のみとし、API挙動やテスト期待値は変えない。
- 共通のログイン、Shop、Recipe、Ingredient、PrepTask作成helperは `ApiTestCase` に集約し続ける。
- `backend/api/tests.py` ではなく `backend/api/tests/` パッケージをDjango test discoveryの対象にする。
- DEMO_MODEとowner/staff権限は別物として扱う。
- デモ環境固有の追加制限は、今後必要なViewへ `deny_in_demo()` を適用して実装する。

## Key Files

- `backend/api/tests/base.py`
- `backend/api/tests/test_auth.py`
- `backend/api/tests/test_shop_scope.py`
- `backend/api/tests/test_categories.py`
- `backend/api/tests/test_units.py`
- `backend/api/tests/test_ingredients.py`
- `backend/api/tests/test_recipes.py`
- `backend/api/tests/test_prep_tasks.py`
- `backend/api/tests/test_board_memos.py`
- `backend/api/tests/test_dashboard.py`
- `backend/api/tests/test_seed_portfolio_data.py`
- `docs/handoff/latest.md`
- `docs/handoff/archive/backend-foundation.md`

## Verification

実行済み:

```bash
docker compose exec backend python manage.py test
docker compose exec backend python manage.py check
docker compose exec backend python manage.py makemigrations --check --dry-run
git diff --check
```

Result:

- backend tests: 125 pass
- backend check: pass
- makemigrations dry-run: no changes detected
- whitespace check: pass

Manual browser verification:

- 今回はbackend test構成整理のみのため未実施。

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
- Demo login account information on LoginPage

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

1. owner / staff両方でログインし、導線と403挙動を実ブラウザで手動確認する。
2. AWS公開デモ用の実env値を整理する。
3. デモ環境で追加禁止する操作（メール変更、パスワード変更、アカウント削除、店舗削除など）の範囲を決め、必要なViewに `deny_in_demo()` を適用する。
4. `seed_portfolio_data --reset` の定期実行方法（cron / systemd timer等）を別タスクで検討する。

## Open Questions

- デモ環境の自動リセット頻度をどうするか。
- デモ環境で通常role制御に加えて、どの操作を追加禁止するか。

## Notes for Next Agent

- `backend/api/tests.py` は削除済み。新規backend APIテストは `backend/api/tests/test_*.py` に追加する。
- 共通fixture / helperが必要な場合は `backend/api/tests/base.py` の `ApiTestCase` を使う。
- `owner@example.com` / `password` と `staff@example.com` / `password` は `seed_portfolio_data` で再作成・更新される。
- `VITE_DEMO_MODE=true` のとき、LoginPageにdemoアカウント情報を表示し、フォーム初期値にはownerアカウントを入れる。
- `VITE_DEMO_MODE` はViteのbuild時環境変数。公開環境ではfrontend build/deploy時に設定する必要がある。
- `backend/api/demo_policy.py` はまだ既存Viewから使っていない。DEMO_MODE固有制限は次タスクで明示的に行う。
- production envにはlocalhostを含めない。
- docsの旧パス `docs/api/`、`docs/data/`、`docs/planning/` は廃止済み。新規参照は `docs/technical/` または `docs/product/` を使う。
- Docker frontendは `http://localhost:5174`。

## Suggested Commit Message

```text
refactor(tests): split backend api tests by feature
```
