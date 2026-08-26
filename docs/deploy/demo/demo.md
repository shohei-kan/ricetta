# Ricetta Public Demo Environment

## 基本方針

Ricettaの公開デモ環境は、通常開発と同じコードベースを使います。

demo専用ディレクトリ、demo専用ブランチ、複製されたfrontend/backendは作りません。

環境ごとに分けるものは以下です。

- `.env` などの環境変数
- Docker Compose設定
- production settings
- seed / reset 運用

デモ環境の切り替えには、以下の環境変数を使います。

```env
DEMO_MODE=True
VITE_DEMO_MODE=true
```

backendは `DEMO_MODE`、frontendは `VITE_DEMO_MODE` でデモ環境かどうかを判定します。

## DemoBanner

`VITE_DEMO_MODE=true` のときだけ、ログイン後の共通レイアウト上部にDemoBannerを表示します。

表示文言:

```text
公開デモ環境です。入力内容は定期的に初期化されます。実店舗データではありません。
```

DemoBannerは、閲覧者に以下を伝えるためのものです。

- 公開デモ環境であること
- 入力内容は定期的に初期化されること
- 実店舗データではないこと

注意:

`VITE_DEMO_MODE` はViteのbuild時環境変数です。公開環境では、frontendのbuild/deploy時に `VITE_DEMO_MODE=true` を設定する必要があります。

## 公開デモ用ログイン情報

`VITE_DEMO_MODE=true` のときだけ、ログイン画面に公開デモ用アカウント情報を表示します。

デモモードでは、ログインフォームの初期値に `owner@example.com / password` を入れ、すぐ試せる状態にします。

ログイン画面のowner / staffカードを選択すると、ログインフォームのメールアドレスとパスワードが選択したアカウントに切り替わります。

カード選択は入力補助だけです。自動ログインや自動submitは行わず、ログインは既存の「ログイン」ボタンを押したときだけ実行します。

通常モードでは、ログイン画面にデモ用ログイン情報を表示せず、ログインフォームにもデモ用アカウントを初期入力しません。

デモアカウント:

```text
owner@example.com / password
staff@example.com / password
```

権限概要:

- ownerは、レシピ・材料・カテゴリ・単位・店舗情報の編集、仕込み・メモ操作ができる
- staffは、レシピ・材料・カテゴリ・単位の閲覧、仕込み・メモ操作ができる
- staffは、レシピ・材料・カテゴリ・単位・店舗情報の編集はできない

デモレシピには用途 `recipe_type` があります。

- `prep`: 仕込み用・中間材料
- `menu`: 販売商品

Recipe Detailの原価情報カードは、仕込み用では材料原価のみ、販売商品では材料原価・販売価格・原価率・粗利を表示します。

デモデータには、仕込み用Recipeを材料として使う例も含めます。

- 仕込み用Recipe「トマトソース」
- Ingredient「トマトソース」: `ingredient_type=prep_recipe`
- 販売商品Recipe「カポナータ」

この例では、トマトソースの1kgあたり原価をもとに、カポナータで使う600g分の原価を計算します。カポナータは8食分の販売商品Recipeなので、1食あたり75g相当のトマトソース原価が反映されます。MVPの簡易単位変換は `kg` ↔ `g`、`L` ↔ `ml` に限定します。

ログイン画面では、公開デモ環境であること、入力内容が定期的に初期化されること、実店舗データではないことも明示します。

## デモデータ seed / reset

通常seed:

```bash
docker compose exec backend python manage.py seed_portfolio_data
```

reset:

```bash
docker compose exec backend python manage.py seed_portfolio_data --reset
```

`seed_portfolio_data` は、以下の用途で同じサンプルデータを再現するために使います。

- ローカル撮影用スクリーンショット
- AWS公開デモ
- デモ環境の定期リセット

## resetの安全方針

`seed_portfolio_data --reset` は、APIへ公開しない内部識別子 `demo_key=portfolio-demo` で特定したデモShopだけをreset対象にします。店舗名は変更可能な表示名であり、reset時に既定の `〇〇食堂` へ戻します。

既存環境で `demo_key` が未設定の場合は、既知のdemo owner `owner@example.com` のMembershipから候補Shopを特定します。Membershipが厳密に1件かつactiveなowner roleの場合だけ `demo_key` を付与し、0件、複数件、staff role、inactiveなどの曖昧・矛盾した状態では、新しいShopを作らずエラーで停止します。既にdemo keyがある場合も、既知ownerが存在すれば同じShopへのactive owner Membershipであることを削除前に確認します。完全な新規DBでdemo ownerがまだ存在しない場合は、新しいdemo Shopを作成します。

安全方針:

- 実店舗データやデモ対象外Shopを削除しない
- 全Shop削除をしない
- 全User削除をしない
- demo ShopとMembershipは削除せず再利用する
- demo owner / staffユーザーは削除せず再利用する
- `owner@example.com` / `staff@example.com` のpasswordは `password` に更新される
- デモShopに紐づくカテゴリ、単位、材料、レシピ、レシピ材料、工程、仕込みタスク、BoardMemoを再投入する
- Shop特定からreset、再投入までを1つのtransactionで実行し、途中失敗時は変更前へ戻す
- BoardMemo初期値は `玉ねぎ`、`ラップ`、`フライヤー油交換`
- 既存BoardMemoをseedで再利用する場合、未チェック状態に戻す

reset対象:

