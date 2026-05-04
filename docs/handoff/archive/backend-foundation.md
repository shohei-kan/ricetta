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
