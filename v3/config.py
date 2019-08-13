import sqlite3

db = sqlite3.connect("database", check_same_thread = False)
cur = db.cursor()

class Config():
    TOKEN = "<YOUR TOKEN>"

def eksekusi(sql):
    cur.execute(sql)
    lineData = cur.fetchall()
    totData = len(lineData)
    return lineData, totData
