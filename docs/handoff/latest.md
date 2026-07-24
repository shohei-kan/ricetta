# Ricetta Handoff Latest

## Date

2026-07-24

## Project

Ricetta

## Status

Demo deployment docs and env examples organized.

## Summary

AWS公開デモ環境に向けて、`docs/deploy/demo.md` を追加し、デモ運用方針、seed/reset、安全方針、production env注意、公開前チェックを整理した。READMEには短いPublic Demo Environment案内を追加し、`.env.prod.example` にはダミー値のみのproduction例を追加した。既存のデモモード基盤と `seed_portfolio_data --reset` は維持している。

## Current Goal

次はAWS公開デモ用の実運用準備へ進める。具体的には、公開環境の実env値、デモ環境で禁止する操作範囲、定期resetの実行方法を決める。

## Current State

- backendは `DEMO_MODE` を `settings.py` で扱える。
- frontendは `VITE_DEMO_MODE=true` のときだけDemoBannerを表示する。
- `VITE_DEMO_MODE` はViteのbuild時環境変数なので、公開環境ではfrontend build/deploy時に設定する必要がある。
- `backend/api/demo_policy.py` に `deny_in_demo()` を追加済み。ただし既存Viewにはまだ適用していない。
- `seed_portfolio_data --reset` を追加済み。
- reset時は固定Shop名 `〇〇食堂` で特定したデモShopだけを削除する。
- demo owner / staffユーザーは削除せず、再利用・更新する。
- reset後はカテゴリ、単位、材料、レシピ、レシピ材料、工程、仕込みタスク、BoardMemoを再投入する。
- BoardMemo初期値は `玉ねぎ`、`ラップ`、`フライヤー油交換`。
- `docs/deploy/demo.md` に公開デモ運用方針と公開前チェックを整理済み。
- `.env.example` には開発用env、`.env.prod.example` にはproduction向けダミーenvを置いている。
- docsは `product/`、`technical/`、`deploy/`、`decisions/`、`handoff/` に整理済み。

## What Was Done

- `docs/deploy/demo.md` を追加した。
- READMEにPublic Demo Environmentの短い案内を追加した。
- `docs/README.md` にDeployセクションを追加した。
- `.env.prod.example` を追加した。
- `AGENTS.md` のdocs構成例へ `deploy/` を追加した。
- `docs/handoff/archive/release-prep.md` に `2026-07-24 Demo deployment docs` を追記した。

## Key Decisions

- 公開デモ環境は同一コードベースを使い、demo専用ディレクトリやdemo専用ブランチは作らない。
- backendは `DEMO_MODE`、frontendは `VITE_DEMO_MODE` でデモ環境を切り替える。
- 画面上のリセットボタンやデモリセットAPIは現時点では作らない。
- 公開デモではUI上の自由リセットより、cron / systemd timer等による定期リセットを優先する。
- production envにはlocalhostを含めない。
- `.env` や `.env.production` はGit管理しない。
- `.env.prod.example` には実secretや実ドメインを書かない。
- `.env.prod.example` は `.gitignore` の例外に追加し、コミット対象にする。

## Key Files

- `docs/deploy/demo.md`
- `.env.prod.example`
- `.env.example`
- `.gitignore`
- `README.md`
- `docs/README.md`
- `AGENTS.md`
- `backend/api/management/commands/seed_portfolio_data.py`
- `backend/api/tests.py`
- `backend/api/demo_policy.py`
- `docs/handoff/latest.md`
- `docs/handoff/archive/release-prep.md`

## Verification

実行済み:

```bash
docker compose exec backend python manage.py check
docker compose exec backend python manage.py makemigrations --check --dry-run
docker compose exec backend python manage.py test
cd frontend && npm run lint
cd frontend && npm run build
docker compose exec backend python manage.py seed_portfolio_data
docker compose exec backend python manage.py seed_portfolio_data --reset
rg -n "docs/(api|data|planning)/|api/api-design|data/data-model|planning/(concept|mvp-requirements|mvp-roadmap)" AGENTS.md README.md docs/README.md docs/deploy docs/decisions docs/product docs/technical -g '*.md'
git diff --check
```

Result:

- backend check: pass
- makemigrations dry-run: no changes detected
- backend tests: 99 pass
- frontend lint: pass
- frontend build: pass
- `seed_portfolio_data`: pass
- `seed_portfolio_data --reset`: pass
- old docs path references outside handoff history: none
- whitespace check: pass

Manual browser verification:

- 未実施。次にUI確認する場合は、`VITE_DEMO_MODE=true` でログイン後レイアウト上部にDemoBannerが出ることを確認する。

## Current Product Scope

- Login / logout and Shop scope
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
- Advanced role management
- Shop device mode
- Demo reset API / reset button
- cron / systemd timer実設定
- AWSインスタンス作成
- Docker Compose production構成の大幅変更
- Demo-specific branch or duplicated app directories

## Next Recommended Tasks

1. `VITE_DEMO_MODE=true` で実ブラウザを開き、ログイン後にDemoBannerが自然に表示されるか確認する。
2. AWS公開デモ用の実env値を整理する。
3. デモ環境で禁止する操作（メール変更、パスワード変更、アカウント削除、店舗削除など）の範囲を決め、必要なViewに `deny_in_demo()` を適用する。
4. `seed_portfolio_data --reset` の定期実行方法（cron / systemd timer等）を別タスクで検討する。
5. production compose / deploy手順を必要最小限で整理する。

## Open Questions

- デモ環境の自動リセット頻度をどうするか。
- デモ環境でどの操作を許可し、どの操作を禁止するか。
- 公開デモの認証情報を固定表示するか、README/docsだけに記載するか。

## Notes for Next Agent

- `seed_portfolio_data --reset` はローカルDBで実行済み。固定名 `〇〇食堂` のデモShopは初期状態へ再投入されている。
- resetはUserを削除しない。`owner@example.com` / `staff@example.com` は再利用され、passwordは `password` に更新される。
- `backend/api/demo_policy.py` はまだ既存Viewから使っていない。挙動変更は次タスクで明示的に行う。
- `VITE_DEMO_MODE` はViteのbuild時環境変数。
- production envにはlocalhostを含めない。
- docsの旧パス `docs/api/`、`docs/data/`、`docs/planning/` は廃止済み。新規参照は `docs/technical/` または `docs/product/` を使う。
- 開発用ログインは `owner@example.com` / `password`。
- Docker frontendは `http://localhost:5174`。

## Suggested Commit Message

```text
docs(demo): add public demo deployment guide
```
