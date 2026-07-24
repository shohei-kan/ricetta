# Planning And Docs Handoff Archive

企画、MVP要件、画面設計、データ/API設計などの初期ドキュメント整理に関するhandoffをここに追記する。

## 2026-06-29 Portfolio README restructuring

採用担当者・面接官がプロダクト背景とbackend設計を把握しやすいよう、READMEを転職用ポートフォリオとして再構成した。

### Summary

- 飲食店運営経験を起点にしたPortfolio SummaryとBackgroundを追加
- ScreenshotsのTODO枠を追加
- 実装済み機能とMVP対象外を分離
- 実際の依存関係に合わせてTech Stackを修正
- Why This Stack、Architecture、Backend Design Highlightsを追加
- Shopスコープ、Session / CSRF、owner権限、原価計算、nested writeを説明
- Data Model Overviewと代表APIへ情報量を整理
- SetupとEnvironment Variablesの重複を統合
- GitHub Actionsの実態に合わせてTest / CIを更新
- Challenges and Learnings、Current Status、Future Improvementsを追加
- 古いInitial planning、Implementation Order、未導入技術の実装済み表現を削除

### Key Decisions

- TanStack Query、React Hook Form、Zod、shadcn/uiは未導入であることを明記する。
- 将来のSaaS化と現在のMVPを混同しない。
- READMEでは代表APIに絞り、詳細は `docs/technical/api-design.md` へ誘導する。
- スクリーンショット未配置をTODOとして明示する。

### Key Files

- `README.md`
- `frontend/package.json`
- `backend/requirements.txt`
- `docker-compose.yml`
- `.github/workflows/ci.yml`

### Verification

- `git diff --check`: pass
- Markdown code fences: even count
- README relative documentation links: existing filesを参照

## 2026-07-24 Docs directory structure cleanup

docs配下を読む目的ごとに整理し、参照パスを新しい配置へ揃えた。

### Summary

- `docs/README.md` を追加し、docs全体の入口を用意した。
- 企画・要件・ロードマップを `docs/product/` へ集約した。
- API設計とデータモデルを `docs/technical/` へ集約した。
- `docs/api/`、`docs/data/`、`docs/planning/` は空になったため削除した。
- README、AGENTS、decisions、handoff archive内の参照パスを新配置へ更新した。
- handoff archiveの運用ルールは `docs/handoff/archive/index.md` に明記済み。

### New Structure

```text
docs/
  README.md
  product/
  technical/
  decisions/
  handoff/
  figma/
```

### Key Files

- `docs/README.md`
- `docs/product/`
- `docs/technical/`
- `docs/decisions/0005-documentation-structure.md`
- `docs/handoff/archive/index.md`
- `AGENTS.md`
- `README.md`

### Verification

- 古い `docs/api` / `docs/data` / `docs/planning` 参照が残っていないことを確認
- `git diff --check`: pass
