# PostgreSQL Restore

## Purpose

このドキュメントは、AWS S3へ保存したRicetta PostgreSQL backupから、安全にデータを復元・検証する手順をまとめたものです。

restoreはDBを書き換える危険操作のため、公開中の `ricetta` DBへ直接restoreせず、一時DBを作成して検証します。

バックアップ全体の方針は [Backup and Restore](./backup-and-restore.md)、バックアップ取得手順は [PostgreSQL Backup](./postgres-backup.md) を参照します。

## Safety Policy

以下を基本方針とします。

- 公開中の `ricetta` DBへ直接restoreしない
- restoreテストでは一時DBを作成する
- restore対象のbackupファイルを人間が明示的に選択する
- restore対象DB名を実行前に確認する
- 本番相当のrestore前には、可能であれば現在DBのdumpを取得する
- restore後はPostgreSQLだけでなくDjangoからもデータを確認する
- 検証終了後は一時DBと一時ファイルを削除する

通常の公開デモ復旧ではseed resetを優先し、database backupからのrestoreは特定時点のDB状態へ戻す必要がある場合に使用します。

## Prerequisites

- EC2へSSH接続できる
- `/srv/ricetta` にproduction環境がある
- `.env.prod` が配置されている
- AWS CLIが利用できる
- EC2 IAM Role経由で `lintake-backups/ricetta/demo/postgres/` を読み取れる
- PostgreSQL containerが起動している

## 1. Load Environment Variables

```bash
ssh ricetta
cd /srv/ricetta

set -a
source .env.prod
set +a
```

## 2. Select Backup

S3上のbackup一覧を確認します。

```bash
aws s3 ls s3://lintake-backups/ricetta/demo/postgres/
```

restore対象を明示的に指定します。

```bash
BACKUP_NAME="<backup-file>.sql.gz"
```

自動でlatestを選択せず、restore対象を人間が確認して指定します。

## 3. Download and Verify Backup

一時ディレクトリを作成します。

```bash
RESTORE_DIR="/tmp/ricetta-restore-test"
mkdir -p "$RESTORE_DIR"
```

S3からbackupを取得します。

```bash
aws s3 cp \
  "s3://lintake-backups/ricetta/demo/postgres/$BACKUP_NAME" \
  "$RESTORE_DIR/$BACKUP_NAME"
```

ファイルを確認します。

```bash
ls -lh "$RESTORE_DIR/$BACKUP_NAME"
gzip -t "$RESTORE_DIR/$BACKUP_NAME"
echo $?
```

`gzip -t` が成功した場合、終了コードは `0` になります。

検証時には、以下のbackupで整合性確認に成功しました。

```text
ricetta_20260809_233539.sql.gz
```

## 4. Create Temporary Database

restore専用の一時DBを作成します。

```bash
RESTORE_DB="ricetta_restore_test_YYYYMMDD"

docker compose --env-file .env.prod -f docker-compose.prod.yml exec -T db \
  createdb -U "$POSTGRES_USER" "$RESTORE_DB"
```

DB一覧を確認します。

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml exec -T db \
  psql -U "$POSTGRES_USER" -d postgres -c '\l'
```

公開デモDB `ricetta` とは別に、一時DBが存在することを確認します。

検証時には以下の一時DBを使用しました。

```text
ricetta_restore_test_20260810
```

## 5. Restore Backup

gzip圧縮されたbackupを展開しながら、一時DBへ直接restoreします。

```bash
gzip -dc "$RESTORE_DIR/$BACKUP_NAME" | \
  docker compose --env-file .env.prod -f docker-compose.prod.yml exec -T db \
  psql -v ON_ERROR_STOP=1 \
  -U "$POSTGRES_USER" \
  -d "$RESTORE_DB"
```

`ON_ERROR_STOP=1` により、SQL実行中にエラーが発生した場合は処理を失敗として停止します。

restore時には以下の処理が実行されることを確認しました。

- `CREATE TABLE`
- `COPY`
- `setval`
- `CREATE INDEX`
- `ALTER TABLE`

これは、テーブル、データ、sequence、index、constraintが復元されていることを示します。

## 6. Verify PostgreSQL Restore

テーブル一覧を確認します。

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml exec -T db \
  psql -U "$POSTGRES_USER" -d "$RESTORE_DB" -c '\dt'
```

