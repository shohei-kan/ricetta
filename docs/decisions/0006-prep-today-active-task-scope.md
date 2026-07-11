# 0006 Prep Today active task scope

## Status

Accepted

## Context

厨房ではタスクを追加した日より、未完了か、いつ完了したかが重要です。予定日だけで一覧を絞ると、前日以前の未完了タスクが画面から消え、現場の仕込みボードとして機能しません。

## Decision

Prep Todayには次を表示します。

- `todo` と `doing` は予定日に関係なく表示する
- `done` は `completed_at` が今日のタスクだけ表示する
- summaryは表示対象の `todo` / `doing` / `done` 件数とする
- `done` へ変更した時点で `completed_at` を設定する
- `done` から未完了へ戻した場合は `completed_at` をnullに戻す
- 現在Shopのタスクだけを対象にする

MVPでは持ち越しラベル、優先度、トリアージ用の色分けを追加しません。

## Consequences

- 未完了タスクは完了するまでPrep Todayに残ります。
- 完了タスクは当日の作業履歴として見え、翌日以降は一覧から外れます。
- 完了レコード自体は削除せず、将来の履歴機能に利用できます。
- `date` query parameterは未完了の予定日絞り込みではなく、完了日の基準日として扱います。
