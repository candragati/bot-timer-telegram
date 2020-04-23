
from modul.kamus import kamus

def help(update,context):
    update.message.reply_text(kamus("cmd_help"))

def help_timer(update,context):
    update.message.reply_text(kamus("cmd_help_timer"))

def help_qotd(update,context):
    update.message.reply_text(kamus("cmd_help_qotd"))

def help_jadwal_sholat(update,context):
    update.message.reply_text(kamus("cmd_help_jadwal_sholat"))