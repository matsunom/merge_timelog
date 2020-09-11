# -*- coding: utf-8 -*-
'''
merge_timelog.pyはTrackingTimeのレポートのCSVファイルとToggl TrackのDetailed ReportのCSVファイルを統合し並び替えます。
実行はpython3で行ってください。
実行オプションは以下の通り。
today         : 今日のエントリーを今日の日付でCSVファイルに出力します。
yesterday     : 昨日のエントリーを昨日の日付でCSVファイルに出力します。
yesterday~    : 昨日と今日のエントリーを昨日の日付でCSVファイルに出力します。
-t yyyy-mm-dd : 指定した日(もしくは次の日も含めて)のエントリーを指定した日の日付でCSVファイルに出力します。

またデフォルトでは睡眠時間を考慮しタイムログのエントリーに6時間の開きがあった場合、最初の6時間と最後の6時間が含まれないエントリーが出力されるようになっています。
もし開始時刻を指定したい場合は実行時に指定してださい。
例)
python3 merge_timelog.py yesterday~ 5
上記の場合午前5時台に開始されたエントリーからCSVファイルに出力されます。

またCSVファイルヘの出力エンコーディングを指定できます。
デフォルトではutf8が設定されており、Excelなどで文字化けせずに内容を確認したい場合は以下のように実行時に指定してください。
python3 merge_timelog yesterday ~ cp932

'''
__author__ = "MatsunoM <https://github.com/matsunom>"

import sys
import datetime
import glob
import csv

# 日時のテキストを取得する
def getDayText(day, t1_day=None):
    dt_today = datetime.date.today()
    if day == 'today':
        day_text = dt_today.strftime('%Y-%m-%d')
    elif day == 'yesterday' or day == 'yesterday~':
        dt_yesterday = dt_today - datetime.timedelta(days=1)
        day_text = dt_yesterday.strftime('%Y-%m-%d')
    elif day == '-t':
        day_text = t1_day.strftime('%Y-%m-%d')
    return day_text

# ファイル名の文字列を取得
def getFname(day, t1_day=None):
    dt_today = datetime.date.today()
    dt_yesterday = dt_today - datetime.timedelta(days=1)
    if day == 'today':
        toggl_file = 'Toggl_time_entries_' + dt_today.strftime('%Y-%m-%d') + '_to_' + dt_today.strftime('%Y-%m-%d')
        trackingtime_file = 'TrackingTime ' + dt_today.strftime('%b %-d,%Y') + '-' + dt_today.strftime('%b %-d,%Y')
        return [toggl_file, trackingtime_file]
    elif day == 'yesterday':
        toggl_file = 'Toggl_time_entries_' + dt_yesterday.strftime('%Y-%m-%d') + '_to_' + dt_yesterday.strftime('%Y-%m-%d')
        trackingtime_file = 'TrackingTime ' + dt_yesterday.strftime('%b %-d,%Y') + '-' + dt_yesterday.strftime('%b %-d,%Y')
        return [toggl_file, trackingtime_file]
    elif day == 'yesterday~':
        toggl_file1 = 'Toggl_time_entries_' + dt_yesterday.strftime('%Y-%m-%d') + '_to_' + dt_yesterday.strftime('%Y-%m-%d')
        trackingtime_file1 = 'TrackingTime ' + dt_yesterday.strftime('%b %-d,%Y') + '-' + dt_yesterday.strftime('%b %-d,%Y')
        toggl_file2 = 'Toggl_time_entries_' + dt_yesterday.strftime('%Y-%m-%d') + '_to_' + dt_today.strftime('%Y-%m-%d')
        trackingtime_file2 = 'TrackingTime ' + dt_yesterday.strftime('%b %-d,%Y') + '-' + dt_today.strftime('%b %-d,%Y')
        return [toggl_file1, toggl_file2, trackingtime_file1, trackingtime_file2]
    elif day == '-t':
        t2_day = t1_day + datetime.timedelta(days=1)
        toggl_file1 = 'Toggl_time_entries_' + t1_day.strftime('%Y-%m-%d') + '_to_' + t1_day.strftime('%Y-%m-%d')
        trackingtime_file1 = 'TrackingTime ' + t1_day.strftime('%b %-d,%Y') + '-' + t1_day.strftime('%b %-d,%Y')
        toggl_file2 = 'Toggl_time_entries_' + t1_day.strftime('%Y-%m-%d') + '_to_' + t2_day.strftime('%Y-%m-%d')
        trackingtime_file2 = 'TrackingTime ' + t1_day.strftime('%b %-d,%Y') + '-' + t2_day.strftime('%b %-d,%Y')
        return [toggl_file1, toggl_file2, trackingtime_file1, trackingtime_file2]        

    else:
        print('Please select today or yesterday or -t')
        sys.exit()


