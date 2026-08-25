# GitHub Public Repository Audit

## Purpose and decision boundary

この文書は、Ricetta repositoryをprivateからpublicへ変更する前の監査結果と、GitHub Consoleで人間が確認する項目の正本です。Issue #92でsource、Git履歴、GitHub Actions、公開metadata、security方針を監査し、最終的な公開可否をIssue #30 Public Release Readiness Reviewへ引き継ぎます。

repository visibilityの変更、Git履歴の書換え、branch / tag / release / remote refの削除、GitHub settingsの変更、credential rotationは本監査では行いません。secretやprivate identifierの実値も本書へ記録しません。

## Audit snapshot

監査時点: 2026-08-25 JST

### Local source and full Git history

次をread-onlyで確認しました。

- `git ls-files`によるcurrent tracked files 202件のfilename監査
- `git rev-list --objects --all`と`git cat-file`による全132 commits、unique historical blobs 661件のfilename / content監査
- tracked fileと全履歴に対するprivate key marker、AWS access key形式、AWS ARN、Account ID文脈、EC2 Instance ID、GitHub token、Slack tokenのpattern検査
- `.env.prod` / `.env.production`、private key、credential file、database dump、backupに該当するhistorical filename検査
- current / historical generic password、secret、token assignmentの候補をpath単位で確認
- commit author / committer emailのnoreply判定。メール実値は表示・記録していない
- GitHub連携で取得できた61 Issuesと33 Pull Requestsのtitle / bodyに対する同じidentifier pattern検査
- README、Docs index、security / deploy docs、workflow、`.gitignore`、tracked screenshotsの公開範囲確認

専用secret scannerはrepositoryに未導入のため追加installせず、Git objectと正規表現によるread-only監査を行いました。この方式は既知patternの検出であり、entropy解析やprovider側でのcredential有効性確認を代替しません。

### Findings

| Check | Result |
| --- | --- |
| Current / historical `.env.prod` or `.env.production` | 検出なし |
| Current / historical private-key filename or key marker | 検出なし |
| Current / historical database dump or backup filename | 検出なし |
| AWS access key形式 | 検出なし |
| AWS ARN / Account ID文脈 / EC2 Instance ID | 検出なし |
| GitHub token / Slack token形式 | 検出なし |
| Generic password / secret assignments | デモ・test用の明示的なダミーcredential候補のみ。production secret候補は検出なし |
| Docs内のemail形式 | デモ用addressまたはsystemd等の技術表記。commit metadataのメールとの一致なし |
| Non-noreply commit metadata | 132 commitsが影響。実値は非表示 |
| GitHub Issue title / body | 61件で対象identifier patternの検出なし |
| GitHub PR title / body | 33件中1件にexample / noreply以外のemail形式が1件。commit metadataとは不一致。実値は非表示、要手動分類 |
| README掲載screenshots | 5件を目視確認。デモ用データのみで、secret / private identifierの写り込みなし |
| `docs/figma/` screenshots | 6件にbrowser chrome、外部design URL、profile / bookmark等の公開不要情報が写り込み。要削除、crop、または安全なexportへの差し替え |
| Git history rewrite | 未実施 |

検出なしは今回使用したpatternと取得できたGit objectsの範囲を意味し、credentialが存在しないことを暗号学的に保証するものではありません。GitHub Actions logs / artifacts、Issue / PR comments、添付画像、Console内の連携設定はlocal Git監査の対象外なので、後述の手動確認が完了するまで公開可とは判断しません。

### GitHub repository inventory

GitHub連携によるread-only確認と事前監査結果:

- visibility: private
- default branch: `main`
- description: 設定済み
- homepage URL / topics: 未設定
- Issues / Projects: 有効
- Wiki / Pages / Discussions: 無効
- GitHub上のbranch: `main`とIssue #91の作業branch
- tags / releases: `v0.1.0`、`v0.2.0`、`v0.3.0`。release assetなし
- workflow: `.github/workflows/ci.yml`のみ
- merge commit / squash / rebase: すべて有効
- merged branch自動削除: 無効
- LICENSE / SECURITY.md: 監査開始時はいずれもなし
- private repositoryの現在のplanではmain Rulesetを利用不可

localに残るremote-tracking refはGitHub上の現在branch一覧と同義ではありません。削除判断は本監査へ混ぜず、GitHub Consoleのbranch一覧を正本として確認します。

## GitHub Actions audit

`ci.yml`は`pull_request`と`main`への`push`でbackend / frontendを検証します。runnerはGitHub-hosted `ubuntu-latest`だけで、`pull_request_target`、self-hosted runner、artifact upload、deploy、repository write、production secret参照はありません。使用ActionはGitHub公式の次のversion tagだけです。

