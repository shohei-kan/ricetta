# EC2 Resource Monitoring

## Purpose and Scope

Ricetta公開デモの単一EC2について、CloudWatchの標準メトリクスとCloudWatch Agentの最小メトリクスで、基盤異常とリソース逼迫を早期検知します。

AWSアカウント全体のBudget、請求、Free Tier、月次コスト確認は [AWS Cost Monitoring and Billing Guardrails](./aws-cost-monitoring.md) を参照してください。本書はEC2の稼働・resource監視を対象とし、請求ガードレールは扱いません。

この構成は2026-08-17に実環境への導入と再起動後の動作確認まで完了しています。変動するAWS resource ID、ARN、Slack IDはこの文書へ保存しません。

対象環境:

- Region: `ap-northeast-1`
- Instance: Ubuntu 24.04 x86_64 / `t3.micro`
- EC2基本モニタリングを維持（詳細モニタリングは無効）
- 固定AWS access keyは使わず、EC2 IAM Roleを使う

対象外:

- CloudWatch Logs、trace、X-Ray
- Docker mount、overlay、tmpfs、全device
- 60秒未満のhigh-resolution metric
- 自動復旧、EC2停止・再起動action
- EC2 RoleによるAlarm、SNS、Dashboard管理

## Source-managed files

| File | Purpose | Deployment destination |
| --- | --- | --- |
| [`ops/cloudwatch/amazon-cloudwatch-agent.json`](../../../ops/cloudwatch/amazon-cloudwatch-agent.json) | Agent metrics configuration | `/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json` |
| [`ops/cloudwatch/cloudwatch-agent-put-metrics-policy.json`](../../../ops/cloudwatch/cloudwatch-agent-put-metrics-policy.json) | EC2 Role用最小IAM policy | IAM inline/customer-managed policy input |

repository内のAgent JSONをsource of truthとします。`fetch-config`でfile設定を読み込むと、Agent側のruntime設定コピーは`/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.d/file_amazon-cloudwatch-agent.json`に作成されます。このruntime fileを直接編集せず、repository側を修正して再配置・再適用します。

Account ID、Instance ID、SNS ARN、Slack workspace/channel IDは環境固有値としてGitへ保存しません。Alarm、SNS、Amazon Q Developer in chat applications、DashboardはAWS管理者がConsoleまたは管理用credentialで作成します。

## Metric collection design

| Source | Namespace | Metric | Statistic | Period | Dimensions |
| --- | --- | --- | --- | --- | --- |
| EC2 standard | `AWS/EC2` | `StatusCheckFailed` | Maximum | 60 seconds | `InstanceId` |
| EC2 standard | `AWS/EC2` | `CPUUtilization` | Average | 300 seconds | `InstanceId` |
| EC2 standard | `AWS/EC2` | `CPUCreditBalance` | Minimum | 300 seconds | `InstanceId` |
| Agent | `CWAgent` | `mem_used_percent` | Average | 60 seconds | `InstanceId` |
| Agent | `CWAgent` | `disk_used_percent` | Maximum | 60 seconds | `InstanceId` |

Agent設定はmemory measurementに`mem_used_percent`を指定し、disk measurementはroot filesystem `/`の`used_percent`を指定して、60秒間隔で収集します。これはAWS Agent公式のLinux EC2 default configと同じmeasurement名です。`append_dimensions`と`aggregation_dimensions: [["InstanceId"]]`は維持します。

Memory metricは`append_dimensions`適用後のoriginalがすでに`InstanceId`だけを持ちます。CloudWatch Agentの`ProcessRollup`は集約先dimension数がoriginal以上の場合にrollupを作らないため、memoryでoriginalをdropすると送信対象が0件になります。このためmemには`drop_original_metrics`を設定せず、`InstanceId`だけを持つoriginalの`mem_used_percent`を送信します。

