# Ricetta Handoff Latest

## Date

2026-07-11

## Project

Ricetta

## Status

Prep Today board memo and compact cards added

## Summary

Prep Todayの仕込みカードをコンパクト化し、各カードの操作を3カラム横並びにした。3カラムの下にはShopスコープの軽量BoardMemoを追加し、未アーカイブメモの追加・チェックでアーカイブ・履歴候補表示に対応した。

## Current Goal

実ブラウザで過去の未完了表示、当日完了表示、Prep Todayからの追加フォームを確認する。

## Current State

- `todo` / `doing` は予定日に関係なくPrepTask一覧へ表示する。
- `done` は `completed_at` のローカル日付が指定日（通常は今日）の場合だけ表示する。
- Prep TodayとDashboardの仕込みsummaryは、同じ表示対象の3status件数を返す。
- `completed_at`、done時の設定、未完了へ戻した際のnull化は既存実装を利用する。
- Prep Todayの追加フォームは現在Shopの有効Recipeと利用可能UnitをAPIから取得する。
- 追加フォームは未着手カラムのボタンからモーダルで開く。
- モーダルを閉じるとcomponentをアンマウントし、入力stateをリセットする。
- Recipe選択時に基準量と基準単位を初期入力し、今日・todoで作成する。
- Prep Todayの仕込みカードは、詳細 + 2つのstatus操作を3カラム横並びで表示する。
- BoardMemoはPrep Todayの3カラム下に表示し、チェックで `archived_at` を設定して一覧から消す。
- BoardMemoは現在Shopにスコープし、カテゴリ、期限、担当者、優先度はMVPでは持たない。
- Recipe Detailはレシピ確認・編集、Prep Todayは仕込み追加・進捗管理を担当する。
- Dashboard主見出しは認証sessionのShop名と権限バッジを表示する。
- Dashboardは今日の仕込み、次にやること、サマリー、期限注意に絞る。
- Dashboardの「今日の仕込み」「次にやること」「stats.prep_task_count」はPrep Todayと同じ表示対象を使う。
- Dashboardの「次にやること」は作業中を未着手より先に表示し、同status内は `sort_order, id` 順にする。
- Dashboardの「次にやること」カードは作業中を黄色系、未着手をオレンジ系で表示する。
- サイドバー下部はアカウントアイコンとアカウントラベルだけの導線にする。
- Recipe Editの材料行は材料名を広く、使用量・単位をコンパクトにし、メモを下段へ置く。
- 材料使用量の編集初期値は不要な小数末尾ゼロを除いて表示する。
- 材料・工程削除は右上×から確認後に実行する。
- 作り方は工程ごとの全幅入力＋下段メモで縦に並べる。
- 主要textareaは共通`AutoResizeTextarea`を使い、1行表示を基本にして既存値の表示時と入力時に内容量へ合わせて自動伸縮する。

## What Was Done

- PrepTask一覧querysetを未完了全件＋指定日完了へ変更した。
- 表示対象を基準にsummaryを集計するよう維持した。
- 過去todo / doing、当日done、過去完了除外、summaryのAPIテストを追加した。
- Prep Todayへ「仕込みを追加」ボタンとレスポンシブフォームを追加した。
- 画面上部の追加ボタンとインラインフォームを削除した。
- PCでは未着手ヘッダー右側に＋、スマホでは未着手上部に「＋ 仕込みを追加」を配置した。
- フォームをoverlay付き中央モーダルへ変更した。
- キャンセル、×、Esc、overlayクリックで閉じられるようにした。
- Recipe Detailの追加ボタン、フォーム、専用のAPI呼び出し・単位取得・バリデーションを削除した。
- 作成成功後に一覧を再取得してフォームを閉じるようにした。
- 完了カードの完了時刻表示を維持した。
- API、データモデル、画面仕様、decisionを更新した。
- Dashboardから「よく使うレシピ」と小さいRicetta見出しを削除した。
- Dashboard見出しをShop名＋権限へ変更し、2カラム比率を現場情報優先に調整した。
- サイドバー下部のAccount導線をアイコン＋ラベルだけに簡略化した。
- Recipe Editの材料カードをレスポンシブな3列＋メモ下段へ変更した。
- 材料行削除を右上のaria-label付き×ボタンへ変更した。
- RecipeIngredient数量のフォーム初期値から不要な末尾ゼロを除くhelperを追加した。
- 材料追加を背景なしの「＋ 追加」へ軽量化した。
- 材料・工程削除へwindow.confirmを追加した。
- 工程カードを番号ヘッダー、全幅作り方、下段メモ、右上×へ変更した。
- 工程追加を背景なしの「＋ 追加」へ軽量化した。
- 工程カードを白背景へ変更し、材料カードとトーンを統一した。
- `frontend/src/components/ui/AutoResizeTextarea.tsx` を追加した。
- Recipeの説明、材料メモ、作り方、工程メモ、アレルゲンメモ、注意点を共通textareaへ置き換えた。
- Ingredientのメモ、Prep Today追加モーダルのメモ、Accountの店舗メモを共通textareaへ置き換えた。
- Dashboard APIのPrepTask抽出条件をPrep Today APIと共通化した。
- Dashboard APIテストを未完了全件 + 対象日完了の表示対象に合わせて更新した。
- Dashboard API / data model / screen docsをPrep Today基準の表示に更新した。
- Dashboard APIの`next_tasks`を作業中 → 未着手の順に変更した。
- Dashboardの次にやることカードとstatusバッジを作業中=黄色系、未着手=オレンジ系へ変更した。
- Dashboard APIテストを作業中優先の順序へ更新した。
- `BoardMemo` model / serializer / API / migrationを追加した。
- BoardMemo APIは未アーカイブのみをデフォルト表示し、`include_archived=1`で履歴候補用に過去メモも返す。
- Prep Todayの3カラム下へ横長のメモカードを追加し、`＋ 追加` とチェックでアーカイブできるようにした。
- Prep Todayの仕込みカード余白を詰め、メモは空なら非表示、ある場合は1行表示へ調整した。
- Prep Todayカードの操作を、未着手=詳細/開始/完了、作業中=詳細/未着手/完了、完了=詳細/未着手/作業中にした。
- BoardMemo APIテストを追加した。

