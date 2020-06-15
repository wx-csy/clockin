#!/usr/bin/env python3
import abc
import time
import uuid
import sqlite3 as db

import web
from web import form
from logger import require_logging
import ad

render = web.template.render('templates/', base='layout', globals={
    'zip' : zip,
    'time': time, 
    'get_ad': ad.get_ad,
})


def temp_validator(temp) :
    if not isinstance(temp, str) or len(temp) > 5 :
        return False
    try :
        val = float(temp)
        return 35.0 <= val <= 42.0
    except ValueError :
        return False

MorningForm = form.Form(
    form.Hidden('date', value=''),
    form.Textbox('学号', id='sid', maxlength=16, value=''), 
    form.Textbox('姓名', id='name', maxlength=8, value=''),
    form.Textbox('体温', id='temp', value=''),
    form.Checkbox('确认已在APP打卡', id='appchecked', value='t', checked=True),
)

NoonForm = form.Form( 
    form.Hidden('date', value=''),
    form.Textbox('学号', id='sid', maxlength=16, value=''), 
    form.Textbox('姓名', id='name', maxlength=8, value=''),
    form.Textbox('体温', id='temp', value=''),
)

EveningForm = form.Form( 
    form.Hidden('date', value=''),
    form.Textbox('学号', id='sid', maxlength=16, value=''), 
    form.Textbox('姓名', id='name', maxlength=8, value=''),
    form.Textbox('体温', id='temp', value=''),
    form.Checkbox('确认已回宿舍', id='checked', value='t', checked=True),
)

formlist = [None, MorningForm, NoonForm, EveningForm]

def submit(table, kv) :
    dbconn = db.connect('db.sqlite3')
    cur = dbconn.cursor()
    sid = kv['sid']
    name = kv['name']
    date = kv['date']
    temp = kv['temp']
    if not temp_validator(temp) :
        return '体温值非法'
    if date != time.strftime('%Y%m%d') :
        return '打卡日期错误'
    kv['temp'] = float(temp)
    del kv['name']
    kv['timestamp'] = int(time.time())
    cur.execute('SELECT * FROM students WHERE sid=? AND name=?', [sid, name])
    if cur.fetchone() is not None : # auth success
        cur.execute('DELETE FROM {} WHERE sid=? AND date=?'.format(table), [sid, date])
        keys, values = zip(*kv.items())
        cur.execute('INSERT INTO {} ({}) VALUES ({})'
            .format(table, ','.join(keys) , ','.join(['?']*len(values))),
            values)
        if cur.rowcount < 1 :
            return '数据库写入失败'

        cookie_key = web.cookies().get('checkin-cookie-key')

        if cookie_key is not None :
            cur.execute('UPDATE cookies SET sid=? WHERE id=?', [sid, cookie_key])
            if cur.rowcount < 1 :
                cookie_key = None

        if cookie_key is None :
            cookie_key = str(uuid.uuid4())
            result = cur.execute('INSERT INTO cookies (id, sid) VALUES (?, ?)', [cookie_key, sid])

        dbconn.commit()
        dbconn.close()
        web.setcookie('checkin-cookie-key', cookie_key, expires=604800)
        return None
    else : # auth failure
        dbconn.close()
        return '学号或姓名输入错误'

class FormProcessor(abc.ABC):
    @abc.abstractmethod
    def getkv(self) -> dict :
        pass

    @require_logging
    def POST(self) :
        ret = submit(self.table, self.getkv())
        if ret is None :
            return render.success()
        else :
            return render.fail(ret)

class Morning(FormProcessor):
    def __init__(self) :
        self.table = 'morning'
    
    def getkv(self): 
        form = MorningForm()
        form.validates()
        return {
            'sid': form['学号'].get_value(),
            'name': form['姓名'].get_value(),
            'date': form['date'].get_value(),
            'temp': form['体温'].get_value(),
            'checked': form['确认已在APP打卡'].get_value(),
        }

class Noon(FormProcessor):
    def __init__(self) :
        self.table = 'noon'

    def getkv(self): 
        form = NoonForm()
        form.validates()
        return {
            'sid': form['学号'].get_value(),
            'name': form['姓名'].get_value(),
            'date': form['date'].get_value(),
            'temp': form['体温'].get_value(),
        }

class Evening(FormProcessor):
    def __init__(self) :
        self.table = 'evening'

    def getkv(self): 
        form = EveningForm()
        form.validates()
        return {
            'sid': form['学号'].get_value(),
            'name': form['姓名'].get_value(),
            'date': form['date'].get_value(),
            'temp': form['体温'].get_value(),
            'checked': form['确认已回宿舍'].get_value(),
        }