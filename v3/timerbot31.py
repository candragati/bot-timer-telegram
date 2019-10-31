# from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram import MessageEntity
# from telegram import ParseMode
# from telegram.utils.helpers import escape_markdown
import logging
import datetime
import re
import time
# import _thread
import threading
import requests
from config import *
from modul import me,bio,afk,qotd,langdetect,setting,berita,rekam,asl,bantuan,media
from modul.kamus import kamus
from modul.setting import getUsername

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)
logger = logging.getLogger(__name__)

class bot_timer():
    def __init__(self):     
        # updater = Updater(Config.TOKEN,workers = 8,request_kwargs = {'read_timeout':600,'connect_timeout':600})
        # dp = updater.dispatcher
        updater = Config.updater
        dp = Config.dp
        dp.add_handler(CommandHandler("start",              self.start))
        dp.add_handler(CommandHandler("afk",                afk.set_afk))
        dp.add_handler(CommandHandler("setbio",             bio.set_bio))
        dp.add_handler(CommandHandler("bio",                bio.bio))
        dp.add_handler(CommandHandler("setme",              me.set_me))
        dp.add_handler(CommandHandler("me",                 me.me))
        dp.add_handler(CommandHandler("qotd",               qotd.qotd,      pass_args = True))
        dp.add_handler(CommandHandler("dqotd",              qotd.dqotd,     pass_args = True))
        dp.add_handler(CommandHandler("xqotd",              qotd.xqotd,     pass_args = True))
        dp.add_handler(CommandHandler("rqotd",              qotd.rqotd))
        dp.add_handler(CommandHandler("sqotd",              qotd.sqotd,     pass_args = True))
        dp.add_handler(CommandHandler("setting",            setting.setting,pass_args = True))
        dp.add_handler(CommandHandler("berita",             berita.berita,  pass_args = True))
        dp.add_handler(CommandHandler("baca",               rekam.baca))
        dp.add_handler(CommandHandler("tulis",              rekam.tulis))
        dp.add_handler(CommandHandler("judul",              rekam.judul))
        dp.add_handler(CommandHandler("help",               bantuan.help))
        dp.add_handler(CommandHandler("help_qotd",          bantuan.help_qotd))
        dp.add_handler(CommandHandler("help_timer",         bantuan.help_timer))
        dp.add_handler(CommandHandler("help_jadwal_sholat", bantuan.help_jadwal_sholat))
        dp.add_handler(CommandHandler("agenda",             self.agenda))
        dp.add_handler(CommandHandler("media",              media.media,    pass_args = True))
        dp.add_handler(CommandHandler("smedia",             media.smedia,   pass_args = True))
        dp.add_handler(CommandHandler("set",                self.set_timer,
                                      pass_args         =   True,
                                      pass_job_queue    =   True,
                                      pass_chat_data    =   True))
        dp.add_handler(CommandHandler("hitung",             self.timer,
                                      pass_chat_data    =   True, 
                                      pass_job_queue    =   True, 
                                      pass_args         =   True))
        
        
        dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, asl.asl))
        dp.add_handler(MessageHandler(Filters.entity(MessageEntity.MENTION) | Filters.entity(MessageEntity.TEXT_MENTION) ,afk.reply_afk),group = 1)
        dp.add_handler(MessageHandler(Filters.all, langdetect.echo,edited_updates=True),group = 2)
        dp.add_handler(MessageHandler(Filters.text|Filters.video | Filters.photo | Filters.document | Filters.forwarded | Filters.sticker, rekam.isi,edited_updates=True), group = 3)
        dp.add_handler(MessageHandler(~Filters.command & Filters.group, afk.sudah_nongol), group = 4)
        dp.add_handler(MessageHandler(Filters.text, asl.check_age),group = 5)
        # dp.add_handler(MessageHandler(~Filters.text , media.media), group = 6)
        dp.add_error_handler(self.error)
        # Start the Bot
        updater.start_polling()
        updater.idle()     

    def start(self,bot, update):
        try:
            z = self.t1.isAlive()
        except:            
            self.t1 = threading.Thread(target=self.timer, args=(bot,update))
            self.t1.start()
        # _thread.start_new_thread(self.timer,(bot,update))
        update.message.reply_text(kamus("cmd_start"))

    def set_tanggal(self,bot, update, args, job_queue, chat_data):
        try:
            current = datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=0)
            self.hitung(bot,update,args,job_queue, chat_data,int((datetime.datetime.strptime("%s %s"%(args[0], args[1]),"%Y-%m-%d %H:%M:%S")-current).total_seconds())+1)
        except:
            update.message.reply_text(kamus("cmd_error"))

    def set_jam(self,bot, update, args, job_queue, chat_data):
        now = '{:%Y-%m-%d}'.format(datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=0))
        try:
            current = datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=0)
            self.hitung(bot,update,args,job_queue, chat_data,int((datetime.datetime.strptime(now+" "+args[0],"%Y-%m-%d %H:%M:%S")-current).total_seconds())+1)
        except:
            self.set_tanggal(bot, update, args, job_queue, chat_data)

    def jadwal_sholat(self,bot,update, kota):
        try:
            z           = self.t1.isAlive()
            nama        = kota            
            sekarang    = datetime.datetime.now()
            tanggal     =  sekarang.strftime('%Y-%m-%d')
            jam         =  sekarang.strftime('%H:%M')
            hari        = datetime.datetime.strftime(sekarang.date(),"%a")
            chat_id     = update.message["chat"]["id"]
            chat_type   = update.message["chat"]["type"]
            user_id     = update.message.from_user.id
            user_name   = update.message.from_user.username
            cek         = "SELECT waktu FROM daftar_timer WHERE kota = '%s' AND DATE(waktu) = '%s' AND chat_id = '%s'"%(nama,tanggal,chat_id)
            bar, jum    = eksekusi(cek)
            if jum == 0:                
                url_kota= "https://api.banghasan.com/sholat/format/json/kota"
                r       = requests.get(url_kota)
                kota_all=  r.json()['kota']
                for a in kota_all:
                    if a['nama'] == nama.upper():
                        update.message.reply_text(str(kamus("id_ketemu"))%a['id'])
                        url         = "https://api.banghasan.com/sholat/format/json/jadwal/kota/%s/tanggal/%s"%(a['id'],tanggal)            
                        r           = requests.get(url)
                        sholat_all  =  r.json()['jadwal']['data']
                        jadwal      = []
                        t           = ""
                        m           = ""
                        for k,v in sholat_all.items():
                            if k != 'tanggal':
                                waktu = '%s %s:00'%(tanggal,v)
                                if k == 'terbit' or k == 'imsak':
                                    keterangan = "waktu"
                                else:
                                    keterangan = "sholat"

                                if k == 'terbit':t = datetime.datetime.strptime(v,'%H:%M')
                                if k == 'maghrib':m = datetime.datetime.strptime(v,"%H:%M")
                                if hari == "Fri" and k == "dzuhur":                                    
                                    sholat = "jumat"
                                else:
                                    sholat = k                                
                                if jam < v:                                    
                                    status = ""
                                    sql = "INSERT INTO daftar_timer (waktu, chat_id, chat_type, user_id, user_name, pesan, done, sholat, kota) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(
                                            waktu, chat_id, chat_type, user_id, user_name, keterangan, 0,sholat,nama)                            
                                    cur.execute(sql)
                                    db.commit()
                                else:
                                    status = (kamus("sholat_lewat"))
                                jadwal.append('%s %s %s'%(v,sholat,status))
                        tahajud = (t-((m-t)/3)).strftime("%H:%M")
                        if jam < tahajud:
                            status = ""
                            waktu_tahajud = '%s %s:00'%(tanggal,tahajud)
                            sql = "INSERT INTO daftar_timer (waktu, chat_id, chat_type, user_id, user_name, pesan, done, sholat, kota) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(
                                   waktu_tahajud, chat_id, chat_type, user_id, user_name, "sholat", 0,"tahajud",nama)                            
                            cur.execute(sql)
                            db.commit()
                        else:
                            status = (kamus("sholat_lewat"))
                        jadwal.append('%s %s %s'%(tahajud,'tahajud',status))
                        jadwal.sort()
                        agenda_sholat =''.join('%s \n'%jadwal[i] for i in range(len(jadwal)))
                        update.message.reply_text(str(kamus("sholat_jadwal"))%(nama,tanggal,agenda_sholat))
                        break
                else:
                    update.message.reply_text(kamus("kota_tidak_ketemu")%url_kota)
            else:
                update.message.reply_text(str(kamus("sholat_sudah_setting")%nama))
        except Exception as e:            
            update.message.reply_text('%s\n%s'%(kamus("mogok"),e))
        
    def set_timer(self,bot, update, args, job_queue, chat_data):
        if args[0].upper() == 'SHOLAT':
            try:
                kota = ' '.join(args[1:]).upper()                
                self.jadwal_sholat(bot,update,kota)
            except:
                self.help(bot,update)
        else:            
            try:        
                huruf = ''
                try:
                    angka   = re.match("([0-9]+)([a-zA-Z]+)",args[0]).group(1)
                    huruf   = re.match("([0-9]+)([a-zA-Z]+)",args[0]).group(2)
                except:
                    angka   = args[0]
                    satuan  = 1

                if huruf == 's' or huruf == 'd' or huruf == '':
                    satuan  = 1
                elif huruf == 'm':
                    satuan  = 60
                elif huruf == 'h' or huruf == 'j':
                    satuan  = 3600
                else:
                    update.message.reply_text(kamus("cmd_salah"))
                    return

                self.hitung(bot,update,args,job_queue, chat_data,int(angka)*satuan)
            except (IndexError, ValueError):
                self.set_jam(bot, update, args, job_queue, chat_data)

    def hitung(self,bot,update,args,job_queue, chat_data,due):
        try:
            z       = self.t1.isAlive()
            chat_id = update.message.chat_id
            if due <= 0:
                update.message.reply_text(kamus("jadwal_lewat"))                
                return
            
            pesan = ' '.join(update.message.text.split(" ")[2:])
            # match = re.match(r'^[A-Za-z0-9 ?!\/&,.:@]*$', pesan )
            # if match :
            sekarang    = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=0))
            waktu       = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()+datetime.timedelta(seconds=due,hours=0))
            chat_id     = update.message["chat"]["id"]
            chat_type   = update.message["chat"]["type"]
            user_id     = update.message.from_user.id
            user_name   = update.message.from_user.username
            sql         = "INSERT INTO daftar_timer (waktu, chat_id, chat_type, user_id, user_name, pesan, done, sholat, kota) VALUES (?,?,?,?,?,?,?,'','')"
            cur.execute(sql,(waktu, chat_id, chat_type, user_id, user_name, pesan, 0))
            db.commit()                
            update.message.reply_text(kamus("jadwal_set")%(sekarang, waktu))
            # else:
            #     update.message.reply_text('incorrect string')
        except Exception as e:
            update.message.reply_text('%s\n%s'%(kamus("mogok"),e))

    def agenda(self,bot,update):
        try:
            z       = self.t1.isAlive()
            user_id = update.message.from_user.id
            chat_id = update.message["chat"]["id"]
            sql     = "SELECT waktu, pesan, sholat, kota FROM daftar_timer WHERE user_id = '%s' AND chat_id = '%s' AND done = 0"%(user_id, chat_id)
            bar, jum = eksekusi(sql)

            if jum == 0:
                update.message.reply_text(kamus("jadwal_kosong"))
            else:
                cek = []
                for i in range(jum):
                    waktu       = bar[i][0]                    
                    sekarang    = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=0))
                    if sekarang > waktu:
                        teks    = kamus("sholat_lewat")
                        done    = "UPDATE daftar_timer SET done = 1 WHERE waktu = '%s' and chat_id = '%s' AND user_id = '%s'"%(waktu,chat_id,user_id)
                        cur.execute(done)
                        db.commit()
                    else:
                        teks    = ""
                    cek.append("%s %s %s %s %s"%(waktu, bar[i][1],bar[i][2],bar[i][3], teks))                    
                cek.sort()
                agenda  = ''.join('%s \n'%cek[i] for i in range(len(cek)))
                update.message.reply_text(kamus("jadwal_list")%agenda)
        except Exception as e:
            update.message.reply_text('%s\n%s'%(kamus("mogok"),e))
    
    def error(self,bot, update, error):
        """Log Errors caused by Updates."""
        update.message.reply_text(str(error))

    def timer(self,bot,update):
        while True:           
            sekarang    = datetime.datetime.now()
            hari        = datetime.datetime.strftime(sekarang.date(),"%a") 
            user_id     = update.message.from_user.id
            waktu       =  '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=0))
            sql         = "SELECT waktu, pesan, chat_id, user_name, sholat, kota FROM daftar_timer WHERE waktu = '%s'"%waktu
            # print (sql)
            try:
                bar, jum = eksekusi(sql)
                if jum == 0:
                    pass
                else:
                    for i in range(jum):
                        chat_id = bar[i][2]
                        if len(bar[i][4]) > 1:
                            if bar[i][1]== 'sholat':
                                kata = "\n\n%s"%kamus("sholat_footnote")
                            else:
                                kata = ""
                            if hari == "Sun":
                                sholat_waktu = bar[i][1]
                                if sholat_waktu == "waktu":
                                    sholat_waktu = "time"
                                else:
                                    sholat_waktu = "prayer"
                                
                                if bar[i][4] == "terbit":
                                    sholat = "sunrise"
                                else:
                                    sholat = bar[i][4]
                                pesan = (kamus("sholat_teks")%(sholat,sholat_waktu, bar[i][5], bar[i][3],kata))
                            else:
                                pesan = (kamus("sholat_teks")%(bar[i][1], bar[i][4], bar[i][5], bar[i][3],kata))
                        else:
                            if (bar[i][1].split()[0])=="banned":                                
                                try:
                                    user_id = (bar[i][1].split()[1])
                                    bot.send_sticker(chat_id, 'CAADBQADSQ4AAs_rwQcgxkK2JzKWwhYE')  # banhammer marie sticker
                                    bot.kick_chat_member(chat_id, user_id)
                                    pesan = ("banned @%s"%(bar[i][3]))
                                except:
                                    pesan = ("%s - @%s"%(bar[i][1],bar[i][3]))    
                            else:
                                pesan = ("%s - @%s"%(bar[i][1],bar[i][3]))
                        bot.send_message(text = pesan,chat_id = chat_id)
                        done = "UPDATE daftar_timer SET done = 1 WHERE waktu = '%s' and chat_id = '%s' AND user_id = '%s'"%(waktu,chat_id,user_id)
                        cur.execute(done)
                        db.commit()
                time.sleep(1)
            except Exception as e:
                update.message.reply_text("Error %s"%e)

if __name__ == '__main__':
    bot_timer()
