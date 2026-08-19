# Ricetta Incident Response Runbook

## Purpose and scope

Ricetta公開デモで障害や異常を検知したときに、最初の5〜10分で影響範囲を把握し、症状から原因を切り分け、安全な一次対応を選ぶためのRunbookです。

本書の責務はread-only調査、証拠保全、一次対応、エスカレーション判断です。詳細な監視設定、backup、restore、demo reset、secret更新、再構築手順は各正本へ委譲します。

対象環境:

- AWS EC2 1台
- Docker Compose production stack: `db` / `backend` / `frontend` / `caddy`
- PostgreSQL 15 container
- Caddy HTTPS reverse proxy
- CloudWatch / SNS / Amazon Q Developer / Slack通知
- systemdによるPostgreSQL backup、backup監視、demo reset

この文書にAccount ID、Instance ID、ARN、Email、Slack workspace/channel ID、secret実値を記録しません。`.env.prod`やsystemd用secret fileの内容を表示するコマンドも掲載しません。

## Related sources of truth

| Responsibility | Source of truth |
| --- | --- |
| EC2 metrics、Alarm、CloudWatch Agent、一次対応 | [EC2 Resource Monitoring](../monitoring/ec2-resource-monitoring.md) |
| AWS請求異常 | [AWS Cost Monitoring and Billing Guardrails](../monitoring/aws-cost-monitoring.md) |
| backup / recovery方針 | [Backup and Restore](../backup/backup-and-restore.md) |
| PostgreSQL backup | [PostgreSQL Backup](../backup/postgres-backup.md) |
| PostgreSQL restore | [PostgreSQL Restore](../backup/postgres-restore.md) |
| backup監視 / Slack通知 | [PostgreSQL Backup Monitoring](../backup/postgres-monitoring.md) |
| production Compose / Caddy / demo reset | [AWS Demo Environment](../demo/aws-demo-env.md) |
| demo dataとreset安全方針 | [Public Demo Environment](../demo/demo.md) |
| secret復旧 / 更新 | [Secret Management](../secret-management.md) |
| Temporary EC2 rebuild | GitHub Issue #69（将来のrebuild Runbook入口） |

## Incident response principles

1. 変更前に現在時刻、症状、検知方法、影響範囲、直前のdeployや設定変更を記録する。
2. read-only確認と証拠保全を優先し、ログや状態を確認せずに再起動しない。
3. 同じ失敗コマンドを繰り返さない。再試行する場合は、前回から変わった条件と目的を記録する。
4. secret、credential、`.env.prod`の内容、private identifierをterminal出力、Issue、Slack、Docsへ貼らない。
5. ログ共有前にtoken、cookie、Authorization header、Email、IP、resource identifier等を確認し、必要な範囲だけredactする。
6. security侵害の疑いは通常障害から分け、credential保全・失効判断と監査証跡保全を優先する。
7. restore、rollback、demo reset、EC2 rebuildは一次切り分けの代わりに実行しない。判断基準を満たした場合だけ正本へ進む。
8. `docker compose down -v`、volume削除、DB初期化、無差別なDocker cleanupは本Runbookの手順として実行しない。

## Command safety labels

| Label | Meaning |
| --- | --- |
| **READ-ONLY** | 状態・ログ・応答を確認する。通常は対象の永続状態を変更しない |
| **STATE-CHANGING** | process、container、data、設定、credential、外部resourceの状態を変更する |
| **DESTRUCTIVE** | data消失や復旧困難につながる。通常の一次対応では実行しない |

`docker compose exec`自体はcontainer内でcommandを実行する仕組みです。掲載した`check`や接続確認はread-onlyですが、引数をmigration、reset、shell内のwrite処理へ変えるとstate-changingになるため、そのまま応用しません。

## First 5–10 minutes

### 1. Start an incident record

ローカルMacまたはEC2で時刻だけを取得します。

```bash
date -u '+%Y-%m-%dT%H:%M:%SZ'
```

- **Location:** ローカルMacまたはEC2
- **Safety:** READ-ONLY
- **Purpose:** 比較可能なUTCの基準時刻を残す
- **Expected:** `2026-08-20T01:23:45Z`形式
- **Look for:** Slack、CloudWatch、deploy、journalの時刻とtimezone差を混同しない

Issueやprivate incident noteへ、症状、検知方法、影響範囲、直前の変更を記録します。secretやprivate identifierは記載しません。

