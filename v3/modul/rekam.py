from telegram import Bot, Update, Message
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode
from telegram.utils.helpers import escape_markdown
from telegram import MessageEntity
from config import *
from modul.kamus import kamus
from modul.buatPdf import buatPdf
from datetime import datetime
import pprint
import json
import threading


lock = threading.Lock()
def baca(bot:Bot,update:Update):     
    chat            = update.effective_chat  # type: Optional[Chat]
    user            = update.effective_user  # type: Optional[User]
    message         = update.effective_message  # type: Optional[Message]    
    chat_id         = message.chat.id
    chat_type       = message.chat.type
    if chat_type    == 'private':
        chat_title  =   "PM%s"%chat_id
    else:
        chat_title  = message.chat.title
    message_id      = message.message_id

    # print (message)
    from_user_name  = message.from_user.username
    from_user_id    = message.from_user.id
    member          = chat.get_member(from_user_id)
    # waktu           = str(message.reply_to_message.date.strftime('%Y-%m-%d %H:%M:%S'))    
    try:
        baca_id     = message['reply_to_message']['message_id']
    except:
        baca_id     = message_id

    try:
        sekarang    = str(datetime.today().date())
        sql = "SELECT nomor FROM rekam WHERE chat_id = '%s'"%chat_id
        bar, jum = eksekusi(sql)        
        try:
            cek_done = "SELECT done FROM rekam WHERE chat_id = '%s' AND done = 0"%(chat_id)
            barD, jumD = eksekusi(cek_done)
            if jumD != 0:
                update.message.reply_text("Saya belum selesai membaca...")
            else:
                sql_insert = "INSERT INTO rekam (nomor, waktu, chat_id, chat_type, chat_title, judul, baca, tulis,done) VALUES (?,?,?,?,?,?,?,?,?)"
                cur.execute(sql_insert,(jum+1,sekarang, chat_id, chat_type, chat_title, 0,baca_id, 0,0))
                db.commit()
                update.message.reply_text("Mulai membaca...")
        except Exception as e:
            update.message.reply_text("Silahkan reply chat yang akan ditandai untuk dibaca\n%s"%e)    

    except Exception as e:
        update.message.reply_text("Silahkan reply chat yang akan ditandai untuk dibaca\n%s"%e)

def tulis(bot:Bot,update:Update):
    chat            = update.effective_chat  # type: Optional[Chat]
    user            = update.effective_user  # type: Optional[User]
    message         = update.effective_message  # type: Optional[Message]    
    chat_id         = message.chat.id
    chat_type       = message.chat.type
    if chat_type    == 'private':
        chat_title  =   "PM%s"%chat_id
    else:
        chat_title  = message.chat.title
    message_id      = message.message_id

    # print (message)
    from_user_name  = message.from_user.username
    from_user_id    = message.from_user.id
    member          = chat.get_member(from_user_id)    

    try:
        tulis_id    = message['reply_to_message']['message_id']
    except:
        tulis_id    = message_id

    cek_done        = "SELECT nomor,baca FROM rekam WHERE chat_id = '%s' AND done = 0"%(chat_id)
    bar, jum        = eksekusi(cek_done)
    
    try:        
        if jum == 0:
            update.message.reply_text("Saya tidak tau mau nulis apa...")
        elif int(bar[0][1]) > int(tulis_id):
            update.message.reply_text("Jangan suruh saya naik-turun gitu mas...")
        else:
            update.message.reply_text("Sedang menulis...")       
            buatPdf(chat_id)            
            try:
                lock.acquire(True)
                sql_tulis = "UPDATE rekam SET tulis = ?, done = 1 WHERE nomor = ? AND chat_id = ?"
                cur.execute(sql_tulis,(tulis_id, bar[0][0], chat_id))
                db.commit()            
            finally:
                lock.release()
            file = open("%s%s.pdf"%(abs(chat_id), bar[0][0]),"rb")
            bot.send_document(chat_id, file)
    except Exception as e:        
        try:
            lock.acquire(True)
            sql_tulis = "UPDATE rekam SET tulis = ?, done = 0 WHERE nomor = ? AND chat_id = ?"
            cur.execute(sql_tulis,(tulis_id, bar[0][0], chat_id))
            db.commit()            
        finally:
            lock.release()
        update.message.reply_text("Bingung...\n%s"%e)


