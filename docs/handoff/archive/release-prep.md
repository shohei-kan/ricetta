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

## 2026-07-28 Public demo launch polish

AWS公開デモ公開前後の仕上げとして、仕込み用Recipeの材料化、production Docker構成、healthcheck、AWS運用docs、favicon / OGP metaを整えた。

### Summary

- Recipeには `recipe_type` を追加済み。`prep` は仕込み用・中間材料、`menu` は販売商品。
- `base_yield_quantity` / `base_yield_unit` はUI上「出来上がり量」として扱い、`cost_summary.material_cost` は出来上がり量1単位あたり原価として計算する。
- Ingredientには `ingredient_type` を追加済み。`raw` は通常材料、`prep_recipe` は仕込み用Recipe由来材料。
- `ingredient_type=prep_recipe` は `source_recipe` を参照し、同一Shopの `recipe_type=prep` のRecipeだけを指定できる。
- Recipe保存時の直接循環は400で止め、原価計算側にも再帰ガードを入れた。
- 公開デモseedでは、仕込み用Recipe「トマトソース」をIngredient「トマトソース」として登録し、販売商品Recipe「カポナータ」の材料に600g使用する。
- パスタRecipeは公開デモseedから削除した。
- ピクルスは公開デモseedでは `menu / 10食分` の販売商品Recipeとして扱う。
- Recipe Formの材料 / 作り方 `＋ 追加` ボタンを1行表示にし、材料削除×のホバー領域とSelectFieldの上下スクロール・上下開きを調整した。
- `docs/deploy/aws-demo-env.md` を追加し、AWS EC2 + Docker Compose公開時のenv、起動、migrate、seed/reset、operation checksを整理した。
- `docker-compose.prod.yml`、production用backend/frontend Dockerfile、Caddyfileを追加し、EC2 1台 + PostgreSQLコンテナ + Gunicorn + Caddy HTTPS構成を用意した。
- backend healthcheckは `/api/v1/health/` を使い、認証不要で `{"status": "ok"}` を返す。
- `docs/deploy/aws-demo-env.md` にEC2上で設定済みの `ricetta-demo-reset.service` / `ricetta-demo-reset.timer` 自動reset運用を追記した。
- resetはEC2起動時 / 再起動時と毎日04:30 JSTに実行される。
- `frontend/public/favicon.png` を追加し、favicon / apple-touch-iconに設定した。
- `frontend/public/ogp.png` を配置し、`frontend/index.html` にtitle、description、OGP、Twitter Card、`noindex, nofollow` を追加した。
- READMEのPublic Demo Environmentに、Ricettaアプリ本体はnoindexで、発見導線はLINTAKE WorksページとGitHub READMEに寄せる方針を追記した。

### Key Files

- `backend/api/models.py`
- `backend/api/migrations/0007_ingredient_ingredient_type_ingredient_source_recipe.py`
- `backend/api/serializers.py`
- `backend/api/costing.py`
- `backend/api/views.py`
- `backend/api/management/commands/seed_portfolio_data.py`
- `backend/api/tests/test_auth.py`
- `backend/api/tests/test_recipes.py`
- `backend/api/tests/test_seed_portfolio_data.py`
- `frontend/src/pages/IngredientFormPage.tsx`
- `frontend/src/pages/RecipeFormPage.tsx`
- `frontend/index.html`
- `frontend/public/favicon.png`
- `frontend/public/ogp.png`
- `docker-compose.prod.yml`
- `backend/Dockerfile.prod`
- `frontend/Dockerfile.prod`
- `frontend/Caddyfile.prod`
- `Caddyfile`
- `.env.prod.example`
- `docs/deploy/demo.md`
- `docs/deploy/aws-demo-env.md`
- `README.md`

### Verification

- migration `0007_ingredient_ingredient_type_ingredient_source_recipe.py` created and migrated.
- backend tests: 149 pass
- backend check: pass
- makemigrations dry-run: no changes detected
- frontend lint: pass
- frontend build: pass
- production compose config: pass
- production compose config with `.env.prod.example`: pass
- production Docker images build: pass
- `seed_portfolio_data --reset`: pass
- seed DB確認: カポナータに `トマトソース / 600.00 g / prep_recipe` が含まれる
- seed DB確認: パスタRecipeなし
- `frontend/public/ogp.png` 存在確認: pass
- `frontend/index.html` のOGP / Twitter Card / robots / description / title確認: pass
- whitespace check: pass

### Manual Checks

- Ingredient一覧で「トマトソース」が仕込み由来材料として表示されることを確認。
- Recipe Formで材料selectに `トマトソース（仕込み）` が表示され、材料として選べることを確認。
- カポナータのRecipe Detailで、材料にトマトソース600gが表示されることを確認。
- カポナータの原価にトマトソース由来Ingredient分が反映されることを確認。
- Recipe Formの材料 / 作り方の `＋ 追加` ボタンが1行表示されることを確認。
- 材料削除×のホバー領域が入力欄に不自然に被らないことを確認。
- Recipe FormのSelectFieldが画面位置に応じて上下へ開き、候補をスクロールできることを確認。

### Decisions

- Recipeを直接RecipeIngredientから参照するのではなく、Ingredientを介して仕込み用Recipeを材料化する。
- `ingredient_type=prep_recipe` のIngredientは、source recipeの1単位あたり原価から材料原価を計算する。
- MVPの単位変換は `kg/g` と `L/ml` の小さなhelperで対応し、Unitモデルに変換係数は追加しない。
- 公開デモdocsでは、仕様説明は `docs/deploy/demo.md`、実運用envメモは `docs/deploy/aws-demo-env.md` に分ける。
- DEMO_MODEはowner/staff権限とは別レイヤー。業務操作は公開デモで触れる状態を保ち、アカウント破壊・店舗破壊・認証情報変更系だけを将来の禁止対象にする。
- AWS公開デモはEC2 1台 + Docker Compose + PostgreSQLコンテナ + Caddyから開始する。
- Ricettaアプリ本体は `noindex, nofollow` とし、発見導線はLINTAKE WorksページとGitHub READMEに寄せる。

### Next

- AWS公開デモへfrontend変更を反映し、`ogp.png`、favicon、共有プレビュー、DemoBanner、owner/staffログインを確認する。
- EC2停止/再開後に `docs/deploy/aws-demo-env.md` のOperation checksとCheck auto resetでproduction composeと自動reset timerを確認する。
