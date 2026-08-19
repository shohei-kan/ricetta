# AWS Cost Monitoring and Billing Guardrails

## Purpose and Scope

Ricetta公開デモを運用するAWSアカウント全体について、想定外課金を早期に把握し、月次で原因を調査するための正本です。AWS Budgets、Cost Explorer、Free Tier、Credits、Billsの確認手順、現在のコスト基準、再構築、一次対応、rollbackを扱います。

EC2のCPU・メモリ・ディスク等の稼働監視は [EC2 Resource Monitoring](./ec2-resource-monitoring.md)、S3上のPostgreSQL backup運用は [Backup and Restore](../backup/backup-and-restore.md) を参照してください。本書はアプリケーション障害監視ではなく、AWSアカウント全体の請求リスクを対象とします。

対象外:

- AWSリソースや通知経路の自動変更
- 本格的なFinOps、複数accountへのコスト配賦
- Terraform / AnsibleによるBilling設定の管理
- Budget超過時のEC2停止やresource削除

AWS Account ID、Instance ID、ARN、通知先Email、Slack workspace/channel IDはrepositoryへ保存しません。変動する金額は確認日付きの観測または概算として扱い、恒久的な料金保証にしません。

## Monitoring layers and responsibility

| Layer | Purpose | Update latency / trigger |
| --- | --- | --- |
| AWS Budgets | 月額警戒線に対する段階通知 | 約8〜12時間程度。リアルタイム監視ではない |
| Cost Explorer | 増加したservice、Usage Type、Record Type、Regionの調査 | 当月値は見込みであり請求確定値ではない |
| Free Tier | Always Free等の使用量と上限の確認 | 月次確認 |
| Credits | promotional / service credit残高の確認 | 月次確認 |
| Bills | 税、service別請求、請求確定値の確認 | 月次および請求確定後 |

Budgetは課金を止める仕組みではありません。自動Budget Actionは設定せず、通知後に人間が影響、backup、依存関係を確認して対応します。

## Production changes completed before this documentation work

以下のAWS実環境変更は、このsource-first文書整備より前に管理者が実施済みです。今回のCodex作業はその状態を文書化するもので、AWS、SNS、Amazon Q、Slack、Budgetへ追加の変更は行っていません。

- 既存SNS Topic PolicyへAWS Budgets用Statementを1件追加した
- ACTUAL 30 / 50 / 80 / 100%の各通知へSNS subscriberを1件ずつ追加した
- FORECASTED 100%通知を追加し、Email subscriber 1件とSNS subscriber 1件を設定した

既存のEmail通知、CloudWatch用SNS Policy Statement、SNS→Amazon Q→Slack接続は維持しています。

## Production Budget configuration

以下は2026-08-19に実環境で確認済みです。

| Setting | Verified value |
| --- | --- |
| Budget name | `AWS費用` |
| Type / period | `COST` / `MONTHLY` |
| Limit | USD 10 |
| Metric | `UnblendedCost` |
| Cost filters | なし（AWSアカウント全体） |
| Cost types | 未指定（AWS既定値） |
| Automatic Budget Actions | 0 |

Budget上限USD 10は、通常月額の保証やresource停止条件ではなく、厳格な警戒線として当面維持します。Public demoを常時稼働する場合は、公開後の実績を確認したうえでUSD 20を見直し候補とします。

### Notifications

| Cost basis | Threshold | Comparison | 2026-08-19 state |
| --- | --- | --- | --- |
| ACTUAL | 30% | `GREATER_THAN` | ALARM |
| ACTUAL | 50% | `GREATER_THAN` | ALARM |
| ACTUAL | 80% | `GREATER_THAN` | OK |
| ACTUAL | 100% | `GREATER_THAN` | OK |
| FORECASTED | 100% | `GREATER_THAN` | OK |

各通知にはEmail subscriber 1件とSNS subscriber 1件が設定されています。Email実値は記録しません。Budgetの更新には約8〜12時間かかるため、通知stateとCost Explorerの表示時刻を確認し、即時性を前提にしません。

通知経路:

