# Ricetta MVP Roadmap

## 目的

Ricetta MVP の実装順を整理する。

Ricetta は「小さな飲食店のための、レシピ台帳。」をコンセプトにした、小規模飲食店向けレシピ管理SaaSです。

MVPでは、まず以下の体験を成立させる。

```text
レシピを登録する
↓
今日の仕込みに入れる
↓
必要量に応じた材料量を見る
↓
作業が終わったら完了にする
```

このロードマップでは、個人開発で進めやすいように、実装を小さなPhaseに分ける。

---

## 全体方針

MVPでは、機能を広げすぎない。

優先すること：

- レシピ台帳として使える
- 材料と分量を登録できる
- 原価計算の土台がある
- 今日の仕込みが見える
- スマホ・タブレットで見やすい
- 店舗ごとにデータが分離される

後回しにすること：

- Stripe決済
- 複数店舗管理
- POS連携
- 在庫自動減算
- 高度な発注管理
- AI自動分類
- 本格的な仕込みログ
- 期限・残量アラート

---

# Phase 0: Project Scaffold

## 目的

開発の土台を作る。

## やること

- GitHub repository 作成
- README.md 配置
- AGENTS.md 配置
- docs/ 配置
- Docker Compose 初期構成
- backend/ 作成
- frontend/ 作成
- .env.example 作成
- GitHub Actions 最小CIの検討

## 成果物

```text
README.md
AGENTS.md
docker-compose.yml
.env.example
backend/
frontend/
docs/
```

## 完了条件

- ローカルでDocker Composeが起動できる
- backend / frontend の開発開始ができる
- CodexがAGENTS.mdを参照して作業できる

---

# Phase 1: Backend Foundation

## 目的

MVPの中心となるデータモデルとAPI土台を作る。

## やること

- Django project 作成
- DRF 導入
- PostgreSQL 接続
- settings 分割または環境変数対応
- `/api/v1/` prefix 設定
- User / Shop / Membership / Category / Unit モデル
- Membershipから現在のShopを特定する
- API queryをshop_idで絞る
- フロントから渡されたshop_idを信用しない

## 完了条件

- Djangoが起動する
- DB migration が通る
- 初期カテゴリ・単位を登録できる
- ログインユーザーのShopを取得する設計がある

---

# Phase 2: Auth / Shop Scope

## 目的

ログインと店舗スコープの基本を成立させる。

## やること

### Auth API

- `POST /api/v1/auth/login/`
- `POST /api/v1/auth/logout/`
- `GET /api/v1/auth/me/`

### Shop API

- `GET /api/v1/shop/me/`
- `PATCH /api/v1/shop/me/`

## MVP方針

MVPではOwner中心で実装する。

Staffの細かい権限制御は後回しでもよいが、Membershipにはroleを持たせる。

## 完了条件

- Ownerでログインできる
- ログイン中ユーザーのShopを取得できる
- 他Shopのデータにアクセスできない設計になっている

---

# Phase 3: Ingredients

## 目的

原価計算の土台となる材料管理を実装する。

## やること

### Ingredient API

- `GET /api/v1/ingredients/`
- `POST /api/v1/ingredients/`
- `GET /api/v1/ingredients/{id}/`
- `PATCH /api/v1/ingredients/{id}/`
- `DELETE /api/v1/ingredients/{id}/`

### Ingredient Model

材料に以下を持たせる。

- name
- supplier
- memo
- cost_mode
- purchase_quantity
- purchase_unit
- purchase_price
- usage_unit
- conversion_from_quantity
- conversion_from_unit
- conversion_to_quantity
- conversion_to_unit

### 原価計算モード

```text
none
same_unit
conversion
```

## UI

- Ingredient List
- Ingredient Form

## 完了条件

- 材料を登録できる
- 原価計算しない材料を作れる
- 仕入単位のまま計算する材料を作れる
- 換算して計算する材料を作れる
- 材料一覧で原価計算モードが分かる

---

# Phase 4: Recipes

## 目的

Ricettaの中心であるレシピ台帳を実装する。

## やること

### Recipe API

- `GET /api/v1/recipes/`
- `POST /api/v1/recipes/`
- `GET /api/v1/recipes/{id}/`
- `PATCH /api/v1/recipes/{id}/`
- `DELETE /api/v1/recipes/{id}/`

### Recipe Model

- name
- category
- description
- main_image
- base_yield_quantity
- base_yield_unit
- selling_price
- notes
- allergen_notes

### RecipeIngredient

- recipe
- ingredient
- quantity
- unit
- sort_order
- memo

### RecipeStep

- recipe
- step_number
- instruction
- image
- memo

## UI

- Recipe List
- Recipe Detail
- Recipe Edit

## 完了条件

- レシピを作成できる
- レシピに材料を追加できる
- レシピに作り方を追加できる
- レシピ一覧から詳細へ遷移できる
- レシピ詳細で材料と作り方が見やすい
- 材料欄に原価情報が混ざっていない

---

# Phase 5: Cost Calculation

## 目的

レシピの材料原価を計算できるようにする。

## 方針

原価計算はバックエンドで行う。

フロントでは計算結果を表示する。

## やること

- `cost_mode=none` の材料を原価から除外する
- `cost_mode=same_unit` の材料原価を計算する
- `cost_mode=conversion` の材料原価を計算する
- レシピ全体の材料原価を合計する
- 販売価格がある場合、原価率と粗利を計算する