# ファイル読み込みエントリーの集合を返す
def readFile(fname):
    with open(fname) as f:
        reader = csv.DictReader(f)
        lines = [row for row in reader]
    if 'Toggl' in fname:
        entries = readToggl(lines)
    elif 'TrackingTime' in fname:
        entries = readTrackingTime(lines)
    return entries

def readToggl(lines):
    try:
        entries = [[line.get('Description'), timeConvert_for_Toggl(line.get('Start time')), timeConvert_for_Toggl(line.get('End time')), datetime.datetime.strptime(line.get('Start date'), '%Y-%m-%d'), datetime.datetime.strptime(line.get('End date'), '%Y-%m-%d')] for line in lines]
    except ValueError:
        entries = [[line.get('Description'), timeConvert_for_Toggl(line.get('Start time')), timeConvert_for_Toggl(line.get('End time')), datetime.datetime.strptime(line.get('Start date'), '%Y/%m/%d'), datetime.datetime.strptime(line.get('End date'), '%Y/%m/%d')] for line in lines]
    return entries

# trackingtimeにはタスク終了時の日付が見つからないないためスタートと同じ日付をいれる
def readTrackingTime(lines):
    entries = [[line.get('Task'), timeConvert_for_TrackingTime(line.get('From')), timeConvert_for_TrackingTime(line.get('To')), datetime.datetime.strptime(line.get('Date'), '%m/%d/%Y'), datetime.datetime.strptime(line.get('Date'), '%m/%d/%Y')] for line in lines]
    return entries

def timeConvert_for_Toggl(time_text):
    return ":".join(time_text.split(":")[:-1])

def timeConvert_for_TrackingTime(time_text):
    time_parts = time_text.split(":")
    time_h = int(time_parts[0])
    time_m = time_parts[1].split()[0]
    noon = time_parts[1].split()[1]
    # 24時間表記に変換する
    if noon == 'pm' and time_h != 12:
        time_h += 12
    elif noon == 'am' and time_h == 12:
        time_h -= 12
    time = str(time_h) + ":" + time_m
    return time

def over24hour(entries):
    this_day = entries[0][3].day
    entries2 = []
    num = 1
    for entry in entries:
        if entry[3].day != this_day or entry[4].day != this_day:
            start_time = str(int(entry[1].split(":")[0]) + 24) + ':' + str(entry[1].split(":")[1])
            end_time = str(int(entry[2].split(":")[0]) + 24) + ':' + str(entry[2].split(":")[1])
            entry[1] = start_time
            entry[2] = end_time
        # TrackingTimeのログはEnd Dateが存在しないため、Start Dateで穴埋めされている。そのための例外処理
        elif entry[3].day == this_day and int(entry[2].split(":")[0]) == 0:
            end_time = str(int(entry[2].split(":")[0]) + 24) + ':' + str(entry[2].split(":")[1])
            entry[2] = end_time
        entries2.append(entry[:3])
    return entries2

# 2桁にすべて揃える
def formatChange(entries):
    entries2 = []
    for entry in entries:
        start_hour, start_minute = entry[1].split(":")
        end_hour, end_minute = entry[2].split(":")
        if len(start_hour) < 2:
            start_hour = str(0) + start_hour
            start_time = start_hour + ":" + start_minute
            entry[1] = start_time
        if len(end_hour) < 2:
            end_hour = str(0) + end_hour
            end_time = end_hour + ":" + end_minute
            entry[2] = end_time
        entries2.append(entry)
    return entries2

# 時刻によるフィルター
# エントリー上部・下部に睡眠総当分のフィルター
def timeFilter(entries, start_hour=None):
    # 引数による開始時刻の指定が無ければ、上下のエントリの終了時刻と開始時刻の間にとX時間以上の開きがあった場合のエントリから取り出す
    breaktime = 6 # default
    index_num = []
    # if start_hour == None:
    for i, entry in enumerate(entries):
        # 1回目は2つの比較ができないのでスキップ
        if i == 0:
            start_time1 = int(entry[1].split(":")[0])
            end_time1 = int(entry[2].split(":")[0])
            continue
        start_time2 = int(entry[1].split(":")[0])
        end_time2 = int(entry[2].split(":")[0])
        # エントリ1の終了時刻とエントリ2の終了時刻を比較
        if (start_time2 - end_time1) >= breaktime:
            index_num.append(i)
        start_time1 = start_time2
        end_time1 = end_time2

    if not start_hour == None:
        for i, entry in enumerate(entries):
            start_time = int(entry[1].split(":")[0])
            if start_time >= start_hour:
                index_start_hour = i
                break
    else:
        index_start_hour = None

    if len(index_num) >= 2:
        if index_start_hour == None:
            return entries[index_num[0]:index_num[-1]]
        else:
            if index_start_hour > index_num[0]:
                if index_start_hour > index_num[-1]:
                    print("Error: start_hour is over daytime.")
                    sys.exit()
            index_num[0] = index_start_hour
            return entries[index_num[0]:index_num[-1]]
    elif len(index_num) == 1:
        if index_start_hour == None:
            if int(entries[index_num[0]][1].split(":")[0]) > 24 + breaktime:
                return entries[:index_num[0]]
            else:
                return entries[index_num[0]:]
        else:
            if index_start_hour < index_num[0]:
                if int(entries[index_num[0]][1].split(":")[0]) > 24 + breaktime:
                    return entries[index_start_hour:index_num[0]]
                else:
                    return entries[index_start_hour:]
            else:
                print("Error: start_hour is over daytime.")
                sys.exit()
    else:
        if index_start_hour == None:
            return entries
        else:
            return entries[index_start_hour:]


