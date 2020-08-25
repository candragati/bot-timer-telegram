# 
# from telegram.ext import Updater
from config import *
import datetime
import re
import threading
import requests
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
                sql_new_member         = "INSERT INTO new_members (chat_id, chat_type, user_id, user_name,age,done) VALUES (?,?,?,?,?,0)"
                cur.execute(sql_new_member,(chat_id, chat_type, user_id, user_name, 0))
                db.commit()
            finally:
                lock.release()
            update.message.reply_text("Hei %s! \nASL plz, Or you will be banned in 10 minutes."%(user_name))

def check_age(update,context):
    # pprint.pprint (update)
    bot = context.bot
    if update.message == None:
        return
    message         = update.message.text   
    chat_id         = update.message["chat"]["id"]
    user_id         = str(update.message.from_user.id)
    pesan           = "banned %s"%user_id
    cek_new_member  = "SELECT age FROM new_members WHERE chat_id = '%s' AND user_id = '%s' AND done = 0 and age = 0"%(chat_id, user_id)
    bar, jum = eksekusi( cek_new_member)
    if jum == 0:
        pass        
    else:
        rpl_x = ""
        age =  (re.sub("\D", "", message))
        if age == "":
            rpl_x = update.message.reply_text("ASL PLS!").to_dict()            
            del_msg.insert(0,update.message.message_id)
            del_msg.insert(0,rpl_x["message_id"])            
        elif len(age) > 2:                                    
            rpl_x = update.message.reply_text("You must answer correctly").to_dict()
            del_msg.insert(0,update.message.message_id)
            del_msg.insert(0,rpl_x["message_id"])            
        else:            
            if int(age) >= 17:
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

                
                update.message.reply_text("Welcome to the group!")                
                for i in range(len(del_msg)):                    
                    bot.delete_message(chat_id = chat_id, message_id =  del_msg[i])                    
            else:
                rpl_x = update.message.reply_text("You are not allowed to join the group").to_dict()                
                del_msg.insert(0,update.message.message_id)
                del_msg.insert(0,rpl_x["message_id"])            
        
        if rpl_x != "":
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
            pass

# dp = Config.dp
# dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, asl))
