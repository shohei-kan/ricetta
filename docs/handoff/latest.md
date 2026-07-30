# Ricetta Handoff Latest

## Date

2026-07-30

## Project

Ricetta

## Status

GitHub Issue #5 のモバイルボトムナビ改善を実装済み。lint / build は成功し、実機Safariでの表示確認中。767px / 768px の境界確認は完了。

## Summary

`md` 未満の画面で、下スクロール時にボトムナビを隠し、上スクロール時とページ上部では再表示するようにした。24px のしきい値で小さなスクロール揺れを無視し、route変更時は表示状態へリセットする。背景は `bg-white/60` と `backdrop-blur-md` で軽くし、既存の表示対象パスとデスクトップサイドバーは維持している。

## Current Goal

Issue #5 の実ブラウザ確認を行い、問題がなければ `feat(frontend): hide bottom navigation on scroll` でコミットする。

## Current State

- 作業ブランチ: `feature/issue-5-hide-bottom-nav-on-scroll`
- モバイル境界: Tailwind `md` 未満（767px以下）
- `md` 以上: 既存の固定サイドバー
- ボトムナビ対象: Dashboard / Prep Today / Recipe List / Ingredient List / Settings / Account
- 詳細・作成・編集画面の既存表示条件は変更していない

## What Was Done

- `useBottomNavVisibility` hookを追加した。
- 24pxの移動しきい値とページ上部24pxの常時表示領域を設定した。
- passive scroll listenerとcleanupを実装した。
- route変更とbreakpoint変更時に表示状態をリセットするようにした。
- `translateY` / opacityによる200msの表示切替を追加した。
- reduced motion、非表示時のpointer events・tab focus除外に対応した。
- main下余白をsafe-area込みにした。
- ボトムナビ背景を半透明白＋backdrop blurへ変更し、境界線を軽くした。
- Safari対策としてviewport固定の外枠とアニメーションする内側を分離した。
- main下余白をナビ高72px＋safe-areaに合わせた。
- UIガイドラインへスクロール時の挙動を追記した。

## Key Decisions

- スクロール制御は既存breakpointに合わせて767px以下だけで有効にする。
- 小さな揺れを避けるため、直近の方向転換位置から24px移動した時だけ状態を切り替える。
- `fixed inset-x-0 bottom-0` は外側navだけが担当し、transformは内側要素だけに適用する。
- 既存のボトムナビ表示対象パスはIssue #5の範囲外として維持する。

## Key Files

- `frontend/src/components/AppLayout.tsx`
- `frontend/src/hooks/useBottomNavVisibility.ts`
- `docs/product/ui-guidelines.md`
- `docs/handoff/latest.md`

## Verification

実行済み:

```bash
cd frontend
npm run lint
npm run build
git diff --check
```

結果:

- frontend lint: pass
- frontend build: pass
- whitespace check: pass

Manual browser verification:

- iPhone Safariで一部確認済み。
- 767px以下でボトムナビ表示、768px以上でサイドバー表示になる境界確認は完了。
- 下端スクロール時の余白問題を確認し、viewport固定の外枠とアニメーション内側要素の分離で修正済み。
- 主要画面の最終確認のみ残っている。

## Current Product Scope

- Login / logout and Shop scope
- Recipe / Ingredient / Prep Today / Dashboard / Settings / Account
- Smartphone bottom navigation
- Tablet landscape / PC fixed sidebar
- Mobile bottom navigation hide-on-scroll

## Out of Scope for MVP

- Stripe / Checkout / Billing portal
- POS integration
- Automatic inventory deduction
- Multi-shop management UI
- Advanced role management
- Shop device mode

## Next Recommended Tasks

1. 375px前後で主要画面の初期表示、下スクロール、上スクロール、最上部復帰を確認する。
2. 767pxで同じ挙動とsafe-area下余白を確認する。
3. 768px以上でサイドバーが維持され、ボトムナビが表示されないことを確認する。
4. 非表示時にTabフォーカスがボトムナビへ移らないことを確認する。
5. 問題がなければIssue #5用コミットを作成する。

## Open Questions

- 実機Safariで `env(safe-area-inset-bottom)` を含む最下部余白を最終確認する。

## Notes for Next Agent

- ブラウザ自動確認はアプリ側エラーではなく、ブラウザ制御環境の初期化エラーで未実施。
- `npm run dev -- --host 127.0.0.1` は起動できた。
- 既存の画面別ナビ表示条件は `mobileBottomNavPaths` に残している。

## Suggested Commit Message

```text
feat(frontend): hide bottom navigation on scroll
```