- `PrepTask`
- `BoardMemo`
- `RecipeStep`
- `RecipeIngredient`
- `Recipe`
- `Ingredient`
- `Category`
- shop-specific `Unit`
- `Membership`
- `Shop`

標準Unit（`shop=None`）は削除しません。

## リセットボタンを作らない理由

Phase 1:

```text
seed_portfolio_data --reset を用意する
```

Phase 2:

```text
AWS上でsystemd timerにより、毎日04:30 JSTに自動リセットする（運用中）
```

Phase 3:

```text
必要になったら、DEMO_MODE=Trueかつowner限定のリセットAPI / ボタンを検討する
```

現時点では、画面上のリセットボタンやAPIは作りません。

理由:

- 他の閲覧者が操作中にリセットされる可能性がある
- 誤操作が起きやすい
- 公開デモではUI上の自由リセットより定期リセットの方が安全

## demo_policy.py

`backend/api/demo_policy.py` には、デモ環境で禁止したい操作を集約します。

`deny_in_demo()` は、`DEMO_MODE=True` のときにDRFの `PermissionDenied` を送出します。

デモ環境で禁止する操作を追加する場合は、各Viewへ直接 `settings.DEMO_MODE` を書かず、`deny_in_demo()` 経由で制御します。

### DEMO_MODEでも許可する操作

公開デモでは、以下の業務操作は試せる状態を維持します。

- Recipe 作成・編集・削除
- Ingredient 作成・編集・削除
- Category 作成・編集・削除
- Unit 作成・編集・削除
- PrepTask 作成・編集・削除・ステータス変更
- BoardMemo 作成・チェック・戻し
- 自分の表示名変更
- owner / staff の通常role制御

理由:

- 公開デモで操作感を見せるため
- `seed_portfolio_data --reset` で初期状態に戻せるため
- staffは既存role制御で管理操作ができないため

### DEMO_MODEで禁止する操作

現時点では、メールアドレス変更、パスワード変更、アカウント削除、店舗削除、外部連携設定、ファイルアップロードのViewは未実装です。そのため、既存Viewへ新たに `deny_in_demo()` を適用する箇所はありません。

将来、以下の操作を実装する場合は `deny_in_demo()` の適用対象にします。

- メールアドレス変更
- パスワード変更
- アカウント削除
- demo owner / staffユーザーの削除
- デモ店舗そのものの削除
- 外部連携
- ファイルアップロード

現在存在する関連Viewの扱い:

- `auth/me` の表示名変更は、DEMO_MODEでも許可する
- `shop/me` の店舗情報更新は、通常role制御どおりownerのみ許可する
- 店舗削除Viewは未実装
- パスワード変更Viewは未実装
- メールアドレス変更Viewは未実装

## AWS production env 注意

公開デモ環境では、production相当の設定を使います。

AWS EC2 + Docker Composeで実際に設定するenv値と運用コマンドの確認は、[AWS demo env checklist](./aws-demo-env.md) を参照してください。

- `DJANGO_DEBUG=False`
- `DJANGO_SECRET_KEY` は本番用の安全な値にする
- `DJANGO_ALLOWED_HOSTS` は本番ドメインまたはEC2ホストのみにする
- `DJANGO_CSRF_TRUSTED_ORIGINS` は本番URLのみにする
- localhostをproduction envに含めない
- `.env` や `.env.production` はGit管理しない
- `.env.prod.example` にはダミー値のみを書く
- 管理画面を不用意に公開しない
- 実データを入れない
- `seed_portfolio_data` で作成したサンプルデータのみを使用する

## localhost CSRF の注意

localhost の CSRF trusted origins は開発用です。

production env には localhost を含めません。

AWS公開デモでは、本番URLのみを `DJANGO_CSRF_TRUSTED_ORIGINS` に入れます。

## 定期リセット運用

AWS公開デモでは、systemd timerにより毎日04:30 JSTに次のresetを実行します。

```bash
docker compose exec backend python manage.py seed_portfolio_data --reset
```

定期処理は次の順序です。

| Time | Process | Purpose |
| --- | --- | --- |
| 04:10 JST | PostgreSQL backup | reset前のDB状態をS3へ保存 |
| 04:30 JST | Demo reset | 公開デモを初期状態へ戻す |
| 05:00 JST | Backup monitor | S3上の最新backupを確認 |

read-only確認:

```bash
systemctl status ricetta-demo-reset.timer --no-pager
systemctl list-timers --all | grep ricetta
journalctl -u ricetta-demo-reset.service -n 80 --no-pager
```

backupと監視を含む運用の詳細は、[PostgreSQL backup](../backup/postgres-backup.md)と[PostgreSQL backup monitoring](../backup/postgres-monitoring.md)を参照してください。

## 公開前チェック

- `DEMO_MODE=True` をbackend環境に設定している
- `VITE_DEMO_MODE=true` をfrontend build/deploy時に設定している
- `DJANGO_DEBUG=False` になっている
- `DJANGO_SECRET_KEY` が安全な値になっている
- `DJANGO_ALLOWED_HOSTS` に本番ドメインまたはEC2ホストだけが入っている
- `DJANGO_CSRF_TRUSTED_ORIGINS` に本番URLだけが入っている
- production envにlocalhostが入っていない
- `.env` や `.env.production` をGit管理していない
- 実データを入れていない
- `seed_portfolio_data --reset` を実行し、デモデータが初期状態に戻る
- DemoBannerが表示される
