# Ricetta API Design

## 概要

Ricetta のMVPで使用するAPI設計を整理する。

Ricetta は「小さな飲食店のための、レシピ台帳。」をコンセプトにした、小規模飲食店向けレシピ管理SaaS。

MVPでは以下を実現する。

- ログイン
- 店舗スコープ管理
- レシピ管理
- 材料管理
- 原価計算
- 今日の仕込み管理
- 設定管理

## 技術前提

- Backend: Django + Django REST Framework
- DB: PostgreSQL
- API prefix: `/api/v1/`
- 認証: MVPでは Django Session Auth + DRF Basic Auth
- 初期MVPでは決済APIは作らない
- 将来的に Stripe Checkout / Billing を追加予定

## API設計方針

### 1. API prefix

すべてのAPIは以下のprefix配下に置く。

```text
/api/v1/
```

### 2. 店舗スコープ

Ricetta はSaaS化を前提に、店舗単位でデータを分離する。

基本方針：

- Recipe / Ingredient / PrepTask などは必ず `shop_id` を持つ
- APIではログインユーザーの所属Shopで絞り込む
- フロントから送られた `shop_id` を信用しない
- 作成時もサーバー側で `request.user` からShopを決定する

例：

```text
request.user
→ Membership
→ shop
→ shop_idでquerysetをfilter
```

### 3. MVPでは複雑にしすぎない

MVPでは以下を優先する。

- CRUDが分かりやすい
- 1店舗運用を前提にする
- ただし将来SaaS化できる設計にする
- Stripe決済は後から追加できる余地だけ残す

---

# 1. Auth API

## POST /api/v1/auth/login/

ログインする。

### Request

```json
{
  "email": "owner@example.com",
  "password": "password"
}
```

### Response

```json
{
  "user": {
    "id": 1,
    "email": "owner@example.com",
    "name": "山田 太郎"
  },
  "shop": {
    "id": 1,
    "name": "〇〇食堂"
  },
  "membership": {
    "role": "owner"
  }
}
```

### Error

```json
{
  "detail": "メールアドレスまたはパスワードが正しくありません。"
}
```

---

## POST /api/v1/auth/logout/

ログアウトする。

### Response

```json
{
  "detail": "ログアウトしました。"
}
```

---

## GET /api/v1/auth/me/

ログイン中のユーザー情報を取得する。

### Response

```json
{
  "user": {
    "id": 1,
    "email": "owner@example.com",
    "name": "山田 太郎"
  },
  "shop": {
    "id": 1,
    "name": "〇〇食堂"
  },
  "membership": {
    "role": "owner"
  }
}
```

未ログインの場合は `401 Unauthorized` を返す。

---

# 2. Shop API

## GET /api/v1/shop/me/

現在ログイン中のユーザーが所属する店舗情報を取得する。

### Response

```json
{
  "id": 1,
  "name": "〇〇食堂",
  "business_type": "カフェ",
  "memo": "小規模カフェ"
}
```

---

## PATCH /api/v1/shop/me/

店舗情報を更新する。

### Request

```json
{
  "name": "〇〇食堂",
  "business_type": "カフェ",
  "memo": "小規模カフェ"
}
```

### Response

```json
{
  "id": 1,
  "name": "〇〇食堂",
  "business_type": "カフェ",
  "memo": "小規模カフェ"
}
```

---

# 3. Recipe API

## GET /api/v1/recipes/

レシピ一覧を取得する。

### Query Params

```text
q=トマト
category=仕込み
```

### Response

```json
[
  {
    "id": 1,
    "name": "トマトソース",
    "category": {
      "id": 1,
      "name": "仕込み"
    },
    "base_yield_quantity": "1.00",
    "base_yield_unit": {
      "id": 10,
      "name": "バッチ"
    },
    "main_image": null,
    "updated_at": "2026-04-29T10:00:00+09:00"
  }
]
```

---

## POST /api/v1/recipes/

レシピを作成する。

### Request

```json
{
  "name": "トマトソース",
  "category_id": 1,
  "description": "パスタや煮込みに使う基本のトマトソース。",
  "base_yield_quantity": "1",
  "base_yield_unit_id": 10,
  "selling_price": null,
  "notes": "焦げやすいので、煮込み中は定期的に混ぜる。",
  "allergen_notes": "なし",
  "ingredients": [
    {
      "ingredient_id": 1,
      "quantity": "2",
      "unit_id": 7,
      "sort_order": 1
    },
    {
      "ingredient_id": 2,
      "quantity": "300",
      "unit_id": 1,
      "sort_order": 2
    }
  ],
  "steps": [
    {
      "step_number": 1,
      "instruction": "玉ねぎをみじん切りにする。"
    },
    {
      "step_number": 2,
      "instruction": "オリーブオイルでにんにくを弱火で香り出しする。"
    }
  ]
}
```

