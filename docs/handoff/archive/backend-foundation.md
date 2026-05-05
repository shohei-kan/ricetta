# Backend Foundation Handoff Archive

Backend scaffold、Docker、CI、Auth / Shop scope、Category / Unit、Ingredient APIなど、backend土台作業に関するhandoffをここに追記する。

## 2026-05-04 Ingredient API and CI Fix

### Summary

Backend Foundation through Phase 3 is complete. Ricetta has Django 5.2.13, DRF, PostgreSQL, Docker Compose, GitHub Actions CI, health check, Auth / Shop Scope APIs, Category / Unit APIs, and Ingredient API with cost-mode validation.

### Completed Scope

- Project scaffold: `backend/`, `frontend/`, Docker Compose, `.env.example`, GitHub Actions CI.
- Backend foundation: Django + DRF, PostgreSQL, `/api/v1/` routing, health check.
- Auth / Shop scope: Django standard User, Shop, Membership, login/logout/me, shop/me.
- Category / Unit: shop-scoped categories, standard Units (`shop=null`), current-Shop Units.
- Docker / CI fixes:
  - Docker Compose reads `.env`.
  - backend uses `POSTGRES_HOST=db` in Docker.
  - CI backend uses PostgreSQL service at `localhost:5432`.
  - CI frontend uses Node.js 22.
- Ingredient:
  - `Ingredient` model and migration `0002_ingredient.py`.
  - Ingredient CRUD API.
  - server-side Shop assignment via `get_current_shop(user)`.
  - current-Shop queryset filtering.
  - logical delete with `is_active=false`.
  - Unit scope validation: standard Units + current-Shop Units only.
  - cost_mode validation for `none`, `same_unit`, and `conversion`.
  - `unit_cost_label` for Ingredient display.

### Key Decisions

- `shop_id` from frontend is never trusted for shop-scoped models.
- Current Shop is derived from active Membership.
- Ingredient is always scoped to current Shop.
- Ingredient can only reference standard Units or current-Shop Units.
- `same_unit` requires `usage_unit == purchase_unit`.
- `conversion` requires `conversion_from_unit == purchase_unit` and `conversion_to_unit == usage_unit`.
- Ingredient delete is logical delete.
- Recipe-level cost calculation is not implemented yet.
- Durable decisions live in `docs/decisions/`.

### Verification

Verified after Ingredient implementation:

```bash
docker compose run --rm backend python manage.py check
docker compose run --rm backend python manage.py makemigrations --check --dry-run
docker compose run --rm backend python manage.py test

cd frontend
npm run build
npm run lint
```

Result:

- Backend check: pass
- Migration check: pass
- Backend tests: 29 tests pass
- Frontend build: pass
- Frontend lint: pass

Also verified backend against a PostgreSQL test container after Ingredient implementation.

### Key Files

- `backend/api/models.py`
- `backend/api/serializers.py`
- `backend/api/views.py`
- `backend/api/urls.py`
- `backend/api/tests.py`
- `backend/api/migrations/0001_initial.py`
- `backend/api/migrations/0002_ingredient.py`
- `backend/api/shop_scope.py`
- `backend/api/management/commands/seed_initial_data.py`
- `backend/ricetta/settings.py`
- `docker-compose.yml`
- `.github/workflows/ci.yml`
- `docs/api/api-design.md`
- `docs/data/data-model.md`

## 2026-05-05 Recipe API

### Summary

Phase 4 is complete. Recipe / RecipeIngredient / RecipeStep backend models and API were added, with current-Shop scoping, nested create/update, logical delete, and Recipe detail `cost_summary`.

### Completed Scope

- `Recipe`, `RecipeIngredient`, and `RecipeStep` models.
- Migration `0003_recipe_recipeingredient_recipestep_and_more.py`.
- `GET /api/v1/recipes/`
- `POST /api/v1/recipes/`
- `GET /api/v1/recipes/{id}/`
- `PATCH /api/v1/recipes/{id}/`
- `DELETE /api/v1/recipes/{id}/`
- Recipe queryset filtering by current Shop and `is_active=true`.
- Server-side Shop assignment via `get_current_shop(user)`.
- Scope validation for Category, Ingredient, and Unit references.
- Nested create for ingredients and steps.
- Nested PATCH policy: replace submitted `ingredients` / `steps`.
- Logical delete with `is_active=false`.
- Recipe `cost_summary` calculation using Ingredient `cost_mode`.

### Key Decisions

- `shop_id` from frontend remains untrusted.
- RecipeIngredient can reference only current-Shop active Ingredients.
- Recipe and RecipeIngredient Units are limited to standard Units or current-Shop Units.
- Recipe Category is limited to current-Shop Categories.
- Costed RecipeIngredient rows must use the Ingredient `usage_unit`; mismatch is a validation error.
- Ingredients response in Recipe detail contains work information only: ingredient name, quantity, unit, order, memo.
- Recipe-level cost information is grouped in `cost_summary`.
- Material-level cost breakdown API is deferred.

