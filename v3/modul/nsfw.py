
from config import *
import calendar
from pprint import pprint
import os
import tempfile
from nudenet import NudeDetector


def cek(update,context):
    detector = NudeDetector()
    bot         = context.bot
    args        = context.args
    chat_id     = update.message["chat"]["id"]
    chat_type   = update.message["chat"]["type"]
    chat        = update.effective_chat
    user_id     = update.message.from_user.id
    user_member = chat.get_member(user_id)   

    message = update.message
    photo       = message.photo
    video       = message.video
    caption = message.caption or ""
    if "#amanmin" in caption.lower():
        return    

    file_id = None
    if photo:
        file_id = photo[-1].file_id  # ambil resolusi terbesar    
    elif video and video.thumb:
        file_id = video.thumb.file_id
    else:
        return

    file = bot.get_file(file_id)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        file.download(custom_path=tmp.name)
        tmp_path = tmp.name

    results = detector.detect(tmp_path)
    os.remove(tmp_path)

    hasil = ""
    classes = []
    skor = []
    for d in results:
        if d['class'] not in ['FACE_FEMALE','FACE_MALE']:
            hasil += f"{d['class']} {d['score']*100:,.2f}%\n"
            classes.append(d['class'])
            skor.append(d['score'])
    
    unsafe_score = max(skor, default=0)
    skor = round(unsafe_score*100,2)
    if skor > 60:
        message.reply_text(f"Message Deleted! NSFW content found!\n\n{hasil}\ntambahkan #amanmin pada caption kalau yakin ini aman.")
        message.delete()
    
