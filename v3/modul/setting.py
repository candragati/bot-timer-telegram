
from config import *
import calendar

def setting(update,context):
    bot         = context.bot
    args        = context.args
    chat_id     = update.message["chat"]["id"]
    chat_type   = update.message["chat"]["type"]
    chat        = update.effective_chat
    user_id     = update.message.from_user.id
    user_member = chat.get_member(user_id)
    if user_member.status == 'administrator' or user_member.status == 'creator':
        if len(args)==0:
            update.message.reply_text("setting apa pak?")
        elif args[0]=='en':
            hari = list(calendar.day_abbr)
            try:
                if args[1].upper()=='CLEAR':
                    sql = "DELETE FROM setting WHERE chat_id = '%s'"%chat_id                
                    eksekusi(sql)
                    
                    update.message.reply_text("sudah gak ada english day lagi. horee...")
                else:
                    sql = "SELECT english_day FROM setting WHERE chat_id = '%s'"%chat_id
                    bar, jum = eksekusi(sql)
                    english_day = args[1].title()
                    index_day   = hari.index(english_day)
                    day_name    = calendar.day_name[index_day]
                    if jum == 0:
                        sql = "INSERT INTO setting (chat_id, chat_type,english_day) VALUES (?,?,?)"
                        eksekusi(sql,(chat_id,chat_type,english_day))
                    else:
                        sql = "UPDATE setting SET english_day=? WHERE chat_id = ?"
                        eksekusi(sql,(english_day, chat_id))
                    
                    update.message.reply_text("english day is set for %s"%day_name)            
            except Exception as e:
                update.message.reply_text("choose one from %s"%hari)
        elif args[0]=='asl':
            try:
                if args[1].upper()=='OFF':
                    sql = "UPDATE setting SET asl = 'OFF' WHERE chat_id = '%s'"%chat_id                
                    eksekusi(sql)
                    
                    update.message.reply_text("filter ASL non aktif")
                elif args[1].upper()=='ON':
                    sql = "SELECT asl FROM setting WHERE chat_id = '%s'"%chat_id
                    bar, jum = eksekusi(sql)
                    
                    if jum == 0:
                        sql = "INSERT INTO setting (chat_id, chat_type,asl) VALUES (?,?,?)"
                        eksekusi(sql,(chat_id,chat_type,'ON'))
                    else:
                        sql = "UPDATE setting SET asl=? WHERE chat_id = ?"
                        eksekusi(sql,('ON', chat_id))
                    
                    update.message.reply_text("filter ASL aktif")            
                elif args[1].upper()=='UMUR':
                    sql = "SELECT asl FROM setting WHERE chat_id = '%s'"%chat_id
                    bar, jum = eksekusi(sql)
                    
                    if jum == 0:
                        sql = "INSERT INTO setting (chat_id, chat_type,asl) VALUES (?,?,?)"
                        eksekusi(sql,(chat_id,chat_type,'UMUR'))
                    else:
                        sql = "UPDATE setting SET asl=? WHERE chat_id = ?"
                        eksekusi(sql,('UMUR', chat_id))
                    
                    update.message.reply_text("filter ASL dirubah ke bahasa")            
                else:
                    update.message.reply_text("pilih ON|OFF|UMUR")
            except Exception:
                update.message.reply_text("pilih ON|OFF|UMUR")
        elif args[0] == 'spam':
            try:
                if args[1].upper()=='OFF':
                    sql = "UPDATE setting SET spam = 'OFF' WHERE chat_id = '%s'"%chat_id                
                    eksekusi(sql)
                    
                    update.message.reply_text("filter spam non aktif")
                elif args[1].upper()=='ON':
                    sql = "SELECT spam FROM setting WHERE chat_id = '%s'"%chat_id
                    bar, jum = eksekusi(sql)
                    
                    if jum == 0:
                        sql = "INSERT INTO setting (chat_id, chat_type,spam) VALUES (?,?,?)"
                        eksekusi(sql,(chat_id,chat_type,'ON'))
                    else:
                        sql = "UPDATE setting SET spam=? WHERE chat_id = ?"
                        eksekusi(sql,('ON', chat_id))
                    
                    update.message.reply_text("filter spam aktif")            
                else:
                    update.message.reply_text("pilih ON|OFF")
            except Exception:
                update.message.reply_text("pilih ON|OFF")

        else:
            update.message.reply_text("aku gak selalu ngerti kamu mas...")
    else:
        update.message.reply_text("user biasa kayak kamu gak bisa suruh-suruh aku")
            

def getUsername(update,context,args):
    bot = context.bot    
    alt = '<a href="tg://user?id='+args[0]+'">@'+ args[1] +'</a>'
    if len(args) == 0:
        return "@" + args[1]
    else:
        chat_id = update.message["chat"]["id"]
        try:
            e = bot.getChatMember(chat_id, args[0])
            return "@" + e['user']['username'] if 'username' in e['user'] else alt
        except:
            pass
        try:
            f =  bot.getChatMember(args[0], args[0])
            return "@" + f['user']['username'] if 'username' in f['user'] else alt
        except:
            pass
        return alt