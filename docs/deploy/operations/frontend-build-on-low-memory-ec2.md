# Frontend Build on a Low-memory EC2 Host

## Purpose and scope

このRunbookは、Ricetta公開デモを稼働させている低メモリEC2上で、production frontend imageをsourceから手動buildし、安全にfrontendだけを切り替える手順です。通常のdeploy、production環境変数、Caddy構成は [AWS Demo Environment](../demo/aws-demo-env.md)、障害の初動は [Incident Response Runbook](./incident-response.md) を正本とします。

EC2上での直接buildは例外的な運用です。CPU、memory、disk I/Oを既存serviceと競合し、公開デモの応答遅延やhost全体の不安定化を招く可能性があります。既存frontend containerはbuild済みimageを配信できるため、build前に停止しません。新imageの完成を待ってからfrontendだけを再作成することで、build失敗を公開中のfrontendへ波及させないためです。

恒久対応は、CIまたは別のbuild hostで検証済みartifact / imageを作り、EC2は取得と切り替えだけを行う構成です。一時swapは低メモリhostでの手動buildを支える限定的な緩和策であり、standard構成やpermanent swapにはしません。

## Evidence and interpretation from Issue #91

確認された事実:

- 対象EC2はt3.microで、RAMは約909 MiB、通常運用時はswapなしだった。
- 初回のfrontend buildは `tsc -b && vite build` で長時間進行が見えない状態になった。
- build中も既存frontend containerは稼働し、公開frontendはHTTP 200を維持した。
- 同時間帯に高loadとmemory不足が観測されたが、Kernel OOMの記録は確認されなかった。
- snapd watchdog failureも同時間帯に発生した。
- 1 GiBの一時swapを有効化し、buildを低priority、background、専用logで再実行した。
- 再実行中のswap使用量は最大約260 MiBで、frontend buildは約13秒で成功した。
- 成功後に新旧image IDを比較し、新imageを検出してからfrontendだけを再作成した。
- 切り替え後はrunning imageとlatest imageが一致し、frontendとAPI healthはHTTP 200、`/admin/`はHTTP 404だった。
- backend、db、caddyは再作成されず、正常稼働を維持した。
- 最終確認後にswapを無効化して一時swap fileを削除した。`/etc/fstab`には追加していない。

この結果はmemory pressureが停止の強い原因候補であることを示しますが、根本原因の確定ではありません。一時swap使用後の成功だけでは因果関係を証明できず、cacheや再試行時の条件差もあり得ます。snapd watchdog failureも同時期の事象として記録し、build停止との因果関係は断定しません。

## Conventions

以下はEC2の `/srv/ricetta` で実行します。`.env.prod`はComposeへ渡すだけで、`cat`、`less`、`grep`、`docker compose config`等で内容を表示しません。実行時刻、Git revision、各image ID、log path、health結果をprivateな作業記録へ残し、secretやprivate identifierは転記しません。

```bash
cd /srv/ricetta
```

## 1. Read-only preflight

最初に公開応答、service、host resource、failed unit、OOM記録、Docker使用量、source revisionを確認します。

```bash
date -u '+%Y-%m-%dT%H:%M:%SZ'
git status --short --branch
git rev-parse HEAD

docker compose --env-file .env.prod -f docker-compose.prod.yml ps
uptime
free -h
swapon --show
df -h /
docker system df
docker stats --no-stream \
  --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}'
systemctl --failed --no-pager
sudo journalctl -k --since '30 minutes ago' --no-pager | grep -Ei 'oom|out of memory|killed process' || true

curl -fsS -o /dev/null -w 'frontend=%{http_code}\n' \
  https://ricetta.lintake.net/
curl -fsS -o /dev/null -w 'api_health=%{http_code}\n' \
  https://ricetta.lintake.net/api/v1/health/
curl -sS -o /dev/null -w 'admin=%{http_code}\n' \
  https://ricetta.lintake.net/admin/
```