```text
AWS Budgets
→ existing SNS topic
→ Amazon Q Developer in chat applications
→ Slack infra-alerts
```

既存SNS Topic PolicyではCloudWatch用Statementを維持し、Budget用Statementを1件追加済みです。Budget用StatementはPrincipalを`budgets.amazonaws.com`、Actionを`SNS:Publish`とし、`aws:SourceAccount`で同一account、`aws:SourceArn`で同一accountのAWS Budgetsに限定しています。Topicは非KMS暗号化、HTTPS subscriptionは1件です。policyのARNやAccount ID実値はGitへ保存しません。再構築やrollbackでは現在のPolicyを先に読み取り、Policy document全体を盲目的に上書きしません。

BudgetからSlackへの実通知到着は次回Budget評価待ちです。CloudWatch Alarmから同じSNS→Amazon Q→Slack経路への通知確認済みという事実だけでは、Budget publisherの実通知確認を代替しません。

## Current cost baseline

### Verified Cost Explorer observation

2026-08-19時点の当月Cost Explorerで確認済みの見込み値です。請求確定値ではありません。

| Item | Observed cost (approx.) |
| --- | ---: |
| 税込見込み合計 | USD 6.61 |
| Usage subtotal before tax | USD 6.01 |
| Tax | USD 0.60 |
| EC2 `t3.micro` | USD 2.28 |
| EBS `gp3` | USD 1.62 |
| Public IPv4 total | USD 2.11 |
| Public IPv4 IdleAddress | USD 1.26 |
| Public IPv4 InUseAddress | USD 0.85 |
| S3 | USD 0.00029 |
| CloudWatch | USD 0.00014 |
| Secrets Manager | USD 0.000015 |

データ転送費は無視できる規模でした。`NetUnblendedCost`と`UnblendedCost`は同額で、CreditのRecord Typeはありませんでした。

### Estimate, not a verified bill

2026-08-19の利用状況と料金前提から、24時間稼働時の税込月額を約USD 18と概算します。この値は利用時間、月の日数、税、無料枠、料金改定で変動します。Budget USD 10との比較用の概算であり、請求額の保証ではありません。

- EC2停止中は`t3.micro`のcompute料金が止まる
- EBSとPublic IPv4はEC2停止中も課金が続く
- Public IPv4はidle / in-useとも確認時点でUSD 0.005/hour

