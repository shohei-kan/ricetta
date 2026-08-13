# Ricetta Handoff Latest

## Date

2026-08-13

## Project

Ricetta

## Status

Issue #25のproduction backend health check hotfixを実装・ローカル検証済み。commit / pushは未実施。

## Summary

内部health checkが接続先の `127.0.0.1` をHostとして送り、公開hostだけを許可するDjangoから400になる問題を修正した。`DJANGO_ALLOWED_HOSTS` の先頭hostをHost headerに使い、HTTPS転送headerとproduction security設定は維持した。

## Current Goal

health check hotfixの差分をレビューし、本番反映手順に沿って再デプロイする。

## Current State

- Branch: `fix/production-backend-health-host`
- production Compose: 外部参照する10変数を必須化
- production Django: 必須設定の欠落・空文字・placeholderを拒否
- DRF authentication: Sessionのみ
- login throttle: Caddy 1段を前提にIP単位で `5/minute`
- public `/admin`: Caddyで404
- HSTS: 3600秒、includeSubDomains / preloadは無効
- backend health check: `DJANGO_ALLOWED_HOSTS` の先頭hostと `X-Forwarded-Proto: https` を送信

## What Was Done

- `docker-compose.prod.yml` のbackend health checkで `DJANGO_ALLOWED_HOSTS` を環境変数から取得するようにした。
- カンマ区切りの先頭hostをtrimしてHost headerへ設定した。
- `X-Forwarded-Proto: https` を維持した。
- production health checkのHost選択と両headerを固定する回帰テストを追加した。

## Key Decisions

- 開発用fallbackは `DJANGO_DEBUG=True` に限り、本番相当環境では使用しない。
- HSTSは影響を限定するため3600秒から開始し、subdomainとpreloadには広げない。
- Caddyの標準転送と内部health checkの明示headerにより、DjangoがHTTPS requestとして認識できるようにする。
- 内部接続先は `127.0.0.1` のまま、HTTP Hostだけを許可済みproduction hostに合わせる。
- 公開デモpasswordはREADMEで公開され、定期resetにも使う非secretのため変更しない。

## Key Files

- `backend/ricetta/settings.py`
- `backend/api/authentication.py`
- `backend/api/serializers.py`
- `backend/api/views.py`
- `backend/api/tests/test_auth.py`
- `backend/api/tests/test_security_settings.py`
- `docker-compose.prod.yml`
- `Caddyfile`
- `docs/deploy/demo/aws-demo-env.md`
- `docs/technical/api-design.md`

## Verification

- Backend tests: 161 passed
- Production security / health check tests: 6 passed
- Compose config with `.env.prod.example`: pass
- `git diff --check`: pass

EC2、AWS、Bitwarden、`.env.prod`、production secretは変更していない。

## Current Product Scope

- AWS EC2 public demo
- Session Authentication + CSRF
- Bitwarden-based production secret management
- Caddy HTTPS reverse proxy

## Out of Scope for MVP

- Distributed rate limiting across processes / instances
- HSTS preload / includeSubDomains
- Public Django admin
- New external security services or dependencies

## Next Recommended Tasks

1. 差分をレビューしてcommitする。
2. productionへ再デプロイし、backendコンテナがhealthyになることを確認する。
3. 外部HTTPS health endpointが引き続き200になることを確認する。

## Open Questions

- trafficや構成拡張時に共有cacheを使うrate limitingへ移行するか。
- 3600秒の運用確認後にHSTS期間を段階的に延長するか。

## Notes for Next Agent

- `.env.prod` やsecret実値をGit、Issue、PR、docs、ログへ出さない。
- `check --deploy` のW005 / W021は意図したHSTS方針によるもの。
- rollback後もbrowserが最大1時間HSTSを保持する点に注意する。

## Suggested Commit Message

```text
fix(deploy): use allowed host for backend health check
```