### Verification

Verified after Recipe API implementation:

```bash
docker compose run --rm -e POSTGRES_HOST= backend python manage.py check
docker compose run --rm -e POSTGRES_HOST= backend python manage.py makemigrations --check --dry-run
docker compose run --rm -e POSTGRES_HOST= backend python manage.py test

cd frontend
npm run build
npm run lint
```

Result:

- Backend check: pass
- Migration check: pass
- Backend tests: pass
- Frontend build: pass
- Frontend lint: pass

### Key Files

- `backend/api/models.py`
- `backend/api/serializers.py`
- `backend/api/views.py`
- `backend/api/urls.py`
- `backend/api/costing.py`
- `backend/api/tests.py`
- `backend/api/migrations/0003_recipe_recipeingredient_recipestep_and_more.py`
- `docs/api/api-design.md`
- `docs/data/data-model.md`

## 2026-05-05 PrepTask API

### Summary

Phase 5 is complete. PrepTask backend model and API were added for the Today's Prep board, including date-filtered list responses, status summary, status update API, and current-Shop scoping.

### Completed Scope

- `PrepTask` model.
- Migration `0004_preptask.py`.
- `GET /api/v1/prep-tasks/`
- `POST /api/v1/prep-tasks/`
- `GET /api/v1/prep-tasks/{id}/`
- `PATCH /api/v1/prep-tasks/{id}/`
- `DELETE /api/v1/prep-tasks/{id}/`
- `PATCH /api/v1/prep-tasks/{id}/status/`
- Date-filtered PrepTask list with `summary` and `tasks`.
- Server-side Shop assignment via `get_current_shop(user)`.
- Scope validation for Recipe and Unit references.
- Status transitions with `completed_at` handling.

### Key Decisions

- `shop_id` from frontend remains untrusted.
- PrepTask can reference only current-Shop active Recipes.
- PrepTask Units are limited to standard Units or current-Shop Units.
- PrepTask list uses server today when `date` is omitted.
- PrepTask list is ordered by `sort_order, id` for MVP.
- PrepTask delete is physical delete for MVP.
- Status can be updated through normal PATCH, but the UI-oriented tap flow should use the dedicated `status/` endpoint.
- `done` sets `completed_at=now`; moving back to `todo` or `doing` clears `completed_at`.

### Verification

Verified after PrepTask API implementation:

```bash
docker compose run --rm backend python manage.py check
docker compose run --rm backend python manage.py makemigrations --check --dry-run
docker compose run --rm backend python manage.py test

cd frontend
npm run build
npm run lint
```

Result:

- Backend check: pass
- Migration check: pass
- Backend tests: pass
- Frontend build: pass
- Frontend lint: pass

### Key Files

- `backend/api/models.py`
- `backend/api/serializers.py`
- `backend/api/views.py`
- `backend/api/urls.py`
- `backend/api/tests.py`
- `backend/api/migrations/0004_preptask.py`
- `docs/api/api-design.md`
- `docs/data/data-model.md`

## 2026-05-05 Dashboard API

### Summary

Phase 6 is complete. Dashboard API was added as a current-Shop scoped aggregate endpoint for the post-login "today on the floor" view.

### Completed Scope

- `GET /api/v1/dashboard/`
- `date=YYYY-MM-DD` query support.
- Server today fallback when `date` is omitted.
- `prep_summary` for `todo` / `doing` / `done` PrepTask counts.
- `next_tasks` for incomplete PrepTasks, ordered by `sort_order, id`, limited to 5.
- `frequent_recipes` for most-used Recipes based on PrepTask usage count, limited to 5.
- `stats` for active Recipe count, active Ingredient count, and target-date PrepTask count.
- `alerts` as an empty array for MVP.
- Dashboard tests for auth, shop scope, summaries, next tasks, frequent recipes, stats, and alerts.

### Key Decisions

- Dashboard is an aggregate API, not a persistent model.
- `shop_id` from frontend remains untrusted.
- Dashboard scope is determined by `get_current_shop(user)`.
- `frequent_recipes` uses PrepTask usage count for MVP.
- `alerts` is always `[]` until expiry / remaining quantity features exist.

### Verification

Verified after Dashboard API implementation:

```bash
docker compose run --rm backend python manage.py check
docker compose run --rm backend python manage.py makemigrations --check --dry-run
docker compose run --rm backend python manage.py test

cd frontend
npm run build
npm run lint
```

Result:

- Backend check: pass
- Migration check: pass
- Backend tests: pass
- Frontend build: pass
- Frontend lint: pass

### Key Files

- `backend/api/views.py`
- `backend/api/urls.py`
- `backend/api/tests.py`
- `docs/api/api-design.md`
- `docs/data/data-model.md`