Django migrationデータを確認します。

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml exec -T db \
  psql -U "$POSTGRES_USER" -d "$RESTORE_DB" \
  -c "SELECT COUNT(*) FROM django_migrations;"
```

検証時の結果:

```text
Tables: 20
django_migrations: 25
```

## 7. Verify Application Data

restore DBの主要データ件数を確認します。

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml exec -T db \
  psql -U "$POSTGRES_USER" -d "$RESTORE_DB" \
  -c "
SELECT
  (SELECT COUNT(*) FROM api_recipe) AS recipes,
  (SELECT COUNT(*) FROM api_ingredient) AS ingredients,
  (SELECT COUNT(*) FROM api_preptask) AS prep_tasks,
  (SELECT COUNT(*) FROM api_shop) AS shops,
  (SELECT COUNT(*) FROM api_membership) AS memberships,
  (SELECT COUNT(*) FROM auth_user) AS users;
"
```

必要に応じて現在の公開DBでも同じqueryを実行し、件数を比較します。

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml exec -T db \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" \
  -c "
SELECT
  (SELECT COUNT(*) FROM api_recipe) AS recipes,
  (SELECT COUNT(*) FROM api_ingredient) AS ingredients,
  (SELECT COUNT(*) FROM api_preptask) AS prep_tasks,
  (SELECT COUNT(*) FROM api_shop) AS shops,
  (SELECT COUNT(*) FROM api_membership) AS memberships,
  (SELECT COUNT(*) FROM auth_user) AS users;
"
```

検証時にはrestore DBと元DBで以下の件数が一致しました。

```text
recipes:      4
ingredients: 21
prep_tasks:   4
shops:        1
memberships:  2
users:        2
```

backup取得後に公開DBが変更されている場合、件数が完全一致しないこと自体はrestore失敗を意味しません。

backup取得時点のデータとして妥当かを確認します。

## 8. Verify Through Django

公開中のbackendは変更せず、一時コンテナだけをrestore DBへ接続します。

### Django system check

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml run --rm \
  -e POSTGRES_DB="$RESTORE_DB" \
  backend python manage.py check
```

検証時の結果:

```text
System check identified no issues (0 silenced).
```

### Read restored data through Django

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml run --rm \
  -e POSTGRES_DB="$RESTORE_DB" \
  backend python manage.py shell -c \
  "from django.db import connection; c=connection.cursor(); c.execute('SELECT COUNT(*) FROM api_recipe'); print('recipes:', c.fetchone()[0])"
```

検証時の結果:

```text
recipes: 4
```

これにより、PostgreSQLだけでなくDjangoアプリケーションからもrestoreされたデータを参照できることを確認しました。

## 9. Cleanup

削除前に対象を必ず確認します。

```bash
echo "$RESTORE_DB"
echo "$RESTORE_DIR"
```

期待する例:

```text
ricetta_restore_test_20260810
/tmp/ricetta-restore-test
```

一時DBを削除します。

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml exec -T db \
  dropdb -U "$POSTGRES_USER" "$RESTORE_DB"
```

一時ファイルを削除します。

```bash
rm -rf "$RESTORE_DIR"
```

最後にDB一覧と一時ディレクトリを確認します。

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml exec -T db \
  psql -U "$POSTGRES_USER" -d postgres -c '\l'

ls -ld "$RESTORE_DIR" 2>/dev/null || echo "restore directory removed"
```

期待する状態:

- `ricetta` DBが残っている
- restore test DBが存在しない
- `restore directory removed` が表示される

## Verification Result

以下を検証済みです。

- S3から `.sql.gz` backupを取得できる
- gzipファイルの整合性を確認できる
- 公開デモDBとは別の一時DBを作成できる
- backupからPostgreSQLへrestoreできる
- 20テーブルが復元される
- `django_migrations` が25件復元される
- 主要データ件数が元DBと一致する
- Django system checkが成功する
- Djangoからrestore DBのデータを参照できる
- 公開デモDBへ影響を与えずに検証できる
- 検証後に一時DB・一時ファイルを削除できる

## Notes

この手順はrestoreテストとして検証済みです。

公開中の `ricetta` DBへ直接restoreする手順は、このドキュメントの対象外です。

将来的には定期的なrestore drillを実施し、バックアップが継続して復元可能であることを確認する運用を検討します。
