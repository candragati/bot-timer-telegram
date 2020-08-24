
from telegram import ParseMode
from telegram.utils.helpers import escape_markdown
from config import *
from modul import reputasi

def set_bio(update,context):
    m           = update.effective_message
    r_user_name = m.reply_to_message.from_user.username
    r_user_id   = str(m.reply_to_message.from_user.id)
    user_id     = str(update.message.from_user.id)
    teks        = m.text.split(None,1)    
    if r_user_id == user_id:
        update.message.reply_text("Gak bisa update bio punya sendiri")
    elif len(teks) == 2:
        try:
            chat_id     = str(update.message["chat"]["id"])
            chat_type   = update.message["chat"]["type"]
            cek         = "SELECT user_name,teks FROM bio WHERE chat_id='%s' AND user_id='%s'"%(chat_id, r_user_id)
            bar, jum = eksekusi(cek)
            if jum == 0:            
                sql = "INSERT INTO bio (chat_id, chat_type, user_id, user_name, teks) VALUES (?,?,?,?,?)"
                cur.execute(sql,(chat_id, chat_type, r_user_id, r_user_name, teks[1]))
            else:
                sql = "UPDATE bio SET teks = ? WHERE chat_id = ? AND user_id = ?"
                cur.execute(sql,(teks[1],chat_id,r_user_id))
            db.commit()
            update.message.reply_text("Memperbarui bio nya @%s"%r_user_name)
        except:
            update.message.reply_text("Gak bisa simpan bio")

def bio(update,context):
    m   = update.effective_message
    bot = context.bot
    try:
        user_id     =  m.reply_to_message.from_user.id   
        user_name   = bot.get_chat(user_id).username
        teks_r      = reputasi.reputasi(update,context,user_id)
        chat_id     = update.message["chat"]["id"]        
        sql         = "SELECT teks FROM bio WHERE chat_id='%s' AND user_id='%s'"%(chat_id, user_id)
        bar, jum = eksekusi(sql)
        if jum == 0:            
            update.message.reply_text("Gak ada member yang sudi menulis tentang @%s."%user_name)
        else:
            update.effective_message.reply_text("*{}*:\n{}\n\n{}".format(user_name, escape_markdown(bar[0][0]),teks_r),parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        update.message.reply_text("reply lalu ketik /bio\n%s"%e)
