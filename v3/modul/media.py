
from config import *
# from openpyxl.styles import Side, Border
import threading
import re,os
from modul.buatPdfMedia import buatPdf
import pprint
from datetime import *
import random
from urllib.parse import urlparse
from modul.kamus import kamus
import requests
from telegram import InputMediaPhoto, InputMediaVideo

lock = threading.Lock()

def smedia(update,context):     
    args = context.args
    chat_id = update.message["chat"]["id"]   
    chat_type = update.message["chat"]["type"]             
    message         = update.effective_message.reply_to_message
    # pprint.pprint(message.to_dict())
    if len(args)==0:
        update.message.reply_text(str(kamus("media_kurang")))
    else:
        # try:
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
                image_size  = "0x0"
                thumb_id    = ""
            elif animation is not None:            
                media       = animation['file_id']
                tipe        = "animation"
                try:
                    thumb_id    = animation['thumb']['file_id']
                    width       = animation['thumb']['width']
                    height      = animation['thumb']['height']
                except:
                    thumb_id    = animation['file_id']
                    width       = animation['width']
                    height      = animation['height']
                image_size  = "%sx%s"%(width,height)
            elif document is not None:            
                media       = document['file_id']
                try:
                    thumb_id    = document['thumb']['file_id']
                    width       = document['thumb']['width']
                    height      = document['thumb']['height']
                except:
                    thumb_id    = document['file_id']
                    width       = document['width']
                    height      = document['height']
                tipe        = "document"                
                image_size  = "%sx%s"%(width,height)
            elif len(photo) != 0:            
                media       = photo[0]['file_id']
                thumb_id    = photo[-1].file_id
                tipe        = "photo"
                width       = photo[-1].width
                height      = photo[-1].height
                image_size  = "%sx%s"%(width,height)
            elif sticker is not None:            
                media       = sticker['file_id']
                thumb_id    = sticker['thumb']['file_id']
                tipe        = "sticker"
                width       = sticker['thumb']['width']
                height      = sticker['thumb']['height']
                image_size  = "%sx%s"%(width,height)
            elif video is not None:            
                media       = video['file_id']
                thumb_id    = video['thumb']['file_id']
                tipe        = "video"
                width       = video['thumb']['width']
                height      = video['thumb']['height']
                image_size  = "%sx%s"%(width,height)
            elif voice is not None:            
                media       = voice['file_id']
                tipe        = "voice"
                image_size  = "0x0"
                thumb_id    = ""
            elif video_note is not None:            
                media       = video_note['file_id']
                tipe        = "video_note"
                image_size  = "0x0"
                thumb_id    = ""
            elif contact is not None:            
                media       = contact['vcard']
                tipe        = "contact"
                image_size  = "0x0"
                thumb_id    = ""
            else:
                update.message.reply_text(str(kamus("media_asing")))
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
            eksekusi(cek,(chat_id,keyword))
            
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
                    sql = "INSERT INTO media (nomor,waktu, chat_id, chat_type, media_tipe, media_keyword, media_id, thumb_id, image_size) VALUES (?,?,?,?,?,?,?,?,?)"
                    eksekusi(sql,(jum,waktu, chat_id, chat_type, tipe, keyword, media, thumb_id, image_size))
                    
                finally:
                    lock.release()
                update.message.reply_text(str(kamus("media_simpan")%keyword))
        # except Exception as e:            
        #     update.message.reply_text('Gagal simpan media\n%s'%(e))

def rmedia(update,context):
    bot         = context.bot
    chat_id     = update.message["chat"]["id"]
    mediaRandom = []
    acak        = []
    sql         = "SELECT nomor  FROM media WHERE chat_id = '%s'"%chat_id
    bar, jum    = eksekusi(sql)
    for i in range(jum):
        mediaRandom.append(bar[i][0])
    acak.append('%s'%random.choice(mediaRandom))
    
    sql = "SELECT media_tipe, media_id, media_keyword FROM media WHERE chat_id = ? AND nomor = ?"
    eksekusi(sql,(chat_id,acak[0]))   
             
    bar =  (cur.fetchall())
    jum =  (len(bar))
    if jum == 0:
        update.message.reply_text(str(kamus("media_kosong")))
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

        if bar[0][2] == 'resign2':            
            bot.leave_chat(chat_id)