- `actions/checkout@v4`
- `actions/setup-python@v5`
- `actions/setup-node@v4`

PostgreSQL passwordとDjango secret keyはCI専用の明示的なdummy値で、production credentialではありません。fork Pull Requestへrepository secretを渡す参照もありません。

workflowにはtop-levelの明示的権限がなかったため、Issue #92で次を追加します。

```yaml
permissions:
  contents: read
```

これによりworkflowの`GITHUB_TOKEN`をsource checkoutに必要なread-onlyへ限定します。GitHub Console側のdefault workflow permissionsもread-onlyであること、ActionsによるPull Request作成・承認を許可していないことを手動確認します。

## License policy

Ricettaは現時点では採用担当・面接官に見せるportfolioとして公開します。オープンソースライセンスは付与せず、LICENSE fileも追加しません。All rights reservedとし、sourceがpublicに閲覧可能であることを、利用・改変・再配布を許諾するオープンソース化と同一視しません。

将来オープンソース化する場合は、dependency、第三者素材、contribution方針を確認したうえでライセンス方針を再検討します。

## Security reporting policy

脆弱性やsecret漏えいの疑いをpublic Issue、PR、Discussionへ書かない方針とし、[Security Policy](../../.github/SECURITY.md)でGitHub private vulnerability reportingを案内します。個人メールアドレスやproduction secretは報告先としてDocsへ掲載しません。

public化前にGitHub Consoleでprivate vulnerability reportingを有効化し、repositoryのSecurityタブに **Report a vulnerability** が表示されることを確認します。利用できない状態はsecurity reportのprivateな受け口がないため、public化停止条件です。

## GitHub Console manual checklist

以下はcredential値やprivate identifierをIssue / PRへ転記せず、存在、用途、owner、最終利用時期、削除判断だけをprivateな監査記録で確認します。

### Public repository presentation

- [ ] homepage URLが公開デモの意図したHTTPS URLである
- [ ] topicsがportfolioとtech stackを過不足なく表す
- [ ] social previewにsecret、個人情報、実店舗データ、不適切なcropがない
- [ ] description、README、screenshots、Issues / PR、comments、添付画像がpublic向けである
- [ ] Wiki / Pages / Discussionsの無効状態が意図どおりである
- [ ] LICENSEがなく、READMEのLicense節とGitHub表示が方針どおりである

### Pull Requests and branches

- [ ] merge commit / squash / rebaseの許可方針を#30で確定する
- [ ] merged branch自動削除を有効化するか#30で確定する
- [ ] branches、tags、releasesとassetを棚卸しし、不要項目は公開前に別途判断する
- [ ] open / closed Issues、PR、review、comments、添付画像に公開不可情報がない

### Actions

- [ ] Workflow permissionsのdefaultがread-only
- [ ] GitHub ActionsによるPull Request作成・承認を許可していない
- [ ] fork PRとfirst-time / external contributorのworkflow実行がapproval対象
- [ ] fork PRへwrite tokenまたはrepository / environment secretを渡さない
- [ ] Actions logs / artifactsのretention期間が必要最小限
- [ ] 過去のActions logsにsecret、個人メール、AWS / Slack private identifierがない
- [ ] artifact一覧が空、または全assetの内容・retention・公開影響を確認済み
- [ ] repository / organizationにpublic repositoryから利用可能なself-hosted runnerがない

### Secrets, access, and integrations

- [ ] Repository secretsを名前・用途・最終利用workflowで棚卸し
- [ ] Environment secretsとprotection rulesを棚卸し
- [ ] Repository / Environment / Organization Variablesを棚卸し
- [ ] Deploy keysに不要なkeyやwrite accessがない
- [ ] Webhooksに不要なendpointやproductionへ直接到達する連携がない
- [ ] GitHub Apps / OAuth Appsのrepository accessと権限が必要最小限
- [ ] collaborators / teams / outside collaboratorsの権限が必要最小限
- [ ] organization base permissionとrepository roleの組合せを確認

### Security features

- [ ] dependency graphが有効
- [ ] Dependabot alertsを確認し、公開停止に相当する未解決事項がない
- [ ] Dependabot security updatesの採否を確認
- [ ] secret scanningが有効
- [ ] push protectionが有効
- [ ] private vulnerability reportingが有効で、private report導線を確認
- [ ] code scanningの利用有無と未対応alertを確認
- [ ] public化直後にSecurity alertsと設定を再確認する担当者を決める

## Main Ruleset immediately after public visibility

