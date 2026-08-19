# PostgreSQL Backup Monitoring

backup失敗またはSlack通知からRicetta全体の影響を切り分ける場合は [Incident Response Runbook](../operations/incident-response.md) を入口にし、本書でbackup監視固有のexit statusと復旧手順を確認します。

## Purpose

このドキュメントは、Ricetta公開デモ環境のPostgreSQLバックアップ監視とSlack通知の運用手順をまとめたものです。

バックアップ処理を自動化するだけでなく、以下の異常を検知し、必要な場合のみ通知できる状態を目的とします。

- PostgreSQL dumpの失敗
- backupファイルの異常
- gzip圧縮の失敗
- S3 uploadの失敗
- S3上にbackupが存在しない
- S3上の最新backupが0 byte
- 最新backupが一定時間以上更新されていない
- S3の状態確認そのものに失敗する

正常時はSlack通知を送らず、対応が必要な異常のみ通知します。

関連ドキュメント:

- [Backup and Restore](./backup-and-restore.md)
- [PostgreSQL Backup](./postgres-backup.md)
- [PostgreSQL Restore](./postgres-restore.md)

## Monitoring Overview

Ricettaのバックアップ監視は、以下の2段構成です。

```text
04:10
ricetta-postgres-backup.timer
        ↓
ricetta-postgres-backup.service
        ↓
pg_dump
gzip
S3 upload
local retention
        ↓
失敗時
OnFailure
        ↓
Slack alert


04:30
ricetta-demo-reset.timer
        ↓
demo data reset


05:00
ricetta-backup-monitor.timer
        ↓
ricetta-backup-monitor.service
        ↓
S3 latest backup check
        ↓
existence
size
age
        ↓
異常時
OnFailure
        ↓
Slack alert
```

バックアップ処理自身の失敗だけでなく、timer停止などによりbackup処理そのものが実行されなかった場合も、05:00の独立monitorによって検知できる構成です。

## Schedule

| Time | Process | Purpose |
| --- | --- | --- |
| 04:10 JST | PostgreSQL backup | reset前のDB状態を保存 |
| 04:30 JST | Demo reset | 公開デモを初期状態へ戻す |
| 05:00 JST | Backup monitor | S3上の最新backupを確認 |

確認:

```bash
systemctl list-timers --all | grep ricetta
```

期待する順序:

```text
04:10 ricetta-postgres-backup.timer
04:30 ricetta-demo-reset.timer
05:00 ricetta-backup-monitor.timer
```

## Managed Files

Gitで管理する監視関連ファイル:

```text
ops/
├── scripts/
│   ├── ricetta-postgres-backup.sh
│   ├── ricetta-backup-monitor.sh
│   ├── ricetta-backup-alert.sh
│   └── ricetta-backup-notify.sh
│
└── systemd/
    ├── ricetta-postgres-backup.service
    ├── ricetta-postgres-backup.timer
    ├── ricetta-backup-monitor.service
    ├── ricetta-backup-monitor.timer
    └── ricetta-backup-alert@.service
```

EC2上の配置先:

```text
/usr/local/bin/ricetta-postgres-backup.sh
/usr/local/bin/ricetta-backup-monitor.sh
/usr/local/bin/ricetta-backup-alert.sh
/usr/local/bin/ricetta-backup-notify.sh

/etc/systemd/system/ricetta-postgres-backup.service
/etc/systemd/system/ricetta-postgres-backup.timer
/etc/systemd/system/ricetta-backup-monitor.service
/etc/systemd/system/ricetta-backup-monitor.timer
/etc/systemd/system/ricetta-backup-alert@.service
```

GitHub上のファイルを正本とし、EC2へ配置して使用します。

## Slack Notification

通知先:

```text
Slack App:
LINTAKE Monitor

Channel:
#infra-alerts
```

Slack Incoming Webhookを使用します。

Webhook URLはsecretとして扱い、Git管理しません。

EC2上では以下のファイルから読み込みます。

```text
/etc/ricetta/backup-monitor.env
```

想定内容:

```env
SLACK_WEBHOOK_URL=<secret>
```

Webhook URLの実値はドキュメント、GitHub Issue、Pull Request、README、チャット、スクリーンショットへ記載しません。

