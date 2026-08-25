# Security Policy

## Reporting a vulnerability

Ricettaの脆弱性またはsecret漏えいの可能性を見つけた場合は、public Issue、Pull Request、Discussionへ詳細を書かないでください。production secret、credential、個人情報、再現に必要なprivate identifier、未修正のexploit detailsも公開コメントへ貼り付けないでください。

GitHub repositoryの **Security** タブにあるprivate vulnerability reporting（**Report a vulnerability**）を使用してください。この導線が表示されない場合はpublic reportを作成せず、repository ownerがprivate vulnerability reportingを有効化するまで詳細の送信を控えてください。

報告には、secret実値を除いた影響範囲、再現条件、該当versionまたはcommit、最小限の再現手順を含めてください。secretの可能性がある値は本文へ複製せず、種類と露出箇所だけを示してください。

## Supported versions

Ricettaは現在、採用担当・面接官向けのportfolioとして公開する準備段階です。正式なsupport期間やsecurity update SLAは設けていません。公開デモおよびdefault branchの現行versionを確認対象とし、過去のtagに対する個別の修正提供は保証しません。

## Disclosure

修正、credential rotation、公開時期は影響を確認してからrepository ownerが判断します。修正または緩和が完了する前に、脆弱性の詳細をpublic Issue等へ移さないでください。
