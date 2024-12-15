import sqlite3
from telegram.ext import Updater

db          = sqlite3.connect("database", check_same_thread = False)
cur         = db.cursor()
class Config():
    BOT_ID = <YOUR_BOT_ID> # @tehgebot
    TOKEN   = "<YOUR_BOT_TOKEN>" # @tehgebot
    APINEWS = "<YOUR_API_NEWS>"
    
    updater = Updater(TOKEN,use_context = True,workers = 8,request_kwargs = {'read_timeout':600,'connect_timeout':600})
    dp = updater.dispatcher
    
    
def eksekusi(sql):
    cur.execute(sql)
    lineData = cur.fetchall()
    totData = len(lineData)
    return lineData, totData


