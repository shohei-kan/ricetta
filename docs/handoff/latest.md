# Ricetta Handoff Latest

## Date

2026-06-29

## Project

Ricetta

## Status

Account Phase 1 + 2 implemented; local CSRF origins fixed

## Summary

保護ルート `/account` とAccountページを追加した。店舗情報はownerのみ更新可能、Membershipの表示名はowner / staffとも本人が更新可能。ローカルViteの5173 / 5174 OriginからSession認証のPATCHが通るようCSRF trusted originsを設定した。

## Current Goal

実ブラウザでowner / staff表示とPC・スマホレイアウトを目視確認し、必要なら余白を調整する。

## Current State

- `GET /api/v1/auth/me/` はmembershipの `role` と `display_name` を返す。
- `PATCH /api/v1/auth/me/` で現在Membershipの表示名を更新できる。
- `GET /api/v1/shop/me/` はowner / staffとも利用できる。
- `PATCH /api/v1/shop/me/` はownerのみ利用でき、staffは403となる。
- `/account` では店舗情報、自分のメール・表示名・権限、ログアウトを扱う。
- メール変更、パスワード変更、複数店舗切り替えは未実装。
- 開発時の `CSRF_TRUSTED_ORIGINS` は `http://localhost:5173,http://localhost:5174`。

## What Was Done

- Membership表示名更新用Serializerと `PATCH /auth/me/` を追加した。
- owner Membership判定を `shop_scope.py` に追加した。
- 店舗更新をowner限定にした。
- owner / staffの表示名更新、店舗更新権限テストを追加した。
- frontendにShop API clientとAccountページを追加した。
- `/account` を保護ルートへ追加した。
- サイドバーの店舗名・権限ブロックをAccount導線へ変更した。
- スマホヘッダーへAccount導線を追加した。
- ログアウトをAccountページ下部へ移動した。
- API設計書と画面仕様を更新した。
- `DJANGO_CSRF_TRUSTED_ORIGINS` を追加し、開発既定値へViteの5173 / 5174を設定した。
- backendを再起動し、両OriginからAccount関連PATCHが200になることを確認した。
- 完了履歴を `archive/frontend-implementation.md` と `archive/backend-foundation.md` に保存した。
- READMEをAccount機能、owner / staff権限、CSRF開発Origin、現在ステータスに合わせて更新した。
- READMEを転職用ポートフォリオ向けに再構成し、背景、技術選定、Architecture、backend設計、データモデル、学びを追加した。

## Key Decisions

- 新規モデルは追加せず、標準User・Shop・Membershipを利用する。
- 表示名は店舗内の情報として `Membership.display_name` に保存する。
- staffは店舗情報を閲覧できるが更新できない。
- 権限制御はフロント表示だけでなくAPIで強制する。
- Account Phase 1 + 2ではメール・パスワードを変更しない。
- localhostのtrusted originsは開発専用とし、本番では環境変数で本番Originだけに上書きする。

## Key Files

- `backend/api/shop_scope.py`
- `backend/api/serializers.py`
- `backend/api/views.py`
- `backend/api/tests.py`
- `backend/ricetta/settings.py`
- `.env.example`
- `README.md`
- `frontend/src/api/auth.ts`
- `frontend/src/api/shop.ts`
- `frontend/src/pages/AccountPage.tsx`
- `frontend/src/App.tsx`
- `frontend/src/components/AppLayout.tsx`
- `docs/api/api-design.md`
- `docs/product/screens.md`

## Verification

実行済み:

```bash
cd frontend && npm run lint
cd frontend && npm run build
docker compose exec backend python manage.py check
docker compose exec backend python manage.py makemigrations --check --dry-run
docker compose exec backend python manage.py test
```

Result:

- Frontend lint: pass
- Frontend build: pass
- Django system check: pass
- Migration check: pass（変更なし）
- Backend tests: pass
- Account関連12テスト: pass
- `Origin: http://localhost:5173` から `PATCH /auth/me/`, `PATCH /shop/me/`: HTTP 200
- `Origin: http://localhost:5174` から `PATCH /auth/me/`, `PATCH /shop/me/`: HTTP 200
- in-app browserが利用できず、PC・スマホの自動目視確認は未実施。

## Current Product Scope

- Login / logout
- Account表示とMembership表示名更新
- owner限定の店舗情報更新
- Shop account scope
- Dashboard / Recipe / Ingredient / Prep / Settings
- Smartphone and tablet landscape layouts

## Out of Scope for MVP

- Accountでのメールアドレス変更
- Accountでのパスワード変更
- 複数店舗切り替え
- Stripe / POS / inventory automation
- Advanced role management

## Next Recommended Tasks

1. ownerで `/account` の店舗情報・表示名更新とログアウトを確認する。
2. staffで店舗情報が閲覧のみ、表示名は更新可能であることを確認する。
3. 390px前後のスマホ幅と1024px前後のタブレット横幅を確認する。
4. 次Phaseでメール変更・パスワード変更の仕様を決める。

## Open Questions

- 複数の有効Membershipがある場合の現在Shop選択方法。
- 将来のメール変更で再認証・メール確認をどこまで必須にするか。

## Notes for Next Agent

- 開発用ログインは `owner@example.com` / `password`。
- 現在Membershipは有効MembershipのID順先頭を採用する。
- 店舗更新権限は `get_current_owner_membership()` で強制する。
- 表示名更新後はfrontendの `refreshMe()` でsession表示を同期する。
- Docker frontendは `http://localhost:5174`。
- 本番の `DJANGO_CSRF_TRUSTED_ORIGINS` にlocalhostを含めない。

## Suggested Commit Message

```text
fix(csrf): trust local Vite development origins
```