最新料金は [VPC pricing](https://aws.amazon.com/vpc/pricing/) と [EBS pricing](https://aws.amazon.com/ebs/pricing/) を確認します。

## Resource inventory

2026-08-19に実環境で確認済みです。

| Resource | Verified state | Cost note |
| --- | --- | --- |
| EC2 | `t3.micro` 1台、detailed monitoring disabled | running中のcomputeを確認 |
| EBS | `gp3` 30 GiB 1個、接続中、encryption false | EC2停止中も課金 |
| Public IPv4 | Elastic IP 1個、関連付け済み、未関連付け0 | idle / in-useとも課金対象 |
| EBS Snapshot | 0 | 現在なし |
| NAT Gateway | 0 | 現在なし |
| Load Balancer | 0 | 現在なし |
| RDS | 0 | 現在なし |
| S3 bucket | 1 | backup保存先 |
| Route 53 hosted zone | 0 | 現在なし |

EBS未暗号化はこのIssueでは変更しません。Issue #69のTemporary EC2 rebuild drillで、暗号化されたroot EBSとして再構築する候補です。

### S3 backup cost state

S3 backupの運用責務と復旧手順は [Backup and Restore](../backup/backup-and-restore.md) を正本とします。2026-08-19に以下を実環境で確認しました。

- Region: `ap-northeast-1`
- default encryption: `AES256`
- Public Access Block: 4項目すべてtrue
- Versioning: disabled
- Lifecycle: なし
- Object count: 19
- Total size: 274139 bytes
- timestamp付きPostgreSQL backupで、現状は極小

現在のsizeでは1日1件でも年間数MB程度という概算のため、Lifecycleは追加しません。長期保持要件、object数、storage / request costは月次棚卸しで再評価します。

Versioningが無効であることは、backupの削除・上書きからの保護や復元可能性を保証しません。backupの安全性と復元確認は [Backup and Restore](../backup/backup-and-restore.md) およびrestore drillで別途確認します。

## Free Tier and credits

2026-08-19に実環境で確認済みです。

| Item | Verified state |
| --- | --- |
| CloudWatch Alarm | Always Free上限10に対して十分余裕あり |
| Custom metrics | Always Free上限10に対して十分余裕あり |
| Dashboard | Always Free上限3に対して十分余裕あり |
| SNS cost | USD 0 |
| Issue #56 monitoring increment | 現時点で無料枠内 |
| Credit balance | なし |
| New free / promotional credits | なし |

無料枠や料金条件は変更され得るため、固定値だけを根拠にせず [Free Tier usage tracking](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/tracking-free-tier-usage.html) とBilling Consoleで毎月確認します。

## Monthly cost review

月1回、およびBudget通知受信時に次の順で確認します。画面表示の期間、通貨、見込みか確定かを記録し、Account ID等はIssueへ転記しません。

1. **Budgets**: `AWS費用`の当月actual / forecast、各通知state、通知履歴、Actionが0件であることを確認する。
2. **Cost Explorer**: 当月を選び、以下の順でGroup byまたはFilterして増加要因を絞る。
   1. Service
   2. Usage Type
   3. Record Type
   4. Region
3. **Free Tier**: current usage、limit、forecastを確認する。
4. **Credits**: credit残高、期限、Record Typeへの反映を確認する。残高がない場合も「なし」と記録する。
5. **Bills**: service別料金、Tax、前月確定値を確認し、Cost Explorerの見込みとの差を確認する。
6. 下記resource棚卸しを実施し、不要に見えるresourceもbackupと依存関係を確認するまで削除しない。

### Cost inventory checklist

- [ ] EC2: instance数、state、type、稼働時間、detailed monitoring
- [ ] EBS: volume数、type、size、attachment、snapshot、暗号化
- [ ] Public IPv4: in-use / idle address数、関連付け
- [ ] Snapshot: EBS Snapshot数と保持期間
- [ ] S3: bucket数、object数、size、request / transfer、Versioning、Lifecycle
- [ ] CloudWatch: custom metrics、alarms、dashboards、logs
- [ ] Route 53: hosted zone、domain関連費用
- [ ] NAT Gateway: 個数、稼働時間、data processing
- [ ] Load Balancer: 個数、稼働時間、処理量
- [ ] RDS: instance / storage / snapshot
- [ ] Cost Explorerに現れたその他serviceと未使用resource

## Unexpected charge first response

請求異常と同時にapplication障害やsecurity侵害が疑われる場合は、証拠保全と影響範囲の切り分けを [Incident Response Runbook](../operations/incident-response.md) から開始します。

1. Budget通知のactual / forecast、threshold、対象期間、評価時刻を確認する。
2. Cost ExplorerをService → Usage Type → Record Type → Regionの順で絞り、増加源を特定する。
3. 対象serviceのConsoleまたはread-only APIでresourceを特定する。識別子をpublicなIssueへ転記しない。
4. resourceのowner、用途、backup、依存関係、削除時の復旧方法を確認する。確認前に停止・detach・release・deleteしない。
5. 不正利用が疑われる場合はIAM activity、root MFA、CloudTrail、不審または意図しないcredentialの有無を確認し、credential漏えい対応を優先する。
6. 必要に応じてAWS Supportへ連絡する。
7. 確認期間、原因、影響額、実施した対応、継続確認事項をIssueとhandoffへ記録する。secretやresource IDは記録しない。

Budgetは遅延するため、通知時点で既に費用が増えている可能性があります。上限超過だけを理由に、稼働resourceを自動削除しません。

## Rebuild and verification procedure

Temporary EC2 rebuild時はIssue #69のRunbookから本節へリンクし、Billing管理権限を持つ管理者sessionで手動再構築します。EC2 RoleへBudgets、SNS policy変更、Cost Explorer管理権限を追加しません。

1. Billing Consoleでaccount全体のmonthly COST Budgetを作成する。
2. Limit USD 10、`UnblendedCost`、filterなし、CostTypes未指定、Action 0件を設定する。
3. ACTUAL 30 / 50 / 80 / 100%、FORECASTED 100%、`GREATER_THAN`を設定する。
4. 各通知へ管理対象Email 1件と既存SNS Topic 1件を設定する。実値はrepositoryへ保存しない。
5. SNS Topic Policyを読み取り、既存CloudWatch Statementを保持したままBudget用Statementだけを追加する。Policy document全体を未確認のtemplateで上書きしない。
6. Budget用StatementのPrincipal / Actionと、同一accountへ限定する`aws:SourceAccount` / `aws:SourceArn`条件をConsole上で照合する。
7. SNS→Amazon Q Developer→Slack `infra-alerts`の既存関連付けを確認する。
8. Budget一覧と通知設定を再表示し、Budget、threshold、subscriber、Action 0件を照合する。
9. 次回Budget評価後にEmailとSlackへの実通知到着を確認する。到着前は未検証として記録する。
10. Cost Explorer、Free Tier、Credits、Billsとresource棚卸しを実行し、確認日付きbaselineを更新する。

account固有placeholderを埋めるだけのJSONは作成しません。将来Terraform化する場合、本書のBudget表、通知表、policy制約、検証手順を入力仕様とします。

## Rollback

変更対象を限定し、既存Email通知、CloudWatch Alarm通知、Amazon Q接続は維持します。

1. FORECASTED 100%通知だけを削除する。
2. 必要な各Budget通知からSNS subscriberだけを削除し、Email subscriberは維持する。
3. SNS Topic PolicyからBudget用Statementだけを削除し、既存CloudWatch用Statementを維持する。
4. Budget一覧、通知subscriber、SNS Topic Policyを再表示して対象外の設定が維持されていることを確認する。

Budget本体、CloudWatch Alarm、SNS Topic、HTTPS subscription、Amazon Q channel configurationをまとめて削除しません。

## Acceptance Criteria mapping

| Issue #77 Acceptance Criteria | Evidence in this document |
| --- | --- |
| AWSコストの上限目安が決まっている | USD 10を厳格な警戒線として維持し、USD 20は将来候補と明記 |
| 想定外の課金を通知で検知できる | 5段階のBudget通知とEmail / SNS経路を記録。Budget→Slack実通知は保留 |
| 無料枠 / クレジット残高の確認手順が分かる | Monthly cost reviewとFree Tier and credits |
| EC2停止中にも課金されるリソースを把握できている | EBSとPublic IPv4の継続課金、resource inventory |
| 月次で確認するコスト項目が整理されている | Monthly cost reviewとcost inventory checklist |
| 想定外課金時の確認手順がDocsに残っている | Unexpected charge first response |

通知構成は作成済みですが、Budget→Slack実通知到着だけがAcceptance Criteriaの最終検証として残っています。

## Open items and handoff

- 次回Budget評価でBudget→SNS→Amazon Q→Slackの実通知到着を確認し、本節とhandoffを更新する。
- Budget上限は公開後の実績を見て再評価する。現時点ではUSD 10を維持する。
- EBS未暗号化はIssue #77で変更せず、Issue #69で暗号化root EBSとしての再構築候補にする。
- S3 Lifecycleは現時点で追加せず、長期保持要件と実コストを定期的に再評価する。
- Terraform / Ansible化は別Issueで扱う。

## References

- [AWS Budgets: Managing your costs with AWS Budgets](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html)
- [AWS Budgets: SNS topic policy](https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-sns-policy.html)
- [AWS Cost Explorer](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-exploring-data.html)
- [AWS Free Tier usage tracking](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/tracking-free-tier-usage.html)
- [Amazon VPC pricing](https://aws.amazon.com/vpc/pricing/)
- [Amazon EBS pricing](https://aws.amazon.com/ebs/pricing/)