期待値は、`db` / `backend`が`healthy`、`frontend` / `caddy`が`Up`、frontendとAPI healthが`200`、`/admin/`が`404`です。次の場合はbuildを開始せず、[Incident Response Runbook](./incident-response.md) で先に切り分けます。

- 公開healthまたはCompose serviceが既に異常
- root filesystemに1 GiBのswap file、Docker build layer、logを置く十分な空きがない
- 既存swapがある、同名のswap fileがある、または別のbuildが動いている
- loadやmemory pressureが高い状態で継続している
- worktreeまたはrevisionが意図したdeploy sourceと一致しない

## 2. Preserve the rollback image

build前に、現在稼働中のfrontend image IDとCompose project名を取得し、旧imageへ一時tagを付けます。tagの追加はrunning containerを変更しません。

```bash
FRONTEND_CONTAINER_ID="$(docker compose \
  --env-file .env.prod \
  -f docker-compose.prod.yml \
  ps -q frontend)"

OLD_FRONTEND_IMAGE_ID="$(docker inspect \
  --format '{{.Image}}' \
  "$FRONTEND_CONTAINER_ID")"

FRONTEND_IMAGE_REF="$(docker inspect \
  --format '{{.Config.Image}}' \
  "$FRONTEND_CONTAINER_ID")"

COMPOSE_PROJECT_NAME="$(docker inspect \
  --format '{{ index .Config.Labels "com.docker.compose.project" }}' \
  "$FRONTEND_CONTAINER_ID")"

ROLLBACK_TAG="${COMPOSE_PROJECT_NAME}-frontend:pre-build"
docker image tag "$OLD_FRONTEND_IMAGE_ID" "$ROLLBACK_TAG"

BACKEND_CONTAINER_ID="$(docker compose --env-file .env.prod -f docker-compose.prod.yml ps -q backend)"
DB_CONTAINER_ID="$(docker compose --env-file .env.prod -f docker-compose.prod.yml ps -q db)"
CADDY_CONTAINER_ID="$(docker compose --env-file .env.prod -f docker-compose.prod.yml ps -q caddy)"

printf 'old_frontend_image=%s\nfrontend_image_ref=%s\nrollback_tag=%s\n' \
  "$OLD_FRONTEND_IMAGE_ID" "$FRONTEND_IMAGE_REF" "$ROLLBACK_TAG"
printf 'backend_container=%s\ndb_container=%s\ncaddy_container=%s\n' \
  "$BACKEND_CONTAINER_ID" "$DB_CONTAINER_ID" "$CADDY_CONTAINER_ID"
```

値が空なら続行しません。build失敗時もrunning container、旧image、rollback tagを削除しません。

## 3. Create a temporary 1 GiB swap file

既存swapとpath衝突がないことをpreflightで確認してから、専用pathへ作成します。`chmod 600`を適用し、`/etc/fstab`には追加しません。

```bash
sudo fallocate -l 1G /var/tmp/ricetta-frontend-build.swap
sudo chmod 600 /var/tmp/ricetta-frontend-build.swap
sudo mkswap /var/tmp/ricetta-frontend-build.swap
sudo swapon /var/tmp/ricetta-frontend-build.swap

swapon --show
free -h
```

`fallocate`が利用できないfilesystemでは、その場で別手段へ置き換えず中断します。途中で失敗した場合は、有効化済みかを`swapon --show`で確認してから「Cleanup」の手順を実行します。

## 4. Start the build in the background at low priority

固定のPID fileとlog fileを使うため、同名processが存在しないことを確認してから開始します。`nice -n 10`はCPU scheduling priorityを下げますが、memory上限を設定するものではありません。