### 2. Check public HTTPS paths from outside EC2

```bash
curl -fsS -o /dev/null -w 'frontend=%{http_code}\n' \
  https://ricetta.lintake.net/

curl -fsS -o /dev/null -w 'api_health=%{http_code}\n' \
  https://ricetta.lintake.net/api/v1/health/

curl -sS -o /dev/null -w 'admin=%{http_code}\n' \
  https://ricetta.lintake.net/admin/
```

- **Location:** ローカルMac
- **Safety:** READ-ONLY
- **Purpose:** DNS、TLS、Caddy、upstreamを通る外部経路を確認する
- **Options:** `-f`はHTTP 400以上を失敗、`-sS`は通常出力を抑えつつerror表示、`-o /dev/null`はbodyを保存しない、`-w`はstatus codeだけ表示。`/admin/`は404が正常なので`-f`を付けない
- **Expected:** frontendとAPI healthが`200`、公開しない`/admin/`は意図したsecurity動作として`404`
- **Look for:** 名前解決失敗、TLS error、timeout、HTTP 502/503、frontendだけまたはAPIだけの失敗
- **Caution:** login credential、cookie、Authorization headerを追加しない

### 3. Check the production stack on EC2

```bash
cd /srv/ricetta

docker compose \
  --env-file .env.prod \
  -f docker-compose.prod.yml \
  ps
```

- **Location:** EC2
- **Safety:** READ-ONLY
- **Purpose:** 4 serviceのcontainer stateとhealthを一覧する
- **Options:** `--env-file`はCompose変数を`.env.prod`から読むが値を表示しない、`-f`はproduction Composeを明示、`ps`は状態表示
- **Expected:** `db` / `backend`は`healthy`、`frontend` / `caddy`は`Up`
- **Look for:** `Exited`、`Restarting`、`unhealthy`、欠落したservice、異常に短いuptime
- **Caution:** `docker compose config`は展開済みsecretを表示し得るため、incident共有用には実行しない

### 4. Check EC2 resources and host uptime

```bash
uptime
free -h
df -h /
docker stats \
  --no-stream \
  --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}'
```

- **Location:** EC2
- **Safety:** READ-ONLY
- **Purpose:** host load、memory、root disk、container resource使用量を確認する
- **Options:** `-h`は人間向け単位、`--no-stream`は継続更新せず1回だけ表示、`--format`はcontainer IDを除外して名前とCPU / memoryだけ表示
- **Expected:** root filesystemに余裕があり、memory枯渇や異常なCPU使用が継続していない
- **Look for:** load average急増、available memory低下、`/`の80%超過、特定containerのCPU / memory集中

### 5. Check CloudWatch and recent changes

AWS Consoleで5つのproduction Alarmと直近のstate transition時刻をread-onlyで確認します。Alarm stateとmetric graphは別々に確認します。Alarmが現在OKでも調査時刻のgraphに一時的な異常が残る場合があり、ALARMでも欠測とresource超過をgraphで区別する必要があります。CloudWatch画面のAccount ID、Instance ID、ARNをIssueやSlackへコピーしません。

- Status check
- CPU utilization
- CPU credit balance
- memory used
- root disk used

AWS側のread-only確認は、ローカルMacのbrowserからAWS Consoleを使うか、必要な場合だけ信頼できる管理者sessionのAWS CloudShellを使います。EC2 IAM Roleはapplication、backup、限定的なmetric送信のための権限であり、CloudWatch Alarm、SNS、Amazon Q、DNS等の管理・調査権限が不足する可能性があります。EC2上のAWS CLIで`AccessDenied`になってもRoleへ権限を追加せず、管理者sessionへ切り替えます。

- **Location:** AWS ConsoleまたはAWS CloudShell（信頼できる管理者session）
- **Safety:** READ-ONLYの表示・describe操作だけ
- **Purpose:** Alarm state、metric graph、state history、notification actionを確認する
- **Expected:** stateとgraphの理由が整合し、設定済みactionが確認できる
- **Look for:** threshold超過、datapoint欠測、直前のEC2 stop/start、action欠落、AWS Health event
- **Caution:** AWS CLIの一覧結果はidentifierを含み得るため、本書ではcommandを固定せず、出力をIssueやSlackへ貼らない

