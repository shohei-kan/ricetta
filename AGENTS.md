# AGENTS.md

## Project

Ricetta（リチェッタ）

小さな飲食店のための、レシピ台帳。

Ricetta is a SaaS-style web application for small restaurants, cafes, bars, delis, bakeries, and other small food businesses. It helps shops manage recipes, ingredients, food cost, and daily prep tasks that are often scattered across paper, Excel, whiteboards, and verbal instructions.

## Product Concept

Ricetta focuses on:

- Recipe records
- Ingredient and quantity management
- Basic food cost calculation
- Today's prep board
- Smartphone / tablet / PC-friendly access

The MVP should stay small and practical.

The core user experience is:

```text
レシピを登録する
↓
今日の仕込みに入れる
↓
必要量に応じた材料量を見る
↓
作業が終わったら完了にする
```

## Tech Stack

Frontend:

- React
- Vite
- TypeScript
- Tailwind CSS
- shadcn/ui
- TanStack Query
- React Hook Form
- Zod

Backend:

- Django
- Django REST Framework
- PostgreSQL

Development:

- Docker Compose
- GitHub
- GitHub Actions

API prefix:

```text
/api/v1/
```

Payments:

- Stripe Checkout / Billing is planned for the future.
- Stripe is not part of the initial MVP.

## Directory Policy

Expected structure:

```text
frontend/
backend/
docs/
  api/
  planning/
  product/
  data/
  handoff/
    latest.md
    archive/
  decisions/
README.md
AGENTS.md
docker-compose.yml
.env.example
```

## MVP Scope

### In Scope

The MVP should include:

- Login / logout
- Shop account scope
- Recipe list
- Recipe detail
- Recipe create / edit
- Ingredient create / edit
- Ingredient cost mode
- Basic food cost calculation
- Today's prep list
- Prep task status update
- Smartphone layout
- Tablet landscape layout

### Out of Scope

Do not implement these in the MVP:

- Stripe payment
- Checkout
- Billing portal
- POS integration
- Multi-shop management
- Automatic inventory deduction
- Advanced ordering
- AI auto-classification
- Nutrition calculation
- HACCP reports
- Advanced role management
- Shop device mode
- Full prep inventory / expiry alerts

Leave room for future expansion, but do not build these yet.

## Important Product Decisions

### 1. Shop Scope

Ricetta is designed as a future SaaS.

All main data should be scoped by `shop_id`.

Important:

- Do not trust `shop_id` sent from the frontend.
- The backend must determine the shop from the logged-in user and Membership.
- Querysets must always be filtered by the current user's shop.

Main shop-scoped data:

- Recipe
- Ingredient
- PrepTask
- Category
- Unit
- PrepLog, future
- Subscription, future

### 2. Navigation

Smartphone:

- Use bottom navigation.

Tablet landscape / PC:

- Use a fixed left sidebar.
- Sidebar width should be about 120px.
- Sidebar should always be visible.
- Sidebar items should be text-only cards.

Sidebar items:

```text
ホーム
仕込み
レシピ
材料
設定
```

### 3. Back Button

Detail and edit screens should include a back button.

Examples:

```text
Recipe List → Recipe Detail → 戻る → Recipe List
Prep Today → Recipe Detail → 戻る → Prep Today
Recipe Detail → Recipe Edit → 戻る → Recipe Detail
```

Use the back button to preserve user context.  
Use sidebar navigation for larger screen changes.

### 4. Recipe Detail Priority

Recipe detail is a working screen for the kitchen.

Prioritize:

1. Recipe name
2. Prep quantity
3. Ingredients
4. Steps
5. Notes
6. Cost summary

Do not overload the ingredient list.

### 5. Ingredient and Cost Separation

Materials are work information.  
Cost is management information.

Do not show cost details inside the ingredient list on the recipe detail screen.

Ingredient section should show only:

- Ingredient name
- Quantity
- Unit

Cost information should be grouped in a separate `原価情報` card.

### 6. Ingredient Cost Mode

Ingredients should support three cost calculation modes:

```text
none
same_unit
conversion
```

Meanings:

- `none`: Do not include in cost calculation.
- `same_unit`: Calculate using purchase unit directly.
- `conversion`: Convert purchase unit to usage unit.

Examples:

```text
none:
水、塩少々、飾り

same_unit:
卵 1個 = 30円
3個使用 → 90円

conversion:
ホールトマト 1缶 = 180円
1缶 = 400g
200g使用 → 90円
```

MVP supports:

- Cost on / off
- Same-unit calculation
- One-step conversion
- kg ⇔ g
- L ⇔ ml
- Custom conversion such as 缶 → g, 袋 → g, 本 → ml