```bash
BUILD_LOG=/var/tmp/ricetta-frontend-build.log
BUILD_PID_FILE=/var/tmp/ricetta-frontend-build.pid

test ! -s "$BUILD_PID_FILE"

nohup sh -c '
  echo $$ > /var/tmp/ricetta-frontend-build.pid
  exec nice -n 10 docker compose \
    --env-file .env.prod \
    -f docker-compose.prod.yml \
    build frontend
' >"$BUILD_LOG" 2>&1 &

printf 'launcher_pid=%s\nlog=%s\n' "$!" "$BUILD_LOG"
```

既存frontendは停止せず、そのimageを配信させたままにします。build commandの終了statusはlogだけで推測せず、process終了後にlog末尾とnew image IDの両方で判定します。

## 5. Monitor without attaching to the build

別のSSH sessionから、短い間隔で次を確認します。継続表示が必要な場合も、それぞれを手動で再実行し、公開healthを監視から外しません。

```bash
tail -n 80 /var/tmp/ricetta-frontend-build.log

BUILD_PID="$(cat /var/tmp/ricetta-frontend-build.pid)"
ps -o pid,ppid,ni,stat,etime,%cpu,%mem,cmd -p "$BUILD_PID"

uptime
free -h
swapon --show
docker stats --no-stream \
  --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}'

curl -fsS -o /dev/null -w 'frontend=%{http_code}\n' \
  https://ricetta.lintake.net/
curl -fsS -o /dev/null -w 'api_health=%{http_code}\n' \
  https://ricetta.lintake.net/api/v1/health/
```

併せて、必要な時間範囲だけkernelとsnapdのjournalをread-onlyで確認します。両者の時刻が近くても因果関係を断定しません。

```bash
sudo journalctl -k --since '30 minutes ago' --no-pager
sudo journalctl -u snapd --since '30 minutes ago' --no-pager
```

## 6. Safely interrupt a stalled or harmful build

公開health悪化、memory / swap枯渇、過大なload、logとprocess stateから進行不能が疑われる場合は、新たなfrontendへ切り替えずbuildだけを停止します。

```bash
BUILD_PID="$(cat /var/tmp/ricetta-frontend-build.pid)"
ps -o pid,ppid,ni,stat,etime,%cpu,%mem,cmd -p "$BUILD_PID"
kill -TERM "$BUILD_PID"
```

少し待って同じ`ps`で終了を確認します。PIDが別processへ再利用される危険を避けるため、表示されたcommandが対象buildであることを確認せずkillしません。`kill -KILL`、Docker daemon restart、Compose stackの停止、`docker system prune`へ安易に進みません。停止後も現在稼働中のcontainer、旧image、rollback tagを残し、公開healthを再確認してCleanupへ進みます。

## 7. Guard the frontend switch with image IDs

build processが終了し、log末尾に成功が確認できた場合だけnew imageを調べます。Composeが生成するfrontend imageの`latest` tagと、running containerのimageを比較します。

```bash
tail -n 120 /var/tmp/ricetta-frontend-build.log

LATEST_FRONTEND_IMAGE_ID="$(docker image inspect \
  --format '{{.Id}}' \
  "$FRONTEND_IMAGE_REF")"

printf 'running_before=%s\nlatest=%s\n' \
  "$OLD_FRONTEND_IMAGE_ID" "$LATEST_FRONTEND_IMAGE_ID"

test -n "$LATEST_FRONTEND_IMAGE_ID"
test "$LATEST_FRONTEND_IMAGE_ID" != "$OLD_FRONTEND_IMAGE_ID"
```

IDが同じ、空、またはbuild成功が確認できない場合は切り替えません。現在稼働中のfrontendを停止・削除せず、調査またはCleanupへ進みます。

新imageが確認できた場合だけ、依存serviceを起動・再作成しないオプションでfrontendを切り替えます。

```bash
docker compose \
  --env-file .env.prod \
  -f docker-compose.prod.yml \
  up -d --no-deps --force-recreate frontend

LATEST_FRONTEND_IMAGE_ID="$(docker image inspect \
  --format '{{.Id}}' \
  "$FRONTEND_IMAGE_REF")"
```

