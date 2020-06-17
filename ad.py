import sqlite3 as db
import random
import time

def get_ad() :
    dbconn = db.connect('db.sqlite3')
    cur = dbconn.cursor()
    cur.execute('''
        SELECT content FROM ads
        WHERE date_begin <= ? AND date_end >= ? AND visible = 1
    ''', [time.strftime('%Y%m%d')] * 2)
    ret = cur.fetchall()
    dbconn.close()
    if not ret :
        return ''
    return random.choice(ret)[0]
    