現在のprivate repository planではRulesetを利用できないため、#30でpublic化が承認され、人間がvisibilityをpublicへ変更した直後にGitHub Consoleでmain Rulesetを作成します。Rulesetが有効になるまで通常の変更をmerge / pushしません。

1. **Settings → Rules → Rulesets → New branch ruleset**を開く。
2. 対象branchをdefault branch `main`へ限定する。
3. Rulesetをactiveにする。
4. branch deletionを禁止する。
5. non-fast-forward updateを禁止し、force pushを許可しない。
6. Pull Request経由を必須にする。
7. required status checksとしてCIの`backend`と`frontend`を指定する。
8. branch更新後にstatus checksの再実行を要求するか、現在の開発flowに合わせて確認する。
9. bypass listは空を原則とする。緊急時のrepository owner bypassが必要なら、対象role、利用条件、事後reviewを#30で明文化する。
10. Ruleset enforcement画面とtest PRで、直接push、force push、branch削除、CI未成功mergeが拒否されることを確認する。

public化により既存ruleの適用状態が変わる可能性があるため、visibility変更直後と最初のPR merge前の2回確認します。

## Public release stop conditions

次のいずれかが未解決なら#30でpublic化を承認しません。

- currentまたはGit履歴に有効なcredential、private key、token、password、公開不可identifierがある
- Actions logs / artifacts、Issue、PR、comment、添付画像にsecretまたは公開不可情報がある
- PR本文で検出したemail形式1件が公開可能な技術表記か確認されていない
- `docs/figma/`のbrowser screenshot 6件が公開不要なbrowser / account関連情報を含む
- public repositoryから利用可能なself-hosted runnerがある
- fork由来workflowへwrite tokenまたはsecretを渡す設定がある
- productionへ直接到達する不要なDeploy key、Webhook、App / OAuth連携がある
- private vulnerability reportingを含む非公開のsecurity report導線がない
- non-noreply commit metadataの公開影響についてrepository ownerの判断がない
- LICENSEなし / All rights reserved方針がREADMEとGitHub表示で明確でない
- public化直後にmain Rulesetを設定・検証する担当者と手順が確定していない
- #30でMajor以上と判断された問題が残っている

secretが見つかった場合はrepositoryから削除するだけでは不十分です。まずcredentialを失効・rotationし、その後にGit履歴、Actions logs / artifacts、Issue / PR等の修正範囲を判断します。

## Known Issues for Issue #30

1. **Commit metadata email:** 全132 commitsにnoreplyではないauthorまたはcommitter emailが含まれます。実値は記録しません。選択肢は、公開影響を理解して現履歴を維持する、public化前に別Issueで履歴書換えと全ref調整を計画する、または公開を延期する、のいずれかです。本Issueでは履歴を書き換えません。
2. **GitHub Console audit incomplete:** Actions logs / artifacts、Issues / PR / attachments、secrets、variables、keys、hooks、Apps、collaborators、runner、Security機能は人間のConsole確認が必要です。
3. **PR body email candidate:** 33 PRsのtitle / body監査で、example / noreply以外のemail形式が1件あります。commit metadataのメールとは一致しません。実値をIssueやDocsへ転記せず、GitHub Consoleで公開可能な技術表記か個人情報かを分類し、必要ならpublic化前にredactします。
4. **Figma reference screenshots:** `docs/figma/`の6件はbrowser全体のscreenshotで、browser chrome、外部design URL、profile / bookmark等の公開不要情報が写り込んでいます。public化前に削除、必要範囲だけへのcrop、またはbrowser chromeを含まない安全なexportへの差し替えが必要です。画像内の実値はIssue / PRへ転記しません。
5. **Repository presentation:** homepage URLとtopicsが未設定で、social previewは手動確認が必要です。
6. **Branch governance:** main Rulesetはprivate状態では利用不可です。public化直後に設定し、最初の通常変更前に検証する必要があります。
7. **Repository workflow policy:** 3つのmerge方式とmerged branch自動削除方針が未確定です。
8. **Off-repository exposure:** GitHub Actions history、release metadata、Issue / PR comments等はGit objectsのpattern監査だけでは網羅できません。

## Handoff to Issue #30

Issue #30では、手動チェックリストを完了し、Known Issuesを一件ずつaccept / remediate / deferとして判断します。公開承認時は、visibility変更担当者、main Ruleset設定担当者、public化直後のActions / Security再確認担当者、問題発見時にprivateへ戻す判断者を記録します。

public化直後は、Ruleset、Actions default permissions、fork approval、Security alerts、secret scanning / push protection、公開README / social preview、branches / tags / releasesの見え方を再確認します。確認が終わるまで新しい通常変更をmergeしません。
