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

`seed_portfolio_data --reset` は、固定Shop名 `〇〇食堂` で特定したデモShopだけをreset対象にします。

安全方針:

- 実店舗データやデモ対象外Shopを削除しない
- 全Shop削除をしない
- 全User削除をしない
- demo owner / staffユーザーは削除せず再利用する
- `owner@example.com` / `staff@example.com` のpasswordは `password` に更新される
- デモShopに紐づくカテゴリ、単位、材料、レシピ、レシピ材料、工程、仕込みタスク、BoardMemoを再投入する
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
AWS上でcronまたはsystemd timerにより、毎日早朝などに自動リセットする
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

現在は `deny_in_demo()` を用意していますが、既存Viewにはまだ適用していません。

将来的な禁止候補:

- メールアドレス変更
- パスワード変更
- アカウント削除
- demo owner / staffユーザーの削除
- デモ店舗そのものの削除
- 外部連携
- ファイルアップロード

デモ環境で禁止する操作を追加する場合は、各Viewへ直接 `settings.DEMO_MODE` を書かず、`deny_in_demo()` 経由で制御します。

## AWS production env 注意

公開デモ環境では、production相当の設定を使います。

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

## 定期リセット予定

将来的には、cronまたはsystemd timerで毎日早朝などに以下を実行する予定です。

```bash
docker compose exec backend python manage.py seed_portfolio_data --reset
```

実際のcron / systemd timer設定は、別タスクで検討します。

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