def media(update,context): 
    bot     = context.bot
    args    = context.args
    chat_id = update.message["chat"]["id"]                    
    
    cek_done = "SELECT done FROM rekam WHERE chat_id = '%s' AND done = 0"%(chat_id)
    barD, jumD = eksekusi(cek_done)
    if jumD != 0:
        update.message.reply_text(str(kamus("media_kulgram")))
    elif len(args)==0:
        update.message.reply_text(str(kamus("media_kurang")))
    else:
        keyword = ' '.join(args)
        sql = "SELECT media_tipe, media_id FROM media WHERE chat_id = ? AND media_keyword = ?"
        bar, jum = eksekusi(sql,(chat_id,keyword))   
        if jum == 0:
            update.message.reply_text(str(kamus("media_kosong")))
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

            if keyword == 'resign2':
                chat        = update.effective_chat
                user_id     = update.message.from_user.id
                user_member = chat.get_member(user_id)
                if user_member.status == 'administrator' or user_member.status == 'creator':
                    bot.leave_chat(chat_id)

def xmedia(update,context):
    update.message.reply_text("start download")

    bot             = context.bot
    args            = context.args
    message         = update.effective_message  # type: Optional[Message]    
    chat_id         = message.chat.id
    sql = "SELECT nomor,waktu, media_tipe, media_keyword,thumb_id  FROM media WHERE chat_id = '%s'"%(chat_id)
    barR, jumR = eksekusi(sql)
    
    for i in range(jumR):        
        nomor       = barR[i][0]
        waktu       = barR[i][1]
        waktu       = datetime.strptime(waktu,"%Y-%m-%d %H:%M:%S")
        m_tipe      = barR[i][2]
        m_keyword   = barR[i][3]
        m_id        = barR[i][4]
        
        if os.path.isfile('static/%s'%m_id):
            pass
        else:
            try:
                media_file  = bot.get_file(m_id)
                media_file.download('static/%s'%m_id)
            except:
                pass
    update.message.reply_text("download selesai")
        

    # buatPdf(chat_id)
    # namafile    = "media%s.pdf"%(abs(chat_id))
    # file = open(namafile,"rb")
    # bot.send_document(chat_id, file)
    # 

def cmedia(update, context):
    bot     = context.bot    
    args    = context.args[0] 
    chat_id = update.message["chat"]["id"]   

    hostname =urlparse(args).hostname

    arsip = "https://arsip.hmpbi.my.id/"

    if hostname == 'twitter.com' or hostname == 'x.com':
        sosmed = "api/twit"
    elif ('facebook' in hostname) or ('fb' in hostname):
        sosmed = "api/fb"
    elif 'instagram' in hostname:
        sosmed = "api/ig"
    elif hostname == 'tiktok.com':
        sosmed = "api/tiktok"
    else:
        update.message.reply_text("link apaan nih")
        return

    
    endpoint= f"?url={args}"
    link = f"{arsip}{sosmed}{endpoint}"
    req = requests.get(link).json()
    if req['success']:
        if req['media']:
            media = []
            for i, m in enumerate(req['media']):
                caption = req['caption']
                if m['type'] != 'video':
                    media.append(InputMediaPhoto(m['url'], caption = caption))
                else:
                    media.append(InputMediaVideo(m['url'], caption = caption))



        
        
        bot.send_media_group(chat_id = chat_id, media = media)
    else:
        update.message.reply_text("gagal")

    


    # https://arsip.hmpbi.my.id/api/twit?url=https://twitter.com/Egrammar_tip/status/1753387150119518283

