import sqlite3
import os
from telegram.ext import Updater
from dotenv import load_dotenv

load_dotenv()

db          = sqlite3.connect("database", check_same_thread = False)
cur         = db.cursor()
class Config():
    TOKEN    = os.environ.get('TOKEN', None)
    BOT_ID   = os.environ.get('BOT_ID', None) 
    APINEWS  = os.environ.get('APINEWS', None)
    ICETEA   = os.environ.get('ICETEA', None)
    BOT_CHAT_ID = os.environ.get('BOT_CHAT_ID', None)
    updater  = Updater(TOKEN,use_context = True,workers = 8,request_kwargs = {'read_timeout':600,'connect_timeout':600})
    dp = updater.dispatcher
    
    
def eksekusi(sql):
    cur.execute(sql)
    lineData = cur.fetchall()
    totData = len(lineData)
    return lineData, totData


