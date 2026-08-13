# Ricetta Handoff Latest

## Date

2026-08-13

## Project

Ricetta

## Status

GitHub Issue #29「Stabilize demo reset shop identification」を実装し、commit前レビューとPostgreSQL検証まで完了。commit / push / 本番変更は未実施。

## Summary

公開デモShopを可変の店舗名ではなく、内部識別子 `demo_key=portfolio-demo` で特定するようにした。既存DBは既知ownerのMembership候補が厳密に1件の場合だけ自動移行し、曖昧な場合はfail closedで停止する。reset全体をtransaction化した。

## Current Goal

Issue #29のmigrationと既存production DB移行フローをレビューし、安全な本番反映手順を確認する。

## Current State

- Branch: `fix/issue-29-demo-shop-key`
- Shop: nullable / unique / non-editableな内部field `demo_key` を追加
- Demo Shop: `demo_key=portfolio-demo`
- Normal Shop: `demo_key=null`
- Reset target: demo_keyを優先し、初回だけ既知owner Membershipから移行
- Reset transaction: Shop解決、既存データ削除、再seedまで単一transaction
- API / admin edit form: demo_keyを非公開

## What Was Done

- Shop modelとmigrationへnullable uniqueなdemo_keyを追加した。
- seed/resetの店舗名依存を削除し、demo_key lookupへ変更した。
- 既存ownerのMembershipが厳密に1件かつactiveなowner roleなら既存Shopへdemo_keyを付与する移行処理を追加した。
- 0件、複数件、role不一致、inactive、既存keyとのShop不一致ではCommandErrorにして削除・新規Shop作成を止めた。
- commit前レビューでowner role / active確認と既存keyとの所属整合性チェックを追加し、demo_keyをnon-editableに強化した。
- reset時にShop / Membership / Userを維持し、デモデータだけを削除・再投入するようにした。
- reset後に店舗名、owner / staff、Membership、デモデータを既定状態へ戻すようにした。
- 管理コマンド全体をtransaction.atomicで保護した。
- 新規DB、既存移行、曖昧候補、改名後reset、冪等性、rollback、API非露出、DB一意制約をテストした。
- data model、demo運用docs、AWS systemd運用docsを更新した。

## Key Decisions

- demo_keyはURL用slugや環境変数のShop IDではなく、DB内の内部識別子とする。
- 既存demo_keyがあれば常にそのShopを正本とする。
- demo_keyがなく既知ownerが存在する場合、Membership候補が厳密に1件のときだけ移行する。
- demo ownerが存在しない完全な新規DBでは新しいdemo Shopを作成する。
- 店舗名は表示名として変更可能なままにし、reset時に既定名へ戻す。

## Key Files

- `backend/api/models.py`
- `backend/api/admin.py`
- `backend/api/migrations/0008_shop_demo_key.py`
- `backend/api/management/commands/seed_portfolio_data.py`
- `backend/api/tests/test_seed_portfolio_data.py`
- `docs/technical/data-model.md`
- `docs/deploy/demo/demo.md`
- `docs/deploy/demo/aws-demo-env.md`

## Verification

- Demo seed/reset tests: 14 passed
- Backend tests: 176 passed
- `python manage.py check`: pass
- `python manage.py makemigrations --check --dry-run`: no changes detected
- Migration 0008 apply / rollback / reapply on isolated SQLite DB: pass
- Fresh seed, renamed Shop reset twice, owner / staff authentication on isolated DB: pass
- PostgreSQL 15 migration apply / rollback / reapply: pass
- PostgreSQL 15 nullable unique、renamed Shop reset twice、data counts、owner / staff authentication: pass
- `git diff --check`: pass

`.env.prod`、production DB、production secret、GitHub、本番環境は変更していない。

## Current Product Scope

- Public demo seed/reset safety
- Stable internal demo Shop identification
- Existing demo DB migration

## Out of Scope for MVP

- DEMO_SHOP_ID environment variable
- Public or URL-facing Shop slug
- Demo data content changes
- Frontend UI changes

## Next Recommended Tasks

1. migrationと既存owner Membership候補の本番状態をread-onlyで確認する。
2. backup後にmigrationを適用する。
3. 手動resetを1回実行し、demo_key、Shop ID、owner/staff login、デモデータを確認する。
4. systemd serviceを手動実行してからtimer運用へ戻す。

## Open Questions

- なし。

## Notes for Next Agent

- migration自体はnullable field追加だけで、既存Shopへのdemo_key付与は最初のseed/reset実行時に行う。
- owner@example.comのMembershipが一意なactive owner roleでない場合や、demo keyのShopと所属先が違う場合、resetは意図的に停止する。
- systemd service / timerとreset command lineは変更不要。
- rollback testはデータ削除と大部分の再seed後に例外を発生させ、元の店舗名・追加材料・Recipe変更が戻ることを確認する。

## Suggested Commit Message

```text
fix(demo): identify reset shop by internal key
```
