# 0002 Shop Scope

## Date

2026-05-04

## Status

Accepted

## Context

Ricetta は将来的なSaaS化を前提にしています。

SaaS化する場合、複数の店舗が同じアプリを使うことになります。

そのため、店舗Aのレシピ・材料・仕込み情報が、店舗Bから見えてはいけません。

MVPでは1店舗・1Ownerに近い運用で始めますが、将来的に複数店舗・複数ユーザーへ拡張できる設計が必要です。

## Decision

Ricettaでは、Shopをデータ分離の基本単位にします。

主要データはすべて `shop_id` を持ちます。

対象：

- Recipe
- Ingredient
- PrepTask
- Category
- Unit
- PrepLog, future
- Subscription, future

ユーザーと店舗の関係は `Membership` で管理します。

```text
User
Shop
Membership
```

MVPでは1ユーザー1店舗でもよいですが、データモデル上はMembershipを用意します。

## Backend Rule

APIでは、フロントから送られた `shop_id` を信用しません。

サーバー側でログインユーザーからShopを特定します。

```text
request.user
→ Membership
→ shop
→ shop_idでquerysetをfilter
```

作成時も、フロントから `shop_id` を受け取るのではなく、サーバー側で現在のShopを設定します。

## Reasons

### 1. SaaS化に必要な土台だから

Ricettaは将来的にサブスク化を想定しています。

店舗ごとのデータ分離は、SaaS化の前提です。

### 2. セキュリティ上必須だから

フロントから `shop_id` を送る設計にすると、他店舗のIDを指定されるリスクがあります。

必ずサーバー側で所属店舗を判定します。

### 3. 将来の複数店舗管理に対応しやすいから

Membershipを使えば、将来的に以下のような運用が可能になります。

```text
User A は 店舗A の owner
User A は 店舗B の viewer
```

MVPでは使いませんが、拡張余地を残せます。

## Consequences

### Positive

- SaaS化しやすい
- 他店舗データ混入を防げる
- 権限管理を拡張しやすい
- API設計のルールが明確になる

### Negative

- MVPとしては少しだけモデルが増える
- UserとShopを直接紐づけるより実装が少し複雑
- Membership取得の共通処理が必要

## MVP Simplification

MVPでは、以下のように簡略化してよいです。

- 1ユーザー1店舗を前提にする
- roleは `owner` / `staff` 程度にする
- Staffの細かい権限制御は後回し
- Shop切り替えUIは作らない

ただし、データは必ずShopに紐づけます。

## Related Docs

- `docs/technical/data-model.md`
- `docs/technical/api-design.md`
- `docs/product/mvp-requirements.md`