### Response

```json
{
  "id": 1,
  "name": "トマトソース"
}
```

---

## GET /api/v1/recipes/{id}/

レシピ詳細を取得する。

### Response

```json
{
  "id": 1,
  "name": "トマトソース",
  "category": {
    "id": 1,
    "name": "仕込み"
  },
  "description": "パスタや煮込みに使う基本のトマトソース。",
  "base_yield_quantity": "1.00",
  "base_yield_unit": {
    "id": 10,
    "name": "バッチ"
  },
  "selling_price": null,
  "notes": "焦げやすいので、煮込み中は定期的に混ぜる。",
  "allergen_notes": "なし",
  "ingredients": [
    {
      "id": 1,
      "ingredient": {
        "id": 1,
        "name": "ホールトマト"
      },
      "quantity": "2.00",
      "unit": {
        "id": 7,
        "name": "缶"
      }
    },
    {
      "id": 2,
      "ingredient": {
        "id": 2,
        "name": "玉ねぎ"
      },
      "quantity": "300.00",
      "unit": {
        "id": 1,
        "name": "g"
      }
    }
  ],
  "steps": [
    {
      "id": 1,
      "step_number": 1,
      "instruction": "玉ねぎをみじん切りにする。"
    }
  ],
  "cost_summary": {
    "material_cost": "480",
    "selling_price": null,
    "cost_rate": null,
    "gross_profit": null
  }
}
```

### 方針

材料一覧には原価を含めない。

材料ごとの原価内訳が必要な場合は、将来的に別APIまたは `cost_detail` として追加する。

---

## PATCH /api/v1/recipes/{id}/

レシピを更新する。

### Request

POSTと同じ構造を基本にする。

---

## DELETE /api/v1/recipes/{id}/

レシピを削除する。

MVPでは物理削除でもよいが、将来的には `is_active=false` による論理削除を検討する。

### Response

```json
{
  "detail": "削除しました。"
}
```

---

# 4. Ingredient API

## GET /api/v1/ingredients/

材料一覧を取得する。

ログイン中ユーザーの現在Shopに紐づく `is_active=true` のIngredientのみ返す。

### Query Params

```text
q=トマト
```

### Response

```json
[
  {
    "id": 1,
    "name": "ホールトマト",
    "supplier": "業務スーパー",
    "cost_mode": "conversion",
    "purchase_quantity": "1.00",
    "purchase_unit": {
      "id": 7,
      "name": "缶"
    },
    "purchase_price": "180",
    "usage_unit": {
      "id": 1,
      "name": "g"
    },
    "conversion": {
      "from_quantity": "1.00",
      "from_unit": {
        "id": 7,
        "name": "缶"
      },
      "to_quantity": "400.00",
      "to_unit": {
        "id": 1,
        "name": "g"
      }
    },
    "unit_cost_label": "0.45円 / g"
  }
]
```

---

## POST /api/v1/ingredients/

材料を作成する。

作成時はフロントから `shop_id` を受け取らず、サーバー側で現在Shopを設定する。

Unit指定は `shop = null` の標準Unit、または現在Shopの店舗独自Unitのみ許可する。

### Request: 原価計算しない

```json
{
  "name": "塩少々",
  "supplier": "",
  "memo": "",
  "cost_mode": "none"
}
```

### Request: 仕入単位のまま計算

```json
{
  "name": "卵",
  "supplier": "",
  "memo": "",
  "cost_mode": "same_unit",
  "purchase_quantity": "1",
  "purchase_unit_id": 5,
  "purchase_price": "30",
  "usage_unit_id": 5
}
```

### Request: 使用単位に換算して計算

```json
{
  "name": "ホールトマト",
  "supplier": "業務スーパー",
  "memo": "",
  "cost_mode": "conversion",
  "purchase_quantity": "1",
  "purchase_unit_id": 7,
  "purchase_price": "180",
  "usage_unit_id": 1,
  "conversion_from_quantity": "1",
  "conversion_from_unit_id": 7,
  "conversion_to_quantity": "400",
  "conversion_to_unit_id": 1
}
```

### Response

```json
{
  "id": 1,
  "name": "ホールトマト"
}
```

---

## GET /api/v1/ingredients/{id}/

材料詳細を取得する。

現在ShopのIngredientのみ取得できる。他ShopのIngredientは `404 Not Found`。

---

