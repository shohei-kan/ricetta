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

## 2026-07-24 Demo deployment docs

AWS公開デモ環境に向けて、デモ運用方針、env example、公開前チェックを整理した。

### Summary

- `docs/deploy/demo.md` を追加した。
- READMEにPublic Demo Environmentの短い案内を追加した。
- `docs/README.md` にDeployセクションを追加した。
- `.env.prod.example` を追加し、production向けのダミー値と公開デモ用コメントを用意した。
- `AGENTS.md` のdocs構成例へ `deploy/` を追加した。
- デモリセットボタン/APIはまだ作らない方針を明記した。
- cron / systemd timerは今後検討する方針を明記した。

### Key Files

- `docs/deploy/demo.md`
- `.env.prod.example`
- `README.md`
- `docs/README.md`
- `AGENTS.md`
- `docs/handoff/latest.md`

### Verification

- 旧docsパスの新規参照なし
- READMEと `docs/deploy/demo.md` のデモ方針に矛盾なし
- env exampleに実secret / 実ドメインなし
- Backend check: pass
- Backend migration dry-run: no changes detected
- Backend tests: 99 pass
- Frontend lint: pass
- Frontend build: pass
- `seed_portfolio_data`: pass
- `seed_portfolio_data --reset`: pass

### Next

- `VITE_DEMO_MODE=true` で実ブラウザのDemoBanner表示を確認する。
- デモ環境で禁止する操作範囲を決め、必要なViewに `deny_in_demo()` を適用する。
- 定期resetの実行方法を別タスクで決める。

## 2026-07-24 Owner staff permission alignment

AWS公開デモ前に、owner / staffの操作範囲を整理した。

### Summary

- Recipe / Ingredient / Shopの管理操作をowner限定にした。
- staffはRecipe / Ingredientを閲覧できるが、作成・編集・削除はAPIで403になる。
- staffはPrepTask作成、PrepTask status変更、BoardMemo追加・チェック、自分の表示名編集を行える。
- frontendではstaffにRecipe / Ingredientの作成・編集導線を表示しない。
- Recipe / Ingredientフォームへstaffが直URLでアクセスした場合、権限メッセージを表示する。
- README、API design、data model、MVP requirements、roadmap、screensのrole説明を更新した。

### Key Files

- `backend/api/shop_scope.py`
- `backend/api/views.py`
- `backend/api/tests.py`
- `frontend/src/pages/RecipeListPage.tsx`
- `frontend/src/pages/RecipeDetailPage.tsx`
- `frontend/src/pages/RecipeFormPage.tsx`
- `frontend/src/pages/IngredientListPage.tsx`
- `frontend/src/pages/IngredientDetailPage.tsx`
- `frontend/src/pages/IngredientFormPage.tsx`
- `docs/technical/api-design.md`

### Verification

- role関連backend tests: 96 pass
- frontend lint: pass
- frontend build: pass
- backend tests: 113 pass
- backend check: pass
- makemigrations dry-run: no changes detected

### Next

- 実ブラウザでowner / staff両方の導線を確認する。
- SettingsのCategory / Unit管理は、この後の `2026-07-24 Category unit permission alignment` でowner限定へ揃えた。
- DEMO_MODE固有の追加禁止操作は `deny_in_demo()` で別途実装する。

## 2026-07-24 Category unit permission alignment

AWS公開デモ前に、Settings内のCategory / Unit管理をowner限定へ揃えた。

### Summary

- Category / UnitのGETはowner / staffとも参照可能なまま維持した。
- Category / Unitの作成・編集・削除はAPI側でowner限定にした。
- staffがCategory / Unit変更APIを直接叩いた場合は403になる。
- Settings画面ではstaffにCategory / Unitの管理フォーム、編集ボタン、削除ボタンを表示しない。
- staffには現在のカテゴリ・単位一覧と、管理はオーナーのみである旨を表示する。
- README、API design、data model、MVP requirements、roadmap、screensのrole説明を更新した。

### Key Files

- `backend/api/views.py`
- `backend/api/tests.py`
- `frontend/src/pages/SettingsPage.tsx`
- `docs/technical/api-design.md`
- `docs/product/screens.md`
- `docs/handoff/latest.md`

### Verification

- Category / Unit backend tests: 17 pass
- frontend lint: pass
- frontend build: pass
- backend tests: 125 pass
- backend check: pass
- makemigrations dry-run: no changes detected
- whitespace check: pass

### Next

- 実ブラウザでowner / staff両方のSettings表示を確認する。
- DEMO_MODE固有の追加禁止操作は `deny_in_demo()` で別途実装する。

## 2026-07-24 Demo login account information

AWS公開デモ向けに、ログイン画面へdemo用ログイン情報とowner / staffの操作範囲を表示するようにした。

### Summary

- `VITE_DEMO_MODE=true` のときだけLoginPageに公開デモ用アカウント情報を表示する。
- `VITE_DEMO_MODE=true` のときだけLoginPageのフォーム初期値に `owner@example.com / password` を入れる。
- owner / staffカードクリックでフォームのemail/passwordを切り替える入力補助を追加した。
- 選択中カードにオレンジ系の枠線、淡い背景、`選択中` ラベルを表示した。
- カード選択は入力補助のみで、自動ログインや自動submitは行わない。
- 通常モードではデモ用ログイン情報を表示せず、フォーム初期値も空にする。
- PC / タブレット幅ではowner / staffカードを横並びにした。
- ownerアカウントとして `owner@example.com / password` を表示する。
- staffアカウントとして `staff@example.com / password` を表示する。
- ownerはレシピ・材料・カテゴリ・単位・店舗情報の編集、仕込み・メモ操作ができることを明記した。
- staffはレシピ・材料・カテゴリ・単位の閲覧、仕込み・メモ操作ができることを明記した。
- staffはレシピ・材料・カテゴリ・単位・店舗情報の編集はできないことを明記した。
- `docs/deploy/demo.md` に公開デモ用ログイン情報、初期入力、カード選択、自動ログインしない方針、権限概要を追記した。

### Key Files

- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/config/demo.ts`
- `docs/deploy/demo.md`
- `docs/handoff/latest.md`

### Verification

- frontend lint: pass
- frontend build: pass
- frontend build with `VITE_DEMO_MODE=true`: pass
- whitespace check: pass

### Next

- 実ブラウザで `VITE_DEMO_MODE=true` のログイン画面表示、ownerアカウント初期入力、owner / staffカード切り替えを確認する。
- 通常起動でログイン画面にデモ用ログイン情報が出ず、初期値も空であることを確認する。
