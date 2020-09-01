# merge_timelog
This script to merge time Toggl detailed report and TrackingTime report per day.
Input is multiple today's or yesterday's reports and output is a merged report formatted csv. Also we can get number of task entries and amount of time of entries.

This script treats one day report when yesterday or today.

This script pick 'discription', 'start_time' and 'end_time' from Toggl detailed report.
This script pick 'Task', 'From' and 'To' from TrackingTime report.

Name of log file.
- Toggl_time_entries_2020-08-24_to_2020-08-30.csv
- TrackingTime Aug 26,2020-Aug 26,2020 - 25523.csv

`python merge_timelog.py yesterday`

`17 entries. 8時間24分 work.`

`file created: /Users/username/Downloads/TimeLog_2020-08-26.csv`

Before you use this script, you need to change dirpath on 98th line in merge_timelog.py.

# command args
`python merge_timelog.py today`

This option search log files in dirpath the period between today to today.

`python merge_timelog.py yesterday`

This option search log files in dirpath the period between yesterday to yesterday.

`python merge_timelog.py yesterday~`

This option search log files in dirpath the period between yesterday to today.

# Also set export csv's encoding, default is cp932(SHIFT-JIS), if you use utf8, set 2 args like below.

`python merge_timelog.py yesterday utf8`