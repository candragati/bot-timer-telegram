
from config import *
import calendar

def upsert_setting(chat_id, chat_type, field, value):
    sql = f"SELECT {field} FROM setting WHERE chat_id = ?"
    _, jum = eksekusi(sql, (chat_id,))

    if jum == 0:
        sql = f"INSERT INTO setting (chat_id, chat_type, {field}) VALUES (?,?,?)"
        eksekusi(sql, (chat_id, chat_type, value))
    else:
        sql = f"UPDATE setting SET {field}=? WHERE chat_id=?"
        eksekusi(sql, (value, chat_id))


def setting(update,context):
    bot         = context.bot
    args        = context.args
    chat_id     = update.message["chat"]["id"]
    chat_type   = update.message["chat"]["type"]
    chat        = update.effective_chat
    user_id     = update.message.from_user.id
    status = chat.get_member(user_id).status
    cmd         = args[0].lower()
    if status in ('administrator','creator'):
        if not args:
            update.message.reply_text("setting apa pak?")
        elif cmd=='en':
            hari = list(calendar.day_abbr)
            try:
                if args[1].upper()=='CLEAR':
                    sql = "UPDATE setting SET english_day = null WHERE chat_id = ?"
                    eksekusi(sql,(chat_id,))
                    
                    update.message.reply_text("sudah gak ada english day lagi. horee...")
                else:
                    sql = "SELECT english_day FROM setting WHERE chat_id = ?"
                    bar, jum = eksekusi(sql, (chat_id,))
                    english_day = args[1].title()
                    index_day   = hari.index(english_day)
                    day_name    = calendar.day_name[index_day]
                    if jum == 0:
                        sql = "INSERT INTO setting (chat_id, chat_type,english_day) VALUES (?,?,?)"
                        eksekusi(sql,(chat_id,chat_type,english_day))
                    else:
                        sql = "UPDATE setting SET english_day=? WHERE chat_id = ?"
                        eksekusi(sql,(english_day, chat_id))
                    
                    update.message.reply_text(f"english day is set for {day_name}")            
            except Exception as e:
                update.message.reply_text(f"choose one from {hari}")
        elif cmd in ('asl', 'spam', 'nsfw'):
            if len(args) < 2:
                update.message.reply_text("pilih ON|OFF|UMUR")
                return

            value = args[1].upper()

            valid = {
                'asl':  ('ON', 'OFF', 'UMUR'),
                'spam': ('ON', 'OFF'),
                'nsfw': ('ON', 'OFF'),
            }

            if value not in valid[cmd]:
                update.message.reply_text("pilih " + "|".join(valid[cmd]))
                return

            upsert_setting(chat_id, chat_type, cmd, value)

            status = "aktif" if value != 'OFF' else "non aktif"
            update.message.reply_text(f"filter {cmd} {status}")


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