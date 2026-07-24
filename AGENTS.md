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
  README.md
  product/
  technical/
  decisions/
  figma/
  handoff/
    latest.md
    archive/
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
- Do not expose `shop_id` as a writable serializer field for shop-scoped models.
- Create shop-scoped records by setting `shop` on the server side.
- Users must not read, update, or delete another shop's data.

Main shop-scoped data:

- Recipe
- Ingredient
- PrepTask
- Category
- Unit, for shop-specific units
- RecipeIngredient, through Recipe
- PrepLog, future
- Subscription, future

When adding a new shop-scoped model, also add tests that prove cross-shop access is blocked for list/detail/update/delete and that create ignores frontend-provided shop identifiers.

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

## Architecture Responsibility Rules

Keep frontend, backend, and database responsibilities clear.

Frontend is responsible for:

- UI rendering
- Form interaction
- Client-side validation for better UX
- API calling
- Loading, error, and empty states
- Temporary screen state

Frontend must not make final authorization decisions. Frontend must not decide or trust `shop_id`. Frontend may display cost values, but final cost calculation belongs on the backend.

Backend is responsible for:

- Authentication
- Authorization
- Shop scope enforcement
- Data validation
- Persistent business rules
- Cost calculation
- API response shape
- Database writes

Backend must treat all frontend input as untrusted. Validate data again on the server even when the frontend already validates it.

Database is responsible for:

- Persistence
- Relational integrity
- Schema managed by migrations

Use database constraints where they protect important integrity, but keep request-aware rules such as current-Shop scope in backend serializers, querysets, and services.

## API and Save Behavior Rules

- All MVP APIs use `/api/v1/`.
- Business APIs require authentication.
- Create and update endpoints should return saved data or a useful summary.
- Validation errors should be clear enough for forms to display.
- Do not return raw stack traces or internal implementation details to the frontend.
- Keep API response shapes stable once frontend integration starts.
- When an API response changes, update `docs/technical/api-design.md`.

For nested writes, such as Recipe with ingredients and steps:

- Choose a simple MVP strategy.
- Document the strategy in `docs/handoff/latest.md`.
- If the strategy affects future implementation, add or update `docs/decisions/`.

## Error Handling Rules

Backend:

- Return 400 for validation errors.
- Return 401 for unauthenticated requests.
- Return 403 or 404 for unauthorized access.
- For cross-shop data access, prefer 404 when hiding the existence of the resource is safer.
- Avoid leaking internal implementation details.

Frontend:

- Show a clear message when saving fails.
- Keep form input when an API request fails.
- Show loading, empty, and error states.
- Do not show raw stack traces or technical errors to users.

User-facing message examples:

```text
保存に失敗しました。もう一度お試しください。
入力内容を確認してください。
ログインが必要です。
このデータは見つかりませんでした。
```

## Cost Calculation Rules

Ricetta separates material work information from management cost information.

```text
ingredients = 作るための情報
cost_summary = 管理情報
```

- Ingredient and recipe material lists should show work information only.
- Do not mix cost details into ingredient rows on Recipe Detail.
- Recipe-level cost information should be returned as `cost_summary`.
- Cost calculation should be implemented on the backend.
- Frontend should display cost results, not calculate final values.
- Keep detailed accounting behavior small for MVP; document rounding or calculation tradeoffs when they affect future work.

## Documentation Rules

Keep documentation current when implementation changes.

Important docs:

```text
docs/product/concept.md
docs/product/mvp-requirements.md
docs/product/mvp-roadmap.md
docs/product/screens.md
docs/product/ui-guidelines.md
docs/technical/data-model.md
docs/technical/api-design.md
docs/handoff/latest.md
docs/decisions/
```

Update docs according to the type of change:

| Change | Update |
|---|---|
| Product scope change | `docs/product/mvp-requirements.md` |
| Implementation order change | `docs/product/mvp-roadmap.md` |
| Screen or UI change | `docs/product/screens.md` or `docs/product/ui-guidelines.md` |
| Data model change | `docs/technical/data-model.md` |
| API change | `docs/technical/api-design.md` |
| Long-term decision | `docs/decisions/` |
| Completed task or next context | `docs/handoff/latest.md` |
| Setup or command change | `README.md` |

At the end of a Codex task, update `docs/handoff/latest.md` by default unless the task is truly tiny and does not affect the next agent's context.

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

for the latest working context only.

`latest.md` is not the full project history. It is the current handoff for the next agent: where the project is now, what matters for the next task, and what to do next.

Move older handoffs into:

```text
docs/handoff/archive/
```

when a phase is completed, the next work theme starts, `latest.md` has become too long, or older details make the current state hard to see.

Do not create a new archive file for every handoff. Archive files should be grouped by broad topic. If the broad topic already exists, append a new entry to that file instead of creating a new file.

```text
docs/handoff/archive/index.md
docs/handoff/archive/planning-and-docs.md
docs/handoff/archive/backend-foundation.md
docs/handoff/archive/frontend-implementation.md
docs/handoff/archive/release-prep.md
```

Create additional archive files only when a new broad topic is needed, for example:

```text
docs/handoff/archive/billing-and-subscription.md
docs/handoff/archive/deployment.md
```

`docs/handoff/archive/index.md` is the archive table of contents. It should list archive files and their broad purpose, not every small work entry.

