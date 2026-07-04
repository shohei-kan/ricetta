# Ricetta Handoff Latest

## Date

2026-07-05

## Project

Ricetta

## Status

Mobile Recipe Detail swipe navigation implemented

## Summary

`lg`未満のRecipe Detailで、概要・材料・作り方をタップに加えて横スワイプでも切り替えられるようにした。PC / タブレット横の一覧表示には影響しない。

## Current Goal

実ブラウザで390px前後とPC / タブレット幅を目視確認する。

## Current State

- Recipe Detail上部にはカテゴリ、レシピ名、基準量 / 単位を常時表示する。
- `lg`未満は概要・材料・作り方の3タブをcomponent stateで切り替える。
- 左スワイプで次、右スワイプで前のタブへ移動する。
- 横50px以上かつ横移動優位の場合だけ反応し、縦スクロールを優先する。
- 原価情報はモバイルの概要表示に含める。
- `lg`以上はタブを隠し、上部統合カード、中段の材料・作り方2カラム、下段の補助情報3カラムで表示する。
- タブは左右余白付き、最大幅 `max-w-lg` のセグメント表示にする。
- Recipe Detailタブとスマホヘッダーはstickyにしない。
- 材料メモは初期非表示で、メモがある場合だけ表示切り替えを出す。
- 今日の仕込み追加フォームと編集導線は概要タブにある。
- 戻るを左、今日の仕込み追加と編集を右に置き、同じ高さの上部操作バーにする。
- 原価カードはbackendの `cost_summary` をそのまま表示し、frontendでは原価計算しない。
- 材料別原価は現在のRecipe Detail APIに含まれないため表示していない。
- スマホのボトムナビはDashboard、Prep Today、Recipe List、Ingredient List、Settingsだけに表示する。
- スマホヘッダーはロゴとアカウントアイコンだけを表示する。
- スマホのボトムナビは5項目すべてをLucideアイコン + 小さいラベルで表示する。
- PC / タブレット横のサイドナビも同じLucideアイコン + テキストで表示する。

## What Was Done

- Recipe Detailのモバイル表示を概要・材料・作り方の3タブへ変更した。
- `lg`以上をタブなしの一覧表示へ変更した。
- 独立していたレシピ概要カードを上部のレシピ名カードへ統合した。
- `lg`以上で材料と作り方を1:1の2カラムへ変更した。
- 原価・注意点・アレルゲンを材料・作り方の下段へ移動した。
- タブの横幅、余白、active配色を落ち着いたセグメント表現へ調整した。
- 材料を区切り線中心のコンパクトなリストへ変更した。
- 下ごしらえメモの表示 / 非表示切り替えを追加した。
- 作り方を丸い手順番号付きの工程リストへ変更した。
- 原価サマリーをレスポンシブな2列表示へ対応した。
- `AppLayout` が実pathnameを受け取り、スマホのボトムナビ表示を制御するよう変更した。
- `lucide-react` を追加し、手描きSVGをHome / ClipboardList / BookOpen / Package / Settingsへ置き換えた。
- スマホヘッダーの設定ボタンを削除し、アカウントをCircleUserRoundアイコンへ変更した。
- Recipe Detailタブとスマホヘッダーのsticky指定を解除した。
- サイドナビへHome / ClipboardList / BookOpen / Package / Settingsアイコンを追加した。
- Recipe Detailの画面仕様を更新した。

## Key Decisions

- レシピの識別に必要な基本情報はタブ切り替え後も常時見えるようにする。
- 原価はbackend算出値のみ表示し、材料別内訳をfrontendで推測しない。
- 詳細・作成・編集・Accountではスマホのボトムナビを非表示にする。
- 材料名と分量の一覧性を優先し、材料メモは利用者が必要なときだけ開く。
- 読む画面の縦領域を優先し、上部UIはスクロールに追従させない。
- 画面幅を活かせる`lg`以上では情報をタブで隠さない。
- 現場で同時参照しやすい材料と作り方を同じ行に置き、管理・補助情報は下段へ下げる。
- レスポンシブ間でセクションを複製せず、同じコンポーネントをCSSで切り替える。
- スワイプ判定はReact touch eventとrefだけで実装し、新規依存を追加しない。

## Key Files

- `frontend/src/pages/RecipeDetailPage.tsx`
- `frontend/src/components/AppLayout.tsx`
- `frontend/src/App.tsx`
- `frontend/package.json`
- `frontend/package-lock.json`
- `docs/product/screens.md`

## Verification

実行済み:

```bash
cd frontend && npm run lint
cd frontend && npm run build
```

Result:

- Frontend lint: pass
- Frontend build: pass
- 390px幅の静的レイアウト確認: タブ約318px、5項目ナビは各約72pxで収まる
- Responsive条件確認: `lg:hidden`の3タブ、中段`lg:grid-cols-2`、下段3カラムを使用
- Component確認: 材料一覧は全レスポンシブで同じstateful componentを使用
- Swipe条件確認: 50px閾値、横移動優位、先頭・末尾停止、`lg`以上無効
- DOM/CSS確認: Recipe Detailタブとスマホヘッダーにsticky / fixed指定なし
- Route確認: 一覧系5ルートだけボトムナビ表示、Recipe DetailとAccountは非表示
- in-app browser: 実行環境の接続情報不足により起動できず、実ブラウザ目視確認は未実施

## Current Product Scope

- Login / logout
- Shop-scoped Dashboard / Recipe / Ingredient / Prep / Settings / Account
- Recipe Detail responsive tab UI
- Smartphone and tablet landscape layouts

## Out of Scope for MVP

- 材料別原価内訳API
- Stripe / POS / inventory automation
- Multi-shop UI

## Next Recommended Tasks

1. 390px前後で3タブ、概要内の原価、材料メモ切り替えを目視確認する。
2. 1024px前後とPC幅で上部統合カード、中段2カラム、下段補助情報を確認する。
3. Recipe Listなど一覧系ではボトムナビが表示され、詳細・作成・編集・Accountでは非表示になることを確認する。

## Open Questions

- 材料別原価内訳を将来表示する場合、Recipe Detail APIのレスポンスへ内訳を追加するか。

## Notes for Next Agent

- backend変更は不要という要件に従い、APIやcost calculationは変更していない。
- `backend/api/tests.py` に今回の作業以前からある未コミット変更には触れていない。
- 開発用ログインは `owner@example.com` / `password`。
- Docker frontendは `http://localhost:5174`。

## Suggested Commit Message

```text
feat(frontend): refine desktop recipe workspace
```
