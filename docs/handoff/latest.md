# Ricetta Handoff Latest

## Date

2026-05-04

## Project

Ricetta

## Status

Project scaffold

## Summary

Ricettaプロジェクトの開発土台を整えた。backend (Django + DRF)、frontend (React + Vite + TypeScript + Tailwind CSS)、Docker Compose、CIを設定。

## Current Goal

Ricettaの開発土台を整える。

## What Was Done

- backend/ Django + DRF初期構成作成
- frontend/ React + Vite + TypeScript + Tailwind CSS初期構成作成
- Docker Compose設定 (backend, frontend, db)
- .env.example作成
- .gitignore作成
- GitHub Actions CI作成 (backend: check/migration/test, frontend: build/lint)
- docs/handoff/latest.md作成
- docs/handoff/archive/作成

## Key Decisions

- API prefix: /api/v1/
- DB: PostgreSQL
- 環境変数で設定管理
- health check API: GET /api/v1/health/

## Key Files

- docker-compose.yml
- .env.example
- .gitignore
- .github/workflows/ci.yml
- backend/requirements.txt
- backend/Dockerfile
- backend/ricetta/settings.py
- backend/api/views.py
- frontend/Dockerfile
- frontend/vite.config.ts
- frontend/tailwind.config.js
- frontend/postcss.config.js
- frontend/src/App.tsx

## Current Product Scope

MVPでやることを簡単に記載。

## Out of Scope for MVP

MVPでやらないことを簡単に記載。

## Technical Assumptions

- Frontend: React + Vite + TypeScript
- UI: Tailwind CSS + shadcn/ui (準備)
- Backend: Django + Django REST Framework
- DB: PostgreSQL
- Dev: Docker Compose
- CI: GitHub Actions
- API prefix: /api/v1/

## Next Recommended Tasks

1. レシピモデル実装
2. 材料モデル実装
3. 認証実装
4. レシピ一覧画面作成
5. レシピ作成画面作成

## Open Questions

- Stripe統合はMVP後
- 複数店舗管理は将来

## Notes for Next Agent

backendのhealth check APIが動作することを確認。frontendのトップ画面が表示されることを確認。

## Suggested Commit Message

```text
chore(scaffold): initialize Ricetta project structure and CI
```
