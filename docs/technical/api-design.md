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

## GET /api/v1/auth/csrf/

Django Session AuthでPOST / PATCH / DELETEを行う前に、CSRF cookieを取得する。

### Response

```json
{
  "detail": "CSRF cookie set."
}
```

このAPIは `ensure_csrf_cookie` で `csrftoken` cookieをセットする。frontendはunsafe methodのAPI requestでcookieからCSRF tokenを読み、`X-CSRFToken` headerとして送る。

---

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
    "role": "owner",
    "display_name": "山田 太郎"
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
    "role": "owner",
    "display_name": "山田 太郎"
  }
}
```

未ログインの場合は `401 Unauthorized` を返す。

---

## PATCH /api/v1/auth/me/

現在ログイン中ユーザーの、現在Shopにおける表示名を更新する。owner / staffともに自分の表示名だけ更新できる。

### Request

```json
{
  "display_name": "山田 店長"
}
```

### Response

`GET /api/v1/auth/me/` と同じ形式で、更新後の認証情報を返す。`role`、User、ShopはこのAPIから変更できない。

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

現在Shopの店舗情報を更新する。`Membership.role=owner` のユーザーのみ実行できる。

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

staffが更新しようとした場合は `403 Forbidden` を返す。

```json
{
  "detail": "店舗情報を編集できるのはオーナーのみです。"
}
```

---

# 3. Recipe API

## GET /api/v1/recipes/

レシピ一覧を取得する。

owner / staffとも閲覧できる。

### Query Params

```text
q=トマト
category=1
```

`category` はCategory IDで絞り込みます。

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

`Membership.role=owner` のユーザーのみ実行できる。staffが実行した場合は `403 Forbidden`。

`shop_id` は受け取りません。サーバー側でログイン中ユーザーのMembershipから現在Shopを特定して設定します。

Recipeで指定できるCategoryは現在ShopのCategoryのみです。Unitは標準Unitまたは現在ShopのUnitのみ、RecipeIngredientで指定できるIngredientは現在Shopの `is_active=true` のIngredientのみです。

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
  "name": "トマトソース",
  "category": {
    "id": 1,
    "name": "仕込み"
  },
  "description": "パスタや煮込みに使う基本のトマトソース。",
  "main_image": null,
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
      },
      "sort_order": 1,
      "memo": ""
    }
  ],
  "steps": [
    {
      "id": 1,
      "step_number": 1,
      "instruction": "玉ねぎをみじん切りにする。",
      "image": null,
      "memo": ""
    }
  ],
  "cost_summary": {
    "material_cost": "0",
    "selling_price": null,
    "cost_rate": null,
    "gross_profit": null
  }
}
```

---

## GET /api/v1/recipes/{id}/

レシピ詳細を取得する。

