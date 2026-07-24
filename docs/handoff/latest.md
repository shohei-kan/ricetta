# Ricetta Handoff Latest

## Date

2026-07-24

## Project

Ricetta

## Status

Demo login account selection added to the public demo login page.

## Summary

AWS公開デモ環境向けに、`VITE_DEMO_MODE=true` のときだけログイン画面へ公開デモ用アカウント情報を表示し、owner / staffカード選択でログインフォームのメールアドレスとパスワードを切り替えられるようにした。初期状態はownerアカウントで、カード選択は入力補助のみ。自動ログインや自動submitは行わない。通常モードではデモ用アカウント情報も初期入力も出さない。

## Current Goal

次はAWS公開デモ用の実運用準備へ進める。具体的には、公開環境の実env値、デモ環境で追加禁止する操作範囲、定期resetの実行方法、実ブラウザでのdemoログイン表示とowner/staff導線確認を詰める。

## Current State

- backendは `DEMO_MODE` を `settings.py` で扱える。
- frontendは `VITE_DEMO_MODE=true` のときだけDemoBannerを表示する。
- `VITE_DEMO_MODE=true` のときだけLoginPageに公開デモ用アカウント情報を表示する。
- `VITE_DEMO_MODE=true` のときだけLoginPageのフォーム初期値に `owner@example.com / password` を入れる。
- `VITE_DEMO_MODE=true` のときだけowner / staffカード選択でフォーム入力値を切り替えられる。
- 通常モードではLoginPageにデモ用ログイン情報を表示せず、フォーム初期値も空にする。
- `backend/api/demo_policy.py` に `deny_in_demo()` を追加済み。ただし既存Viewにはまだ適用していない。
- `seed_portfolio_data --reset` を追加済み。固定Shop名 `〇〇食堂` のデモShopだけを削除し、サンプルデータを再投入する。
- ownerはRecipe / Ingredient / Category / Unit / Shop情報の作成・編集・削除ができる。
- staffはRecipe / Ingredient / Category / Unitを閲覧・参照できるが、作成・編集・削除はAPIで403になる。
- staffはPrepTask作成、PrepTask status変更、BoardMemo追加・チェック、自分の表示名編集ができる。
- Accountではstaffに店舗情報編集フォームを出さない既存UIを維持している。
- Recipe / Ingredientの一覧・詳細・フォームはstaff向け表示制御を追加済み。
- SettingsではstaffにCategory / Unitの管理フォーム、編集ボタン、削除ボタンを出さず、参照一覧と権限メッセージを表示する。
- `docs/deploy/demo.md` に公開デモ用ログイン情報とowner/staff権限概要を追記済み。
- docsは `product/`、`technical/`、`deploy/`、`decisions/`、`handoff/` に整理済み。

## What Was Done

- `frontend/src/pages/LoginPage.tsx` にdemo時だけ表示される `DemoAccountInfo` を追加した。
- demo時だけログインフォーム初期値を `owner@example.com / password` にした。
- owner / staffカードクリックでフォームのemail/passwordを切り替える入力補助を追加した。
- 選択中カードにオレンジ系の枠線、淡い背景、`選択中` ラベルを表示した。
- 手入力した場合はカードの選択状態を外すようにした。
- owner / staffのログイン情報をコピーしやすい等幅表示にした。
- PC / タブレット幅ではowner / staffカードを2カラム横並びにした。
- staffが編集できない操作を、強すぎない赤系の情報ボックスで明記した。
- `docs/deploy/demo.md` に公開デモ用ログイン情報、初期入力、カード選択、自動ログインしない方針、権限概要を追記した。
- `docs/handoff/archive/release-prep.md` に今回のrelease prep履歴を追記した。

## Key Decisions

- DEMO_MODEとowner/staff権限は別物として扱う。
- 公開デモ用ログイン情報は `VITE_DEMO_MODE=true` のときだけ表示する。
- デモ用ログインフォーム初期値も `VITE_DEMO_MODE=true` のときだけ使う。
- デモ用アカウントカードはフォーム入力値を切り替えるだけで、自動ログインしない。
- 通常モードではデモ用ログイン情報を表示せず、初期入力もしない。
- 通常のrole制御として、Recipe / Ingredient / Category / Unit / Shopの管理操作はowner限定にする。
- staffには現場運用に必要なPrepTask / BoardMemo操作を許可する。
- ワンクリックログイン、コピー機能、デモリセットAPI / ボタンは今回実装しない。
- owner/staffの権限ロジックやbackendは今回変更しない。

