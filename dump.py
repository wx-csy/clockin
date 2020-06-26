#!/usr/bin/env python3

import sqlite3 as db
import zipfile, csv, io, time

dbconn = db.connect('db.sqlite3')
cur = dbconn.cursor()
cur.execute('SELECT date FROM morning')
res = cur.fetchall()
cur.execute('SELECT date FROM noon')
res += cur.fetchall()
cur.execute('SELECT date FROM evening')
res += cur.fetchall()

identity = lambda x : '' if x is None else str(x)
checked_fmt = lambda x : '' if x is None else 'YN'[int(x)]
time_fmt = lambda x : '' if x is None else time.strftime('%H:%M', time.localtime(int(x)))
fmts = [identity, identity, identity, identity, checked_fmt, time_fmt, identity, time_fmt,
    identity, checked_fmt, time_fmt]

with zipfile.ZipFile('record.zip', 'w') as myzip :
    for date in set(list(zip(*res))[0]) :
        cur.execute('''
            SELECT students.sid, students.name, students.major, 
                morning.temp, morning.checked, morning.timestamp,
                noon.temp, noon.timestamp,
                evening.temp, evening.checked, evening.timestamp
            FROM students 
            LEFT OUTER JOIN morning ON students.sid=morning.sid AND morning.date=?
            LEFT OUTER JOIN noon ON students.sid=noon.sid AND noon.date=?
            LEFT OUTER JOIN evening ON students.sid=evening.sid AND evening.date=?
            ORDER BY students.major, students.sid ASC
        ''', [date] * 3)
        dataset = cur.fetchall()
        fd = io.StringIO()
        csvfile = csv.writer(fd)
        csvfile.writerow(('学号', '姓名', '早温', '早签', '早时', '午温', '午时', '晚温', '晚归', '晚时'))
        for row in dataset :
            tup = []
            for fn, val in zip(fmts, row) :
                tup.append(fn(val))
            csvfile.writerow(tup)
        myzip.writestr(date + '.csv', fd.getvalue().encode('gbk'))
        fd.close()

dbconn.close()