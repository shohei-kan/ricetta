# Ricetta Handoff Latest

## Date

2026-07-24

## Project

Ricetta

## Status

Demo mode foundation added; backend Pylance typing cleanup completed.

## Summary

AWS公開デモ環境に向けて、同一コードベースを環境変数でデモ表示へ切り替える最小基盤を追加した。あわせて直前に `backend/api/views.py` のPylance型エラーを、実行時挙動を変えずに型補助で解消した。

## Current Goal

次はAWS公開デモ用の運用準備へ進める。具体的には、デモ用seed/reset方針、公開環境の環境変数、デプロイ手順、デモ環境で禁止する操作の範囲を決める。

## Current State

- backendは `DEMO_MODE` を `settings.py` で扱える。
- frontendは `VITE_DEMO_MODE=true` のときだけデモバナーを表示する。
- DemoBannerはログイン後の共通レイアウト上部に表示される。
- `backend/api/demo_policy.py` に `deny_in_demo()` を追加済み。
- 今回は既存Viewへ `deny_in_demo()` を適用していないため、通常機能の挙動は変えていない。
- `.env.example` に `DEMO_MODE=False` と `VITE_DEMO_MODE=false` を追加済み。
- `backend/api/views.py` はPylance向けにDRF `Request` / `query_params` / serializer `validated_data` / PrepTask summary集計の型を整理済み。
- 既存のPrep Today / BoardMemo / Recipe / Dashboard機能は維持している。

## What Was Done

- `backend/ricetta/settings.py` に `DEMO_MODE = env_bool('DEMO_MODE', False)` を追加した。
- `backend/api/demo_policy.py` を追加し、デモ環境で将来の禁止操作に使う `deny_in_demo()` を用意した。
- `frontend/src/config/demo.ts` を追加し、`VITE_DEMO_MODE === 'true'` で `isDemoMode` を判定するようにした。
- `frontend/src/components/demo/DemoBanner.tsx` を追加した。
- `frontend/src/components/AppLayout.tsx` に `DemoBanner` を組み込んだ。
- `.env.example` にbackend/frontendのデモモード環境変数を追記した。
- `backend/api/views.py` のPylance型エラーを型注釈・helper・castで解消した。

## Key Decisions

- デモ版は別ディレクトリ、別ブランチ、複製コードを作らず、同じコードベースを環境変数で切り替える。
- `DEMO_MODE` / `VITE_DEMO_MODE` のデフォルトは通常モード（false）。
- デモ環境で禁止する操作は、各Viewに直接 `settings.DEMO_MODE` を書かず、`deny_in_demo()` 経由にする。
- 今回はseed reset、リセットAPI、リセットボタン、docs/deploy整備はまだ行わない。

## Key Files

- `backend/ricetta/settings.py`
- `backend/api/demo_policy.py`
- `backend/api/views.py`
- `frontend/src/config/demo.ts`
- `frontend/src/components/demo/DemoBanner.tsx`
- `frontend/src/components/AppLayout.tsx`
- `.env.example`

## Verification

実行済み:

```bash
PYTHONPYCACHEPREFIX=/private/tmp/ricetta-pycache python3 -m compileall backend/api/views.py
docker compose exec backend python manage.py check
docker compose exec backend python manage.py makemigrations --check --dry-run
docker compose exec backend python manage.py test
cd frontend && npm run lint
cd frontend && npm run build
cd frontend && VITE_DEMO_MODE=true npm run build
git diff --check
```

Result:

- backend compile: pass
- backend check: pass
- makemigrations dry-run: no changes detected
- backend tests: 98 pass
- frontend lint: pass
- frontend build: pass
- frontend build with `VITE_DEMO_MODE=true`: pass
- whitespace check: pass

Manual browser verification:

- 未実施。次にUI確認する場合は、`VITE_DEMO_MODE=true` でログイン後レイアウト上部にバナーが出ることを確認する。

## Current Product Scope

- Login / logout and Shop scope
- Recipe / Ingredient / Prep Today / Dashboard / Settings / Account
- Active Prep Today board and direct PrepTask creation
- BoardMemo as lightweight whiteboard memo under Prep Today columns
- Smartphone, tablet landscape, and PC layouts
- Demo mode foundation via environment variables

## Out of Scope for MVP

- Stripe / Checkout / Billing portal
- POS integration
- Automatic inventory deduction
- Advanced ordering
- Multi-shop management UI
- Advanced role management
- Shop device mode
- Demo reset API / reset button
- Demo-specific branch or duplicated app directories

## Next Recommended Tasks

1. `VITE_DEMO_MODE=true` で実ブラウザを開き、ログイン後にDemoBannerが自然に表示されるか確認する。
2. AWS公開デモ用の環境変数一覧を整理する。
3. `seed_portfolio_data --reset` を公開デモ向けに安全に使える形へ調整する。
4. デモ環境で禁止する操作（メール変更、パスワード変更、アカウント削除、店舗削除など）の範囲を決め、必要なViewに `deny_in_demo()` を適用する。
5. `docs/deploy/demo.md` など、デモ公開手順のドキュメント整備を行う。

## Open Questions

- デモ環境の自動リセット頻度をどうするか。
- デモ環境でどの操作を許可し、どの操作を禁止するか。
- 公開デモの認証情報を固定表示するか、README/docsだけに記載するか。

## Notes for Next Agent

- 現在の未コミット差分には、今回のデモモード基盤に加えて、直前の `backend/api/views.py` Pylance型エラー対応が含まれる。
- `backend/api/demo_policy.py` はまだ既存Viewから使っていない。挙動変更は次タスクで明示的に行う。
- `VITE_DEMO_MODE` はViteのbuild時環境変数なので、公開環境ではfrontend build/deploy時に設定する必要がある。
- `.env` は編集していない。実環境値はGit管理外で設定する。
- 開発用ログインは `owner@example.com` / `password`。
- Docker frontendは `http://localhost:5174`。

## Suggested Commit Message

```text
feat(demo): add environment-driven demo mode foundation
```
