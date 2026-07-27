# AWS Demo Environment Variables

公開デモの基本方針やデモアカウント、DemoBanner、seed/resetの詳細は [docs/deploy/demo.md](./demo.md) を参照してください。

このファイルは、AWS公開時のenv設定と運用コマンドに絞った実務メモです。

## Scope

このメモの対象:

- AWS EC2 + Docker ComposeでRicetta公開デモを動かすためのenv整理
- DBはまずEC2内PostgreSQLコンテナ
- 将来RDS分離を検討
- 実値ではなくダミー値のみ記載
- secretや本物のドメインは書かない

このメモでは、既存のDjango settings / frontend実装で参照している環境変数に合わせます。

現時点では、以下のような変数は既存実装で読んでいないため、env例には含めません。

- `DJANGO_ENV`
- `CORS_ALLOWED_ORIGINS`
- `SESSION_COOKIE_SECURE`
- `CSRF_COOKIE_SECURE`

必要になったら、settings実装と `.env.prod.example` を揃えてから追加します。

## Backend `.env.prod`

AWS公開デモ用backend envの例です。

```env
DJANGO_SECRET_KEY=replace-me-with-production-secret
DJANGO_DEBUG=False
DEMO_MODE=True

DJANGO_ALLOWED_HOSTS=ricetta.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://ricetta.example.com

POSTGRES_DB=ricetta
POSTGRES_USER=ricetta
POSTGRES_PASSWORD=replace-me
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

注意:

- production envにlocalhostを含めない
- `DJANGO_SECRET_KEY` は必ず本番用に差し替える
- `DJANGO_DEBUG=False` にする
- 公開デモでは `DEMO_MODE=True` にする
- `.env.prod` はGit管理しない
- 変数名は既存settingsや `.env.prod.example` と矛盾させない
- 既存実装で使っていない変数は、envだけに勝手に追加しない

## Database `.env.db`

PostgreSQLコンテナ用envの例です。

```env
POSTGRES_DB=ricetta
POSTGRES_USER=ricetta
POSTGRES_PASSWORD=replace-me
```

注意:

- `.env.db` はGit管理しない
- DBパスワードは本番用にする
- バックアップは別タスクで検討する

## Frontend build env

公開デモ用frontend buildでは、以下を設定します。

```env
VITE_DEMO_MODE=true
```

注意:

- `VITE_DEMO_MODE` はViteのbuild時環境変数
- build後にサーバーのenvだけ変えても反映されない
- 公開デモ用frontend image / buildでは `VITE_DEMO_MODE=true` を渡す必要がある
- API URL envは現時点の既存実装にないため、ここには記載しない

## Initial deploy commands

AWSサーバー上での初回起動時に実行する想定コマンドです。

```bash
docker compose up -d --build
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py seed_portfolio_data --reset
```

注意:

- composeファイル名がproduction用に分かれている場合は、既存構成に合わせて読み替える
- ここでは大幅なcompose変更はしない
- 初回公開前に必ずmigrate後にseed/resetを実行する

## Manual reset command

```bash
docker compose exec backend python manage.py seed_portfolio_data --reset
```

このコマンドで行うこと:

- デモデータを初期状態に戻す
- `owner@example.com` / `staff@example.com` のpasswordを `password` に戻す
- 固定Shop名 `〇〇食堂` を対象にする
- 実店舗データを入れない前提で使う

## Demo account smoke test

公開後に確認すること:

- `owner@example.com / password` でログインできる
- `staff@example.com / password` でログインできる
- DemoBannerが表示される
- ログイン画面にデモアカウントカードが表示される
- staffでRecipe / Ingredient / Category / Unit / Shop情報の編集導線が出ない
- DEMO_MODEでもRecipe / Ingredient / Category / Unit / PrepTask / BoardMemo操作を試せる
- カポナータにトマトソース由来Ingredientが含まれる
- トマトソースは仕込み由来Ingredientとして表示される

## Security checklist

- [ ] `DJANGO_DEBUG=False`
- [ ] `DEMO_MODE=True`
- [ ] `VITE_DEMO_MODE=true` でfrontendをbuild
- [ ] `DJANGO_SECRET_KEY` は本番用
- [ ] `DJANGO_ALLOWED_HOSTS` は公開ドメインのみ
- [ ] `DJANGO_CSRF_TRUSTED_ORIGINS` はhttps公開URLのみ
- [ ] production envにlocalhostを含めない
- [ ] `.env.prod` / `.env.db` はGit管理しない
- [ ] HTTPSでアクセスできる
- [ ] 実店舗データを入れていない
- [ ] `seed_portfolio_data --reset` 実行済み
- [ ] owner / staffでログイン確認済み
- [ ] DEMO_MODEで禁止する破壊系Viewが未実装、または `deny_in_demo()` 適用済み

## Reset automation future task

定期resetは今後の課題です。

候補:

- cron
- systemd timer
- GitHub Actions + SSH
- 手動resetから開始

現時点では、手動resetで開始します。