owner / staffとも閲覧できる。

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
  "main_image": null,
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
      },
      "sort_order": 1,
      "memo": ""
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
      },
      "sort_order": 2,
      "memo": ""
    }
  ],
  "steps": [
    {
      "id": 1,
      "step_number": 1,
      "instruction": "玉ねぎをみじん切りにする。",
      "image": null,
      "memo": ""
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

`cost_summary` は、Recipe全体の材料原価を `base_yield_quantity` で割った、出来上がり単位1単位あたりの原価を返します。

- `cost_mode=none`: 原価に含めない
- `cost_mode=same_unit`: `purchase_price / purchase_quantity * quantity`
- `cost_mode=conversion`: `purchase_price * conversion_from_quantity / purchase_quantity / conversion_to_quantity * quantity`
- RecipeIngredientの材料原価を合計した後、`base_yield_quantity` が正の数なら割って1単位あたりの `material_cost` にする
- `selling_price` が未設定の場合、`cost_rate` と `gross_profit` は `null`

MVPでは、原価計算するIngredientのRecipeIngredient単位はIngredientの `usage_unit` と一致させます。一致しない場合は作成・更新時にバリデーションエラーにします。

---

## PATCH /api/v1/recipes/{id}/

レシピを更新する。

`Membership.role=owner` のユーザーのみ実行できる。staffが実行した場合は `403 Forbidden`。

### Request

POSTと同じ構造を基本にする。

MVPでは、`ingredients` または `steps` が送られた場合、既存のRecipeIngredient / RecipeStepを一度削除して送信内容で作り直します。

---

## DELETE /api/v1/recipes/{id}/

レシピを削除する。

`Membership.role=owner` のユーザーのみ実行できる。staffが実行した場合は `403 Forbidden`。

MVPでは `is_active=false` による論理削除です。一覧・詳細・更新・削除は現在Shopの `is_active=true` のRecipeのみ対象です。

### Response

```text
204 No Content
```

---

# 4. Ingredient API

## GET /api/v1/ingredients/

材料一覧を取得する。

owner / staffとも閲覧できる。

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

`Membership.role=owner` のユーザーのみ実行できる。staffが実行した場合は `403 Forbidden`。

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

owner / staffとも閲覧できる。

現在ShopのIngredientのみ取得できる。他ShopのIngredientは `404 Not Found`。

---

## PATCH /api/v1/ingredients/{id}/

材料を更新する。

`Membership.role=owner` のユーザーのみ実行できる。staffが実行した場合は `403 Forbidden`。

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

`Membership.role=owner` のユーザーのみ実行できる。staffが実行した場合は `403 Forbidden`。

MVPでは `is_active=false` による論理削除とする。

現在ShopのIngredientのみ削除できる。他ShopのIngredientは `404 Not Found`。

---

# 5. PrepTask API

## GET /api/v1/prep-tasks/

現在取り組む仕込みタスク一覧を取得する。

ログイン必須。現在ShopのPrepTaskのみ返す。

### Query Params

```text
date=2026-05-05
```

`date` 未指定時はサーバー側のtodayを使う。`date` は完了タスクの完了日判定に使用する。

表示対象は次の通り。

- `status=todo` または `status=doing`：予定日に関係なく返す
- `status=done`：`completed_at` のローカル日付が指定日と一致する場合だけ返す

指定日より前に完了したタスクは返さない。querysetは常に現在Shopへスコープする。

### Response

```json
{
  "date": "2026-05-05",
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
      "memo": "",
      "sort_order": 1,
      "completed_at": null
    }
  ]
}
```

`summary` は上記表示対象の `todo` / `doing` / `done` 件数。MVPでは `tasks` を `sort_order, id` 順に返す。`carried_over` は返さない。

---

## POST /api/v1/prep-tasks/

仕込みタスクを作成する。

owner / staffとも実行できる。

`shop_id` は受け取らない。サーバー側でログイン中ユーザーのMembershipから現在Shopを特定して設定する。

指定できるRecipeは現在Shopの `is_active=true` のRecipeのみ。指定できるUnitは標準Unitまたは現在ShopのUnitのみ。

### Request

```json
{
  "date": "2026-05-05",
  "recipe_id": 1,
  "planned_quantity": "3",
  "planned_unit_id": 10,
  "memo": "",
  "sort_order": 1
}
```

### Response

```json
{
  "id": 1,
  "date": "2026-05-05",
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
  "memo": "",
  "sort_order": 1,
  "completed_at": null
}
```

---

## PATCH /api/v1/prep-tasks/{id}/

仕込みタスクを更新する。

### Request

```json
{
  "date": "2026-05-05",
  "recipe_id": 1,
  "planned_quantity": "4",
  "planned_unit_id": 10,
  "memo": "",
  "sort_order": 2
}
```

通常PATCHでも `status` 更新は可能。`status=done` では `completed_at` を設定し、`done` 以外へ戻した場合は `completed_at=null` にする。

---

## PATCH /api/v1/prep-tasks/{id}/status/

仕込みタスクのステータスを更新する。

owner / staffとも実行できる。

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

Statusは以下のみ有効。

```text
todo
doing
done
```

`done` にした場合は `completed_at=now`。`done` 以外に戻した場合は `completed_at=null`。

---

## DELETE /api/v1/prep-tasks/{id}/

仕込みタスクを削除する。

MVPでは物理削除。他ShopのPrepTaskは `404 Not Found`。

---

# 6. BoardMemo API

Prep Today下部のホワイトボード的な軽量メモを扱う。

カテゴリ、期限、担当者、優先度はMVPでは扱わない。

## GET /api/v1/board-memos/

Prep Todayで表示するメモ一覧を取得する。

ログイン必須。現在ShopのBoardMemoのみ返す。

### Query Params

```text
include_archived=1
```

`include_archived=1` を指定した場合は、履歴候補用にアーカイブ済みも含めて返す。未指定時は次のメモを返す。

- `archived_at=null` の未チェックメモ全件
- `archived_at` のローカル日付が今日のチェック済みメモ

昨日以前にチェック済みのメモは、通常一覧では返さない。

未チェックメモは `created_at` 昇順、今日チェック済みメモは `archived_at` 降順で返す。

### Response

```json
[
  {
    "id": 1,
    "text": "玉ねぎ",
    "is_archived": false,
    "archived_at": null,
    "created_at": "2026-05-05T10:00:00+09:00",
    "updated_at": "2026-05-05T10:00:00+09:00"
  }
]
```

## POST /api/v1/board-memos/

メモを追加する。

owner / staffとも実行できる。

`shop_id` は受け取らない。サーバー側でログイン中ユーザーのMembershipから現在Shopを特定して設定する。

### Request

```json
{
  "text": "ラップ"
}
```

## PATCH /api/v1/board-memos/{id}/archive/

メモをアーカイブする。

owner / staffとも実行できる。

Prep Todayでは未チェックメモのチェック操作でこのAPIを呼ぶ。アーカイブ後もチェックした当日中は、同じメモカード内の「チェック済み」エリアに薄く表示する。

## PATCH /api/v1/board-memos/{id}/unarchive/

メモのアーカイブを取り消す。

owner / staffとも実行できる。

Prep Todayではチェック済みメモを再度クリックした場合にこのAPIを呼び、未チェックエリアへ戻す。

---

# 7. Category API

## GET /api/v1/categories/

レシピカテゴリ一覧を取得する。

owner / staffとも参照できる。Recipe作成・編集フォームの選択肢としても利用する。

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

`Membership.role=owner` のユーザーのみ実行できる。staffが実行した場合は `403 Forbidden`。

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

`Membership.role=owner` のユーザーのみ実行できる。staffが実行した場合は `403 Forbidden`。

ログイン中ユーザーの現在Shopに紐づくカテゴリのみ更新できる。

---

## DELETE /api/v1/categories/{id}/

カテゴリを削除する。

`Membership.role=owner` のユーザーのみ実行できる。staffが実行した場合は `403 Forbidden`。

MVPでは `is_active=false` による論理削除とする。

ログイン中ユーザーの現在Shopに紐づくカテゴリのみ削除できる。

---

# 8. Unit API

## GET /api/v1/units/

単位一覧を取得する。

owner / staffとも参照できる。Recipe / Ingredient / PrepTaskの入力選択肢としても利用する。

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

`Membership.role=owner` のユーザーのみ実行できる。staffが実行した場合は `403 Forbidden`。

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

`Membership.role=owner` のユーザーのみ実行できる。staffが実行した場合は `403 Forbidden`。

標準単位（`shop = null`）は更新できない。店舗独自単位のみ更新できる。

---

## DELETE /api/v1/units/{id}/

単位を削除する。

`Membership.role=owner` のユーザーのみ実行できる。staffが実行した場合は `403 Forbidden`。

標準単位（`shop = null`）は削除できない。店舗独自単位のみ `is_active=false` による論理削除とする。

---

# 9. Dashboard API

## GET /api/v1/dashboard/

Dashboard表示に必要な情報を取得する。

ログイン必須。Dashboardに含めるRecipe / Ingredient / PrepTaskはすべて現在Shopにスコープする。

### Query Params

```text
date=2026-05-05
```

`date` 未指定時はサーバー側のtodayを使う。`date` は完了済みタスクを当日分として扱う基準日で、未完了タスクは予定日に関係なく含める。

### Response

```json
{
  "date": "2026-05-05",
  "prep_summary": {
    "todo": 3,
    "doing": 1,
    "done": 2
  },
  "next_tasks": [
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
      "memo": "",
      "sort_order": 1
    }
  ],
  "frequent_recipes": [
    {
      "id": 1,
      "name": "トマトソース",
      "category": {
        "id": 1,
        "name": "仕込み"
      }
    }
  ],
  "stats": {
    "recipe_count": 24,
    "ingredient_count": 86,
    "prep_task_count": 6
  },
  "alerts": []
}
```

### MVPでの注意

- `prep_summary`: Prep Todayと同じ表示対象（未完了の `todo` / `doing` 全件 + `completed_at` が対象日の `done`）を status別に集計する。
- `next_tasks`: Prep Todayと同じ表示対象のうち `status != done` のPrepTaskを、作業中（`doing`）→ 未着手（`todo`）の順に並べ、同じstatus内は `sort_order, id` 順で最大5件返す。
- `frequent_recipes`: 現在ShopのPrepTask利用回数が多いRecipeを最大5件返す。
- `stats.recipe_count`: 現在Shopの `is_active=true` のRecipe数。
- `stats.ingredient_count`: 現在Shopの `is_active=true` のIngredient数。
- `stats.prep_task_count`: Prep Todayと同じ表示対象のPrepTask数。
- `alerts`: MVPでは期限注意・残量注意を未実装のため空配列を返す。

`期限注意` は将来機能です。

---

# 10. Cost Calculation

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
total_material_cost = 材料原価の合計
material_cost = total_material_cost / base_yield_quantity
cost_rate = material_cost / selling_price * 100
gross_profit = selling_price - material_cost
```

販売価格が未設定の場合：

```text
cost_rate = null
gross_profit = null
```

---

# 11. Error Response Format

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

# 12. MVP API一覧

## Auth

```text
GET  /api/v1/auth/csrf/
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

# 13. MVPで後回しにするAPI

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
