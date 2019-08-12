from telegram import Bot, Update
from telegram import ParseMode
from telegram.utils.helpers import escape_markdown
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from config import *
from modul.kamus import kamus
from telegram import MessageEntity


def set_afk(bot:Bot,update:Update):
    m = update.effective_message            
    teks =  m.text.split(None,1)
    if len(teks) == 2:        
        try:
            chat_id = str(update.message["chat"]["id"])
            chat_type = update.message["chat"]["type"]
            user_id = str(update.message.from_user.id)
            user_name = update.message.from_user.username
            cek = "SELECT user_name,teks FROM afk WHERE chat_id='%s' AND user_id='%s'"%(chat_id, user_id)
            bar, jum = eksekusi(cek)
            if jum == 0:            
                sql = "INSERT INTO afk (chat_id, chat_type, user_id, user_name, teks,hapus) VALUES (?,?,?,?,?,0)"
                cur.execute(sql,(chat_id, chat_type, user_id, user_name, teks[1]))
            else:
                sql = "UPDATE afk SET teks = ?, hapus = ? WHERE chat_id = ? AND user_id = ?"
                cur.execute(sql,(teks[1],'0',chat_id,user_id))
            db.commit()
            update.message.reply_text("%s sekarang AFK"%user_name)
        except Exception as e:
            update.message.reply_text("ketik /afk <alasan anda>\n%s"%e)

def sudah_nongol(bot:Bot,update:Update):    
    message         = update.effective_message  # type: Optional[Message]    
    chat_id         = message.chat.id    
    from_user_name  = message.from_user.username
    from_user_id    = message.from_user.id    
    # echo afk
    cek         = "SELECT user_name FROM afk WHERE chat_id='%s' AND user_id='%s' AND hapus = 0"%(chat_id, from_user_id)
    bar, jum    = eksekusi(cek)
    if jum == 0:
        pass
    else:
        sql = "UPDATE afk SET hapus = 1 WHERE chat_id = ? AND user_id = ?"
        cur.execute(sql,(chat_id,from_user_id))
        db.commit()
        update.message.reply_text("%s sudah nongol lagi"%from_user_name)

def reply_afk(bot:Bot, update:Update):
    # Dari mention    
    message     = update.effective_message        
    chat_id         = message.chat.id    
    entities    = message.parse_entities([MessageEntity.TEXT_MENTION, MessageEntity.MENTION])    
    if message.entities and entities:        
        for ent in entities:            
            if ent.type == MessageEntity.TEXT_MENTION:
                user_id = ent.user.id
            elif ent.type == MessageEntity.MENTION:
                user_id = (message.text[ent.offset:ent.offset + ent.length])
            if not user_id:
                return            
            mention = user_id.replace("@","")
            cek     = "SELECT teks FROM afk WHERE chat_id='%s' AND user_name='%s' AND hapus = 0"%(chat_id, mention)
            bar, jum = eksekusi(cek)
            if jum == 0:
                pass
            else:
                update.message.reply_text("%s gak online, dia lagi %s"%(mention,bar[0][0]))
            

    # Dari reply
    try:
        r_user_name = message.reply_to_message.from_user.username
        cek         = "SELECT teks FROM afk WHERE chat_id='%s' AND user_name='%s' AND hapus = 0"%(chat_id, r_user_name)
        bar, jum    = eksekusi(cek)
        if jum == 0:
            pass
        else:
            update.message.reply_text("%s gak online, dia lagi %s"%(r_user_name,bar[0][0]))
    except:
        pass

# dp = Config.dp
# # dp.add_handler(MessageHandler(Filters.all & Filters.group, sudah_nongol))
# dp.add_handler(MessageHandler(Filters.entity(MessageEntity.MENTION) | Filters.entity(MessageEntity.TEXT_MENTION),reply_afk))
# dp.add_handler(CommandHandler("afk",set_afk))
# dp.add_handler(MessageHandler(Filters.all, set_afk))