## Key Decisions

- 予定日より作業状態と完了日時をPrep Todayの表示基準にする。
- Dashboardの仕込み表示もPrep Todayを正として同じ表示基準にする。
- PrepTaskとBoardMemoは意味が違うため、BoardMemoは3カラム内に混ぜず下部補助カードに置く。
- MVPでは持ち越しラベル、優先度、トリアージ色を追加しない。
- 完了レコードは削除せず履歴として保持する。
- 追加操作は作成後に入る未着手カラムへ置き、一覧の視認性を優先する。
- 仕込み追加導線をPrep Todayへ一本化し、Recipe Detailは確認・編集に集中させる。
- 詳細は `docs/decisions/0006-prep-today-active-task-scope.md` を参照する。

## Key Files

- `backend/api/views.py`
- `backend/api/tests.py`
- `backend/api/models.py`
- `backend/api/serializers.py`
- `backend/api/urls.py`
- `backend/api/migrations/0005_boardmemo.py`
- `frontend/src/pages/PrepTodayPage.tsx`
- `frontend/src/api/boardMemos.ts`
- `frontend/src/pages/RecipeDetailPage.tsx`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/components/AppLayout.tsx`
- `frontend/src/components/ui/AutoResizeTextarea.tsx`
- `frontend/src/pages/RecipeFormPage.tsx`
- `frontend/src/pages/IngredientFormPage.tsx`
- `frontend/src/pages/PrepTodayPage.tsx`
- `frontend/src/pages/AccountPage.tsx`
- `docs/api/api-design.md`
- `docs/data/data-model.md`
- `docs/product/screens.md`
- `docs/decisions/0006-prep-today-active-task-scope.md`

## Verification

実行済み:

```bash
docker compose exec backend python manage.py test api.tests.BoardMemoApiTests api.tests.PrepTaskApiTests api.tests.DashboardApiTests
docker compose exec backend python manage.py makemigrations --check --dry-run
cd frontend && npm run lint
cd frontend && npm run build
```

Result:

- BoardMemo + PrepTask + Dashboard API tests: 38 pass
- Migration check: pass（変更なし）
- Frontend lint: pass
- Frontend build: pass
- Creation modal lint/build: pass
- Dashboard lint/build: pass
- Recipe form lint/build: pass
- Recipe step auto-resize lint/build: pass
- Global textarea lint/build: pass
- in-app browser: 実行環境メタデータの`sandboxPolicy`欠落により起動できず、手動確認は未実施

## Current Product Scope

- Login / logout and Shop scope
- Recipe / Ingredient / Prep Today / Dashboard / Settings / Account
- Active Prep Today board and direct PrepTask creation
- Smartphone, tablet landscape, and PC layouts

## Out of Scope for MVP

- 持ち越しラベル
- 仕込み優先度 / トリアージ色
- PrepTask履歴専用画面
- BoardMemoのカテゴリ / 期限 / 担当者 / 優先度
- Stripe / POS / inventory automation

## Next Recommended Tasks

1. 過去未完了、当日完了、過去完了除外を実データで確認する。
2. Prep Todayから追加でき、Recipe Detailには追加導線がないことを確認する。

## Open Questions

- 将来の履歴画面で完了タスクをどの期間・単位で検索するか。

## Notes for Next Agent

- `completed_at` は既存の `0004_preptask` migrationに含まれるため、新規migrationは不要。
- `date` query parameterは完了日の基準日として残している。
- backendのShop scopeとRecipe / Unit scoped validationは既存serializer fieldで維持している。
- 開発用ログインは `owner@example.com` / `password`。
- Docker frontendは `http://localhost:5174`。

## Suggested Commit Message

```text
feat(prep): add board memos and compact task cards
```
