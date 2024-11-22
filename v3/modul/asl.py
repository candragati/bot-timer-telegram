# 
# from telegram.ext import Updater
from config import *
import datetime
import re
import threading
import requests
import random
import time
# import pprint

lock = threading.Lock()
del_msg = []    

def asl(update,context):    
    new_members = update.message.new_chat_members
    waktu       = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()+datetime.timedelta(seconds=600,hours=0))
    chat_id     = update.message["chat"]["id"]
    chat_type   = update.message["chat"]["type"]
    
    for member in new_members:
        user_id  = member.id
        if user_id == Config.BOT_ID:
            pass
        else:
            rpl_x = ""
            done = 0
            user_name= member.username if member.username else member.first_name
            cek_new_member  = "SELECT age FROM new_members WHERE chat_id = '%s' AND user_id = '%s' AND done = 1"%(chat_id, user_id)
            bar, jum = eksekusi( cek_new_member)
            if jum != 0:
                teks = "Verified account. Welcome back %s"%user_name
                rpl_x = update.message.reply_text(teks).to_dict()
                del_msg.insert(0,update.message.message_id)
                del_msg.insert(0,rpl_x["message_id"])    
                done = 1        
            else:
                sql             = "SELECT asl FROM setting WHERE chat_id = '%s'"%chat_id
                bar, jum        = eksekusi(sql)
                if jum == 0:
                    pass
                elif bar[0][0] == 'ON':
                    user_name= member.username if member.username else member.first_name
                    pesan = "banned %s"%user_id
                    try:
                        lock.acquire(True)
                        sql         = "INSERT INTO daftar_timer (waktu, chat_id, chat_type, user_id, user_name, pesan, done, sholat, kota) VALUES (?,?,?,?,?,?,?,'','')"
                        cur.execute(sql,(waktu, chat_id, chat_type, user_id, user_name, pesan, 0))
                        db.commit()
                    finally:
                        lock.release()

                    try:
                        lock.acquire(True)
                        sql_new_member         = "INSERT INTO new_members (chat_id, chat_type, user_id, user_name,age,done,waktu) VALUES (?,?,?,?,?,0,?)"
                        cur.execute(sql_new_member,(chat_id, chat_type, user_id, user_name, 0, '{:%Y-%m-%d}'.format(datetime.datetime.now())))
                        db.commit()
                    finally:
                        lock.release()
                    teks = ("Hei %s! \nASL plz, Or you will be banned in 10 minutes."%(user_name))
                    rpl_x = update.message.reply_text(teks).to_dict()
                    del_msg.insert(0,update.message.message_id)
                    del_msg.insert(0,rpl_x["message_id"])            
                elif bar[0][0] == 'UMUR':
                    user_name= member.username if member.username else member.first_name
                    pesan = "banned %s"%user_id
                    try:
                        lock.acquire(True)
                        sql         = "INSERT INTO daftar_timer (waktu, chat_id, chat_type, user_id, user_name, pesan, done, sholat, kota) VALUES (?,?,?,?,?,?,?,'','')"
                        cur.execute(sql,(waktu, chat_id, chat_type, user_id, user_name, pesan, 0))
                        db.commit()
                    finally:
                        lock.release()

                    try:                    
                        lock.acquire(True)
                        sql_new_member         = "INSERT INTO new_members (chat_id, chat_type, user_id, user_name,age,done,waktu) VALUES (?,?,?,?,?,0,?)"
                        cur.execute(sql_new_member,(chat_id, chat_type, user_id, user_name, 0, '{:%Y-%m-%d}'.format(datetime.datetime.now())))
                        db.commit()
                    finally:
                        lock.release()
                    teks = ("Hallo %s! \nUntuk menghindari spammer, silahkan sebut nama, umur dan lokasi nya ya sebelum 10 menit."%(user_name))
                    rpl_x = update.message.reply_text(teks).to_dict()
                    del_msg.insert(0,update.message.message_id)
                    del_msg.insert(0,rpl_x["message_id"])            
                else:
                    pass
            
            
    del user_id, new_members

