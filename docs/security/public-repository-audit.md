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
- commit metadataに含まれるprivacy情報の有無と公開影響を確認。実値は表示・記録していない
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
| Repository privacy findings | current treeとGit履歴を確認し、repository ownerが影響を評価して対応方針を決定済み。実値は非表示 |
| GitHub Issue title / body | 61件で対象identifier patternの検出なし |
| GitHub PR title / body | PR #55の1件はsystemd template unit identifierによるemail形式のfalse positive。個人メール、credential、private identifierではないことを確認済み |
| README掲載screenshots | 5件を目視確認。デモ用データのみで、secret / private identifierの写り込みなし |
| Git history rewrite | 未実施 |

検出なしは今回使用したpatternと取得できたGit objectsの範囲を意味し、credentialが存在しないことを暗号学的に保証するものではありません。GitHub Actions logs / artifacts、Issue / PR comments、添付画像、Console内の連携設定はlocal Git監査の対象外なので、後述の手動確認が完了するまで公開可とは判断しません。

### GitHub repository inventory

GitHub連携によるread-only確認と事前監査結果:

- visibility: private
- default branch: `main`
- description / homepage URL / topics: 設定済み。Websiteは [https://ricetta.lintake.net](https://ricetta.lintake.net)
- Issues / Projects: 有効
- Pull Requests: 有効
- Wiki / Sponsorships / Discussions: 無効
- GitHub Pages: 未設定
- Releases: 表示。Deployments / Packages: 非表示
- GitHub上のbranch: `main`のみ
- tags / releases: `v0.1.0`、`v0.2.0`、`v0.3.0`。release assetなし
- workflow: `.github/workflows/ci.yml`のみ
- merge commit / squash: 有効。rebase / auto-merge: 無効
- Pull Request branchの更新提案 / merged branch自動削除: 有効
- LICENSE: なし（All rights reserved方針）
- `.github/SECURITY.md`: あり、内容確認済み
- private repositoryの現在のplanではmain Rulesetを利用不可

localに残るremote-tracking refはGitHub上の現在branch一覧と同義ではありません。削除判断は本監査へ混ぜず、GitHub Consoleのbranch一覧を正本として確認します。

## GitHub Actions audit

`ci.yml`は`pull_request`と`main`への`push`でbackend / frontendを検証します。runnerはGitHub-hosted `ubuntu-latest`だけで、`pull_request_target`、self-hosted runner、artifact upload、deploy、repository write、production secret参照はありません。使用ActionはGitHub公式の次のversion tagだけです。

- `actions/checkout@v4`
- `actions/setup-python@v5`
- `actions/setup-node@v4`

PostgreSQL passwordとDjango secret keyはCI専用の明示的なdummy値で、production credentialではありません。fork Pull Requestへrepository secretを渡す参照もありません。

workflowには現在、次のread-only権限を明示しています。

```yaml
permissions:
  contents: read
```

これによりworkflowの`GITHUB_TOKEN`をsource checkoutに必要なread-onlyへ限定します。GitHub Consoleでは次を確認済みです。

- 使用Actionは`actions/checkout`、`actions/setup-python`、`actions/setup-node`だけ
- Actionをfull-length commit SHAへ固定する設定は無効
- artifact / log retentionは30日
- fork Pull Request workflowは無効
- default workflow permissionsはread-only
- ActionsによるPull Request作成・承認は無効
- 他repositoryからのActions accessは`Not accessible`
- self-hosted runnerは0件
- latest CIはsuccess
- artifactsは0件
- 2026-08-26 JSTに、GitHub APIで取得可能な93 runs / 185 jobs / 約4.8 MBのlogsをread-onlyで確認
- private key marker、AWS access key / ARN / Account ID / EC2 Instance ID、GitHub / Slack token、JWT、email形式、secret assignmentの高信頼patternは検出なし
- 12桁数値候補はDocker image layer IDによるfalse positive。failure 1件はGitHub-hosted runnerのDocker pull HTTP 500で、credentialまたはapplication test failureではない

## License policy

Ricettaは現時点では採用担当・面接官に見せるportfolioとして公開します。オープンソースライセンスは付与せず、LICENSE fileも追加しません。All rights reservedとし、sourceがpublicに閲覧可能であることを、利用・改変・再配布を許諾するオープンソース化と同一視しません。

将来オープンソース化する場合は、dependency、第三者素材、contribution方針を確認したうえでライセンス方針を再検討します。

## Security reporting policy

脆弱性やsecret漏えいの疑いをpublic Issue、PR、Discussionへ書かない方針とし、[Security Policy](../../.github/SECURITY.md)でGitHub private vulnerability reportingを案内します。個人メールアドレスやproduction secretは報告先としてDocsへ掲載しません。

private vulnerability reportingは公開前Blockerにはしません。public化直後に有効化し、repositoryのSecurityタブに **Report a vulnerability** が表示されることを必須確認とします。確認が終わるまでは通常のmerge / pushを行いません。

## GitHub Console manual checklist

以下はcredential値やprivate identifierをIssue / PRへ転記せず、存在、用途、owner、最終利用時期、削除判断だけをprivateな監査記録で確認します。

### Public repository presentation

- [x] descriptionが設定済み
- [x] homepage URLが公開デモの意図したHTTPS URLである
- [x] topicsがportfolioとtech stackを過不足なく表す
- [ ] social previewにsecret、個人情報、実店舗データ、不適切なcropがない
- [x] READMEとSecurity Policyがpublic向けである
- [ ] screenshots、Issues / PR、comments、添付画像がpublic向けである
- [x] Issues / Projects / Pull Requestsが有効
- [x] Wiki / Sponsorships / Discussionsが無効
- [x] Releasesが表示され、Deployments / Packagesが非表示
- [x] LICENSEがなく、READMEのLicense節とGitHub表示が方針どおりである

### Pull Requests and branches

- [x] default branchが`main`
- [x] remote branchが`main`だけ
- [x] merge commit / squashを許可し、rebaseを許可しない
- [x] Pull Request branchの更新提案とmerged branch自動削除が有効
- [x] auto-mergeが無効
- [ ] public化直後にmain Ruleset / branch protectionを設定・検証する
- [ ] open / closed Issues、PR、review、comments、添付画像に公開不可情報がない

### Actions

- [x] 使用ActionがGitHub公式の3 Actionだけ
- [x] full-length commit SHA固定が無効
- [x] Workflow permissionsのdefaultがread-only
- [x] GitHub ActionsによるPull Request作成・承認を許可していない
- [x] fork Pull Request workflowが無効
- [x] 他repositoryからのActions accessが`Not accessible`
- [x] Actions logs / artifactsのretention期間が30日
- [x] 過去のActions logsにsecret、個人メール、AWS / Slack private identifierがない
- [x] latest CIがsuccess
- [x] artifact一覧が0件
- [x] self-hosted runnerが0件

### Secrets, access, and integrations

- [x] Repository secretsが0件
- [x] Environment secretsが0件
- [x] Actions variablesが0件
- [x] Environmentsが0件
- [x] Deploy key `ricetta-ec2-pull`はread-onlyで維持
- [x] Webhooksが0件
- [x] GitHub AppはChatGPT Codex Connectorのみで、repository accessは`Only select repositories`
- [x] external collaboratorsが0件
- [x] pending invitationsが0件
- [x] Codespaces secrets / trusted repositoriesが0件

### Security features

- [x] dependency graphが有効
- [x] Dependabot alertsが有効で、検出vulnerabilityが0件
- [x] Dependabot malware alertsが有効で、検出malwareが0件
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
- public repositoryから利用可能なself-hosted runnerがある
- fork由来workflowへwrite tokenまたはsecretを渡す設定がある
- productionへ直接到達する不要なDeploy key、Webhook、App / OAuth連携がある
- LICENSEなし / All rights reserved方針がREADMEとGitHub表示で明確でない
- public化直後にmain Rulesetを設定・検証する担当者と手順が確定していない
- #30でMajor以上と判断された問題が残っている

secretが見つかった場合はrepositoryから削除するだけでは不十分です。まずcredentialを失効・rotationし、その後にGit履歴、Actions logs / artifacts、Issue / PR等の修正範囲を判断します。

## Remaining controls for Issue #30

Public release auditで確認した非Blockerのprivacy事項は、repository ownerが影響を確認し、対応方針を決定済みです。詳細な判断記録はGit repository外で管理します。有効なcredentialやproduction secretの検出はありません。

Public化直後にSocial preview、main Ruleset / branch protection、secret scanning、push protection、private vulnerability reporting、code scanningの利用可否を設定・確認します。完了するまで通常のmerge / pushを行いません。

## Handoff to Issue #30

Issue #30では、手動チェックリストを完了し、公開前監査で残るBlockerがないことと、public化直後の担当・手順を確認します。公開承認時は、visibility変更担当者、main Ruleset設定担当者、public化直後のActions / Security再確認担当者、問題発見時にprivateへ戻す判断者を記録します。

public化直後は、Ruleset、Actions default permissions、fork approval、Security alerts、secret scanning / push protection、公開README / social preview、branches / tags / releasesの見え方を再確認します。確認が終わるまで新しい通常変更をmergeしません。
