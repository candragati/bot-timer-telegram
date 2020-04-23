
from config import *
# from openpyxl.styles import Side, Border
import threading
import re
from modul.buatPdfMedia import buatPdf
import pprint
import datetime

lock = threading.Lock()

def smedia(update,context):     
    args = context.args
    chat_id = update.message["chat"]["id"]   
    chat_type = update.message["chat"]["type"]             
    message         = update.effective_message.reply_to_message
    
    if len(args)==0:
        update.message.reply_text('Silahkan tulis keywordnya')
    else:
        try:
            # detect media
            audio       = message.audio
            document    = message.document
            animation   = message.animation
            photo       = message.photo
            sticker     = message.sticker        
            video       = message.video
            voice       = message.voice
            video_note  = message.video_note
            contact     = message.contact
            # location    = message.location
            # venue       = message.venue
            # invoice     = message.invoice
            keyword     = ' '.join(args)            
            if audio is not None:
                media       = audio['file_id']   
                tipe        = "audio"
            elif document is not None:            
                media       = document['file_id']
                tipe        = "document"
            elif animation is not None:            
                media       = animation['file_id']
                tipe        = "animation"
            elif len(photo) != 0:            
                media       = photo[0]['file_id']
                tipe        = "photo"
            elif sticker is not None:            
                media       = sticker['file_id']
                tipe        = "sticker"
            elif video is not None:            
                media       = video['file_id']
                tipe        = "video"
            elif voice is not None:            
                media       = voice['file_id']
                tipe        = "voice"
            elif video_note is not None:            
                media       = video_note['file_id']
                tipe        = "video_note"
            elif contact is not None:            
                media       = contact['vcard']
                tipe        = "contact"
            else:
                update.message.reply_text("Tipe Media tidak dikenal")
                return
            # elif location is not None:            
            #     media       = location
            #     tipe        = "location"
            # elif venue is not None:            
            #     media       = venue['file_id']
            #     tipe        = "venue"
            # elif invoice is not None:            
            #     media       = invoice['file_id']
            #     tipe        = "invoice"

            cek = "SELECT media_keyword FROM media WHERE chat_id = ? AND media_keyword = ?"
            cur.execute(cek,(chat_id,keyword))            
            jumC =  (len(cur.fetchall()))            
            if jumC >= 1:
                update.message.reply_text('Double keyword')
            else:
                waktu = str(message.date.strftime('%Y-%m-%d %H:%M:%S'))
                hitung = "SELECT nomor FROM media WHERE chat_id = '%s'"%(chat_id)
                bar, jum = eksekusi(hitung)            
                jum = jum+1
                try:
                    lock.acquire(True)
                    sql = "INSERT INTO media (nomor,waktu, chat_id, chat_type, media_tipe, media_keyword, media_id) VALUES (?,?,?,?,?,?,?)"
                    cur.execute(sql,(jum,waktu, chat_id, chat_type, tipe, keyword, media))
                    db.commit()
                finally:
                    lock.release()
                update.message.reply_text("media berhasil di simpan dengan keyword %s"%keyword)
        except Exception as e:            
            update.message.reply_text('Gagal simpan media\n%s %s'%(e,cek))

def media(update,context): 
    bot     = context.bot
    args    = context.args
    chat_id = update.message["chat"]["id"]                    
    
    cek_done = "SELECT done FROM rekam WHERE chat_id = '%s' AND done = 0"%(chat_id)
    barD, jumD = eksekusi(cek_done)
    if jumD != 0:
        update.message.reply_text("Fitur /media dimatikan. Masih belum selesai membaca...")
    elif len(args)==0:
        update.message.reply_text('Silahkan tulis keywordnya')
    else:
        keyword = ' '.join(args)
        sql = "SELECT media_tipe, media_id FROM media WHERE chat_id = ? AND media_keyword = ?"
        cur.execute(sql,(chat_id,keyword))            
        bar =  (cur.fetchall())
        jum =  (len(bar))
        if jum == 0:
            update.message.reply_text('media tidak ketemu')
        else:
            # detect media' 
            
            media = {
            "audio"       : "bot.send_audio",
            "document"    : "bot.send_document",
            "animation"   : "bot.send_animation",
            "photo"       : "bot.send_photo",
            "sticker"     : "bot.send_sticker",
            "video"       : "bot.send_video",
            "voice"       : "bot.send_voice",
            "video_note"  : "bot.send_video_note",
            "contact"     : "bot.send_contact",
            "location"    : "bot.send_location",
            "venue"       : "bot.send_venue",
            "invoice"     : "bot.send_invoice",
            }

            perintah = media[bar[0][0]]
            if bar[0][0] == "contact":
                vcard       = bar[0][1]
                FN          =  re.findall('FN:(.*)',vcard)
                PHONE       =  re.findall('MOBILE:(.*)',vcard)
                media_id    = "phone_number = '%s', first_name = '%s'"%(PHONE[0], FN[0])
            else:
                media_id    = "'%s'"%bar[0][1]
            try:
                m_id        =  update.message["reply_to_message"]["message_id"]
                exec ("%s('%s',%s,reply_to_message_id=%s)"%(perintah,chat_id,media_id,m_id))
            except:
                exec ("%s('%s',%s)"%(perintah,chat_id,media_id))

def xmedia(update,context):
    bot = context.bot
    chat_id         = update.message["chat"]["id"]    
    # message         = update.effective_message  # type: Optional[Message]   
    to_chat_id      = -1001337729941 
    # message_id      = message.reply_to_message.message_id
    # r               = message.reply_to_message
    # date            = r.date
    # from_user       = r.from_user.username
    message_id      = 6648
    message         = (bot.forward_message(to_chat_id, chat_id, message_id).to_dict())
    pprint.pprint (message)
    chat_id         = message['chat']['id']
    message_id      = message['message_id']
    from_user_name  = message['forward_from']['username']
    from_user_id    = message['forward_from']['id']
    date            = datetime.datetime.fromtimestamp(message['date'])
    msg_text        = message['text']

    # print (chat_id, message_id, from_user_name, from_user_id, date, msg_text)
    
    # pprint.pprint (update.message.messages.getHistory())