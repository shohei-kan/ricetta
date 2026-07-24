# Release Prep Handoff Archive

MVP公開前の確認、デプロイ、リリース準備に関するhandoffをここに追記する。

## 2026-07-24 Demo mode foundation

AWS公開デモ環境へ向けて、同一コードベースを環境変数でデモ表示へ切り替える最小基盤を追加した。

### Summary

- backend settingsへ `DEMO_MODE` を追加した。
- frontendへ `VITE_DEMO_MODE` 判定用の `isDemoMode` configを追加した。
- ログイン後の共通レイアウト上部へ `DemoBanner` を追加した。
- `backend/api/demo_policy.py` に `deny_in_demo()` を追加した。
- `.env.example` に `DEMO_MODE=False` と `VITE_DEMO_MODE=false` を追加した。
- seed reset、デモリセットAPI、デモリセットボタン、docs/deploy本格整備は未実装。

### Decisions

- デモ版は別ディレクトリ、別ブランチ、複製コードを作らず、環境変数で切り替える。
- デモ環境で禁止する操作は、各Viewへ直接 `settings.DEMO_MODE` を書かず、`deny_in_demo()` 経由にする。
- 今回は `deny_in_demo()` を既存Viewへ適用せず、通常挙動を変えない。

### Key Files

- `backend/ricetta/settings.py`
- `backend/api/demo_policy.py`
- `frontend/src/config/demo.ts`
- `frontend/src/components/demo/DemoBanner.tsx`
- `frontend/src/components/AppLayout.tsx`
- `.env.example`

### Verification

- Backend check: pass
- Backend migration dry-run: no changes detected
- Backend tests: 98 pass
- Frontend lint: pass
- Frontend build: pass
- Frontend build with `VITE_DEMO_MODE=true`: pass

### Next

- `VITE_DEMO_MODE=true` で実ブラウザのバナー表示を確認する。
- AWS公開デモ用の環境変数とデプロイ手順を整理する。
- `seed_portfolio_data --reset` の安全な公開デモ運用を検討する。
- デモ環境で禁止する操作範囲を決める。

## 2026-07-24 Safe portfolio seed reset

AWS公開デモ環境の定期初期化に向けて、`seed_portfolio_data` 管理コマンドへ `--reset` を追加した。

### Summary

- `python manage.py seed_portfolio_data --reset` を追加した。
- `--reset` なしの通常seedは従来通り作成・更新のみ行う。
- reset時は固定Shop名 `〇〇食堂` で特定したデモShopだけを削除し、seedを再投入する。
- demo owner / staffユーザーは削除せず、既存ユーザーを再利用・更新する。
- reset対象は `PrepTask`、`BoardMemo`、`RecipeStep`、`RecipeIngredient`、`Recipe`、`Ingredient`、`Category`、shop-specific `Unit`、`Membership`、`Shop`。
- 標準Unit（`shop=None`）は削除しない。
- BoardMemoの初期メモとして `玉ねぎ`、`ラップ`、`フライヤー油交換` を作成する。
- 削除処理の近くに、全Shop削除禁止・デモShop限定・AWS公開デモ定期リセット用途の安全コメントを残した。

### Decisions

- デモ対象Shopの特定は、既存seedの固定値であるShop名 `〇〇食堂` を使う。
- `--reset` 時はownerの既存active Membershipを再利用しない。デモShopを作り直し、Membershipを再作成する。
- User削除は行わない。ログイン情報を維持し、実データ巻き込みリスクを下げる。

### Key Files

- `backend/api/management/commands/seed_portfolio_data.py`
- `backend/api/tests.py`

### Verification

- Backend seed command tests: 3 pass
- Backend check: pass
- Backend migration dry-run: no changes detected
- Backend tests: 99 pass
- `seed_portfolio_data`: pass
- `seed_portfolio_data --reset`: pass
- `seed_portfolio_data --reset` second run: pass

### Next

- AWS公開デモ用の環境変数とデプロイ手順を整理する。
- デモ環境で禁止する操作範囲を決め、必要なViewに `deny_in_demo()` を適用する。
- 定期実行方法（cron / systemd timer等）は別タスクで検討する。
