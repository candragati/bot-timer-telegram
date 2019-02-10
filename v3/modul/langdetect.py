from telegram import Bot, Update
from telegram import ParseMode
from telegram.utils.helpers import escape_markdown
from config import *
from modul.kamus import kamus
from telegram import MessageEntity
from googletrans import Translator
import datetime
import re

def echo(bot:Bot,update:Update):
    #sudah nongol    
    message = re.sub(r"(?:\@|https?\://)\S+", "", update.message["text"])
    translator = Translator()
    a = translator.detect(message).lang
    sekarang = datetime.datetime.now()
    hari = datetime.datetime.strftime(sekarang.date(),"%a")
    if hari == 'Sun' and a != 'en':
        update.message.reply_text("Please use english in sunday only.")
            