## 8. Verify the switch and public behavior

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml ps

NEW_FRONTEND_CONTAINER_ID="$(docker compose \
  --env-file .env.prod \
  -f docker-compose.prod.yml \
  ps -q frontend)"

RUNNING_FRONTEND_IMAGE_ID="$(docker inspect \
  --format '{{.Image}}' \
  "$NEW_FRONTEND_CONTAINER_ID")"

printf 'running_after=%s\nlatest=%s\n' \
  "$RUNNING_FRONTEND_IMAGE_ID" "$LATEST_FRONTEND_IMAGE_ID"
test "$RUNNING_FRONTEND_IMAGE_ID" = "$LATEST_FRONTEND_IMAGE_ID"

test "$(docker compose --env-file .env.prod -f docker-compose.prod.yml ps -q backend)" = "$BACKEND_CONTAINER_ID"
test "$(docker compose --env-file .env.prod -f docker-compose.prod.yml ps -q db)" = "$DB_CONTAINER_ID"
test "$(docker compose --env-file .env.prod -f docker-compose.prod.yml ps -q caddy)" = "$CADDY_CONTAINER_ID"

curl -fsS -o /dev/null -w 'frontend=%{http_code}\n' \
  https://ricetta.lintake.net/
curl -fsS -o /dev/null -w 'api_health=%{http_code}\n' \
  https://ricetta.lintake.net/api/v1/health/
curl -sS -o /dev/null -w 'admin=%{http_code}\n' \
  https://ricetta.lintake.net/admin/
```

確認項目:

- Composeで`db` / `backend`が`healthy`、`frontend` / `caddy`が`Up`
- running frontend image IDとlatest frontend image IDが一致
- frontendがHTTP 200
- `/api/v1/health/`がHTTP 200
- `/admin/`が意図どおりHTTP 404
- backend、db、caddyのcontainer ID / uptimeが切り替え前から変わっていない

## Rollback

切り替え後にfrontendだけの異常が出た場合は、保存したrollback tagをComposeのfrontend image名へ戻し、frontendだけを再作成します。backend、db、caddyは対象にしません。

```bash
docker image tag \
  "${COMPOSE_PROJECT_NAME}-frontend:pre-build" \
  "$FRONTEND_IMAGE_REF"

docker compose \
  --env-file .env.prod \
  -f docker-compose.prod.yml \
  up -d --no-deps --force-recreate frontend

LATEST_FRONTEND_IMAGE_ID="$(docker image inspect \
  --format '{{.Id}}' \
  "$FRONTEND_IMAGE_REF")"
```

その後、「Verify the switch and public behavior」と同じCompose、image ID、frontend、API、`/admin/`確認を行います。rollbackが必要な間は旧imageとrollback tagを削除しません。DB migrationを伴わないfrontend限定手順なので、database rollbackは行いません。

## Cleanup

build終了後は、成功・失敗・中断のいずれでも一時swapを確実に無効化して削除します。まずbuild processが終了していることと、swap使用量が回収可能であることを確認します。`swapoff`がmemory不足で失敗した場合はfileを削除せず、負荷を下げてavailable memoryを確保してから再試行します。

```bash
free -h
swapon --show

sudo swapoff /var/tmp/ricetta-frontend-build.swap
swapon --show
sudo rm /var/tmp/ricetta-frontend-build.swap

sudo test ! -e /var/tmp/ricetta-frontend-build.swap
grep -F '/var/tmp/ricetta-frontend-build.swap' /etc/fstab || true
rm -f /var/tmp/ricetta-frontend-build.pid
```

`swapon --show`に一時swapがなく、fileが存在せず、`/etc/fstab`にentryがないことを確認します。build logは調査・作業記録が不要になってから削除します。rollback tagは新frontendの安定確認とrollback期間終了後に別途整理し、無差別なimage cleanupは行いません。