Disk metricのoriginalにはfilesystem由来の追加dimensionがあり、`aggregation_dimensions`によって`InstanceId`だけの`disk_used_percent`を別途生成できます。diskでは`drop_original_metrics: ["disk_used_percent"]`と`drop_device: true`を維持し、追加dimensionを持つoriginalを送信しません。最終的な送信対象は、どちらも`InstanceId`だけをdimensionに持つ`mem_used_percent`と`disk_used_percent`の2系列です。logs / tracesセクションはなく、Agent自身の利用統計も`usage_data: false`で無効化します。

InstanceIdはAgentの`${aws:InstanceId}`置換を使い、EC2 metadataから取得します。Instance Metadata ServiceはIMDSv2を使用し、EC2 Roleへ`ec2:DescribeInstances`を追加しません。

## Minimal IAM policy

EC2 Role `ricetta-demo-backup-role`へ、source-managed policy JSONの内容だけを追加します。

```text
Action: cloudwatch:PutMetricData
Resource: *
Condition: cloudwatch:namespace = CWAgent
```

`PutMetricData`はresource-level ARNで制限できないため`Resource: "*"`とし、namespace conditionで`CWAgent`だけに制限します。AWS managed `CloudWatchAgentServerPolicy`はCloudWatch LogsやX-Ray等の不要権限を含むため使用しません。Alarm、SNS、Dashboardの作成・変更権限もEC2 Roleへ付与しません。

IAM変更はEC2上では行わず、管理者が別の管理sessionから適用します。適用後はIAM Role credentialが自動更新されるため、固定keyや`~/.aws/credentials`は作りません。

## Alarm design

Alarm名にはenvironmentと目的を含めますが、Git管理する文書には実Instance IDを入れません。例: `ricetta-demo-ec2-cpu-high`。

| Alarm | Namespace | MetricName | Dimension | Statistic | Period | Threshold | ComparisonOperator | EvaluationPeriods | DatapointsToAlarm | TreatMissingData | ALARM | OK | INSUFFICIENT_DATA |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| EC2 status failed | `AWS/EC2` | `StatusCheckFailed` | `InstanceId` | Maximum | 60 | 1 | GreaterThanOrEqualToThreshold | 1 | 1 | missing | SNS notify | SNS notify | SNS notify |
| CPU high | `AWS/EC2` | `CPUUtilization` | `InstanceId` | Average | 300 | 80% | GreaterThanOrEqualToThreshold | 3 | 3 | missing | SNS notify | SNS notify | SNS notify |
| CPU credits low | `AWS/EC2` | `CPUCreditBalance` | `InstanceId` | Minimum | 300 | 24 credits | LessThanOrEqualToThreshold | 3 | 3 | missing | SNS notify | SNS notify | SNS notify |
| Memory high | `CWAgent` | `mem_used_percent` | `InstanceId` | Average | 60 | 85% | GreaterThanOrEqualToThreshold | 10 | 10 | breaching | SNS notify | SNS notify | SNS notify |
| Root disk high | `CWAgent` | `disk_used_percent` | `InstanceId` | Maximum | 60 | 80% | GreaterThanOrEqualToThreshold | 5 | 5 | breaching | SNS notify | SNS notify | SNS notify |

EC2基本モニタリングでもstatus check metricsは1分周期で提供されるため、StatusCheckFailedは60秒・1/1で検知します。CPU alarmは基本モニタリングの5分粒度で3連続、合計15分の高負荷を検知します。メモリは10分、diskは5分の連続超過を要求し、一時的な変動を除外します。

### Production alarms

2026-08-17に次の5 Alarmを設計表どおり作成し、threshold、statistic、period、M-of-N、TreatMissingDataを照合しました。

- `ricetta-demo-status-check-failed`
- `ricetta-demo-cpu-utilization-high`
- `ricetta-demo-cpu-credit-balance-low`
- `ricetta-demo-memory-used-high`
- `ricetta-demo-root-disk-used-high`

全AlarmでActionsEnabledは有効、ALARM / OK / INSUFFICIENT_DATAの各通知actionは1件、確認終了時の状態はすべてOKです。actionは通知だけで、自動再起動、EC2停止、自動復旧actionは設定していません。

### CPUCreditBalance threshold