並行して、直前のdeploy、merge、EC2 stop/start、DNS、certificate、IAM、secret更新、demo reset、backup実行の有無を確認します。変更者と時刻は記録しますがsecret値は記録しません。

### 6. Preserve recent logs

```bash
cd /srv/ricetta

docker compose \
  --env-file .env.prod \
  -f docker-compose.prod.yml \
  logs --since=15m --tail=200 backend

docker compose \
  --env-file .env.prod \
  -f docker-compose.prod.yml \
  logs --since=15m --tail=200 caddy
```

- **Location:** EC2
- **Safety:** READ-ONLY
- **Purpose:** incident直前からのbackend / Caddyログを確認する
- **Options:** `--since=15m`は直近15分、`--tail=200`は末尾200行、末尾のservice名で対象を限定
- **Expected:** health requestが200、連続するexceptionやupstream errorがない
- **Look for:** traceback、Gunicorn worker exit、database connection error、502、TLS issuance error、同一requestの反復
- **Caution:** ログをそのまま共有せず、credential、cookie、Email、IP、private identifierを確認する

### 7. Check failed units and timers

```bash
systemctl --failed --no-pager
systemctl list-timers --all --no-pager

systemctl status ricetta-postgres-backup.service --no-pager
systemctl status ricetta-backup-monitor.service --no-pager
systemctl status ricetta-demo-reset.service --no-pager
```

- **Location:** EC2
- **Safety:** READ-ONLY
- **Purpose:** failed unit、次回timer、直近のoneshot結果を確認する
- **Options:** `--failed`はfailed unitだけ、`--all`はinactive timerも含む、`--no-pager`は対話pagerを開かない
- **Expected:** failed unitなし。backup / monitor / resetの直近実行がsuccessで、timerに次回時刻がある
- **Look for:** `failed`、non-zero exit、timer欠落、期待時刻を過ぎたlast trigger

`ops/systemd/`でsource管理しているのはPostgreSQL backup / monitor / alertの5 unitです。`ricetta-demo-reset.service`と`ricetta-demo-reset.timer`は [AWS Demo Environment](../demo/aws-demo-env.md) に記録された既存実環境構成であり、現時点ではrepositoryの`ops/systemd/`管理fileではありません。

### 8. Classify the affected layer

| Observation | Likely layer |
| --- | --- |
| frontendとAPIの両方が名前解決できない | DNSまたはdomain側 |
| TLS handshakeだけ失敗 | certificate、Caddy、DNS到達性 |
| frontendは200、API healthだけ失敗 | Caddy API route、backend、DB依存 |
| API healthは200、画面asset / routeだけ失敗 | frontend build、frontend Caddy、browser cache |
| API healthは200、特定APIだけ500 | backend business path、DB query、data |
| EC2へ到達できずStatus Check Alarm | EC2またはAWS基盤 |
| backendがunhealthy、dbがhealthy | backend process、settings、migration、application error |
| dbがunhealthy | PostgreSQL、disk、volume、DB startup |
| containersは正常、backup unitだけfailed | backup script、S3、IAM、network |

## Read-only command catalog

### Compose service logs

```bash
cd /srv/ricetta

docker compose \
  --env-file .env.prod \
  -f docker-compose.prod.yml \
  logs --since=30m --tail=300 backend
```

- **Location:** EC2
- **Safety:** READ-ONLY
- **Purpose:** 例では`backend`へログを限定する。別serviceを調べる場合は末尾を`frontend`、`db`、`caddy`のいずれか1つへ明示的に置き換える
- **Expected:** 起動完了後にfatal errorが反復していない
- **Look for:** 最初のerror、その直前のevent、restart境界
- **Caution:** 複数serviceの大量ログを一度に出さず、実在する1 serviceを明示する

### Django configuration check

```bash
cd /srv/ricetta

docker compose \
  --env-file .env.prod \
  -f docker-compose.prod.yml \
  exec -T backend python manage.py check
```

- **Location:** EC2
- **Safety:** READ-ONLY
- **Purpose:** 起動済みbackend内でDjango system checkを実行する
- **Options:** `exec`は既存container内、`-T`はpseudo-TTYを割り当てない
- **Expected:** `System check identified no issues`
- **Look for:** settings、model、URL configurationのcheck error
- **Caution:** `migrate`やreset commandへ置き換えない

### Django-to-PostgreSQL connection check

