from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode
from telegram.utils.helpers import escape_markdown
from config import *
from modul.kamus import kamus
from modul import afk
from telegram import MessageEntity
from googletrans import Translator
import datetime
import re
import random
import pprint
from telegram import PhotoSize, UserProfilePhotos

# import pymysql
# conn = pymysql.connect(host='192.168.50.2',port = 9999, user='bot_telegram_s5', passwd='aBd%2ap^NULL_ptr_d~@#', db='bot_telegram_s5')

teks = (
    "Please use only English in Sunday.",
    "Its seems you didnt read the rules",
    "Dont forget to use English today",
    "Please read our rules!",
    "Just one day to use english",
    "Should i kick your ass?",
    "If you join this group, you must follow our rules",
    "Use english, and i will stop reply your chat again",
    "Hmm.... you dont speak english. Its sunday!",
    "Pak, pake english pak",
    "Speak english mblo"
    )


def echo(bot:Bot,update:Update): 
    # pprint.pprint (update.message.to_dict())
    try:
        fwd_username =  update.message["forward_from"]["username"]
        fwd_name     =  '%s %s'%(update.message["forward_from"]["first_name"],update.message["forward_from"]["last_name"])
        cek_forward =  1
    except:                        
        fwd_username =  None
        fwd_name     =  None
        cek_forward =  0

    
    chat            = update.effective_chat  # type: Optional[Chat]
    user            = update.effective_user  # type: Optional[User]
    message         = update.effective_message  # type: Optional[Message]    
    chat_id         = message.chat.id
    chat_type       = message.chat.type
    message_id      = message.message_id
    # pprint.pprint(update.message.to_dict())
    
    from_user_name  = message.from_user.username
    from_user_id    = message.from_user.id    
    member          = chat.get_member(from_user_id)
    date            = message.date
    
    try:
        msg_text        = message.text.encode("unicode_escape")
    except:
        msg_text        = message.text
    from_first_name = message.from_user.first_name
    from_last_name  = message.from_user.last_name

    
    if from_last_name is None:        
        nama        = "%s"%(from_first_name)
    else:
        nama        = "%s %s"%(from_first_name, from_last_name)
        

    sql             = "SELECT english_day FROM setting WHERE chat_id = '%s'"%chat_id
    bar, jum        = eksekusi(sql)
    if jum == 0:
        pass
    else:                
        try:
            if not message.caption:
                return
            text = message.text.encode('ascii', 'ignore').decode('ascii') or message.caption.encode('ascii', 'ignore').decode('ascii')
            if not text:
                return
            message = re.sub(r"(?:\@|https?\://)\S+", "", text)
            message = re.sub(r'".*?"', "", text)
            message = re.sub(r'/.*', "", text)
            message = re.sub(r"\b[A-Z\.]{2,}s?\b", "", text)
            translator = Translator()
            a           = translator.detect(message).lang            
            sekarang    = datetime.datetime.now()
            tanggal     = '{:%Y-%m-%d}'.format(sekarang)
            hari        = datetime.datetime.strftime(sekarang.date(),"%a")
            if hari == bar[0][0] and a != 'en':
                cek = "SELECT user_id, mute FROM blacklist WHERE chat_id = '%s' AND user_id = '%s' AND tanggal = '%s'"%(chat_id,from_user_id,tanggal)
                bar, jum = eksekusi(cek)
                if jum == 0:
                    infut = "INSERT INTO blacklist (chat_id, chat_type, user_id, user_name, mute,tanggal) VALUES ('%s','%s','%s','%s',0,'%s')"%(chat_id, chat_type, from_user_id, from_user_name,tanggal)
                    cur.execute(infut)
                    db.commit()
                    bot.send_message(chat_id,  random.choice(teks), reply_to_message_id=message_id)
                elif jum != 0 and bar[0][1] < 3:
                    infut = "UPDATE blacklist SET mute = mute+1 WHERE chat_id = '%s' AND user_id = '%s' AND tanggal = '%s'"%(chat_id, from_user_id,tanggal)
                    cur.execute(infut)
                    db.commit()
                    sisa = 2-bar[0][1]
                    if sisa == 0:
                        if member.status == 'administrator' or member.status == 'creator':
                            bot.send_message(
                                chat_id, 
                                'Your next-non-english chat will be deleted.', 
                                reply_to_message_id=message_id)
                        else:
                            bot.send_message(
                                chat_id, 
                                'Your next-non-english chat will make you muted to this group for 24 hours.', 
                                reply_to_message_id=message_id)
                    else:
                        bot.send_message(
                                chat_id, 
                                'You have %s remaining'%(sisa), 
                                reply_to_message_id=message_id)
                elif jum!=0 and bar[0][1]==3:
                    if member.status == 'administrator' or member.status == 'creator':
                        update.effective_message.delete()
                    elif member.can_send_messages is None or member.can_send_messages:
                        mutetime    = datetime.datetime.now()+datetime.timedelta(hours=24)
                        tanggalmute = sekarang = '{:%Y-%m-%d %H:%M:%S}'.format(mutetime)
                        infut       = "UPDATE blacklist SET mute_sampe_tanggal = '%s' WHERE chat_id = '%s' AND user_id = '%s' AND tanggal = '%s'"%(tanggalmute,chat_id, from_user_id,tanggal)
                        cur.execute(infut)
                        db.commit()
                        bot.restrict_chat_member(chat_id, from_user_id, until_date=mutetime, can_send_messages=False)
                        bot.send_message(chat_id, "Restricted until {}!".format(tanggalmute), reply_to_message_id=message_id) 
                    else:
                        bot.send_message(chat_id, "Already muted.", reply_to_message_id=message_id)
        except Exception as a:
            bot.send_message(chat_id,str(a), reply_to_message_id=message_id)
        
    
    
    
        
        # print (update.message.sticker)
        # sticker_id = update.message.sticker.file_id
# dp = Config.dp
# dp.add_handler(MessageHandler(Filters.text, echo,edited_updates=True))
