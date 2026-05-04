# Ricetta Data Model

## データ設計の基本方針

Ricetta は、将来的なSaaS化を前提に、店舗ごとのデータ分離を最初から考慮します。

基本方針：

- 主要データはすべて `shop_id` を持つ
- APIではログインユーザーの所属店舗で必ず絞り込む
- フロントから送られた `shop_id` を信用しない
- MVPでは1ユーザー1店舗を基本にする
- 将来的に複数店舗・複数ユーザーへ拡張できるようにする

## 店舗ごとのデータ分離方針

Ricettaでは、Shopをデータ分離の基本単位にします。

以下のデータはShopに紐づきます。

- Recipe
- Ingredient
- PrepTask
- PrepLog
- Category
- Unit
- Subscription

サーバー側では、常にログインユーザーのMembershipからShopを特定します。

例：

```text
request.user
→ Membership
→ shop
→ shop_idでデータを絞り込み
```

## 主要エンティティ

MVPおよび将来拡張で扱う主要エンティティは以下です。

- Shop
- User
- Membership
- Recipe
- RecipeIngredient
- Ingredient
- PrepTask
- PrepLog
- Subscription

## Shop

店舗を表します。

### 主なフィールド

| フィールド | 型 | 説明 |
|---|---|---|
| id | UUID / BigAutoField | 店舗ID |
| name | string | 店舗名 |
| business_type | string | 業態 |
| memo | text | メモ |
| created_at | datetime | 作成日時 |
| updated_at | datetime | 更新日時 |

### 将来拡張

| フィールド | 説明 |
|---|---|
| plan | 現在のプラン |
| trial_ends_at | トライアル終了日 |
| subscription_status | 契約状態 |
| stripe_customer_id | Stripe顧客ID |

## User

ログインユーザーを表します。

MVPでは Django標準User を利用します。

メールログインは `username=email` として扱います。`email` も同じ値を保存し、APIレスポンスでは `email` をユーザー識別子として返します。

認証方式は Django Session Auth + DRF Basic Auth で開始します。JWTは必要になってから検討します。

### 主なフィールド

| フィールド | 型 | 説明 |
|---|---|---|
| id | UUID / BigAutoField | ユーザーID |
| email | string | メールアドレス |
| name | string | 表示名 |
| password | string | パスワードハッシュ |
| is_active | boolean | 有効状態 |
| created_at | datetime | 作成日時 |
| updated_at | datetime | 更新日時 |

## Membership

ユーザーと店舗の所属関係を表します。

MVPでは1ユーザー1店舗で運用してもよいですが、将来拡張のためにMembershipを分けます。

### 主なフィールド

| フィールド | 型 | 説明 |
|---|---|---|
| id | UUID / BigAutoField | 所属ID |
| user_id | FK | User |
| shop_id | FK | Shop |
| role | string | owner / staff |
| display_name | string | 店舗内表示名 |
| is_active | boolean | 有効状態 |
| created_at | datetime | 作成日時 |
| updated_at | datetime | 更新日時 |

### role

MVPでは以下の2種類です。

| role | 説明 |
|---|---|
| owner | 店舗管理者 |
| staff | スタッフ |

将来：

- editor
- viewer
- device

などに拡張可能です。

## Recipe

レシピを表します。

### 主なフィールド

| フィールド | 型 | 説明 |
|---|---|---|
| id | UUID / BigAutoField | レシピID |
| shop_id | FK | 店舗 |
| name | string | レシピ名 |
| category_id | FK / nullable | カテゴリ |
| description | text | 説明 |
| main_image | image / string | 完成写真 |
| base_yield_quantity | decimal | 基準量 |
| base_yield_unit_id | FK | 基準単位 |
| selling_price | decimal / nullable | 販売価格 |
| notes | text | 注意点・メモ |
| allergen_notes | text | アレルゲンメモ |
| is_active | boolean | 有効状態 |
| created_by_id | FK | 作成者 |
| updated_by_id | FK | 更新者 |
| created_at | datetime | 作成日時 |
| updated_at | datetime | 更新日時 |

### 例

トマトソース：

- name: トマトソース
- category: 仕込み
- base_yield_quantity: 1
- base_yield_unit: バッチ
- selling_price: null

## RecipeIngredient

レシピに紐づく材料と使用量を表します。

### 主なフィールド

