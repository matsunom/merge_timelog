import os
import datetime
import sys
import glob
import csv
import pprint


# 日時のテキストを取得する
def getDayText(day):
    dt_today = datetime.date.today()
    if day == 'today':
        day_text = dt_today.strftime('%Y-%m-%d')
    elif day == 'yesterday':
        dt_yesterday = dt_today - datetime.timedelta(days=1)
        day_text = dt_yesterday.strftime('%Y-%m-%d')
    return day_text

# ファイル名の文字列を取得
def getFname(day):
    dt_today = datetime.date.today()
    if day == 'today':
        toggl_file = 'Toggl_time_entries_' + dt_today.strftime('%Y-%m-%d') + '_to_' + dt_today.strftime('%Y-%m-%d')
        trackingtime_file = 'TrackingTime ' + dt_today.strftime('%b %d,%Y') + '-' + dt_today.strftime('%b %d,%Y')
    elif day == 'yesterday':
        dt_yesterday = dt_today - datetime.timedelta(days=1)
        toggl_file = 'Toggl_time_entries_' + dt_yesterday.strftime('%Y-%m-%d') + '_to_' + dt_yesterday.strftime('%Y-%m-%d')
        trackingtime_file = 'TrackingTime ' + dt_yesterday.strftime('%b %d,%Y') + '-' + dt_yesterday.strftime('%b %d,%Y')
    else:
        print('Please select today or yesterday.')
        sys.exit()
    return [toggl_file, trackingtime_file]

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
    entries = [[line.get('Description'), timeConvert_for_Toggl(line.get('Start time')), timeConvert_for_Toggl(line.get('End time'))] for line in lines]
    return entries

def readTrackingTime(lines):
    entries = [[line.get('Task'), timeConvert_for_TrackingTime(line.get('From')), timeConvert_for_TrackingTime(line.get('To'))] for line in lines]
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
    time = str(time_h) + ":" + time_m
    return time

# take the second element for sort
def take_second(elem):
    return elem[1]

def writeFile(fname, entries):
    with open(fname, 'w') as output_csv:
        header = ['Name', 'From', 'To']
        writer = csv.writer(output_csv)
        writer.writerow(header)
        writer.writerows(entries)

def calcAmountTimeEntries(entries):
    amount_entry_time = datetime.timedelta(hours=0, minutes=0) # 初期化
    for entry in entries:
        start_time = entry[1].split(":")
        start_time = datetime.timedelta(hours=int(start_time[0]), minutes=int(start_time[1]))
        end_time = entry[2].split(":")
        end_time = datetime.timedelta(hours=int(end_time[0]), minutes=int(end_time[1]))   
        duration = end_time - start_time
        amount_entry_time += duration
    return amount_entry_time

def main():
    # 引数処理
    try:
        which_day = sys.argv[1]
    except IndexError:
        print('Please select today or yesterday.')
        sys.exit()
    # get file name today or yesterday
    fnames = getFname(which_day)
    dirpath = '' # 絶対パス　'/Users/username/Downloads/'
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
    entries.sort(key=lambda x: x[1])

    output_file = dirpath + 'TimeLog_' + getDayText(which_day) + '.csv'
    
    writeFile(output_file, entries)
    
    num_entries = len(entries)
    amount_entry_time = '時間'.join(str(calcAmountTimeEntries(entries)).split(':')[:-1]) + '分'
    

    print("{} entries. {} work.".format(num_entries, amount_entry_time))
    print("file created: {}".format(output_file))

if __name__ == '__main__':
    main()