#!/usr/bin/env python3

import time
import sqlite3 as db

import web

import ad
import forms
from forms import Morning, Noon, Evening
from logger import require_logging

render = web.template.render('templates/', base='layout', globals={
    'zip' : zip,
    'time': time, 
    'get_ad': ad.get_ad,
})

urls = (
    '/', 'Index',
    '/clockin', 'ClockIn',
    '/auth', 'Authentication',
    '/clockin/morning', 'Morning',
    '/clockin/noon', 'Noon',
    '/clockin/evening', 'Evening',
    '/clockin/readme', 'Readme',
    '/clockin/stat/(.+)', 'Statistics',
)
app = web.application(urls, globals())

def get_current_form() :
    hr = time.localtime().tm_hour
    if 6 <= hr < 12 : return 1
    if 12 <= hr < 18 : return 2
    if 18 <= hr : return 3
    return 0

def get_default_values_by_cookie(cookie_key) :
    if cookie_key is None :
        return '', ''
    dbconn = db.connect('db.sqlite3')
    cur = dbconn.cursor()
    cur.execute('''
        SELECT students.sid, students.name 
        FROM cookies 
        INNER JOIN students ON cookies.sid=students.sid 
        WHERE cookies.id=?
    ''', [cookie_key])
    row = cur.fetchone()
    if row is None :
        sid, name = '', ''
    else :
        sid, name = row[0], row[1]
    dbconn.close()
    return sid, name

class Index:
    def GET(self):
        web.seeother('/clockin')

class ClockIn: 
    @require_logging
    def GET(self): 
        form_id = get_current_form()
        if form_id :
            theform = forms.formlist[form_id]()
            sid, name = get_default_values_by_cookie(web.cookies().get('checkin-cookie-key'))
            theform['学号'].value = sid
            theform['姓名'].value = name
            theform['date'].value = time.strftime('%Y%m%d')
            return render.form(theform, form_id)
        else :
            return render.goodnight()

class Statistics:
    @require_logging
    def GET(self, date): 
        dbconn = db.connect('db.sqlite3')
        cur = dbconn.cursor()
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
        ''', [date, date, date])
        data = cur.fetchall()
        dbconn.close()
        identity = lambda x : '' if x is None else x
        temp_fmt = lambda x : '' if x is None else'{}℃'.format(x) if float(x) < 37.3 else '<span style="color:#E53333;">{}℃</span>'.format(x)
        checked_fmt = lambda x : '' if x is None else '❌✔️'[int(x)]
        time_fmt = lambda x : '' if x is None else time.strftime('%H:%M', time.localtime(int(x)))
        return render.statistics(data, date, 
            [identity, identity, identity, temp_fmt, checked_fmt, time_fmt, temp_fmt, time_fmt,
             temp_fmt, checked_fmt, time_fmt])

class Readme:
    @require_logging
    def GET(self):
        return render.readme() 

if __name__=="__main__":
    # web.internalerror = web.debugerror
    app.run()