Webhook URLの正本はBitwardenの `Ricetta Backup Monitor Secrets` で管理します。更新と復旧の手順は [Secret Management](../secret-management.md) を参照します。

### Secret file permissions

```bash
sudo chown root:root /etc/ricetta/backup-monitor.env
sudo chmod 600 /etc/ricetta/backup-monitor.env
```

確認:

```bash
sudo ls -l /etc/ricetta/backup-monitor.env
```

期待する権限:

```text
-rw------- root root
```

## Notification Policy

正常時の通知は送信しません。

異常時のみSlackへ通知します。

通知内容は以下に限定します。

- 対象サービス
- 異常の概要
- systemd result
- exit status
- 調査用journalctl command

以下は通知しません。

- PostgreSQL password
- Django secret key
- AWS credentials
- Slack Webhook URL
- `.env.prod` の内容
- journal全文

通知形式:

```text
🚨 [Ricetta / Backup]
または
⚠️ [Ricetta / Monitor]

異常内容

Service: <service>
Result: <result>
Exit status: <status>

確認:
journalctl -u <service> -n 80 --no-pager
```

## Backup Exit Codes

`ricetta-postgres-backup.sh` は、既知の異常について専用exit codeを返します。

| Exit Code | Meaning |
| --- | --- |
| 21 | `pg_dump` failed |
| 22 | dump file is empty |
| 23 | gzip failed or compressed file is empty |
| 24 | S3 upload failed |
| 25 | local retention cleanup failed |

これにより、systemdから単純な成功・失敗だけではなく、失敗原因を識別できます。

## Monitor Exit Codes

`ricetta-backup-monitor.sh` はS3上のbackup状態を確認します。

| Exit Code | Meaning |
| --- | --- |
| 31 | no backup found |
| 32 | latest backup is 0 byte |
| 33 | latest backup exceeded allowed age |
| 34 | failed to inspect S3 |

通常の最大許容時間:

```text
21600 seconds
= 6 hours
```

monitorは05:00 JSTに実行するため、04:10 JSTのbackupが正常に作成されていれば十分に許容時間内となります。

## Backup Failure Detection

PostgreSQL backup service:

```text
ricetta-postgres-backup.service
```

失敗時:

```text
ricetta-postgres-backup.service
        ↓
non-zero exit status
        ↓
OnFailure
        ↓
ricetta-backup-alert@ricetta-postgres-backup.service
        ↓
ricetta-backup-alert.sh
        ↓
exit code判定
        ↓
ricetta-backup-notify.sh
        ↓
Slack
```

service確認:

```bash
systemctl cat ricetta-postgres-backup.service
```

`OnFailure` が設定されていることを確認します。

## Independent Backup Health Monitor

監視script:

```text
/usr/local/bin/ricetta-backup-monitor.sh
```

以下を確認します。

1. S3にbackupが存在する
2. 最新backupのsizeが0 byteより大きい
3. 最新backupが許容時間内に作成されている
4. S3自体を正常に確認できる

手動実行:

```bash
/usr/local/bin/ricetta-backup-monitor.sh
```

正常時の例:

```text
[ricetta-backup-monitor] latest key: ricetta/demo/postgres/ricetta_20260810_235240.sql.gz
[ricetta-backup-monitor] latest size: 11436
[ricetta-backup-monitor] age seconds: 2218
[ricetta-backup-monitor] backup is healthy
```

## systemd Monitor Service

service:

```text
ricetta-backup-monitor.service
```

手動実行:

```bash
sudo systemctl start ricetta-backup-monitor.service
```

ログ確認:

```bash
journalctl \
  -u ricetta-backup-monitor.service \
  -n 50 --no-pager
```

正常時:

```text
backup is healthy
Deactivated successfully
Finished ricetta-backup-monitor.service
```

## systemd Monitor Timer

timer:

```text
ricetta-backup-monitor.timer
```

有効化:

```bash
sudo systemctl enable --now ricetta-backup-monitor.timer
```

確認:

```bash
systemctl status ricetta-backup-monitor.timer
```

期待する状態:

```text
Active: active (waiting)
Trigger: 05:00 JST
```

## Failure Injection Tests

