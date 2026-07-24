# Ricetta Handoff Latest

## Date

2026-07-24

## Project

Ricetta

## Status

Docs directory structure cleaned up; demo mode foundation added.

## Summary

docs配下を読む目的ごとに整理し、`product/` と `technical/` へ主要ドキュメントを集約した。handoff運用として、`latest.md` は毎回更新し、過去分は大分類ごとのarchiveへ日付・タイトル付きで積み重ねる方針も明記済み。AWS公開デモ環境に向けたデモモード基盤と、直前の `backend/api/views.py` Pylance型エラー対応も現在の作業状態として保持している。

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
- `docs/handoff/archive/index.md` にhandoff運用ルールを明記済み。
- `docs/README.md` を追加し、docs全体の入口を用意済み。
- `docs/product/` に企画・要件・ロードマップ・画面・UI方針を集約済み。
- `docs/technical/` にAPI設計とデータモデルを集約済み。
- 直近の公開デモ作業は `docs/handoff/archive/release-prep.md` へ追記済み。
- 直近のPrep Today / BoardMemo作業は `docs/handoff/archive/frontend-implementation.md` へ追記済み。
- 今回のdocs配置整理は `docs/handoff/archive/planning-and-docs.md` へ追記済み。
- 既存のPrep Today / BoardMemo / Recipe / Dashboard機能は維持している。

## What Was Done

- `backend/ricetta/settings.py` に `DEMO_MODE = env_bool('DEMO_MODE', False)` を追加した。
- `backend/api/demo_policy.py` を追加し、デモ環境で将来の禁止操作に使う `deny_in_demo()` を用意した。
- `frontend/src/config/demo.ts` を追加し、`VITE_DEMO_MODE === 'true'` で `isDemoMode` を判定するようにした。
- `frontend/src/components/demo/DemoBanner.tsx` を追加した。
- `frontend/src/components/AppLayout.tsx` に `DemoBanner` を組み込んだ。
- `.env.example` にbackend/frontendのデモモード環境変数を追記した。
- `backend/api/views.py` のPylance型エラーを型注釈・helper・castで解消した。
- `docs/handoff/archive/index.md` にhandoff運用ルールを追加した。
- `docs/handoff/archive/release-prep.md` にDemo mode foundationのarchive entryを追加した。
- `docs/handoff/archive/frontend-implementation.md` にPrep Today board memo and compact cardsのarchive entryを追加した。
- `docs/api/api-design.md` を `docs/technical/api-design.md` へ移動した。
- `docs/data/data-model.md` を `docs/technical/data-model.md` へ移動した。
- `docs/planning/` 配下の企画・要件・ロードマップを `docs/product/` へ移動した。
- `docs/README.md` を追加した。
- README、AGENTS、decisions、handoff archiveの参照パスを新配置へ更新した。
- `docs/handoff/archive/planning-and-docs.md` にDocs directory structure cleanupのarchive entryを追加した。

## Key Decisions

- デモ版は別ディレクトリ、別ブランチ、複製コードを作らず、同じコードベースを環境変数で切り替える。
- `DEMO_MODE` / `VITE_DEMO_MODE` のデフォルトは通常モード（false）。
- デモ環境で禁止する操作は、各Viewに直接 `settings.DEMO_MODE` を書かず、`deny_in_demo()` 経由にする。
- 今回はseed reset、リセットAPI、リセットボタン、docs/deploy整備はまだ行わない。
- handoffは毎回 `latest.md` を更新し、古くなった内容は大分類ごとのarchiveへ `## YYYY-MM-DD タイトル` で追記する。
- docsは `product/` = 何を作るか、`technical/` = どう実装するか、`decisions/` = なぜ決めたか、`handoff/` = 今どこか、で読む目的ごとに分ける。

## Key Files

- `backend/ricetta/settings.py`
- `backend/api/demo_policy.py`
- `backend/api/views.py`
- `frontend/src/config/demo.ts`
- `frontend/src/components/demo/DemoBanner.tsx`
- `frontend/src/components/AppLayout.tsx`
- `.env.example`
- `docs/README.md`
- `docs/product/`
- `docs/technical/`
- `docs/handoff/latest.md`
- `docs/handoff/archive/index.md`
- `docs/handoff/archive/planning-and-docs.md`
- `docs/handoff/archive/release-prep.md`
- `docs/handoff/archive/frontend-implementation.md`
- `docs/decisions/0005-documentation-structure.md`
- `README.md`
- `AGENTS.md`

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
git diff --check docs/handoff/latest.md docs/handoff/archive/index.md docs/handoff/archive/release-prep.md docs/handoff/archive/frontend-implementation.md
rg -n "docs/(api|data|planning)/|api/api-design|data/data-model|planning/(concept|mvp-requirements|mvp-roadmap)" AGENTS.md README.md docs/decisions docs/product docs/technical -g '*.md'
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
- handoff docs whitespace check: pass
- old docs path references outside handoff history: none

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
- docsの旧パス `docs/api/`、`docs/data/`、`docs/planning/` は廃止済み。新規参照は `docs/technical/` または `docs/product/` を使う。
- handoff更新時は `latest.md` を短く現在地へ保ち、過去分は既存archiveの大分類へ追記する。
- archiveへ追記する場合は `## YYYY-MM-DD タイトル` 形式で区切る。
- `backend/api/demo_policy.py` はまだ既存Viewから使っていない。挙動変更は次タスクで明示的に行う。
- `VITE_DEMO_MODE` はViteのbuild時環境変数なので、公開環境ではfrontend build/deploy時に設定する必要がある。
- `.env` は編集していない。実環境値はGit管理外で設定する。
- 開発用ログインは `owner@example.com` / `password`。
- Docker frontendは `http://localhost:5174`。

## Suggested Commit Message

```text
docs: reorganize documentation structure
```