## Key Files

- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/config/demo.ts`
- `docs/deploy/demo.md`
- `docs/handoff/latest.md`
- `docs/handoff/archive/release-prep.md`

## Verification

実行済み:

```bash
cd frontend
npm run lint
npm run build
VITE_DEMO_MODE=true npm run build
git diff --check
```

Result:

- frontend lint: pass
- frontend build: pass
- frontend build with `VITE_DEMO_MODE=true`: pass
- whitespace check: pass

Manual browser verification:

- `VITE_DEMO_MODE=true npm run dev` でログイン画面に公開デモ用アカウント情報が表示されることを確認。
- 初期状態で `owner@example.com / password` が入力されることを確認。
- owner / staffカードクリックでフォーム入力値と選択状態が切り替わることを確認。
- カードクリックだけでは自動ログインされないことを確認。
- 通常起動ではデモアカウント情報が表示されず、email/password初期値も空であることを確認。
- owner / staff 両方でログインできることを確認。

## Current Product Scope

- Login / logout and Shop scope
- owner / staff role control for MVP operations
- Recipe / Ingredient / Prep Today / Dashboard / Settings / Account
- Active Prep Today board and direct PrepTask creation
- BoardMemo as lightweight whiteboard memo under Prep Today columns
- Smartphone, tablet landscape, and PC layouts
- Demo mode foundation via environment variables
- Safe portfolio demo seed reset
- Public demo operation docs
- Demo login account information on LoginPage

## Out of Scope for MVP

- Stripe / Checkout / Billing portal
- POS integration
- Automatic inventory deduction
- Advanced ordering
- Multi-shop management UI
- Advanced role management beyond owner / staff
- Shop device mode
- Demo reset API / reset button
- cron / systemd timer実設定
- AWSインスタンス作成
- Docker Compose production構成の大幅変更
- Demo-specific branch or duplicated app directories

## Next Recommended Tasks

1. ブラウザで `VITE_DEMO_MODE=true` のログイン画面に公開デモ用アカウント情報が表示され、`owner@example.com / password` が初期入力されることを確認する。
2. owner / staffカードクリックでフォーム入力値と選択状態が切り替わり、自動ログインされないことを確認する。
3. 通常起動でログイン画面に公開デモ用アカウント情報が表示されず、フォーム初期値も空であることを確認する。
4. owner / staff両方でログインし、導線と403挙動を手動確認する。
5. AWS公開デモ用の実env値を整理する。
6. デモ環境で追加禁止する操作（メール変更、パスワード変更、アカウント削除、店舗削除など）の範囲を決め、必要なViewに `deny_in_demo()` を適用する。
7. `seed_portfolio_data --reset` の定期実行方法（cron / systemd timer等）を別タスクで検討する。

## Open Questions

- デモ環境の自動リセット頻度をどうするか。
- デモ環境で通常role制御に加えて、どの操作を追加禁止するか。

## Notes for Next Agent

- `owner@example.com` / `password` と `staff@example.com` / `password` は `seed_portfolio_data` で再作成・更新される。
- `VITE_DEMO_MODE=true` のとき、LoginPageに `owner@example.com / password` と `staff@example.com / password` を表示し、フォーム初期値にはownerアカウントを入れる。
- demoアカウントカードクリックはフォーム値の切り替えのみ。自動ログインや自動submitはしない。
- 通常モードではLoginPageのemail/password初期値は空。
- `VITE_DEMO_MODE` はViteのbuild時環境変数。公開環境ではfrontend build/deploy時に設定する必要がある。
- staffはRecipe / Ingredientのフォーム直URLにアクセスしても、frontendでは権限メッセージを表示し、APIでも403になる。
- staffはSettingsを開いてCategory / Unit一覧を参照できるが、管理フォーム、編集、削除は表示されない。APIでもCategory / Unit変更操作は403になる。
- Shop情報更新は既存通りowner限定。表示名更新はowner / staff両方可能。
- `backend/api/demo_policy.py` はまだ既存Viewから使っていない。DEMO_MODE固有制限は次タスクで明示的に行う。
- production envにはlocalhostを含めない。
- docsの旧パス `docs/api/`、`docs/data/`、`docs/planning/` は廃止済み。新規参照は `docs/technical/` または `docs/product/` を使う。
- Docker frontendは `http://localhost:5174`。

## Suggested Commit Message

```text
feat(demo): add selectable demo login accounts
```
