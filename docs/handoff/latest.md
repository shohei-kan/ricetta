# Ricetta Handoff Latest

## Date

2026-07-28

## Project

Ricetta

## Status

README reflects the published public demo state.

## Summary

READMEをAWS公開デモ完了後の状態に合わせて更新した。Public Demo Environmentに実URL、owner/staffデモアカウント、自動reset、AWS EC2 + Docker Compose + PostgreSQL + Gunicorn + Caddy HTTPS構成を明記し、Current Statusから未デプロイ表現を削除した。公開デモURL共有用のmeta / OGP / noindex整備も反映済み。

## Current Goal

次はAWS公開デモへfrontend変更を反映し、`https://ricetta.lintake.net/ogp.png`、favicon、共有プレビュー、DemoBanner、owner/staffログインを実ブラウザで確認する。

## Current State

- 公開URLは `https://ricetta.lintake.net`。
- production構成は `docker-compose.prod.yml` を使う。
- productionは backend / frontend / db / caddy の4サービス構成。
- backendはDjango + gunicorn。
- frontendはVite build済みdistをCaddyで配信する。
- 外向きCaddyはHTTPS / reverse proxyを担当する。
- backend healthcheckは `/api/v1/health/` を使い、未認証でも200を返す。
- demo data resetは `seed_portfolio_data --reset` を使う。
- EC2上では `ricetta-demo-reset.service` / `ricetta-demo-reset.timer` により、EC2起動時・再起動時と毎日04:30 JSTに自動resetされる。
- `docs/deploy/demo.md` は公開デモの仕様説明。
- `docs/deploy/aws-demo-env.md` はAWS EC2 + Docker Compose公開時のenvと運用コマンド確認用。
- READMEは公開済みportfolio demoの状態に更新済み。
- Recipe / Ingredient / prep recipe materialization / production compose / auto reset / OGP整備の詳細履歴は `docs/handoff/archive/release-prep.md` に移動済み。

## What Was Done

- `frontend/index.html` に公開デモ共有用のmeta情報を追加した。
- `frontend/public/favicon.png` をfavicon / apple-touch-iconに設定した。
- `frontend/public/ogp.png` をOGP / Twitter Card画像として参照するようにした。
- READMEのPublic Demo Environmentに、Ricettaアプリ本体はnoindexで、発見導線はLINTAKE WorksページとGitHub READMEに寄せる方針を追記した。
- READMEのPublic Demo Environment、Architecture、Current Status、Future Improvementsを公開済み状態へ更新した。
- `docs/handoff/archive/release-prep.md` に `2026-07-28 Public demo launch polish` を追加し、長くなった公開準備ログを退避した。
- `docs/handoff/latest.md` を次作業向けの短い現在地情報に整理した。

## Key Decisions

- Ricettaアプリ本体は `noindex, nofollow` とし、検索・発見導線はLINTAKE WorksページとGitHub READMEに寄せる。
- OGP画像は `frontend/public/ogp.png` を使い、HTMLでは絶対URL `https://ricetta.lintake.net/ogp.png` を指定する。
- Handoffの詳細履歴は `latest.md` に溜めず、作業テーマごとにarchiveへ追記する。
- 今回の公開準備履歴は `docs/handoff/archive/release-prep.md` に集約する。

## Key Files

- `frontend/index.html`
- `frontend/public/favicon.png`
- `frontend/public/ogp.png`
- `README.md`
- `docs/handoff/latest.md`
- `docs/handoff/archive/release-prep.md`
- `docs/deploy/demo.md`
- `docs/deploy/aws-demo-env.md`

## Verification

実行済み:

```bash
cd frontend
npm run lint
npm run build
ls -lh frontend/public/ogp.png
grep -n "og:image\|twitter:image\|robots\|description\|title" frontend/index.html
grep -n "Public Demo Environment\|Current Status\|Future Improvements" -A30 README.md
git diff --check
```

Result:

- frontend lint: pass
- frontend build: pass
- `frontend/public/ogp.png` 存在確認: pass
- `frontend/index.html` のOGP / Twitter Card / robots / description / title確認: pass
- READMEのPublic Demo Environment / Current Status / Future Improvements確認: pass
- whitespace check: pass

Manual browser verification:

- 未実施。次にAWS公開デモへ反映後、実ブラウザと共有プレビューを確認する。

## Current Product Scope

- Login / logout and Shop scope
- owner / staff role control for MVP operations
- Recipe / Ingredient / Prep Today / Dashboard / Settings / Account
- Recipe type distinction between prep recipes and menu recipes
- Prep recipes as reusable ingredients through `ingredient_type=prep_recipe`
- Active Prep Today board and direct PrepTask creation
- BoardMemo as lightweight whiteboard memo under Prep Today columns
- Smartphone, tablet landscape, and PC layouts
- Demo mode via environment variables
- Safe portfolio demo seed reset
- Production demo deployment on EC2 + Docker Compose + Caddy HTTPS
- Public demo share metadata

## Out of Scope for MVP

- Stripe / Checkout / Billing portal
- POS integration
- Automatic inventory deduction
- Advanced ordering
- Multi-shop management UI
- Advanced role management beyond owner / staff
- Shop device mode
- Yield loss / waste rate / cooked weight
- Complex unit conversion table
- Automatic Ingredient creation button from prep Recipe
- Full deep cycle validation before save
- Demo reset API / reset button
- AWS構成のECS / ALB / RDS分離
- Demo-specific branch or duplicated app directories

## Next Recommended Tasks

1. EC2でfrontend imageを再buildし、Caddyをrestartしてmeta / favicon / OGP変更を反映する。
2. `https://ricetta.lintake.net/ogp.png` が200で表示されることを確認する。
3. faviconがブラウザタブに表示されることを確認する。
4. Slack / Notion / GitHub README等で共有プレビューを確認する。OGPキャッシュで即時反映されない場合がある点に注意する。
5. DemoBanner、owner/staffログイン、カポナータのトマトソース由来Ingredient表示を確認する。
6. EC2停止/再開後は `docs/deploy/aws-demo-env.md` のOperation checksとCheck auto resetに沿ってproduction composeと自動reset timerを確認する。

## Open Questions

- OGP共有プレビューのキャッシュ更新をどのサービスで確認するか。
- LINTAKE Worksページ側にもRicetta公開デモURLとGitHub README導線をどう掲載するか。

## Notes for Next Agent

- `frontend/public/ogp.png` は未追跡ファイルとして追加されている可能性がある。コミット時に含める。
- `frontend/public/favicon.png` は既にRicettaアイコンとして使う。
- frontend meta変更をAWSへ反映するにはfrontend imageの再buildが必要。
- 反映例:

```bash
ssh ricetta
cd /srv/ricetta
git pull
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build frontend
docker compose --env-file .env.prod -f docker-compose.prod.yml restart caddy
```

- production composeは `--env-file .env.prod` 付きで使う。
- EC2側の実secret / `.env.prod` の値はdocsやリポジトリに書かない。
- 詳しい公開準備履歴は `docs/handoff/archive/release-prep.md` の `2026-07-28 Public demo launch polish` を参照する。
- Docker frontendのローカル開発URLは `http://localhost:5174`。

## Suggested Commit Message

```text
docs(readme): update public demo status
```
