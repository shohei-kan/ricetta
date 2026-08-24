# 公開デモ Cross-browser Smoke Test

## この文書の状態

- 対象: GitHub Issue [#58 Perform cross-browser smoke test for public demo](https://github.com/shohei-kan/ricetta/issues/58)
- 現在の段階: **必須5browser実施済み、#82・#83の本番反映後回帰と最終集計待ち**
- Chrome desktop判定: **Pass with issues**
- iPhone Safari判定: **Pass**
- Safari desktop判定: **Fail（既知Majorの#86あり）**
- Firefox desktop判定: **Fail（既知Majorの#86あり）**
- Edge desktop判定: **Pass**
- 全browser総合判定: **Not run（#82・#83の本番反映後回帰と最終集計待ち）**
- #82と#83はmainへmerge済みだが、Edge実施時点の本番frontendには未反映であり、修正後の表示を確認済みとは扱わない。

この文書はRicetta公開デモの手動cross-browser smoke testについて、計画、実施環境、結果、発見事項を一か所で管理する正本である。ピクセル単位の完全一致ではなく、重大な表示崩れ、操作不能、認証・Session・CSRF異常がないことを確認する。

自動frontend smoke test / E2E testはIssue [#47 Add frontend smoke tests](https://github.com/shohei-kan/ricetta/issues/47)の責務であり、このIssueではtoolやdependencyを追加しない。公開デモの構成とアカウント利用方法は[Public demo guide](../deploy/demo/demo.md)、画面仕様は[Screen specifications](../product/screens.md)を参照し、この文書へcredentialを複製しない。

## Statusの定義

| Status | 意味 |
| --- | --- |
| Not run | 未実施。結果を判断できない |
| Pass | 計画した必須項目を実施し、問題なし |
| Pass with issues | 公開可能だが、追跡する軽微な問題あり |
| Blocked | 環境、端末、権限などにより完了できない |
| Fail | 完了条件を満たさない問題あり |
| N/A | 実機やデータ状態に該当しない。理由を記録する |

`Not run` と `Blocked` を `Pass` に数えない。件数欄の `—` はゼロではなく、未集計を表す。

## 完了条件

- 必須5ブラウザがすべて実施済みである。
- Chrome / Safari / Firefox / Edge desktopで主要画面に重大なレイアウト崩れがない。
- iPhone Safariで主要導線、responsive、safe area、scroll、tap操作が利用できる。
- owner / staffでlogin、主要画面、logoutを確認済みである。
- 主要navigation、代表form、Session / CSRFを伴う代表更新が利用できる。
- Blockerが0件、未対応Majorが0件である。
- iPhone Safariが `Pass` または公開可能と判断した `Pass with issues` である。
- 発見事項を重大度判定し、必要なものをIssue #58とは別のIssue候補として記録済みである。
- 公開を妨げるブラウザ固有問題が残っていない。

## 実施環境記録template

実施時に値を記入する。Account ID、Instance ID、IP address、session cookie、CSRF token、credential、個人情報は記録しない。

| 項目 | 記録 |
| --- | --- |
| 実施日 |  |
| Tester |  |
| Public demo URL |  |
| Deployed commit |  |
| OS / device |  |
| Browser / version |  |
| Viewport / 画面サイズ |  |
| Orientation |  |
| Test開始時のdemo状態 |  |
| 備考 |  |

## Browser matrix

| 優先 | Browser | OS / device | Version | Status | Blocker | Major | Minor | Cosmetic | Evidence / Issue | Tester | Tested at |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| 1 | Chrome desktop | macOS 15.5 / MacBook Air | Google Chrome 151.0.7922.138 | Pass with issues | 0 | 1 | 3 | 1 | [#82](https://github.com/shohei-kan/ricetta/issues/82), [#83](https://github.com/shohei-kan/ricetta/issues/83), [#84](https://github.com/shohei-kan/ricetta/issues/84), [#85](https://github.com/shohei-kan/ricetta/issues/85), [#86](https://github.com/shohei-kan/ricetta/issues/86) |  | 2026-08-19〜2026-08-20 |
| 2 | iPhone Safari | iOS 26.6 / iPhone 12 mini | Safari | Pass | 0 | 0 | 0 | 0 | 新規findingなし |  | 2026-08-20 |
| 3 | Safari desktop | macOS 15.5（24F74） | Safari 18.5 | Fail | 0 | 1 | 1 | 0 | [#85](https://github.com/shohei-kan/ricetta/issues/85), [#86](https://github.com/shohei-kan/ricetta/issues/86) |  | 2026-08-20 15:22:24 JST〜2026-08-21 |
| 4 | Firefox desktop | macOS 15.5（24F74） | Mozilla Firefox 154.0 | Fail | 0 | 1 | 1 | 0 | [#85](https://github.com/shohei-kan/ricetta/issues/85), [#86](https://github.com/shohei-kan/ricetta/issues/86) |  | Started: 2026-08-21 15:00:55 JST |
| 5 | Edge desktop | Windows 10 Pro 2009（Build 19045）/ 64-bit | Microsoft Edge 149.0.4022.80 | Pass | 0 | 0 | 0 | 0 | 新規findingなし。[#85](https://github.com/shohei-kan/ricetta/issues/85)修正確認 |  | Started: 2026-08-24 12:42:02 JST |

EdgeをmacOSで確認した場合は `macOS / Edge` と明記し、Windows Edge確認済みとは扱わない。iPhone Safariは機種とiOS versionを記録する。

## 現実的なcoverage

`広範` は全共通項目とbrowser専用項目、`主要` はlogin / logout、主要画面、navigation、代表form、Session / CSRF、`権限詳細` はownerとの差分を含む確認を表す。これは実施予定の範囲であり、結果ではない。

| Browser | Owner | Staff | 固有の重点 | Status |
| --- | --- | --- | --- | --- |
| Chrome desktop | 広範 | 主要 + 権限詳細 | 基準動作、responsive DevTools | Pass with issues |
| iPhone Safari | 広範 | 主要 + 権限詳細 | portrait / landscape、safe area、bottom nav、tap / keyboard | Pass |
| Safari desktop | 主要 | login / 主要画面 / logout | fixed / sticky、native form、Session、back-forward cache | Fail（[#86](https://github.com/shohei-kan/ricetta/issues/86)） |
| Firefox desktop | 主要 | login / 主要画面 / logout | form、scrollbar、flex / grid、focus | Fail（[#86](https://github.com/shohei-kan/ricetta/issues/86)） |
| Edge desktop | 主要 | login / 主要画面 / logout | Windows 10でのlayout、form、Session、Chromeとの差 | Pass |

staffの詳細な権限差はChrome desktopとiPhone Safariで確認する。他のdesktop browserでもstaffでlogin、Dashboard、Recipe List / Detail、Prep Today、Account / Settings、logoutを確認し、owner sessionと混同しない。

## Chrome desktop実施結果

### Environment

| 項目 | 記録 |
| --- | --- |
| Test date | 2026-08-19〜2026-08-20 |
| Target | public demo |
| OS | macOS 15.5 |
| Device | MacBook Air |
| Browser | Google Chrome 151.0.7922.138 |
| Status | Pass with issues |

Tester、deployed commit、viewportは記録されていないため、推測で補完しない。

### External preflight

| 確認 | 実測結果 | 判定 |
| --- | --- | --- |
| Frontend | HTTP 200 | Pass |
| HTTPS health | HTTP 200 | Pass |
| `/admin/` | HTTP 404 | Pass。意図した正常動作 |
| HTTPからHTTPSへのredirect | HTTP 308 | Pass |
| Page title / favicon | 表示を確認 | Pass |
| Layout / horizontal scroll / basic operation | 重大なlayout崩れ、意図しない横scroll、操作不能なし | Pass |

### Owner

- 正しい認証情報でloginに成功した。
- Dashboard、Home、Prep Today、Recipe List、Recipe Detail、Recipe Detail内の原価情報、Ingredient List、Settings、Accountを表示できた。
- Navigation、browser back、reload、`/dashboard` のdirect accessを確認した。
- Accountの表示名を一時変更し、更新requestがHTTP PATCH 200となることを確認した。
- 更新requestに `X-CSRFToken` headerが存在することを確認した。header値は記録していない。
- Reload後も一時変更が反映され、確認後に元の表示名へ復元した。
- Logoutに成功した。logout後の `/dashboard` direct accessはLoginへredirectし、browser back後のreloadでもLoginへ戻った。
- Logout後に観測したHTTP 401は、未認証状態に対する想定内のresponseである。

### Staff

- Loginに成功し、staff role表示を確認した。
- Dashboard、Recipe、Ingredient、Settings、Accountを表示できた。
- Owner専用の追加・編集・削除controlが表示されず、Settingsがread-onlyであることを確認した。
- 許可されたPrep status更新に成功し、確認後に元の状態へ復元した。
- Logoutに成功した。
- 新しい重大なConsole errorは確認されなかった。

### Findings

| Issue | Finding | Severity | Chromeへの影響 |
| --- | --- | --- | --- |
| [#82 Show authentication error for rejected login](https://github.com/shohei-kan/ricetta/issues/82) | Login APIがHTTP 400を返した際、UIが認証失敗ではなく通信失敗として表示する | Minor | 正しい認証情報ではlogin可能 |
| [#83 Replace technical wording on Settings with user-facing copy](https://github.com/shohei-kan/ricetta/issues/83) | SettingsにMVP、Recipe Form、Shop、Unit等の技術的表現が残る | Cosmetic | 操作不能なし |
| [#84 Add identifiers and label associations to form controls](https://github.com/shohei-kan/ricetta/issues/84) | Chrome DevToolsがapp-owned form fieldのid / name不足を警告する | Minor | 現時点でform操作不能なし |
| [#85 Fix recipe and ingredient detail/edit back-button loop](https://github.com/shohei-kan/ricetta/issues/85) | Recipe / IngredientのDetailとEditでアプリ内戻るボタンがループする | Minor | Browser backまたはsidebar navigationで回避可能 |
| [#86 Add owner deletion flow for recipes and ingredients](https://github.com/shohei-kan/ricetta/issues/86) | Owner向けRecipe / Ingredient削除UIが存在しない | Major | UI上の回避策なし。公開可否は[#30](https://github.com/shohei-kan/ricetta/issues/30)で判断する |

Chrome desktop集計はBlocker 0、Major 1、Minor 3、Cosmetic 1。Browser判定は指定どおり **Pass with issues** を維持する。[#86](https://github.com/shohei-kan/ricetta/issues/86)はbrowser-independentな既知Majorとして追跡し、公開可否は[#30](https://github.com/shohei-kan/ricetta/issues/30)で判断する。

## iPhone Safari実施結果

### Environment

| 項目 | 記録 |
| --- | --- |
| Test date | 2026-08-20 |
| Target | public demo |
| Device | iPhone 12 mini |
| OS | iOS 26.6 |
| Browser | Safari |
| Safari mode | 通常 |
| Page zoom | 100% |
| 文字サイズ | 標準 |
| Status | Pass |

Testerとdeployed commitは記録されていないため、推測で補完しない。

### Basic display and operation

- Login layout、owner login、Dashboard表示に問題はなかった。
- Input tap時の予期しないzoomはなく、keyboard表示中も入力とscrollを行えた。
- Bottom navigation、safe area、home indicatorとの間隔を確認した。
- Safari address barの縮小・再表示時もlayoutを維持した。
- Landscape表示とportraitへ戻した後の表示に問題はなかった。
- Reload後もSessionを維持した。

### Owner

- Prep Today、Recipe List、Recipe Detail、Recipe Detail内の原価情報、Ingredient、Settings、Accountを利用できた。
- Detail画面では設計どおりbottom navigationが表示されなかった。
- Recipe form、iPhone native select UI、長いformのscrollを利用できた。
- 意図しない横scroll、contentの重なり、操作不能箇所は確認されなかった。

### Session / CSRF functional check

- Accountの表示名を一時変更して保存し、reload後も変更内容を維持した。
- Safariを終了して再度開いた後もSessionを維持した。
- 元の表示名へ復元し、復元後のreloadでも元の値を維持した。
- Logout後の `/dashboard` direct accessはLoginへ遷移した。
- Browser back後も認証済み画面を操作できず、reload後はLoginを表示した。
- Chrome desktopでは `X-CSRFToken` headerの存在を確認済みである。iPhone Safariではtoken値や通信headerを記録せず、更新成功、reload、復元によって機能面を確認した。

### Staff

- Loginとstaff role表示に成功した。
- RecipeとIngredientを閲覧でき、追加・編集・削除controlが表示されなかった。
- Settingsを閲覧でき、category / unitの編集controlが表示されなかった。
- Accountで店舗情報の編集が制限されていた。
- Prep statusを一時変更し、reload後の反映を確認してから元のstatusへ復元した。復元後のreloadでも元のstatusを維持した。
- Login中のunknown routeはDashboard、logout後のunknown routeはLoginへ遷移した。
- Logoutに成功し、staff表示時のlayoutとsafe areaにも問題はなかった。

### Findings

iPhone Safariで新しい問題は確認されなかった。Blocker 0、Major 0、Minor 0、Cosmetic 0。確認した範囲にpublic release blockerはなく、判定は **Pass** である。

[#85](https://github.com/shohei-kan/ricetta/issues/85)と[#86](https://github.com/shohei-kan/ricetta/issues/86)はiPhone Safariで再確認していないため、iPhone Safariの結果へ加算しない。

## Safari desktop実施結果

### Environment

| 項目 | 記録 |
| --- | --- |
| Started at | 2026-08-20 15:22:24 JST |
| Completed at | 2026-08-21 |
| Target | public demo |
| OS | macOS 15.5 |
| OS build | 24F74 |
| Browser | Safari 18.5 |
| Window | 通常window |
| Page zoom | 100% |
| Status | Fail |

Testerとdeployed commitは確認されていないため、推測で補完しない。

### External preflight

| 確認 | 実測結果 | 判定 |
| --- | --- | --- |
| Frontend | HTTP 200 | Pass |
| HTTPS health | HTTP 200 | Pass |
| `/admin/` | HTTP 404 | Pass。意図した正常動作 |
| HTTPからHTTPSへのredirect | HTTP 308 | Pass |
| Page title / favicon | 表示を確認 | Pass |

### Owner

- Login layout、owner login、Dashboardへの遷移と表示を確認した。
- Reload後もSessionを維持し、JavaScript Consoleに予期しないerrorはなかった。
- Navigation、Prep Today、Recipe List / Detail、Recipe Detail内の原価情報、Ingredient List / Detail、Settings、Accountを利用できた。
- Recipe form、Ingredient form、Safari native selectを利用できた。
- 狭いwindow幅、scroll、contentの重なりに問題はなかった。
- Browser back / forwardは正常だった。ただしアプリ内戻るボタンには[#85](https://github.com/shohei-kan/ricetta/issues/85)のループがある。
- Accountの表示名を一時変更し、更新requestがHTTP PATCH 200となることを確認した。
- 更新requestに `X-CSRFToken` headerが存在することを確認した。header値は記録していない。
- Reload後も一時変更を維持し、確認後に元の表示名へ復元した。復元後のreloadでも元の値を維持した。
- Logout後の `/dashboard` direct accessはLoginへ遷移した。Browser back後も認証済み画面を操作できず、reload後はLoginを表示した。

### Staff

- Loginとstaff role表示に成功した。
- Recipe、Ingredient、Settingsを閲覧でき、owner限定の追加・編集controlが表示されなかった。
- Accountで店舗情報の編集が制限され、権限制限によるlayout崩れはなかった。
- Prep statusを一時変更し、reload後の反映を確認してから元のstatusへ復元した。復元後のreloadでも元のstatusを維持した。
- Login中のunknown routeはDashboard、logout後のunknown routeはLoginへ遷移した。
- Logoutに成功し、Consoleに予期しないerrorはなかった。

### Findings

| Issue | Finding | Severity | 影響 / 回避策 |
| --- | --- | --- | --- |
| [#85 Fix recipe and ingredient detail/edit back-button loop](https://github.com/shohei-kan/ricetta/issues/85) | Recipe / IngredientのDetailとEditでアプリ内戻るボタンがループする。Safari 18.5とChrome 151で再現 | Minor | Browser backまたはsidebar navigationで回避可能 |
| [#86 Add owner deletion flow for recipes and ingredients](https://github.com/shohei-kan/ricetta/issues/86) | Owner向けRecipe / Ingredient削除UIが存在しない。DEMO_MODEによる意図的な非表示ではなく、frontend未実装 | Major | UI上の回避策なし。公開可否は[#30](https://github.com/shohei-kan/ricetta/issues/30)で判断する |

Safari desktop集計はBlocker 0、Major 1、Minor 1、Cosmetic 0。主要画面、Session、form、browser navigation自体は利用できたが、既知Majorの[#86](https://github.com/shohei-kan/ricetta/issues/86)があるため、既存の重大度規則に従って判定は **Fail** とする。公開可否は[#30](https://github.com/shohei-kan/ricetta/issues/30)で判断する。

## Firefox desktop実施結果

### Environment

| 項目 | 記録 |
| --- | --- |
| Started at | 2026-08-21 15:00:55 JST |
| Target | public demo |
| OS | macOS 15.5 |
| OS build | 24F74 |
| Browser | Mozilla Firefox 154.0 |
| Window | 通常ウィンドウ |
| Page zoom | 100% |
| Status | Fail |

Tester、deployed commit、完了日時は確認されていないため、推測で補完しない。

### External preflight

| 確認 | 実測結果 | 判定 |
| --- | --- | --- |
| Login / frontend | 表示を確認 | Pass |
| Page title / favicon | 表示を確認 | Pass |
| HTTPS health | 応答を確認 | Pass |
| `/admin/` | HTTP 404 | Pass。意図した正常動作 |
| HTTPからHTTPSへのredirect | Redirectを確認 | Pass |
| 未login時の `/api/v1/auth/me/` | HTTP 401 | Pass。意図した未認証応答 |

### Owner

- Owner login、Dashboardへの遷移と表示、reload後のSession維持を確認した。
- Navigation、Prep Today、Recipe、Recipe Detail内の原価情報、Ingredient、Settings、Accountを利用できた。
- Form、Firefox native select、scrollbar、flex / grid、狭いwindow幅での表示に問題はなかった。
- Tab / Shift+Tabによるkeyboard focusとBrowser back / forwardは正常だった。ただしアプリ内戻るボタンには[#85](https://github.com/shohei-kan/ricetta/issues/85)のループがある。
- Accountの表示名を一時変更し、更新requestがHTTP PATCH 200となることを確認した。
- 更新requestに `X-CSRFToken` headerが存在することを確認した。header値は記録していない。
- Reload後も一時変更を維持し、確認後に元の表示名へ復元した。復元後のreloadでも元の値を維持した。
- Logout後の `/dashboard` direct accessはLoginへ遷移した。Browser back後も認証済み画面を操作できず、reload後はLoginを表示した。

### Staff

- Loginとstaff role表示に成功した。
- Recipe、Ingredient、Settings、Accountを閲覧でき、owner限定操作が表示されないview-only制御を確認した。
- Prep statusを一時変更し、reload後の反映を確認してから元のstatusへ復元した。復元後のreloadでも元のstatusを維持した。
- Login中のunknown routeはDashboard、logout後のunknown routeはLoginへ遷移した。
- Logoutに成功し、Consoleに予期しないerrorはなかった。

### Findings

| Issue | Finding | Severity | 影響 / 回避策 |
| --- | --- | --- | --- |
| [#85 Fix recipe and ingredient detail/edit back-button loop](https://github.com/shohei-kan/ricetta/issues/85) | Recipe / IngredientのDetailとEditでアプリ内戻るボタンがループする。Firefox 154.0でも再現 | Minor | Browser backまたはsidebar navigationで回避可能 |
| [#86 Add owner deletion flow for recipes and ingredients](https://github.com/shohei-kan/ricetta/issues/86) | Owner向けRecipe / Ingredient削除buttonが存在しない。Firefox 154.0でも再現 | Major | UI上の回避策なし。公開可否は[#30](https://github.com/shohei-kan/ricetta/issues/30)で判断する |

Firefox固有の新規findingは確認されなかった。Firefox desktop集計はBlocker 0、Major 1、Minor 1、Cosmetic 0。Firefox互換性に起因するFailではなく、既知Majorの[#86](https://github.com/shohei-kan/ricetta/issues/86)が再現したため、既存の重大度規則に従って判定は **Fail** とする。公開可否は[#30](https://github.com/shohei-kan/ricetta/issues/30)で判断する。

## Edge desktop実施結果

### Environment

| 項目 | 記録 |
| --- | --- |
| Started at | 2026-08-24 12:42:02 JST |
| Target | public demo |
| OS | Windows 10 Pro |
| Windows version | 2009 |
| OS build | 19045 |
| Architecture | 64-bit |
| Browser | Microsoft Edge 149.0.4022.80 |
| Window | 通常window |
| Display resolution | 1366 × 768 |
| Windows scaling | 100% |
| Page zoom | 100% |
| Status | Pass |

Tester、deployed commit、完了日時は確認されていないため、推測で補完しない。

### External preflight

| 確認 | 実測結果 | 判定 |
| --- | --- | --- |
| Frontend | HTTP 200 / `text/html; charset=utf-8` | Pass |
| HTTPS health | HTTP 200 / `application/json` | Pass |
| `/admin/` | HTTP 404 | Pass。意図した正常動作 |
| HTTPからHTTPSへのredirect | HTTP 308 | Pass |
| Page title / favicon | 表示を確認 | Pass |
| Demo banner | 表示を確認 | Pass |

### Owner

- Login layoutに問題はなく、未login状態の `/dashboard` direct accessはLoginへ遷移した。
- Owner login後にDashboardへ遷移し、reload後もSessionを維持した。
- Dashboard、Prep Today、Recipe、Ingredient、Settings、Accountを利用できた。
- 1366 × 768、Windows scaling 100%、page zoom 100%で、desktop layout、文字切れ、主要navigationに問題はなかった。
- Recipe List → Detail → Edit → アプリ内戻る → Detail → アプリ内戻る → Listの遷移を確認した。Ingredientでも同じ画面階層の遷移を確認した。
- [#85](https://github.com/shohei-kan/ricetta/issues/85)のDetail / Edit loopはEdgeで再現せず、browser Back / Forwardも正常だった。
- Accountの表示名を一時変更し、更新requestがHTTP PATCH 200となることを確認した。
- 更新requestに `X-CSRFToken` headerが存在することを確認した。header値、token、cookieの実値は記録していない。
- Reload後も一時変更を維持し、確認後に元の表示名へ復元した。
- Logout後の `/dashboard` direct accessはLoginへ遷移し、browser Backとreloadでも認証済み画面へ戻らなかった。
- 予期しないConsole errorは確認されなかった。Logout等に伴うHTTP 401は想定内の未認証responseとしてfindingに含めない。

### Staff

- Loginとlogoutに成功し、owner sessionと混同しなかった。
- Dashboard、Prep Today、Recipe、Ingredient、Settings、Accountと主要navigationを利用できた。
- Owner限定の編集操作とSettingsの管理formが表示されないことを確認した。
- Login中のunknown routeはDashboardへ遷移した。
- Edge固有のlayout崩れ、操作不能、予期しないConsole errorは確認されなかった。

### Findings and pending verification

Edge固有の新規findingは確認されなかった。Edge desktop集計はBlocker 0、Major 0、Minor 0、Cosmetic 0で、確認したEdge互換性の判定は **Pass** である。

- [#85](https://github.com/shohei-kan/ricetta/issues/85)は本番反映済みで、Chrome、Safari、Edgeでは修正後の戻る導線を確認済みである。Firefoxでの修正後確認は記録されていない。
- [#82](https://github.com/shohei-kan/ricetta/issues/82)と[#83](https://github.com/shohei-kan/ricetta/issues/83)はmainへmerge済みだが、Edge実施時点の本番frontendには未反映である。新しいlogin error文言とSettings文言はEdgeで最終確認済みとしない。
- [#84](https://github.com/shohei-kan/ricetta/issues/84)と[#86](https://github.com/shohei-kan/ricetta/issues/86)はopenのKnown Issueである。[#86](https://github.com/shohei-kan/ricetta/issues/86)はbrowser-independentであり、公開可否は[#30](https://github.com/shohei-kan/ricetta/issues/30)で判断する。

## 実施前の共通確認

安全のため、demo resetやserver操作はこのtest planから実行しない。

| ID | 確認と目的 | 期待結果 | Status / 記録 |
| --- | --- | --- | --- |
| PRE-01 | 実施URLとdeployed commitを管理者に確認し、別revisionを試さない | 対象が記録欄と一致する | Not run |
| PRE-02 | Browserでpublic demo URLを開き、HTTPSを確認する | 証明書警告なく表示される | Chrome・Safari・Firefox・Edge: Pass / iPhone: Not run |
| PRE-03 | 同じoriginの `/api/v1/health/` をBrowserで開き、公開APIの到達性を確認する | `status` が `ok` のJSONを返す | Chrome・Safari・Edge: HTTP 200確認（bodyの個別記録なし）、Firefox: Pass（status codeの個別記録なし）/ iPhone: Not run |
| PRE-04 | 同じoriginの `/admin/` を開き、公開しない管理画面の境界を確認する | 意図どおり404 | Chrome・Safari・Firefox・Edge: Pass / iPhone: Not run |
| PRE-05 | Demo resetの最終状態と実行予定を管理者に確認する | テスト中に予期せぬresetがない時間帯を選べる | Not run |
| PRE-06 | 通常window、標準zoom、動作へ影響するextensionなしで開始する | cache / extension由来の誤判定を避けられる | Not run |
| PRE-07 | roleを切り替える前にUIからlogoutする | owner / staffのsessionが混在しない | Chrome・iPhone・Safari・Firefox・Edge: Pass |
| PRE-08 | screenshotやDevToolsを使う前に表示内容を確認する | cookie、token、password、個人情報が写らない | Not run |

logoutできずroleを切り替えられない場合は `Blocked` として記録する。必要ならBrowser設定から対象siteだけのdataを消去するが、cookieの値を表示・転記しない。別roleのtabを残さない。

## Sourceに一致する画面とroute

| 画面 / UI | Route | 主な確認 |
| --- | --- | --- |
| Login | `/login` | account選択、login、generic error |
| Dashboard / ホーム | `/dashboard` | role、カード、loading / empty表示 |
| Prep Today / 仕込み | `/prep` | task、メモ、`仕込みを追加` dialog |
| Recipe List / レシピ一覧 | `/recipes` | 検索、empty state、detail遷移 |
| Recipe Detail | `/recipes/:id` | `概要` / `材料` / `作り方`、swipe、編集導線 |
| Cost Summary / 原価情報 | 独立routeなし | Recipe Detail内の `原価情報` を確認 |
| Recipe Form | `/recipes/new`, `/recipes/:id/edit` | ownerのみ。staffは権限案内 |
| Ingredient List / 材料一覧 | `/ingredients` | 検索、responsive list、detail遷移 |
| Ingredient Detail | `/ingredients/:id` | 原価計算情報、ownerの編集導線 |
| Ingredient Form | `/ingredients/new`, `/ingredients/:id/edit` | ownerのみ。staffは権限案内 |
| Settings / 設定 | `/settings` | category / unit。staffは閲覧のみ |
| Account / アカウント | `/account` | 店舗情報、表示名、role、logout |

desktop sidebarとmobile bottom navigationのラベルは `ホーム`、`仕込み`、`レシピ`、`材料`、`設定`。`アカウント` はdesktop sidebar下部またはmobile headerから開く。mobile bottom navigationは上位routeでのみ表示され、detail / form routeでは表示されない設計である。

専用404画面はない。存在しないrouteでは、login中なら `/dashboard`、未loginなら `/login` へredirectされることを確認する。

## 共通Smoke Test checklist

### Public表示と認証

| ID | 操作 / 確認 | 期待結果 | 適用 | Status |
| --- | --- | --- | --- | --- |
| COM-01 | HTTPSでLoginを開く | certificate warningやmixed-content起因の操作不能がない | 全browser | Chrome・Safari・Firefox・Edge: Pass / iPhone: Not run |
| COM-02 | Tabのfaviconとpage titleを見る | Ricettaのfaviconとtitleが表示される | 全browser | Chrome・Safari・Firefox・Edge: Pass / iPhone: Not run |
| COM-03 | 既存正本のowner accountを選びloginする | Dashboardへ移動し、オーナー表示になる | 全browser | Chrome・iPhone・Safari・Firefox・Edge: Pass |
| COM-04 | 意図的なinvalid loginを1回だけ試す | accountの存在を推測させないgeneric errorが表示される | Chromeのみ | Fail（Minor、[#82](https://github.com/shohei-kan/ricetta/issues/82)） |
| COM-05 | protected route間を移動する | login sessionが維持され、再loginを要求されない | 全browser | Chrome・iPhone・Safari・Firefox・Edge: Pass |
| COM-06 | Accountからlogoutし、Browser backとprotected route直打ちを試す | 保護画面へ戻れずLoginへredirectされる | 全browser / 両role | Chrome owner・iPhone・Safari・Firefox・Edge owner: Pass、Chrome・Edge staff logout: Pass |
| COM-07 | logout後にstaffでloginする | スタッフ表示となりowner sessionが残らない | 全browser | Chrome・iPhone・Safari・Firefox・Edge: Pass |

invalid loginを短時間に繰り返さない。login throttleをテストするIssueではない。

### 主要画面とnavigation

| ID | 操作 / 確認 | 期待結果 | Status |
| --- | --- | --- | --- |
| COM-10 | ホームから5つの主要navigationを順に開く | 選択状態と画面が一致し、操作不能や重大な崩れがない | Chrome・iPhone・Safari・Firefox・Edge: Pass |
| COM-11 | Recipe Listで既存recipeを検索し、detailを開く | loading、検索結果、detail遷移が正常 | iPhone・Safari・Firefox・Edge: list / detail表示はPass。検索・loadingの個別記録なし / Chrome: Not run |
| COM-12 | Recipe Detailの `概要` / `材料` / `作り方` を切り替える | 内容が切り替わり、縦scrollを妨げない | iPhone: Pass。Safari・Firefox: detail表示Pass、tab切替の個別記録なし / Chrome・Edge: Not run |
| COM-13 | Recipe Detailの `原価情報` を見る | prep recipeでは材料原価、販売recipeでは販売価格・原価率・粗利等が読める | Chrome・iPhone・Safari・Firefox: Pass / Edge: Not run |
| COM-14 | Ingredient Listを開き検索、detailへ進む | desktop / mobile表示と遷移が利用可能 | Safari・Firefox・Edge: list / detail表示はPass。検索の個別記録なし / Chrome・iPhone: Not run |
| COM-15 | Prep Todayを開きtask、status、board memo領域を見る | contentが重ならず、buttonが操作可能 | Chrome・iPhone・Safari・Firefox: 画面表示・staff status更新と復元はPass。Edge: 画面表示Pass。board memoの個別記録なし |
| COM-16 | AccountとSettingsを開く | roleに合う情報と操作だけが表示される | Chrome・iPhone・Safari・Firefox・Edge: Pass |
| COM-17 | Browser back / forwardを主要画面間で使う | routeと表示、navigation選択状態が一致する | Safari・Firefox・Edge: browser back / forwardはPass。Edgeのアプリ内戻るは[#85](https://github.com/shohei-kan/ricetta/issues/85)修正確認済み、Safari・Firefoxの表中結果は修正前。Chrome: back Pass、forward個別記録なし / iPhone: Not run |
| COM-18 | Dashboard、Recipe Detail、Accountでreloadする | login sessionが維持され、同じ画面を再表示できる | Chrome: reload Pass、route内訳なし。iPhone: Account / Prep更新後、Safari・Firefox: Session / Account / Prep更新後のreload Pass。Edge: Dashboard / Account更新後Pass、Recipe Detail reloadの個別記録なし |
| COM-19 | 現在のRecipe Detail URLを新しいtabで直接開く | login済みならdetailを表示。ID実値は結果文書へ転記しない | Not run |
| COM-20 | 存在しないtest用pathを開く | login中はDashboard、logout中はLoginへredirectする | iPhone・Safari・Firefox: Pass。Edge: login中はPass、logout中は個別記録なし / Chrome: Not run |

### UI state、form、focus

| ID | 操作 / 確認 | 期待結果 | Status |
| --- | --- | --- | --- |
| COM-30 | reloadや画面遷移直後のloading表示を観察する | layoutを壊さず、終了後にcontentへ切り替わる | Not run |
| COM-31 | Recipe / Ingredient検索に一致しない文字列を使う | `見つかりません` のempty stateが表示され、dataは変更されない | Not run |
| COM-32 | 通常操作中に自然にerrorが出た場合だけ表示を確認する | 内容が読み取れ、secretや内部traceを表示しない | Not run |
| COM-33 | button、link相当button、input、selectをkeyboardで移動する | focus位置が判別でき、Enter / Space等で基本操作できる | Firefox: Pass（Tab / Shift+Tab）/ 他browser: Not run |
| COM-34 | Prep Todayで `仕込みを追加` dialogを開き、保存せず閉じる | dialogがviewport内でscrollでき、閉じる操作でdataが変わらない | iPhone: Pass / 他browser: Not run |
| COM-35 | ownerのRecipe Formを開き、input / select / buttonを操作して保存せず戻る | form controlが利用でき、不要なdata変更がない | iPhone・Safari・Firefox: Pass / Chrome・Edge: Not run |
| COM-36 | 既存の長い表示内容を探し、narrow幅で確認する | textが主要操作を押し出さず、意図しない横scrollがない | iPhone・Safari・Firefox: Pass / Chrome・Edge: Not run |
| COM-37 | desktop sidebarとmobile bottom navを伴う長い画面をscrollする | fixed / sticky UIがcontentや操作を隠さない | iPhone・Safari: Pass / Chrome・Firefox・Edge: Not run |
| COM-38 | viewportをdesktopからmobile相当へ変える | navigationとlayoutが適切に切り替わる | Chrome desktopのみ / Not run |

error stateはnetwork遮断、API改変、production data操作で人工的に作らない。自然に再現できなければ `N/A（安全に再現できず）` とする。empty stateは検索結果0件で安全に確認できる。manifestは現在のsourceにないためテスト対象外である。

## Owner / staff権限checklist

### Owner

| ID | 確認 | 期待結果 | Status |
| --- | --- | --- | --- |
| ROLE-O1 | Recipe / Ingredientの一覧とdetail | 追加・編集導線が見える | Safari: 追加・編集はPass / 他browser: Not run |
| ROLE-O2 | Settings | category / unitの追加・編集UIが見える | Not run |
| ROLE-O3 | Account | 店舗情報の編集導線が見える | Not run |
| ROLE-O4 | Prep Today | taskとboard memoの操作UIが見える | Not run |
| ROLE-O5 | 自分の表示名 | `表示名を保存` が利用できる | Chrome・iPhone・Safari・Firefox・Edge: Pass |
| ROLE-O6 | Recipe / Ingredientの削除 | Owner向けの安全な削除導線が利用できる | Chrome・Safari・Firefox: Fail（[#86](https://github.com/shohei-kan/ricetta/issues/86)）/ iPhone: 再確認なし / Edge: Not run |

削除、recipe保存、ingredient保存、店舗情報更新は権限表示確認だけに留める。Issue #58のSession / CSRF代表操作には、後述の表示名更新だけを使う。

### Staff

| ID | 確認 | 期待結果 | 適用 | Status |
| --- | --- | --- | --- | --- |
| ROLE-S1 | Dashboard、Recipe / Ingredient、Prep Today | 閲覧でき、Prepの通常操作UIを利用できる | 全browser | Chrome・iPhone・Safari・Firefox・Edge: Pass |
| ROLE-S2 | Recipe / Ingredient一覧とdetail | 追加・編集導線が表示されない | Chrome / iPhone詳細、他は主要確認 | Chrome・iPhone・Safari・Firefox・Edge: Pass |
| ROLE-S3 | `/recipes/new` を直接開く | APIを無理に呼ばず、owner限定の権限案内が表示される | Chrome / iPhone | Not run |
| ROLE-S4 | `/ingredients/new` を直接開く | APIを無理に呼ばず、owner限定の権限案内が表示される | Chrome / iPhone | Not run |
| ROLE-S5 | Settings | 現在値は見えるがcategory / unitの管理formと編集buttonは表示されない | Chrome / iPhone詳細、他は主要確認 | Chrome・iPhone・Safari・Firefox・Edge: Pass |
| ROLE-S6 | Account | 店舗情報の編集buttonがなくowner限定案内が表示される | 全browser | Chrome・iPhone・Safari・Firefox・Edge: Pass |
| ROLE-S7 | 自分の表示名 | staff自身の表示名だけ更新できる | Chrome / iPhone | Not run |

BrowserのDevToolsから権限外APIを直接送信しない。raw APIの403保証はbackend testの責務である。UIが権限外操作を非表示または権限案内で安全に扱うことを確認し、403を無理に発生させない。

## Session / CSRFの安全な代表確認

Accountの「自分の表示名」はowner / staffとも自分だけを更新でき、元へ戻せるため代表操作に使う。店舗情報、recipe、ingredient、prep task、demo resetは使わない。

各対象browserで、次を1回ずつ行う。Chrome desktopとiPhone Safariではowner / staff、他のdesktop browserではownerで行う。

1. Accountを開き、現在の表示名を画面上で確認する。実値を文書やscreenshotへ記録しない。Status: **Chrome・iPhone・Safari・Firefox・Edge owner: Pass / 他scope: Not run**
2. 元に戻せる一時的なQA用suffixを追加し、`表示名を保存` を押す。Status: **Chrome・Safari・Firefox・Edge owner: Pass（HTTP PATCH 200）、iPhone owner: Pass（機能確認）/ 他scope: Not run**
3. errorなしで保存が完了し、reload後も一時値が表示されることを確認する。これが通常のSession / CSRF経路を通る代表更新となる。Status: **Chrome・Safari・Firefox・Edge owner: Pass（`X-CSRFToken` header存在確認、値は未記録）、iPhone owner: Pass（更新・reloadによる機能確認）/ 他scope: Not run**
4. 直ちに元の表示名へ戻して保存し、reload後に復元を確認する。Status: **Chrome・iPhone・Safari・Firefox・Edge owner: Pass / 他scope: Not run**
5. logoutし、Browser backおよびAccount直打ちで保護画面へ戻れないことを確認する。Status: **Chrome・iPhone・Safari・Firefox・Edge owner: Pass / 他scope: Not run**
6. 次のroleへ切り替える前にlogout完了を確認し、別roleのtabを閉じる。Status: **Chrome・iPhone・Safari・Firefox・Edge: Pass**

CSRF tokenやcookie値を表示、copy、記録しない。更新失敗時は繰り返さず、現在の表示と時刻だけを機密情報なしで記録して `Fail` または `Blocked` とする。元の表示名へ戻せない場合はMajor以上として直ちに共有する。

## iPhone Safari専用checklist

| ID | 確認 | 期待結果 | Status |
| --- | --- | --- | --- |
| IOS-01 | portraitでLoginと主要画面を開く | viewportがdevice幅に合い、意図しない横scrollがない | Pass |
| IOS-02 | landscapeへ回転する | content、header、formが欠けず再配置される | Pass |
| IOS-03 | notch / Dynamic Island側とhome indicator側を見る | 操作UIがsafe areaと重ならない。非該当機種はN/A | Pass |
| IOS-04 | bottom navで5画面を移動する | tap可能で選択状態が明確、home indicatorと重ならない | Pass |
| IOS-05 | 長い画面を下方向・上方向へscrollする | bottom navが下scrollで隠れ、上scroll / top / route変更で戻る | Pass |
| IOS-06 | Safari address barの表示 / 縮小を伴ってscrollする | fixed UIとcontentが重ならずjumpしない | Pass |
| IOS-07 | Recipe Detailのtab tapと横swipeを試す | 縦scrollを妨げず、tabが意図どおり切り替わる | Pass |
| IOS-08 | buttonとheader account iconをtapする | tap targetが押しやすく、隣を誤操作しない | Pass |
| IOS-09 | Login、検索、表示名formでkeyboardを開く | inputが隠れず、16px相当のtextで意図しないinput zoomがない | Pass |
| IOS-10 | `仕込みを追加` のselectとdecimal inputを操作する | native controlとkeyboardが使え、保存せず閉じられる | Pass |
| IOS-11 | dialog内をscrollし、背面も意図せず動かないか確認する | dialog操作を妨げるbackground scrollがない | Pass |
| IOS-12 | reloadする | current routeとSessionが維持される | Pass |
| IOS-13 | Safariを閉じて再度開く | 期待するSession継続、または安全なLoginへの遷移となる | Pass |
| IOS-14 | detail / form routeを見る | 設計どおりbottom navがなくても戻る操作が利用できる | Pass |

source上、日付inputは主要formにないためdate pickerは `N/A（該当controlなし）` とする。実機にnotch / Dynamic Islandがない場合も理由を添えてN/Aにする。

## Desktop browser固有checklist

| Browser | 確認 | Status |
| --- | --- | --- |
| Chrome | 基準動作に加え、DevTools responsive表示で767px付近のnavigation切替、scroll、横overflowを確認する | Pass with issues（重大なlayout崩れ・横scrollなし。767px個別結果は未記録） |
| Safari | sticky sidebar、fixed要素、native form control、Session、back / forward後の表示とback-forward cache由来の古い状態を確認する | Fail（基本動作はPass、[#85](https://github.com/shohei-kan/ricetta/issues/85) Minor、[#86](https://github.com/shohei-kan/ricetta/issues/86) Major。#85は修正後確認済み） |
| Firefox | input / select、scrollbar、flex / grid、keyboard focus ring、長いcontentを確認する | Fail（form、native select、scrollbar、flex / grid、narrow window、focusはPass。[#85](https://github.com/shohei-kan/ricetta/issues/85) Minor、[#86](https://github.com/shohei-kan/ricetta/issues/86) Major。#85の修正後確認は未実施） |
| Edge | Chromeと同じChromium系でもlayout、form、Sessionを再確認し、確認したOSをmatrixへ明記する | Pass（Windows 10 Pro / 1366 × 768、主要layout・form・Session・navigationを確認。Edge固有findingなし） |

## Browserごとの実施順

1. Chrome desktop
2. iPhone Safari
3. Safari desktop
4. Firefox desktop
5. Edge desktop

各browserの開始時に、実施環境、deployed commit、preflight、開始時のdemo状態を記録する。ownerから開始し、完了後にUIからlogoutしてstaffへ切り替える。各browserの終了時に、未確認項目、発見事項、重大度、evidence、元へ戻す操作の完了、最終logoutを記録してBrowser matrixを更新する。

### 最初のChrome desktop手順

1. Browser名 / version、OS、画面サイズ、tester、日時、deployed commitを記録する。
2. extensionの影響がない通常window、標準zoomでpublic demoを開く。
3. PRE-02からPRE-08を順に確認する。resetは実行しない。
4. COM-01からCOM-06をownerで行う。invalid loginは1回だけにする。
5. COM-10からCOM-38、ROLE-O1からROLE-O5を行う。保存を伴う確認は表示名だけにする。
6. Session / CSRF代表確認を行い、一時値を必ず元へ戻す。
7. logoutしてstaffへ切り替え、COM-07、主要画面、ROLE-S1からROLE-S7を行う。
8. staffでlogoutし、protected routeへ戻れないことを確認する。
9. 結果、未確認項目、問題件数、evidenceを記録し、Browser matrixを更新する。
10. Blocker / Majorがあれば次browserへ進む前に別Issue候補として共有する。

## 重大度と問題の扱い

| Severity | 基準 | 例 |
| --- | --- | --- |
| Blocker | 公開不能、login不能、主要導線不能、data破損、security問題 | 全roleがlogin不能、credential露出 |
| Major | 特定browserで主要機能が使用困難。容易な回避策がない | navigation不能、代表更新不能、主要contentが隠れる |
| Minor | 回避可能な表示・操作問題。主要導線は完了できる | 一部controlの操作性低下、軽いoverflow |
| Cosmetic | 公開を妨げない軽微な視覚差 | 小さなspacing、色、font rendering差 |

問題を見つけてもIssue #58内で実装を修正しない。再現性と影響を記録し、follow-up Issue候補にする。securityまたはdata破損の疑いはscreenshot採取や再現操作を続けず、secret-freeな事実だけを管理者へ共有する。

## 問題記録template

```markdown
### Finding: <短い題名>

- Browser / OS / device:
- Browser version:
- Route / screen:
- Role:
- Precondition:
- Reproduction steps:
  1.
- Expected:
- Actual:
- Severity: Blocker / Major / Minor / Cosmetic
- Reproducibility:
- Screenshot / evidence:
- Console / network summary:
- Workaround:
- Proposed follow-up Issue:
- Confirmed facts:
- Assumptions:
```

cookie、CSRF token、Authorization header、password、個人情報、private identifierを記録しない。screenshotはaddress bar、Accountの個人情報、DevToolsのrequest header / storageを含まないようcropする。console / network全体を貼らず、必要箇所だけをredactして要約する。

## 結果summary

### Browser結果

Browser matrixを正本とする。Chrome desktopは **Pass with issues**、iPhone Safariは **Pass**、Safari desktopとFirefox desktopは **Fail**、Edge desktopは **Pass** である。必須5browserの実機確認は揃ったが、#82・#83の本番反映後回帰と最終集計が残るため、全browser総合判定は **Not run** を維持する。

### Role結果

| Role | Status | 確認browser | Evidence / Issue |
| --- | --- | --- | --- |
| Owner | Chrome: Pass with issues / iPhone: Pass / Safari: Fail / Firefox: Fail / Edge: Pass | Chrome desktop、iPhone Safari、Safari desktop、Firefox desktop、Edge desktop | [#82](https://github.com/shohei-kan/ricetta/issues/82)〜[#86](https://github.com/shohei-kan/ricetta/issues/86)。Safari / FirefoxのFail理由は既知Majorの[#86](https://github.com/shohei-kan/ricetta/issues/86)。Edge固有findingなし |
| Staff | Chrome: Pass with issues / iPhone: Pass / Safari: Pass / Firefox: Pass / Edge: Pass | Chrome desktop、iPhone Safari、Safari desktop、Firefox desktop、Edge desktop | Chrome findings: [#83](https://github.com/shohei-kan/ricetta/issues/83), [#84](https://github.com/shohei-kan/ricetta/issues/84)。Firefox・Edge固有findingなし |

### Finding集計

| Blocker | Major | Minor | Cosmetic | 作成したIssue |
| ---: | ---: | ---: | --- |
| 0 | 1 | 3 | 1 | [#82](https://github.com/shohei-kan/ricetta/issues/82), [#83](https://github.com/shohei-kan/ricetta/issues/83), [#84](https://github.com/shohei-kan/ricetta/issues/84), [#85](https://github.com/shohei-kan/ricetta/issues/85), [#86](https://github.com/shohei-kan/ricetta/issues/86) |

- [#86](https://github.com/shohei-kan/ricetta/issues/86)はbrowser-independentな既知Majorであり、公開可否は[#30](https://github.com/shohei-kan/ricetta/issues/30)で判断する。
- Chrome判定: **Pass with issues**
- iPhone Safariでpublic releaseを妨げる問題: **なし**
- iPhone Safari判定: **Pass**
- Safari desktop判定: **Fail**
- Firefox desktop判定: **Fail**（Firefox互換性ではなく既存Majorの[#86](https://github.com/shohei-kan/ricetta/issues/86)が理由）
- Edge desktop判定: **Pass**（Edge固有findingなし、[#85](https://github.com/shohei-kan/ricetta/issues/85)修正確認済み）
- [#85](https://github.com/shohei-kan/ricetta/issues/85)修正後確認: **Chrome・Safari・EdgeでPass。Firefoxは未確認**
- [#82](https://github.com/shohei-kan/ricetta/issues/82)・[#83](https://github.com/shohei-kan/ricetta/issues/83): **mainへmerge済み。本番frontend反映後の回帰は未実施**
- Open Known Issue: **[#84](https://github.com/shohei-kan/ricetta/issues/84)、[#86](https://github.com/shohei-kan/ricetta/issues/86)**
- 全browser総合判定: **Not run（#82・#83の本番反映後回帰と最終集計待ち）**
- Issue #58の完了可否: **まだClose不可。#82・#83の本番反映後回帰と最終集計が残る**
- 未実施browser: **なし**
- 次のaction: #82・#83の本番反映後に対象表示を回帰確認し、Findingの最終状態とAcceptance Criteriaを再集計する。

## Acceptance Criteria対応

| Issue #58 Acceptance Criteria | この文書の確認箇所 | 現在 |
| --- | --- | --- |
| Chrome / Safari / Firefox / Edgeで重大なlayout崩れがない | Browser matrix、共通 / desktop checklist | Chrome・Safari・Firefox・Edgeとも重大なlayout崩れなし。Safari・Firefoxのbrowser判定は既知Majorの[#86](https://github.com/shohei-kan/ricetta/issues/86)によりFail |
| iPhone Safariで主要導線を操作できる | iPhone Safari専用checklist | Pass |
| owner / staffでlogin / logoutできる | Public表示と認証、Role結果 | Chrome・iPhone・Safari・Firefox・Edge: Pass |
| 主要navigationが機能する | 主要画面とnavigation | Browser back / forwardは各desktopでPass。[#85](https://github.com/shohei-kan/ricetta/issues/85)のアプリ内戻るはChrome・Safari・Edgeで修正確認済み、Firefoxの修正後確認は未実施 |
| 主要form / 操作がbrowser差で使用不能でない | UI state / form、Session / CSRF | 各browserの代表form / 更新はPass。owner削除操作はbrowser-independentな[#86](https://github.com/shohei-kan/ricetta/issues/86)としてopen |
| Session / CSRFを伴う主要操作が正常 | 表示名の安全な代表確認 | Chrome・iPhone・Safari・Firefox・Edge owner: Pass |
| 公開を妨げるbrowser固有問題がない | 完了条件、重大度、結果summary | Edge固有findingなし。既知Issueの公開可否は[#30](https://github.com/shohei-kan/ricetta/issues/30)で判断し、#82・#83回帰後に最終判定する |
| 発見事項を必要に応じて別Issue化 | 問題記録template、結果summary | Chrome / Safari / Firefox: #82〜#86、iPhone・Edge: 新規findingなし |

## 実施者の最終確認

- [x] 5browserの環境情報と結果を記録した
- [x] owner / staffを混同せず、各browserでlogoutまで確認した
- [x] 一時的な表示名を元へ戻した
- [x] Not run / Blocked / N/AをPassとして数えていない
- [ ] Blocker 0、未対応Major 0を確認した
- [x] evidenceからsecret、credential、個人情報を除いた
- [x] 必要なfollow-up Issueを作成または候補として記録した
- [x] Issue #58のAcceptance Criteriaと結果を照合した
