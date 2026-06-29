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
- READMEでは代表APIに絞り、詳細は `docs/api/api-design.md` へ誘導する。
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
