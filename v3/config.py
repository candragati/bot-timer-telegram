import sqlite3
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

db          = sqlite3.connect("database", check_same_thread = False)
cur         = db.cursor()
class Config():
    BOT_ID = 609147123 # @srabatsrobot
    # BOT_ID = 751837159 # @tehgebot
    TOKEN = "609147123:AAGxNzS2-GTvJKiTiU-HuAHkMqOruI9Teiw" # @srabatsrobot
    # TOKEN   = "751837159:AAG8jttm85vQg-yDv_25yuVLZEOET8SMNoE" # @tehgebot
    APINEWS = "cd0811abe6804a4f8bbd7d095e402737"
    updater = Updater(TOKEN,workers = 8,request_kwargs = {'read_timeout':600,'connect_timeout':600})
    dp = updater.dispatcher
    
    
def eksekusi(sql):
    cur.execute(sql)
    lineData = cur.fetchall()
    totData = len(lineData)
    return lineData, totData


