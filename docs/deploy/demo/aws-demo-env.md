# AWS Demo Environment Variables

公開デモの基本方針やデモアカウント、DemoBanner、seed/resetの詳細は [Public demo environment](./demo.md) を参照してください。

このファイルは、AWS公開時のenv設定と運用コマンドに絞った実務メモです。

## Scope

このメモの対象:

- AWS EC2 + Docker ComposeでRicetta公開デモを動かすためのenv整理
- DBはまずEC2内PostgreSQLコンテナ
- 将来RDS分離を検討
- 実値ではなくダミー値のみ記載
- secretや本物のドメインは書かない

現在の公開デモ想定ドメインは `ricetta.lintake.net` です。docsでは必要に応じて実ドメインを参照してよいですが、`.env.prod.example` は `ricetta.example.com` のままにします。

このメモでは、既存のDjango settings / frontend実装で参照している環境変数に合わせます。

現時点では、以下のような変数は既存実装で読んでいないため、env例には含めません。

- `DJANGO_ENV`
- `CORS_ALLOWED_ORIGINS`
- `SESSION_COOKIE_SECURE`
- `CSRF_COOKIE_SECURE`

これらはenv変数ではなく、`DJANGO_DEBUG=False` のときDjango settingsが自動的に有効化します。

## Backend `.env.prod`

AWS公開デモ用backend envの例です。

```env
DJANGO_SECRET_KEY=replace-me-with-production-secret
DJANGO_DEBUG=False
DEMO_MODE=True

DJANGO_ALLOWED_HOSTS=ricetta.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://ricetta.example.com
CADDY_SITE_ADDRESS=ricetta.example.com

POSTGRES_DB=ricetta
POSTGRES_USER=ricetta
POSTGRES_PASSWORD=replace-me

VITE_DEMO_MODE=true
```

注意:

- production envにlocalhostを含めない
- `DJANGO_SECRET_KEY` は必ず本番用に差し替える
- `DJANGO_DEBUG=False` にする
- 公開デモでは `DEMO_MODE=True` にする
- `.env.prod` はGit管理しない
- 変数名は既存settingsや `.env.prod.example` と矛盾させない
- 既存実装で使っていない変数は、envだけに勝手に追加しない
- `CADDY_SITE_ADDRESS` はCaddyが受ける公開ドメインを指定する
- 実運用では `CADDY_SITE_ADDRESS=ricetta.lintake.net` のように実ドメインへ差し替える
- `POSTGRES_HOST` と `POSTGRES_PORT` はproduction Composeが `db` / `5432` を固定指定するため、`.env.prod` には記載しない
- production Composeは上記10変数のいずれかが未設定ならconfig段階で失敗する
- Djangoも `DJANGO_DEBUG=False` のとき必須値の空文字、開発用値、明らかなplaceholderを拒否する
- `.env.prod.example` のplaceholderは項目を示すためのものであり、Djangoのproduction起動には使えない

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
docker compose --env-file .env.prod -f docker-compose.prod.yml config
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
docker compose --env-file .env.prod -f docker-compose.prod.yml exec backend python manage.py migrate
docker compose --env-file .env.prod -f docker-compose.prod.yml exec backend python manage.py seed_portfolio_data --reset
```

注意:

- production公開デモでは `docker-compose.prod.yml` を使う
- backendはgunicornで起動する
- frontendはbuild済みdistを静的配信する
- frontendはReact Routerの直接URLアクセス・リロードに対応するため、frontend側CaddyでSPA fallbackする
- 外向きCaddyが80/443を受け、`/api/*` と `/static/*` をbackendへ、それ以外をfrontendへreverse proxyする
- `/admin` と `/admin/*` は公開デモ運用で使わないため、Caddyが404を返して外部公開しない
- 素の `docker compose -f docker-compose.prod.yml config` はローカル `.env` を読む可能性があるため、実値確認には `--env-file .env.prod` を使う
- ここでは大幅なcompose変更はしない
- 初回公開前に必ずmigrate後にseed/resetを実行する

## Operation checks

EC2起動後やデプロイ後は、以下でproduction composeの状態と主要ログを確認します。

```bash
cd /srv/ricetta
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
docker compose --env-file .env.prod -f docker-compose.prod.yml logs --tail=80 caddy
docker compose --env-file .env.prod -f docker-compose.prod.yml logs --tail=80 backend
```

期待する状態:

- `backend` が `healthy`
- `db` が `healthy`
- `frontend` が `Up`
- `caddy` が `Up`
- Caddyログに証明書エラーがない
- backendログで `/api/v1/health/` が `200`

## Production Security Settings

`DJANGO_DEBUG=False` では、以下を有効にします。

- `SESSION_COOKIE_SECURE=True`
- `CSRF_COOKIE_SECURE=True`
- `SECURE_SSL_REDIRECT=True`
- `SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO", "https")`
- `SECURE_HSTS_SECONDS=3600`
- `SECURE_HSTS_INCLUDE_SUBDOMAINS=False`
- `SECURE_HSTS_PRELOAD=False`

Caddyの標準動作でbackendへ `X-Forwarded-Proto` が渡り、Djangoが元のHTTPS requestをsecure requestとして認識できる構成にします。Docker内部のbackend health checkはCaddyを通らないHTTP接続のため、headerを明示してSSL redirectを避け、`/api/v1/health/` の200を確認します。

HSTSは誤設定時の影響を限定するため、まず1時間から開始します。`includeSubDomains` と `preload` は他のsubdomainや長期的なbrowser登録へ影響するため有効化しません。

DRFはSession Authenticationだけを使い、Basic Authenticationは受け付けません。unsafe methodは引き続きCSRF tokenを必要とします。login APIはCaddy 1段を信頼するIP単位の `5/minute` throttleを使い、認証失敗はuser状態にかかわらずgeneric errorを返します。

### Deploy verification

```bash
cd /srv/ricetta
docker compose --env-file .env.prod -f docker-compose.prod.yml config --quiet
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
docker compose --env-file .env.prod -f docker-compose.prod.yml exec backend python manage.py check
docker compose --env-file .env.prod -f docker-compose.prod.yml exec backend python manage.py check --deploy
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
curl -I https://ricetta.lintake.net/api/v1/health/
curl -I https://ricetta.lintake.net/admin/
```

確認項目:

- backend / dbがhealthy
- health endpointがHTTPSで200
- `/admin` が404
- Session loginとlogoutが成功
- Secure属性付きSession / CSRF cookieが発行される
- owner / staff権限差が維持される
- HTTPアクセスがHTTPSへredirectされる
- responseの `Strict-Transport-Security` が `max-age=3600`

### Rollback

問題がある場合は、直前のコミットへコードを戻してproduction imageを再buildします。`.env.prod` を開発用値やplaceholderに戻して起動を回避してはいけません。

Secure Cookie有効化後はHTTP経由でsessionを使えないため、rollback確認もHTTPSで行います。HSTSはbrowserに最大1時間保持されるため、コードを戻しても直ちにHTTP接続の検証に切り替えられない点に注意します。

## Stop / restart operation

普段コストを抑えるため、応募前まではEC2を停止運用します。

EC2停止:

- AWS Console
- EC2
- Instances
- `ricetta-demo`
- Instance state
- Stop instance

EC2再開後の確認:

```bash
ssh -i ~/.ssh/ricetta-demo-key.pem ubuntu@ricetta.lintake.net
cd /srv/ricetta
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

`restart: unless-stopped` のため、EC2再起動後は各コンテナが自動起動する想定です。

## Healthcheck note

production composeではbackend healthcheckに `/api/v1/health/` を使います。

このendpointは認証不要で、未ログインでもHTTP 200と軽量レスポンスを返します。

```json
{"status": "ok"}
```

backendログで `GET /api/v1/health/` が `200` なら正常です。DB書き込みなどの重い処理は行いません。

## Manual reset command

```bash
cd /srv/ricetta
docker compose --env-file .env.prod -f docker-compose.prod.yml exec backend python manage.py seed_portfolio_data --reset
```

このコマンドで行うこと:

- デモデータを初期状態に戻す
- `owner@example.com` / `staff@example.com` のpasswordを `password` に戻す
- 内部識別子 `demo_key=portfolio-demo` のShopを対象にする
- 店舗表示名を既定の `〇〇食堂` に戻す
- 実店舗データを入れない前提で使う

初回migration後、既存demo Shopに `demo_key` がない場合は、`owner@example.com` のMembershipが厳密に1件かつactiveなowner roleのときだけ自動移行します。0件、複数件、role不一致、inactive、または既存demo keyとMembership先の不一致ではfail closedで停止するため、ShopやMembershipの状態を確認してから再実行してください。systemd service / timerの実行コマンド自体は変更ありません。

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
- [ ] `docker compose --env-file .env.prod -f docker-compose.prod.yml config` が通る
- [ ] HTTPSでアクセスできる
- [ ] `/admin` が404を返す
- [ ] `/api/v1/health/` がHTTPSで200を返す
- [ ] Session / CSRF cookieにSecure属性が付く
- [ ] HSTSが `max-age=3600`、includeSubDomains / preloadなしで返る
- [ ] 実店舗データを入れていない
- [ ] `seed_portfolio_data --reset` 実行済み
- [ ] owner / staffでログイン確認済み
- [ ] DEMO_MODEで禁止する破壊系Viewが未実装、または `deny_in_demo()` 適用済み

## Demo auto reset

公開デモでは、デモデータを自動resetします。

resetには `seed_portfolio_data --reset` を使います。

現在EC2に設定している内容:

- reset script: `/usr/local/bin/ricetta-demo-reset.sh`
- systemd service: `ricetta-demo-reset.service`
- systemd timer: `ricetta-demo-reset.timer`
- server timezone: `Asia/Tokyo`

自動resetのタイミング:

- EC2起動時 / 再起動時
- 毎日 04:30 JST

resetで起きること:

- 公開デモデータを初期状態に戻す
- `owner@example.com` / `staff@example.com` のpasswordを `password` に戻す
- デモ中に入力されたデータはresetで消える

timer確認結果の例:

```text
Wed 2026-07-29 04:30:00 JST ... ricetta-demo-reset.timer ricetta-demo-reset.service
```

手動実行成功時のログ例:

```text
[ricetta-demo-reset] starting at ...
[ricetta-demo-reset] waiting for backend...
[ricetta-demo-reset] backend is ready
Seeded portfolio demo data. Accounts: owner@example.com / password, staff@example.com / password
[ricetta-demo-reset] completed at ...
```

### Current reset script

現在EC2に設定しているスクリプト例です。

```bash
#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/srv/ricetta"
COMPOSE="docker compose --env-file .env.prod -f docker-compose.prod.yml"

cd "$APP_DIR"

echo "[ricetta-demo-reset] starting at $(date -Is)"

$COMPOSE up -d

echo "[ricetta-demo-reset] waiting for backend..."

for i in $(seq 1 30); do
  if $COMPOSE exec -T backend python manage.py check >/dev/null 2>&1; then
    echo "[ricetta-demo-reset] backend is ready"
    break
  fi

  if [ "$i" -eq 30 ]; then
    echo "[ricetta-demo-reset] backend did not become ready" >&2
    exit 1
  fi

  sleep 5
done

$COMPOSE exec -T backend python manage.py seed_portfolio_data --reset

echo "[ricetta-demo-reset] completed at $(date -Is)"
```

### Current systemd service

現在EC2に設定しているsystemd service例です。

```ini
[Unit]
Description=Reset Ricetta demo data
Wants=network-online.target docker.service
After=network-online.target docker.service

[Service]
Type=oneshot
User=ubuntu
WorkingDirectory=/srv/ricetta
ExecStart=/usr/local/bin/ricetta-demo-reset.sh
TimeoutStartSec=300

[Install]
WantedBy=multi-user.target
```

### Current systemd timer

現在EC2に設定しているsystemd timer例です。

```ini
[Unit]
Description=Run Ricetta demo reset daily

[Timer]
OnCalendar=*-*-* 04:30:00
Persistent=true
Unit=ricetta-demo-reset.service

[Install]
WantedBy=timers.target
```

### Check auto reset

自動reset設定の確認コマンドです。

```bash
systemctl is-enabled ricetta-demo-reset.service
systemctl is-enabled ricetta-demo-reset.timer
systemctl status ricetta-demo-reset.timer
systemctl list-timers --all | grep ricetta
journalctl -u ricetta-demo-reset.service -n 80 --no-pager
```

期待する状態:

- service: `enabled`
- timer: `enabled`
- timer: `active (waiting)`
- next trigger: `04:30 JST`
- journalに `Seeded portfolio demo data` が出る

### Manual reset via systemd

手動でsystemd経由のresetを実行したい場合:

```bash
sudo systemctl start ricetta-demo-reset.service
journalctl -u ricetta-demo-reset.service -n 80 --no-pager
```

### Disable auto reset

自動resetを止める場合:

```bash
sudo systemctl disable --now ricetta-demo-reset.timer
sudo systemctl disable ricetta-demo-reset.service
```

再有効化する場合:

```bash
sudo systemctl enable ricetta-demo-reset.service
sudo systemctl enable --now ricetta-demo-reset.timer
```

### Timezone note

timezone確認:

```bash
timedatectl
```

現在の公開デモEC2は `Asia/Tokyo` に設定済みです。