def calcAmountTimeEntries(entries):
    amount_entry_time = datetime.timedelta(days=0, hours=0, minutes=0) # 初期化
    for entry in entries:
        start_time = entry[1].split(":")
        start_time = datetime.timedelta(hours=int(start_time[0]), minutes=int(start_time[1]))
        end_time = entry[2].split(":")
        end_time = datetime.timedelta(hours=int(end_time[0]), minutes=int(end_time[1]))   
        duration = end_time - start_time
        if duration <= datetime.timedelta(days=0, hours=0, minutes=0):
            end_time += datetime.timedelta(days=1)
            duration = end_time - start_time
        amount_entry_time += duration
    return amount_entry_time

def writeFile(fname, entries, encoding):
    try:
        with open(fname, 'w', encoding=encoding) as output_csv:
            header = ['Name', 'From', 'To']
            writer = csv.writer(output_csv)
            writer.writerow(header)
            writer.writerows(entries)
    except LookupError:
        sys.exit()

def main():
    # 引数処理
    args = sys.argv
    try:
        which_day = args[1]
    except IndexError:
        print('Please select today or yesterday or -t.')
        sys.exit()

    start_hour = None
    encoding = 'utf8'
    if len(args) > 2: 
        for arg in args[2:]:
            try:
                start_hour = int(arg)
                if (start_hour < 0) or (24 <= start_hour):
                    print("開始時刻の指定は0から23までです。")
                    sys.exit()
            except ValueError:
                if len(arg) < 6:
                    encoding = arg
                    if encoding not in ['cp932', 'utf8']:
                        print('csv encoding error and select utf8 or cp932(SHIFT-JIS).')
                        sys.exit()
                else:
                    try:
                        t_day = datetime.datetime.strptime(arg, '%Y-%m-%d')
                    except ValueError:
                        print("-tオプションでの日付指定方式が間違っています。")
                        print("2020-09-10 のようにハイフンで区切って入力してください。")
                        sys.exit()
    # ファイル名の取得    
    if which_day == '-t':
        fnames = getFname(which_day, t_day)
    else:
        fnames = getFname(which_day)
    dirpath = '/Users/matsunom/Downloads/'
    matchpath = dirpath + '*.csv'
    csv_names = glob.glob(matchpath)

    # print(fnames)
    # print(csv_names)

    fpaths = []
    for fname in fnames:
        for csv_name in csv_names:
            if csv_name.startswith(dirpath + fname):
                fpaths.append(csv_name)
    if not fpaths:
        print('No Time Record Files in ~/Downloads ')
        sys.exit()
    
    # print(fpaths)

    entries = []
    for fpath in fpaths:
        entries.extend(readFile(fpath))
    
    # 24時以降を25時のようにする
    entries = over24hour(entries)
    # 1桁の数字は2桁にする
    entries = formatChange(entries)
    # エントリーを from をキーにして並び替える
    entries.sort(key=lambda x: x[1])
    # 1日の開始時刻フィルダーをかける
    # print(entries)
    # timeFilter(entries)
    entries = timeFilter(entries, start_hour)

    # エントリー数と活動時間を出力
    num_entries = len(entries)
    amount_entry_time = '時間'.join(str(calcAmountTimeEntries(entries)).split(':')[:-1]) + '分'
    print("{} entries. {} work.".format(num_entries, amount_entry_time))

    # ファイル名の生成
    if which_day == '-t':
        output_file = dirpath + 'TimeLog_' + getDayText(which_day, t_day) + '.csv'
    else:
        output_file = dirpath + 'TimeLog_' + getDayText(which_day) + '.csv'
    # csvファイルを生成
    writeFile(output_file, entries, encoding)
    print("file created: {}".format(output_file))

    # print(entries)

if __name__ == '__main__':
    main()