## PATCH /api/v1/ingredients/{id}/

材料を更新する。

現在ShopのIngredientのみ更新できる。

Unit指定は `shop = null` の標準Unit、または現在Shopの店舗独自Unitのみ許可する。

### cost_mode validation

`none`:

- 必須は `name` のみ
- 仕入数量・仕入単位・仕入価格・使用単位・換算情報は空でも保存できる

`same_unit`:

- `purchase_quantity`, `purchase_unit_id`, `purchase_price`, `usage_unit_id` が必須
- `purchase_quantity > 0`
- `purchase_price >= 0`
- MVPでは `usage_unit_id == purchase_unit_id` を必須にする

`conversion`:

- `purchase_quantity`, `purchase_unit_id`, `purchase_price`, `usage_unit_id`, `conversion_from_quantity`, `conversion_from_unit_id`, `conversion_to_quantity`, `conversion_to_unit_id` が必須
- `purchase_quantity > 0`
- `purchase_price >= 0`
- `conversion_from_quantity > 0`
- `conversion_to_quantity > 0`
- MVPでは `conversion_from_unit_id == purchase_unit_id` を必須にする
- MVPでは `conversion_to_unit_id == usage_unit_id` を必須にする

---

## DELETE /api/v1/ingredients/{id}/

材料を削除する。

MVPでは `is_active=false` による論理削除とする。

現在ShopのIngredientのみ削除できる。他ShopのIngredientは `404 Not Found`。

---

# 5. PrepTask API

## GET /api/v1/prep-tasks/

今日の仕込みタスク一覧を取得する。

### Query Params

```text
date=2026-04-29
```

### Response

```json
{
  "date": "2026-04-29",
  "summary": {
    "todo": 3,
    "doing": 1,
    "done": 2
  },
  "tasks": [
    {
      "id": 1,
      "recipe": {
        "id": 1,
        "name": "トマトソース"
      },
      "planned_quantity": "3.00",
      "planned_unit": {
        "id": 10,
        "name": "バッチ"
      },
      "status": "todo",
      "memo": ""
    }
  ]
}
```

---

## POST /api/v1/prep-tasks/

仕込みタスクを作成する。

### Request

```json
{
  "date": "2026-04-29",
  "recipe_id": 1,
  "planned_quantity": "3",
  "planned_unit_id": 10,
  "memo": ""
}
```

### Response

```json
{
  "id": 1,
  "date": "2026-04-29",
  "status": "todo"
}
```

---

## PATCH /api/v1/prep-tasks/{id}/

仕込みタスクを更新する。

### Request

```json
{
  "planned_quantity": "4",
  "planned_unit_id": 10,
  "memo": ""
}
```

---

## PATCH /api/v1/prep-tasks/{id}/status/

仕込みタスクのステータスを更新する。

### Request

```json
{
  "status": "doing"
}
```

または、

```json
{
  "status": "done"
}
```

### Response

```json
{
  "id": 1,
  "status": "done",
  "completed_at": "2026-04-29T10:30:00+09:00"
}
```

---

## DELETE /api/v1/prep-tasks/{id}/

仕込みタスクを削除する。

---

# 6. Category API

## GET /api/v1/categories/

レシピカテゴリ一覧を取得する。

### Response

```json
[
  {
    "id": 1,
    "name": "仕込み",
    "sort_order": 1
  },
  {
    "id": 2,
    "name": "メイン",
    "sort_order": 2
  }
]
```

---

## POST /api/v1/categories/

カテゴリを作成する。

### Request

```json
{
  "name": "ソース",
  "sort_order": 5
}
```

---

## PATCH /api/v1/categories/{id}/

カテゴリを更新する。

ログイン中ユーザーの現在Shopに紐づくカテゴリのみ更新できる。

---

## DELETE /api/v1/categories/{id}/

カテゴリを削除する。

MVPでは `is_active=false` による論理削除とする。

ログイン中ユーザーの現在Shopに紐づくカテゴリのみ削除できる。

---

# 7. Unit API

## GET /api/v1/units/

単位一覧を取得する。

`shop = null` の標準単位と、ログイン中ユーザーの現在Shopに紐づく店舗独自単位を返す。

### Response

```json
[
  {
    "id": 1,
    "name": "g",
    "unit_type": "weight",
    "is_default": true,
    "is_standard": true
  },
  {
    "id": 7,
    "name": "缶",
    "unit_type": "custom",
    "is_default": true,
    "is_standard": true
  }
]
```

---

## POST /api/v1/units/

店舗独自の単位を作成する。

### Request