def check_age(update,context):
    # pprint.pprint (update)
    bot = context.bot
    if update.message == None:
        return
    message         = update.message.text   
    chat_id         = update.message["chat"]["id"]
    chat_type       = update.message["chat"]["type"]
    user_id         = str(update.message.from_user.id)
    user_name       = update.message.from_user.username
    pesan           = "banned %s"%user_id
    rpl_x           = ""
    sql             = "SELECT asl FROM setting WHERE chat_id = '%s'"%chat_id
    bar, jum        = eksekusi(sql)    
    if jum == 0:
        pass
    elif bar[0][0] == 'ON':
        cek_new_member  = "SELECT age FROM new_members WHERE chat_id = '%s' AND user_id = '%s' AND done = 0 and age = 0"%(chat_id, user_id)
        bar, jum = eksekusi( cek_new_member)
        if jum == 0:
            pass
        elif len(message) > 50:
            teks = "teks kepanjangan, coba yg agak pendekan"
            rpl_x = update.message.reply_text(teks).to_dict()
            del_msg.insert(0,update.message.message_id)
            del_msg.insert(0,rpl_x["message_id"])            
        else:
            age =  (re.sub("\D", "", message))
            if age == "":                        
                sqlCek = "SELECT waktu, done FROM daftar_timer WHERE chat_id = '%s' AND user_id = '%s' AND done = 0"%(chat_id, user_id)
                bar, jum = eksekusi(sqlCek)
                if jum != 0:
                    waktu       = bar[0][0]                    
                    sekarang    = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=0))
                    if sekarang > waktu:                
                        waktuBerikut = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()+datetime.timedelta(seconds=600,hours=0))
                        teks    = "ASL plz, Or you will be banned in 10 minutes."
                        sql         = "UPDATE daftar_timer SET waktu= ? WHERE chat_id=? AND user_id = ?"
                        cur.execute(sql,(waktuBerikut, chat_id, user_id))
                        db.commit()
                        rpl_x = update.message.reply_text(teks).to_dict()
                    else:
                        rpl_x = update.message.reply_text("ASL PLS!").to_dict()

                    del_msg.insert(0,update.message.message_id)
                    del_msg.insert(0,rpl_x["message_id"])            
            elif len(age) > 2:                                    
                rpl_x = update.message.reply_text("You must answer correctly").to_dict()
                del_msg.insert(0,update.message.message_id)
                del_msg.insert(0,rpl_x["message_id"])            
            else:   
                if int(age) >= 60:
                    rpl_x = update.message.reply_text("Too old").to_dict()                
                    del_msg.insert(0,update.message.message_id)
                    del_msg.insert(0,rpl_x["message_id"])                     
                elif int(age) >= 17:                
                    cekHistori = "SELECT age, waktu FROM new_members WHERE user_id = '%s' AND done = 1"%user_id
                    bar, jum = eksekusi(cekHistori)
                    if jum == 0:
                        age_cocok(update, context, del_msg= del_msg)
                    else:
                        today = datetime.date.today()
                        born = datetime.datetime.strptime(bar[0][1], '%Y-%m-%d')
                        # usia = (today.year - born.year - ((today.month, today.day) < (born.month, born.day)))+bar[0][0]
                        usia = (today.year - born.year)+bar[0][0]

                        if usia != int(age):
                            teks = ("Salah sebut umur, umur anda disini tetap dihitung mundur")
                            rpl_x = update.message.reply_text(teks).to_dict()
                            del_msg.insert(0,update.message.message_id)
                            del_msg.insert(0,rpl_x["message_id"])            
                        else:
                            age_cocok(update, context, del_msg= del_msg)
                
                else:
                    rpl_x = update.message.reply_text("You are not allowed to join the group").to_dict()                
                    del_msg.insert(0,update.message.message_id)
                    del_msg.insert(0,rpl_x["message_id"])            
        del rpl_x
    elif bar[0][0] == 'UMUR':
        cek_new_member  = "SELECT age FROM new_members WHERE chat_id = '%s' AND user_id = '%s' AND done = 0 and age = 0"%(chat_id, user_id)
        bar, jum = eksekusi( cek_new_member)
        if jum == 0:
            pass  
        elif len(message) > 50:
            teks = "teks kepanjangan, coba yg agak pendekan"
            rpl_x = update.message.reply_text(teks).to_dict()
            del_msg.insert(0,update.message.message_id)
            del_msg.insert(0,rpl_x["message_id"])      
        else:            
            age =  (re.sub("\D", "", message))
            if age == "":                        
                sqlCek = "SELECT waktu, done FROM daftar_timer WHERE chat_id = '%s' AND user_id = '%s' AND done = 0"%(chat_id, user_id)
                bar, jum = eksekusi(sqlCek)
                if jum != 0:
                    waktu       = bar[0][0]                    
                    sekarang    = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=0))
                    if sekarang > waktu:                
                        waktuBerikut = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()+datetime.timedelta(seconds=600,hours=0))
                        teks    = "Tulis nama, umur dan lokasi ya sebelum 10 menit"
                        sql         = "UPDATE daftar_timer SET waktu= ? WHERE chat_id=? AND user_id = ?"
                        cur.execute(sql,(waktuBerikut, chat_id, user_id))
                        db.commit()
                        rpl_x = update.message.reply_text(teks).to_dict()
                    else:
                        rpl_x = update.message.reply_text("Nama, Umur dan lokasinya oy!").to_dict()

                    del_msg.insert(0,update.message.message_id)
                    del_msg.insert(0,rpl_x["message_id"])            
            elif len(age) > 2:                                    
                rpl_x = update.message.reply_text("You must answer correctly").to_dict()
                del_msg.insert(0,update.message.message_id)
                del_msg.insert(0,rpl_x["message_id"])            
            else:                   
                cekHistori = "SELECT age, waktu FROM new_members WHERE user_id = '%s' AND done = 1"%user_id
                bar, jum = eksekusi(cekHistori)
                if jum == 0:
                    age_cocok(update, context, del_msg= del_msg)
                else:
                    today = datetime.date.today()
                    born = datetime.datetime.strptime(bar[0][1], '%Y-%m-%d')
                    # usia = (today.year - born.year - ((today.month, today.day) < (born.month, born.day)))+bar[0][0]
                    usia = (today.year - born.year)+bar[0][0]

                    if usia != int(age):
                        teks = ("Salah sebut umur, umur anda disini tetap dihitung mundur")
                        rpl_x = update.message.reply_text(teks).to_dict()
                        del_msg.insert(0,update.message.message_id)
                        del_msg.insert(0,rpl_x["message_id"])            
                    else:
                        age_cocok(update, context, del_msg= del_msg)
        del rpl_x
    else:
        pass
        # if rpl_x != "":
            # # Template queue for delete unused messages.
            # # Description: Set queue to delete 2 messages.
            #
            # # 1. delete_message from bot itself.
            # chat_id = chat_id # from var above
            # messsage_id = rpl_x["message_id"]
            #
            # # 2. delete_message from user (unqualified ASL reply).
            # chat_id = chat_id # from var above
            # message_id = update.message.message_id
            #
            #
            # pass
