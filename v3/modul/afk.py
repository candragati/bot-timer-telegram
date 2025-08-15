# 
from config import *
from telegram import MessageEntity, ParseMode
import threading
import random
from telegram.utils.helpers import escape_markdown
from modul.kamus import kamus

lock = threading.Lock()
def set_afk(update,context):
    m   = update.effective_message
    if update.message["chat"]["type"] == 'private':
        update.message.reply_text("hanya bisa di gunakan pada grup.")
    else:
        teks= m.text.split(None,1)
        if len(teks) == 2:        
            try:
                lock.acquire(True)
                chat_id     = str(update.message["chat"]["id"])
                chat_type   = update.message["chat"]["type"]
                user_id     = str(update.message.from_user.id)
                user_name   = update.message.from_user.username if update.message.from_user.username else update.message.from_user.first_name
                cek         = "SELECT user_name,teks FROM afk WHERE chat_id='%s' AND user_id='%s'"%(chat_id, user_id)
                bar, jum = eksekusi(cek)
                if jum == 0:            
                    sql = "INSERT INTO afk (chat_id, chat_type, user_id, user_name, teks,hapus) VALUES (?,?,?,?,?,0)"
                    eksekusi(sql,(chat_id, chat_type, user_id, user_name, teks[1]))
                else:
                    sql = "UPDATE afk SET teks = ?, hapus = ? WHERE chat_id = ? AND user_id = ?"
                    eksekusi(sql,(teks[1],'0',chat_id,user_id))
                
                update.message.reply_text("%s sekarang AFK"%user_name)
            except Exception as e:
                update.message.reply_text("ketik /afk <alasan anda>\n%s"%e)
            finally:
                lock.release()
        else:
            update.message.reply_text("ketik /afk <alasan anda>")

def sudah_nongol(update,context):
    
    sticker_list = [
        'CAADBQADSQ4AAs_rwQcgxkK2JzKWwhYE',
        'CAACAgUAAx0CT7wjlQACGqBeQu_wChW-vRTQ9hKxcGIy4HBOfwACtw4AAs_rwQd8QPeC03KeRhgE',     # eh, si goblok kirain siapa
        'CAACAgUAAx0CT7wjlQACGqFeQvDB6zrGFARZQPLUAgjKjbn7UAACPQEAAl6mRAN3GFRd_ZKRgBgE',     # assalamualaikum, pangeran surga
        'CAACAgIAAx0CT7wjlQACGqJeQvE-E1KTLZOd6ZTifnqtKPUL7wACYgIAAujW4hLtBrhjLkSc1hgE',     # welcome
        'CAACAgUAAx0CT7wjlQACGqNeQvKnv4JMZboYyacd6z9xi9JJpAACKhAAAnmwyAI3SsZosUM60BgE',     # assalamualaikum
        'CAACAgUAAx0CT7wjlQACGqReQvM-ffUBCsr-WzdZeUnUhMEG5wACjQADNA0zDEQ0qj9A6y5BGAQ',      # twice
        'CAACAgUAAx0CT7wjlQACGqVeQvSMt5bBb0M20XpW1HArrs_DRwACWwADgJs6A-dfn-m8hNBcGAQ',      # its you again
        'CAACAgUAAx0CT7wjlQACGqZeQvTYm-5Z4OHjKHiJjnKcUBcMqwAC8AEAAv9NCwa6uWtSex7dXRgE',     # udah ngopi belum?
        'CAACAgUAAx0CT7wjlQACGqdeQvUAATzpaAJPNq9oBM7Fzv1NcOoAAjwAA8sjeQABtyJKHyvrmPcYBA',   # jkt
        'CAACAgUAAx0CT7wjlQACGqheQvWACBI5_6Gy083wL2IPNmAOvwACgA8AAn6RAwABuo5iwBs3wt4YBA',   # orang kualitas tinggi
        'CAACAgQAAx0CT7wjlQACGqleQvXSNcE25y-HElEkDUX33LNBMQACggIAArEFUQ8uwlWPhNi92hgE',     # ceng xiao
        'CAACAgUAAx0CT7wjlQACGqpeQvX_43FyOASO9JwBpUbwKOwsggACLwMAAukKyAOM_3J3n9ovyBgE',     # im watching you
        'CAACAgUAAx0CT7wjlQACGqxeQvauWfWwdwQEoWUIOR19ni8CvwACwA0AAs_rwQePaWgh6l5nURgE',     # jangan tinggalkan aku yang
        'CAACAgUAAx0CT7wjlQACGq1eQvchfTaUwpN5Vzz28ci00WlbbAACbAADGZ0zDwMfpOg88gjVGAQ',      # online terus opo ora kerjo
        'CAACAgUAAx0CT7wjlQACGq5eQvgYtt4J0IpZaZpvgQ22In57HQACTgEAAs4IEQZ9vLZj0IvZYxgE',     # sini peluk
    ]

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
        try:
            lock.acquire(True)
            sql = "UPDATE afk SET hapus = 1 WHERE chat_id = ? AND user_id = ?"
            eksekusi(sql, (chat_id, from_user_id))
            
            update.message.reply_sticker(sticker=random.choice(sticker_list))
        finally:
            lock.release()

def reply_afk(update, context):
    # Dari mention    
    message     = update.effective_message
    chat_id     = message.chat.id    
    entities    = message.parse_entities([MessageEntity.TEXT_MENTION, MessageEntity.MENTION])
    user_name   = message.from_user.username
    next        = True
    if message.entities and entities:        
        for ent in entities:            
            if ent.type == MessageEntity.TEXT_MENTION:
                user_id = ent.user.id
                cek     = "SELECT teks, user_name, user_id FROM afk WHERE chat_id='%s' AND user_id='%s' AND hapus = 0"%(chat_id, user_id)
            elif ent.type == MessageEntity.MENTION:
                user_name = (message.text[ent.offset:ent.offset + ent.length])
                mention = user_name.replace("@","")
                cek     = "SELECT teks, user_name, user_id FROM afk WHERE chat_id='%s' AND user_name='%s' AND hapus = 0"%(chat_id, mention)
            if not user_name:
                return
            bar, jum= eksekusi(cek)
            if jum == 0:
                pass
            else:
                next = False
                update.message.reply_text("[%s](tg://user?id=%s) gak online, dia lagi %s"%(escape_markdown(bar[0][1]), bar[0][2],bar[0][0]),parse_mode=ParseMode.MARKDOWN)

    # Dari reply
    try:        
        r_user_name   = message.reply_to_message.from_user.username if message.reply_to_message.from_user.username else message.reply_to_message.from_user.id
        cek         = "SELECT teks, user_name, user_id FROM afk WHERE chat_id='%s' AND (user_id='%s' OR user_name='%s') AND hapus = 0"%(chat_id, r_user_name, r_user_name)        
        bar, jum    = eksekusi(cek)
        if jum == 0:
            pass
        else:
            if next: update.message.reply_text("[%s](tg://user?id=%s) gak online, dia lagi %s"%(escape_markdown(bar[0][1]), bar[0][2],bar[0][0]),parse_mode=ParseMode.MARKDOWN)
    except:
        pass