```json
{
  "name": "ポーション",
  "unit_type": "custom"
}
```

---

## PATCH /api/v1/units/{id}/

単位を更新する。

標準単位（`shop = null`）は更新できない。店舗独自単位のみ更新できる。

---

## DELETE /api/v1/units/{id}/

単位を削除する。

標準単位（`shop = null`）は削除できない。店舗独自単位のみ `is_active=false` による論理削除とする。

---

# 8. Dashboard API

## GET /api/v1/dashboard/

Dashboard表示に必要な情報を取得する。

### Query Params

```text
date=2026-04-29
```

### Response

```json
{
  "date": "2026-04-29",
  "prep_summary": {
    "todo": 3,
    "doing": 1,
    "done": 2
  },
  "next_tasks": [
    {
      "id": 1,
      "recipe_name": "トマトソース",
      "planned_quantity": "3",
      "planned_unit": "バッチ"
    }
  ],
  "frequent_recipes": [
    {
      "id": 1,
      "name": "トマトソース"
    },
    {
      "id": 2,
      "name": "ドレッシング"
    }
  ],
  "stats": {
    "recipe_count": 24,
    "ingredient_count": 86,
    "prep_task_count": 6
  }
}
```

### MVPでの注意

`期限注意` は将来機能です。

MVPではダミー表示、またはAPIレスポンスには含めず、フロント側で非表示にしてもよいです。

---

# 9. Cost Calculation

原価計算はバックエンドで行う。

## 基本方針

- 原価計算はサーバー側で行う
- フロントは計算結果を表示する
- 材料欄には原価情報を混ぜない
- 原価は `cost_summary` に集約する

## cost_mode: none

原価に含めない。

```text
cost = 0
```

## cost_mode: same_unit

例：

```text
卵 1個 = 30円
使用量 3個
原価 = 90円
```

## cost_mode: conversion

例：

```text
ホールトマト 1缶 = 180円
1缶 = 400g
使用量 200g
原価 = 90円
```

## レシピ全体

```text
material_cost = 材料原価の合計
cost_rate = material_cost / selling_price * 100
gross_profit = selling_price - material_cost
```

販売価格が未設定の場合：

```text
cost_rate = null
gross_profit = null
```

---

# 10. Error Response Format

エラーレスポンスは基本的にDRF標準形式を使う。

### Validation Error

```json
{
  "name": ["この項目は必須です。"],
  "base_yield_quantity": ["0より大きい値を入力してください。"]
}
```

### Not Found

```json
{
  "detail": "見つかりませんでした。"
}
```

### Permission Error

```json
{
  "detail": "この操作を行う権限がありません。"
}
```

### Auth Error

```json
{
  "detail": "ログインが必要です。"
}
```

---

# 11. MVP API一覧

## Auth

```text
POST /api/v1/auth/login/
POST /api/v1/auth/logout/
GET  /api/v1/auth/me/
```

## Shop

```text
GET   /api/v1/shop/me/
PATCH /api/v1/shop/me/
```

## Dashboard

```text
GET /api/v1/dashboard/
```

## Recipes

```text
GET    /api/v1/recipes/
POST   /api/v1/recipes/
GET    /api/v1/recipes/{id}/
PATCH  /api/v1/recipes/{id}/
DELETE /api/v1/recipes/{id}/
```

## Ingredients

```text
GET    /api/v1/ingredients/
POST   /api/v1/ingredients/
GET    /api/v1/ingredients/{id}/
PATCH  /api/v1/ingredients/{id}/
DELETE /api/v1/ingredients/{id}/
```

## PrepTasks

```text
GET    /api/v1/prep-tasks/
POST   /api/v1/prep-tasks/
PATCH  /api/v1/prep-tasks/{id}/
PATCH  /api/v1/prep-tasks/{id}/status/
DELETE /api/v1/prep-tasks/{id}/
```

## Categories

```text
GET    /api/v1/categories/
POST   /api/v1/categories/
PATCH  /api/v1/categories/{id}/
DELETE /api/v1/categories/{id}/
```

## Units

```text
GET    /api/v1/units/
POST   /api/v1/units/
PATCH  /api/v1/units/{id}/
DELETE /api/v1/units/{id}/
```

---

# 12. MVPで後回しにするAPI

以下はMVPでは作らない。

```text
POST /api/v1/checkout/
GET  /api/v1/billing/
POST /api/v1/stripe/webhook/
GET  /api/v1/prep-logs/
POST /api/v1/prep-logs/
GET  /api/v1/devices/
POST /api/v1/devices/
```

Stripe、仕込みログ詳細、店舗端末管理はMVP後に検討する。