`t3.micro`は2 vCPUのburstable instanceで、baselineを超えるCPU使用はcreditを消費します。24 creditsはこのinstanceが1時間に獲得する12 creditsの2倍で、残量枯渇より前に調査する運用上のearly-warning値です。実際の残り時間はCPU使用率とUnlimited modeのsurplus credit課金状態で変わるため、固定の「稼働可能時間」とは解釈しません。運用実績を2～4週間確認し、通常時に24付近まで下がるならthresholdまたはevaluationを見直します。

## Missing data and notification policy

| State transition | SNS / Slack | Policy |
| --- | --- | --- |
| `ALARM` | Notify | 障害・逼迫として一次対応を開始 |
| `OK` | Notify | 復旧を共有し、原因・対応・再発防止を記録 |
| `INSUFFICIENT_DATA` | Notify | telemetry gapとしてAgent/system/EC2状態を確認 |

EC2標準メトリクスは`missing`とし、全評価点が欠測なら`INSUFFICIENT_DATA`へ遷移させます。Agentメトリクスは継続的に毎分送られる前提なので`breaching`とし、Agent停止やIAM/network不具合もALARMとして検知します。これにより、メモリ・diskの高騰とAgent欠測が同じAlarmになるため、通知受信後は最初にmetric graphとAgent statusを見て区別します。

各AlarmのAlarm action、OK action、Insufficient data actionへ同じSNS topicを設定します。CloudWatch actionは状態遷移時に実行され、状態継続中に繰り返し通知されない点に注意します。

## Agent installation on Ubuntu x86_64

以下は実EC2で行う手順です。このrepositoryの作業では実行しません。

### 1. Package download and verification

AWS公式のUbuntu amd64 packageを一時directoryへdownloadします。

```bash
monitoring_tmp="$(mktemp -d)"
cd "$monitoring_tmp"
curl -fLO https://amazoncloudwatch-agent.s3.amazonaws.com/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
curl -fLO https://amazoncloudwatch-agent.s3.amazonaws.com/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb.sig
curl -fLO https://amazoncloudwatch-agent.s3.amazonaws.com/assets/amazon-cloudwatch-agent.gpg
expected_fingerprint="937616F3450B7D806CBD9725D58167303B789C72"
actual_fingerprint="$(
  gpg --with-colons --show-keys amazon-cloudwatch-agent.gpg |
    awk -F: '$1 == "fpr" { print $10; exit }'
)"
test "$actual_fingerprint" = "$expected_fingerprint"
gpg --import amazon-cloudwatch-agent.gpg
gpg --verify amazon-cloudwatch-agent.deb.sig amazon-cloudwatch-agent.deb
```

期待fingerprintはAWS公式のCloudWatch Agent署名検証文書に掲載された値です。作業時点でも公式文書のfingerprintとdownload URLを再確認します。fingerprint照合または`gpg --verify`が失敗した場合はinstallしません。`curl | sudo`や未検証packageのinstallは行いません。

### 2. Install and place configuration

```bash
sudo dpkg -i amazon-cloudwatch-agent.deb
sudo systemctl stop amazon-cloudwatch-agent
sudo install -o root -g root -m 0644 \
  /srv/ricetta/ops/cloudwatch/amazon-cloudwatch-agent.json \
  /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
```

### 3. Local validation

```bash
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json
```

`fetch-config`が設定をparseし、失敗時は非zeroになります。読み込まれたfile設定は`/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.d/file_amazon-cloudwatch-agent.json`へ展開されますが、このruntime copyではなくrepository側のJSONをsource of truthとして維持します。IAM policyがまだ未反映の場合は`-s`を付けず、設定validation後に停止状態を維持します。

JSON schema validationとruntime設定への変換成功は、設定形式と変換処理の成功だけを示します。receiverが対象measurementを実際に収集し、CloudWatchへ期待するmetric名で送信できたことまでは保証しません。実際にdiskだけ到着してmemoryが欠落した事例があるため、再適用後はAgent statusに加え、CloudWatchの`ListMetrics`とdatapoint取得で`mem_used_percent` / `disk_used_percent`双方の到着を確認します。

