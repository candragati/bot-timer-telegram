
from telegram import ParseMode
from telegram.utils.helpers import escape_markdown
from config import *
import emoji

def reputasi_good(update,context):
    try:
        m               = update.effective_message
        r_user_name     =  m.reply_to_message.from_user.username
        r_user_id       =  str(m.reply_to_message.from_user.id)
        user_id         = str(update.message.from_user.id)
        from_user_name  = m.from_user.username
        from_user_id    = m.from_user.id    
        teks            =  m.text.split(None,1)
        waktu           = str(m.reply_to_message.date.strftime('%Y-%m-%d %H:%M:%S'))
        if r_user_id == user_id:
            update.message.reply_text("Gak bisa ngasih reputasi punya sendiri")
        elif len(teks) == 2:
            try:
                chat_id = str(update.message["chat"]["id"])
                chat_type = update.message["chat"]["type"]
                sql = "INSERT INTO reputasi (tanggal, chat_id, chat_type, user_id, user_name, reputasi_good, alasan, user_id_from, user_name_from) VALUES (?,?,?,?,?,1,?,?,?)"
                cur.execute(sql,(waktu, chat_id, chat_type, r_user_id, r_user_name, teks[1], from_user_id, from_user_name))
                db.commit()
                update.message.reply_text("%s dapet reputasi bagus dari %s"%(r_user_name, from_user_name))
            except:
                update.message.reply_text("Gak bisa simpan reputasi :(")
        else:
            update.message.reply_text("kasih alasan untuk reputasi ini")
    except:
        update.message.reply_text("mau ngasih reputasi ke siapa mas?")

def reputasi_bad(update,context):
    try:
        m               = update.effective_message
        r_user_name     =  m.reply_to_message.from_user.username
        r_user_id       =  str(m.reply_to_message.from_user.id)
        user_id         = str(update.message.from_user.id)
        from_user_name  = m.from_user.username
        from_user_id    = m.from_user.id    
        teks            =  m.text.split(None,1)
        waktu           = str(m.reply_to_message.date.strftime('%Y-%m-%d %H:%M:%S'))
        if r_user_id == user_id:
            update.message.reply_text("Gak bisa ngasih reputasi punya sendiri")
        elif len(teks) == 2:
            try:
                chat_id = str(update.message["chat"]["id"])
                chat_type = update.message["chat"]["type"]
                sql = "INSERT INTO reputasi (tanggal, chat_id, chat_type, user_id, user_name, reputasi_bad, alasan, user_id_from, user_name_from) VALUES (?,?,?,?,?,1,?,?,?)"
                cur.execute(sql,(waktu, chat_id, chat_type, r_user_id, r_user_name, teks[1], from_user_id, from_user_name))
                db.commit()
                update.message.reply_text("%s dapet reputasi jelek dari %s"%(r_user_name, from_user_name))
            except:
                update.message.reply_text("Gak bisa simpan reputasi :(")
        else:
            update.message.reply_text("kasih alasan untuk reputasi ini")
    except:
        update.message.reply_text("mau ngasih reputasi ke siapa mas?")


def reputasi(update,context,user_id):
    chat_id = update.message["chat"]["id"]

    sqlr = "SELECT SUM(reputasi_good), SUM(reputasi_bad) FROM reputasi WHERE chat_id='%s' AND user_id='%s'"%(chat_id, user_id)
    barr, jumr = eksekusi(sqlr)    
    if barr[0][0] == None and barr[0][1] == None:
        return ("")
    else:
        if barr[0][0] > 10:
            rep_g = ":star: x {}".format(barr[0][0])
        else:
            rep_g =  ''.join([(":star:") for i in range(barr[0][0])])

        if barr[0][1] > 10:
            rep_b = ":shit: x {}".format(barr[0][1])
        else:
            rep_b =  ''.join([(":shit:") for i in range(barr[0][1])])

        return emoji.emojize("reputasi\n{}\n{}".format(rep_g,rep_b), use_aliases=True)


