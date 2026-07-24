# Ricetta Handoff Latest

## Date

2026-07-24

## Project

Ricetta

## Status

Safe portfolio seed reset added for demo operations.

## Summary

AWS公開デモ環境の定期初期化に向けて、`seed_portfolio_data` 管理コマンドへ `--reset` を追加した。reset時は固定名 `〇〇食堂` で特定したデモShopだけを削除し、サンプルデータを毎回同じ状態へ再投入する。通常seed、デモモード基盤、docs配置整理、Pylance型エラー対応も現在の未コミット作業に含まれる。

## Current Goal

次はAWS公開デモ用の運用準備へ進める。具体的には、公開環境の環境変数、デプロイ手順、デモ環境で禁止する操作の範囲、定期resetの実行方法を決める。

## Current State

- backendは `DEMO_MODE` を `settings.py` で扱える。
- frontendは `VITE_DEMO_MODE=true` のときだけDemoBannerを表示する。
- `backend/api/demo_policy.py` に `deny_in_demo()` を追加済み。ただし既存Viewにはまだ適用していない。
- `seed_portfolio_data --reset` を追加済み。
- reset時は固定Shop名 `〇〇食堂` で特定したデモShopだけを削除する。
- demo owner / staffユーザーは削除せず、再利用・更新する。
- reset後はカテゴリ、単位、材料、レシピ、レシピ材料、工程、仕込みタスク、BoardMemoを再投入する。
- BoardMemo初期値は `玉ねぎ`、`ラップ`、`フライヤー油交換`。
- 既存BoardMemoをseedで再利用する場合、`archived_at=None` に戻し、フィールドが存在すれば `is_archived=False` / `archived_by=None` も反映する。
- docsは `product/` と `technical/` へ整理済み。旧 `docs/api/`、`docs/data/`、`docs/planning/` は廃止済み。

## What Was Done

- `seed_portfolio_data` に `--reset` オプションを追加した。
- `--reset` 時の削除対象をデモShopに限定する安全コメントを追加した。
- `--reset` 時はownerの既存active Membershipを再利用せず、デモShopを作り直すようにした。
- 通常seedでBoardMemo初期メモを冪等に作成するようにした。
- 既存BoardMemo再利用時に、将来の `is_archived` / `archived_by` フィールドが存在しても未チェック状態へ戻るようにした。
- 管理コマンドテストへ、通常seedのBoardMemo作成、`--reset` 2回連続実行、他Shop保護を追加した。
- 今回のrelease prep履歴を `docs/handoff/archive/release-prep.md` へ追記した。

## Key Decisions

- デモ版は別ディレクトリ、別ブランチ、複製コードを作らず、同じコードベースを環境変数で切り替える。
- `--reset` の削除処理では全Shop削除や全User削除をしない。
- reset対象は固定名で特定したデモShopに紐づくデータだけにする。
- Userは削除せず再利用する。`owner@example.com` / `staff@example.com` のpasswordは `password` に更新される。
- 今回はリセットAPI、リセットボタン、cron / systemd timer設定、docs/deploy整備はまだ行わない。
- handoffは毎回 `latest.md` を更新し、古くなった内容は大分類ごとのarchiveへ `## YYYY-MM-DD タイトル` で追記する。

## Key Files

- `backend/api/management/commands/seed_portfolio_data.py`
- `backend/api/tests.py`
- `backend/ricetta/settings.py`
- `backend/api/demo_policy.py`
- `frontend/src/config/demo.ts`
- `frontend/src/components/demo/DemoBanner.tsx`
- `frontend/src/components/AppLayout.tsx`
- `.env.example`
- `docs/handoff/latest.md`
- `docs/handoff/archive/release-prep.md`

## Verification

実行済み:

```bash
docker compose exec backend python manage.py test api.tests.PortfolioSeedCommandTests
docker compose exec backend python manage.py check
docker compose exec backend python manage.py makemigrations --check --dry-run
docker compose exec backend python manage.py test
docker compose exec backend python manage.py seed_portfolio_data
docker compose exec backend python manage.py seed_portfolio_data --reset
docker compose exec backend python manage.py seed_portfolio_data --reset
docker compose exec backend python manage.py test api.tests.PortfolioSeedCommandTests
```

Result:

- backend seed command tests: 3 pass
- backend check: pass
- makemigrations dry-run: no changes detected
- backend tests: 99 pass
- `seed_portfolio_data`: pass
- `seed_portfolio_data --reset`: pass
- `seed_portfolio_data --reset` second run: pass

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

## Out of Scope for MVP

- Stripe / Checkout / Billing portal
- POS integration
- Automatic inventory deduction
- Advanced ordering
- Multi-shop management UI
- Advanced role management
- Shop device mode
- Demo reset API / reset button
- cron / systemd timer設定
- Demo-specific branch or duplicated app directories

## Next Recommended Tasks

1. `VITE_DEMO_MODE=true` で実ブラウザを開き、ログイン後にDemoBannerが自然に表示されるか確認する。
2. AWS公開デモ用の環境変数一覧を整理する。
3. デモ環境で禁止する操作（メール変更、パスワード変更、アカウント削除、店舗削除など）の範囲を決め、必要なViewに `deny_in_demo()` を適用する。
4. `seed_portfolio_data --reset` の定期実行方法（cron / systemd timer等）を別タスクで検討する。
5. `docs/deploy/demo.md` など、デモ公開手順のドキュメント整備を行う。

## Open Questions

- デモ環境の自動リセット頻度をどうするか。
- デモ環境でどの操作を許可し、どの操作を禁止するか。
- 公開デモの認証情報を固定表示するか、README/docsだけに記載するか。

## Notes for Next Agent

- `seed_portfolio_data --reset` はローカルDBで実行済み。固定名 `〇〇食堂` のデモShopは初期状態へ再投入されている。
- resetはUserを削除しない。`owner@example.com` / `staff@example.com` は再利用され、passwordは `password` に更新される。
- reset時はownerの既存active Membershipを再利用しないため、デモShop以外をリネーム・削除しない。
- `backend/api/demo_policy.py` はまだ既存Viewから使っていない。挙動変更は次タスクで明示的に行う。
- `VITE_DEMO_MODE` はViteのbuild時環境変数なので、公開環境ではfrontend build/deploy時に設定する必要がある。
- docsの旧パス `docs/api/`、`docs/data/`、`docs/planning/` は廃止済み。新規参照は `docs/technical/` または `docs/product/` を使う。
- 開発用ログインは `owner@example.com` / `password`。
- Docker frontendは `http://localhost:5174`。

## Suggested Commit Message

```text
feat(seed): add safe portfolio demo reset
```
