
from config import *
from googletrans import Translator
import time
import datetime
import re
import random
import pprint
import traceback
import threading
import emoji

chat_id_target = '-1001162202776'    
lock = threading.Lock()
def echo(update,context):
    bot             = context.bot
    chat            = update.effective_chat  # type: Optional[Chat]
    # user            = update.effective_user  # type: Optional[User]
    message         = update.effective_message  # type: Optional[Message]    
    chat_id         = message.chat.id
    chat_type       = message.chat.type
    message_id      = message.message_id
    from_user_name  = message.from_user.username
    from_user_id    = message.from_user.id    
    member          = chat.get_member(from_user_id)
    # date            = message.date
    
    sql = "SELECT media_id, media_keyword,media_tipe FROM media WHERE chat_id = '%s' AND image_size IS NULL"%chat_id_target
    bar, jum = eksekusi(sql)
    
    for i in range(0,10):
        
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
        # print (i,bar[i][2])
        perintah = media[bar[i][2]]
        if bar[i][2] == "contact":
            vcard       = bar[i][0]
            FN          =  re.findall('FN:(.*)',vcard)
            PHONE       =  re.findall('MOBILE:(.*)',vcard)
            media_id    = "phone_number = '%s', first_name = '%s'"%(PHONE[0], FN[0])
        else:
            media_id    = "'%s'"%bar[i][0]
        exec ("%s('%s',%s)"%(perintah,chat_id,media_id))
        bot.send_message(text = bar[i][1],chat_id = chat_id)

    #     # time.sleep(2)

    # media_id = 'AgADBQAD1KcxG-SL5xvEtw5acKk02HVX2zIABAEAAwIAA2EAA11QAgABFgQ'
    # bar, jum = eksekusi("SELECT media_id, media_keyword,media_tipe FROM media WHERE chat_id = '-1001286308688' AND media_id = '%s'"%media_id)
    # bot.send_photo('%s'%chat_id, media_id)
    # bot.send_message(text = bar[0][1],chat_id = chat_id)

    # sqlUpdate = "UPDATE media SET thumb_id = ?, image_size = ? WHERE media_id = ?"
    # eksekusi(sqlUpdate, (thumb_id, image_size, media))
    # 
    


    
    
        
        # print (update.message.sticker)
        # sticker_id = update.message.sticker.file_id

def smedia(update,context):     
    args = context.args
    chat_id = update.message["chat"]["id"]   
    chat_type = update.message["chat"]["type"]             
    message         = update.effective_message.reply_to_message
    # pprint.pprint(message.to_dict())
    keyword     = ' '.join(args)
    
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
    elif document is not None:            
        media       = document['file_id']
        thumb_id    = document['thumb']['file_id']
        tipe        = "document"                
        width       = document['thumb']['width']
        height      = document['thumb']['height']
        image_size  = "%sx%s"%(width,height)
    elif animation is not None:            
        media       = animation['file_id']
        thumb_id    = animation['thumb']['file_id']
        tipe        = "animation"
        width       = animation['thumb']['width']
        height      = animation['thumb']['height']
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
    elif contact is not None:            
        media       = contact['vcard']
        tipe        = "contact"
        image_size  = "0x0"
        thumb_id    = ""
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
    # print (thumb_id)
    # print (media)
    # print (image_size)
    sqlUpdate = "UPDATE media SET thumb_id = ?, image_size = ?, media_id = ? WHERE media_keyword = ?"
    eksekusi(sqlUpdate, (thumb_id, image_size, media, keyword))
    
    update.message.reply_text("media berhasil di simpan dengan keyword %s"%keyword)
    