def isi(bot:Bot,update:Update): 
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
    

    # rekam
    sql = "SELECT nomor, waktu, baca, tulis, judul, author FROM rekam WHERE done = 0 and chat_id = '%s'"%(chat_id)
    bar, jum = eksekusi(sql)
    if jum == 0:
        pass
    else:
        try:
            msg_text        = message.text.encode("unicode_escape")
        except:
            msg_text        = message.text
        # nomor = bar[0][0]
        # waktu = bar[0][1]
        # baca = bar[0][2]
        # tulis = bar[0][3]
        # judul = bar[0][4]
        # author = bar[0][5]
        # pprint.pprint(message.to_dict())
        # print (from_first_name)
        try:
            uphoto          = bot.get_user_profile_photos(from_user_id, limit=1).photos[0]        
            uphoto_file_id  = uphoto[-1].file_id        
            uphoto          = bot.get_file(uphoto_file_id)
            uphoto.download('gambar/%s'%from_user_name)
        except:
            uphoto = 0
        
        # detect reply
        if message.reply_to_message == None:
            reply_id = 0
        else:
            reply_id = message.reply_to_message.message_id        

        # detect media
        sticker     = message.sticker        
        photo       = message.photo
        video       = message.animation
        if len(photo) != 0:
            media       = photo[-1].file_id
            isi         = message.caption
            teks_media  = str(media)
            media_file  = bot.get_file(media)
            media_file.download('gambar/%s'%media)
        elif sticker is not None:            
            media       = sticker['thumb']['file_id']
            teks_media  = str(media)
            isi         = ""
            media_file  = bot.get_file(media)
            media_file.download('gambar/%s'%media)
        elif video is not None:
            media       = video['thumb']['file_id']
            teks_media  = str(media)
            isi         = ""
            media_file  = bot.get_file(media)
            media_file.download('gambar/%s'%media)
        else:
            isi         = msg_text
            teks_media  = ""

        sql_cek         = "SELECT message_id FROM rekam_log WHERE nomor = '%s' AND chat_id = '%s' AND message_id='%s'"%(bar[0][0],chat_id, message_id)
        barC, jumC      = eksekusi(sql_cek)
        if jumC == 0:
            if cek_forward == 0:
                sql_insert  = "INSERT INTO rekam_log (nomor, waktu, chat_id, user_id,username,nama, message_chat, message_media,message_id, reply_to, edited) VALUES (?,?,?,?,?,?,?,?,?,?,?)"
                cur.execute(sql_insert,(bar[0][0],date, chat_id, from_user_id,from_user_name, nama, isi,teks_media,message_id,reply_id,0))
            else:
                sql_insert  = "INSERT INTO rekam_log (nomor, waktu, chat_id, user_id,username,nama, message_chat, message_media,message_id, reply_to, edited,forward_username, forward_name) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)"
                cur.execute(sql_insert,(bar[0][0],date, chat_id, from_user_id,from_user_name, nama, isi,teks_media,message_id,reply_id,0,fwd_username, fwd_name))
        else:
            sql_update  = "UPDATE rekam_log SET message_chat=?,edited = 1 WHERE nomor = ? AND chat_id = ? AND message_id = ?"
            cur.execute(sql_update,(isi, bar[0][0],chat_id, message_id))
        db.commit()

def judul(bot:Bot,update:Update): 
    chat            = update.effective_chat  # type: Optional[Chat]
    user            = update.effective_user  # type: Optional[User]
    message         = update.effective_message  # type: Optional[Message]    
    chat_id         = message.chat.id
    chat_type       = message.chat.type
    message_id      = message.message_id

    # print (message)
    from_user_name  = message.reply_to_message.from_user.username
    from_user_id    = message.reply_to_message.from_user.id
    member          = chat.get_member(from_user_id)
    try:
        judul_teks  = message['reply_to_message']['text']
        cek_done    = "SELECT nomor FROM rekam WHERE chat_id = '%s' AND done = 0"%(chat_id)
        barD, jumD  = eksekusi(cek_done)
        if jumD !=0:
            try:
                lock.acquire(True)
                sql_judul = "UPDATE rekam SET judul = ?, author = ?,author_id = ? WHERE nomor = ? AND chat_id = ?"
                cur.execute(sql_judul,(judul_teks, from_user_name, from_user_id, barD[0][0], chat_id))
                db.commit()
            finally:
                lock.release()
            update.message.reply_text("Judul : %s\nOleh %s"%(judul_teks,from_user_name))
        else:
            update.message.reply_text("Silahkan tandai chat dengan reply /baca")
    except Exception as e:
        update.message.reply_text("Gak bisa nulis judul\n%s"%e)
    
# dp = Config.dp
# dp.add_handler(MessageHandler(Filters.all, isi,edited_updates=True))