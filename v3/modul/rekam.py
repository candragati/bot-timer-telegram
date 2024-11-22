
from config import *
from modul.buatPdf import buatPdf
from datetime import datetime
# import pprint
import threading


lock = threading.Lock()
def baca(update,context):     
    message         = update.effective_message  # type: Optional[Message]    
    chat_id         = message.chat.id
    chat_type       = message.chat.type
    if chat_type    == 'private':
        chat_title  =   "PM%s"%chat_id
    else:
        chat_title  = message.chat.title
    message_id      = message.message_id

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
                update.message.reply_text("Saya lagi sibuk membaca. Belum disuruh untuk /tulis")
            else:
                sql_insert = "INSERT INTO rekam (nomor, waktu, chat_id, chat_type, chat_title, judul, baca, tulis,done) VALUES (?,?,?,?,?,?,?,?,?)"
                cur.execute(sql_insert,(jum+1,sekarang, chat_id, chat_type, chat_title, 0,baca_id, 0,0))
                db.commit()
                update.message.reply_text("Mulai membaca...\nsetelah mencapai 100 chat, pencatatan akan dihentikan.")
        except Exception as e:
            update.message.reply_text("Silahkan reply chat yang akan ditandai untuk dibaca\n%s"%e)    

    except Exception as e:
        update.message.reply_text("Silahkan reply chat yang akan ditandai untuk dibaca\n%s"%e)

def tulis(update,context):
    bot             = context.bot
    args            = context.args
    message         = update.effective_message  # type: Optional[Message]    
    chat_id         = message.chat.id
    message_id      = message.message_id
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


def isi(update,context): 
    bot             = context.bot
    args            = context.args
    try:
        fwd_username=  update.message["forward_from"]["username"]
        fwd_name    =  '%s %s'%(update.message["forward_from"]["first_name"],update.message["forward_from"]["last_name"])
        cek_forward =  1
    except:                        
        fwd_username=  None
        fwd_name    =  None
        cek_forward =  0

    
    message         = update.effective_message  # type: Optional[Message]    
    chat_id         = message.chat.id
    message_id      = message.message_id
    from_user_name  = message.from_user.username
    from_user_id    = message.from_user.id    
    date            = message.date        
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
        # nomor = bar[0][0]
        # waktu = bar[0][1]
        baca = bar[0][2]
        jarak = message_id - baca
        if jarak == 50:
            update.message.reply_text("INFORMASI\n\nsudah sampai 50 chat...")
        elif jarak >= 100:
            update.message.reply_text("INFORMASI\n\nsudah sampai 100 chat.\nPencatatan dihentikan")
            tulis(update, context)
            return

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
            width       = photo[-1].width
            height      = photo[-1].height
            image_size  = "%sx%s"%(width,height)
        elif sticker is not None:            
            media       = sticker['thumb']['file_id']
            teks_media  = str(media)
            isi         = ""
            media_file  = bot.get_file(media)
            media_file.download('gambar/%s'%media)
            width       = sticker['thumb']['width']
            height      = sticker['thumb']['height']
            image_size  = "%sx%s"%(width,height)
        elif video is not None:
            media       = video['thumb']['file_id']
            teks_media  = str(media)
            isi         = ""
            media_file  = bot.get_file(media)
            media_file.download('gambar/%s'%media)
            width       = video['thumb']['width']
            height      = video['thumb']['height']
            image_size  = "%sx%s"%(width,height)
        else:
            isi         = msg_text
            teks_media  = ""
            image_size  = "0x0"

        sql_cek         = "SELECT message_id FROM rekam_log WHERE nomor = '%s' AND chat_id = '%s' AND message_id='%s'"%(bar[0][0],chat_id, message_id)
        barC, jumC      = eksekusi(sql_cek)
        if jumC == 0:
            if cek_forward == 0:
                sql_insert  = "INSERT INTO rekam_log (nomor, waktu, chat_id, user_id,username,nama, message_chat, message_media,message_id, reply_to, edited,image_size) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)"
                cur.execute(sql_insert,(bar[0][0],date, chat_id, from_user_id,from_user_name, nama, isi,teks_media,message_id,reply_id,0,image_size))
            else:
                sql_insert  = "INSERT INTO rekam_log (nomor, waktu, chat_id, user_id,username,nama, message_chat, message_media,message_id, reply_to, edited,forward_username, forward_name,image_size) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
                cur.execute(sql_insert,(bar[0][0],date, chat_id, from_user_id,from_user_name, nama, isi,teks_media,message_id,reply_id,0,fwd_username, fwd_name,image_size))
        else:
            sql_update  = "UPDATE rekam_log SET message_chat=?,edited = 1 WHERE nomor = ? AND chat_id = ? AND message_id = ?"
            cur.execute(sql_update,(isi, bar[0][0],chat_id, message_id))
        db.commit()

def judul(update,context): 
    message         = update.effective_message  # type: Optional[Message]    
    chat_id         = message.chat.id
    
    # print (message)
    from_user_name  = message.reply_to_message.from_user.username
    from_user_id    = message.reply_to_message.from_user.id
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