# Ricetta Handoff Latest

## Date

2026-08-13

## Project

Ricetta

## Status

GitHub Issue #27「Make recipe nested writes transactional」を実装・ローカル検証済み。commit / pushは未実施。

## Summary

Recipe作成・更新時のRecipe本体、RecipeIngredient、RecipeStepのnested write全体をtransactionで保護した。途中のDB処理で例外が発生しても、親だけの保存や既存nested dataの削除が残らないことを回帰テストで確認した。

## Current Goal

Issue #27の差分をレビューし、CI確認後に取り込む。

## Current State

- Branch: `fix/issue-27-recipe-transactions`
- Recipe create / update: serializerメソッド全体を `transaction.atomic()` で保護
- Nested update: `ingredients` / `steps` 指定時の全件置換方式を維持
- Shop scope: Category / Ingredient / Unitの既存scoped field validationを維持
- Permissions: ownerのみ作成・更新可、staffは403の既存仕様を維持
- Model / migration / API response shape: 変更なし

## What Was Done

- RecipeSerializerのcreate全体をtransaction化した。
- RecipeSerializerのupdate全体をtransaction化した。
- createで親と材料の保存後に手順作成が失敗した場合のrollback testを追加した。
- updateで親更新、旧nested削除、新材料作成後に手順作成が失敗した場合のrollback testを追加した。
- 存在しないCategory / Ingredient / Unit IDの拒否テストを追加した。
- API designへnested writeのtransaction方針を追記した。

## Key Decisions

- transaction境界はRecipeSerializerの各create / updateメソッド全体とする。
- 既存の事前validation、全件置換方式、エラー形式、owner / staff権限は変更しない。
- rollback testはmockしたRecipeStep作成で実行時例外を発生させ、それ以前のDB write / deleteが実際に行われたことを失敗直前に確認する。

## Key Files

- `backend/api/serializers.py`
- `backend/api/tests/test_recipes.py`
- `docs/technical/api-design.md`
- `docs/handoff/latest.md`

## Verification

- Recipe tests: 40 passed
- Backend tests: 165 passed
- `python manage.py check`: pass
- `python manage.py makemigrations --check --dry-run`: no changes detected
- `git diff --check`: pass

`.env.prod`、production secret、GitHub、本番環境は変更していない。

## Current Product Scope

- Recipe nested create / update
- Shop-scoped Category / Ingredient / Unit references
- Owner-only Recipe writes

## Out of Scope for MVP

- Nested write UI変更
- Nested rowsの差分更新
- 深いRecipe循環参照の完全なグラフ検証
- Model / migration変更

## Next Recommended Tasks

1. 差分とrollback testのfailure injection箇所をレビューする。
2. CIでbackend testsを確認する。
3. ownerでRecipe create / updateのfrontend smoke testを行う。

## Open Questions

- なし。

## Notes for Next Agent

- Recipeのnested updateは引き続き、送信されたcollectionだけを全件置換する。
- shop scope拒否はDB transactionに入る前のserializer field validationで行う。
- transaction testはvalidation errorではなく、RecipeStep write時の実行時例外を利用している。

## Suggested Commit Message

```text
fix(api): make recipe nested writes transactional
```
