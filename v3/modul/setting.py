from telegram import Bot, Update
from telegram import ParseMode
from telegram.utils.helpers import escape_markdown
from config import *
from modul.kamus import kamus
from telegram import MessageEntity
import calendar

def setting(bot:Bot,update:Update,args):
    chat_id = update.message["chat"]["id"]
    chat_type = update.message["chat"]["type"]
    chat = update.effective_chat
    user_id = update.message.from_user.id
    user_member = chat.get_member(user_id)
    if user_member.status == 'administrator' or user_member.status == 'creator':
        if len(args)==0:
            update.message.reply_text("setting apa pak?")
        elif args[0]=='en':
            hari = list(calendar.day_abbr)
            try:
                if args[1].upper()=='CLEAR':
                    sql = "DELETE FROM setting WHERE chat_id = '%s'"%chat_id                
                    cur.execute(sql)
                    db.commit()
                    update.message.reply_text("sudah gak ada english day lagi. horee...")
                else:
                    sql = "SELECT english_day FROM setting WHERE chat_id = '%s'"%chat_id
                    bar, jum = eksekusi(sql)
                    english_day = args[1].title()
                    index_day = hari.index(english_day)
                    day_name = calendar.day_name[index_day]
                    if jum == 0:
                        sql = "INSERT INTO setting (chat_id, chat_type,english_day) VALUES (?,?,?)"
                        cur.execute(sql,(chat_id,chat_type,english_day))
                    else:
                        sql = "UPDATE setting SET english_day=? WHERE chat_id = ?"
                        cur.execute(sql,(english_day, chat_id))
                    db.commit()
                    update.message.reply_text("english day is set for %s"%day_name)            
            except Exception as e:
                update.message.reply_text("choose one from %s"%hari)
        else:
            update.message.reply_text("aku gak selalu ngerti kamu mas...")
    else:
        update.message.reply_text("user biasa kayak kamu gak bisa suruh-suruh aku")
            