Inside each archive file, separate entries with date and title headings:

```text
# Backend Foundation Handoff Archive

## 2026-05-04 Initial scaffold

Summary...

## 2026-05-04 Auth and shop scope

Summary...
```

`latest.md` should use this fixed structure:

```text
# Ricetta Handoff Latest

## Date
## Project
## Status
## Summary
## Current Goal
## Current State
## What Was Done
## Key Decisions
## Key Files
## Verification
## Current Product Scope
## Out of Scope for MVP
## Next Recommended Tasks
## Open Questions
## Notes for Next Agent
## Suggested Commit Message
```

A handoff should include:

- Date
- Project
- Current status
- What was done
- Key files
- Current decisions
- Next recommended tasks
- Notes / caveats
- Suggested Commit Message

Handoff content rules:

- Keep `latest.md` short and current.
- Do not accumulate the full project history in `latest.md`.
- Do not repeat old phase details at length.
- Prefer links or references to archive files instead of repeating old history.
- Include only decisions and caveats that affect the next work.
- Remove resolved open questions.
- Record verification that was actually run.
- If verification could not be run, say exactly why.
- Do not use handoff files for long-term product or technical decisions.

### Decisions

Use:

```text
docs/decisions/
```

for important product or technical decisions.

All decision docs belong under `docs/decisions/`. Do not use a root-level `decisions/` directory.

Examples:

```text
0001-mvp-scope.md
0002-shop-scope.md
0003-cost-calculation-mode.md
0004-tablet-navigation.md
```

Future decision candidates, when the implementation needs them:

```text
0006-auth-and-csrf-strategy.md
0007-image-upload-scope.md
```

Do not create decision docs for every tiny change.  
Use them when a decision affects future implementation.

Use decision docs for durable choices such as MVP scope, shop scope, cost calculation mode, navigation, or documentation structure. Use handoff files for short-lived working context such as what changed in the last task, what was verified, and what the next agent should do.

## Coding Guidelines

### General

- Keep MVP small.
- Prefer clear implementation over clever implementation.
- Avoid premature abstraction.
- Use typed interfaces where helpful.
- Keep business logic out of UI components when possible.
- Make shop scope explicit on the backend.
- Do not refactor large unrelated areas.
- Do not rename directories or change project structure without a clear reason.

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
- Client-side validation is for UX only; backend validation is authoritative.
- Preserve form input when save requests fail.
- Show loading, empty, and error states for API-backed screens.

### Backend

- Use Django + DRF.
- Use PostgreSQL.
- Prefer model-level clarity.
- Use serializers for validation.
- Use viewsets where appropriate, but avoid overcomplicating early.
- Filter querysets by current shop.
- Keep cost calculation in backend service/helper functions.
- Treat frontend input as untrusted.
- Do not expose `shop_id` as writable for shop-scoped models.
- Do not change the authentication strategy without explicit direction.

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

Do not add Stripe, billing, POS integration, inventory automation, or multi-shop UI during MVP unless explicitly requested.

### Migrations

- Model changes require migrations.
- Do not rewrite existing migrations casually after they may have been shared.
- Run migration checks before considering backend work complete.
- Prefer Docker Compose for local verification when the task depends on the project runtime.

Recommended backend checks:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Docker equivalent:

```bash
docker compose run --rm backend python manage.py check
docker compose run --rm backend python manage.py makemigrations --check --dry-run
docker compose run --rm backend python manage.py test
```

### Environment Variables and Secrets

- `.env` must not be committed.
- Update `.env.example` when new environment variables are added.
- Do not hardcode secret keys, database passwords, Stripe keys, or tokens.
- Use development defaults only when they are clearly safe for local development.
- Production-like secrets must be provided through environment variables.

When adding a new environment variable, update:

- `.env.example`
- `README.md`, if developers need setup information
- `docs/handoff/latest.md`, if it affects the current task or next agent

### Dependencies

- Do not add new dependencies casually.
- Check whether the existing stack can solve the problem first.
- Prefer built-in Django, DRF, React, and TypeScript features when reasonable.
- Add a short reason in the task summary or handoff when adding a dependency.
- Update lockfiles.
- Ensure CI passes.

Do not add these without explicit direction:

- New UI library
- New state management library
- New API client library
- New auth library
- Payment library

### CI

- Do not proceed to the next implementation phase with known failing CI.
- If CI fails because of environment configuration, fix CI before adding business features.
- Keep CI minimal and fast.
- Do not add deployment or CD workflows unless explicitly requested.
- Do not add secrets-dependent CI jobs during MVP setup.

Recommended checks:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
npm run build
npm run lint
```

Consider adding frontend `typecheck` only after the project has a stable script for it.

### Codex Scope Guardrails

- Do not implement features outside the current prompt.
- Do not add future SaaS features unless explicitly requested.
- Do not implement Stripe, billing, POS integration, inventory automation, or multi-shop UI during MVP unless explicitly requested.
- Do not refactor large unrelated areas.
- Do not rename directories or change project structure without a clear reason.
- Do not change authentication strategy without explicit direction.
- Do not silently change API response shapes.
- Do not add new dependencies, migrations, or environment variables for documentation-only tasks.

When a necessary design judgment comes up:

- Record task-local context in `docs/handoff/latest.md`.
- Record or propose a decision doc in `docs/decisions/` if the choice has long-term product or technical impact.

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