監視機能は、意図的に異常を発生させて動作確認しています。

### S3 Upload Failure

通常のbackup先やIAM設定を壊さず、テスト用backup scriptで権限外のS3 prefixを指定しました。

結果:

```text
S3 upload
↓
failure
↓
exit status 24
↓
systemd failure
↓
OnFailure triggered
↓
Slack notification
```

journalでは以下を確認しました。

```text
Main process exited
Failed with result 'exit-code'
Triggering OnFailure= dependencies
```

テスト後は通常のbackup serviceを再実行し、S3 uploadが正常に完了することを確認しました。

### Stale Backup Detection

monitor scriptの最大許容時間をテスト時のみ1秒に変更して、意図的にstale判定させました。

通常設定:

```text
MAX_AGE_SECONDS=21600
```

テスト設定:

```text
MAX_AGE_SECONDS=1
```

結果:

```text
latest backup is too old
↓
exit status 33
↓
systemd failure
↓
OnFailure
↓
alert script detects status=33
↓
Slack notification
```

journal確認結果:

```text
[ricetta-backup-alert] alert sent for ricetta-backup-monitor.service status=33 result=exit-code
```

Slackへの原因別日本語通知も確認済みです。

### Recovery After Failure Test

一時的なfailure test設定を削除し、monitorを再実行しました。

結果:

```text
backup is healthy
Deactivated successfully
Finished ricetta-backup-monitor.service
```

これにより、

```text
normal
↓
intentional failure
↓
alert
↓
recovery
↓
normal
```

まで確認しています。

## Normal Backup Verification

監視機能追加後の更新版backup scriptでも、正常backupを確認しました。

確認時の処理:

```text
creating dump
compressing dump
uploading to S3
S3 upload completed
pruning local backups
completed
```

systemdも正常終了しました。

```text
Deactivated successfully
Finished ricetta-postgres-backup.service
```

## Troubleshooting

### Backup service failed

```bash
systemctl status ricetta-postgres-backup.service --no-pager

journalctl \
  -u ricetta-postgres-backup.service \
  -n 80 --no-pager
```

exit statusを確認し、`Backup Exit Codes` と照合します。

### Monitor service failed

```bash
systemctl status ricetta-backup-monitor.service --no-pager

journalctl \
  -u ricetta-backup-monitor.service \
  -n 80 --no-pager
```

exit statusを確認し、`Monitor Exit Codes` と照合します。

### Alert notification

```bash
journalctl \
  -u 'ricetta-backup-alert@ricetta-backup-monitor.service' \
  -n 50 --no-pager
```

またはbackup側:

```bash
journalctl \
  -u 'ricetta-backup-alert@ricetta-postgres-backup.service' \
  -n 50 --no-pager
```

### Check latest S3 backup

```bash
aws s3 ls \
  s3://lintake-backups/ricetta/demo/postgres/
```

確認項目:

- 最新backupが存在する
- `.sql.gz` になっている
- sizeが0 byteではない
- 日時が想定範囲内である

### Check timers

```bash
systemctl list-timers --all | grep ricetta
```

## Verification Result

以下を検証済みです。

- backup処理の成功・失敗をsystemdで判別できる
- backup失敗時にjournalから原因を調査できる
- backup処理で既知の異常をexit codeで分類できる
- S3 upload失敗を異常として検知できる
- S3上の最新backupを確認できる
- 最新backupのsizeを確認できる
- 0 byte backupを異常として扱える
- 古いbackupを異常として検知できる
- S3確認失敗を独立した異常として扱える
- systemd `OnFailure` からSlack通知を送信できる
- 原因別の日本語通知を送信できる
- 通知にsecretを含めない
- S3 uploadの意図的failure testを実施済み
- stale backupの意図的failure testを実施済み
- failure test後に正常状態へ復帰できる
- monitor timerが05:00 JSTに有効化されている

## Future Improvements

今後は以下を検討します。

- Slack通知の共通化
- SplitMate / GreenLogへの監視展開
- Wyseホームサーバーへの監視展開
- S3 Lifecycleとの組み合わせ
- 定期的なrestore drillとの連携
- EC2 / disk / Docker container監視
- Terraform / Ansibleによる監視設定の自動構築