| フィールド | 型 | 説明 |
|---|---|---|
| id | UUID / BigAutoField | ID |
| recipe_id | FK | Recipe |
| ingredient_id | FK | Ingredient |
| quantity | decimal | 使用量 |
| unit_id | FK | 使用単位 |
| sort_order | integer | 表示順 |
| memo | text | メモ |
| created_at | datetime | 作成日時 |
| updated_at | datetime | 更新日時 |

### 例

トマトソース：

- ホールトマト 2缶
- 玉ねぎ 300g
- にんにく 10g
- オリーブオイル 60ml
- 塩 12g

## Ingredient

材料マスターを表します。

### 主なフィールド

| フィールド | 型 | 説明 |
|---|---|---|
| id | UUID / BigAutoField | 材料ID |
| shop_id | FK | 店舗 |
| name | string | 材料名 |
| supplier | string / nullable | 仕入先 |
| memo | text | メモ |
| cost_mode | string | none / same_unit / conversion |
| purchase_quantity | decimal / nullable | 仕入数量 |
| purchase_unit_id | FK / nullable | 仕入単位 |
| purchase_price | decimal / nullable | 仕入価格 |
| usage_unit_id | FK / nullable | レシピで使う単位 |
| conversion_from_quantity | decimal / nullable | 換算元数量 |
| conversion_from_unit_id | FK / nullable | 換算元単位 |
| conversion_to_quantity | decimal / nullable | 換算先数量 |
| conversion_to_unit_id | FK / nullable | 換算先単位 |
| is_active | boolean | 有効状態 |
| created_at | datetime | 作成日時 |
| updated_at | datetime | 更新日時 |

### cost_mode

| 値 | 説明 |
|---|---|
| none | 原価計算しない |
| same_unit | 仕入単位のまま計算 |
| conversion | 使用単位に換算して計算 |

### 例：原価計算しない

塩少々：

- cost_mode: none

### 例：仕入単位のまま計算

卵：

- purchase_quantity: 1
- purchase_unit: 個
- purchase_price: 30
- usage_unit: 個
- cost_mode: same_unit

### 例：換算して計算

ホールトマト：

- purchase_quantity: 1
- purchase_unit: 缶
- purchase_price: 180
- conversion_from_quantity: 1
- conversion_from_unit: 缶
- conversion_to_quantity: 400
- conversion_to_unit: g
- usage_unit: g
- cost_mode: conversion

## PrepTask

今日の仕込みタスクを表します。

### 主なフィールド

| フィールド | 型 | 説明 |
|---|---|---|
| id | UUID / BigAutoField | タスクID |
| shop_id | FK | 店舗 |
| date | date | 仕込み日 |
| recipe_id | FK | Recipe |
| planned_quantity | decimal | 予定数量 |
| planned_unit_id | FK | 単位 |
| status | string | todo / doing / done |
| assigned_to_id | FK / nullable | 担当者 |
| memo | text | メモ |
| sort_order | integer | 並び順 |
| completed_at | datetime / nullable | 完了日時 |
| created_at | datetime | 作成日時 |
| updated_at | datetime | 更新日時 |

### status

| 値 | 説明 |
|---|---|
| todo | 未着手 |
| doing | 作業中 |
| done | 完了 |

### 例

- date: 2026-04-29
- recipe: トマトソース
- planned_quantity: 3
- planned_unit: バッチ
- status: todo

## PrepLog

仕込み完了後の記録を表します。

MVPでは簡略化し、将来拡張用として設計します。

### 主なフィールド

| フィールド | 型 | 説明 |
|---|---|---|
| id | UUID / BigAutoField | ログID |
| shop_id | FK | 店舗 |
| recipe_id | FK | Recipe |
| source_task_id | FK / nullable | 元のPrepTask |
| made_at | datetime | 仕込み日時 |
| made_by_id | FK / nullable | 担当者 |
| quantity | decimal | 仕込み量 |
| unit_id | FK | 単位 |
| memo | text | メモ |
| created_at | datetime | 作成日時 |
| updated_at | datetime | 更新日時 |

### MVPでの扱い

MVPでは、PrepTaskの完了だけで十分です。  
PrepLogは後から追加してもよいです。

ただし、将来以下を扱うために設計候補として残します。

- 使用期限
- 残量
- 廃棄
- 使い切り
- 期限注意

## Subscription

SaaS契約情報を表します。

MVPでは決済機能を実装しませんが、将来Stripe連携できるよう設計だけ残します。