def age_cocok(update,context, del_msg, done=None):
    bot = context.bot
    if update.message == None:
        return
    message         = update.message.text   
    chat_id         = update.message["chat"]["id"]
    user_id         = str(update.message.from_user.id)
    pesan           = "banned %s"%user_id
    if done == None or done == 0:
        age =  (re.sub("\D", "", message))
        try:
            lock.acquire(True)
            done = "UPDATE new_members SET done = 1, age = '%s' WHERE chat_id = '%s' AND user_id = '%s'"%(age,chat_id,user_id)                    
            cur.execute(done)
            db.commit()
        finally:
            lock.release()

        try:
            lock.acquire(True)
            done_timer = "DELETE FROM daftar_timer WHERE chat_id = '%s' AND user_id = '%s' AND pesan = '%s'"%(chat_id,user_id,pesan)                    
            cur.execute(done_timer)
            db.commit()
        finally:
            lock.release()

    # IceTea bridging.
    URL = "https://telegram-bot.teainside.org/api.php"
    PARAMS = {
        "action"    : "asl_msg",
        "key"       : Config.ICETEA,
        "chat_id"   : chat_id,
        "user_id"   : user_id,
        "msg_id"    : update.message.message_id
    }
    r = requests.get(url = URL, params = PARAMS)

    teks = ("Welcome to the group!")                
    rpl_x = update.message.reply_text(teks).to_dict()
    del_msg.insert(0,update.message.message_id)
    del_msg.insert(0,rpl_x["message_id"])    
    time.sleep(5)        
    for i in range(len(del_msg)):                    
        bot.delete_message(chat_id = chat_id, message_id =  del_msg[i])                    
