from telegram import Bot, Update
from telegram import ParseMode
from telegram.utils.helpers import escape_markdown
from config import *
import random
from modul.kamus import kamus

def qotd(bot:Bot,update:Update,args): 
    chat_id = update.message["chat"]["id"]                
    if len(args)==0:
        m = update.effective_message            
        try:
            waktu = str(m.reply_to_message.date.strftime('%Y-%m-%d %H:%M:%S'))
            quote =  m.reply_to_message.text.replace("'","''")
            cek = "SELECT nomor FROM qotd WHERE quote = '%s'"%(quote)
            barC,jumC = eksekusi(cek)
            if jumC >= 1:
                update.message.reply_text(str(kamus("qotd_dobel"))%(barC[0][0]))
            else:
                try:
                    user_name   =  update.message["reply_to_message"]["forward_from"]["username"]
                    user_id     =  update.message["reply_to_message"]["forward_from"]["id"]
                except:                        
                    user_name   =  m.reply_to_message.from_user.username
                    user_id     =  m.reply_to_message.from_user.id
                chat_type = update.message["chat"]["type"]
                hitung = "SELECT quote FROM qotd WHERE chat_id = '%s'"%(chat_id)
                bar, jum = eksekusi(hitung)            
                jum = jum+1
                sql = "INSERT INTO qotd (nomor,waktu, chat_id, chat_type, user_id, user_name, quote, hapus) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s')"%(
                jum,waktu, chat_id, chat_type, user_id, user_name, quote, 0)
                cur.execute(sql)
                db.commit()
                update.message.reply_text(str(kamus("quote_simpan"))%(jum,jum,jum))
        except Exception as e:            
            update.message.reply_text('%s\n%s'%(kamus("quote_mogok"),e))
    elif str(args[0]).isdigit():
        sql = "SELECT quote, user_name, nomor FROM qotd WHERE chat_id = '%s' AND nomor = '%s'"%(chat_id, args[0])
        bar, jum = eksekusi(sql)
        if jum == 0:
            update.message.reply_text(kamus("quote_not_found"))
        else:
            update.message.reply_html("<i>{}</i>\n\n@{}:{}".format(bar[0][0],bar[0][1],bar[0][2]))
    else:
        update.message.reply_text("Silahkan reply atau forward chat yang akan di quote")

def rqotd(bot:Bot,update:Update):
    chat_id = update.message["chat"]["id"]
    quote = []
    sql = "SELECT quote, user_name,nomor FROM qotd WHERE chat_id = '%s' AND hapus = 0"%chat_id
    bar, jum = eksekusi(sql)
    for i in range(jum):
        quote.append("<i>{}</i>\n\n@{}:{}".format(bar[i][0],bar[i][1],bar[i][2]))        
    update.message.reply_html(random.choice(quote))

def dqotd(bot:Bot,update:Update,args):
    chat_id = update.message["chat"]["id"]
    if len(args) == 0:
        update.message.reply_text(kamus("quote_kurang"))
    elif str(args[0]).isdigit():
        hitung = "SELECT quote FROM qotd WHERE chat_id = '%s'"%(chat_id)
        bar, jum = eksekusi(hitung)            
        if jum == 0:
            update.message.reply_text(kamus("dqotd_not_found"))
        else:
            sql = ("UPDATE qotd SET hapus = 1 WHERE chat_id = '%s' AND nomor = '%s'"%(chat_id, args[0]))
            cur.execute(sql)
            db.commit()                
            update.message.reply_text(kamus("dqotd_sukses"))
    else:
        update.message.reply_text(kamus("quote_kurang"))   