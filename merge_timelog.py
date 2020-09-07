import sys
import datetime
import glob
import csv

# 日時のテキストを取得する
def getDayText(day):
    dt_today = datetime.date.today()
    if day == 'today':
        day_text = dt_today.strftime('%Y-%m-%d')
    elif day == 'yesterday' or day == 'yesterday~':
        dt_yesterday = dt_today - datetime.timedelta(days=1)
        day_text = dt_yesterday.strftime('%Y-%m-%d')
    return day_text

# ファイル名の文字列を取得
def getFname(day):
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
    else:
        print('Please select today or yesterday.')
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

def changeDay(entries, start_hour=None):
    # 引数による開始時刻の指定が無ければ、初めの6時間以上の開きがあった場合のエントリから取り出す
    if start_hour == None:
        index_num = 0
        for i, entry in enumerate(entries):
            # 1回目は2つの比較ができないのでスキップ
            if i == 0:
                start_time1 = int(entry[1].split(":")[0])
                continue
            start_time2 = int(entry[1].split(":")[0])
            if (start_time2 - start_time1) >= 6:
                index_num = i
                break
            start_time1 = start_time2
        return entries[index_num:]
    # 引数による開始時刻の指定がある場合は、その時刻よりあとのエントリを取り出す
    else:
        index_num = 0
        for i, entry in enumerate(entries):
            start_time = int(entry[1].split(":")[0])
            if start_time >= start_hour:
                index_num = i
                break
        return entries[index_num:]

def writeFile(fname, entries, encoding):
    entries = [entry[:3] for entry in entries]
    try:
        with open(fname, 'w', encoding=encoding) as output_csv:
            header = ['Name', 'From', 'To']
            writer = csv.writer(output_csv)
            writer.writerow(header)
            writer.writerows(entries)
    except LookupError:
        sys.exit()

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

def main():
    # 引数処理
    args = sys.argv
    try:
        which_day = args[1]
    except IndexError:
        print('Please select today or yesterday.')
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
                encoding = arg
                if encoding not in ['cp932', 'utf8']:
                    print('csv encoding error and select utf8 or cp932(SHIFT-JIS).')
                    sys.exit()

    # ファイル名の取得
    fnames = getFname(which_day)
    dirpath = '/Users/username/Downloads/'
    matchpath = dirpath + '*.csv'
    csv_names = glob.glob(matchpath)
    fpaths = []
    for fname in fnames:
        for csv_name in csv_names:
            if csv_name.startswith(dirpath + fname):
                fpaths.append(csv_name)
    if not fpaths:
        print('No Time Record Files in ~/Downloads ')
        sys.exit()

    entries = []
    for fpath in fpaths:
        entries.extend(readFile(fpath))

    # エントリーを from をキーにして並び替える
    entries.sort(key=lambda x: (x[3], x[1]))

    # 1日の開始時刻フィルダーをかける
    entries = changeDay(entries, start_hour)

    # ファイル名の生成
    output_file = dirpath + 'TimeLog_' + getDayText(which_day) + '.csv'
    #csvファイルを生成
    writeFile(output_file, entries, encoding)
    
    # エントリー数と活動時間を出力
    num_entries = len(entries)
    amount_entry_time = '時間'.join(str(calcAmountTimeEntries(entries)).split(':')[:-1]) + '分'
    print("{} entries. {} work.".format(num_entries, amount_entry_time))
    print("file created: {}".format(output_file))

if __name__ == '__main__':
    main()