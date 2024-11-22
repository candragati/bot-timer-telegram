
from config import *
from googletrans import Translator
import datetime
import re
import random
import traceback
import threading
import emoji
from telegram import ChatPermissions

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

lock = threading.Lock()
def echo(update,context):
    bot             = context.bot    
    chat            = update.effective_chat  # type: Optional[Chat]
    # user            = update.effective_user  # type: Optional[User]
    message         = update.effective_message  # type: Optional[Message]    
    chat_id         = message.chat.id
    message_id      = message.message_id

    lock.acquire(True)
    try:        
        sql             = "SELECT english_day FROM setting WHERE chat_id = '%s'"%chat_id
        bar, jum        = eksekusi(sql)
        if jum == 0:
            pass
        else:               
            try:
                chat_type       = message.chat.type
                from_user_name  = message.from_user.username
                from_user_id    = message.from_user.id
                member          = chat.get_member(from_user_id)
                sekarang        = message.date+datetime.timedelta(hours=7)

                translator = Translator()
                try:
                    message = re.sub(r"(?:\@|https?\://)\S+", "", message.text.encode().decode('utf-8'))                    
                except:
                    if not message.caption:
                        return
                    elif message.caption ==None:
                        message = "this is caption"
                    else:
                        message = re.sub(r"(?:\@|https?\://)\S+", "", message.caption.encode().decode('utf-8'))
                        # message = message.caption.encode('ascii', 'ignore').decode('ascii')
                message = re.sub(r'".*?"', "", message)
                message = re.sub(r'/.*', "", message)
                message = re.sub(r"\b[A-Z\.]{2,}s?\b", "", message)
                try:
                    a           = translator.detect(str(message)).lang
                    if len(a) == 0:return
                    # sekarang    = datetime.datetime.now()
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
                                try:
                                    update.effective_message.delete()
                                except:
                                    bot.send_message(
                                        chat_id, 
                                        'Gak bisa di delete nih',
                                        reply_to_message_id=message_id)
                            elif member.can_send_messages is None or member.can_send_messages:
                                mutetime    = datetime.datetime.now()+datetime.timedelta(hours=24)
                                tanggalmute = sekarang = '{:%Y-%m-%d %H:%M:%S}'.format(mutetime)
                                infut       = "UPDATE blacklist SET mute_sampe_tanggal = '%s' WHERE chat_id = '%s' AND user_id = '%s' AND tanggal = '%s'"%(tanggalmute,chat_id, from_user_id,tanggal)
                                cur.execute(infut)
                                db.commit()
                                b = ChatPermissions(canSendMessages=False, canSendMediaMessages=False, canSendPolls=False, canSendOtherMessages=False, canAddWebPagePreviews=False, canChangeInfo=False, canInviteUsers=False, canPinMessages=False)
                                bot.restrict_chat_member(chat_id, from_user_id,b, until_date=mutetime, can_send_messages=False)
                                bot.send_message(chat_id, "Restricted until {}!".format(tanggalmute), reply_to_message_id=message_id) 
                            else:
                                bot.send_message(chat_id, "Already muted.", reply_to_message_id=message_id)
                except:
                    # print (traceback.format_exc())
                    pass # belum update ke v13, coba hapus demojize
            except:
                bot.send_message(chat_id,str(traceback.format_exc()), reply_to_message_id=message_id)
    finally:
        lock.release()        
    
    
    
        
        # print (update.message.sticker)
        # sticker_id = update.message.sticker.file_id
# dp = Config.dp
# dp.add_handler(MessageHandler(Filters.text, echo,edited_updates=True))