```bash
if sudo systemctl is-active --quiet amazon-cloudwatch-agent; then
  echo "CloudWatch Agent started before IAM was ready" >&2
  exit 1
fi
```

### 4. Start and verify automatic startup

IAM policy適用後に起動します。

```bash
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -s \
  -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json

sudo systemctl enable amazon-cloudwatch-agent
sudo systemctl status amazon-cloudwatch-agent --no-pager
sudo systemctl is-enabled amazon-cloudwatch-agent
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a status
```

CloudWatch Consoleの`CWAgent` namespaceで、対象InstanceIdの2メトリクスだけが約1分間隔で到着することを確認します。EC2再起動後にもserviceがactiveで、新しいdatapointが届くことを確認します。

### Production Agent verification

2026-08-17にUbuntu 24.04 x86_64 / `t3.micro`へCloudWatch Agent `1.300071.0b1720`を導入しました。

- 公式deb、署名、GPG keyを取得し、AWS公式fingerprintとの一致とGPG署名成功を確認してからinstallした
- repository JSONとruntime copyの一致、JSON schema validation、config translation成功を確認した
- serviceはenabled / active、Agent statusはrunning / configured
- usage dataは無効
- 固定AWS access keyは使用せずEC2 IAM Roleを使用
- Agent権限はnamespaceを`CWAgent`へ限定した`cloudwatch:PutMetricData`だけ
- CloudWatch上には`mem_used_percent`と`disk_used_percent`の2系列だけが存在する
- 両系列はnamespace `CWAgent`、60秒間隔、dimensionは`InstanceId`だけで、同じEC2を示し、最新datapointが継続して到着している

初回検証ではdiskだけが到着し、memoryが未送信でした。原因候補は、`InstanceId`だけを持つmemory originalと同数dimensionのrollupが生成されない状態でoriginalをdropし、送信対象が0件になったことです。memのdrop設定を削除したsourceを再適用後、memoryとdiskの2系列が継続して到着することを確認しました。

## SNS and Slack notification route

構成:

```text
CloudWatch Alarm
→ SNS topic in ap-northeast-1
→ Amazon Q Developer in chat applications Slack channel configuration
→ existing Slack monitoring channel
```

管理者による構築手順:

1. `ap-northeast-1`に監視専用SNS standard topicを作成する。
2. Amazon Q Developer in chat applicationsでSlack workspaceをauthorizeする。
3. 既存監視channelのconfigurationを作成または更新し、SNS topicを関連付ける。
4. Q Developer用IAM Roleとguardrailは通知閲覧に必要な範囲に限定する。EC2 Roleを流用しない。
5. 5つのAlarmのALARM / OK / INSUFFICIENT_DATA actionにSNS topicを指定する。
6. 安全な一時Alarmまたは一時thresholdでALARM→OK通知を確認し、元のthresholdへ戻してテスト用Alarmを削除する。

SNS topic ARN、Slack workspace ID、channel IDはAWS側だけで管理します。Incoming WebhookやLambdaは使いません。既存のEC2 backup alert webhookとは別経路・別責務です。

### Production notification verification

2026-08-17にSNS topic `ricetta-demo-cloudwatch-alarms`、Amazon Q channel configuration `ricetta-demo-monitoring`、Slack channel `infra-alerts`を構成しました。IDとARNはこの文書へ記録しません。

- SNS subscription confirmed
- Amazon Q test messageのSlack到着を確認
- 安全な一時AlarmでALARM通知を確認
- thresholdを安全な値へ戻し、OK通知を確認
- 一時Alarmを削除し、本番用Alarmが5件だけ残っていることを確認
- Slackスマートフォン通知を確認

Macデスクトップ通知はAWS監視構成のAcceptance Criteriaには含めません。

## Dashboard

1つのCloudWatch Dashboardに以下を配置します。

| Row | Widget | View |
| --- | --- | --- |
| 1 | Alarm status | 5 alarms |
| 2 | `StatusCheckFailed` | Maximum, 1 minute |
| 2 | `CPUUtilization` | Average, 5 minutes |
| 3 | `mem_used_percent` | Average, 1 minute |
| 3 | `disk_used_percent` | Maximum, 1 minute |
| 4 | `CPUCreditBalance` | Minimum, 5 minutes |