```bash
cd /srv/ricetta

docker compose \
  --env-file .env.prod \
  -f docker-compose.prod.yml \
  exec -T backend python manage.py shell -c \
  "from django.db import connection; connection.ensure_connection(); print('database connection: ok')"
```

- **Location:** EC2
- **Safety:** READ-ONLY
- **Purpose:** production settingsを使ってbackendからDBへ接続できるか確認する
- **Options:** `shell -c`は指定した短いPythonをDjango contextで1回実行
- **Expected:** `database connection: ok`
- **Look for:** hostname、timeout、authentication、database missing、connection refused
- **Caution:** query、write、credential表示を追加しない

### Caddy configuration validation

```bash
cd /srv/ricetta

docker compose \
  --env-file .env.prod \
  -f docker-compose.prod.yml \
  exec -T caddy caddy validate --config /etc/caddy/Caddyfile
```

- **Location:** EC2
- **Safety:** READ-ONLY
- **Purpose:** 実行中container内のCaddyfileをparse / validateする
- **Options:** `validate`は設定を適用せず検証、`--config`はcontainer内pathを明示
- **Expected:** valid configuration
- **Look for:** parse error、directive error、address設定error
- **Caution:** `reload`へ置き換えない

### Unit journal

```bash
journalctl \
  -u ricetta-postgres-backup.service \
  --since '30 minutes ago' \
  -n 200 \
  --no-pager
```

- **Location:** EC2
- **Safety:** READ-ONLY
- **Purpose:** 指定unitの直近journalを確認する
- **Options:** `-u`はunit限定、`--since`は期間、`-n`は最大行数、`--no-pager`はpager無効
- **Expected:** completed / success
- **Look for:** documented exit status、S3 / IAM error、timeout、OnFailure通知error
- **Caution:** unit名だけをmonitor / alert / resetへ置き換え、secret fileの内容は表示しない

### DNS resolution and TLS handshake

```bash
dig +short ricetta.lintake.net A

dig +short @1.1.1.1 ricetta.lintake.net A

openssl s_client \
  -connect ricetta.lintake.net:443 \
  -servername ricetta.lintake.net \
  </dev/null
```

- **Location:** ローカルMac
- **Safety:** READ-ONLY
- **Purpose:** public DNSのA record応答とTLS handshakeを分離して確認する
- **Prerequisite:** ローカルMacで`dig`と`openssl`が利用できること。利用できない場合はincident中にEC2へpackageを追加せず、同じtoolがある別の信頼できる管理者端末を使う
- **Options:** `+short`は回答だけ、`@1.1.1.1`はpublic resolverを明示、`-connect`は接続先、`-servername`はSNI、`</dev/null`は対話入力を終了
- **Expected:** default resolverとpublic resolverのDNS回答が一致し、TLS handshakeの`Verify return code`が`0 (ok)`
- **Look for:** resolver間の差はcache / 伝播途中の候補、両方の予期しない同一回答は設定誤りの候補。public resolverだけのtimeoutはローカルnetworkが外向きDNSを制限している可能性もある。空の回答、expiry、hostname mismatch、connection refused / timeoutも確認する
- **Caution:** 出力されたIPやcertificate詳細をpublic Issueへ貼らない

切り分けは、外部`curl`のHTTP status → default / public resolverのDNS回答 → certificate / SNI → EC2到達性とCaddy state / logの順で進めます。DNS変更直後はresolver間の差とTTL経過を確認し、単一resolverの結果だけで設定を書き換えません。

## Symptom-based runbooks