# dp = Config.dp
# dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, asl))

def lupaUmur(update,context):
    bot = context.bot
    if update.message == None:
        return
    message         = update.message.text   
    chat_id         = update.message["chat"]["id"]
    user_id         = str(update.message.from_user.id)
    sql         = "SELECT age,waktu FROM new_members WHERE user_id = '%s'"%(user_id)
    bar, jum = eksekusi(sql)
    if jum == 0:
        update.message.reply_text("saya belum dikasih tau umurnya berapa") 
    else:
        today = datetime.date.today()
        born = datetime.datetime.strptime(bar[0][1], '%Y-%m-%d')
        # usia = (today.year - born.year - ((today.month, today.day) < (born.month, born.day)))+bar[0][0]
        usia = (today.year - born.year)+bar[0][0]
        
        umur = list(str(usia))
        if len(umur) == 1:
            umur = list('0'+str(usia))

        if 17 <= usia <= 25:
            kategori = "remaja aktif"            
        elif 26 <= usia <= 35:
            kategori = "dewasa awal"            
        elif 36 <= usia <= 45:
            kategori = "dewasa akhir"
        elif 46 <= usia <= 55:
            kategori = 'lansia awal'
        else:
            kategori = "apa ya?"

        if 17 <= usia <= 25:
            generasi = "Gen Z"
        elif 26 <= usia <= 40:
            generasi = "kaum milenial"
        elif 41 <= usia <= 55:
            generasi = "Gen X"
        elif 56 <= usia <= 76:
            generasi = "Baby Boomers"
        else:
            generasi = "apa ya?"



        sebutUmur = [
            'cluenya adalah : angka pertama %s, angka terakhir %s'%(umur[0], umur[1]), 
            'anda pernah ngaku kalo umurnya %s tahun'%usia,
            'umur %s termasuk kategori %s'%(usia, kategori),
            'umur %s masuk generasi %s'%(usia, generasi),
            'umur anda %s tahun, meskipun diragukan kebenarannya'%usia,
        ]
        update.message.reply_text(random.choice(sebutUmur)) 

def setUmur(update,context):
    bot = context.bot
    if update.message == None:
        return
    message         = update.message.text   
    m   = update.effective_message
    chat_id         = update.message["chat"]["id"]
    chat_type       = update.message["chat"]["type"]
    user_id         = str(update.message.from_user.id)
    user_name       = update.message.from_user.username
    waktu       = '{:%Y-%m-%d}'.format(datetime.datetime.now())

    teks= m.text.split(None,1)
    if len(teks) == 2:
        try:
            lock.acquire(True)
            umur =  re.sub("\D", "", str(teks[1]))
            if umur == '':
                update.message.reply_text("sebutin umur dalam bentuk angka")  
            elif len(list(umur)) >= 3:
                update.message.reply_text("umurnya ngaco")
            elif len(list(umur)) < 2:
                update.message.reply_text("terlalu dini kamu dek")
            else:
                sql         = "SELECT age FROM new_members WHERE user_id = '%s'"%(user_id)
                bar, jum = eksekusi(sql)
                if jum == 0:
                    sqlUmur         = "INSERT INTO new_members (chat_id, chat_type, user_id, user_name,age,done,waktu) VALUES (?,?,?,?,?,?,?)"
                    cur.execute(sqlUmur,(chat_id, chat_type, user_id, user_name, umur, 1, waktu))
                    db.commit()
                else:
                    sqlUmur = "UPDATE new_members SET done = 1, age = '%s', waktu = '%s' WHERE user_id = '%s'"%(umur,waktu, user_id)                    
                    cur.execute(sqlUmur)
                    db.commit()
                update.message.reply_text("umur anda sudah saya catet untuk dilaporin sewaktu2.")
        except Exception as e:
            update.message.reply_text(e)  
        finally:
            lock.release()
    else:
        update.message.reply_text("ketik /setUmur <umur anda sekarang>")  


    