Dashboard名、Region、InstanceIdはAWS側で入力し、sourceへ実値を保存しません。期間は通常3時間、調査時は24時間または1週間へ切り替えます。

2026-08-17にDashboard `ricetta-demo-ec2-monitoring`を作成しました。widgetは7件で、5 Alarmの状態、5 metrics、説明用textを表示し、validation messageが0件であることを確認しました。Dashboard、SNS、Alarm、Amazon Qは手動管理とし、Terraform化は今回の対象外です。

## EC2 reboot verification

2026-08-17に計画再起動を実施し、次を確認しました。

- CloudWatch Agentが自動起動し、enabled / active、running / configuredへ復旧
- runtime設定を正常に読み込んだ
- `mem_used_percent`と`disk_used_percent`が再起動約1分後から毎分到着
- Docker Composeの全4サービスが自動復旧
- backendとdbがhealthy
- HTTPS health endpointが200
- 5 Alarmが最終的にすべてOK

## Incident first response

Alarm通知からRicetta全体の共通トリアージへ入る場合は [Incident Response Runbook](../operations/incident-response.md) を入口にし、本節で各metric固有の確認を行います。

| Alarm | First checks | Initial action |
| --- | --- | --- |
| Status check | EC2 status checks、AWS Health、reachability | AWS基盤障害かinstance障害かを切り分ける。自動rebootはしない |
| CPU high | `docker stats`、`top`、request増加、backup/reset時刻 | runaway processを特定。安易にprocessをkillせず影響を確認 |
| CPU credits low | CPU graph、credit消費傾向、surplus credit | 高CPU原因を抑制。継続するならinstance sizeを検討 |
| Memory high | `free -h`、`docker stats`、OOM journal | memory consumerとOOMを確認。swap追加は別判断 |
| Disk high | `df -h /`、`docker system df`、Docker logs、backup directory | 大きい対象を特定。DB volumeやbackupを無断削除しない |
| Agent missing | Agent status、journal、IAM、IMDSv2、network | Agent再起動前にfailure reasonを保存 |

共通確認:

```bash
uptime
free -h
df -h /
docker stats --no-stream
docker system df
sudo systemctl status amazon-cloudwatch-agent --no-pager
sudo journalctl -u amazon-cloudwatch-agent -n 100 --no-pager
```

対応後はAlarmがOKへ戻った時刻、原因、操作、再発防止を記録します。

## Rollback

Agentに問題がある場合は、計画停止をSlackへ共有し、管理者がAgent Alarm actionsを無効化したことを確認してから、次の順でAgentをstop / disableします。Agent欠測は`breaching`扱いなので、actionsを先に止めないとALARM通知されます。

```bash
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a stop
sudo systemctl disable amazon-cloudwatch-agent
```

停止後、最後にEC2 RoleからAgent用policyを外します。package削除が必要な場合だけ`sudo apt remove amazon-cloudwatch-agent`を実行します。EC2標準Alarm、SNS、DashboardはAgent rollbackだけを理由に削除しません。

## Rebuild procedure

1. EC2へ既存のapplication / backup IAM Roleをattachする。
2. source-managed最小Agent policyを管理者sessionからRoleへ追加する。
3. repositoryをdeployし、Agent packageの署名を検証してinstallする。
4. source-managed設定を所定pathへ配置し、parse validationする。
5. Agentをenable/startし、`CWAgent`の2 metricsだけが到着することを確認する。
6. AWS管理者がSNS、Amazon Q Developer Slack configuration、5 alarms、Dashboardを再作成する。
7. ALARM / OK通知を安全な一時thresholdで確認する。
8. EC2を計画再起動し、Agent自動起動とmetric再開を確認する。

将来Terraform / Ansible化する際は、2つのJSONとAlarm design tableを入力仕様とし、Region、InstanceId、SNS ARN、Slack IDsをenvironment-specific variablesへ分離します。

## Cost review