各症状で、最初に共通トリアージを実施します。表の「first checks」は追加のread-only確認です。状態変更は [Controlled state changes](#controlled-state-changes) の条件を満たすまで行いません。

### Web, frontend, API, and authentication

| Symptom | Likely causes | First checks / healthy signal | Initial response / do not do | Escalation and source |
| --- | --- | --- | --- | --- |
| 画面が表示されない | DNS、TLS、Caddy、frontend、EC2停止 | frontend / APIの外部status、Compose `ps`、Caddyログ。両方200が正常 | layerを特定する。browser refreshだけを繰り返さない | DNS/TLSなら本書該当項目、EC2ならIssue #69判断 |
| frontendだけ異常 | frontend container、build asset、SPA fallback、cache | API health 200、frontend state `Up`、frontend / Caddyログ | 別browser/private windowで再現確認。APIを再起動しない | [AWS Demo Environment](../demo/aws-demo-env.md) |
| API healthが応答しない | backend停止、Caddy route、host setting、EC2 resource | Compose `ps`、backend / Caddyログ、Django check | 最初のbackend errorを保存。すぐ全stackを再起動しない | backend単体再作成条件を判断 |
| APIが500を返す | application exception、DB query、data、migration mismatch | healthの成否、該当時刻のbackend traceback、DB接続 | request pathと時刻を記録し、同じwrite requestを反復しない | code rollback / DB判断へ進む |
| ログインできない | backend、session / CSRF、Secure cookie、account reset、throttle | health 200、browser status、backend / Caddyログ、直近reset | passwordやcookieを共有しない。accountを直接DB更新しない | [Public Demo Environment](../demo/demo.md)、[Secret Management](../secret-management.md) |
| デモリセット失敗 | backend未ready、DB、Shop / Membership整合性のfail-closed、timer / script | reset service status / journal、backend / db state、transaction rollback後に変更前データが維持されたこと | journalを保存し、resetを連打しない。Shop識別やMembership矛盾を手動DB更新で迂回しない | [AWS Demo Environment](../demo/aws-demo-env.md)、[Public Demo Environment](../demo/demo.md) |

### Containers, Caddy, and PostgreSQL

| Symptom | Likely causes | First checks / healthy signal | Initial response / do not do | Escalation and source |
| --- | --- | --- | --- | --- |
| backendが停止 / 再起動 | Gunicorn exit、settings、DB待機、OOM | `ps`、backendログ、memory、db healthy。安定した`healthy`が正常 | restart countと最初のexitを記録。loop中にrestartしない | 単体再作成またはcode rollback判断 |
| frontendが停止 | static server / image / build異常 | `ps`、frontendログ、API health。`Up`が正常 | API / DBへ触れずfrontendへ限定 | frontend単体再作成判断 |
| dbが停止 / unhealthy | PostgreSQL起動失敗、disk、volume、corruption | `ps`、dbログ、`df -h /`、DB接続。`healthy`が正常 | 書込みを増やさずログ保全。volumeを削除しない | [Backup and Restore](../backup/backup-and-restore.md)、restore判断 |
| Caddyが応答しない | container停止、port、config、certificate、upstream | `ps`、Caddyログ、config validation、外部curl | backend / dbを先に再起動しない。reload前にvalidate | Caddy単体再作成またはDNS/TLS対応 |
| PostgreSQLへ接続できない | db停止、network、credential不一致、database missing | db state / log、Django-to-DB check、disk | secret値を表示しない。認証失敗だけでDB初期化しない | [Secret Management](../secret-management.md)、[PostgreSQL Restore](../backup/postgres-restore.md) |

### EC2 and CloudWatch

| Symptom | Likely causes | First checks / healthy signal | Initial response / do not do | Escalation and source |
| --- | --- | --- | --- | --- |
| CPU Alarm | load増加、runaway process、backup/reset、traffic | CloudWatch graph、`uptime`、format指定した`docker stats` | 高使用container/processを特定。即killしない | [EC2 Resource Monitoring](../monitoring/ec2-resource-monitoring.md) |
| Memory Alarm | container増加、leak、OOM | `free -h`、stats、backend/db logs、kernel OOM記録 | OOM前後を保存。根拠なくswapや再起動を行わない | 同上 |
| Disk Alarm | Docker log/image、DB volume、local backup | `df -h /`、`docker system df`、大きいcategoryの確認 | DB、backup、volumeを削除しない。無差別prune禁止 | 同上、[Backup and Restore](../backup/backup-and-restore.md) |
| EC2 Status Check Alarm | AWS基盤、instance OS / network | Alarm種別、AWS Health、EC2 status checks、SSH到達性 | AWS側かinstance側か分離。自動rebootしない | AWS SupportまたはIssue #69 rebuild判断 |
| CloudWatch Agent metric欠測 | EC2 stop / reboot、Agent停止、IAM、IMDSv2、network | EC2 state / reboot時刻、Agent status / journal、最後のdatapoint。稼働中は毎分到着が正常 | EC2停止・再起動による期待された欠測かを先に分離し、Agent restart前にjournalを保存 | [EC2 Resource Monitoring](../monitoring/ec2-resource-monitoring.md) |

CloudWatch Agentのread-only確認:

```bash
sudo systemctl status amazon-cloudwatch-agent --no-pager
sudo journalctl -u amazon-cloudwatch-agent -n 100 --no-pager
```

- **Location:** EC2
- **Safety:** READ-ONLY
- **Expected:** service active、fatal送信errorなし
- **Look for:** IAM deny、metadata、network、config parse error

### CloudWatch notification path

CloudWatch Alarm通知がSlackへ届かない場合、次の順にread-onlyで切り分けます。設定変更やtest通知は一次調査に含めません。

| Layer | Read-only check | Healthy signal |
| --- | --- | --- |
| CloudWatch Alarm | state history、metric graph、notification action | 対象時刻にstate transitionがあり、SNS actionが設定済み |
| SNS | topic、policy、subscription state | 対象topicとconfirmed subscriptionが存在 |
| Amazon Q Developer | channel configuration、関連SNS topic | 対象configurationが存在し、topic関連付けが一致 |
| Slack | channel履歴、client側通知設定 | message自体が到着。desktop通知だけの不調と区別 |

Alarmがthresholdを超えてもstate transitionがなければ通知actionは実行されません。詳細なAlarm / SNS / Amazon Q構成は [EC2 Resource Monitoring](../monitoring/ec2-resource-monitoring.md) を正本とします。AWS Budget通知は更新が遅い請求ガードレールであり、application availability Alarmではありません。請求異常は [AWS Cost Monitoring and Billing Guardrails](../monitoring/aws-cost-monitoring.md) で別に扱います。

### Backup, S3, and notifications

| Symptom | Likely causes | First checks / healthy signal | Initial response / do not do | Escalation and source |
| --- | --- | --- | --- | --- |
| PostgreSQL backup失敗 | pg_dump、DB、compression、S3 upload、local cleanup | backup service status / journal、documented exit status | local artifactとjournalを確認。失敗jobを連打しない | [PostgreSQL Backup](../backup/postgres-backup.md)、[PostgreSQL Backup Monitoring](../backup/postgres-monitoring.md) |
| S3にbackupがない | upload失敗、IAM、prefix、network、timer未実行 | monitor service journal、backup timer last/next、backup service result | bucketやobjectを削除しない。latestだけでなく実行履歴を見る | 同上 |
| backup監視異常 | S3確認失敗、latest empty / stale、IAM | monitor status / journal、exit status | 原因codeを記録。monitorを無効化しない | [PostgreSQL Backup Monitoring](../backup/postgres-monitoring.md) |
| Slack通知異常 | OnFailure未発火、notify script、secret file、network | alert unit / source unit journal、他通知経路 | webhook値を表示・test messageへ貼らない。通知失敗とbackup失敗を分離 | [PostgreSQL Backup Monitoring](../backup/postgres-monitoring.md)、[Secret Management](../secret-management.md) |

backup通知はCloudWatchのSNS→Amazon Q経路ではなく、source unitの`OnFailure`→alert unit→notify script→Slack webhookです。Slack未通知時は、source unitが失敗したか、`OnFailure`が起動したか、alert unitが成功したかを順に確認し、CloudWatch通知経路と混同しません。

確認対象unit:

```bash
systemctl status ricetta-postgres-backup.timer --no-pager
systemctl status ricetta-backup-monitor.timer --no-pager
journalctl -u ricetta-postgres-backup.service -n 100 --no-pager
journalctl -u ricetta-backup-monitor.service -n 100 --no-pager
journalctl -u ricetta-backup-alert@ricetta-postgres-backup.service -n 100 --no-pager
```

- **Location:** EC2
- **Safety:** READ-ONLY
- **Expected:** timer active、last run success、monitor healthy
- **Look for:** exit status 21–25または31–34。意味はbackup monitoring正本を参照

### DNS, TLS, restore, rebuild, and security

| Symptom | Likely causes | First checks / healthy signal | Initial response / do not do | Escalation and source |
| --- | --- | --- | --- | --- |
| DNS異常 | A record変更、伝播、resolver、domain側 | `dig`、別resolver / network、EC2到達性 | 現在値と変更時刻を記録。根拠なくrecordを書き換えない | DNS provider側確認、[AWS Demo Environment](../demo/aws-demo-env.md) |
| TLS / HTTPS異常 | certificate取得 / 更新、SNI、DNS、Caddy data | `openssl s_client`、Caddyログ、HTTP/HTTPS差 | certificateやCaddy volumeを削除しない | Caddy / DNS側対応、必要ならprovider確認 |
| DB restoreが必要に見える | logical data loss、corruption、誤操作 | app停止範囲、DB接続、Recovery Point Objective（RPO、許容できるデータ損失時点）、backup存在 / 時刻 / gzip整合性、restore対象 | 接続不能だけでrestoreしない。restore判断後は新規書込みを止め、公開DBへ直接restoreしない | [PostgreSQL Restore](../backup/postgres-restore.md) の一時DB検証へ |
| EC2 rebuildが必要に見える | instance回復不能、root disk / OS重大障害 | AWS status、SSH、volume / backup availability、GitHub / Bitwarden / S3アクセス | 現EC2を削除せず証拠とbackupを確認 | Issue #69のTemporary EC2 rebuild drillへ |
| credential漏えい / 不正アクセス疑い | secret露出、不審login / IAM、改ざん、予期しない課金 | 発生時刻、CloudTrail、IAM activity、root MFA、login / deploy履歴 | 通常障害と分離。安全上可能なら再起動やログ削除より証跡保全を先に行う。侵害hostを信頼して修復を続けない | 信頼できる管理者端末 / sessionからcredential失効、Bitwarden更新、[Secret Management](../secret-management.md)、必要に応じAWS Support |

## Decision matrix

| Decision | Choose when | Preconditions | Avoid / next source |
| --- | --- | --- | --- |
| 監視継続のみ | 一過性で現在正常、影響なし、原因候補を記録済み | graph / logs / external healthを一定時間確認 | 再発時刻とthresholdを記録 |
| container単体再作成 | 1 serviceだけ異常、依存service正常、config / imageが既知 | logs保全、対象明示、外部health baseline、rollback方針 | `db`は通常対象にしない |
| app全体再起動 | backend / frontend / caddyが共通原因で不整合、DB正常 | logs保全、短時間停止共有、backup状態確認 | DBを同時restartしない |
| 直前codeへrollback | deploy直後から再現し、旧revisionで解消する合理的根拠 | DB migration互換性、変更差分、rollback後verification | [AWS Demo Environment](../demo/aws-demo-env.md) |
| DB restore | logical loss / corruptionが確認され、resetでは目的を満たさない | 新規書込み停止、RPO合意、restore対象backupを人が選択、存在 / 時刻 / gzip整合性、復元可能性の一時DB検証、現DB backup | [PostgreSQL Restore](../backup/postgres-restore.md) |
| EC2 rebuild | instance / OS / root diskが回復不能、または侵害hostを信頼できない | GitHub / Bitwarden / S3、DNS、backup、削除前証拠 | Issue #69。現EC2を先に削除しない |
| security対応 | credential漏えい、不審IAM / login /改ざん | 証跡保全、影響credential特定、信頼できる端末 | Bitwarden / IAM側で失効・rotation。通常restartで済ませない |
| DNS / TLS対応 | application内部正常で名前解決またはhandshakeだけ異常 | current record、certificate、Caddy log、変更履歴 | record / certificate storageを無断削除しない |
| AWS / external確認 | EC2 Status Check、AWS Health、provider障害、account異常 | service healthとlocal evidence | 必要に応じAWS Support。private IDはpublic記録しない |

S3 objectが存在することやsizeが0より大きいことだけでは、PostgreSQLへ正常にrestoreできる保証になりません。restore前にRPOを確認し、gzip整合性と一時DBへのrestoreを検証してから本番影響のある判断へ進みます。

## Controlled state changes

この節だけがSTATE-CHANGINGです。共通トリアージと該当症状のread-only確認を完了し、実行者、対象、理由、開始時刻、rollback方法を記録してから実行します。

### Recreate frontend only

frontendだけが異常で、API / backend / db / Caddyが正常、frontendログを保存済みの場合の限定例です。

```bash
cd /srv/ricetta

docker compose \
  --env-file .env.prod \
  -f docker-compose.prod.yml \
  up -d --no-deps --force-recreate frontend
```

- **Location:** EC2
- **Safety:** STATE-CHANGING
- **Target:** `frontend`だけ
- **Options:** `up -d`はbackground起動、`--no-deps`は依存serviceを変更しない、`--force-recreate`は対象containerを再作成
- **Preconditions:** logs保全、image / configの出所確認、API health正常、短時間影響の共有
- **Verification:** Compose `ps`、frontend / API外部status、frontend / Caddyログ
- **Rollback:** 直前code / imageへ戻す判断はAWS Demo Environmentのrollbackへ進む
- **Do not:** service名を`db`へ置き換えない

### Restart application-facing services

backend / frontend / caddyに共通する一時的process不整合が確認され、DBがhealthyの場合だけ検討します。

```bash
cd /srv/ricetta

docker compose \
  --env-file .env.prod \
  -f docker-compose.prod.yml \
  restart backend frontend caddy
```

- **Location:** EC2
- **Safety:** STATE-CHANGING
- **Target:** `backend` / `frontend` / `caddy`。`db`を含めない
- **Preconditions:** 3 serviceのlogs保全、DB healthy、backup状態確認、停止影響共有
- **Verification:** Compose `ps`、external frontend / API health、直後の各serviceログ
- **Do not:** 原因不明のrestart loop、`docker compose restart`だけで全serviceを暗黙対象にしない

### Actions not executed from this Runbook

以下は状態変更または破壊的操作です。本書から直接実行せず、判断条件を満たして正本へ移動します。

- migration: deploy手順とschema互換性を確認して [AWS Demo Environment](../demo/aws-demo-env.md) へ
- demo reset: dataが初期化されるため [Public Demo Environment](../demo/demo.md) と [AWS Demo Environment](../demo/aws-demo-env.md) へ
- PostgreSQL restore: [PostgreSQL Restore](../backup/postgres-restore.md) の一時DB検証へ
- code rollback: migration互換性を確認して [AWS Demo Environment](../demo/aws-demo-env.md) へ
- credential失効 / rotation: 信頼できる端末から [Secret Management](../secret-management.md) へ
- EC2 stop / reboot / rebuild: AWS statusとbackupを確認し、Issue #69へ
- DNS record / TLS storage変更: current stateとrollback値を記録してprovider手順へ

次のDESTRUCTIVE操作は一次対応として掲載・実行しません。

```text
docker compose down -v
Docker volume deletion
PostgreSQL data directory deletion or initialization
Unscoped docker system prune
S3 backup deletion
EC2 or EBS deletion
```

## Recovery verification

状態変更後は最低限、次を確認して記録します。

1. external frontendとAPI healthが期待するHTTP statusへ戻った。
2. Compose `ps`で`db` / `backend`がhealthy、`frontend` / `caddy`がUp。
3. 変更対象serviceの新しいログにfatal errorがない。
4. loginと主要画面をsecretを記録せずsmoke checkした。
5. backup / monitor / reset timerが意図せず停止していない。
6. CloudWatch Alarmが回復した、または回復待ち理由を記録した。
7. 原因、操作、復旧時刻、再発防止をincident recordへ追記した。

## Incident record template

secret、credential、cookie、個人情報、Account ID、Instance ID、ARN、Email、Slack ID、publicに不要なIPやlog全文を記載しません。

```markdown
# Incident: <short title>

- 発生日時（timezone付き）:
- 検知方法:
- 症状:
- 影響範囲:
- 直前の変更:
- 確認済み事実:
- 仮説 / 未確認事項:
- 原因（根拠・確認方法を含む）:
- 実施したread-only確認:
- 実施した対応:
- 復旧日時（timezone付き）:
- 再発防止:
- 関連Issue / PR:
- 未解決事項:
```

## Acceptance Criteria mapping

| Issue #78 Acceptance Criteria | Evidence |
| --- | --- |
| 主要な障害パターンが症状別に整理されている | Symptom-based runbooks |
| 障害時に最初に確認する場所が分かる | First 5–10 minutes |
| Docker / Caddy / backend / dbの確認コマンドが分かる | Read-only command catalog |
| backup失敗時の確認手順が分かる | Backup, S3, and notifications |
| restoreが必要なケースを判断できる | Decision matrix、DB restore symptom |
| DNS / TLS異常時の確認手順がある | DNS resolution and TLS handshake、symptom table |
| CloudWatch / Slack通知から一次対応に入れる | First 5–10 minutes、EC2 / backup symptom tables |
| DocsとしてGit管理されている | 本ファイルとdocs indexの導線 |
