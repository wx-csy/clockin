import web
import sqlite3 as db
import time

def logging() :
    dbconn = db.connect('db.sqlite3')
    cur = dbconn.cursor()
    cur.execute('''
        INSERT INTO log (timestamp, ip, url, query, method, status, cookie)
        VALUES (?,?,?,?,?,?,?)
    ''', [int(time.time()), web.ctx['ip'], web.url(), web.ctx['query'], 
        web.ctx['method'], web.ctx['status'], web.cookies().get('checkin-cookie-key')])
    dbconn.commit()
    dbconn.close()

def require_logging(method) :
    def _impl(*params) :
        ret = method(*params)
        logging()
        return ret
    return _impl