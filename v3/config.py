import sqlite3

db = sqlite3.connect("database", check_same_thread = False)
cur = db.cursor()

class Config():
    TOKEN = "609147123:AAGxNzS2-GTvJKiTiU-HuAHkMqOruI9Teiw"

def eksekusi(sql):
    cur.execute(sql)
    lineData = cur.fetchall()
    totData = len(lineData)
    return lineData, totData