## 表示方針

Recipe Detailでは、原価は「原価情報」カードに集約する。

材料欄には原価を表示しない。

## 完了条件

- 材料原価合計が表示される
- 販売価格がある場合、原価率が表示される
- 販売価格がない場合、原価率は `-` または `null`
- 計算モードごとのテストがある

---

# Phase 6: Today's Prep

## 目的

ホワイトボード代替となる「今日の仕込み」を実装する。

## やること

### PrepTask API

- `GET /api/v1/prep-tasks/?date=YYYY-MM-DD`
- `POST /api/v1/prep-tasks/`
- `PATCH /api/v1/prep-tasks/{id}/`
- `PATCH /api/v1/prep-tasks/{id}/status/`
- `DELETE /api/v1/prep-tasks/{id}/`

### PrepTask Model

- shop
- date
- recipe
- planned_quantity
- planned_unit
- status
- memo
- sort_order
- completed_at

### Status

```text
todo
doing
done
```

表示：

```text
未着手
作業中
完了
```

## UI

- Prep Today
- Prep Action Modal

## 操作方針

ドラッグ&ドロップは使わない。

タップで操作する。

## 完了条件

- 今日の仕込みが表示される
- 仕込みタスクを追加できる
- 未着手 / 作業中 / 完了で表示できる
- タップでステータス変更できる
- 仕込みカードからレシピ詳細へ遷移できる
- 予定数量に応じてレシピ詳細の仕込み量が反映される

---

# Phase 7: Dashboard

## 目的

ログイン後の「今日の現場」を実装する。

## やること

### Dashboard API

- `GET /api/v1/dashboard/?date=YYYY-MM-DD`

### 表示項目

- 今日の仕込みサマリー
- 次にやること
- よく使うレシピ
- ミニサマリー
- 期限注意

## MVP方針

期限注意は将来機能。

MVPではダミー表示、または非表示でもよい。

## 完了条件

- 今日の仕込み件数が表示される
- 次にやることが表示される
- 仕込み画面へ遷移できる
- レシピ一覧へ遷移できる
- タブレット横で見やすい

---

# Phase 8: Frontend Layout

## 目的

Ricettaの主要画面レイアウトを作る。

## やること

### 共通レイアウト

スマホ：

- 下部ナビ

タブレット横 / PC：

- 120px固定サイドバー
- テキストのみ
- カード型
- 常時表示

### 画面

- Login
- Dashboard
- Prep Today
- Prep Action Modal
- Recipe List
- Recipe Detail
- Recipe Edit
- Ingredient List
- Ingredient Form
- Settings

## 完了条件

- スマホ幅で主要画面が崩れない
- タブレット横でサイドバーが表示される
- Recipe Detailで材料と作り方が見やすい
- 戻るボタンが機能する

---

# Phase 9: Forms / Validation

## 目的

入力フォームとバリデーションを整える。

## やること

- React Hook Form
- Zod
- APIエラー表示
- 保存成功トースト
- 入力保持
- 必須項目チェック
- 数値チェック

## 対象フォーム

- Recipe Edit
- Ingredient Form
- PrepTask Form
- Settings

## 完了条件

- 必須項目のエラーが出る
- 数値項目で不正値を入力できない
- 保存失敗時に入力内容が消えない
- APIエラーがユーザー向けに表示される

---

# Phase 10: MVP Polish

## 目的

MVPとして試験導入できる状態に整える。

## やること

- UI微調整
- 空状態
- ローディング表示
- エラー表示
- レスポンシブ確認
- テストデータ作成
- README更新
- handoff更新

## 確認項目

- レシピが登録できる
- 材料が登録できる
- 原価計算が動く
- 今日の仕込みが使える
- スマホで見やすい
- タブレット横で見やすい
- 他Shopのデータにアクセスできない
- MVP対象外の機能が混ざっていない

---

# MVP後に検討するPhase

## Phase 11: Prep Logs

仕込み完了後の記録。

- PrepLog
- made_at
- made_by
- quantity
- unit
- memo

## Phase 12: Expiry / Remaining Quantity

使用期限・残量管理。

- expires_at
- remaining_quantity
- discarded
- used_up

## Phase 13: Stripe Billing

SaaS課金。

- Pricing
- Checkout
- Billing
- Stripe Webhook

## Phase 14: Staff / Device Mode

スタッフ権限・店舗端末。

- Staff閲覧権限
- 原価非表示
- 店舗タブレット用モード

---

# 実装時の注意

## 迷ったら小さくする

MVPでは、便利そうな機能を入れすぎない。

判断基準：

```text
レシピ台帳と今日の仕込みボードを成立させるために必要か？
```

必要でなければ後回しにする。

## ドキュメント更新

実装で仕様を変えた場合は、関連ドキュメントを更新する。

対象：

- README.md
- AGENTS.md
- docs/planning/mvp-requirements.md
- docs/product/screens.md
- docs/data/data-model.md
- docs/api/api-design.md
- docs/handoff/latest.md

## 初回MVPのゴール

初回MVPのゴールは、以下を試せる状態にすること。

```text
小さな飲食店が、
レシピ台帳と今日の仕込みボードを、
ひとつのアプリで使えるか。
```