### 主なフィールド

| フィールド | 型 | 説明 |
|---|---|---|
| id | UUID / BigAutoField | 契約ID |
| shop_id | FK | 店舗 |
| plan | string | free / starter / shop / pro |
| status | string | trialing / active / past_due / canceled |
| trial_ends_at | datetime / nullable | トライアル終了日時 |
| current_period_end | datetime / nullable | 現在期間終了日 |
| stripe_customer_id | string / nullable | Stripe顧客ID |
| stripe_subscription_id | string / nullable | StripeサブスクID |
| created_at | datetime | 作成日時 |
| updated_at | datetime | 更新日時 |

### MVPでの扱い

MVPでは、以下のどちらかで簡略化します。

1. Subscriptionモデルを作らず、Shopに簡易フィールドだけ持つ
2. Subscriptionモデルだけ作り、Stripe連携はしない

おすすめは、初期MVPではShopに簡易フィールドを持たせ、SaaS化時にSubscriptionモデルへ分離することです。

## 補助エンティティ

### Category

レシピカテゴリを表します。

| フィールド | 説明 |
|---|---|
| id | ID |
| shop_id | 店舗 |
| name | カテゴリ名 |
| sort_order | 並び順 |
| is_active | 有効状態 |

初期カテゴリ：

- 仕込み
- メイン
- デザート
- ドリンク
- ソース
- 副菜
- その他

作成時は、フロントから `shop_id` を受け取らず、サーバー側で現在ログイン中ユーザーのShopを設定します。

削除はMVPでは `is_active=false` の論理削除とします。

### Unit

単位を表します。

| フィールド | 説明 |
|---|---|
| id | ID |
| shop_id | 店舗。標準単位はnullでも可 |
| name | 単位名 |
| unit_type | weight / volume / count / custom |
| is_default | 標準単位か |
| sort_order | 並び順 |
| is_active | 有効状態 |

初期単位：

- g
- kg
- ml
- L
- 個
- 本
- 枚
- 缶
- 袋
- 束
- バッチ
- 人前
- 食
- 台
- 杯
- 小さじ
- 大さじ
- 適量

標準単位は `shop = null`、店舗独自単位は `shop = Shop` として扱います。

Unit APIでは標準単位と現在Shopの店舗独自単位だけを返します。標準単位は編集・削除できません。

## 主なリレーション

```text
Shop 1 - N Membership
User 1 - N Membership

Shop 1 - N Recipe
Shop 1 - N Ingredient
Shop 1 - N PrepTask
Shop 1 - N Category
Shop 1 - N Unit

Recipe 1 - N RecipeIngredient
Ingredient 1 - N RecipeIngredient

Recipe 1 - N PrepTask

PrepTask 1 - 0..1 PrepLog
Recipe 1 - N PrepLog

Shop 1 - 0..1 Subscription
```

## MVPでは使うが簡略化する項目

### 権限

MVPではOwner中心で実装します。

Membershipは作っておきますが、細かなStaff制御は後回しにします。

### Subscription

MVPでは決済はしません。

ただし、ShopまたはSubscriptionに以下の情報を持てる設計にします。

- plan
- subscription_status
- trial_ends_at

### PrepLog

MVPでは、仕込み完了はPrepTaskのstatusで管理します。

PrepLogは将来拡張です。

### 画像

MVPでは、画像アップロードは簡易実装でも可とします。

将来は以下を検討します。

- S3互換ストレージ
- 画像圧縮
- 複数画像
- 工程写真

## 将来拡張のために残しておく項目

### 複数店舗管理

将来的には、1ユーザーが複数Shopに所属できるようにします。

Membershipを分けることで対応可能です。

### Staff権限

将来的には以下を追加します。

- owner
- editor
- viewer
- device

### 店舗端末

将来的にShopDeviceを追加します。

想定フィールド：

- shop_id
- name
- role
- device_token_hash
- is_active
- last_seen_at

### 仕込み在庫

PrepLogを拡張して、以下を扱います。

- initial_quantity
- remaining_quantity
- expires_at
- status
- discarded_at

### 原価計算拡張

将来的に対応する可能性があります。

- 歩留まり
- 廃棄率
- 加熱後重量
- 複数換算
- 仕入価格履歴

### Stripe連携

将来的にSubscriptionをStripeと連携します。

- stripe_customer_id
- stripe_subscription_id
- current_period_end
- webhook event