MVP does not support:

- Yield loss
- Waste rate
- Cooked weight
- Multi-step conversion
- Inventory integration

### 7. Today's Prep

Today's prep replaces a kitchen whiteboard.

Prep statuses:

```text
todo
doing
done
```

Japanese display:

```text
未着手
作業中
完了
```

Interactions should be tap-based.  
Do not use drag-and-drop for MVP.

Prep cards should show:

- Recipe name
- Planned quantity
- Unit

Example:

```text
トマトソース
3バッチ
```

## UI Principles

Ricetta should feel like:

```text
Notionより現場向け
Excelより見やすい
紙より探しやすい
ホワイトボードより残る
大手業務システムより軽い
```

UI tone:

- Clean
- Soft
- Practical
- Easy to read in a kitchen
- Large enough for tablet use
- Avoid over-designed interactions
- Avoid unnecessary icons if text is clearer

Use Japanese labels for user-facing UI.

## Documentation Rules

Keep documentation current when implementation changes.

Important docs:

```text
docs/planning/concept.md
docs/planning/mvp-requirements.md
docs/product/screens.md
docs/data/data-model.md
docs/api/api-design.md
docs/handoff/latest.md
docs/decisions/
```

### README.md

README is for humans.

It should include:

- Project overview
- Setup instructions
- Development commands
- Environment variables
- Basic architecture
- Links to important docs

### AGENTS.md

AGENTS.md is for Codex / AI agents.

It should include:

- Project rules
- Technical assumptions
- Product decisions
- MVP boundaries
- Documentation update rules

### Handoff

Use:

```text
docs/handoff/latest.md
```

for the latest working context.

Move older handoffs into:

```text
docs/handoff/archive/
```

when needed.

A handoff should include:

- Date
- Project
- Current status
- What was done
- Key files
- Current decisions
- Next recommended tasks
- Notes / caveats

### Decisions

Use:

```text
docs/decisions/
```

for important product or technical decisions.

Examples:

```text
0001-mvp-scope.md
0002-shop-scope.md
0003-cost-calculation-mode.md
0004-tablet-navigation.md
```

Do not create decision docs for every tiny change.  
Use them when a decision affects future implementation.

## Coding Guidelines

### General

- Keep MVP small.
- Prefer clear implementation over clever implementation.
- Avoid premature abstraction.
- Use typed interfaces where helpful.
- Keep business logic out of UI components when possible.
- Make shop scope explicit on the backend.

### Frontend

- Use TypeScript.
- Use TanStack Query for server state.
- Use React Hook Form + Zod for forms.
- Keep components readable and small.
- Prefer reusable components for:
  - Button
  - Card
  - Sidebar
  - Form field
  - Status badge
  - Recipe card
  - Prep task card

### Backend

- Use Django + DRF.
- Use PostgreSQL.
- Prefer model-level clarity.
- Use serializers for validation.
- Use viewsets where appropriate, but avoid overcomplicating early.
- Filter querysets by current shop.
- Keep cost calculation in backend service/helper functions.

### API

API prefix:

```text
/api/v1/
```

MVP APIs:

```text
Auth
Shop
Dashboard
Recipes
Ingredients
PrepTasks
Categories
Units
```

Do not implement Stripe, billing, or POS APIs in MVP.

## Testing Guidelines

At minimum, add tests for:

- Shop-scoped queryset filtering
- Recipe CRUD
- Ingredient cost modes
- Cost calculation
- PrepTask status updates
- Auth required endpoints

Important cases:

- User cannot access another shop's data
- `cost_mode=none` does not affect material cost
- `cost_mode=same_unit` calculates correctly
- `cost_mode=conversion` calculates correctly
- Selling price missing results in `cost_rate = null`

## Initial Implementation Order

Recommended order:

```text
1. Project scaffold
2. Docker Compose
3. Backend models
4. Auth / Shop scope
5. Categories / Units seed data
6. Ingredients
7. Recipes
8. Cost calculation
9. PrepTasks
10. Dashboard API
11. Frontend layout
12. Frontend screens
13. Form integration
14. UI polish
```

Do not start with Stripe.

Do not start with advanced prep logs.

Do not start with multi-shop management.

## Commit Message Style

Use Conventional Commits.

Examples:

```text
docs(planning): add Ricetta MVP requirements
feat(api): add ingredient cost mode
feat(frontend): add tablet sidebar layout
fix(cost): handle missing selling price
refactor(recipe): split recipe detail components
```

## Current MVP Reminder

The first version should prove this:

> 小さな飲食店が、レシピ台帳と今日の仕込みボードをひとつのアプリで使えるか。

If a feature does not support this directly, defer it.