AWSアカウント全体の実コスト、Budget、Free Tier、resource棚卸しの最新正本は [AWS Cost Monitoring and Billing Guardrails](./aws-cost-monitoring.md) です。以下はIssue #56で監視追加分を設計した時点の記録です。

2026-08-17にAWS公式料金ページで見積前提を確認しました。

```text
Cost review status: complete
Checked date: 2026-08-17
Region: ap-northeast-1
Free Tier assumption: アカウント内の対象Free Tier枠が他用途で消費されていないと仮定
Estimated monitoring increment: USD 0/month under the stated Free Tier assumption
```

見積対象:

- EC2基本モニタリング: 詳細モニタリングを有効化しない
- custom metrics: `CWAgent`の2系列
- metric alarms: 5 standard-resolution alarms
- Dashboard: 1 dashboard（50 metrics以下）
- SNS notifications
- Amazon Q Developer in chat applicationsの通知利用
- Logs ingestion/storage: 0
- high-resolution metrics/alarms: 0

確認時点のFree Tier前提は、CloudWatch custom / detailed metrics 10、standard-resolution alarm metrics 10、50 metrics以下のcustom dashboard 3、SNSは最初の月100万requestです。Amazon Q Developer in chat applications自体に追加料金はなく、underlying servicesの料金だけが対象です。

今回の2 custom metrics、5 standard-resolution alarms、1 dashboard、少量のSNS通知は、同じAWSアカウントで該当Free Tier枠が他用途に消費されていない前提では月額USD 0想定です。アカウント全体のFree Tier使用量は実際には確認していないため、他用途や将来の追加resourceによって課金される可能性があります。AWS creditsは見積もりに含めません。

実請求はBilling / Cost Explorerで導入後も継続確認します。想定外のcustom metric数が増えた場合は、`CWAgent`のdimension一覧とAgent configを確認します。

## Verification checklist for production rollout

- [x] EC2 Roleにnamespace制限付き`PutMetricData`だけが追加されている
- [x] 固定AWS credentialsがない
- [x] Agent設定validationが成功する
- [x] Agentがactive / enabled、running / configuredである
- [x] `CWAgent`に2 metrics、各InstanceId 1系列だけがある
- [x] StatusCheckFailedは1分、その他EC2 standard metricsは5分、detailed monitoringが無効である
- [x] 5 alarmsが設計表どおりで、最終状態がすべてOKである
- [x] ALARM / OK / INSUFFICIENT_DATA actionsがSNS topicを参照する
- [x] SlackでALARMとOKを受信できる
- [x] Dashboardに5 metrics、alarm status、説明textがありvalidation messageがない
- [x] 再起動後にAgentとmetric送信が復旧する
- [x] test alarm / temporary thresholdが残っていない

## References

- [AWS: Create the CloudWatch agent configuration file](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/create-cloudwatch-agent-configuration-file.html)
- [AWS CloudWatch Agent source: Linux EC2 default config](https://github.com/aws/amazon-cloudwatch-agent/blob/9884add8ed69a6d2ab7d9c8c5bf9bbce66a7302c/translator/config/defaultConfig.go)
- [AWS CloudWatch Agent source: ProcessRollup](https://github.com/aws/amazon-cloudwatch-agent/blob/9884add8ed69a6d2ab7d9c8c5bf9bbce66a7302c/plugins/outputs/cloudwatch/cloudwatch.go)
- [AWS: Manage detailed monitoring for EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/manage-detailed-monitoring.html)
- [AWS: Verify the CloudWatch Agent package signature](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/verify-CloudWatch-Agent-Package-Signature.html)
- [AWS: Configure how CloudWatch alarms treat missing data](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/alarms-and-missing-data.html)
- [AWS: CloudWatch alarm actions](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/alarm-actions.html)
- [AWS: Amazon Q Developer in chat applications](https://docs.aws.amazon.com/chatbot/latest/adminguide/what-is.html)
- [AWS: CloudWatch pricing](https://aws.amazon.com/cloudwatch/pricing/)
- [AWS: SNS pricing](https://aws.amazon.com/sns/pricing/)
- [AWS: Amazon Q Developer in chat applications pricing](https://aws.amazon.com/chatbot/pricing/)
