### 1. スクリプトの説明
このスクリプトは下記の2つのアプリのレポートファイルを組み合わせ、タイムエントリを昇順に並び替えます。
- Toggle Track Detailed Report
- TrackingTime Report

扱える期間は次のようになっています。
- 昨日
- 昨日~今日
- 今日

そのためレポート(CSVファイル)を各アプリのウェブサイトからダウンロードする際は、上記の日付をレポート範囲として選ぶ必要があります。
またTrackingTimeでレポートを選択する際は、TASK・FROM・TO・DATEのカラムがレポートに含まれる必要があります。

---

それぞれのアプリのレポートのダウンロード方法は次のようになります。

[Toggl](https://toggl.com)

Reports → Detailed → 期間の選択

[TrackingTime](https://trackingtime.co/)

Reports → TimeSheets → 期間の選択


ダウンロードしたレポートはinputディレクトリに移動させます。スクリプトを実行させるとCSVファイルがoutputディレクトリに出力されます。

---

**pythonではなくpython3で実行してください。**

このスクリプトは3つの引数を持ちます。

`python3 merge_timelog.py 期間 開始時刻 エンコーディング`

例)

`python merge_timelog.py today`

`python merge_timelog.py today 8 utf8`

期間は必ず指定が必要ですが、開始時刻とエンコーディングは必要に応じで指定してください。開始時刻とエンコーディングの順番は問いません。

#### 期間

期間を省くことはできません。また以下の3つのみを受け付けます。
- yesterday
- yesterday~
- today

yesterdayは昨日1日のみを扱います。昨日の日付で出力ファイルを作成します。

yesterday~は昨日と今日の2日間を扱います。昨日の日付で出力ファイルを作成します。

todayは今日1日のみを扱います。今日のの日付で出力ファイルを作成します。

#### 開始時刻

任意で開始時刻を設定できます。開始時刻を整数(0~23)で設定すると、開始時刻以降の時間帯のみを出力ファイルに書き込みます。デフォルトでは最初に6時間以上エントリー間に開きがあった場合、6時間の開きがあった後のエントリーから出力ファイルに書き込みます。

#### エンコーディング

任意でエンコーディングを指定できます。選べるのはutf8とp932(SHIFT-JIS)となっています。デフォルトではutf8がしてれています。

### 2. 出力の説明
出力するCSVファイルには2つのレポートファイルをマージし、開始時刻の昇順で並び替えられたものが書き込まれます。書き込まれるカラムはTask, From, Toの3項目となっています。時刻は24時間表記で書き込まれます。
| Task | From | To |
| --- | --- | --- |
| task1 | 06:30 | 07:00 |
| task2 | 07:30 | 09:00 |
| task3 | 10:00 | 12:00 |
