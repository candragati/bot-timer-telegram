
from telegram import ParseMode
from telegram.utils.helpers import escape_markdown
from config import *
from modul import reputasi

def me(update,context):
    chat_id = update.message["chat"]["id"]
    user_id = update.message.from_user.id
    teks_r = reputasi.reputasi(update,context,user_id)
    

    sql = "SELECT user_name,teks FROM me WHERE chat_id='%s' AND user_id='%s'"%(chat_id, user_id)
    bar, jum = eksekusi(sql)
    if jum == 0:            
        update.message.reply_text("Kamu belum set info.")
    else:
        update.effective_message.reply_text("*{}*:\n{}\n\n{}".format(bar[0][0], escape_markdown(bar[0][1]), teks_r),parse_mode=ParseMode.MARKDOWN)

def set_me(update,context):
    m = update.effective_message            
    teks =  m.text.split(None,1)
    if len(teks) == 2:    
        try:    
            chat_id     = str(update.message["chat"]["id"])
            chat_type   = update.message["chat"]["type"]
            user_id     = str(update.message.from_user.id)
            user_name   = update.message.from_user.username
            cek         = "SELECT user_name,teks FROM me WHERE chat_id='%s' AND user_id='%s'"%(chat_id, user_id)
            bar, jum = eksekusi(cek)
            if jum == 0:            
                sql = "INSERT INTO me (chat_id, chat_type, user_id, user_name, teks) VALUES (?,?,?,?,?)"
                cur.execute(sql,(chat_id, chat_type, user_id, user_name, teks[1]))
            else:
                sql = "UPDATE me SET teks = ? WHERE chat_id = ? AND user_id = ?"
                cur.execute(sql,(teks[1],chat_id,user_id))
            db.commit() 
            update.message.reply_text("info anda di perbaharui")
        except Exception as e:
            update.message.reply_text("Gak bisa set info\n%s"%e)


