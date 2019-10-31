#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""Simple Bot to send timed Telegram messages.

# This program is dedicated to the public domain under the CC0 license.

This Bot uses the Updater class to handle the bot and the JobQueue to send
timed messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Alarm Bot example, sends a message after a set time.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram.ext import Updater, CommandHandler
from telegram import ParseMode
import logging
import datetime
import re
import time

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('pake /set <detik> <pesan> untuk timer')

def help(bot, update):
    update.message.reply_text('pake /set <detik> <pesan> untuk timer\n/unset untuk batal')


def alarm(bot, job):
    """Send the alarm message."""
    pesan = str(job.name[0])
    nama = str(job.name[1])
    bot.send_message(job.context,parse_mode=ParseMode.MARKDOWN, text='{} - _{}_'.format(pesan,nama))

def set_tanggal(bot, update, args, job_queue, chat_data):
    try:
        current = datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=7)
        hitung(bot,update,args,job_queue, chat_data,int((datetime.datetime.strptime("%s %s"%(args[0], args[1]),"%Y-%m-%d %H:%M:%S")-current).total_seconds())+1)
    except:
        update.message.reply_text('perintah: /set <detik> <pesan>')

def set_jam(bot, update, args, job_queue, chat_data):
    now = '{:%Y-%m-%d}'.format(datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=7))
    try:
        current = datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=7)
        hitung(bot,update,args,job_queue, chat_data,int((datetime.datetime.strptime(now+" "+args[0],"%Y-%m-%d %H:%M:%S")-current).total_seconds())+1)
    except:
        set_tanggal(bot, update, args, job_queue, chat_data)


def set_timer(bot, update, args, job_queue, chat_data):
    """Add a job to the queue."""


    try:
        # args[0] should contain the time for the timer in seconds
        huruf = ''
        try:
            angka = re.match("([0-9]+)([a-zA-Z]+)",args[0]).group(1)
            huruf = re.match("([0-9]+)([a-zA-Z]+)",args[0]).group(2)
        except:
            angka = args[0]
            satuan = 1

        if huruf == 's' or huruf == 'd' or huruf == '':
            satuan = 1
        elif huruf == 'm':
            satuan = 60
        elif huruf == 'h' or huruf == 'j':
            satuan = 3600
        else:
            update.message.reply_text('format salah. \ns atau d = untuk detik\nm = untuk menit\nh atau j = untuk jam')
            return

        hitung(bot,update,args,job_queue, chat_data,int(angka)*satuan)
    except (IndexError, ValueError):
        set_jam(bot, update, args, job_queue, chat_data)

def hitung(bot,update,args,job_queue, chat_data,due):
    chat_id = update.message.chat_id
    if due < 0:
        update.message.reply_text('Maap. Kita gak bisa kembali ke masa lalu.')
        return

    # Add job to queue
    pesan = ' '.join(update.message.text.split(" ")[2:])
    match = re.match(r'^[A-Za-z0-9 ?!&,.:]*$', pesan )
    if match :
        nama =  (update.message.from_user.username)
        teks = [pesan, nama]
        job = job_queue.run_once(alarm, due, context=chat_id, name = teks)

        chat_data['job'] = job
        sekarang = '{:%H:%M:%S}'.format(datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=7))
        waktu = '{:%H:%M:%S}'.format(datetime.datetime.now()+datetime.timedelta(seconds=due,hours=7))

        update.message.reply_text('waktu saat ini : %s\nTimer berhasil di set pada pukul %s'%(sekarang, waktu))
    else:
        update.message.reply_text('incorrect string')







def unset(bot, update, chat_data):
    """Remove the job if the user changed their mind."""
    if 'job' not in chat_data:
        update.message.reply_text('Gak ada timer yang di set')
        return

    job = chat_data['job']
    job.schedule_removal()
    del chat_data['job']

    update.message.reply_text('Timer berhasil di batalin!')


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" menyebabkan terjadinya error "%s"', update, error)


def main():
    """Run bot."""
    updater = Updater("<TOKENBOT>")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("set", set_timer,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("unset", unset, pass_chat_data=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until you press Ctrl-C or the process receives SIGINT, SIGTERM or
    # SIGABRT. This should be used most of the time, since start_polling() is
    # non-blocking and will stop the bot gracefully.

    updater.idle()


if __name__ == '__main__':
    main()
