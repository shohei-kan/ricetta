# Ricetta Handoff Latest

## Date

2026-08-12

## Project

Ricetta

## Status

GitHub Issue #25「Production security hardening」の実装・ローカル検証は完了。commit / pushは未実施。

## Summary

production設定をfail closedにし、HTTPS security settings、Session Authentication限定、login throttle、genericな認証失敗、Caddyでの `/admin` 非公開化を追加した。公開デモ用owner / staff passwordは運用secretではないため現状を維持した。

## Current Goal

Issue #25の差分をレビューし、本番反映手順に沿って安全にデプロイする。

## Current State

- Branch: `security/issue-25-production-hardening`
- production Compose: 外部参照する10変数を必須化
- production Django: 必須設定の欠落・空文字・placeholderを拒否
- DRF authentication: Sessionのみ
- login throttle: Caddy 1段を前提にIP単位で `5/minute`
- public `/admin`: Caddyで404
- HSTS: 3600秒、includeSubDomains / preloadは無効

## What Was Done

- `DJANGO_DEBUG=False` でsecret、host、CSRF origin、DB接続設定をfail closedにした。
- Secure Cookie、SSL redirect、proxy SSL header、段階的HSTSを設定した。
- Docker内部health checkへforwarded HTTPS headerを付けた。
- Basic Authenticationを外し、Session Authenticationと既存401 responseを維持した。
- login専用throttleとgenericな認証失敗responseを追加した。
- Caddyで `/admin` 以下を404にし、API・static・SPA routingを維持した。
- auth、CSRF、権限、production settings、Caddy、health checkのtestを追加した。
- deployとAPI docsへ設定理由、確認、rollback、制約を追記した。

## Key Decisions

- 開発用fallbackは `DJANGO_DEBUG=True` に限り、本番相当環境では使用しない。
- HSTSは影響を限定するため3600秒から開始し、subdomainとpreloadには広げない。
- Caddyの標準転送と内部health checkの明示headerにより、DjangoがHTTPS requestとして認識できるようにする。
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
- `python manage.py check`: pass
- production-like `python manage.py check --deploy`: pass with expected W005 / W021 only
- Frontend `npm run lint`: pass
- Frontend `npm run build`: pass
- Production image build: pass
- Compose config with `.env.prod.example`: pass
- Compose config without required env: expected failure
- Caddy config validation: valid、warningなし
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
2. Bitwardenを正本とする既存 `.env.prod` の必須10変数を確認する。
3. deploy docsの手順でbuild、migration、health、login、role、admin、security headerを確認する。

## Open Questions

- trafficや構成拡張時に共有cacheを使うrate limitingへ移行するか。
- 3600秒の運用確認後にHSTS期間を段階的に延長するか。

## Notes for Next Agent

- `.env.prod` やsecret実値をGit、Issue、PR、docs、ログへ出さない。
- `check --deploy` のW005 / W021は意図したHSTS方針によるもの。
- rollback後もbrowserが最大1時間HSTSを保持する点に注意する。

## Suggested Commit Message

```text
fix(security): harden production configuration
```
