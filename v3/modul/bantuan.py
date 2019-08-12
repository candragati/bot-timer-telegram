from telegram import Bot, Update
from modul.kamus import kamus
from modul.kamus import kamus

def help(bot:Bot,update:Update):
    update.message.reply_text(kamus("cmd_help"))

def help_timer(bot:Bot,update:Update):
    update.message.reply_text(kamus("cmd_help_timer"))

def help_qotd(bot:Bot,update:Update):
    update.message.reply_text(kamus("cmd_help_qotd"))

def help_jadwal_sholat(bot:Bot,update:Update):
    update.message.reply_text(kamus("cmd_help_jadwal_sholat"))