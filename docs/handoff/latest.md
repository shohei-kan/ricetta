# Ricetta Handoff Latest

## Date

2026-05-10

## Project

Ricetta

## Status

Docker development startup fixed

## Summary

Docker開発環境の起動エラーを修正した。frontendはVite 8の要求に合わせてNode.js 22へ更新し、backendはDocker内部でPostgreSQLへ `db:5432` 接続する構成を確認した。ホスト側PostgreSQL公開ポートは `localhost:5433`。

## Current Goal

次はブラウザで `http://localhost:5174` を開き、ログイン後の主要画面とAPI proxyの実操作を確認する。

## Current State

- `docker compose up --build -d` で db / backend / frontend が起動する。
- dbはコンテナ内 `5432`、ホスト公開 `5433`。
- backendは `POSTGRES_HOST=db` / `POSTGRES_PORT=5432` で接続する。
- frontendはNode.js `v22.22.2` でVite dev serverが起動する。
- frontendのDocker内API proxyは `http://backend:8000` を向く。

## What Was Done

- `frontend/Dockerfile` のベースイメージをNode 22へ更新した。
- Alpine/musl系のVite native binding問題を避けるため `node:22-bookworm-slim` を採用した。
- `docker-compose.yml` のdb公開ポートを `5433:5432` にし、backendのDB接続ポートは `5432` のまま維持した。
- frontend serviceに `VITE_API_PROXY_TARGET=http://backend:8000` を追加した。
- frontend起動時に `npm ci` を実行し、`/app/node_modules` volume内の依存をコンテナ環境に合わせるようにした。
- Vite proxy targetを環境変数で切り替えられるようにした。
- `.env.example` / local `.env` / READMEの開発ポート説明を更新した。

## Key Decisions

- Docker Compose内部通信ではホスト公開ポートではなくコンテナポートを使う。backend -> db は `db:5432`。
- ホストからDBを見る場合だけ `localhost:5433` を使う。
- Docker内frontendからbackendへproxyするため、Django `ALLOWED_HOSTS` には `backend` を含める。
- `/app/node_modules` volumeが古い optional native dependencyを保持するとViteが落ちるため、frontendコンテナ起動時に `npm ci` する。

## Key Files

- `docker-compose.yml`
- `frontend/Dockerfile`
- `frontend/vite.config.ts`
- `.env.example`
- `.env`
- `README.md`
- `docs/handoff/latest.md`

## Verification

実行済み:

```bash
docker compose config
docker compose down
docker compose up --build
docker compose up --build -d
docker compose ps
docker compose exec frontend node -v
docker compose exec backend python manage.py check
docker compose exec backend python -c "import os, socket; print(os.getenv('POSTGRES_HOST'), os.getenv('POSTGRES_PORT')); s=socket.create_connection(('db', 5432), 3); print('db socket ok'); s.close()"
docker compose exec frontend node -e "fetch('http://backend:8000/api/v1/health/').then(async r=>{console.log(r.status); console.log(await r.text())})"
docker compose exec frontend npm run build
docker compose exec frontend npm run lint
```

Result:

- Docker config: backend `POSTGRES_PORT=5432`, db published `5433:5432`, frontend published `5174:5173`
- `docker compose up --build`: db ready, backend running, frontend Vite ready
- Frontend Node: `v22.22.2`
- Backend check: pass
- Backend -> db socket: `db 5432`, `db socket ok`
- Frontend -> backend proxy target health request: HTTP 401 with auth-required JSON, meaning host/proxy reaches Django
- Frontend build: pass
- Frontend lint: pass
- このCodex実行環境からホスト公開ポートへの直接 `curl localhost:5174/8010` は接続できなかったが、`docker compose ps` ではpublish済み。ユーザーのMacブラウザ/TablePlus側で最終確認する。

## Current Product Scope

MVP対象:

- Login / logout
- Shop account scope
- Dashboard summary
- Recipe list/detail/create/edit
- Ingredient create/edit
- Ingredient cost mode
- Basic food cost calculation
- Today's prep list
- Prep task status update
- Smartphone layout
- Tablet landscape layout
- SettingsでCategory / Unit管理

## Out of Scope for MVP

- Stripe payment / Checkout / Billing Portal
- POS integration
- Multi-shop management UI
- Automatic inventory deduction
- Advanced ordering
- AI auto-classification
- Nutrition calculation
- HACCP reports
- Advanced role management
- Shop device mode
- Full prep inventory / expiry alerts
- Drag-and-drop prep operation
- Image upload implementation

## Next Recommended Tasks

1. Macのブラウザで `http://localhost:5174` を開いて主要画面を確認する
2. TablePlus等で `localhost:5433` / db `ricetta` / user `ricetta` へ接続できるか確認する
3. 必要ならホスト公開ポートをREADMEの開発環境説明にさらに詳しく追記する
4. UI polish後のスマホ幅・タブレット横・PC幅の目視確認を続ける

## Open Questions

- Staffの原価情報閲覧制限をどのPhaseで入れるか
- 標準Unitの追加・変更をdata migrationで固定するか、seed command運用に寄せるか
- `unit_cost_label` / `cost_summary` の丸めを将来どこまで厳密にするか
- Ingredientの仕入価格履歴をどのPhaseで扱うか
- RecipeIngredientの個別編集APIを将来追加するか、nested replacementのまま進めるか
- PrepTask deleteを将来論理削除へ変えるか
- Dashboardの `frequent_recipes` を将来どの期間で集計するか
- 本番frontendでSession Auth / CSRF / CORSの境界をどの構成にするか
- Prep Todayの日付切り替えUIをどのタイミングで入れるか
- Prep Action Modalを入れるか、カード内ボタンのまま進めるか
- Recipe formで材料行・工程行の並び替えUIを入れるか
- Recipe formで原価プレビューを表示するか
- Recipe Detail以外からPrepTaskを作成する専用導線が必要か
- Settingsで店舗情報編集をMVPに含めるか

## Notes for Next Agent

- Login開発用アカウントは `owner@example.com` / `password`。
- frontendは `shop_id` を送らず、backend responseを表示する。
- API clientは `frontend/src/api/api.ts`。
- Docker起動URLは frontend `http://localhost:5174`、backend `http://localhost:8010`、DB host access `localhost:5433`。
- Docker内部では backend -> db は必ず `db:5432`。
- frontend Dockerfileは `node:22-bookworm-slim`。Vite/Rolldownのnative bindingを安定させるためAlpineは避けている。
- frontend serviceは起動時に `npm ci` する。`/app/node_modules` volumeが古い依存を保持する問題への対策。
- frontend Docker内API proxyは `VITE_API_PROXY_TARGET=http://backend:8000`。

## Suggested Commit Message

```text
fix(docker): align ricetta dev ports and update frontend node
```
